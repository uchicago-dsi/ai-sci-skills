#!/usr/bin/env python3
"""Refuse a commit that adds British spellings to text a reader will see.

Anna writes American English, and British forms kept coming back into her
slides, notes and figure labels after being fixed. Most edits reach a file
through a shell script or a subagent, never through an editor tool, so a
check on the editor would miss them. Every path ends in `git commit`, so the
check sits there.

Only lines the commit adds are read, so a frozen notebook entry or an old
run's README that predates the rule never blocks. Prose files (Markdown,
Quarto, LaTeX, plain text) are read whole. In Python, only comments and
string literals that contain a space are read: that is where docstrings, plot labels, captions
and generated READMEs come from, and identifiers are literals that renaming
would break. The word list and the identifier exemptions live in
`british_spelling.py`.

When a hit is a quotation, a proper name or a third party's identifier that
must stay as written, put it in backticks, which are exempt.
"""
import io
import os
import re
import subprocess
import sys
import tokenize
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from british_spelling import find, strip_code  # noqa: E402
from guard_ruff_before_commit import commits, run  # noqa: E402
from hookio import allow, command_text, deny_tool, is_shell, payload  # noqa: E402

PROSE = (".md", ".qmd", ".rmd", ".tex", ".txt", ".rst")


def added_lines(toplevel):
    """{path: set of 1-based line numbers the staged diff adds}."""
    result = run(["git", "-C", toplevel, "diff", "--cached", "--unified=0",
                  "--no-color", "--diff-filter=ACMR"], timeout=30)
    if not result or result[0] != 0:
        return {}
    added, path, line = {}, None, 0
    for text in result[1].splitlines():
        if text.startswith("+++ "):
            path = text[6:] if text.startswith("+++ b/") else None
            continue
        hunk = re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", text)
        if hunk:
            line = int(hunk.group(1))
            continue
        if path and text.startswith("+") and not text.startswith("+++"):
            added.setdefault(path, set()).add(line)
            line += 1
    return added


def staged_text(toplevel, path):
    """The staged content of one file, or None."""
    try:
        done = subprocess.run(["git", "-C", toplevel, "show", ":" + path],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout.decode("utf-8", "replace") if done.returncode == 0 else None


def python_reader_text(source, lines):
    """Comments and string literals that start on the given lines."""
    pieces = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.start[0] not in lines:
                continue
            if token.type == tokenize.COMMENT:
                pieces.append(token.string)
            elif token.type == tokenize.STRING and re.search(r"\s", token.string):
                # A literal with no whitespace is a key, an arm name or a
                # path, which is an identifier; labels and captions have spaces.
                pieces.append(token.string)
            elif getattr(tokenize, "FSTRING_MIDDLE", None) == token.type:
                pieces.append(token.string)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return ""
    return "\n".join(pieces)


def main():
    event = payload()
    cwd = event.get("cwd") or os.getcwd()
    if not is_shell(event) or not commits(command_text(event)):
        allow()
    result = run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], timeout=20)
    if not result or result[0] != 0:
        allow()
    toplevel = result[1].strip()

    report = []
    for path, lines in sorted(added_lines(toplevel).items()):
        lower = path.lower()
        if not (lower.endswith(PROSE) or lower.endswith(".py")):
            continue
        source = staged_text(toplevel, path)
        if source is None:
            continue
        if lower.endswith(".py"):
            text = python_reader_text(source, lines)
        else:
            rows = source.split("\n")
            text = "\n".join(rows[n - 1] for n in sorted(lines) if n - 1 < len(rows))
        hits = find(strip_code(text))
        if hits:
            report.append("  %s: %s" % (path, ", ".join(
                "%s -> %s" % (word, american) for word, american in hits[:8])))
    if not report:
        allow()

    deny_tool(
        "Refused this commit: it adds British spellings to text a reader will see.\n\n"
        "%s\n\n"
        "Use the American form in prose, comments, docstrings and string "
        "literals (plot labels, captions, generated READMEs), then re-stage "
        "and commit. Identifiers, paths and run names are already exempt; a "
        "quotation or third-party name that must stay as written goes in "
        "backticks." % "\n".join(report[:20]))


if __name__ == "__main__":
    main()
