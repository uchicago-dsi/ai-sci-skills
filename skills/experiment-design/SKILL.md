---
name: experiment-design
description: "Design the smallest useful experiment matrix that separates important hypotheses and changes a decision. Use when the agent is proposing runs, ablations, sweeps, benchmarks, or debugging experiments across research or engineering projects."
---

# Experiment Design

## Design For Decisions

- The purpose of an experiment is to change a decision, not to accumulate runs.
- Start from the decision that needs to be made.
- Work backward to the smallest experiment that can separate the live hypotheses.

## Use This Output Contract

When proposing an experiment, report:

1. Decision to make.
2. Live hypotheses.
3. Nearest control or baseline.
4. Minimal experiment matrix.
5. Predicted outcomes by hypothesis.
6. Readouts that will decide the result.
7. Stop rule and follow-up rule.
8. Baseline inheritance: what remains active if the candidate fails, and what
   evidence would be required to supersede it.

## Apply These Rules

- Every arm should exist for a reason.
- If two arms would not change the decision differently, remove one.
- Prefer one-variable changes over broad combinatorial sweeps.
- Freeze everything not under test.
- Use the nearest baseline, not a weak or outdated one.
- If the baseline is unfair, stale, or confounded, fix that before treating the experiment as decision-worthy.
- Prefer cheap discriminative checks before expensive cluster-scale runs.
- Keep the best valid baseline as an explicit arm or immutable comparison until
  a prospectively defined successor beats it on the same decision readouts.
- For every candidate, identify the exact delta from the baseline and what
  remains active if that delta fails.
- Make stop rules hypothesis-scoped. Failure of an additive rescue or broader
  variant retires that addition or combination, not an unchanged successful
  parent method.

## Choose Readouts Carefully

- Pick the smallest set of metrics, artifacts, or visual checks that can separate the hypotheses.
- Include a visual readout when failure modes are easier to see than summarize, for example overlays, curves, slices, masks, diff images, or before/after artifact views.
- Include at least one readout that reflects the real success criterion, not just a proxy.
- Name in advance what outcomes would favor each hypothesis.
- Decide how you will interpret mixed results before launching.

## Guard Against Waste

- Do not broaden the matrix when a smaller check is still ambiguous.
- Do not run a sweep just because parameters are available.
- Do not collect outputs you will not actually inspect.
- Do not start a large run if a toy, slice, overfit, dry-run, or subset check would reveal the same failure mode.

## End With A Clear Recommendation

- State the exact runs to launch.
- State what result would cause you to stop, continue, or pivot.
- State what you are deliberately not running and why.
- State the baseline disposition and exact falsification scope before pivoting.

## References

- Read `references/templates.md` for compact design templates and anti-patterns.
