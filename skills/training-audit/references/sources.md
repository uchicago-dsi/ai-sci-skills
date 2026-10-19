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
