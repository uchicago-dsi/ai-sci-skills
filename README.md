# ai-sci-skills

Reusable skills for AI-assisted scientific research.

Coding agents lose context across sessions, trust results they shouldn't, and propose sweeps when a single diagnostic run would suffice. These skills encode recurring workflows and judgment calls so they don't have to be re-taught every session.

Each skill is intentionally compact. The shared versions encode decision rules and workflows that generalize across projects, while cluster-specific, lab-specific, and repo-specific facts stay in local policy files.

## Skills

| Skill | What it does |
| --- | --- |
| `slurm` | Submit, inspect, and debug Slurm jobs without mixing scheduler problems with runtime failures |
| `experiment-design` | Propose the smallest experiment that changes a decision |
| `sensemaking` | Check whether a finding makes sense before trusting it |
| `skeptical-labmate` | Stress-test claims, baselines, and follow-up plans |
| `lab-notebook` | Keep records restartable and auditable |
| `quarto-presentations` | Create, render, check, and export Quarto reveal.js slide decks |
| `job-babysitting` | Classify job health and choose the next action |
| `mission-control` | Coordinate workers, reconcile steering, and intervene before directions become stale |
| `rut-breaker` | Detect low-yield loops and force a better reset move |
| `handoff` | Create restart-ready session handoffs |
| `bounded-auto-loop` | Run a short autonomous loop with a fixed budget and stop rule |
| `maintenance-pass` | Trim dead code, vestiges, and duplication without churn |
| `research-code-parsimony` | Reuse existing owners and cut over cleanly instead of growing code |
| `claude-code-worker` | Delegate isolated Claude Code tasks with resumable sessions and quota-aware recovery |
| `agentcomm` | Let agents coordinate with each other through a shared mailbox |
| `quota-saving-mode` | Cut the model requests spent on polling, waiting, and status chatter |
| `humanize` | Edit prose so it sounds like the author and reads plainly |
| `slack-notifications` | Post job progress and failure reports to a private Slack channel, and answer questions there, with least-privilege credentials and a code-enforced secret filter |

### Agents talking to each other

`agentcomm` gives several agents working on one problem a shared mailbox, so
they can hand off, ask each other questions, and say when something is done
without a person relaying it.

It is most useful across harnesses. Claude Code can already message other Claude
sessions directly, so two Claude agents need no help from this. A Claude agent
and a Codex agent cannot see each other at all, and the mailbox is what lets
them coordinate: a durable name each, a roster showing who is reading, and read
state that tells a peer whether a question has actually been picked up.

`quota-saving-mode` uses it for the same reason, to deliver a wake-up when a
long job finishes rather than having an agent poll for it. That skill ships
`bin/await-notify` and `bin/await-event` for harnesses without built-in
background notification; Claude Code has its own and does not need them.

## Installation

These skills use the common `SKILL.md` folder layout supported by several local coding and research agents (Cursor, Claude Code, Codex, Gemini CLI). Install them by copying or symlinking the skill folders into your agent's skills directory.

### 1. Clone the repository

```bash
# HTTPS
git clone https://github.com/uchicago-dsi/ai-sci-skills.git ~/ai-sci-skills

# or SSH
git clone git@github.com:uchicago-dsi/ai-sci-skills.git ~/ai-sci-skills
```

### 2. Choose a skills directory

You can install globally (available everywhere) or per-project (scoped to one repo).

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

If your tool supports both, global is usually the easiest default.

### 3. Copy or symlink

```bash
SKILLS_DIR=/path/to/your/skills-directory
mkdir -p "$SKILLS_DIR"
```

**Copy** (stable snapshot):

```bash
cp -R ~/ai-sci-skills/skills/* "$SKILLS_DIR"/
```

**Symlink** (edits in the repo take effect immediately):

```bash
for d in ~/ai-sci-skills/skills/*; do
  ln -sfn "$d" "$SKILLS_DIR/$(basename "$d")"
done
```

After installing, restart the agent session if your client caches the available skills list.

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

## Usage

Most agents will discover and invoke a skill automatically when the task matches. You can also invoke one directly:

```
Use $sensemaking before you summarize these results.
Use $experiment-design to propose the next minimal run matrix.
Use $slurm to inspect why this job is pending.
Use $mission-control to coordinate these workers and reconcile queued steering.
Use $handoff to write a restart-ready handoff.
Use $maintenance-pass to trim safe, high-yield maintenance debt.
```

## Local adaptation

Keep shared skills generic. Put cluster-specific facts, site-specific Slurm policy, project paths, and lab conventions in local project notes.

### Recommend skills in `AGENTS.md`

If a project uses `AGENTS.md` or a similar local policy file, add a short skill reminder to connect generic skills to local expectations. The point isn't to make the skill visible (most clients already discover skills by name and description) — it's to say which skills matter in this project and when to reach for them.

```md
## Shared Skills

- Use `$slurm` for scheduler inspection, submission, and Slurm failure triage.
- Use `$sensemaking` before trusting or reporting a result.
- Use `$experiment-design` before proposing new runs or sweeps.
- Use `$lab-notebook` for notebook updates and experiment logging.
```

Avoid copying the full skill body into `AGENTS.md`. The local file says when; the skill carries the how.

### Bootstrap `slurm`

The shared `slurm` skill stays generic. Cluster-specific facts should live in `docs/slurm-site.md`, not in the shared skill body. To have an agent bootstrap it for you:

```
Use $slurm to bootstrap this cluster for the current repo. Inspect partitions,
QoS, account defaults, and the repo's launcher/env convention. Then write a
short local Slurm site note in docs/slurm-site.md with only the durable facts
that change launch decisions.
```

The detailed bootstrap workflow lives in [skills/slurm/references/bootstrap.md](skills/slurm/references/bootstrap.md).

## Contributing

Contributions are welcome — new general-purpose skills, tighter wording, additional client examples, bug fixes, and clearer guidance are all useful. Keep skills compact and reusable; put site-specific or lab-specific facts in local policy files instead of the shared skill body.
