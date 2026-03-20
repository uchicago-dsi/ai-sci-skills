# Sensemaking Checks

## Minimal Template

Use this compact form:

- Observation:
- Expected:
- Nearest reference:
- Conclusion:
- Inference confidence: `low`, `medium`, or `high`
- Falsifier:
- Decision impact:

## Ask These Questions

- Compared with what?
- By how much?
- Does the size of the effect match the proposed mechanism?
- Is this consistent with the nearest sibling or baseline?
- Would I trust this enough to change the next action?
- What would falsify my current interpretation?
- Is my confidence too high for the evidence I actually have?

## Good Reference Choices

- nearest known-good run
- prior result on the same slice/case/example
- explicit baseline or control
- same pipeline before the last meaningful change
- the simplest version of the method that already works

## Good Visual Checks

- side-by-side baseline vs candidate artifact
- overlay or diff image for structural changes
- curve or trajectory plot for temporal behavior
- representative failure case next to a known-good case
- one raw artifact view before and after a suspected fix

## Good Endings

- "Conclusion: X. Confidence: medium. Next step: Y."
- "Conclusion: this is real but not decision-changing. Confidence: high. Keep the current plan."
- "Conclusion: not yet trustworthy. Confidence: low. Next check: Z."
