# Health Signals

## Minimal Checklist

When babysitting a job, try to answer:

- What counts as progress for this job?
- What was the last confirmed progress point?
- What two signals best support the current state?
- What would make me intervene?
- When should I recheck if I do nothing now?

## Strong Progress Signals

- Log timestamps keep advancing.
- Step, epoch, batch, or task counters increase.
- New checkpoints or output shards appear.
- Metrics update on the expected cadence.
- A scheduler or process state transition matches the expected lifecycle.

Prefer confirmation from a second source when the cost is low.

## Weak Or Ambiguous Signals

- The process still exists but nothing else changed.
- GPU or CPU allocation exists without fresh outputs.
- The job is still `RUNNING` but log files are stale.
- The output directory exists but no new artifacts appear.

Treat these as prompts to inspect further, not proof of health.

## Common Waiting Cases

- Scheduler says `PENDING`, queued, blocked by resources, dependency, or reservation.
- The launcher is waiting for upstream inputs or a downstream reduction phase.
- The run is between long phases with sparse expected logging.

Report the blocker and the recheck condition instead of forcing action early.

## Common Stall Patterns

- No fresh logs, checkpoints, or counters for longer than the normal cadence.
- Repeated identical log lines without state change.
- A nominally active job with no I/O growth and no metric movement.
- Heartbeat files or sidecar status artifacts stopped updating.

Prefer two stale signals before declaring a stall.

## Common Failure Patterns

- Traceback or explicit runtime error in logs.
- OOM, timeout, import failure, assertion failure, or repeated crash loop.
- Terminal scheduler state with non-success exit code.
- Missing required outputs after the launcher claims completion.

Separate scheduler-only failures from real runtime defects before changing code or resubmitting.

## Good Next Actions

- Recheck later when the job is healthy or waiting and the blocker is known.
- Inspect logs when progress is ambiguous.
- Compare against a healthy sibling run when you need a cadence baseline.
- Cancel or restart only after evidence supports stall or obsolescence.
- Resubmit only after deciding whether the prior failure was scheduler-only or a real runtime defect.
