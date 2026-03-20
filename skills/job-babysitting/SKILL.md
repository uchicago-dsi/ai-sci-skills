---
name: job-babysitting
description: "Monitor long-running jobs or pipelines, classify them as healthy, waiting, stalled, failed, completed, or unknown, and choose the next action. Use when the agent needs to babysit training runs, batch jobs, services, experiments, or scheduled work over time."
---

# Job Babysitting

## Treat Babysitting As State Classification

- Babysitting means maintaining an evidence-backed view of whether work is progressing and intervening only when the evidence supports it.
- Compose this skill with scheduler, experiment, or domain skills. Use those skills for platform-specific commands and this skill for monitoring logic.
- Reuse the project's existing monitoring signals before inventing a new dashboard or parser.

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

## References

- Read `references/health-signals.md` for monitoring cues, stall heuristics, and next-action patterns.
