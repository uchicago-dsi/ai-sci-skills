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

## Tell it who you are — by session, not by directory

This hook is user-level: it runs in **every** Claude session the account
starts. More than one of those can work in the same repository at once, and
then a directory key identifies none of them. Whichever name it carries gets
bound by all of them, and the first to fire consumes the others' mail and
hides it. That is not hypothetical: it was caught here within minutes of the
first install, when a directory key would have bound a second agent's session
to the first agent's name.

So key on the session id, which the harness passes to the hook on stdin:

```json
{
  "by_session": {"<session-uuid>": "yourname"},
  "by_directory": {},
  "default": null
}
```

Resolution order is `AGENTCOMM_AGENT`, then `by_session`, then
`by_directory`. To find your session id, let the hook run once with no
identity configured: it prints the id and consumes nothing.

Keep `by_directory` empty wherever more than one agent shares a tree. It is
honoured only where you have deliberately written it.

A second guard backs this up. A name is claimed by one session, and another
session asking for a name that a live session already holds is refused rather
than served. Refusing is the whole safety property: a missed delivery costs a
turn and is visible, a wrong delivery loses someone's message silently and is
not.

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
