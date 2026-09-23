#!/usr/bin/env python3
"""Refuse recursive filesystem walks issued from a login node.

A login node is shared with the whole division, and a recursive descent of a
GPFS tree is metadata traffic that every other person on the node waits behind.
On 2026-09-22 three agent sessions each started one within an hour and CRI
raised the possibility of rebooting the node, which would have ended every
session on it. The written rule did not prevent that, so this checks instead.

The hook decides from the command text alone and never touches the filesystem:
a hook that stats a path can itself hang when the filesystem is the thing in
trouble, which is exactly when it runs. Paths are resolved lexically against
the session's working directory so that `find .` inside a GPFS checkout is
recognised for what it is.

Allowed through: anything on a compute node, anything inside a Slurm job, and
any walk bounded to depth 3 or less, which covers naming a known layout rather
than searching for one.
"""
import json
import os
import re
import shlex
import socket
import sys

BIG_ROOTS = ("/gpfs", "/ess")
LOGIN_NODE = re.compile(r"^cri\d+in\d+$")
MAX_OK_DEPTH = 3
SEGMENT_SPLIT = re.compile(r"(?:\|\||&&|[;&|\n])")

# Inline-code walks. A command can carry a whole heredoc, so these are matched
# against the raw text rather than against parsed arguments.
INLINE_WALK = re.compile(r"os\.walk\s*\(|\.rglob\s*\(|Path\.walk\s*\(|glob\.i?glob\s*\([^)]*\*\*")

# `cat > file <<'EOF'` writes text; `python <<'EOF'` runs it. Only the second
# is a walk, so the body of a written heredoc is dropped before anything is
# matched against it. Without this, saving a script that merely mentions
# `find /gpfs` is refused as though it had run one.
HEREDOC_START = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")
WRITER = re.compile(r"^\s*(?:cat|tee)\b[^|]*>")


def strip_written_heredocs(command):
    """Remove the bodies of heredocs that are being written to a file."""
    lines = command.split("\n")
    out, skip_until = [], None
    for line in lines:
        if skip_until is not None:
            if line.strip() == skip_until:
                skip_until = None
            continue
        out.append(line)
        m = HEREDOC_START.search(line)
        if m and WRITER.search(line):
            skip_until = m.group(2)
    return "\n".join(out)


def depth_bound(tokens):
    """Return the smallest explicit depth limit in tokens, or None if unbounded."""
    found = []
    for i, t in enumerate(tokens):
        if t in ("-maxdepth", "-d", "--max-depth") and i + 1 < len(tokens):
            v = tokens[i + 1]
            if v.isdigit():
                found.append(int(v))
        elif t.startswith("--max-depth="):
            v = t.split("=", 1)[1]
            if v.isdigit():
                found.append(int(v))
        elif re.fullmatch(r"-d\d+", t):
            found.append(int(t[2:]))
    return min(found) if found else None


def big_tree_targets(tokens, cwd):
    """Return the path arguments that land under a shared filesystem root.

    Resolution is lexical: the path is joined to the working directory and
    normalised, with no stat, readlink or existence check.
    """
    hits = []
    for t in tokens[1:]:
        if t.startswith("-"):
            continue
        p = os.path.normpath(t if os.path.isabs(t) else os.path.join(cwd, t))
        if p.startswith(BIG_ROOTS):
            hits.append(p)
    return hits


def verdict(command, cwd):
    """Return a refusal reason for command, or None to let it run."""
    command = strip_written_heredocs(command)
    for segment in SEGMENT_SPLIT.split(command):
        segment = segment.strip()
        if not segment:
            continue
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        if not tokens:
            continue

        verb = os.path.basename(tokens[0])
        if verb in ("sudo", "time", "nohup", "setsid", "nice", "ionice") and len(tokens) > 1:
            tokens = tokens[1:]
            verb = os.path.basename(tokens[0])

        if verb in ("locate", "updatedb"):
            return f"`{verb}` scans the whole filesystem index"

        if verb in ("find", "bfs", "du", "ncdu"):
            targets = big_tree_targets(tokens, cwd)
            if not targets:
                continue
            bound = depth_bound(tokens)
            if bound is None:
                return f"`{verb}` descends {targets[0]} with no depth limit"
            if bound > MAX_OK_DEPTH:
                return (f"`{verb} -maxdepth {bound}` on {targets[0]} is still a deep "
                        f"descent; {MAX_OK_DEPTH} is the limit here")
            continue

        if verb == "ls" and any(t.startswith("-") and "R" in t for t in tokens):
            targets = big_tree_targets(tokens, cwd)
            if targets:
                return f"`ls -R` recurses {targets[0]}"

        # ripgrep honours .gitignore, which keeps it off the derived trees. The
        # flags that defeat that turn it back into a full walk.
        if verb in ("rg", "ag", "grep"):
            unbounded = any(t in ("-u", "-uu", "-uuu", "--no-ignore", "--hidden") for t in tokens)
            recursive = verb != "grep" or any(
                t.startswith("-") and not t.startswith("--") and ("r" in t or "R" in t) for t in tokens)
            if unbounded and recursive and big_tree_targets(tokens, cwd):
                return f"`{verb}` with ignore rules disabled walks every file under the target"

    if INLINE_WALK.search(command) and (
            any(r in command for r in BIG_ROOTS) or cwd.startswith(BIG_ROOTS)):
        return "inline code walks a tree with os.walk, rglob or a ** glob"
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if payload.get("tool_name") != "Bash":
        sys.exit(0)
    if os.environ.get("SLURM_JOB_ID"):
        sys.exit(0)
    if not LOGIN_NODE.match(socket.gethostname().split(".")[0]):
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command", "")
    cwd = payload.get("cwd") or os.getcwd()
    reason = verdict(command, cwd)
    if not reason:
        sys.exit(0)

    print(
        f"Refused on {socket.gethostname().split('.')[0]}, a shared login node: {reason}.\n"
        "\n"
        "This node carries everyone's interactive sessions, and a GPFS tree descent is "
        "metadata traffic they all queue behind. Pick one:\n"
        "  - Read the manifest, census or receipt file the producer already wrote. This "
        "is almost always the right answer and it is also the fast one.\n"
        "  - Bound the walk to depth 3 or less by naming the layout you expect.\n"
        "  - Submit it to Slurm from a pinned worktree if it genuinely must enumerate "
        "a large tree.\n"
        "\n"
        "The rule is in AGENTS.md under Compute And Slurm. Do not work around this hook "
        "by renaming the command or splitting it up; if none of the three options fit, "
        "ask Anna.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
