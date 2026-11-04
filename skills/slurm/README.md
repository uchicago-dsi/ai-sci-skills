# slurm

Helps an agent submit, inspect and debug Slurm jobs, and tell a scheduler
problem (a job waiting for resources, a wrong partition) from a failure in the
job itself. `SKILL.md` is what the agent reads.

The skill stays the same on every cluster. What differs between clusters,
such as partitions, quality-of-service limits, default accounts and how a
project launches jobs, goes in a short note in each project,
`docs/slurm-site.md`. The agent writes that note the first time it needs it,
following [`references/bootstrap.md`](references/bootstrap.md). To ask for it
directly:

```
Use $slurm to bootstrap this cluster for the current repo. Inspect partitions,
QoS, account defaults, and the repo's launcher/env convention. Then write a
short local Slurm site note in docs/slurm-site.md with only the durable facts
that change launch decisions.
```

## Login-node guard

`hooks/block_login_node_walks.py` refuses a recursive `find`, `rg`, `du`,
`ls -R` or `os.walk` over a shared filesystem when the agent is on a login node,
where that traffic slows everyone's sessions. A walk limited to three levels
passes, and so does anything inside a Slurm job. It is off until you turn it on;
[`../../hooks/README.md`](../../hooks/README.md) says how.

Two environment variables fit it to a cluster, for example in the `env` block of
`~/.claude/settings.json`:

| Variable | Meaning | Without it |
| --- | --- | --- |
| `SLURM_GUARD_LOGIN_HOSTS` | a regular expression matching login nodes' short host names | any machine with `sbatch` counts as a login node while outside a job |
| `SLURM_GUARD_SHARED_ROOTS` | the shared filesystems, separated by `:`, such as `/gpfs:/scratch` | every path counts as shared except `/tmp`, `/var/tmp`, `/dev/shm` and `$TMPDIR` |
