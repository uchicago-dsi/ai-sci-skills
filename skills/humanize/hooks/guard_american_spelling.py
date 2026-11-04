#!/usr/bin/env python3
"""Refuse a commit that adds British spellings to text a reader will see.

For writing in American English. British forms keep coming back into slides,
notes and figure labels after being fixed. Most edits reach a file
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
import sys
import tokenize
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from british_spelling import find, strip_code  # noqa: E402
from hookio import added_lines, allow, command_text, commits, deny_tool, is_shell, payload, run, staged_text  # noqa: E402

PROSE = (".md", ".qmd", ".rmd", ".tex", ".txt", ".rst")


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
    deny_tool("Refused this commit.\n\nBritish spellings in text a reader will see:\n%s\n"
              "Use the American form in prose, comments, docstrings and string literals (plot "
              "labels, captions, generated READMEs). Identifiers, paths and run names are already "
              "exempt. A quotation or third-party name that must stay as written goes in "
              "backticks. Fix, re-stage and commit again." % "\n".join(report[:20]))


if __name__ == "__main__":
    main()
