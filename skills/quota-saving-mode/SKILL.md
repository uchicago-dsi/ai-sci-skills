---
name: quota-saving-mode
description: Reduce model quota spent on repeated supervision, polling, context loading, and status chatter when the user asks for quota-saving operation. Preserve scientific rigor and task quality; do not silently downgrade models or narrow the goal.
---

# Quota-Saving Mode

Spend reasoning on decisions, implementation and verification—not repeatedly
rediscovering unchanged state. This is an operating preference, not a runtime
setting or a guarantee about billed usage. Follow required progress reporting,
tool wait limits, safety rules and the user's model choices.

## Default operating loop

- Choose a meaningful next decision boundary and the evidence that would change
  the action. Work through a coherent block instead of ending a turn after each
  healthy poll; an automatically resumed goal can otherwise become a costly
  status loop. Do not pause an authorized goal merely to save quota.
- Separate **mechanical health checks** from **scientific review**. Check startup
  and unfamiliar failure modes promptly. Once healthy, use the existing expected
  cadence: ordinarily minutes for cheap process/error checks, a checkpoint or
  roughly 15–30 minutes for substantive interpretation. Shorten this when delayed
  action would lose evidence, leave resources idle or miss a deadline. These are
  defaults, not permission to weaken a required monitor.
- Prefer existing completion signals or native interruptible waits. Where tools
  support it, keep repeated short waits and cheap status checks inside one
  composed tool execution; return to model reasoning for a result, error,
  deadline, user steering or decision-changing evidence. Obey per-call wait
  limits rather than issuing an uninterruptible long sleep. Never infer terminal
  failure from a timeout or stale log alone; verify the same live handle. The
  concrete form of this is the next section, and it is not optional: a `wait`
  loop is the single largest avoidable cost this skill exists to prevent.
- Give substantive user updates at milestones, failures, decisions or requests,
  not after every poll. Use the smallest permitted heartbeat when higher-priority
  instructions require more frequent progress reports. Do not promise to remove
  runtime-mandated updates or control CLI wakeups that tools do not expose.

## Never wait in the model's loop

Polling is free. Re-entering the model is not. Every tool return replays the
whole context so the model can decide one thing, and when that thing is "still
running" the request was wasted. One measured session spent 40.6% of its input
tokens this way, and a single background cell was waited on 64 consecutive
times.

Two rules follow, and the second matters more than the first.

**Never call `wait` in a loop.** Not once. If a `wait` returns "still running",
that request bought nothing.

**Never block either.** A long-blocking tool call suspends the agent, which is
worse than the polling it replaces: a 45-minute run would make the session
unusable for 45 minutes. Codex also clamps `exec_command` to 30 seconds and
degrades silently somewhere past 8-13 minutes of looped calls, so long blocks
are unreliable as well as unusable.

The correct shape is the one a human uses: start the work, leave, be told.

### Start detached, register a watcher, keep working

1. Launch the job so it survives and returns immediately -- `sbatch`, or
   `setsid ... </dev/null >log 2>&1 &` for a local process. Do not hold a cell.
2. Register an out-of-process watcher that will wake this session when the job
   reaches a terminal state. The watcher blocks; the agent does not.
3. Go do the next piece of real work. Do not check back.

The wake-up arrives as an ordinary user turn. Codex accepts injected messages
while a session is live: an idle session takes them immediately, and a busy one
shows `Messages to be submitted after next tool call` and delivers at the next
turn boundary. Either way the cost is exactly one model request per real event,
which is the floor.

Which watcher you need depends on the harness.

Claude Code already has this built in, so it needs no extra tool: start the work
with a background task and the harness re-invokes the session when it exits, and
a `Monitor` with an until-loop waits on a condition. Use those. Reach for the
scripts below only for a wake-up the harness cannot see, such as a Slurm job it
is not tracking.

Codex has no equivalent, so it needs an out-of-process watcher. `await-notify`
and `await-event` ship in this repository's `bin/` for that case.

`await-notify` registers that watcher. It returns immediately with a receipt
and the waiting happens in a detached process:

```
await-notify --to <tmux-target> [options] -- <await-event args...>
  --to TARGET       tmux session or session:window.pane to wake (required)
  --mailbox AGENT   also send the full detail via `agentcomm send AGENT`
  --label TEXT      short human name for the thing being watched
  --timeout S       give up after S seconds total (default 86400)
  --interval S      seconds between internal polls (default 30)
```

```bash
sbatch scripts/slurm_fan_fit.sh            # -> Submitted batch job 15233526
await-notify --to <agent-session> --mailbox <agent-name> --label "fan fit" -- slurm 15233526
# {"event":"watch_registered","watch_id":"...","ledger":"..."}
# then go do something else; the wake-up arrives as:
# EVENT (fan fit): {"event":"slurm_terminal","state":"COMPLETED","exit_code":"0:0",...}
```

It refuses to register against a tmux session that does not exist, because a
watcher whose wake-up can never land is indistinguishable from a job that never
finished. Every registration, firing, and delivery appends to a ledger under
`~/.local/state/await-notify/`, so a failure to deliver is visible rather than
silent.

Detail goes to the mailbox and the pane gets the short notice, which is the
established split: keep PHI, identifiers and source excerpts out of both.

`await-event` is the detector underneath, useful directly only in a shell:

```
await-event slurm 12345 [more ids...]   any listed job reaches a terminal state
await-event file <path>                 path exists and its size stops changing
await-event pid <pid>                   process exits
await-event log <path> <regex>          regex appears in newly appended bytes
await-event cmd <command...>            command exits 0
  --interval S    seconds between internal polls (default 30)
  --max-block S   give up and report still_waiting after S seconds (default 900)
```

It prints one JSON line and nothing before it. Exit 0 fired, 10 still waiting,
2 usage error.

### If no watcher is available

Fall back to the job's own completion signal -- a Slurm dependency, an epilog
that writes a marker, a `--mail-type` hook -- and check it when you next have a
reason to run a command anyway. Never open a poll loop just to look.

Where a check genuinely cannot be deferred, one bounded `await-event` call of
20 seconds inside a single tool execution is acceptable. A second consecutive
one is not: that is a poll loop with extra steps.

### Verify the watcher before trusting its silence

A wait condition that can never fire reports the same quiet as a healthy run,
and it is the easier half to get wrong because the output filter is the half you
think about. Key it on a pid, an exit marker, or a file the work writes -- never
a `pgrep -f` on the command being watched, which matches the watching shell's
own arguments. Prove it fires on a real positive before relying on it.

## Delegate once, review once

- Delegate only when authorized and a bounded task repays setup/review overhead.
  Prefer a coherent 30–90 minute task with explicit scope, acceptance checks,
  artifact paths and one final report over many tiny assignments.
- With an applicable worker skill, follow its quota-saving orchestration rather
  than duplicating its protocol. Default to zero intermediate code reviews and
  one risk-appropriate final review. Concurrent supervisor reasoning needs a
  named decision it can advance while the worker runs.
- Do not repeat a worker's whole investigation or inspect every delegated QC
  image. Independently verify consequential claims, inspect flagged failures and
  an appropriate sample, and expand review when evidence warrants it. Batch
  findings; avoid routine correction round-trips.
- Keep the requested model/effort. Cheaper routing is an explicit choice, not a
  hidden quality cut. External workers still incur briefing and review cost.

## Keep context and records lean

- Read mandatory instructions fully; afterward reuse unchanged instructions
  already present in context. Retrieve exact files, changed log tails and relevant
  fields, not complete histories, giant directory listings or repeated manuals.
- Batch independent reads/checks and cap output to what can change the decision.
  Do not dump a full worker transcript beside its final report and patch.
- Maintain one concise current-state note plus authoritative result artifacts.
  Record interventions and findings, not every healthy poll. Preserve the full
  objective, uncertainty, provenance and next action without repeating the campaign.

## Never economize away the result

Preserve protected-data boundaries, temporal fidelity, untouched splits, matched
denominators, code review and required scientific/QC checks. Do not shorten a
necessary experiment or call an unreviewed artifact successful to save tokens.
Do not add monitoring infrastructure, change permissions or edit global runtime
settings merely because this skill is active.

Assess savings using actual usage when available, plus supervisor interventions,
repeated reads and repair time. Those counts are proxies, not a conversion to
quota: caching, reasoning, tools and model choice affect consumption. Keep this
assessment lightweight; do not create a second bookkeeping project.
