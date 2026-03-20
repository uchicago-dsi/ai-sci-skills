---
name: slurm
description: "Inspect queue state, submit or cancel jobs, debug sbatch and submitit runs, and separate scheduler issues from runtime failures. Use when the agent works with Slurm commands, submit scripts, submit.py launchers, or submitit logs."
---

# Slurm

## Use It As A Platform Skill

- Assume repo and workspace policy has already been loaded into context.
- Honor the active manual-mode, quota, logging, and handoff rules for the current workspace.
- Keep heavy compute off the headnode. Inspect files, edit code, and submit or monitor jobs from the headnode; run real compute on Slurm nodes only.
- Compose this skill with repo or experiment skills. Let them define intent; use this skill for scheduler choices and failure triage.

## Use This Decision Ladder

1. Discover the project’s `micromamba` env from existing repo conventions.
2. Prefer the repo-native launcher, usually `submit.py` or another checked-in `submitit` entrypoint.
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

- Assume each project has its own `micromamba` environment.
- Prefer the env named by the current workspace policy or by the project’s existing command patterns.
- If the env is not obvious, inspect nearby `AGENTS.md`, `README*`, `environment.yml`, `env*.yml`, `pyproject.toml`, or checked-in launcher scripts to see how the project already runs `python`, `pytest`, or submission commands.
- Reuse the project’s existing `micromamba run -n <env> ...` convention instead of inventing a new env choice.

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
- Avoid ad hoc inline `sbatch --wrap` commands unless the repository already treats that pattern as standard for the task.
- Capture the returned job ID. Prefer `sbatch --parsable` when the job ID must feed automation or notebook updates.
- Record the exact launcher or script, config, and output path used for the submission so the run can be reconciled later.
- Preserve the same experimental intent when resubmitting unless the user explicitly changes it.

## Treat Preemptible QoS As Overflow Capacity

- Some clusters expose a preemptible overflow tier such as `burst`, `scavenger`, `spot`, or `preempt`.
- Treat any such tier as extra, interruptible capacity rather than the default place for important long runs.
- Prefer the standard non-preemptible partition or QoS first when it is available.
- Use preemptible capacity when:
  - standard capacity is full and you need overflow,
  - the run is a short one-off, probe, smoke test, or debug job,
  - the work is eviction-tolerant and easy to requeue or replace.
- Avoid preemptible capacity for long, fragile, or high-value runs unless the user explicitly wants that tradeoff.
- Distinguish scheduler max from repo policy. A repo may intentionally cap itself below the cluster maximum.
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

## References

- Read `references/bootstrap.md` when you need to bootstrap `docs/slurm-site.md` for a new cluster or repo.
- Read `references/command-patterns.md` for command templates, common state interpretations, and `submitit` log triage.
