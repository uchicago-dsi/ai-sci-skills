# ai-sci-skills

Reusable skills for AI-assisted scientific research.

Coding agents lose context across sessions, trust results they shouldn't, and
propose sweeps when a single diagnostic run would do. These skills write down
the recurring workflows and judgment calls once, so nobody has to re-teach them
every session.

Each skill is a folder holding a `SKILL.md`, the layout that Cursor, Claude
Code, Codex and Gemini CLI all read. The skills carry decision rules and
workflows that hold across projects; cluster-specific, lab-specific and
repo-specific facts stay in each project's own policy files (see
[Local adaptation](#local-adaptation)).

## Installation

Clone the repository, pick the directory your agent reads skills from, and
copy or symlink the skill folders into it.

### 1. Clone the repository

```bash
# HTTPS
git clone https://github.com/uchicago-dsi/ai-sci-skills.git ~/ai-sci-skills

# or SSH
git clone git@github.com:uchicago-dsi/ai-sci-skills.git ~/ai-sci-skills
```

### 2. Choose a skills directory

A global install is available in every project; a project-level install is
scoped to one repository. If your tool supports both, global is the easier
default.

**Global directories:**

| Tool | Directory |
| --- | --- |
| Cursor | `~/.cursor/skills/` |
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Gemini CLI | `~/.gemini/skills/` |

**Project-level directories:**

| Tool | Directory |
| --- | --- |
| Cursor | `.cursor/skills/` |
| Claude Code | `.claude/skills/` |
| Codex | `.codex/skills/` |
| Gemini CLI | `.gemini/skills/` |

### 3. Copy or symlink

```bash
SKILLS_DIR=/path/to/your/skills-directory
mkdir -p "$SKILLS_DIR"
```

**Copy** (a stable snapshot):

```bash
cp -R ~/ai-sci-skills/skills/* "$SKILLS_DIR"/
```

**Symlink** (edits in the repository take effect immediately):

```bash
for d in ~/ai-sci-skills/skills/*; do
  ln -sfn "$d" "$SKILLS_DIR/$(basename "$d")"
done
```

If your client caches the list of available skills, restart the agent session
after installing.

<details>
<summary>Full examples for each tool</summary>

```bash
# Cursor
mkdir -p ~/.cursor/skills
cp -R ~/ai-sci-skills/skills/* ~/.cursor/skills/

# Claude Code
mkdir -p ~/.claude/skills
cp -R ~/ai-sci-skills/skills/* ~/.claude/skills/

# Codex
mkdir -p ~/.codex/skills
cp -R ~/ai-sci-skills/skills/* ~/.codex/skills/

# Gemini CLI
mkdir -p ~/.gemini/skills
cp -R ~/ai-sci-skills/skills/* ~/.gemini/skills/
```

</details>

## Skills

Each name links to the skill's folder.

### Designing and judging experiments

| Skill | What it does |
| --- | --- |
| [`experiment-design`](skills/experiment-design/) | Propose the smallest experiment that changes a decision |
| [`decision-gates`](skills/decision-gates/) | Separate a scientific threshold that decides promotion or stopping, which needs explicit approval, from a mechanical check the agent can set itself |
| [`leakage-and-splits`](skills/leakage-and-splits/) | Keep held-out data held out: split by whole source groups, count independent units, and check whether a split was already used for fitting |
| [`sensemaking`](skills/sensemaking/) | Check whether a finding makes sense before trusting it |
| [`skeptical-labmate`](skills/skeptical-labmate/) | Stress-test claims, baselines, and follow-up plans |
| [`training-audit`](skills/training-audit/) | Diagnose early validation decline and choose controlled optimization checks |
| [`training-run-hygiene`](skills/training-run-hygiene/) | Keep a training run visible and recoverable: scale-free loss histories, validation curves, early stopping, and health checks on the full cohort |

### Running work on a cluster

| Skill | What it does |
| --- | --- |
| [`slurm`](skills/slurm/) | Submit, inspect, and debug Slurm jobs without mixing scheduler problems with runtime failures |
| [`job-babysitting`](skills/job-babysitting/) | Classify job health and choose the next action |
| [`run-provenance`](skills/run-provenance/) | Decide how much provenance a run owes, record it before the first expensive step, and write a README that says how to remake the output |
| [`quota-saving-mode`](skills/quota-saving-mode/) | Cut the model requests spent on polling, waiting, and status chatter |
| [`bounded-auto-loop`](skills/bounded-auto-loop/) | Run a short autonomous loop with a fixed budget and stop rule |
| [`rut-breaker`](skills/rut-breaker/) | Detect low-yield loops and force a better reset move |

### Keeping records

| Skill | What it does |
| --- | --- |
| [`lab-notebook`](skills/lab-notebook/) | Keep records restartable and auditable |
| [`handoff`](skills/handoff/) | Create restart-ready session handoffs |

### Writing code

| Skill | What it does |
| --- | --- |
| [`research-code-parsimony`](skills/research-code-parsimony/) | Reuse existing owners and cut over cleanly instead of growing code |
| [`maintenance-pass`](skills/maintenance-pass/) | Trim dead code, vestiges, and duplication without churn |
| [`shared-checkout-git`](skills/shared-checkout-git/) | Stage and commit safely when several agents or people share one working tree |

### Coordinating agents

| Skill | What it does |
| --- | --- |
| [`mission-control`](skills/mission-control/) | Coordinate workers, reconcile steering, and intervene before directions become stale |
| [`claude-code-worker`](skills/claude-code-worker/) | Delegate isolated Claude Code tasks with resumable sessions and quota-aware recovery |
| [`agentcomm`](skills/agentcomm/) | Let agents coordinate with each other through a shared mailbox; see its [README](skills/agentcomm/README.md) for when it helps and when it is unnecessary |

### Writing for people

| Skill | What it does |
| --- | --- |
| [`humanize`](skills/humanize/) | Edit prose so it sounds like the author and reads plainly |
| [`paper-structure`](skills/paper-structure/) | Organize a manuscript for a specific venue: fix the claim, load the venue's section skeleton and limits, and budget words before drafting |
| [`quarto-presentations`](skills/quarto-presentations/) | Create, render, check, and export Quarto reveal.js slide decks |

### Protected data

| Skill | What it does |
| --- | --- |
| [`working-with-phi`](skills/working-with-phi/README.md) | Work on protected health data on a cluster without it entering the agent's session; adapted from the [CLIF clif-icu plugin](https://github.com/Common-Longitudinal-ICU-data-Format/skills) and [kaveriC/clif-sensitive-data-demo](https://github.com/kaveriC/clif-sensitive-data-demo) |

## Usage

Most agents discover and invoke a skill on their own when the task matches.
You can also ask for one by name:

```
Use $sensemaking before you summarize these results.
Use $experiment-design to propose the next minimal run matrix.
Use $slurm to inspect why this job is pending.
Use $mission-control to coordinate these workers and reconcile queued steering.
Use $handoff to write a restart-ready handoff.
Use $maintenance-pass to trim safe, high-yield maintenance debt.
```

## Tools in `bin/`

A few skills come with a shell command. Link the ones you need onto your
`PATH`, for example into `~/.local/bin`.

- `agent-scratch` gives one-off work an expiring home. `run-provenance` sends
  probes and throwaway scripts there so they don't sit beside durable outputs,
  where a later reader can't tell them from evidence. It creates
  `$AGENT_SCRATCH_BASE/<project>/agent_scratch/<slug>/` for whichever
  repository the agent is in. Each cluster needs two things once: its shell
  profile exports `AGENT_SCRATCH_BASE` (your scratch directory there), and a
  `scrontab` entry runs `agent-scratch sweep` nightly, which deletes entries
  untouched for 14 days:

  ```
  #SCRON --time=00:30:00 --mem=1G
  17 3 * * * $HOME/.local/bin/agent-scratch sweep --days 14
  ```

- `await-notify` and `await-event` wake an agent when a long job finishes, so
  it doesn't poll. `quota-saving-mode` uses them for harnesses without
  built-in background notification, such as Codex; Claude Code has its own
  and doesn't need them.
- `phi` runs work on protected data blind and manages the review and release
  of its output. Setup is in the
  [`working-with-phi` README](skills/working-with-phi/README.md).

`hooks/` holds guards that refuse a tool call which would break a rule, and
say why; [hooks/README.md](hooks/README.md) explains how to wire them into
Claude Code or Codex.

## Local adaptation

Keep shared skills generic. Put cluster-specific facts, site-specific Slurm
policy, project paths, and lab conventions in local project notes.

### Recommend skills in `AGENTS.md`

If a project uses `AGENTS.md` or a similar local policy file, add a short
reminder saying which skills matter in this project and when to reach for
them. Most clients already discover skills by name and description, so the
reminder's job is to connect generic skills to local expectations.

```md
## Shared Skills

- Use `$slurm` for scheduler inspection, submission, and Slurm failure triage.
- Use `$sensemaking` before trusting or reporting a result.
- Use `$experiment-design` before proposing new runs or sweeps.
- Use `$lab-notebook` for notebook updates and experiment logging.
```

Don't copy the full skill body into `AGENTS.md`. The local file says when;
the skill carries the how.

### Bootstrap `slurm`

The shared `slurm` skill stays generic, and cluster-specific facts live in
the project's `docs/slurm-site.md`. To have an agent write that file for you:

```
Use $slurm to bootstrap this cluster for the current repo. Inspect partitions,
QoS, account defaults, and the repo's launcher/env convention. Then write a
short local Slurm site note in docs/slurm-site.md with only the durable facts
that change launch decisions.
```

The full bootstrap workflow is in
[skills/slurm/references/bootstrap.md](skills/slurm/references/bootstrap.md).

## Contributing

Contributions are welcome: new general-purpose skills, tighter wording,
additional client examples, bug fixes, and clearer guidance. Keep skills
compact and reusable, and put site-specific or lab-specific facts in local
policy files, never in the shared skill body.
