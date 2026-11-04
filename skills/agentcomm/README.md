# agentcomm

Gives several agents working on one problem a shared mailbox, so they can hand
off, ask each other questions, and say when something is done without a person
relaying it. Each agent binds a durable name; a roster shows who is reading;
and read state tells a peer whether a question has actually been picked up.

It is most useful across harnesses. Claude Code can already message other
Claude sessions directly, so two Claude agents need no help from this. A Claude
agent and a Codex agent can't see each other at all, and the mailbox is what
lets them coordinate.

`quota-saving-mode` uses the mailbox for the same reason, to deliver a wake-up
when a long job finishes so an agent doesn't poll for it. That skill ships
`await-notify` and `await-event` in its `bin/` for harnesses without built-in
background notification; Claude Code has its own and doesn't need them.

## Where to read next

- [`SKILL.md`](SKILL.md) is the skill itself: where to install the `agentcomm`
  command, how an agent binds a name once per session, why it must read by
  consuming so its counters stay true, and what may never go through the
  mailbox.
- [`hooks/README.md`](hooks/README.md) wires a Claude session so arriving mail
  is delivered into its context automatically, and explains why the hook keys
  on the session, never on the directory.
