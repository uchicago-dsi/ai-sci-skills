---
name: lab-notebook
description: "Record work in a lab notebook so it is both a literal activity log and an efficient re-entry aid. Use when the agent is running experiments, debugging workflows, triaging jobs, or updating project state that must be recoverable later."
---

# Lab Notebook

## Optimize For Re-entry And Auditability

- A notebook should answer both:
  - what exactly happened?
  - what do we currently believe?
- Prefer one low-friction chronological record plus a sparse current-summary layer.
- Reuse the project's existing notebook pattern instead of inventing a new structure.

## Choose The Notebook Shape

- If the project already uses one file with summary plus chronology, keep that shape.
- If the project already uses a detailed campaign notebook plus a sparse top-level lab notebook, keep that split.
- Do not create two equally detailed notebooks.
- Default rule:
  - detailed layer: append literal work record
  - summary layer: update only when the decision or current understanding changes

## Use This Entry Contract

For each meaningful experiment, debugging step, or job intervention, capture:

1. Question or goal.
2. Action taken.
3. Evidence:
   - commands, scripts, configs, paths, job IDs, artifacts, metrics.
4. Result:
   - what actually happened.
5. Conclusion:
   - the inference you are drawing, if any.
6. Inference confidence:
   - `low`, `medium`, or `high` when the entry is making a real inference.
7. Decision impact:
   - what changed in current understanding, or what the next step is.

## Update The Summary Sparingly

- Update the summary layer only when one of these changes:
  - current best explanation
  - current best branch or baseline
  - settled negative results
  - next discriminative check
  - success criterion or decision rule
- Do not rewrite the summary after every routine action.
- The summary should be short enough that a fresh agent can re-enter from it.
- If multiple live explanations matter, keep a tiny hypothesis registry in the summary layer:
  - hypothesis
  - strongest support
  - strongest weakening evidence
  - next falsifier

## Make Entries Useful

- Include exact evidence paths and identifiers.
- Include representative visual artifact paths when a plot, overlay, slice, curve, or diff view materially affected the decision.
- Record negative results explicitly when they rule out a family of ideas.
- If the entry draws an inference, state it explicitly instead of leaving it implicit in the next step.
- Keep inference confidence coarse: `low`, `medium`, or `high`.
- Do not add confidence to entries that are only reporting raw observations or routine actions.
- Preserve chronology so later readers can reconstruct what happened.
- End each entry with "so what?" in concrete form.
- If nothing changed in understanding, say that explicitly.

## Avoid Notebook Drift

- Do not let the summary become stale relative to the chronology.
- Do not dump raw metrics or images without interpretation.
- Do not record an interpretation without enough evidence to re-check it later.
- Do not duplicate the full chronological detail into the summary.


## Search The Notebook Before Proposing

Before suggesting a new experiment or debugging direction, search the routed
notebook and nearby run READMEs for close prior attempts.

## Record Decisions, Not Every Healthy Poll

Do not record routine static or local checks — linting, compile checks, syntax
checks, whitespace checks, wrapper-sourcing checks. Record substantive data smoke
tests, manifest audits, geometry checks, fit and QC audits, and failure evidence.

The notebook is for decisions and the evidence behind them. A cheap probe that
changed no decision and that one command reproduces does not need an entry; a cheap
probe that changed a decision, or that failed informatively, does.

Log submit, cancel, resubmit, and result events immediately, with the run path, job
ID, config path, hypothesis, takeaway, and next step.

## Write To The Lane That Owns The Work

Lanes are durable workstreams. A transient session or subagent appends to the lane
whose work it is doing, rather than opening its own notebook, and a genuinely new
durable lane registers in the lane index before it gets a notebook.

Each lane notebook has one current staging and commit owner under the
`shared-checkout-git` rule. Work spanning lanes records the entry in the lane that
owns the decision, and links the authoritative run root and provenance rather than
duplicating the entry in each lane.

## Translate Run Names Into Plain English

When reporting results, say the dataset and scope, the model family, the input
representation, the resolution, and the main knob. State the shared setup and the
differing knob before any comparison.

Use labels that identify the mechanism, representation, and version. Do not use
`old`, `new`, or `previous` as experiment labels — chronology does not describe what
was tested.

## References

- Read `references/templates.md` for one-file and two-layer notebook templates.
