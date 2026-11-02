# Job tracking through Slack: a worked example

This composes with `job-babysitting` (how to classify job state) and `slurm`
(scheduler commands). This file covers the Slack side: what to post, when, and
how the pieces fit together.

## The situation

Eight Slurm jobs ran an LLM labelling pipeline over a 546-case cohort, each on
4 GPUs with a 12 h limit. Every job wrote one result file per case, so
`units/*.json` counted progress, and it started a model server that logged
`Application startup complete` when ready. The server had an intermittent GPU
crash (`CUDA error: an illegal memory access`). One evening every job started
dying 10–30 s after startup. The jobs resumed from their result files, so each
crash cost time but not finished work. Nobody could fix what they didn't know
about.

## Setup used

```bash
# ~/.config/slack-notifications/config
SSW_PROGRESS_GLOB='units/*.json'
SSW_TOTAL=546
SSW_LOGS='server.log'
SSW_READY_RE='Application startup complete'
```

```bash
setsid nohup slurm-slack-watch 1878868 1878869 … > ~/.local/state/ssw.log 2>&1 < /dev/null &
```

## What the channel received, and why each message exists

| Message | Why |
|---|---|
| `:eyes: Watching 8 jobs` | Confirms the watcher is alive and which jobs it covers |
| `PENDING → RUNNING` | The queue wait was hours. This is the "go look now" moment. |
| `service up` | Model load takes minutes and says little. This marks when the risky window opens. |
| `:white_check_mark: survived 2+ min past startup` | **The key test.** The instant-crash pattern hit within seconds of startup, so surviving past it was the falsifier for the leading fix. |
| `:rotating_light: <first CUDA error>` | The earliest possible warning, often before Slurm marks the job failed |
| `:warning: Issue report` | Separates *early* crashes (repeatable: investigate, don't resubmit) from *mid-run* ones (intermittent: resume) |
| `:bar_chart: Progress update` | Hourly check, posted only on a state change or 5+ new cases since the last post |
| `:zzz: Still watching` | After 6 h of silence, so quiet still proves the watcher is alive |

## Decisions that mattered

- **Notify-only watcher.** The report *suggests* resubmitting, and a person or
  supervising agent does it. An early crash and a mid-run crash call for
  opposite actions, and an automatic resubmit loop would have burned GPU hours
  on a repeatable failure.
- **Read only the current attempt's logs.** A requeued job keeps its ID, and
  its old log still contains the previous crash. The watcher remembers each
  log's size when an attempt starts and reads only what comes after.
- **Timing sets the verdict.** A crash under `SSW_EARLY_MIN` after the service
  came up (or after the job started, if that wasn't seen) is reported as
  early and repeatable.
- **Test reports on real failures first.** `--dry-report` on the evening's
  failed jobs checked the rules before anyone relied on them.
- **The PI in the channel.** Status questions went to the channel instead of
  the student, and the agent answered from the same evidence.

## Adapting it

- Another scheduler: keep `slack-notify` and the message design. Replace the
  `sacct`/`scontrol` calls.
- Project-specific crash signatures (a known flaky node, a vendor bug): add a
  branch to `report()` in a **local** copy, and keep the shared script generic.
- Sensitive logs: `SSW_QUOTE_ERRORS=0` posts the classification without quoting
  log lines.
