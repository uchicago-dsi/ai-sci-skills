---
name: training-run-hygiene
description: "Make scientific training visible and recoverable through scale-free loss histories, validation/task curves, early stopping, shared Trackio metrics/QC and full-cohort health checks. Use when launching, resuming, monitoring or reviewing a scientific training run, or onboarding its saved outputs into Trackio."
---

# Training Run Hygiene

A completed run is not a healthy one. Every rule here exists to make "this model
is not learning" visible while the run is still cheap to stop.

## Publish Training And QC To The Shared Trackio Dashboard

Use Trackio for new scientific training experiments and onboard currently running
experiments from their saved outputs. Keep each experiment's canonical output
directory authoritative: metrics, histories, checkpoints and QC stay there.
Tracking is a derived index; a server outage must not lose local results or force
an otherwise recoverable training job to fail.

Use one shared server rather than a server per manager. On CRI, read the maintained
setup and onboarding instructions in
`/gpfs/data/karczmar-lab/hfdp/scripts/tracking/README.md`; reuse its server,
environment, exporter and backup owner. Those host-specific details are not
defaults for other clusters. Do not restart shared infrastructure to onboard a lane.

- Name the project `<lane>-<manager>`, with stable lowercase names, such as
  `vanguard-hal`. Each logical experiment is a run across scheduler allocations;
  related experiments share a `group`. Record `manager`, `lane`, `experiment_dir`
  and a nonempty plain-language `config.description` for every new run. The sidebar
  hover tooltip reads it. Explain the scientific question and main knob, the run's
  current role (active focus, reference, completed or superseded), and what metrics
  or pending QC deserve attention. Update it when that role changes. Require this
  metadata before registration rather than relying on memory: the shared saved-output
  exporter rejects missing/blank/non-string descriptions and supports `--validate-only`
  before reading artifacts or contacting the server. Direct SDK callers must provide
  it in `trackio.init(config=...)`; the exporter does not intercept SDK calls. Verify
  the saved server description after publishing.
- Publish training/validation losses, applicable task metrics, the canonical
  learning curve and applicable saved qualitative QC. Namespace metric keys by
  quantity and role. Use clear `train` and `eval` labels, not a metric role named
  `selection`. Explain in descriptions/tables when eval is used for checkpoint
  selection and therefore is not an untouched test; preserve the underlying split.
  Record trained versus evaluated checkpoint, pending/failed readouts, denominator
  and selected versus latest checkpoint. Label missing scores pending, failed or
  unavailable as appropriate; never substitute zero.
- Keep evaluation names common across procedures: metric keys identify the
  quantity, dataset/endpoint and split, while the run name/config identifies the
  encoder, pooling, readout and other method choices. Two pooling/readout arms
  sharing a trained checkpoint are separate logical runs on the same task plots,
  not separate metrics such as `dataset_mean/val` and `dataset_panther/val`.
  Only combine scores whose cohort, endpoint and measurement definitions match;
  retain denominators and any genuine protocol differences in run descriptions.
  When replacing an indexed layout, backfill the common metrics and remove its
  superseded dashboard entries, preserving canonical experiment artifacts.
- Preserve evaluation names across runs. Change a name only when the measured
  quantity, evaluation population/split, preprocessing, inference or aggregation
  actually differs; explain that difference. Do not create method-specific names
  for the same evaluation. Overlay comparable runs on the same metric plot.
  Breast BCE, tissue soft-Dice loss, and vessel-only native Dice are different
  quantities. Epoch means and individual-update losses are different aggregations:
  compare like with like, label the x-axis/unit explicitly, and never connect stage
  resets or resumed prefixes as one trajectory. Do not merge genuinely different
  fixed-crop and sampled-crop eval losses just to make their labels match.
- Use information tables for epochs completed, optimizer updates, presentations
  or augmented examples seen, batch size, participant counts and pending readouts.
  Do not turn these counters into bar charts or redundant epoch-versus-step plots.
  Keep distinct trained stages explicit in tables and metric quantities or run names.
  Retain the full numerical histories; use complete-epoch means for epoch overlays,
  with update-level detail available separately. The shared exporter can suppress
  coordinate metrics with `step_metric: null` and publish native `information_tables`
  in Media; the plot's step already supplies its x coordinate. Verify the table
  through the actual consumer; do not assume a Markdown renderer supports tables.
- Default saved QC PNGs to links through the shared exporter. Save images once in
  their experiment directory and register path/key/step/caption. Use immutable
  epoch filenames for galleries; an image overwritten in place needs an explicit
  mutable snapshot to preserve history. Original files must remain server-readable
  and retained. Link backups do not back up the original pixels; symlinks still
  consume inodes. Arrays/PIL images must first be saved as canonical files.
  Assign the lane's manifest/registration owner to add new gallery entries
  automatically at the QC cadence and retain historical entries while dashboard
  records reference them. The exporter refreshes registered entries, not new files
  it has not been told about.
- The shared exporter links file-backed PNGs; native `trackio.Image(path)` copies.
  Do not claim the native SDK or other media types automatically use links.
  Prefer the existing exporter for images and thin producer adapters over a
  per-trainer logger, copied renderer or Trackio fork.
- For live or pinned runs, use a separate incremental exporter of saved reduced
  tables and existing PNGs. The shared importer reads CSV, newline-complete JSONL
  scalar records and single-object JSON summaries, exporting only explicitly mapped
  metrics. Skip absent pending summaries only when declared optional; malformed
  records remain errors. Declare the actual step metric/unit (for example optimizer
  updates rather than epochs), and use the existing reduction owner for other formats. Preserve execution pins, environments, splits and
  stopping rules. Backfill genuine saved history, retain original checkpoint/step
  identities, and tolerate late asynchronous results without duplicate delivery.
  Do not fabricate missing training losses or rewrite historical artifacts.
- The server/exporter use their dedicated environment. A training script importing
  `trackio` needs the pinned SDK in that project's environment; the dependency
  follows the importing process, not the manager. Saved-output export needs no
  SDK installation or live-code change in the training environment.
- Use the existing read-access policy and protected write credentials; keep tokens
  out of code, notes and agent mail. Do not enable cloud uploads or public sharing
  as a side effect. Server-local URLs only work on the server host unless a
  deliberate route/tunnel exists. Apply project privacy policy to exported pixels,
  embedded labels, config, notes and metric names as well as image captions.

Before reporting a lane onboarded, verify real saved values and representative
images in its project, a repeated unchanged export without duplicate records,
refresh after new output, and automatic exporter startup. Report missing QC or
network access explicitly. Tracking makes existing QC visible; it does not replace
the validation, plotting, early-stopping and provenance requirements below.

## Save Training And Validation Together

Every experiment involving learning must run validation and automatically save a
training-and-validation curve in its canonical output directory. Use `run-provenance`'s
one-directory contract: asynchronous readouts and QC belong under the same
experiment root as its checkpoints and logs.

Before launching a new learning experiment, require `run-provenance`'s automatic
reproduction bundle in that root: a runnable README, the complete effective config,
Git revision/status/diffs, and environment and input identities. Preserve these
records across resumes; this does not require retrofitting historical experiments.

Declare the validation owner, fixed readout recipe, first evaluation and refresh
cadence in the run config before launch. Plot training and validation as distinct
labeled series in one figure, using separate panels when they measure different
quantities. For self-supervised pretraining, show the training objective alongside
regular downstream validation, at least a fixed linear evaluation; a falling SSL
loss alone does not satisfy this requirement. Keep the probe settings fixed
across checkpoints.

Write the curve automatically from the first recorded update, refresh it after
training-history and completed validation updates at the configured cadence, and
retain it when the experiment stops or resumes. Show optimizer updates and actual
training examples seen or eligible-set coverage. If validation has not completed,
label it pending and show the latest completed validation checkpoint; never imply
that a training-only curve or stale readout is current validation. Before calling
monitoring ready, inspect the saved figure after an actual update, including the
single-point case. Singleton traces need a visible mark, and aggregation blocks
must reveal early learning at the experiment's update cadence. Verify that both
sources are bound to the intended experiment. Include the output-directory link in every update.

### Keep One Canonical Curve

Use one canonical `learning_curve.png` per experiment, at its output root,
containing both training and validation panels. Training and asynchronous
validation feed one rendering owner, which refreshes this same file atomically.
Before validation completes, the figure shows training with validation explicitly
pending; completion fills in that figure rather than creating a second version.

Do not keep parallel training-only and training-plus-validation learning curves,
separate evaluator curve directories, or copies named for readability revisions
or checkpoint snapshots. Preserve numerical histories and checkpoint metrics so
the canonical figure can be regenerated without saving redundant plot variants.
Additional QC figures must answer a distinct question, rather than repeat panels
already in the canonical curve. Link the canonical curve from the root README
and experiment updates. Apply this convention to new work; do not rewrite frozen
historical run artifacts or a live execution checkout to retrofit it.

## Implement Early Stopping In Every New Training Pipeline

Every new model-training pipeline must implement validation-based early stopping,
enabled by default for new runs. Record the monitored metric, optimization direction,
minimum improvement, patience, any warm-up, evaluation cadence and maximum training
budget in the effective config before launch. Express patience in completed eligible
validation evaluations. Follow `decision-gates` when adopting the numerical scientific
stopping rule; this implementation requirement does not choose its thresholds.

Persist the best metric, best checkpoint, patience counter and last consumed
evaluation identity with recovery state so resuming does not reset patience or count
an evaluation twice. Consume asynchronous results in checkpoint order; missing,
pending or failed validation must not count as non-improvement. Coordinate a graceful
stop across distributed ranks at a safe checkpoint boundary. Preserve the selected
best checkpoint, record the stopping reason and triggering checkpoint, and drain
required validation/QC after stopping.

An explicitly prescribed fixed-duration protocol, such as an exact reproduction,
may disable early stopping with its reason recorded in the config. Keep the
implementation available, and preserve already frozen live-run stopping policies.

## Run Validation In A Separate Process And Drain Its Backlog

Validation runs in a separate process from training, consuming immutable,
atomically published checkpoints. The training loop publishes durable requests
and continues; it does not run downstream fitting or evaluation inline. Separate
processes may share an allocation when resources permit, but must not duplicate
the scientific validation implementation or change its fixed settings.

Every validation worker is a backlog drainer, not a one-checkpoint job:

- On startup, discover all pending validation work for its experiment, including
  requests left by interrupted workers. Process ready requests in checkpoint
  order, rescan as work completes, and continue until no ready work remains or
  the allocation's safe runtime limit is reached. Do not process only the request
  that triggered the worker or silently discard intermediate checkpoints.
- Use atomic claims/locks and checkpoint/config-bound completion receipts so
  concurrent workers cannot duplicate work. A surplus queued worker exits cleanly
  when no unclaimed work remains. Recover abandoned claims only after confirming
  the owning worker is no longer active.
- Checkpoint the validation workflow after each completed stage. Interrupted work
  resumes from durable progress; failures remain visible and retryable rather
  than being recorded as completed. Report blocked requests without preventing
  independent ready work from progressing.
- Keep pending requests, progress, failures, metrics, receipts and automatically
  refreshed curves under the owning experiment's output directory. Preserve
  checkpoints until their required validation has completed.
- A timer or equivalent automatic dispatcher restarts draining when new work
  arrives or runtime expires; it also drains the final backlog after training
  stops. Expose the newest completed checkpoint and outstanding backlog so stale
  validation is visible. A pending or failed request is never a validation result.

Before training starts, require the validation recipe, cadence, worker/dispatcher
binding, output paths and curve settings in the effective config. Fail before
expensive execution when these are absent. Validation and curves are mandatory
for new experiments, including ablations; changing the method must not bypass
this common path.

## Reuse One Base QC Implementation

Apply `research-code-parsimony` before adding any QC: find the existing numerical
producer, plotting owner and actual callers. All experiments use the same shared
implementation for their applicable base QC: input/augmentation examples, combined
training/validation curves, training exposure, representation health and validation
freshness/backlog. Bind that base set in the complete experiment config; make an
inapplicable diagnostic explicit rather than silently omitting it.

Method-specific diagnostics extend this path with thin adapters. Reuse metric
definitions, layout/style helpers and rendering functions; do not copy a renderer
per architecture, trainer, worker or campaign, or recompute metrics independently
for a plot. Training, asynchronous validation and QC workers consume the same
recorded measurements and plotting owners. Keep common readout settings fixed
across checkpoints and ablations.

Save applicable qualitative QC at initialization and the configured cadence,
alongside numerical checks that can reveal failure even when examples look
plausible. Use a fixed, appropriately split QC roster and record selection rules,
source identities, scores and spatial coordinates where applicable. For grouped
exemplar galleries, use one group per column and configure at least 16 examples
from distinct source images down the rows. Page large collections without
omitting groups; retain empty columns and show available counts when fewer than
16 eligible sources exist. Do not duplicate examples to fill gaps. Keep different
learned representations explicitly identified and use their actual outputs for
selection. Save coverage, concentration, diversity and other applicable health
measurements beside the figures, using shared renderers with thin adapters.

When replacing duplicated QC, update current callers and remove the superseded
implementation in the same scoped change. Preserve immutable historical artifacts
and live execution pins. Shared instructions alone do not establish that existing
runtime paths have been consolidated; check callers before claiming coverage.

## Show Loss And Task Performance In One Updating Figure

The canonical learning curve contains the optimization loss and the same task
metric on training and validation data. For segmentation, show training and
validation Dice beside the loss; patch objectives alone are not segmentation
validation. Use the same deterministic inference recipe, aggregation and fixed
eligible membership for both metric series. Training-set evaluation is descriptive
fit, not evidence of generalization. Label validation used for selection honestly.

One renderer refreshes one stable `learning_curve.png` atomically from recorded
measurements throughout training and after asynchronous evaluations finish. Use
separate axes for loss and task performance, label train/validation distinctly,
and show pending evaluations explicitly. Do not write a plot per epoch or keep
parallel loss-only snapshots. Preserve numerical histories for reproducibility.
A figure inspection must confirm that task performance is actually present on
both splits before calling training monitoring complete.

## Persist A Scale-Free Training History

Every scientific training run must persist an append-only, machine-readable
training history from the first optimizer update through every resume. Record at
minimum:

- update/pass index, total loss, each unweighted loss component and its weighted
  contribution;
- learning rate, gradient norm, elapsed time;
- the exact source/unit coverage of the consumed prefix;
- training and validation observations, labeled by role and checkpoint, for the
  combined curve above.

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

- Configure recovery and scientific checkpoint cadences separately. Use bounded,
  atomically written rolling recovery saves for interruption protection; frequent
  recovery saves do not each trigger validation or retained checkpoint snapshots.
  Retain immutable checkpoints at initialization, a deliberately sparse configured
  evaluation cadence, final completion and the selected best checkpoint. Choose
  cadence from training duration, evaluation cost and acceptable recovery loss;
  do not inherit an every-update or every-epoch default without justification.
- Never replace or delete a checkpoint referenced by a pending evaluation,
  selection, resume or provenance record. Keep recovery retention bounded only
  after verifying those references. Apply cadence changes at a safe resume boundary
  with explicit provenance; preserve existing historical artifacts.
- Resume paths that map model tensors to an accelerator must explicitly restore CPU
  generator and global RNG state on CPU, and must have a deterministic continuation
  regression.
- Record the split policy in run provenance. Once a run writes train/validation
  manifests, resume must reload those snapshots and fail if the current split code
  would regenerate different membership. Never overwrite a run's split in place.
