#!/usr/bin/env python3
"""Drop a prompt that looks like pasted data rows before the model sees it.

Active only in a project with `.claude/phi.json`. A prompt is dropped when it has
a header naming a key column (`mrn`, `patient_id`, `accession`, ... plus the
project's `key_columns`) and at least three lines shaped like records: three or
more delimited fields, two of them numbers or dates. Paths and file names pass.

Claude Code shows the reason to the person and not to the model, and is asked not
to repeat the prompt in that message. The typed text can still be stored in the
local session transcript and prompt history, so this catches an accidental paste;
it does not make pasting safe.

Adapted from the clif-sensitive-data-demo's no-pasted-rows.py
(https://github.com/kaveriC/clif-sensitive-data-demo). Any error drops the prompt.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phi_policy  # noqa: E402

VALUE = re.compile(r"-?\d+(\.\d+)?|\d{4}-\d{2}-\d{2}(\s\d{2}:\d{2}(:\d{2})?)?|\d{1,2}/\d{1,2}/\d{2,4}")


def is_record(line):
    fields = [f.strip() for f in re.split(r"[,\t|]|\s{2,}", line.strip()) if f.strip()]
    return len(fields) >= 3 and sum(bool(VALUE.fullmatch(f)) for f in fields) >= 2


def block(reason):
    sys.stdout.write(json.dumps({
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "suppressOriginalPrompt": True},
    }) + "\n")
    sys.exit(0)


def main():
    event = json.loads(sys.stdin.read() or "{}") or {}
    policy = phi_policy.load(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd"))
    if policy is None:
        return
    lines = (event.get("prompt") or "").splitlines()
    key = re.compile(r"\b(" + "|".join(re.escape(c) for c in policy.key_columns) + r")\b", re.I)
    if any(key.search(line) for line in lines) and sum(map(is_record, lines)) >= 3:
        block("Dropped before the model saw it: this prompt looks like pasted data rows. Describe the "
              "data instead (columns, types, counts), or put it in a job's output and release a review.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:
        block("Dropped: the pasted-rows check failed ({!r}), so it drops the prompt rather than "
              "guess.".format(err))
    sys.exit(0)
