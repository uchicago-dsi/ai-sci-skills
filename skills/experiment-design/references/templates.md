# Experiment Design Templates

## Minimal Template

- Decision:
- Hypotheses:
- Baseline / control:
- Proposed arms:
- Predicted outcomes:
- Readouts:
- Stop rule:
- Next move if positive:
- Next move if negative:

## Good Questions

- What decision am I trying to make?
- Which hypotheses are still live?
- What is the nearest baseline?
- Which single change matters most?
- What is the cheapest run that would kill the weak hypothesis?
- What result would make me stop this line of work?
- Which single visual would tell me fastest that the hypothesis is wrong?

## Strong Patterns

- baseline + one targeted variation
- one cheap pilot before broad launch
- one slice/case/subset before whole-dataset run
- one mechanism check before parameter sweep

## Anti-Patterns

- broad grid without a decision rule
- multiple simultaneous changes per arm
- no explicit control
- readouts chosen after seeing the result
- expensive run used to answer a cheap question
