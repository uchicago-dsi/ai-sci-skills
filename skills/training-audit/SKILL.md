---
name: training-audit
description: Diagnose training instability, early validation decline, or uncertain convergence from saved run evidence, and choose a controlled optimization check before rejecting a method.
---

# Training audit

Turn a training symptom into an evidence-backed diagnosis and the smallest next
check that could change it. Use existing trainers, evaluators and run artifacts;
this skill does not introduce another training or tuning loop.

Invoke with `$training-audit` and a run directory, plus the symptom or comparison
to investigate. Return the evidence-backed diagnosis, unresolved explanations
and one discriminating next check. If the run artifacts are incomplete, identify
the missing evidence before recommending a sweep.

## Establish what actually ran

Read the run's saved effective config, producing commit, checkpoint metadata and
measurement registration. A similarly named config in today's checkout is not
historical evidence. Reconcile encoder/head/projector parameter ownership, actual
LRs, optimizer, schedule, initialization, precision, batch construction, inputs
and exposure. Distinguish intended configuration from executed/logged behavior.
Name missing evidence rather than reconstructing it from a convenient default.

For a historical audit, make one compact row per materially different recipe:
run/pin; eligible and seen independent units; actual optimization; observed
decline; controls already tried; unresolved confounds; next useful check.

## Check the measurement before the model

Compare the same eligible units, endpoint, preprocessing, feature layer/pooling
and readout algorithm. For probes, check feature scaling, regularization search,
training-only folds, grouping, fitting budget, seed and aggregation. A fixed
training-only selection procedure may choose different regularization values;
record them. Mixing that procedure with fixed-regularization scores changes the
measurement. Verify eval/train mode and stochastic transforms at feature extraction.

Separate training, development/model selection and held-out test exposure.
Unlabeled pretraining and teacher targets also count as exposure. Repeatedly
inspecting a test metric does not leave it untouched. Use the existing approved
development readouts for tuning.

Plot or inspect the initial checkpoint and early downstream measurements alongside
training loss, LR and exposure. A falling SSL loss does not demonstrate improving
diagnosis or future-risk features. Show presentations and distinct eligible
images/exams/women separately; repeated crops are not new independent examples.

## Investigate only plausible mechanisms

Use the relevant rows in [diagnostics.md](references/diagnostics.md). First ask
whether this is a measurement mismatch, optimizer/numerical failure, insufficient
training, or lost generalization/transfer. Several may remain possible.

Inspect per-parameter-group LR actually used, gradients before clipping, skipped
updates, objective components and feature health when available. A healthy scalar
loss can conceal a frozen encoder, an overactive projector or collapsed features.
For Adam-like optimizers, LR times raw gradient is not the parameter update;
measure actual updates if that distinction matters. Missing instrumentation is
an uncertainty, not evidence of health.

## Choose a discriminating control

Keep initialization, eligible pool, sampling, objectives, readout and exposure
matched while changing the suspected optimization factor. A fresh lower-encoder-LR
arm can test feature destruction; a separate warmup/schedule arm tests its stated
schedule package. Changing warmup and decay together does not isolate either one.
Do not add regularization, change crops and shrink data in the same rescue arm.

Use the full eligible training pool for scientific comparisons unless the user
explicitly chooses a subset. A cheap mechanics smoke establishes execution only.
Compare at matched exposure and relevant schedule phases, then apply the approved
completion policy. A slower learner's early score does not establish superiority
or inferiority. Report throughput/GPU cost separately from statistical progress.

Do not automatically scale LR with batch size. Accumulation, larger physical
batches and distributed batches can implement different objectives when losses
use batch statistics, negatives or normalization. Verify their actual semantics.

Use the project's single explicit config and existing validation path. Resume
the original optimizer/scheduler/scaler and data state for a true continuation;
a changed optimizer recipe is a new named control. Preserve frozen artifacts.
Keep the best valid baseline active. Reject only the tested delta when it fails.

## Leave a decision, not a checklist

Record: **symptom and evidence; plausible mechanism; competing explanation;
next control and falsifier; settings held fixed; expected decision.** Label
observations, inferences and guesses. If a check was not run, say so.

Use the existing approved scientific stopping/selection rule; do not invent a
numeric threshold here. Missing async evaluation is pending, not no improvement.
Budget exhaustion, runtime completion, scientific completion and model promotion
are separate states. Record exposure and reason at stopping, not just step count.

For source scope and limitations see [sources.md](references/sources.md).
