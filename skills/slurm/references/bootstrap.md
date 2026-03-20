# Slurm Bootstrap

Use this reference only when one of these is true:

- `docs/slurm-site.md` does not exist
- `docs/slurm-site.md` is missing required fields for the current task
- live scheduler commands contradict `docs/slurm-site.md`

## Goal

Write a short local note at `docs/slurm-site.md` containing only the durable Slurm facts that change launch decisions for this repo.

## Required Fields

`docs/slurm-site.md` should contain:

- default account
- default partition
- preemptible or overflow QoS, if any
- when to use that QoS
- important limits
- native launcher
- environment convention

## Ready-To-Paste Prompt

```text
Use $slurm to bootstrap this cluster for the current repo. Inspect partitions, QoS, account defaults, and the repo's launcher/env convention. Then write a short local Slurm site note in docs/slurm-site.md with only the durable facts that change launch decisions.
```

## Inspect The Cluster

```bash
sinfo -o "%P %.10a %.20F %.10l %.8D %N"
sacctmgr -nP show qos format=Name,Preempt,PreemptMode,GraceTime,MaxJobsPU,MaxSubmitJobsPU,MaxTRESPU,MaxWall
sacctmgr -nP show assoc where user=$USER format=Account,Partition,QOS,DefaultQOS
```

## Inspect The Repo

Check the existing repo conventions:

- `AGENTS.md`
- `README*`
- `environment.yml` or `env*.yml`
- `pyproject.toml`
- launchers such as `submit.py`, `run_with_submitit.py`, `submit_*.sh`, or `Makefile`

## Record Only Durable Facts

Good candidates:

- default account and partition
- preemptible or overflow QoS names
- when preemptible QoS should be used
- walltime, job-count, or GPU limits that affect launch choices
- the repo's native launcher
- the repo's environment convention

Do not dump raw scheduler output into the note.

## Note Template

Write `docs/slurm-site.md` like this:

```md
## Slurm Site Note

- Default account:
- Default partition:
- Preemptible or overflow QoS:
- When to use that QoS:
- Important limits:
- Native launcher:
- Environment convention:
```

Keep it short. It should be an operational summary, not a transcript.

## Refresh The Note

Refresh `docs/slurm-site.md` when:

- live scheduler output contradicts the note
- admins change cluster policy
- the repo changes launcher or environment conventions
