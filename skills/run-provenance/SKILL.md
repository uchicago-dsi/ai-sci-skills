---
name: run-provenance
description: "Decide how much provenance a computational run owes, record it before the first expensive step, and write a README that says how to remake the output. Use when launching a run, publishing an artifact another run will consume, freezing a checkout for a queued job, or deciding whether a branch, worktree, or recovery copy can be deleted."
---

# Run Provenance

Provenance exists so a later reader can tell what produced an artifact and remake
it. Everything below scales with what the artifact is for: a probe nobody will
reuse owes very little, and a parent that other runs consume owes all of it.

## Choose The Tier Before You Launch

Use three tiers so iteration stays fast without weakening durable evidence.

1. **Developer checks.** Compile/import checks, config validation, dry runs, and
   disposable local mechanics probes may use uncommitted code and need no
   provenance artifact. A read-only diagnostic that consumes immutable inputs and
   writes nothing anything else will consume is this tier by default; it needs no
   deliberation about which tier applies.
2. **Exploratory scheduled smokes.** Uncommitted code is allowed when the run root
   automatically records the full base commit SHA, exact command, config hash,
   environment identity, immutable data/parent hashes, working-tree status, and an
   exact binary patch or source snapshot covering every dirty or untracked
   execution path. Report these results only as preliminary, with that provenance.
   They may not become reusable parents or decision-grade evidence.
3. **Decision-grade, expensive, or reusable runs.** Long training, final
   comparisons, promotion/retirement evidence, and artifacts consumed as parents
   must execute from a clean checkout pinned to a full 40-character commit SHA,
   with every invoked code and config path tracked and committed. A dirty shared
   checkout should use a clean commit-pinned worktree rather than blocking
   unrelated development.

For tier 3, generate the run README and machine-readable provenance **before the
first scientific kernel or optimizer update**. Record the full commit SHA, exact
command and config hash, environment identity, immutable data/parent manifest
hashes, and clean execution status; the commit already determines the tree and
transitive source contents. Fail closed when a field is absent or the execution
checkout differs from the commit. Resume with the same commit and bound hashes; a
code change requires a new commit and a new semantic run slug or explicitly
versioned attempt. Generate this automatically rather than spending agent effort
on long narrative prose.

Before re-preparing a provenance-hashed run after an owner change, inspect its
existing-artifact policy and either archive the prior immutable result or choose a
new semantic run slug before resubmission.

## Write A README That Says How To Remake The Output

Every new output/run directory needs a launcher-written `README.md` before it is
reported ready, recording the differentiator, launcher, config snapshot, queue/job
IDs, run/fold paths, environment, commit, dirty-state summary, and important
results. Capture provenance on the submitting host and pass it into jobs whose
images lack `git`; a dependency-pending job from a mutable checkout must receive
the intended commit and dirty state at submission or load an immutable snapshot,
never claim a later `HEAD`.

That README must also say how to remake the output, not only what produced it.
Recording a commit and a config hash establishes provenance; it does not tell the
next reader what to run. Include:

- the exact command with every input path;
- the shard or fan-out count, and whether rerunning is idempotent;
- what each emitted array or column holds, with its indexing;
- the producing commit, whether the tree was dirty, and a **checkout of that
  commit as the first rebuild step** — a command without the version it belongs to
  stops reproducing the artifact the moment the producer changes, and the commit is
  the only way back;
- a digest of every input table, because inputs can move underneath a fixed commit
  and a digest mismatch is what tells the next reader which of the two changed.

Generate it from the arguments the run actually received rather than writing it by
hand, so it cannot drift from what it describes, and write it from the first unit
of work rather than only from a reducer, so an interrupted run is still documented.
A cache or export nobody can rebuild is one nobody can trust.

Scale this to what the artifact is for. The full form is owed by anything that
could become a parent, a reusable cache, an export, or decision-grade evidence. A
disposable probe whose whole output is a log, and which one printed command
regenerates, owes the command, the commit, and what it measured, and nothing else:
input digests exist so a later reader can tell whether an input moved, and there is
no later reader for an artifact nobody will consume. When in doubt, write the full
form — a probe is sometimes promoted, and the long form costs minutes.

## Freeze A Checkout By Execution Pin, Not For Its Lifetime

A worktree may advance through many commits while no queued or running job is bound
to it. At submission, record the exact worktree and full commit together, and do
not move, update, or modify that checkout until every job bound to that pin has
finished or been withdrawn; the queued job's pin must still match when the
scheduler starts it. Multiple jobs may share one frozen worktree only when they
bind the same commit. Give simultaneously active different commits separate
worktrees. Once the last bound job is terminal, the clean worktree may be advanced,
reused for the same bounded experiment, or removed.

The pin binds the recorded identity, not only the executed source. Each array task
stamps the commit it sees when it starts, so any commit to that checkout mid-array
splits one run's provenance across two SHAs, and a consumer that requires a single
commit will refuse the result. A documentation-only commit is enough to do it.
Repair that by re-running from a pinned checkout, not by relaxing the consumer's
check.

## Do Not Let Branches And Worktrees Accumulate

- Treat development branches and worktrees as temporary integration state, not
  indefinite forks. As soon as a result is available and no queued or running job
  requires the checkout frozen, either integrate the bounded validated
  implementation promptly or explicitly record that the branch is not intended for
  merge, with the reason and any authoritative result artifact. A not-for-merge
  label is a disposition, not a reason to keep the checkout forever.
- At each clean development boundary, refresh active merge-bound work against the
  current upstream default branch. Never rewrite a commit pinned by a queued or
  running job.
- Retain unmerged code, branches, worktrees, or recovery copies only for a current
  merge plan, a concrete named future use, necessary scientific or provenance
  evidence, or unresolved ownership. Name the reason and the owner in existing task
  state; speculative usefulness and absence from version control are not retention
  reasons. During authorized cleanup, after checking live consumers and execution
  pins, delete obsolete work rather than manufacturing a backup branch, recovery
  commit, or archive. Reassess retained work when its stated use ends.
- Do not rewrite or forcibly purge history merely to remove obsolete working copies
  or references.
