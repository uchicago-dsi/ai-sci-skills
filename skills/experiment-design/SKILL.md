---
name: experiment-design
description: "Design the smallest useful experiment matrix that separates important hypotheses and changes a decision. Use when the agent is proposing runs, ablations, sweeps, benchmarks, or debugging experiments across research or engineering projects."
---

# Experiment Design

## Design For Decisions

- The purpose of an experiment is to change a decision, not to accumulate runs.
- Start from the decision that needs to be made.
- Work backward to the fewest experimental arms that separate the live hypotheses;
  use the full eligible dataset for each arm.

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
- Reuse existing mechanics evidence; perform a minimal real-input check only when
  an unverified execution path needs it, then run the full eligible cohort.
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
- A basic mechanics check may catch invalid shapes, gradients, geometry, memory
  use or outputs before launch. Do not turn it into a small-cohort scientific study.

## End With A Clear Recommendation

- State the exact runs to launch.
- State what result would cause you to stop, continue, or pivot.
- State what you are deliberately not running and why.
- State the baseline disposition and exact falsification scope before pivoting.


## Measure On Every Eligible Unit

Default to the full eligible dataset for training, analyses, comparisons and
scientific diagnostics. A smaller experiment matrix means fewer arms, not fewer
participants. Do not substitute a subset for convenience, queue delay, or an
estimate that a full run will take too long. If a concrete resource constraint
prevents the full run, explain it and ask Anna before narrowing scientific scope.

Use at most a minimal basic mechanics check for an unverified path, combining
real-kernel execution, shape/geometry, gradients, memory and timing checks where
possible. Reuse that evidence; repeat only to verify a specific repair or newly
unverified path. Then go directly to the full eligible dataset. Do not build a
ladder of one-case, few-case and intermediate-cohort runs.

Small runs support mechanical observations only. Do not use their scores, learning
curves or visual examples to rank methods, claim benefit or failure, reject a
scientific premise, choose a scientific direction, or infer generalization. State
the mechanical fact and what remains untested; draw scientific conclusions from
the full eligible comparison. A basic failure may require an implementation repair,
not a verdict on the method.

"Eligible" respects participant-exclusive folds, authorized data access and sealed
confirmation sets: full training means every training-eligible participant, not
training on validation or confirmation data. Resampling-based uncertainty and
selected illustrations may accompany a full-cohort analysis; they do not replace it.

## Run It Only When A Result Would Change The Next Action

- Run a preliminary experiment only when its possible results can change the next
  action. State the question, what different outcomes would change, and why the
  existing evidence is insufficient.
- Scientific uncertainty is resolved on the full eligible cohort. A subset check
  is justified only by a specific unverified mechanical behavior, not by a desire
  to see whether a scientific comparison looks promising before running it fully.
- Do not demand a small-cohort winner before full-cohort comparison. Before
  rejecting a method family, evaluate its strongest mechanically credible
  formulation on the full currently eligible cohort; record the denominator and
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

Repair a failed mechanics check before expanding that execution path. A mechanically
valid small check need not show scientific benefit before full-cohort launch;
establishing that benefit is the full experiment's job. Preserve any explicit
user-approved launch gate rather than inventing one from small-run scores.

## References

- Read `references/templates.md` for compact design templates and anti-patterns.
