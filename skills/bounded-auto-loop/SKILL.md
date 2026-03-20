---
name: bounded-auto-loop
description: "Run a short, bounded autonomous loop of debugging or experiments before checking back in. Use when the user wants the agent to iterate for a few cycles, keep going autonomously, or stop only after a fixed budget or explicit stop rule is met."
---

# Bounded Auto Loop

Use this skill when the user wants a few autonomous iterations without an open-ended research spiral.

## Loop Contract

Before starting, lock these down:

1. Decision to change.
2. Current control or baseline.
3. Live hypotheses.
4. Iteration budget, usually 2-3 iterations.
5. Stop rule.
6. Return condition.

If any of these are missing, infer the narrowest reasonable version and state it briefly.

## Design The Loop

- Choose the smallest checks that can change the decision.
- Freeze everything not under test.
- Prefer one-variable changes over sweeps.
- Stay on the cheapest discriminative surface first.
- When a failure mode is easiest to see, prefer one decisive visual check over a larger batch of scalar metrics.
- Do not widen the search space mid-loop unless the current loop is falsified.

## Run One Iteration At A Time

For each iteration:

1. State the root-cause or causal hypothesis.
2. Make the minimal code or config change.
3. Run the nearest useful validation.
4. Interpret the result before launching the next step.
5. Update the plan or stop.

Do not queue multiple speculative branches at once unless they are independent and the stop rule still stays sharp.

## Stop Aggressively

Stop early if:

- the decision is already changed
- the new branch is materially better than control
- all plausible local variants fail in the same regime
- the next move is a scientific or product choice rather than an engineering extension
- the remaining improvements are too small to justify another cycle

Do not consume the full iteration budget just because it exists.

## Record Enough To Re-enter

- Reuse the project’s existing notebook or log.
- For each meaningful iteration, record:
  - question
  - action
  - evidence
  - result
  - decision impact
- Preserve exact artifact paths, job IDs, and commit hashes when relevant.

## Final Return Contract

When the loop stops, report:

1. Loop contract used.
2. Iterations run.
3. Best branch and nearest control.
4. Negative results that matter.
5. What changed in current understanding.
6. Best next suggested path.

Keep the report decision-focused. Do not dump every intermediate detail unless it changed the conclusion.
