# Command Patterns

## Minimal Checklist

Before acting, answer:

- What env does this repo already use?
- What is the native launcher for this repo?
- Is the issue live queue state, historical state, or runtime failure?
- Which command will answer that exact question?
- What evidence path will I cite back?

## Choose The Source Of Truth

- Use `squeue` for active and pending jobs.
- Use `sacct` for finished or historical jobs.
- Use `scontrol show job -dd <jobid>` when a field is missing, a dependency matters, or queue/accounting outputs disagree.
- Add `-X` to `sacct` when step rows add noise.

## Find The Project Environment

- Assume the repo has its own `micromamba` env.
- Reuse the env from the project’s existing commands before guessing.
- If the env is unclear, inspect nearby policy and project files in this order:
  - `AGENTS.md` or local instructions
  - `README*`
  - `environment.yml` or `env*.yml`
  - launcher scripts such as `submit.py`, `run_with_submitit.py`, `submit_*.sh`, or `Makefile`
- Prefer copying a known-good command pattern such as `micromamba run -n <env> python submit.py ...`.

For first-time cluster bootstrap, read `references/bootstrap.md`.

## Choose The Launcher

- Prefer checked-in `submit.py` or other repo-native `submitit` entrypoints when present.
- Use checked-in `sbatch` scripts when the repo does not provide a higher-level launcher.
- Keep one-off `sbatch --wrap` usage as a fallback, not the default.
- Before submitting, inspect the launcher help or dry-run mode if the repo supports it.

## Inspect QoS Limits

```bash
sacctmgr -nP show qos format=Name,Preempt,PreemptMode,GraceTime,MaxJobsPU,MaxSubmitJobsPU,MaxTRESPU,MaxWall
```

Interpret the fields this way:

- `Preempt` and `PreemptMode` tell you whether a QoS can evict or be evicted.
- `GraceTime` matters for checkpointing and requeue safety.
- `MaxJobsPU`, `MaxSubmitJobsPU`, and `MaxTRESPU` tell you per-user caps.
- `MaxWall` tells you whether a queue is suitable for long jobs.

Do not confuse scheduler max with local working policy. A repo may intentionally restrict itself below the scheduler maximum.

Choose a preemptible or overflow QoS only when it matches the workload:

- general capacity is already full and you need overflow
- the run is short, disposable, or easy to rerun
- the job is a quick debug probe, smoke test, or one-off artifact build

Prefer `general` for long, expensive, or interruption-sensitive work.

## Inspect Live Jobs

```bash
squeue -u "$USER" -o "%.18i %.9T %.24j %.10M %.6D %R"
squeue -j 123456 -o "%.18i %.9T %.24j %.10M %.6D %R"
squeue -h -j 123456 -o "%T|%R|%j"
```

Use these when the task is "what is running now?", "why is this pending?", or "where is job `123456` running?".

## Inspect Accounting And Terminal State

```bash
sacct -j 123456 --format=JobID,JobName%40,State,ExitCode,Elapsed,NodeList,Reason
sacct -X -j 123456 --format=JobID,State,ExitCode,Elapsed,MaxRSS,NodeList
```

Use these when the task is "did it fail?", "what was the exit code?", or "which node ran it?".

## Inspect Scheduler Details

```bash
scontrol show job -dd 123456
sinfo -o "%P %.10a %.20F %.10l %.8D %N"
```

Use `scontrol` for job-level detail and `sinfo` when the task is cluster capacity or partition availability.

## Submit Safely

```bash
sbatch --parsable path/to/script.sbatch
sbatch --parsable --dependency=afterok:123456 path/to/reducer.sbatch
```

- Prefer repo-native `submit.py` or `submitit` launchers when they exist.
- Otherwise use checked-in submit scripts or wrappers.
- Capture the returned job ID immediately.
- Keep the script path, config path, and output root in the same note or status update.

## Cancel Deliberately

```bash
scancel 123456
scancel 123456 123457
```

- Expect a transient `CG` state after cancelling a running job.
- Verify the terminal state with `sacct` if the job still appears in `squeue`.

## Find Logs

Common locations:

- `slurm-<jobid>.out`
- `<run_root>/submitit/`
- `<run_root>/submitit_logs/`

Useful searches:

```bash
find /path/to/run -type f \( -name "slurm-*.out" -o -path "*submitit*" \)
rg -n "Traceback|RuntimeError|AssertionError|CUDA out of memory|OOM|NCCL|Killed" /path/to/run
```

## Separate Scheduler Issues From Runtime Failures

Scheduler-only signals:

- `Priority`
- `Resources`
- `BeginTime`
- `ReqNodeNotAvail`
- `Dependency`
- `QOS*`

Runtime or code signals:

- Python tracebacks
- import errors
- shape mismatches
- NaN or non-finite failures
- CUDA OOM
- NCCL errors

Treat `TIMEOUT` as ambiguous. Inspect logs before deciding whether the fix is code, configuration, or resources.

## Triage Submitit Runs

- Read the newest matching `*_log.err` and `*_log.out` files first.
- Search the run root for `submitit` directories before assuming logs live next to the config.
- Match the job ID to the run directory before editing code or resubmitting.
- After a runtime failure, fix the root cause, run a lightweight validation, then resubmit with the same intent.
- After a scheduler-only failure, adjust queue operations instead of editing code.
