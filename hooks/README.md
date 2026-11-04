# Hooks

A hook is a script Claude Code or Codex runs before or after an agent action.
The ones here are guards: each refuses a tool call that would break a rule, and
says what to do instead. Each lives in the skill it belongs to, under
`skills/<name>/hooks/`. This folder holds only `hookio.py`, the helper they all
share, which each skill's `hooks/` folder links to.

| Skill | Hook | Refuses | Turned on |
| --- | --- | --- | --- |
| `working-with-phi` | `guard_phi.py` | in a project with `.claude/phi.json`: reading a protected or held folder, a job log outside the held area, `srun`/`salloc`/`ssh`, an agent-run `phi release` | automatically by the plugin, or per project by `phi settings --write` |
| | `phi_output_scan.py` | nothing; warns when output looks like it holds an identifier | same |
| | `guard_phi_prompt.py` | a prompt that looks like pasted data rows | same |
| `slurm` | `block_login_node_walks.py` | a recursive `find`, `rg`, `du` or `os.walk` over a shared filesystem from a login node | by hand, below; settings in `skills/slurm/README.md` |
| `humanize` | `guard_american_spelling.py` | a `git commit` that adds British spellings to prose, comments or strings | by hand, below |

Only hooks that do nothing until a project opts in turn themselves on. The
working-with-phi hooks stay silent without `.claude/phi.json`; the other two
would act in every repository, so you choose them.

## Why a hook and not a written rule

Every guard here replaces a rule that was written down, clear, and broken
anyway. A rule competes with every other rule for attention. A hook fires at
the moment the mistake is made, names what it prevents, and says what to do
instead.

Two properties keep them worth having. They refuse only what is near-certainly
wrong: a guard that fires on a legitimate command teaches people to route
around it, so each one was tested against real negatives as well as real
positives. And every refusal carries the fix: "Refused" alone gets worked
around; "submit it as a Slurm job, like this" gets satisfied.

## Which agents these work in

Claude Code and Codex. Both have a `PreToolUse` event that can refuse a call
and pass the same payload, so one script serves both. Other coding agents
(Cursor, Aider, Copilot's agent mode, Gemini CLI) have no point before a tool
runs where a guard could refuse it, so a rule that matters there has to stay
written down, in `AGENTS.md` or `CLAUDE.md`. Check before assuming a hook
covers everyone on a project: a rule removed from the prose because "the hook
catches it" protects nobody whose agent cannot run the hook.

## Turning one on by hand

Skills installed as Claude Code plugins register their own hooks where the
table says so. Otherwise, add the hook to the agent's settings, naming the
script by its absolute path in your clone (`H` below stands for
`~/ai-sci-skills/skills`, written out in full; the agents do not expand `~`
here).

**Claude Code**, in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {"type": "command", "command": "H/slurm/hooks/block_login_node_walks.py", "timeout": 10},
          {"type": "command", "command": "H/humanize/hooks/guard_american_spelling.py", "timeout": 60}
        ]
      }
    ]
  }
}
```

**Codex**, in `~/.codex/hooks.json`, with the same scripts. Codex names its
shell tool differently, so the matcher needs both names:
`"matcher": "Bash|shell|exec_command|local_shell"`. Codex runs only hooks it
has been shown: run `/hooks` in a Codex session and approve them, and again
after any change. `--dangerously-bypass-hook-trust` exists for automation that
already vets its hook sources; keep it out of a normal workflow.

Check with a command you expect to be refused, for example
`codex exec 'Run this and report any refusal verbatim: find / -name x'` on a
login node. A working install prints `hook: PreToolUse Blocked` and the
refusal.

## What `hookio.py` handles

Claude Code accepts a refusal as exit status 2 with the reason on stderr. Both
agents accept a structured JSON object, so that is what these emit, with
status 0:

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "..."}}
```

and for `Stop`, `{"decision": "block", "reason": "..."}`.

`command_text()` is the other half. Codex may hand a shell command as an argv
list, `["bash", "-lc", "<script>"]`. Joining that puts `bash` in command
position, so a guard keyed on the command name sees the wrapper instead of what
runs; `command_text()` returns the script. `commits()`, `added_lines()` and
`staged_text()` serve guards that act on `git commit`.

Write hooks for the oldest Python a hook might be handed, 3.6 on RHEL 8. A hook
that crashes on newer syntax fails silently, the one failure a guard must not
have.

## Writing another one

Put it in the skill it serves, under `hooks/`, with a link to the helper:
`ln -s ../../../hooks/hookio.py skills/<name>/hooks/hookio.py`. An installed
plugin is a copy of the skill's folder; a link like this is copied as the file
it points to.

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

If it should turn on with the plugin, add `hooks/hooks.json` to the skill, as
`skills/working-with-phi/hooks/hooks.json` does, and only if the hook does
nothing until a project opts in.
