---
name: maintenance-pass
description: "Run safe, high-yield codebase maintenance passes that trim dead code, vestiges, duplicate implementations, stale scripts/configs, and excessive LOC without churn. Use when the agent is asked for a maintenance pass, cleanup pass, code cleanup, slop trimming, dead-code removal, de-duplication, vestige pruning, or refactors whose purpose is reducing maintenance burden rather than adding features."
---

# Maintenance Pass

## Optimize For Maintenance Yield

Prioritize the safest change with the largest maintenance payoff. Delete or simplify code only when evidence supports it. Refactor only when it materially reduces duplication, clarifies ownership, removes a failed path, or protects an important contract. Do not move code around for aesthetics.

Use this rough ranking:

```text
maintenance yield = impact * confidence * stale_touch_signal / blast_radius
```

Treat time since last git touch as a triage signal, not proof. The relevant metric is the most recent commit that changed a path, not when the file was created. Code whose latest git touch was a long time ago is more likely to be a vestige, duplicated old path, or stale interface, but stable core infrastructure can also be old and correct.

## Start With Evidence

1. Read local repo instructions first: `AGENTS.md`, `CLAUDE.md`, `README.md`, nearby runbooks, and provenance notes tied to the target area.
2. Check the worktree: `git status --short --untracked-files=all`. Never revert unrelated user changes. Avoid destructive cleanup in a dirty worktree unless the user explicitly scopes it.
3. Establish stable baselines:

```bash
git ls-files '*.py' | wc -l
git ls-files '*.py' | xargs wc -l | tail -n 1
```

4. Build a least-recently-touched candidate list from tracked files before choosing a theme. Prefer files and directories whose most recent git commit touch is old, especially when they are scripts, one-off analyses, retired mechanism code, stale configs, duplicate helpers, or docs for old paths. Use `git log -1 --format='%ct %cs %h' -- <path>` or the inventory helper's least-recently-touched section. Do not use last-touch age alone to delete stable package owners, tests, schemas, or public APIs.
5. If the user gives a target LOC change, treat it as a stopping target, not a quota. Aim for the target with the safest high-yield changes first, but stop short when the next candidate has weak evidence or excessive blast radius. Do not pad the diff with formatting, moves, or speculative rewrites to hit the number.
6. Create a pre-pass commit boundary before editing. If the worktree is clean, make a checkpoint commit, using an empty commit only when the user explicitly requested before/after commits. If the worktree is dirty, do not silently commit unrelated or user-owned changes; either commit only the already-approved scoped changes, make an empty checkpoint commit, or ask before including preexisting work. Record any skipped checkpoint and why.
7. Optionally run the bundled inventory helper from the repo root:

```bash
python <skill-dir>/scripts/maintenance_inventory.py --top 40
```

8. Use `git ls-files`, not broad `find`, to separate tracked maintenance targets from ignored local noise.
9. Use `rg`, `git log`, configs, scripts, docs, notebooks, tests, run READMEs, and CI/workflow files to distinguish live paths from vestiges.

## Prefer High-Yield Categories

Start with:

- Least-recently-touched candidates: tracked files or directories whose most recent git commit touch was many months/years ago, especially scripts, launchers, configs, docs, and one-off analyses with no current references.
- Dead entrypoints: unreferenced scripts, CLIs, launchers, notebooks, or wrappers for retired mechanisms.
- Duplicate owners: repeated loaders, writers, path builders, manifest parsing, plotting, checkpointing, metrics, config parsing, or shell wrapper patterns where a shared owner already exists.
- Failed-path residue: compatibility shims, silent fallbacks, duplicate control paths, old config branches, or experiment families explicitly marked retired.
- Large isolated files: high-LOC files with separable helpers that can be deleted, moved to an existing owner, or split only when that reduces real coupling.
- Tracked local artifacts: generated files, caches, copied outputs, debug dumps, or temporary files that do not belong in source.
- Documentation/config drift: active docs or examples pointing to removed paths, obsolete commands, or retired defaults.

Deprioritize:

- Pure renames, directory reshuffles, formatting-only churn, and speculative abstractions.
- Historical configs, provenance docs, experiment outputs, source data, QC artifacts, and published result records unless the user explicitly asks and local policy allows it.
- Monolith surgery where the behavior is active and the only benefit is making a large file smaller.
- Refactors that broaden the blast radius to save a small number of lines.

## Require Deletion Evidence

Before deleting or retiring code, gather enough evidence to explain why it is safe:

- Search by filename, function/class names, config keys, CLI names, run labels, and output paths.
- Check package code, scripts, configs, docs, notebooks, tests, CI/workflows, scheduler wrappers, and run/provenance notes.
- Inspect `git log -- <path>` and nearby comments for ownership/history.
- Confirm there is a surviving owner or replacement path when removing a duplicate.
- Confirm the target is not source data, experiment provenance, a completed-run record, or an artifact family protected by local instructions.

If evidence is mixed, mark the candidate as "retire later" or remove active references first. Do not delete code merely to reduce LOC.

## Research-Code Guardrails

Apply these defaults unless local instructions are stricter:

- Treat source data as read-only. Never delete source imaging, raw measurements, original labels, or other canonical raw data.
- Do not delete experiment outputs, QC artifacts, run directories, notes, intermediates, or completed-run configs just because a branch did not win.
- Do not retroactively edit configs or provenance for completed runs.
- Do not treat `.gitignore` as deletion permission.
- Do not delete annotation queues, review queues, or browser state without checking saved edits, metadata, QC flags, backups, and sidecars.
- Do not delete cache directories as generic cleanup; only remove caches with evidence that they are stale, retired, cheap to regenerate, and unlikely to be reused.
- Treat unused-code tools such as `vulture` as triage only; CLIs, dynamic config fields, plugin hooks, scheduler env vars, and notebook-used scripts often produce false positives.

## Editing Rules

- Work in small batches with one maintenance theme at a time.
- Preserve behavior unless the user explicitly asks for behavior changes.
- Prefer deleting an entire dead path over partially pruning internals.
- Prefer extending an existing shared owner over adding a new abstraction.
- Replace duplicate call sites when safe; leaving old and new paths side by side usually increases maintenance burden.
- When a refactor increases LOC, justify the increase in terms of reduced duplication, clearer ownership, or stronger contract enforcement.
- Update active docs/config references that would otherwise point to removed code.

## Parallel Agent Pattern

Use subagents only when the user explicitly allows delegation or parallel agent work.

Good parallel uses:

- Explorer agents scan disjoint areas read-only, such as package code, scripts, configs, docs/provenance, or CI.
- Worker agents implement bounded patches with disjoint write scopes after the main agent defines ownership.
- One worker edits package code while another edits tests/docs, if their write sets do not overlap.

Avoid:

- Parallel deletion without main-agent review.
- Multiple workers editing the same files or shared owners.
- Delegating the immediate blocking decision about whether deletion is safe.

The main agent owns integration, final review, validation, and the user-facing summary.

## Validate Proportionally

Use checks that match the risk:

- Narrow Python edits: targeted `python -m py_compile <files>` or `python -m compileall <package-or-dir>`.
- Shared behavior or broad refactors: relevant unit tests or smoke checks, plus compile checks.
- Shell wrapper edits: `bash -n <touched.sh>` and any repo wrapper-sourcing checks.
- Config edits: parse the config format and run the repo's loader/validator when present.
- Style-only or lint-sensitive edits: run the repo's formatter/linter only on touched paths when possible.

Avoid adding heavyweight, GPU-dependent, network-dependent, or cluster-scale checks for routine cleanup unless the user asks.

Always recompute the same LOC/file-count baseline after the pass and report the delta.

## Commit The Pass

After validation, commit the completed pass before reporting final status.

- Stage only files changed for this maintenance pass. Do not sweep unrelated dirty worktree changes into the commit.
- Use a concise maintenance commit message naming the theme, such as `chore: remove retired training entrypoints` or `refactor: centralize artifact writers`.
- If validation fails and cannot be fixed quickly, do not commit a broken pass unless the user explicitly asks for a checkpoint; report the failure and leave the diff unstaged or clearly scoped.
- Keep the pre-pass checkpoint and post-pass change commit separate so future agents can diff exactly what the pass did.

## Report

Lead with the maintenance result:

- Files deleted, merged, or refactored.
- Commit hashes for the pre-pass checkpoint and post-pass change commit, or the reason either boundary was skipped.
- Net LOC/file-count change using the same baseline commands.
- Evidence used to classify vestiges or duplicates.
- Validation run and any failures or skipped checks.
- Residual risk and the next 1-3 highest-yield maintenance candidates.
