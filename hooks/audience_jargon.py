"""Find project-private words in text written for an outside audience.

A deck or a manuscript is read by someone who never saw the pipeline. Words
that only mean something inside it -- "production" for whatever the current
pipeline happens to use, "mid-label" for one slice choice, a generation code
like G121, a run slug -- read as noise to that reader, and they kept coming
back into Anna's slides after being replaced. Each entry names the private
word and what to say instead.

This applies only to repositories that hold audience-facing writing (see
`is_audience_repository`). Code, configs and lab notebooks use these words
correctly, because their readers share the vocabulary.

Anything in backticks is exempt, and so are a Quarto deck's speaker notes,
which only the presenter reads.
"""

import os
import re

RULES = [
    (r"\b[Pp]roduction(?:'s)?\b", "name the thing: 'the 26-exam Fan5 curve', 'the 30 mm slice', 'the pipeline's current fit'"),
    (r"\bmid-?label\b", "'the slice halfway along the segmented aorta' (or 'mid-aorta slice')"),
    (r"\bG1\d\d\b", "a generation code; say what data it is, or cut it"),
    # Joined to a path, a dot, a LaTeX label or brace, it is a file or label, not prose.
    (r"(?<![\w/.:{])[a-z0-9]+(?:_[a-z0-9]+){3,}(?![\w/]|\.\w)", "a run or file name; say what it is, or move it to the notes"),
]
COMPILED = [(re.compile(p), fix) for p, fix in RULES]

# Path components and repository-name suffixes that mark audience writing.
AUDIENCE_COMPONENTS = {"presentations", "papers", "manuscripts"}
AUDIENCE_SUFFIXES = ("-paper", "_paper")


def is_audience_repository(toplevel):
    """True when this repository holds decks or manuscripts."""
    parts = os.path.realpath(toplevel).split(os.sep)
    return bool(AUDIENCE_COMPONENTS.intersection(parts)) or parts[-1].endswith(AUDIENCE_SUFFIXES)


def notes_lines(text):
    """1-based line numbers inside Quarto `::: {.notes}` blocks."""
    inside, depth, lines = False, 0, set()
    for number, line in enumerate(text.split("\n"), start=1):
        stripped = line.strip()
        if not inside and re.match(r"^:{3,}\s*\{\s*\.notes\s*\}", stripped):
            inside, depth = True, 1
            lines.add(number)
            continue
        if inside:
            lines.add(number)
            if re.match(r"^:{3,}\s*\{", stripped):
                depth += 1
            elif re.match(r"^:{3,}\s*$", stripped):
                depth -= 1
                if depth == 0:
                    inside = False
    return lines


def find(text):
    """[(private word as written, what to say instead)], one per distinct word."""
    seen, hits = set(), []
    for pattern, fix in COMPILED:
        for match in pattern.finditer(text):
            word = match.group(0)
            if word.lower() in seen:
                continue
            seen.add(word.lower())
            hits.append((word, fix))
    return hits
