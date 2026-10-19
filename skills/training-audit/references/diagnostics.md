# Symptom-driven diagnostics

These are hypotheses to discriminate, not automatic diagnoses or universal
hyperparameter recipes. Select relevant rows; do not run every check by default.

| Symptom | Evidence to inspect | Smallest useful discriminator |
| --- | --- | --- |
| Development declines immediately | Step-zero score, probe identity, input/feature normalization, train/eval mode, layer-wise drift, actual encoder LR | Repair a demonstrated measurement mismatch first; if encoder drift or update size makes aggressive adaptation plausible, test a fresh matched lower-encoder-LR arm, retaining the original projector/head recipe |
| Train improves, development worsens | Same-readout train/development curves, independent group splits, class/site mix, feature drift and calibration | A gap is compatible with overfitting, but does not identify the cause. Compare matched optimization before attributing failure to architecture or SSL itself |
| SSL improves, downstream worsens | Loss components, backbone versus projector features, same-roster feature variance/covariance/rank, linear readouts on each target task | Distinguish objective misalignment, forgetting, collapse and probe conditioning; a stable feature norm alone excludes none of these |
| Loss or gradients spike | Pre-clip gradient norms, clipping fraction, actual LR transition, optimizer state, per-source batches, nonfinite values | Locate the first failing operation/batch; separately change implicated schedule or numerical operation rather than masking it with clipping |
| Loss barely changes | Trainable parameters, optimizer ownership, gradient connectivity, effective updates, frozen modules, label/loss scale | Inspect one real update through the existing trainer. Tiny-update mechanics checks are not generalization experiments |
| Bigger batch changes behavior | Physical versus accumulated batch, global/local moment calculation, negatives, BatchNorm, loss reduction, update count | Establish whether the objective changed before interpreting an LR or efficiency comparison |
| Resume changes the curve | Checkpoint step, optimizer moments, parameter ordering, scheduler position, scaler, RNG and sampler/cursor, teacher EMA if used | Reconcile the saved boundary; an intentional state reset is a new experiment, not an invisible continuation |
| Training looks healthy but exposure is low | Unique source units, repeat counts, sampling weights, data stalls, rejected inputs | Reconcile data coverage and throughput; additional optimizer updates may mostly repeat the same examples |
| Async evaluation falls behind | Checkpoint hashes, evaluator queue/failures, complete registered endpoint set | Fix the existing evaluation path. Do not count absent results toward patience or bypass a durable stop decision on resume |

## Numerical and optimization gotchas

- Under gradient scaling, inspect/clip gradients after unscaling and after the
  intended accumulation boundary. Check skipped optimizer steps; the scheduler
  must not silently advance as though an update happened when it did not.
  With multiple optimizers, inspect each owner's update/skip behavior.
- Check loss reduction and scale per objective, weight-decay parameter groups,
  scheduler units and off-by-one boundaries. A logged next-step LR can differ
  from the LR that generated the checkpoint. Frozen weights can still have
  changing BatchNorm buffers; a detached teacher must also use its intended mode.
- Use the installed framework version's precision guidance. BF16's range does
  not make all reductions numerically safe; finiteness of the final total loss
  does not establish healthy covariance or gradient calculations. Promote only
  the implicated operation in a numerical control and record the change.
- Normalization and covariance losses can depend on actual per-device batch
  composition. Do not assume gradient accumulation recreates global moments.
  Check source/class grouping before blaming the encoder or batch size alone.

## Scope of negative results

An early decline under one LR establishes that recipe's observed trajectory.
It does not show that every LR, schedule, objective or initialization in the
family fails. Conversely, a lower LR that merely postpones degradation does not
establish an improved converged result. Preserve the baseline, match exposure,
follow the approved stopping rule and state which explanation the control
actually weakens. If all optimization controls fail, objective mismatch remains
an independent hypothesis; do not keep sweeping indefinitely.
