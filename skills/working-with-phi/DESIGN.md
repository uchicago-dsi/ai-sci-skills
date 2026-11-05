# working-with-phi: keeping the agent away from the data

A coding agent such as Claude Code may write and run code that reads protected
data, but nothing from the data may reach the agent until a person has read it
and released it. Everything the agent reads is sent over the network to the
model provider, so a single file it reads by mistake is a disclosure.

This document says how the agent is kept away from the data, what that
protects against, and what it does not. It is written for the people who run
the machines it runs on. How to use the tool is in [README.md](README.md).

## The three places

Each project names three kinds of folder in `.claude/phi.json`. A *job* here
is any run of agent-written code against the data, on the machine the agent is
on or under Slurm.

| Folder | Holds | Agent can read | Agent can write |
| --- | --- | --- | --- |
| protected | the data | no | no |
| held | everything a job prints or saves | no | no (only the job writes there) |
| released | output a person has read and copied out of held | yes | no |

A person releases output by running `phi release` in their own terminal. The
agent is not allowed to run it; today only the hooks below enforce that.

## What separates the agent from the data today

Today the agent, its jobs and the person all run as the same Unix user, and
only Claude Code enforces the separation:

- **Hooks**, scripts Claude Code runs before each command and each message,
  refuse a command that names a protected or held folder and say what to do
  instead. They also refuse a message from the person that looks like pasted
  data rows.
- **Permission rules** refuse Claude Code's built-in file tools (Read, Grep,
  Glob), which open files from inside Claude Code itself, on those folders.
- **Claude Code's sandbox** runs each shell command in bubblewrap with those
  folders unreadable. On Linux it also needs `socat`, which Randi does not have,
  so on Randi this layer is off today.

Three gaps follow (the first two raised by Mike Jarsulic, 2026-11-04):

- The file tools run outside bubblewrap. Only the permission rules guard them,
  so a bug in how Claude Code matches paths would expose the data.
- A job runs agent-written code as the person, so it can write anywhere they
  can. A careless `df.to_csv("debug.csv")` puts data rows beside the code,
  where the agent reads them.
- With the sandbox off, a shell command is checked only by its text. Code that
  builds a data path at run time gets through.

## Proposed: run the whole agent in bubblewrap

Planned, not built.

The agent should run inside a bubblewrap sandbox in which the protected and
held folders do not exist, whichever tool asks for them. A launcher starts it
in place of `claude`:

```bash
phi agent
```

The sandbox shows only folders it is told to show: the project's code, the
person's home and environments, and system directories. Hiding the data folders
from an otherwise complete view would miss other routes to the same files, such
as GPFS snapshot folders (`.snapshots`) and second mount points.

Jobs reach the data through a runner that `phi agent` starts outside the
sandbox. The agent asks the runner, over a socket, to run a folder of code. The
runner runs it in a second bubblewrap sandbox:

| Job sandbox | Setting |
| --- | --- |
| protected folders | read-only |
| held folder | read-write, and the only place it can write |
| network | none |
| what comes back to the agent | numbers only: the exit code, the line and byte counts of what the job printed, the exception type and the line of project code that raised it (not its message), and any counts the code names |

On a Slurm cluster the runner submits the job, and the job script starts the
same sandbox on the compute node. `sbatch` is hidden inside the agent's
sandbox, so the agent cannot submit a job the ordinary way. One route remains;
see below.

With the agent's sandbox in place, Claude Code's own sandbox is no longer needed
to protect the data, and neither is `socat`, which only that sandbox uses. The
hooks stay, because they tell the agent what to do instead of only refusing.

This needs no administrator. It needs Linux with unprivileged user namespaces
and bubblewrap, both present on Randi's login and compute nodes
(`user.max_user_namespaces` is 1,030,000, the RHEL 8 default; bubblewrap
0.4.0, not setuid).

## What it protects against, and what it does not

| Threat | Today on Randi | With `phi agent` |
| --- | --- | --- |
| the agent reads a data file by mistake | refused only when the command names the folder | the folder does not exist for the agent |
| a job writes data rows where the agent can read them | possible | refused: a job can write only to held |
| a job sends data over the network | possible | refused: jobs have no network |
| an agent deliberately working around the rules | the hooks only | refused, except by submitting its own Slurm job; see below |

Because everything still runs as one Unix user, an agent deliberately working
around the rules could bring its own copy of `sbatch` and submit a job that runs
as the person, outside any sandbox. Separate Unix users close that, at the cost
of administrator setup:

| Account | Can read | Can write |
| --- | --- | --- |
| the person | everything | released (they run `phi release`, which copies out of held) |
| an agent account per person (`anna-agent`) | project code, released | project code |
| a runner account per project | the data, project code | held only |

The agent account runs the runner through one sudo rule that allows exactly
that command as the runner account, and an ACL gives the person read access to
held.

`phi` will support both setups: one Unix user under bubblewrap, or separate
accounts where a site creates them.

## Open questions

- Open: whether Randi wants the separate accounts as well, or the single-user
  bubblewrap setup alone.
- Open: whether running jobs with no network breaks anything a project needs,
  such as downloading model weights. These could be fetched before the job and
  placed where the job sandbox can read them.
- Open: whether Claude Code runs well inside bubblewrap 0.4.0 with only the
  listed folders visible. A prototype will show this.
