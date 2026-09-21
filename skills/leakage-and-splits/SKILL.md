---
name: leakage-and-splits
description: "Keep held-out data genuinely held out: assign split eligibility to whole source groups, count independent units rather than rows, and check whether a split was already exposed by earlier fitting. Use when defining, reusing, or claiming a train/validation/test split, or when reporting an n."
---

# Leakage And Splits

The vocabulary below is generic on purpose. A "source group" is whatever repeats:
a participant, a site, an animal, a batch, a sensor, a time period, a physical
specimen.

## Hold Out Whole Groups, Not Rows

- A unit reported as held out must contribute neither gradient nor
  model/optimizer/checkpoint selection. If an outer objective uses data excluded
  only from an inner solve, call it adaptation or outer-training data and reserve a
  separate untouched evaluation split.
- For longitudinal or repeated-measure analyses, assign split eligibility to the
  whole participant/source group before forming pairs. If any visit is held out,
  exclude every visit in that group from training. Define sufficiency, permutation,
  and holdout counts in independent groups rather than in visits or pair
  combinations.
- Treat raw source identity, not an analysis-row identifier, as the unit. When rows
  or annotations reuse a source, record that identity, keep splits source-exclusive,
  report within-source envelopes, and balance cohort summaries over sources.

## Do Not Inflate The Denominator

- Do not count overlapping windows, crops, augmentations, repeated rows, or
  multiscale views of the same physical support as independent evidence. Collapse
  them to the declared independent unit, or report the dependence explicitly and
  narrow the claim.
- Permutation controls for group-level conditioning must permute across the
  grouping unit, not merely across items in batches that may share one source.
  Record donor/recipient group overlap and require it to be zero for a
  cross-source claim.
- A leave-one-unit-out agreement gate must compare the omitted unit against an
  estimate built exclusively from the retained units. Do not compare a retained
  estimate with a full aggregate that still contains the omitted unit, and include
  an adversarial two-unit disagreement check before trusting the gate.

## Audit Selection-Time Leakage, Not Only Execution-Time Access

- Before reusing a cached candidate set as label-free or source-only input, audit
  both its feature columns and its row-selection provenance. Exclude every manual-,
  reference-, label-, or oracle-selected row. Ignoring target-derived columns does
  not remove leakage already encoded by which rows were cached.
- A source-only or label-free process must receive a projected input surface that
  omits reference-bearing paths and fields. Keep post-selection diagnosis in a
  separate process behind an immutable selection commit; a promise not to read
  exposed labels is not a fail-closed boundary.
- Record formulation/design exposure separately from execution-time data access. A
  label-free executable does not make a feature, model, or policy label-unexposed
  when labels informed its definition. Bound development and confirmation claims to
  both facts.
- Any label-derived population prior must record a hashed source roster and hashed
  overlap sets with counts against every declared development, calibration, and
  evaluation roster. State which overlaps were excluded or retained; a boolean
  claim of independence is not sufficient.

## "Sealed" Is A Claim About History

Before calling a split globally sealed, virgin, or untouched, search prior target-,
calibration-, and outcome-fitting artifacts by raw source identity. Record any
historical exposure and scope the sealing claim to the exact current run or claim.
A new manifest label cannot erase prior use.

Exclude any prespecified smoke or falsifier set from policy, threshold, and
model-form selection. Freeze the shared choice on a source-exclusive calibration
manifest, then evaluate the untouched set prospectively. Aggregate repeated
observations within a source before balancing or selecting, so item count cannot
silently increase source weight.
