---
name: decision-gates
description: "Separate a scientific gate that decides promotion, continuation, stopping, or retirement from a mechanical check you can set yourself, get explicit approval for the former, and report it exactly as frozen. Use when proposing a threshold, interpreting a gate result, or scoping a negative result."
---

# Decision Gates

## Get Explicit Approval For A Scientific Gate

Before adopting any scientific promotion, continuation, stopping, or retirement
gate, present the exact:

- metric definitions and thresholds;
- comparison reference;
- independent denominator;
- aggregation;
- evaluation timing;
- the action triggered by pass and by fail;

and obtain explicit approval. Do not infer approval from a general experiment
request, from prior autonomy, from a pilot, or from a similar gate used elsewhere.

Once approved and frozen for a run, preserve that gate and report it exactly. Any
later interpretation or replacement is a separately versioned decision layer, not a
retroactive edit.

## A Mechanical Check Is Not A Gate

The acceptance criteria of a mechanical or developer check need no approval: a
smoke that must reach a real kernel, a schema that must validate, a guardrail that
must reject a known-bad input, a threshold below which a run is obviously not
learning. Set those yourself and report the number.

If a criterion starts deciding whether something is promoted, retired, or
continued, it has become a scientific gate and the approval rule applies again.

## Check That The Gate Can Be Satisfied Before You Build For It

- Before building review, calibration, or reducer infrastructure, enumerate the
  maximum independent eligible cohort under the frozen source, split, availability,
  and contract rules, and prove it can satisfy every predeclared denominator gate.
  If any gate is mathematically unreachable, stop with typed feasibility evidence
  instead of building the downstream workflow.
- Before defining an identifiability or posterior-width gate, write the forward
  model with all fitted nuisance parameters and enumerate scale, shift, and
  permutation symmetries. Do not interpret a coordinate that a nuisance
  reparameterization leaves invariant.
- Before setting an automated QC coverage gate, compute the manual/reference ceiling
  under the same policy. If the reference itself can fail, report overall coverage
  against that ceiling and define any fixed pass fraction on the reference-eligible
  subset.

## Grade Outcomes On More Than Pass/Fail

Interpret a candidate successor on three levels unless a different scheme is
approved for the named experiment:

1. **Mechanically invalid** — required fidelity, data-contract, collapse, or
   numerical guardrails fail.
2. **Mechanically valid and promising** — guardrails pass, and weak,
   subgroup-specific, or directional signals justify retention or further study.
3. **Strong success** — the approved large-effect gate passes.

Missing the strong-success threshold does not by itself retire, discard, or block
further use of a mechanically valid candidate. Preserve weak signals, because later
improvements, combinations, or subgroup analyses may reveal utility — while
labeling their evidential strength accurately.

## Scope A Negative Result To What Was Tested

Scope negative results to the exact formulation, role, and claim tested. Before
retiring a broader mechanism family, use retained artifacts for the cheapest
decision-changing check of whether partial signal remains useful in a
contract-preserving weaker role — a feature, a prior, a symmetry breaker — while
keeping the best valid baseline. Failure as a standalone replacement does not by
itself falsify conditional utility. Reassess source availability against each
consumer's minimum information contract: evidence inadequate for a first-pass
estimate may still support a baseline, tail, or QC role.


## Form The Feasible Set Before You Pick A Winner

When "pass" means that a candidate or template satisfies several criteria jointly,
form the feasible set under all the criteria first, and persist a winner from that
set. Do not optimize one criterion and then test the others only on that optimizer —
the best candidate under one criterion is routinely infeasible under another, and
checking afterwards turns a joint requirement into a single-criterion search with a
veto that fires too late.
