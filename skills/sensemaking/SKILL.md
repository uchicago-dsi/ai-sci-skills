---
name: sensemaking
description: "Check whether findings make sense before trusting or reporting them by comparing to the nearest reference, asking what mechanism could explain them, and naming a falsifier. Use when the agent is interpreting results, summarizing progress, assessing regressions, or deciding whether an observation should change the plan."
---

# Sensemaking

## Use It As A Default Habit

- Compose this skill with domain skills instead of replacing them.
- Use it whenever you are about to trust, summarize, or act on a finding.
- Default question: does this result actually make sense, and if so, what should change because of it?

## Use This Output Contract

When using this skill, structure the reasoning as:

1. Observation: what happened.
2. Expected: what you thought would happen instead.
3. Nearest reference: the baseline, sibling case, prior run, known-good path, or control.
4. Conclusion: the current best explanation or inference.
5. Inference confidence: `low`, `medium`, or `high`.
6. Falsifier: one observation that would seriously weaken that conclusion.
7. Decision impact: what changes, or why nothing changes.

## Apply These Rules

- Separate observation from interpretation.
- Compare against the nearest useful reference, not an abstract ideal.
- Say why the chosen reference is the right baseline or control; if no fair baseline exists, weaken the conclusion.
- Prefer mechanistic explanations over labels such as "noisy", "unstable", or "weird".
- Keep confidence coarse: `low`, `medium`, or `high`, not fake precision.
- Use confidence for the inference, not for the raw observation.
- Let confidence reflect how likely the conclusion is to survive the nearest falsifier:
  - `low`: plausible lead; do not trust it yet
  - `medium`: current best explanation; enough to guide the next check
  - `high`: strong enough to treat as working truth until contradicted
- When the mechanism is spatial, temporal, structural, or artifact-like, inspect or create the nearest useful visual comparison instead of relying on scalar metrics alone.
- Ask whether the finding is strong enough to change the next action.
- If the result does not change the decision, say so explicitly.
- If the result contradicts the current story, update the story.

## Sanity-Check Findings

- Ask whether the effect size matches the claimed explanation.
- Ask whether the result is consistent across the closest comparable cases.
- Ask whether the evidence source is trustworthy enough for the claim being made.
- Ask whether a different explanation fits the evidence as well or better.
- Ask what would have to be true for this result to be misleading.

## Avoid Weak Sensemaking

- Do not report a metric or image difference without saying what it means.
- Do not prefer a summary metric over a decisive overlay, curve, slice, diff image, or side-by-side view when the mechanism is easier to see than describe.
- Do not narrate confidence beyond what the evidence supports.
- Do not assign confidence without first stating the inference.
- Do not treat one surprising result as a new truth without comparison.
- Do not stop at "better" or "worse"; say in what way and relative to what.

## End With A Decision

- If the finding is believable and consequential, state the changed plan.
- If the finding is believable but not consequential, state that no plan change is warranted.
- If the finding is not yet believable, state the next falsifier or sanity check.

## References

- Read `references/checks.md` for reusable prompts and compact response templates.
