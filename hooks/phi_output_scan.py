#!/usr/bin/env python3
"""After a tool runs, warn when its output looks like it holds an identifier.

Active only in a project with `.claude/phi.json`. The output is already in the
session by the time this runs, so it cannot prevent anything; it tells the agent
to stop and not repeat what it saw, and the person to check how it got there.
It looks for record numbers, Social Security numbers, birth dates, and any
patterns the project adds under `identifier_patterns`.

Adapted from the CLIF clif-icu plugin's hooks/phi_scan.py
(https://github.com/Common-Longitudinal-ICU-data-Format/skills). Advisory, so an
error here lets the session continue.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phi_policy  # noqa: E402


def text_of(value, depth=0):
    if depth > 8:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        return " ".join(text_of(v, depth + 1) for v in value.values())
    if isinstance(value, list):
        return " ".join(text_of(v, depth + 1) for v in value)
    return ""


def main():
    event = json.loads(sys.stdin.read() or "{}") or {}
    policy = phi_policy.load(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd"))
    if policy is None:
        return
    hits = sorted({label for _, labels in policy.flag_lines(text_of(event.get("tool_response"))[:200000]) for label in labels})
    if hits:
        sys.stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "PHI scan: this tool output contains text shaped like " + ", ".join(hits) + ". Stop. "
                "Do not repeat, summarize or reason about those values. Tell the person which command "
                "produced it so they can check whether protected data reached the session; if it is "
                "invented or public data, they will say so."),
        }}) + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
