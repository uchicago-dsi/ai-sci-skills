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

When AgentCom is available, it supplies the missing coordination channel without changing
the model or quota owner. Use one named mailbox per Claude worker for the assignment,
acknowledgement, questions, corrections, and completion notice. Keep messages concise and
put bulky evidence in the isolated worktree or state directory, referenced by exact path.
AgentCom does not wake an ended model session by itself, preserve Claude conversation
state, authenticate agent names, or make shared files safe; the bridge and worktree rules
still own those responsibilities.

## Efficient synchronous pattern

For a one-shot task, call `scripts/run_agentcomm_worker.py` once and keep process
waiting inside the same `functions.exec` orchestration. Substitute explicit,
already-validated paths and names:

```javascript
let run = await tools.exec_command({
  cmd: "python <skill-dir>/scripts/run_agentcomm_worker.py --repo <repo> --workdir <worktree> --task-file <task> --state-dir <state> --supervisor <supervisor> --worker <worker> --agentcomm <agentcomm>",
  workdir: "<repo>",
  yield_time_ms: 30000,
  max_output_tokens: 4000,
  login: false,
});
while (run.session_id) {
  run = await tools.write_stdin({
    session_id: run.session_id,
    chars: "",
    yield_time_ms: 55000,
    max_output_tokens: 4000,
  });
  if (run.session_id) notify("Claude worker is still running; Codex remains asleep.");
}
text(run.output);
```

Do not return the intermediate session ID to the model and then issue separate
poll turns. Do not fetch acknowledgement or completion mail after a successful
bridge return: those messages are durable coordination evidence, while the
bridge response is the synchronous result. Read the mailbox only when a live
question needs a decision or when diagnosing a failed bridge.

The short internal waits above are not separate model turns: `functions.exec` owns the loop.
They allow a tool notification at least once per minute while preserving one supervisor wakeup.
Do not run concurrent `write_stdin` calls against the same session.

## Concurrent supervisor pattern

When the supervisor must work on something else, launch the same helper with a short tool yield,
retain its returned process/session handle, and continue. Poll it only at a natural boundary.
This does not reduce worker capability, but each return to Codex consumes supervisor tokens and
may reload substantial context. AgentCom completion is durable but does not itself wake Codex.

Do not call this “free concurrency.” Use the quota-saver pattern for one bounded critical-path
task and the concurrent pattern only when useful parallel reasoning outweighs the measured token
cost.
