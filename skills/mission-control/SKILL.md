---
name: mission-control
description: "Coordinate multiple long-running agents or workers while preserving the global goal, current evidence, and timely steering. Use when supervising tmux or managed agents, delegating parallel work, reconciling queued corrections, preventing workers from acting on stale direction, or serving as mission control across experiments, jobs, and implementation streams."
---

# Mission Control

Maintain the global objective while workers execute bounded tasks. Treat
steering as a control signal, not a FIFO inbox.

## Establish The Current Control State

Before steering, maintain a compact view of:

- global objective and current decision;
- each worker's owned task;
- last verified evidence or artifact;
- current indivisible operation, if any;
- next state-changing action;
- pending correction and whether it is still current.

Inspect the worker's actual pane, log, job, or artifact before relying on its
summary. Refresh this state after a user correction, completed experiment,
failure, commit, submission, or other decision-changing event.

## Keep The Mission State Disposable

If the campaign needs a state file, make it a current-state dashboard, not a
second lab notebook.

- Update it in place; do not append chronology.
- Keep it short, ideally under 80 lines. Delete resolved tasks, stale job states,
  superseded corrections, and metrics that no longer affect a decision.
- Include only the global objective and current decision, active baseline, worker
  ownership and state, live jobs or indivisible operations, blockers, next
  state-changing actions, and links to authoritative artifacts.
- Store commands, detailed metrics, provenance, failures, and historical reasoning
  in the lab notebook or experiment report. Link those records instead of copying
  them.
- If the dashboard starts accumulating history, rebuild it from current evidence
  rather than editing the accumulated narrative.

The lab notebook answers "what happened?" The mission-state file answers "what is
true now, and what happens next?"

## Classify Every Steering Message

Put steering in one of three classes:

1. **Interrupt now:** the message changes direction, invalidates an assumption,
   prevents unsafe or wasted work, or supersedes the worker's current task.
2. **Gate the next mutation:** the worker may finish its current indivisible
   operation, but must incorporate the correction before another commit,
   submission, browser/API call, transfer, deletion, or experiment.
3. **Queue for a natural boundary:** the message is additive, nonurgent, and
   remains useful even if the current task completes first.

A direction-changing correction is not a note in a FIFO queue. It is a gate on
the worker's next state-changing action.

Judge staleness by state, not just elapsed time. A message becomes stale when
new evidence, a changed goal, or completed work invalidates its assumptions.

## Apply A Correction Promptly

For interrupt-now or gated corrections:

1. Inspect exactly what the worker is doing.
2. Let only the smallest indivisible operation finish, such as an atomic write
   or an already-sent external request. Do not wait for the whole reasoning
   turn or workstream.
3. Interrupt the worker at that safe boundary.
4. Reconcile all pending messages with current state.
5. Replace them with one consolidated directive that explicitly supersedes
   stale instructions.
6. Require the worker to acknowledge the current objective and state its exact
   next action before continuing.
7. Verify the acknowledgment in the worker's actual output.

If the acknowledgment is missing or wrong, interrupt again. Do not assume a
queued message will eventually be interpreted correctly.

Do not automatically cancel useful compute that is already running. Decide
separately whether its result remains informative, whether cancellation saves
material resources, and whether the user authorized that action.

## Keep The Queue Fresh

- Before adding steering, inspect and reconcile the existing queue.
- Collapse repeated corrections into one current directive.
- Explicitly mark superseded messages as no longer actionable.
- Do not leave historical instructions queued after the relevant job, quota
  check, transfer, experiment, or decision has completed.
- If the interface cannot delete queued text, interrupt and issue a
  highest-priority message that says which earlier instructions are
  superseded.
- After an interrupt, inspect the input composer before sending. Some
  interfaces move queued text into the composer rather than deleting it.
- Send interface control commands such as goal resume/cancel as standalone
  transactions. Do not concatenate a control command with prose or a backlog;
  the interface may parse the combined text as a new goal.
- Do not stack new messages merely because the worker is busy. Decide whether
  to interrupt, gate, or wait.

## Preserve Mission-Control Focus

Mission control owns:

- the big-picture objective and decision sequence;
- dependencies and conflicts across workers;
- experiment priority and stopping rules;
- direct audits of important results;
- timely intervention when local work diverges.

Workers own bounded implementation and execution. Delegate concrete work when
it can progress independently, but do not delegate interpretation of the
global objective or final scientific judgment. Periodically inspect raw plots,
logs, and artifacts yourself; metrics and worker summaries are evidence, not
authority.

Avoid becoming a duplicate implementation worker when a focused worker can own
the task. Small urgent cross-cutting fixes are appropriate when they unblock
several streams or are faster to verify centrally.

## Preserve Context Economically

- Ask workers to return one compact envelope: state, decision-changing evidence,
  blocker, next action, and artifact path. Put detailed logs and provenance in
  files, not messages.
- Send deltas to a worker's current directive. Reference the canonical queue,
  mission state, or notebook instead of restating shared history.
- Poll at the expected progress cadence or near a terminal event. On unchanged
  state, say only that there is no state change; do not reproduce the queue or
  prior metrics.
- Read the smallest raw artifact slice that can change the classification. Use
  targeted searches, short tails, and bounded tool output instead of loading
  complete logs or result files.
- Implement a shared cross-cutting fix once and have other workers cherry-pick the
  exact commit rather than independently recreating it.
- After context compaction or reassignment, re-enter from the mission state and
  authoritative artifacts instead of reconstructing history from conversation.
- When frequent user-facing updates are required, make unchanged-state updates as
  short as possible while remaining truthful.

Context economy never replaces direct verification of a decision-changing result,
scheduler terminal state, safety condition, or artifact validity.

## Keep Goals And Plans At The Right Scale

- Use the enduring objective as the worker goal.
- Treat experiments, fixes, and reviews as plan items on the way to that goal.
- Resume a paused goal when the user has asked for autonomous continuation and
  no real blocker exists.
- Keep workers productive, but do not invent low-value work merely to keep
  them occupied.
- Resolve ordinary in-scope choices centrally; escalate only decisions that
  require new user authority, materially change the objective, or expand scope.

## Report Like Mission Control

For each worker, report:

1. state: healthy, waiting, stalled, failed, completed, or unknown;
2. current owned task;
3. strongest evidence and last progress point;
4. any active correction or blocker;
5. exact next action and intervention condition.

Distinguish what the worker says from what mission control independently
verified.

## Compose With Other Skills

- Use `$job-babysitting` for scheduler, service, and pipeline health.
- Use `$experiment-design` before authorizing a run matrix.
- Use `$sensemaking` or `$skeptical-labmate` before trusting a scientific
  conclusion.
- Use `$handoff` to preserve restartable global state.
- Use `$bounded-auto-loop` when supervision has a time or iteration budget.
