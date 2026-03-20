---
name: handoff
description: "Create a restart-ready handoff so a fresh agent or future turn can resume work without rereading the full conversation. Use when pausing work, ending a session, switching agents, or preparing a clean-context restart."
---

# Handoff

## Optimize For Cold Restarts

- A handoff is for a fresh agent with no working memory.
- The goal is fast re-entry, not a narrative recap.
- Update the canonical notebook or log first if the project already has one. Then write the handoff.
- Compose this skill with domain skills such as `$lab-notebook`, `$job-babysitting`, or `$slurm`.

## Use This Contract

Every handoff should answer:

1. Goal:
   - what problem or decision is in flight.
2. Current state:
   - what is true now.
3. Evidence:
   - exact paths, job IDs, branches, commits, configs, logs, or artifacts that support the current read.
4. Open uncertainty:
   - what is still unclear, blocked, or waiting.
5. Next action:
   - the exact next check, command, or edit that should happen first.

## Make The Handoff Restartable

- Include exact file paths and identifiers, not vague references such as "the latest run" or "that config".
- Separate facts from hypotheses.
- Name what has already been ruled out so the next agent does not repeat dead work.
- If code changed, include branch, commit SHA if any, validation status, and whether the worktree is dirty.
- If jobs are involved, include job IDs, current state, run root, and the next decision point.
- If waiting on an external event, say what event should trigger the next step.
- End with one concrete re-entry action.

## Keep It Short

- Default target: 5-12 lines or a very short bullet list.
- Prefer one crisp sentence per field over a long paragraph.
- If the handoff is getting long, move durable detail into the project notebook and keep the handoff as an index into that evidence.

## Avoid Weak Handoffs

- Do not retell the whole chronology.
- Do not say "continue from here" without naming the first command or check.
- Do not omit the current best explanation.
- Do not omit validation status after code changes.
- Do not hide uncertainty behind generic phrases such as "needs more debugging".

## Restart Test

- A good handoff lets a fresh agent resume within a couple of minutes using only:
  - the handoff,
  - the repository,
  - the referenced notebooks, logs, and artifacts.
- If that would still require rereading the full chat, the handoff is incomplete.

## References

- Read `references/templates.md` for compact templates for code work, experiments, and job-monitoring handoffs.
