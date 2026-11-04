# ai-sci-skills

Reusable skills for AI-assisted scientific research.

Coding agents lose context across sessions, trust results they shouldn't, and
propose sweeps when a single diagnostic run would do. These skills write down
the recurring workflows and judgment calls once, so nobody has to re-teach them
every session.

Each skill is a folder holding a `SKILL.md`, the layout that Claude Code, Codex,
Cursor and Gemini CLI all read. The skills carry decision rules and workflows
that hold across projects; facts about one cluster, lab or repository stay in
that project's own notes (see [Adapting to a project](#adapting-to-a-project)).

## Installation

Ask your coding agent to do it:

```
Install the skills from https://github.com/uchicago-dsi/ai-sci-skills for
yourself, following its INSTALL.md.
```

[`INSTALL.md`](INSTALL.md) tells the agent where its skills go, links the
skills and the commands in `bin/`, finishes the setup of the few skills that
need more, and asks before changing your shell profile, scheduled jobs or agent
settings. Restart the agent session afterwards.

<details>
<summary>Installing by hand</summary>

Clone the repository, then link each skill folder into your agent's skills
directory and each command onto your `PATH`:

```bash
git clone https://github.com/uchicago-dsi/ai-sci-skills.git ~/ai-sci-skills
SKILLS_DIR=~/.claude/skills   # or ~/.codex/skills, ~/.cursor/skills, ~/.gemini/skills
mkdir -p "$SKILLS_DIR" ~/.local/bin
for d in ~/ai-sci-skills/skills/*/; do ln -sfn "${d%/}" "$SKILLS_DIR/$(basename "$d")"; done
for f in ~/ai-sci-skills/bin/*; do ln -sfn "$f" ~/.local/bin/; done
```

A project-level install uses `.claude/skills/` (or the other agents' equivalent)
inside the project. Copy with `cp -R` in place of `ln` for a fixed snapshot.
A few skills need one more step; the table in step 5 of
[`INSTALL.md`](INSTALL.md) lists them.

</details>

## Skills

Each name links to the skill's folder.

### Designing and judging experiments

- **[experiment-design](skills/experiment-design/)**: propose the smallest
  experiment that changes a decision.
- **[decision-gates](skills/decision-gates/)**: separate a scientific threshold
  that decides promotion or stopping, which needs explicit approval, from a
  mechanical check the agent can set itself.
- **[leakage-and-splits](skills/leakage-and-splits/)**: keep held-out data held
  out: split by whole source groups, count independent units, and check whether
  a split was already used for fitting.
- **[sensemaking](skills/sensemaking/)**: check whether a finding makes sense
  before trusting it.
- **[skeptical-labmate](skills/skeptical-labmate/)**: stress-test claims,
  baselines and follow-up plans.
- **[training-audit](skills/training-audit/)**: diagnose early validation
  decline and choose controlled optimization checks.
- **[training-run-hygiene](skills/training-run-hygiene/)**: keep a training run
  visible and recoverable: scale-free loss histories, validation curves, early
  stopping, and health checks on the full cohort.

### Running work on a cluster

- **[slurm](skills/slurm/)**: submit, inspect and debug Slurm jobs without
  mixing scheduler problems with runtime failures.
- **[job-babysitting](skills/job-babysitting/)**: classify job health and choose
  the next action.
- **[run-provenance](skills/run-provenance/)**: decide how much provenance a run
  owes, record it before the first expensive step, and write a README that says
  how to remake the output.
- **[quota-saving-mode](skills/quota-saving-mode/)**: cut the model requests
  spent on polling, waiting and status chatter.
- **[bounded-auto-loop](skills/bounded-auto-loop/)**: run a short autonomous
  loop with a fixed budget and stop rule.
- **[rut-breaker](skills/rut-breaker/)**: detect low-yield loops and force a
  better reset move.
- **[working-with-phi](skills/working-with-phi/)**: work on protected health
  data on a cluster without it entering the agent's session.

### Keeping records

- **[lab-notebook](skills/lab-notebook/)**: keep records restartable and
  auditable.
- **[handoff](skills/handoff/)**: create restart-ready session handoffs.

### Writing code

- **[research-code-parsimony](skills/research-code-parsimony/)**: reuse existing
  owners and cut over cleanly instead of growing code.
- **[maintenance-pass](skills/maintenance-pass/)**: trim dead code, vestiges and
  duplication without churn.
- **[shared-checkout-git](skills/shared-checkout-git/)**: stage and commit
  safely when several agents or people share one working tree.

### Coordinating agents

- **[mission-control](skills/mission-control/)**: coordinate workers, reconcile
  steering, and intervene before directions become stale.
- **[agentcomm](skills/agentcomm/)**: let agents coordinate with each other
  through a shared mailbox.
- **[claude-code-worker](skills/claude-code-worker/)**: let an agent that is not
  Claude Code, such as Codex, hand a task to Claude Code in an isolated worktree
  and continue that session later. Claude Code itself uses its own subagents for
  this.

### Writing for people

- **[humanize](skills/humanize/)**: edit prose so it sounds like the author and
  reads plainly.
- **[paper-structure](skills/paper-structure/)**: organize a manuscript for a
  specific venue: fix the claim, load the venue's section skeleton and limits,
  and budget words before drafting.
- **[quarto-presentations](skills/quarto-presentations/)**: create, render,
  check and export Quarto reveal.js slide decks.

## Usage

Most agents pick up a skill on their own when the task matches. You can also
ask for one by name:

```
Use $sensemaking before you summarize these results.
Use $experiment-design to propose the next minimal run matrix.
Use $slurm to inspect why this job is pending.
Use $mission-control to coordinate these workers and reconcile queued steering.
Use $handoff to write a restart-ready handoff.
Use $maintenance-pass to trim safe, high-yield maintenance debt.
```

## Adapting to a project

Keep the shared skills generic. Put facts about a cluster, a lab or a project's
paths in that project's own notes, which several skills read or write; the
`slurm` skill, for example, keeps a cluster's facts in `docs/slurm-site.md`.

If a project has an `AGENTS.md` or similar policy file, add a short list of the
skills that matter there and when to reach for them:

```md
## Shared Skills

- Use `$slurm` for scheduler inspection, submission, and Slurm failure triage.
- Use `$sensemaking` before trusting or reporting a result.
- Use `$experiment-design` before proposing new runs or sweeps.
- Use `$lab-notebook` for notebook updates and experiment logging.
```

Don't copy a skill's body into `AGENTS.md`. The project file says when; the
skill says how.

`hooks/` holds optional guards that refuse a tool call which would break a
rule, and say why; [`hooks/README.md`](hooks/README.md) explains how to wire
them into Claude Code or Codex.

## Contributing

New general-purpose skills, tighter wording, examples for more agents, bug
fixes and clearer guidance are all welcome. Keep skills compact and reusable,
and keep facts about one site or lab out of the shared skill body.

Some skills adapt other projects' work;
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) credits them.
