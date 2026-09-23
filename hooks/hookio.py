"""Emit a hook decision in the form both Claude Code and Codex understand.

The two harnesses share a wire format. Codex 0.155.1 carries the same event
names, the same `tool_input` payload, and the same `hookSpecificOutput` /
`permissionDecision` decision object, so one hook script can serve both and
a rule does not have to be written twice and drift.

They differ in how a refusal is signalled. Claude Code accepts exit status 2
with the reason on stderr; that is the simpler path and it is what these
hooks used first. The structured JSON object is the form both document, so it
is what is emitted here, with status 0. A hook that returned both would leave
each harness to decide which one it meant.

Reasons are written for whoever has to act on them: what was refused, the
failure it prevents, and the command that does the right thing instead. A
refusal that only says no gets worked around.
"""

import json
import os
import sys

# Written for the oldest interpreter a hook may be handed. A user-level hook
# runs in whatever shell the harness provides, and depending on a newer
# interpreter would make the hook fail silently, which is the one failure a
# guard must not have.


def deny_tool(reason, event="PreToolUse"):
    """Refuse the tool call about to run, and say why."""
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.stdout.write("\n")
    sys.exit(0)


def block_stop(reason):
    """Refuse to end the turn, so the reply is revised before it is sent."""
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.stdout.write("\n")
    sys.exit(0)


def allow():
    """Say nothing and let the call through."""
    sys.exit(0)


def payload():
    """The event object on stdin, or an empty one when it cannot be read."""
    try:
        return json.loads(sys.stdin.read() or "{}") or {}
    except ValueError:
        return {}


# Codex names its tools `shell` and `apply_patch` where Claude Code names them
# `Bash`, `Write` and `Edit`, and Codex may hand the shell command as an argv
# list rather than one string. These two helpers absorb that so a rule is
# written once.
SHELL_TOOLS = ("Bash", "shell", "exec_command", "local_shell")
WRITE_TOOLS = ("Write", "Edit", "NotebookEdit", "apply_patch", "write_file",
               "edit_file")


def is_shell(event):
    """True when this event is a shell command, under either harness's name."""
    return (event.get("tool_name") or "") in SHELL_TOOLS


def command_text(event):
    """The shell command as one string, from either the string or argv form."""
    arguments = event.get("tool_input") or {}
    for key in ("command", "cmd", "script"):
        value = arguments.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, (list, tuple)) and value:
            parts = [str(part) for part in value]
            # `["bash", "-lc", "<script>"]` is how Codex wraps a shell line.
            # The script is the last element, and it is the only element that
            # should be read as a command: joining the whole argv puts `bash`
            # in command position, so a guard keyed on the command name sees
            # the wrapper instead of what actually runs.
            if len(parts) > 2 and os.path.basename(parts[0]) in (
                    "bash", "sh", "zsh", "dash") and parts[1].startswith("-"):
                return parts[-1]
            return " ".join(parts)
    return ""


def write_targets(event):
    """Paths a write-shaped tool call would create, under either harness."""
    arguments = event.get("tool_input") or {}
    found = []
    for key in ("file_path", "notebook_path", "path", "target_file"):
        value = arguments.get(key)
        if isinstance(value, str) and value:
            found.append(value)
    return found
