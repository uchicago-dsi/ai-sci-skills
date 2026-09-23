#!/usr/bin/env python3
"""Refuse a commit whose staged Python does not pass the project's ruff.

The rule is to run `ruff check` on changed paths before committing and to
report anything pre-existing. It is easy to skip because nothing fails when
you do: the commit succeeds and the finding surfaces later, in someone
else's diff or in a run that already spent its compute.

Ruff is resolved the way wrappers resolve Python -- the sibling of
`HFDP_PYTHON` inside the configured environment -- because a bare `ruff` on
PATH is whichever environment the shell happened to have, and a
`required-version` refusal means the wrong binary answered. If that binary
is missing this allows the commit through and says so, since a guard that
cannot run its own check has no standing to block.

Any finding in a staged Python file blocks, including one that was already
there. The rule asks for pre-existing findings to be reported, and a commit
that touches a file is the moment someone is looking at it. The refusal says
how to proceed when a finding is not yours: name it in the commit message
and commit again.
"""
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hookio import allow, command_text, deny_tool, is_shell, payload  # noqa: E402

REPOSITORY = "/gpfs/data/karczmar-lab/hfdp"
PREFIXES = ("exec", "sudo", "nohup", "time", "command", "env")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def commits(command):
    """True when this command line actually runs `git commit`."""
    for segment in re.split(r"(?:\|\||&&|[;&|\n])", command):
        if "<<" in segment:
            break
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        while words and (ASSIGNMENT.match(words[0]) or words[0] in PREFIXES):
            words.pop(0)
        if not words or os.path.basename(words[0]) != "git":
            continue
        # Skip git's own options to reach the subcommand: `git -C path commit`.
        rest = words[1:]
        while rest and rest[0].startswith("-"):
            rest.pop(0)
            if rest and not rest[0].startswith("-"):
                rest.pop(0)
        if rest and rest[0] == "commit":
            return True
    return False


def run(arguments, cwd=None, timeout=60):
    """One bounded subprocess, or None when it cannot be run."""
    try:
        done = subprocess.run(arguments, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, timeout=timeout, cwd=cwd)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.returncode, done.stdout.decode("utf-8", "replace")


def ruff_binary():
    """The environment's own ruff, or None."""
    prefix = os.environ.get("MAMBA_ROOT_PREFIX")
    name = os.environ.get("HFDP_ENV_NAME", "hfdp")
    if not prefix:
        return None
    candidate = Path(prefix) / "envs" / name / "bin" / "ruff"
    return candidate if candidate.is_file() and os.access(candidate, os.X_OK) else None


def staged_python(cwd):
    """Staged Python files, as repository-relative paths."""
    result = run(["git", "-C", cwd, "diff", "--cached", "--name-only",
                  "--diff-filter=ACMR"], timeout=20)
    if not result or result[0] != 0:
        return []
    return [line for line in result[1].splitlines() if line.endswith(".py")]


def findings(binary, cwd, paths):
    """Ruff's findings for these paths: how many, and the concise listing.

    `--output-format=concise` is one line per finding. The default format
    spreads each over a source excerpt, and counting those lines reported
    two unused imports as seventeen problems -- a count with no denominator
    anyone could check, which is the failure mode this project has most
    often had.
    """
    existing = [p for p in paths if (Path(cwd) / p).is_file()]
    if not existing:
        return 0, ""
    result = run([str(binary), "check", "--output-format=concise"] + existing, cwd=cwd)
    if not result:
        return 0, ""
    lines = [line for line in result[1].splitlines()
             if line.strip() and not line.startswith("Found ")
             and "fixable with" not in line]
    return len(lines), "\n".join(lines)


def main():
    event = payload()
    cwd = event.get("cwd") or os.getcwd()
    if not is_shell(event) or not commits(command_text(event)):
        allow()

    result = run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], timeout=20)
    if not result or result[0] != 0:
        allow()
    toplevel = result[1].strip()
    if os.path.realpath(toplevel) != REPOSITORY:
        allow()

    paths = staged_python(toplevel)
    if not paths:
        allow()
    binary = ruff_binary()
    if binary is None:
        allow()

    count, report = findings(binary, toplevel, paths)
    if not count:
        allow()

    deny_tool(
        "Refused this commit: ruff reports %d finding(s) in the staged Python.\n\n"
        "%s\n"
        "Ruff is the project's required linter and the rule is to run it on "
        "changed paths before committing. Fix them, or if a finding is "
        "pre-existing in a file you only touched, say so explicitly in the "
        "commit message and re-run -- do not silence it with --isolated, "
        "--config, or a hand-picked rule selection, which means the wrong "
        "binary or the wrong ruleset answered.\n\n"
        "Checked with %s across: %s"
        % (count, report.strip()[:1500], binary, ", ".join(paths[:12])))


if __name__ == "__main__":
    main()
