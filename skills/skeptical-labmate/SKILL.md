---
name: skeptical-labmate
description: "Review a claim, result, or next-step recommendation like a sharp labmate who is trying to catch overclaiming, bad baselines, confounds, and missing checks. Use when the agent is about to trust a result, recommend a follow-up, or tell a scientific story."
---

# Skeptical Labmate

## Use It As A Review Pass

- Use this skill before strong conclusions, expensive follow-ups, or paper-style summaries.
- Compose it with `$sensemaking` or `$experiment-design`; this skill is the critical second pass, not the primary analysis.
- The goal is not generic doubt. The goal is to name the most dangerous weak point and the cheapest way to resolve it.

## Use This Output Contract

When using this skill, report:

1. Claim or plan under review.
2. Strongest alternative explanation or confound.
3. Weakest assumption, comparison, or baseline.
4. Cheapest check that would most improve confidence.
5. Recommendation:
   - proceed
   - proceed but weaken claim
   - run one more check
   - stop or pivot

## Apply These Rules

- Attack the baseline first: is it current, fair, and actually comparable?
- Ask what else changed besides the claimed cause.
- Ask whether the result could be measurement, logging, data-split, scheduler, or implementation artifact.
- Ask whether the claim is stronger than the evidence.
- Ask whether the claimed confidence is higher than the evidence supports.
- Ask what a hostile reviewer or careful labmate would object to first.
- Prefer one concrete discriminative check over a vague list of worries.

## Good Skeptical Questions

- Compared with what, exactly?
- What is the strongest non-hypothesis explanation?
- Could the apparent gain come from a confound or artifact?
- Is this result mature enough to trust, or still early/noisy/incomplete?
- What nearby seed, case, split, or baseline would most likely break this story?
- What would make us retract or weaken the claim?

## Avoid Fake Skepticism

- Do not raise abstract doubt with no concrete mechanism.
- Do not demand perfect certainty before acting.
- Do not block progress when the cheap next check is obvious.
- Do not nitpick minor caveats while missing the main confound.

## End With A Decision

- If the claim is good enough, say why and what remains caveated.
- If the claim is too strong, rewrite it in the weaker form you would trust.
- If the plan is weak, state the one check or comparison that should happen before spending more compute.


## Ask Whether It Is A New Mechanism Or A Cleaner Replication

Before presenting a retrain as a new mechanism, compare its data, target, objective,
model, split, and endpoint with the nearest completed attempt. If only the split or
the provenance changed, call it a cleaner replication or a diagnostic, not a remedy
for the prior scientific failure.

## Do Not Claim A Global Result From A Local Search

Before claiming a global peak or extremum for a multimodal curve or objective,
enumerate the relevant modes over the declared domain and refine each candidate. One
initializer, grid neighborhood, or local optimum is not global evidence.

## Diagnose Censoring Before Widening A Prior

Do not calibrate a bounded prior by inflating its covariance when missed references
are parked at a parameter bound. Diagnose the censoring and separate genuine latent
variation from measurement uncertainty before widening the prior or relaxing
coverage.

## Watch For A Stand-In That Cannot Answer The Question

A diagnostic that substitutes a different model family for the one under test must
name which structural properties of the substitute could by themselves produce the
observed result, and it may not carry a negative conclusion about the real model
when the substitute lacks a degree of freedom the real model has. A family that
cannot express the observed shape will always pay a large residual and will always
buy amplitude with an implausible scale, so both outcomes are properties of the
stand-in rather than findings. Cheapness justifies a stand-in for a mechanics probe,
never for a claim about the real model's capability. Labelling the substitution is
necessary and not sufficient — the label has to constrain which conclusions are
allowed.

## References

- Read `references/prompts.md` for compact review prompts and response shapes.
