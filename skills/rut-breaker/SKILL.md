---
name: rut-breaker
description: "Detect when work is stuck in a low-yield loop and force a better reset move. Use when the agent is repeating the same kind of fix, relaunch, sweep, or analysis without materially improving understanding or changing the decision."
---

# Rut Breaker

## Treat A Rut As A Pattern

- A rut is not just slow progress.
- A rut exists when similar actions keep recurring without sharper understanding, better evidence, or a changed plan.
- Compose this skill with domain skills after enough evidence suggests the current loop is low-yield.

## Use This Output Contract

When using this skill, report:

1. Repeating loop.
2. Evidence the loop is low-yield.
3. Stuck assumption.
4. Reset move.
5. Cheapest test after the reset.

## Detect Common Ruts

- Repeated relaunches with no new diagnosis.
- Repeated parameter sweeps that do not narrow uncertainty.
- Repeated code tweaks aimed at the same symptom with no mechanism.
- Repeated notebook updates that add detail but not a sharper conclusion.
- Repeated status checks on a job that is neither clearly healthy nor clearly failed.

## Apply These Rules

- Name the loop concretely.
- State what has actually been learned from the last few cycles.
- Identify the assumption keeping the loop alive.
- Choose a reset move that changes the information structure, not just the parameter values.
- Prefer reset moves that simplify, isolate, or compare against a stronger reference.

## Good Reset Moves

- reduce to one slice, one case, one batch, or one toy setup
- compare against the nearest known-good artifact or baseline
- inspect the raw artifact instead of the summary metric
- freeze all but one variable
- replace a broad sweep with one discriminative check
- change from post hoc interpretation to direct instrumentation or dumping
- stop a branch and return to the strongest open decision

## Avoid Fake Resets

- Do not call it a reset if it is the same move with a wider range.
- Do not add more logging unless the new log can falsify something.
- Do not launch more jobs just to feel active.
- Do not keep a branch alive solely because a lot of work has already gone into it.

## End With A Concrete Pivot

- State the reset move.
- State what you are stopping.
- State the first cheap test that will tell you whether the reset helped.

## References

- Read `references/reset-moves.md` for reset patterns and loop-detection prompts.
