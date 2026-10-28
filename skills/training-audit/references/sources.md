# Handbook sources and reading scope

Checked 2026-10-18. This skill is an original diagnostic workflow combining
engineering guidance with research measurement requirements. Its controls are
working hypotheses, not published guarantees of improvement. These handbooks
are engineering sources; they are not substitutes for a strong-venue research
review or for reading a borrowed method's full paper, supplement and author code.

## Main handbook

[Google Research: Deep Learning Tuning Playbook](https://github.com/google-research/tuning_playbook)
by Godbole, Dahl, Gilmer, Shallue and Nado. Inspected revision
[`7554a51f5d3002ba90308d39701b586f5a9b962e`](https://github.com/google-research/tuning_playbook/tree/7554a51f5d3002ba90308d39701b586f5a9b962e),
committed 2024-06-13; it is not an officially supported Google product.

Reading scope: introduction, incremental/scientific tuning approach, batch-size
guidance, optimization failures/warmup/clipping and run-duration guidance.
Useful principle: make tuning rounds answer a specific question with comparable
evidence. The batch-size discussion is not a license to assume equivalence for
batch-dependent SSL objectives. Illustrative thresholds and warmup/clipping
recipes are not universal defaults. This is the closest broad handbook located,
not a claim that it comprehensively covers modern foundation-model training.

Google also hosts the [Deep Learning Tuning Playbook](https://developers.google.com/machine-learning/guides/deep-learning-tuning-playbook).
Checked its overview on 2026-10-18: the page is marked last updated 2025-08-25
and describes the GitHub document as an earlier version. Its update date does
not establish that every technical recommendation changed. The detailed scope above remains
bound to the inspected GitHub revision.

Also read the hosted [training-pipeline guidance](https://developers.google.com/machine-learning/guides/deep-learning-tuning-playbook/additional-guidance),
[run-duration guidance](https://developers.google.com/machine-learning/guides/deep-learning-tuning-playbook/number-of-steps)
and [learning-rate appendix](https://developers.google.com/machine-learning/guides/deep-learning-tuning-playbook/learning-rate)
on 2026-10-18 (pages marked updated 2025-08-25). Reading scope: evaluation
cadence and sampling, checkpoint selection, distributed execution details,
short-horizon tuning bias and schedule/budget interactions; learning-rate
appendix through its decay-schedule discussion.

Consequences for this tool: keep periodic development membership fixed; account
for minority-class counts and padded evaluation rows; bind asynchronous scores
to the actual checkpoint. Early tuning rankings need not survive longer runs,
especially when the decay schedule changes. The guide recommends retrospective
checkpoint selection and generally treats prospective early stopping as
unnecessary. That recommendation does not replace a project's approved stopping
policy. A selected checkpoint is not an unbiased final-test estimate. Its
distributed RNG advice also needs framework-specific sampler interpretation;
do not blindly assign different sampler seeds to ranks that must partition one
shared permutation. Consult hosted topic pages when refreshing recommendations
rather than assuming the GitHub and hosted versions match.

## Framework-specific execution details

PyTorch **2.6** documentation, selected to match the Prima runs under review;
recheck the installed version for another project or a newer environment.

- [Automatic mixed precision examples](https://docs.pytorch.org/docs/2.6/notes/amp_examples.html):
  read unscaled-gradient/clipping, accumulation and multiple-optimizer sections.
  These establish update-boundary and gradient-scaling semantics, not an optimal
  precision policy for this workload.
- [Numerical accuracy](https://docs.pytorch.org/docs/2.6/notes/numerical_accuracy.html):
  read reduced-precision reduction and attention sections. Precision/backend
  choices can change behavior; no global precision override is prescribed.
- [torch.optim](https://docs.pytorch.org/docs/2.6/optim.html): read scheduler
  ordering and optimizer-state loading sections. The skill adds checking actual
  skipped-update/scheduler behavior rather than assuming a successful update.

## Foundational companions

- [Karpathy: A Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/)
  (2019): identified the requested post and read its overview. Its basic debugging
  perspective remains useful; this skill is not a full adaptation of that post.
- [Stanford CS231n: Neural Networks, Part 3](https://cs231n.github.io/neural-networks-3/):
  inspected the diagnostics outline and gradient-check discussion. Pointer for
  deeper study, not evidence that every suggested ratio or numerical heuristic
  remains appropriate for pretrained transformers. No universal update/weight
  threshold was imported.
