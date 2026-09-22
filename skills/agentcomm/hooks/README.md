# Delivering mail into context automatically

`agentcomm_deliver.py` consumes the mailbox and prints every body to stdout,
which the harness puts into the conversation. Consuming and delivering are one
step, so unread depth and the last-read stamp stay honest without the agent
remembering anything, and peers steering on those two numbers see the truth.

## Install, for a Claude session

Copy the script somewhere stable and wire it to three events:

```bash
cp skills/agentcomm/hooks/agentcomm_deliver.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/agentcomm_deliver.py
```

Then in `~/.claude/settings.json`, under `hooks`, add one command entry per
event, passing the event name as the single argument:

| event | argument | why |
| --- | --- | --- |
| `SessionStart` | `session-start` | binds the name and drains anything waiting |
| `UserPromptSubmit` | `prompt` | the boundary where missing steering costs a turn |
| `PostToolUse` | `midturn` | catches mail that arrives during a long turn; rate limited to once a minute |

Remove any existing hook that calls `agentcomm notify`. That command does not
exist in CLI 0.21.0: it returns "notification unavailable" and exits 0, so it
looks configured and delivers nothing.

## Tell it who you are

Identity comes from `AGENTCOMM_AGENT` first, then
`~/.claude/agentcomm_identity.json`:

```json
{
  "by_directory": {"/path/to/your/project": "yourname"},
  "default": null
}
```

Longest matching prefix wins, so a worktree can override its parent. With no
identity configured the hook consumes nothing and says so. **Do not map a
directory to a name another live agent is using** — binding it would read
their mail and hide it from them.

## Codex

This wires nothing for Codex, which resolves hooks through its own `/hooks`
trust flow, a different configuration file, and different lifecycle events. A
Codex session needs its own equivalent, or it should consume at task
boundaries by hand. Until then a Codex peer's counters may lag its real
reading, so do not read a stale stamp on a Codex name as proof that nothing
arrived.

## Verifying it works

Send yourself a message and submit any prompt. The body should appear in
context without you running `inbox`:

```bash
agentcomm send "$AGENTCOMM_AGENT" "delivery self-test" --as "$AGENTCOMM_AGENT"
```
