#!/usr/bin/env python3
"""Refuse a write to a frozen notebook or a patient image into a shared temp.

Two AGENTS.md rules about where output goes. Both are silent when broken --
the write succeeds, nothing fails, and the damage is found later by someone
reading the wrong file or auditing a temp directory -- so neither is caught
by the ordinary way mistakes surface here.

A frozen notebook. `docs/lab_notebook_randi_hfdp.md` was closed at the
2026-09-04 cutover and is read-only; `docs/lab_notebook_randi.md` is a
routing index and never carries entries. Appending to either puts a result
where the lane that owns it will not find it, and the entry then has to be
moved by hand with its place in the history already lost.

Patient imaging into `/tmp`. This is a Critical Invariant. QC images, contact
sheets, montages and visual debug artifacts derived from clinical imaging
belong under the run root with restrictive permissions. A shared temp
directory is world-traversable and outlives the session that wrote it.

Both checks work on the path alone and never open a file. The temp check
looks at the destination of a redirect or a `--output`-style argument as
well as at tool arguments, because the ad-hoc probe is where this actually
happens: the committed renderer writes where it is told, and the throwaway
matplotlib one-liner writes to `/tmp/x.png`.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hookio import allow, command_text, deny_tool, is_shell, payload, write_targets  # noqa: E402

REPOSITORY = "/gpfs/data/karczmar-lab/hfdp"
# Read-only by rule. Relative names are matched against the repository root.
FROZEN_NOTEBOOKS = {
    "docs/lab_notebook.md": "a routing-only index that never carries entries",
    "docs/lab_notebook_randi.md": "the routing index; entries go to a lane notebook",
    "docs/lab_notebook_randi_hfdp.md":
        "frozen historical at the 2026-09-04 cutover; read it, never append",
}
SHARED_TEMP = ("/tmp/", "/var/tmp/", "/dev/shm/")
IMAGE = re.compile(r"\.(png|jpg|jpeg|tif|tiff|gif|pdf|svg|webp|nii|nii\.gz|dcm)$",
                   re.IGNORECASE)
# Destinations a command names explicitly: a redirect, or a flag whose value
# is a path. Both are how a one-off render chooses where to put its output.
DESTINATION = re.compile(
    r">>?\s*(\S+)|--(?:out|output|output-?(?:file|path|dir|root)|save|savefig|dest)[= ]\s*(\S+)")


def resolved(path, cwd):
    """An absolute path for a tool argument, without touching the filesystem."""
    text = str(path).strip().strip("'\"")
    if not text:
        return None
    return os.path.normpath(text if os.path.isabs(text)
                            else os.path.join(cwd, text))


def frozen_notebook(absolute):
    """The reason this path is read-only, or None."""
    for relative, why in FROZEN_NOTEBOOKS.items():
        if absolute == os.path.join(REPOSITORY, relative):
            return relative, why
    return None


def imaging_into_temp(absolute):
    """True when this writes an image-shaped file into a shared temp directory."""
    return absolute.startswith(SHARED_TEMP) and bool(IMAGE.search(absolute))


def candidates(event, cwd):
    """Every path this call would write, as absolute paths."""
    found = [resolved(p, cwd) for p in write_targets(event)]
    if is_shell(event):
        command = command_text(event)
        for match in DESTINATION.finditer(command):
            target = match.group(1) or match.group(2)
            if target and not target.startswith("/dev/"):
                found.append(resolved(target, cwd))
        # A quoted image path anywhere in a heredoc or a python -c body.
        for quoted in re.findall(r"""['"]([^'"\s]+\.[A-Za-z]{3,4})['"]""", command):
            found.append(resolved(quoted, cwd))
    return [p for p in found if p]


def main():
    event = payload()
    cwd = event.get("cwd") or os.getcwd()
    for absolute in candidates(event, cwd):
        notebook = frozen_notebook(absolute)
        if notebook:
            deny_tool(
                "Refused a write to %s: %s.\n\n"
                "Route the entry to the registered lane notebook indexed in "
                "docs/lab_notebooks/README.md -- for arterial and AIF work "
                "that is docs/lab_notebooks/arterial_input.md. A transient "
                "session appends to the lane whose work it is doing rather "
                "than opening its own.\n\n"
                "The rule is in AGENTS.md under Logging, Reporting, And "
                "Provenance." % (notebook[0], notebook[1]))
        if imaging_into_temp(absolute):
            deny_tool(
                "Refused writing %s into a shared temp directory.\n\n"
                "This is a Critical Invariant: QC images, contact sheets, "
                "montages and visual debug artifacts from clinical imaging go "
                "under the relevant output or run root with restrictive "
                "permissions, never /tmp. A shared temp directory is "
                "world-traversable and outlives this session.\n\n"
                "Write it under outputs/runs/<run>/ and chmod the directory "
                "to 700. If the image is genuinely not patient-derived, say "
                "so and put it in the session scratchpad instead."
                % absolute)
    allow()


if __name__ == "__main__":
    main()
