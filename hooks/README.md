# Hooks

Guards that refuse a tool call which would break a rule, and say why. One set
of scripts serves both Claude Code and Codex.

`hookio.py` is a helper library, not an installer. It absorbs the two places
the harnesses differ so each rule is written once; the wiring below is
manual and has to be done per machine.

## Why a hook and not a written rule

Every guard here replaces a rule that was written down, clear, and broken
anyway. A rule competes with every other rule for attention. A hook does not:
it fires at the moment the mistake is made, names what it prevents, and says
what to do instead.

Two properties keep them worth having rather than worth disabling.

They refuse only what is near-certainly wrong. A guard that fires on a
legitimate command teaches people to route around it, so each one here was
tested against real negatives as well as real positives.

Every refusal carries the fix. "Refused" alone gets worked around; "create a
pinned worktree and submit from it, like this" gets satisfied.

## Which agents these work in

Claude Code and Codex, and nothing else yet.

Both expose a hook system with a `PreToolUse` event that can refuse a call,
and both pass the same payload, so one script serves both. Other coding
agents -- Cursor, Aider, Copilot's agent mode, Gemini CLI and the rest -- do
not currently expose a pre-tool interception point a guard could attach to.
Some have lifecycle or notification callbacks, which can tell you a thing
happened; none of those can refuse it before it runs, and a guard that only
reports is not a guard.

So a rule that matters in an agent other than these two has to stay written
down, in `AGENTS.md` or `CLAUDE.md`, where it competes for attention. Check
before assuming a hook covers everyone on a project: a rule removed from the
prose because "the hook catches it" protects nobody in an agent that cannot
run the hook.

## What each one does

| script | event | refuses |
| --- | --- | --- |
| `block_login_node_walks.py` | PreToolUse, shell | a recursive `find`/`rg`/`du`/`os.walk` over a large shared filesystem from a login node |
| `guard_slurm_submission.py` | PreToolUse, shell | `sbatch` from a shared checkout rather than a pinned worktree; a job name containing `smoke`, `probe`, `test`, `debug`, `pilot`, `placeholder` or `holder`; a submission with unread peer mail |
| `guard_protected_writes.py` | PreToolUse, shell and write tools | a write to a frozen lab notebook; a patient-derived image into `/tmp` or another shared temp directory |
| `guard_ruff_before_commit.py` | PreToolUse, shell | `git commit` whose staged Python has any ruff finding |
| `prose_lint.py` | Stop | an outgoing reply containing the padding phrases `CLAUDE.md` bans |

Several are specific to one project: `guard_slurm_submission.py`,
`guard_protected_writes.py` and `guard_ruff_before_commit.py` all key on a
`REPOSITORY` constant at the top of the file and allow everything outside it.
Change that constant, and the frozen-notebook list, for another project.

## Installing

Copy the scripts somewhere stable and make them executable. They import
`hookio` from their own directory, so keep them together.

```bash
mkdir -p ~/.claude/hooks
cp hooks/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py
```

### Claude Code

Add to `~/.claude/settings.json` under `hooks`. `H` below is the absolute
path to that directory; the harness does not expand `~` here.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": "H/block_login_node_walks.py", "timeout": 10},
          {"type": "command", "command": "H/guard_slurm_submission.py", "timeout": 20},
          {"type": "command", "command": "H/guard_ruff_before_commit.py", "timeout": 90}
        ]
      },
      {
        "matcher": "Bash|Write|Edit|NotebookEdit",
        "hooks": [{"type": "command", "command": "H/guard_protected_writes.py", "timeout": 20}]
      }
    ],
    "Stop": [
      {"hooks": [{"type": "command", "command": "H/prose_lint.py", "timeout": 15}]}
    ]
  }
}
```

### Codex

Same scripts, `~/.codex/hooks.json`, two differences in the wiring.

Codex names its tools `shell` and `apply_patch` where Claude names them
`Bash`, `Write` and `Edit`, so every matcher needs both sets:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|shell|exec_command|local_shell",
        "hooks": [
          {"type": "command", "command": "H/block_login_node_walks.py", "timeout": 10},
          {"type": "command", "command": "H/guard_slurm_submission.py", "timeout": 20},
          {"type": "command", "command": "H/guard_ruff_before_commit.py", "timeout": 90}
        ]
      },
      {
        "matcher": "Bash|shell|exec_command|local_shell|Write|Edit|NotebookEdit|apply_patch",
        "hooks": [{"type": "command", "command": "H/guard_protected_writes.py", "timeout": 20}]
      }
    ],
    "Stop": [
      {"hooks": [{"type": "command", "command": "H/prose_lint.py", "timeout": 15}]}
    ]
  }
}
```

Then trust them. Codex refuses to run a hook it has not been shown, and a
changed definition needs trust again: run `/hooks` in a Codex session and
approve. `--dangerously-bypass-hook-trust` exists for automation that already
vets its hook sources; do not put it in a normal workflow.

Verify rather than assume, with a command you expect to be refused:

```bash
codex exec 'Run this and report any refusal verbatim: sbatch --job-name=x /dev/null'
```

A working install prints `hook: PreToolUse Blocked` and the refusal text.

## What `hookio.py` handles

Claude Code accepts a refusal as exit status 2 with the reason on stderr.
Both harnesses accept the structured JSON object, so that is what these emit,
with status 0:

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "..."}}
```

and for `Stop`, `{"decision": "block", "reason": "..."}`.

`command_text()` is the other half. Codex may hand a shell command as an argv
list, `["bash", "-lc", "<script>"]`. Joining that puts `bash` in command
position, so a guard keyed on the command name sees the wrapper instead of
what runs; `command_text()` returns the script.

## Writing another one

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hookio import allow, command_text, deny_tool, is_shell, payload

def main():
    event = payload()
    if not is_shell(event):
        allow()
    if "rm -rf /" in command_text(event):
        deny_tool("Refused: that would delete the filesystem. Name the "
                  "directory you meant.")
    allow()

main()
```

Write them for the oldest interpreter a hook might be handed. A hook runs in
whatever shell the harness provides, and one that crashes on a new syntax
feature fails silently, which is the single failure a guard must not have.
