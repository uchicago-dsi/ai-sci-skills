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


## Run It Only When A Result Would Change The Next Action

- Run a preliminary experiment only when its possible results can change the next
  action. State the question, what different outcomes would change, and why the
  existing evidence is insufficient.
- There is no mandatory cohort-size ladder. Skip an intermediate-scale run when it
  would not change the next experiment or resolve a material implementation or
  scientific uncertainty. Before running one, name the unresolved question and which
  result would change the next action; if either plausible outcome still calls for
  full-scale learning, go straight there from a real small-subset learning check and
  a representative input-shape and memory check.
- Memorization tests diagnose optimization and representation limits. They do not
  establish the ranking on unseen units, and they do not exclude benefits that
  require scale to appear. Do not demand a small-cohort winner before a larger
  comparison intended to answer those questions.
- Treat a small run of a data-hungry method as a mechanism check only, never as
  evidence about whether it works at scale. A small pilot may reject such an
  implementation only when it exposes a scale-independent mechanics defect directly,
  such as invalid gradients or pathological constraint saturation on clean inputs.
  Before rejecting the family, train the strongest mechanically credible formulation
  on the full currently eligible cohort, and record the eligible denominator and
  every exclusion.

## Do Not Train To Satisfy A Ritual

Do not wait for plateau by default. Continue to convergence when the fit floor, an
optimization-versus-capacity diagnosis, or an unresolved comparison needs it;
otherwise use a bounded run and review once the decision-changing evidence is
available. Do not prolong training merely to satisfy a convergence ritual, or extend
a small experiment to answer a question it cannot answer.

Preserve any already-approved frozen gate; changing it still needs approval.
Mechanical validity, matched references, and required QC remain necessary even when
plateau is not.

## Do Real Scoped Work

Do real scoped work once the code and the data contract are understood. Use toy,
synthetic, or dry-run checks only where they test a concrete failure mode more
cheaply than the real path.

Do not expand a representative smoke into an array or cohort run when a primary
predeclared gate fails, or when the smoke was scientifically uninformative. Repair
or redesign first: technical job success is not a passing scientific smoke.

## References

- Read `references/templates.md` for compact design templates and anti-patterns.
