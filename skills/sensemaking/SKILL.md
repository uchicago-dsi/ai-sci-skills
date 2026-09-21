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
4. Best explanation: the most plausible mechanism right now.
5. Falsifier: one observation that would seriously weaken that explanation.
6. Decision impact: what changes, or why nothing changes.
7. Baseline disposition: whether the nearest valid baseline remains active or
   has been superseded, and by what evidence.
8. Falsification scope: the exact hypothesis or changed delta rejected, plus
   the parent method or unchanged components that remain live.

## Apply These Rules

- Separate observation from interpretation.
- Compare against the nearest useful reference, not an abstract ideal.
- Say why the chosen reference is the right baseline or control; if no fair baseline exists, weaken the conclusion.
- Prefer mechanistic explanations over labels such as "noisy", "unstable", or "weird".
- When the mechanism is spatial, temporal, structural, or artifact-like, inspect or create the nearest useful visual comparison instead of relying on scalar metrics alone.
- Ask whether the finding is strong enough to change the next action.
- If the result does not change the decision, say so explicitly.
- If the result contradicts the current story, update the story.

## Preserve The Best Baseline

- Keep the best valid baseline active until a prospectively defined successor
  beats it on the same decision readouts.
- Attribute a failure only to what changed relative to that baseline. Failure
  of an additive rescue rejects the rescue or combination, not the retained
  baseline.
- Before pivoting, name the baseline, changed delta, result, exact hypothesis
  falsified, hypotheses not falsified, and retained active path.
- Scope stop rules narrowly. Do not retire a successful parent method because
  a broader extension or challenger failed unless that parent was directly
  retested and failed.

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
- Do not treat one surprising result as a new truth without comparison.
- Do not stop at "better" or "worse"; say in what way and relative to what.

## End With A Decision

- If the finding is believable and consequential, state the changed plan.
- If the finding is believable but not consequential, state that no plan change is warranted.
- If the finding is not yet believable, state the next falsifier or sanity check.


## Verify The Element Set Before Comparing Numbers

Verify a matched element set through a quantity that depends **only on the target**,
computed over the whole set by each side independently: the target's mean square, or
a rank-k approximation of it.

Item count, support, and scoring surface can all agree while the roster silently
differs, and every model-dependent number stays plausible when it does. A
target-only quantity cannot differ between two owners scoring the same elements, so
it fails loudly and immediately when they are not. Two owners once disagreed on a
reference by 0.024 with matched counts and matched surfaces, because their
selections overlapped on 12 of 48 rows; the rank-1 residual is what exposed it, and
on the shared 12 they agreed to 5e-16.

Join on physical identity rather than on a positional index. An index is renumbered
per artifact, and a wrong join returns a plausible number rather than an error.

## Compare Matched Units, Not Aggregates

Per-unit losses and errors are usually heavy-tailed, so a mean over a window is
dominated by whichever few hard units it happens to contain. Pair by unit, report
medians and a paired ratio, and treat a difference that survives neither as absent.

## Read The Units Before Converting

- Check whether a field is a unit fraction or already in percentage points before
  converting — a `_frac` and a `_pct` suffix mean different things, and only the
  metric's owner settles it. For decision-relevant values, report both the raw
  fraction and the percentage explicitly.
- When merging CSV-backed metrics, select numeric cells value by value rather than
  inferring a whole column from one row. Missing string identifiers deserialize as
  `NaN` and must never enter a numeric aggregation.

## Make QC Galleries Show The Edges

- A distribution or gate QC gallery must deterministically include the best example,
  the nearest below threshold, the nearest above threshold, and the worst, within
  each major stratum. The first few examples in lexicographic order are not enough.
- A renderer working in a native coordinate system must not assume a fixed array
  axis is the one to slice along. Choose a readable plane from the actual geometry,
  and verify explicitly that anisotropic inputs do not collapse into unreadable
  narrow panels.

## References

- Read `references/checks.md` for reusable prompts and compact response templates.
