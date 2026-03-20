# Handoff Templates

## Minimal Template

- Goal: ...
- State: ...
- Evidence: ...
- Uncertainty: ...
- Next: ...

## Code Work Template

- Goal: what change or bug is in flight
- State: what is implemented right now
- Evidence: touched files, branch, commit SHA if any, validation result
- Uncertainty: what still needs checking
- Next: exact command, file, or test to run first

Example shape:

- Goal: finish X without regressing Y
- State: patch is in place on `branch-name`; worktree clean/dirty
- Evidence: `/abs/path/file.py`, commit `abc1234`, `pytest ...` passed/failed
- Uncertainty: edge case Z still unverified
- Next: run `...` or edit `/abs/path/file.py`

## Experiment Template

- Goal: what hypothesis or decision the run is meant to answer
- State: what has been submitted, finished, or ruled out
- Evidence: config path, run root, overlay path, notebook path, job IDs
- Uncertainty: what result or comparison is still missing
- Next: exact comparison, resubmission, or notebook update

Example shape:

- Goal: decide whether config B beats baseline A on metric M
- State: baseline done; candidate running/pending/failed
- Evidence: `/abs/path/config.yaml`, `/abs/path/run_root`, job `123456`
- Uncertainty: candidate has not produced metric M yet / failure cause not confirmed
- Next: inspect `...` or resubmit with `...`

## Monitoring Template

- Goal: keep campaign moving until the next decision point
- State: which jobs are healthy, waiting, stalled, failed, or completed
- Evidence: job IDs, `squeue`/`sacct` read, log path, newest artifact path
- Uncertainty: what signal is missing to classify the ambiguous case
- Next: the exact log, command, or replacement submission to check first

## Notebook Rule

- Put durable detail in the canonical notebook.
- Use the handoff as a compact restart packet that points into that detail.
