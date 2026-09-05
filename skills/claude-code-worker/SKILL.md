---
name: claude-code-worker
description: "Delegate a bounded coding, review, or research subtask from Codex to Claude Code in an isolated Git worktree, then continue the same Claude session with follow-up turns. Use when the user explicitly asks for Claude/Claude Code delegation, asks to save Codex quota with Claude, or requests a Claude worker that can inspect and edit a repository. Do not use for PHI, credentials, authoritative imaging, source-data mutation, external publication, or a task that cannot safely be isolated."
---

# Claude Code Worker

Use Claude as a write-capable external worker while Codex remains the supervising owner.
The worker is conversational across invocations, but it does not inherit the Codex thread or
native tool state. Give it a compact, self-contained prompt and verify its work yourself.

## Before Launch

1. Read the repository's applicable `AGENTS.md` and task instructions yourself.
2. Choose one concrete, bounded task with an inspectable result.
3. Create a dedicated clean Git worktree under the repository's configured worktree root.
   Do not point Claude at a shared checkout or an execution checkout bound to a live job.
4. Create the state directory outside the worktree. Use a protected directory when the
   prompt or result is private. Never put PHI, credentials, patient identifiers, source
   imaging, or protected clinical text in the prompt or worker-visible paths.
5. Write a self-contained prompt that includes:
   - the exact outcome and boundaries;
   - relevant user constraints and applicable repository rules;
   - current evidence and file paths needed for the task;
   - verification expected from the worker;
   - whether it may commit (default: no);
   - an instruction to report changed files, checks, findings, and blockers.

## Start And Continue

Run the bundled bridge from the repository that owns the worktree:

```bash
python "$CODEX_HOME/skills/claude-code-worker/scripts/run_claude_worker.py" start \
  --workdir "$WORKTREE" \
  --prompt-file "$PROMPT_FILE" \
  --state-dir "$STATE_DIR"
```

The default is intentionally the strongest available Claude worker: Opus, high
effort, autonomous tool use, unrestricted turn count, and write plus shell tools. Safety
comes from Claude restricted/safe mode and the isolated worktree, not from making the
worker read-only. The bridge does not use `--no-session-persistence`; it records the
Claude session ID and raw JSON result under the state directory.

Send a follow-up turn to the same worker conversation:

```bash
python "$CODEX_HOME/skills/claude-code-worker/scripts/run_claude_worker.py" followup \
  --state-dir "$STATE_DIR" \
  --prompt-file "$FOLLOWUP_PROMPT_FILE"
```

Use follow-ups for correction, missing tests, or a focused question. Do not hand the
worker a second unrelated task; start another isolated session instead.

## Recover From Quota Limits

The bridge recognizes quota errors even when Claude exits successfully with
`is_error: true`. It returns exit code **75** and structured `status`, `retry_at`
and `quota_path` fields, preserving the worker session and every attempted turn.
The default cooldown ledger is `~/.cache/claude-code-worker/quota.json`, shared
across workers using the same Claude account. Use `--quota-file` consistently on
all commands if separate accounts need separate ledgers; do not switch accounts,
models or paid usage to evade a limit.

- Keep doing independent authorized work. Record the returned UTC `retry_at` in
  the existing task state and check it at natural work boundaries. Do not label
  the worker completed or abandon Claude for the rest of the goal.
- During cooldown, use native Codex subagents for bounded work when the user
  permits that fallback. They consume Codex quota; do not infer permission from
  a request to save Codex quota with Claude. Pass compact task context, not the
  full conversation, and preserve the same scope and safety boundaries.
- Keep one owner per task. Before transferring unfinished Claude work to Codex,
  confirm the Claude invocation has ended, inspect its partial work, and record
  the transfer in existing task state. Give Codex only the remaining scope;
  never run both workers on the same task or write set.
- `python <skill-dir>/scripts/run_claude_worker.py availability` is a local-only
  check. `waiting` means the cooldown is active; `probe_due` means the time has
  elapsed, **not** that access is restored.
- At `retry_at`, run the same command with `--probe`. This performs one tiny
  tool-free, non-persistent request using the worker model (Opus by default).
  It does not execute the pending task. Before the deadline it makes no request.
  A recognized new limit refreshes the cooldown; other failures need diagnosis.
- On `available`, prefer Claude again for new delegations and relevant paused
  follow-ups. Let already-assigned Codex tasks finish; do not restart them in
  Claude. For a task still owned by Claude, inspect its partial changes and
  current relevance, then resume its same session with `followup` for only the
  unfinished work. Reconcile any completed Codex work before a later Claude
  follow-up; never replay a superseded or already-completed action.
- A time-only reset with an explicit IANA timezone is interpreted as the next
  occurrence plus 60 seconds. Unknown reset formats use a 15-minute backoff.
  If quota is the only remaining wait, retain the task and use the product's
  interruptible wait mechanism, with at most 60 seconds between control returns.

The supervisor owns this loop while active; the helper does not install a daemon
or wake an ended session. Concurrent probes are locked, and worker state is locked
per session so a retry cannot overwrite the failed turn's evidence.

## Supervise And Integrate

- Inspect the worktree diff, status, and commands/tests reported by Claude.
- Run the relevant verification independently. Treat Claude's report as a claim, not
  evidence.
- Steer with another follow-up when the same bounded task needs correction.
- Codex owns staging, integration, conflict handling, and user-facing conclusions unless
  the initial prompt explicitly assigned a worktree-local commit.
- Stop after the requested outcome or an explicit blocker. Do not use the bridge to evade
  repository safety rules or broaden authority.

Read [references/communication.md](references/communication.md) when explaining how this
bridge differs from native Codex subagents.
