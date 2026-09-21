---
name: job-babysitting
description: "Directly monitor long-running jobs or pipelines, classify them as healthy, waiting, stalled, failed, completed, or unknown, and choose the next action. Use when the active agent needs to babysit training runs, batch jobs, services, experiments, or scheduled work over time."
---

# Job Babysitting

## Treat Babysitting As State Classification

- Babysitting means maintaining an evidence-backed view of whether work is progressing and intervening only when the evidence supports it.
- Compose this skill with scheduler, experiment, or domain skills. Use those skills for platform-specific commands and this skill for monitoring logic.
- Reuse the project's existing monitoring signals before inventing a new dashboard or parser.
- The active agent owns the monitoring loop end to end. Do not hand the work to a separate service, timer, watcher, or one-off agent.

## Run The Monitoring Loop Directly

1. Define the requested terminal or decision condition.
2. Define progress signals and their expected cadence before polling.
3. Inspect scheduler or process state, then verify logs and expected artifacts.
4. Classify the state and take only the proportionate next action.
5. Report the evidence, wait for the next meaningful cadence, and repeat.

- Continue until the terminal condition is met, the user stops monitoring, or a genuine blocker requires new authority or information.
- Use native scheduler, process, log, and filesystem tools from the current session. Do not install or invoke a separate monitoring subsystem.
- Keep healthy polls cheap. Read only new log output and changed artifacts instead of repeatedly rescanning complete run trees.
- Preserve interventions and decision-changing results in the run README or routed lab notebook, not in a parallel monitoring ledger.
- Do not spawn a persistent monitoring subagent unless the user explicitly requests delegated ownership.

## Use This Output Contract

When using this skill, report:

1. State: `healthy`, `waiting`, `stalled`, `failed`, `completed`, or `unknown`.
2. Evidence: the strongest signals supporting that state.
3. Last progress point: timestamp, counter, checkpoint, or artifact.
4. Blocker or failure cause: if known.
5. Next action: wait, recheck, inspect, cancel, restart, resubmit, or escalate.

## Define Progress First

- Identify what counts as real progress for the job, such as queue state changes, fresh log lines, checkpoints, metrics, output files, heartbeats, or completed subtasks.
- Identify the expected cadence from healthy prior runs, sibling jobs, or the launcher's documented behavior.
- Do not call a job stalled until you know what normal progress looks like.

## Gather Evidence In Layers

- Check orchestration state, such as scheduler, process, or service status.
- Check progress artifacts, such as log freshness, step counters, metrics, checkpoints, or output directories.
- If outputs exist, inspect one representative artifact or plot when visual corruption or qualitative failure is part of the success criterion.
- Check failure signals, such as tracebacks, repeated retries, OOMs, timeouts, dead heartbeats, or frozen timestamps.
- Check external blockers, such as dependency waits, missing inputs, storage issues, or exhausted resources.

## Apply These Rules

- Do not label a job `stalled` without at least two stale or frozen signals when a second signal is available.
- Do not relaunch a failed job before deciding whether the failure was scheduler-only or a real runtime defect.
- Do not declare success until the expected output artifacts exist.
- Do not mistake process existence, GPU allocation, or `RUNNING` state for proof of health.

## Classify The Current State

- `healthy`: evidence of forward progress exists at the expected cadence.
- `waiting`: blocked by scheduler, dependency, quota, reservation, or another external gate, without evidence of code failure.
- `stalled`: the job is nominally active but progress signals stopped beyond a reasonable threshold.
- `failed`: the job reached a terminal state or logs show a real runtime error.
- `completed`: the job ended and expected outputs exist.
- `unknown`: evidence is incomplete or contradictory.

## Act Proportionally

- For `healthy`, keep monitoring and report the strongest progress evidence.
- For `waiting`, report the blocker and the earliest meaningful recheck.
- For `stalled`, verify with at least two independent stale signals before cancelling or restarting when possible.
- For `failed`, inspect the root cause before relaunching. If the failure is real, fix or escalate instead of blindly retrying.
- For `completed`, verify the expected artifacts before declaring success.
- For `completed`, inspect a representative visual artifact as well when a job can finish while still producing qualitatively bad output.
- For `unknown`, run the fastest check that can reclassify the state.

## Report Like An Operator

- Include exact evidence paths, timestamps, counters, and job or run IDs.
- Distinguish "no recent evidence of progress" from "confirmed failure".
- Make the next action explicit: wait, recheck, inspect logs, cancel, restart, resubmit, or escalate.
- When handing off, say what you checked and what would trigger the next intervention.


## Monitor By Exclusion, Never By An Allowlist

A selector that lists the jobs, runs, or artifacts to watch stops covering work that
is later renamed, and the resulting silence is indistinguishable from health.

- Watch everything in scope and subtract only known-benign long-running owners, so
  new work is covered by default.
- Report every terminal failure state, rather than the absence of a success marker.
- Seed already-finished work silently at startup, so history is not replayed as
  events.
- Keep the failure-detection period shorter than any general review pass.
- When one account serves several projects, scope by submission directory rather
  than by job name, and subtract only directories named explicitly, so an
  unrecognised one is reported once rather than ignored forever.
- A lane submitting from the same checkout can be separated only by name. Treat that
  as the last resort it is: keep the pattern too narrow to match your own work, and
  check that a rename there would surface as noise rather than silence. Noise you
  route by hand costs less than a filter broad enough to swallow something real.

## The Wait Condition Is Where The Defect Hides

A monitor's wait condition is subject to the same known-positive requirement as its
output filter, and it is the easier of the two to get wrong: the filter is what you
think about, so the condition is where the defect hides.

A `pgrep -f` on the command being watched matches the watching shell's own
arguments, so the loop never exits and the watch expires silently no matter what the
work did. Key the condition on a pid, an exit marker, or a file the work writes, and
ask what would make the loop terminate before trusting that it will.

## Prove The Query Fires On A Real Positive

Before treating a monitor's clean result as evidence, verify it returns a known
positive. A query that cannot be shown to fire on a real failure reports the same
silence whether the system is healthy or the query is wrong. Prefer a checked owner
that fails loudly over an ad-hoc command whose silence is unfalsifiable.

A standing notification channel must be a committed script rather than an inline
command, and this holds even when the inline query is correct. An inline loop keeps
its seen-set in a temporary file, so every restart replays days of handled history
as new events; it cannot be reviewed, diffed, or fixed once, and editing it while it
runs shifts byte offsets under a live shell. Give the channel a durable ledger and
prove its query against a real in-scope positive at startup, saying so plainly when
the window holds none.

## A Completed Run Is Not A Healthy One

Monitor learning, not only liveness. Terminal-state sweeps and gates asserting that
a loss is finite and a gradient nonzero all pass for a run that trained to a
constant: nonzero is not decreasing and finite is not improving. On each pass over a
training run, read the scale-free loss against its no-skill reference and the
latent-field spread, and report a run that is not learning as a failure even though
nothing crashed. Detecting this is the agent's job, not the user's.

## References

- Read `references/health-signals.md` for monitoring cues, stall heuristics, and next-action patterns.
