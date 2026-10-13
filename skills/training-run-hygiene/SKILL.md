---
name: training-run-hygiene
description: "Make a training run's health visible: persist a scale-free loss history from the first update, verify basic mechanics, and monitor learning and outcome-blind longitudinal QC on the full eligible cohort. Use when launching, resuming, monitoring, or reviewing any scientific training run."
---

# Training Run Hygiene

A completed run is not a healthy one. Every rule here exists to make "this model
is not learning" visible while the run is still cheap to stop.

## Persist A Scale-Free Training History

Every scientific training run must persist an append-only, machine-readable
training history from the first optimizer update through every resume. Record at
minimum:

- update/pass index, total loss, each unweighted loss component and its weighted
  contribution;
- learning rate, gradient norm, elapsed time;
- the exact source/unit coverage of the consumed prefix;
- training and validation curves separately when a validation objective exists.

**Every loss component must also carry, in the same row, the mean square of its
own target over its own element set, and the resulting scale-free ratio, where
`1.0` is what predicting zero scores.** A loss in physical units may never be
reported as evidence that a model fits, because a small absolute error and a small
target are indistinguishable without the denominator: a run whose loss read
`0.0048` in physical units squared, against a target mean square of `0.0061`, had
learned almost nothing and looked healthy for a month.

Render human-readable curves at a predeclared cadence throughout training, not
only at completion, and render them so a failure to learn is visible: plot the
scale-free ratio with its no-skill reference line and a smoothed trend. One point
per update with one source per point is dominated by source-to-source target scale
and hides a trend of tens of percent.

Resume must append without gaps or duplicated steps. The launcher must fail before
heavy training when the history schema, output path, or plotting cadence is absent.

If a frozen live run lacks a true loss history, add only a versioned checkpoint
sidecar and label its metrics as checkpoint QC rather than optimizer-loss curves.
Never reconstruct or imply losses that were never recorded.

## Verify Mechanics, Then Train On The Full Eligible Dataset

Follow `experiment-design`'s full-dataset default. Reuse existing mechanical
evidence. For an unverified training path, use only a brief real-input check of
forward/backward execution, finite gradients, geometry, memory, checkpoint writing
and required diagnostics. Combine checks where possible; repeat only for a named
repair or unverified path. Do not require small-subset memorization, a favorable
score, a sweep or a plateau before full-cohort training.

Monitor learning against matched no-skill and non-learned references during the
full eligible training run. Small-run losses or images establish no scientific
benefit, method ranking, generalization or lack of potential. Mechanical failures
justify repair; scientific comparisons use the full eligible cohort with preserved
splits. Numerical promotion thresholds still require explicit approval.

## Run Predeclared, Outcome-Blind Longitudinal QC

Every scientific training run must also have predeclared, outcome-blind
longitudinal QC from initialization through training, with numerical diagnostics
on the full eligible roster. A fixed selection spanning major source strata may
provide visual illustrations alongside those diagnostics. Run QC at the declared checkpoint
cadence, preserve physical aspect ratio and the full input extent, and include
task-appropriate fidelity and failure-mode diagnostics.

Any model that emits a latent or parameter field must record that field's
distribution at the same cadence: per field a median, a low and a high percentile,
and bound occupancy, computed in the parameterization's own space — log for a
log-parameterized coordinate. **Field collapse is the characteristic failure of a
latent representation and reconstruction error does not reveal it**, because a
field pinned near one value still produces a plausible output. Report a field whose
spread falls below a predeclared factor as a failure rather than leaving it to a
later probe.

The launcher must bind the QC owner, roster, cadence, and output root before
submission.

## Default Heavy QC To An Asynchronous Worker

Default heavy training QC to an asynchronous scheduled worker on a separate
accelerator, consuming immutable, atomically published checkpoints while training
continues.

- Use a real memory/timing check to establish capacity; choose another device only
  when measured requirements justify it.
- Keep cheap numerical, loss-history, and collapse monitoring inside the training
  process.
- Reuse the same scientific QC owners, roster, metrics, and declared cadence,
  including initialization. Do not build a reduced QC implementation for the
  worker.
- Persist checkpoint/config/source-bound pending requests separately from
  completed receipts, expose failures and backlog, and retry idempotently.
- **Pending or failed QC is not passed QC.** Scientific completion and
  checkpoint-based decisions require the corresponding completed and reviewed
  diagnostics. Do not silently skip required checkpoints to catch up.
- Sharing a training accelerator, or blocking all distributed ranks on heavy QC, is
  an exception that needs an explicit resource or safety reason.
- Switch a frozen live run only at a safe, provenance-preserving checkpoint
  boundary; never edit its execution checkout or rewrite historical receipts.

## Write Checkpoints So A Run Can Actually Resume

- Write checkpoints atomically. A configured checkpoint interval must retain
  immutable step-numbered snapshots in addition to `latest`; do not overwrite the
  only recoverable intermediate when checkpoint selection uses metrics beyond the
  primary loss.
- Resume paths that map model tensors to an accelerator must explicitly restore CPU
  generator and global RNG state on CPU, and must have a deterministic continuation
  regression.
- Record the split policy in run provenance. Once a run writes train/validation
  manifests, resume must reload those snapshots and fail if the current split code
  would regenerate different membership. Never overwrite a run's split in place.
