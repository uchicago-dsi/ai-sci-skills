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
