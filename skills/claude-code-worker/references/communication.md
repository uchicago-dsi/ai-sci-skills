# Communication model

Native Codex subagents are part of the same orchestration system. The parent can launch a
worker with forked conversation context, send messages while it runs, trigger follow-up
turns, interrupt it, wait for updates, and receive a structured final result. This is a
real multi-turn supervisory channel, not one fixed prompt. It is operationally efficient
because context transfer and coordination are built into the agent runtime, although each
worker still consumes model tokens and concurrent workers can increase total usage.

Claude Code is an external CLI process. It does not inherit the Codex conversation or
native tools. The supervising Codex agent must serialize the task into an initial prompt,
inspect the returned JSON, and explicitly resume the saved Claude session for each
follow-up. Session persistence makes the worker conversational, but live unsolicited
messages do not flow between Codex and Claude. The bridge therefore approximates native
subagent steering as a sequence of `start` and `followup` calls.
