#!/usr/bin/env python3
"""Refuse a tool call that would put protected data, or unreviewed output from it, into the session.

Active only in a project with `.claude/phi.json` (see `phi_policy.py`). There the
agent writes and submits code that reads the protected folders but never sees what
that code read or printed until a person has released it. This hook refuses:

- reading, searching or listing a protected folder or the held area with any tool;
- a shell command that names one of them, unless it is a job submission or a `phi`
  command, both of which send output to the held area instead of to the agent;
- a job submission whose log would land outside the held area;
- `srun`, `salloc` and `ssh`, which stream a remote command's output straight back;
- writing to the released area or to the project's `phi.json` (`phi protect` adds folders);
- `phi release`, `phi reject` and `phi unprotect`, which only a person runs;
- reading another tmux pane, which is where a person reviews held output.

It checks each call as written. A script the agent runs directly that opens a
protected folder without naming it on the command line is invisible here; the
operating-system sandbox, which `phi check` verifies, is what stops that read.

Adapted from the CLIF clif-icu plugin's hooks/phi_guard.py
(https://github.com/Common-Longitudinal-ICU-data-Format/skills) and the
clif-sensitive-data-demo's no-row-dumps.py (https://github.com/kaveriC/clif-sensitive-data-demo).
Any error inside this hook refuses the call.
"""
import json
import os
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hookio import allow, command_text, deny_tool, is_shell  # noqa: E402
import phi_policy  # noqa: E402

FILE_PATH_KEYS = ("file_path", "path", "notebook_path")
WRITE_TOOL_NAMES = ("Write", "Edit", "MultiEdit", "NotebookEdit")
SEARCH_TOOL_NAMES = ("Grep", "Glob", "LS")
SAFE_PHI_SUBCOMMANDS = ("new", "run", "collect", "show", "list", "check", "settings", "protect")
REMOTE_SHELLS = ("srun", "salloc", "ssh")
# sbatch options that take no value; every other option does.
SBATCH_FLAGS = {"--exclusive", "--hold", "--parsable", "--wait", "--test-only", "--requeue",
                "--no-requeue", "--overcommit", "--contiguous", "--quiet", "--verbose", "--help",
                "--usage", "--spread-job", "--use-min-nodes", "--oversubscribe", "--no-kill",
                "--ignore-pbs", "--reboot", "--get-user-env", "--version",
                "-H", "-O", "-Q", "-s", "-v", "-W", "-h", "-k", "-V"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|&\n`]|\$\(|\(|\)")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
PREFIX_WORDS = ("sudo", "exec", "time", "nohup", "env", "command", "builtin")

HOW = ("Protected data reaches you only through the held area and a person's review: "
       "run it with `phi run -- <command>` or, on a Slurm cluster, submit it with its log in "
       "the held area; then `phi collect <id>` and `phi show <id>`, and read the result under "
       "the released area.")


def segments(text):
    """Each simple command in a shell line, as (first word, words)."""
    out = []
    for piece in SEGMENT_SPLIT.split(text):
        try:
            words = shlex.split(piece, comments=True)
        except ValueError:
            words = piece.split()
        while words and (ASSIGNMENT.match(words[0]) or words[0] in PREFIX_WORDS):
            words = words[1:]
        if words:
            out.append((os.path.basename(words[0]), words, piece))
    return out


def parse_sbatch(words):
    """(options dict, script path or None) from sbatch's arguments."""
    options, i = {}, 0
    while i < len(words):
        word = words[i]
        if not word.startswith("-") or word == "-":
            return options, word
        if word.startswith("--") and "=" in word:
            key, value = word.split("=", 1)
            options[key] = value
        elif word in SBATCH_FLAGS:
            options[word] = True
        elif not word.startswith("--") and len(word) > 2:  # -ofile
            options[word[:2]] = word[2:]
        else:
            options[word] = words[i + 1] if i + 1 < len(words) else ""
            i += 1
        i += 1
    return options, None


def script_directives(script):
    words = []
    with open(script, encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#SBATCH"):
                words.extend(shlex.split(line[len("#SBATCH"):], comments=True))
            elif line.strip() and not line.startswith("#"):
                break
    return parse_sbatch(words)[0]


def check_sbatch(policy, words, cwd):
    options, script = parse_sbatch(words[1:])
    if script and "--wrap" not in options:
        path = phi_policy.resolve(script, cwd)
        try:
            directives = script_directives(path)
        except OSError:
            deny_tool("Refused: cannot read the job script {} to check where its log goes. "
                      "Name it by a path that exists.".format(script))
        for key, value in directives.items():
            options.setdefault(key, value)
    workdir = phi_policy.resolve(options.get("--chdir") or options.get("-D") or cwd, cwd)
    output = options.get("--output") or options.get("-o")
    error = options.get("--error") or options.get("-e")
    if not output:
        deny_tool("Refused: this job sets no --output, so Slurm writes its log beside the submit "
                  "directory, where you would read it. Add --output (and --error, or leave it to "
                  "merge) inside the held area, {}. `phi new <name>` makes a folder there.".format(
                      policy.raw_held))
    for label, value in (("--output", output), ("--error", error)):
        if not value:
            continue
        if "$" in value:
            deny_tool("Refused: {} {} uses a shell variable this hook cannot resolve. Write the "
                      "held-area path out in full.".format(label, value))
        if not phi_policy.is_under(phi_policy.resolve(value, workdir), policy.held):
            deny_tool("Refused: {} {} is outside the held area, so the job's log would come back "
                      "to you unreviewed. Point it inside {}.".format(label, value, policy.raw_held))


def check_shell(policy, event):
    text = command_text(event)
    cwd = event.get("cwd") or os.getcwd()
    if re.search(r"(^|[\s/;&|(`])phi(\.py)?\s+(release|reject)\b", text):
        deny_tool("Refused: only a person releases or rejects a review, after reading it. Ask them "
                  "to run `phi release <id>` or `phi reject <id> \"reason\"` in their own terminal.")
    if re.search(r"(^|[\s/;&|(`])phi(\.py)?\s+unprotect\b", text):
        deny_tool("Refused: only a person takes a folder off the protected list. Ask them to run "
                  "`phi unprotect <folder>`. You may add folders with `phi protect <folder>`.")
    if re.search(r"\btmux\b.*\b(capture-pane|capturep|save-buffer|saveb|show-buffer|showb|"
                 r"pipe-pane|pipep)\b", text):
        deny_tool("Refused: reading a tmux pane's contents could copy held output that a person is "
                  "reviewing into this session.")
    mentioned = policy.mentioned_roots(text)
    for first, words, piece in segments(text):
        if first in REMOTE_SHELLS:
            deny_tool("Refused: {} sends the remote command's output straight back here, unreviewed. "
                      "Use `phi run -- {}`, or sbatch with its log in the held area.".format(
                          first, " ".join(words)))
        if first == "sbatch":
            check_sbatch(policy, words, cwd)
            continue
        if not policy.mentioned_roots(piece):
            continue
        if first in ("phi", "phi.py") and len(words) > 1 and words[1] in SAFE_PHI_SUBCOMMANDS:
            continue
        deny_tool("Refused: `{}` names {}, and its output would come back to you. {}".format(
            first, ", ".join(policy.mentioned_roots(piece)), HOW))
    if mentioned and not segments(text):
        deny_tool("Refused: this command names {}. {}".format(", ".join(mentioned), HOW))


def check_file_tool(policy, event):
    tool = event.get("tool_name") or ""
    arguments = event.get("tool_input") or {}
    cwd = event.get("cwd") or os.getcwd()
    targets = [arguments[k] for k in FILE_PATH_KEYS if isinstance(arguments.get(k), str) and arguments[k]]
    pattern = arguments.get("pattern")
    if tool == "Glob" and isinstance(pattern, str) and os.path.isabs(os.path.expanduser(pattern)):
        targets.append(pattern.split("*")[0] or "/")
    if tool in SEARCH_TOOL_NAMES and not any(k in arguments for k in FILE_PATH_KEYS):
        targets.append(cwd)
    for target in targets:
        where = policy.classify(target, cwd)
        if where == "hidden":
            deny_tool("Refused: {} is inside a protected folder or the held area. {}".format(target, HOW))
        if where in ("released", "config") and tool in WRITE_TOOL_NAMES:
            deny_tool("Refused: {} is written only by a person (the released area and phi.json "
                      "record what they let through).".format(target))
        if tool in SEARCH_TOOL_NAMES:
            folder = phi_policy.resolve(target, cwd)
            inside = [raw for raw, res in policy.hidden_roots() if phi_policy.is_under(res, folder)]
            if inside:
                deny_tool("Refused: searching {} would descend into {}. Search a narrower folder "
                          "that does not contain it.".format(target, ", ".join(inside)))


def main():
    raw = sys.stdin.read()
    event = json.loads(raw or "{}") or {}
    policy = phi_policy.load(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd"))
    if policy is None:
        allow()
    if is_shell(event):
        check_shell(policy, event)
    else:
        check_file_tool(policy, event)
    allow()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:  # fail closed: a broken guard must refuse, not wave through
        deny_tool("Refused: the PHI guard failed ({!r}), so it refuses rather than guess. "
                  "Fix the error or the project's .claude/phi.json.".format(err))
