---
name: slurm
description: "Inspect queue state, submit or cancel jobs, debug sbatch and submitit runs, and separate scheduler issues from runtime failures. Use when the agent works with Slurm commands, submit scripts, submit.py launchers, or submitit logs."
---

# Slurm

## Use It As A Platform Skill

- Assume repo and workspace policy has already been loaded into context.
- Honor the active authorization, quota, logging, and handoff rules for the current workspace.
- Keep heavy compute off the headnode. Inspect files, edit code, and submit or monitor jobs from the headnode; run real compute on Slurm nodes only.
- Compose this skill with repo or experiment skills. Let them define intent; use this skill for scheduler choices and failure triage.

## Use This Decision Ladder

1. Discover the project’s environment and command convention from local policy and existing launchers.
2. Prefer the repo-native launcher, such as a checked-in workflow command, submission entrypoint, or scheduler wrapper.
3. If cluster policy matters and no trustworthy local note exists, do a light bootstrap of the site facts.
4. If QoS or partition policy matters, inspect the live scheduler limits instead of relying on memory.
5. If no higher-level launcher exists, use the checked-in `sbatch` script or wrapper.
6. Classify the issue as scheduler-only or runtime-related before changing code or resubmitting.
7. Report job IDs, states, reasons, and evidence paths precisely. 

## Bootstrap Site Facts Lightly

- Shared skills should stay generic. Do not edit the shared skill just because one cluster has special queues or limits.
- If `docs/slurm-site.md` exists, read it first.
- Do not load `references/bootstrap.md` unless one of these is true:
  - `docs/slurm-site.md` is missing
  - `docs/slurm-site.md` is missing required fields needed for the current task
  - live scheduler commands contradict `docs/slurm-site.md`
- If local Slurm facts matter and are not already documented nearby, inspect them once, record the durable findings in project-local notes or policy, and reuse that note until contradicted.
- Write the local site note to `docs/slurm-site.md`.
- Required fields for `docs/slurm-site.md` are:
  - default account
  - default partition
  - preemptible or overflow QoS, if any
  - when to use that QoS
  - important limits
  - native launcher
  - environment convention
- Refresh the local note only when:
  - commands contradict it
  - admins changed cluster policy
  - a new project uses different launch conventions

## Discover The Environment

- Prefer the environment and launcher named by the current workspace policy or existing command patterns.
- If the environment is not obvious, inspect nearby `AGENTS.md`, `README*`, environment specifications, module files, container definitions, package metadata, or checked-in launcher scripts.
- Reuse the project’s existing convention, whether it uses environment modules, a virtual environment, Conda or Mamba, a container, a workflow engine, or direct executables. Do not introduce a new environment manager merely to submit a job.

## Choose The Operation

- Inspect state when the task is status, pending reasons, node placement, dependencies, or exit codes.
- Submit or resubmit when the task is launch, restart, replace, or recover a run.
- Cancel only when the user asks, or when local policy explicitly requires retiring obsolete or broken jobs.
- Debug failures when a job reached a terminal or suspicious state such as `FAILED`, `OUT_OF_MEMORY`, `TIMEOUT`, or `CANCELLED`.

## Separate Scheduler Problems From Runtime Problems

- Treat `Priority`, `Resources`, `BeginTime`, `ReqNodeNotAvail`, `Dependency`, and `QOS*` as scheduler issues unless logs prove otherwise.
- Treat Python tracebacks, import errors, shape mismatches, NaNs, CUDA OOMs, and NCCL errors as runtime issues.
- Treat `TIMEOUT` as ambiguous until logs show whether the fix is code, config, or resources.
- Do not edit code before proving the problem is not scheduler-only.

## Inspect State Correctly

- Use `squeue` for active and pending jobs.
- Use `sacct` for completed, failed, or historical jobs.
- Use `scontrol show job -dd` when `squeue` and `sacct` disagree or when dependency, reservation, or node details matter.
- Prefer exact job IDs, exact run directories, and explicit timestamps in status updates.
- Look for repo-native monitoring utilities before rebuilding ad hoc parsing.

## Submit Or Resubmit Jobs

- Prefer repo-native submission entrypoints first, especially checked-in `submit.py` or other `submitit` launchers that encode resource defaults, output layout, validation, and run naming.
- If no repo-native launcher exists, use the checked-in `sbatch` script or wrapper the project already uses.
- Do not inherit an accelerator SKU merely because a parent or nearby run used
  it. Use measured peak memory or the smallest real representative mechanics
  run to establish the least restrictive compatible hardware, then compare
  live priority routes for that hardware and any faster compatible accelerator.
- Avoid ad hoc inline `sbatch --wrap` commands unless the repository already treats that pattern as standard for the task.
- Capture the returned job ID. Prefer `sbatch --parsable` when the job ID must feed automation or notebook updates.
- Record the exact launcher or script, config, and output path used for the submission so the run can be reconciled later.
- Preserve the same experimental intent when resubmitting unless the user explicitly changes it.

## Treat Preemptible QoS As Overflow Capacity

- Some clusters expose a preemptible overflow tier such as `burst`, `scavenger`, `spot`, or `preempt`.
- Treat any such tier as extra, interruptible capacity rather than the default place for important long runs.
- Treat accelerator type and service class as separate choices. The same GPU
  type may be available through both priority/non-preemptible and opportunistic
  routes.
- Before sending a requested accelerator to overflow, inspect live
  partition/QoS associations and node GRES. Prefer a compatible
  priority/non-preemptible route when the project is entitled to it.
- **Entitlement is a policy fact, not a scheduler fact. Never infer it from
  what the scheduler will accept.** `AllowQos=ALL`, a QoS present in your
  association, an accepted `scontrol update`, and even a returned StartTime
  estimate all mean only that the config did not stop you. Clusters routinely
  ship permissive configs over queues that are borrowed, lab-owned, or
  otherwise not yours to prioritize on, and the scheduler will happily model a
  request it should have rejected.
- Where a partition is borrowed or owned by another group, the partition
  determines the service class. Do not move a job to a higher-priority QoS on
  such a partition to escape preemption, however well it would work. Read the
  site note; if the site note does not say, ask the user. Record the answer as
  policy so the next agent does not re-derive it from `scontrol`.
- Preemption on borrowed capacity is the arrangement functioning, not a fault
  to engineer around. Make startup cheap and checkpoint early instead.
- Do not infer that direct priority capacity is unavailable merely because a
  shared persistent-allocation broker has no active holder or slots. Check the
  direct scheduler route independently; brokers and direct Slurm access are
  distinct capacity surfaces.
- Prefer the standard non-preemptible partition or QoS first when it is available.
- Use preemptible capacity when:
  - standard capacity is full and you need overflow,
  - the run is a short one-off, probe, smoke test, or debug job,
  - the work is eviction-tolerant and easy to requeue or replace.
- Avoid preemptible capacity for long, fragile, or high-value runs unless the user explicitly wants that tradeoff.
- Distinguish scheduler max from repo policy, and both from site policy. A repo may intentionally cap itself below the cluster maximum, and a site may intend limits its config does not actually enforce.
- When choosing a preemptible tier, state why the run belongs there, for example "standard queue is full" or "short debug probe".

## Debug Failures In Order

- Inspect scheduler state first so queue problems do not get mistaken for code defects.
- For runtime defects, inspect Slurm stdout/stderr and any `submitit` logs before changing code.
- Apply a targeted fix, run a lightweight validation such as `py_compile` or config sanity checks, then resubmit.
- Do not relaunch an unchanged broken config after a real runtime failure.
- Update the relevant notebook, ledger, or handoff note when local policy requires it.

## Report Clearly

- Include job IDs, state, reason, and the log path used as evidence.
- Distinguish live scheduler state from accounting state when they disagree, for example when `squeue` still shows `CG` while `sacct` already shows `CANCELLED`.
- Use absolute paths for scripts, configs, run roots, and log directories in handoff notes.
- Name uncertainty explicitly and state the fastest next discriminative check.


## Validate A Wrapper Before It Owns A Cohort

- New submit wrappers must exercise real argument parsing for one valid action and
  for missing arguments. A syntax check such as `bash -n` cannot detect malformed
  parameter expansion. Prefer explicit argument-count validation over complex usage
  text inside shell parameter expansion.
- Before expanding an array, exercise the scheduler-to-owner mapping with two
  distinct array indices, or an equivalent real parsing check. The owner must fail
  when an explicit task index conflicts with `SLURM_ARRAY_TASK_ID`; one scheduler
  task may never silently own another task's output.
- Pass run variables with `--export=ALL,VAR=value,...` or a true inline assignment
  (`VAR=value sbatch ...`). Unexported shell variables do not reach Slurm and can
  silently trigger wrapper defaults. Do not put a value containing a comma in
  Slurm's comma-delimited `--export` list; use an export file or an already-exported
  environment value, and have the wrapper log and verify the resolved full value
  before launching expensive work.
- Array stdout/stderr paths must contain `%A_%a`. A shared `%j` log can truncate or
  interleave task evidence.
- Do not inherit a runtime default — device, worker count, partition, shard count —
  from an existing wrapper without checking what it costs. An inherited value
  carries no evidence that anyone measured it, and a wrong one can multiply a job's
  cost by an order of magnitude while still looking like a working command.

## Run A Real Preflight Before `sbatch`

A real immutable preflight must pass before submission; submission success is never
a substitute for preflight validation.

That preflight must execute **every artifact the job writes** before its first
scientific kernel, the run README included, on the submitting host. A preflight that
validates inputs and stops short of writing the outputs passes a run that cannot
start: a stale provenance key in a README writer aborted an entire array having
touched no science, twice in one day, and each loss was seconds of headnode work
away from being caught.

Size monolithic cohort walltime from measured representative throughput plus
reducer and finalization headroom, and exercise the actual finalize path against
disposable prepare-stage provenance before expensive submission.

Before requesting memory near a node's advertised total, inspect live memory and run
`sbatch --test-only`. Slurm's `G` unit may not match a displayed decimal MB, so
leave schedulability margin.

## Persist Progress As You Go

Any job that runs long enough to be killed must persist progress as it goes. A run
that accumulates results in memory and writes once at the end loses everything to a
walltime limit, a node failure, or a preemption — and loses the most when it was
nearly done.

Write each unit as it completes and skip finished units on restart, so an
interrupted run is topped up rather than repeated. This holds on every lane; the
checkpoint/resume contract required for opportunistic capacity is a stricter case of
it, not the only place it applies.

## Fan Out And Reduce

- Default splittable compute, including multi-case renderers and galleries, to
  independent sharded arrays. Project wall time from the first representative real
  unit, merge explicitly, and resubmit only the failed or preempted shards.
- Array reducers should depend on shards with `afterany`, then enforce semantic
  success: require every expected manifest or summary, record skips and failures,
  fail on missing required artifacts, and expose `afterok` only downstream.
- Long shards resume only from validated case-complete artifacts, release case-local
  memory, and account for every input exactly once — as processed, as scientifically
  excluded with a typed reason, or as failed.
- For restartable work on opportunistic capacity, submit **once** using the site
  profile's comma-separated opportunistic partitions, QoS, and typed GRES, and let
  the scheduler choose. Do not hard-code one partition or duplicate submissions to
  chase capacity; split submissions only for a genuine hardware, policy, dependency,
  or resource difference.

## Treat Backlog As Normal

Useful jobs may sit pending when queue policy says to overfill. Treat
`PD(QOSMaxJobsPerUserLimit)`, `PD(Resources)`, and similar backlog as normal
queueing unless the logs or your instructions say otherwise.


## Measure Memory Before Releasing Concurrency

Before releasing concurrent volume or large-object preprocessing, measure a
representative large case's peak RSS at the intended worker count and leave node
headroom. Keep the worker count as runtime plumbing, so an idempotent shard can
resume at lower concurrency after an OOM without changing the scientific contract.

## Lock A Shared External Resource For The Whole Run

A long-running driver that owns a shared external resource — a delivery share, a
mounted staging root — must hold an exclusive lock for its whole run, and must stop
rather than wait when the resource changes underneath it.

A mutation lock inside the worker protects only that mutation: two drivers can still
each believe they own the resource, and the one whose expected arrival count another
driver already drained will wait out its timeout and then act on a later batch under
the earlier batch's provenance.

Prefer a lock whose failure mode cannot be a false conflict. A pid or command-line
scan matches any shell whose own arguments mention the driver, and will block healthy
runs.

## References

- Read `references/bootstrap.md` when you need to bootstrap `docs/slurm-site.md` for a new cluster or repo.
- Read `references/command-patterns.md` for command templates, common state interpretations, and `submitit` log triage.
