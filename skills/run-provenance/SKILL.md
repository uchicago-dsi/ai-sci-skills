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

   Write this tier's files into the expiring scratch directory that
   `dir=$(agent-scratch <slug>)` creates, `$AGENT_SCRATCH_BASE/<project>/agent_scratch/<slug>`,
   where a nightly sweep deletes any entry untouched for 14 days. Do not put it in
   the repository or beside durable outputs, where it outlives its purpose and a
   later reader cannot tell it from evidence. Anything that turns out to be
   needed downstream moves to a real run directory, with its README, before it
   expires. If `agent-scratch` reports that no base is set on this cluster, ask
   rather than choosing a directory.
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

## Version Every Record That Binds A Changed Schema

When an artifact's schema changes, every record that binds that artifact changes
version with it: the pointer, the parent binding, the handoff, any `*_parent` or
`*_publication` record whose admission reads the changed fields. A reader decides
between "current: admit and reuse" and "superseded: keep as evidence, reuse
nothing" from the binding's own version, not by opening the payload. If the
binding keeps its old version while the payload moves, an old artifact claims to
be current and fails the new check deep inside a consumer, long after the change,
in a command that never touched that code.

In one case, three constants versioned one inventory: roster, reducer, and the
parent binding. A commit bumped the first two and missed the third. Four days
later, an unrelated admission run failed at startup on a stored pointer to an
inventory from before the bump.

When bumping a schema:

- `rg` every constant and literal carrying the old version string, and every
  function that constructs or admits a record of that family. Bump them together
  in one commit.
- Register the previous binding version with whatever authenticates superseded
  records. Every stored pointer to the old artifact then resolves as retained
  evidence instead of raising.
- Separate producers from readers. A producer or resumer admits only the
  current version, so it never adopts old records into a new artifact. A
  read-only consumer that must see frozen artifacts (a duplicate screen, a
  comparison, a replay) admits every earlier version whose layout it can read. In
  a second case, a bump that only changed how inputs were discovered left every
  registered exam unreadable to the screen that compares new arrivals against
  them.
- Before calling the bump done, open one real stored record of the old version
  through the live reader and confirm it lands in the superseded branch, or is
  read, as intended.

## Keep Each Experiment In One Output Directory

Choose one canonical output directory per experiment before launch. Keep its
config, provenance, logs, checkpoints, metrics, training/validation curves and QC
there, using subdirectories as needed. Asynchronous validation, QC workers,
retries and later galleries write into the owning experiment's directory; a
separate scheduler or coordinator does not create a separate scientific output
root. Reference shared source data, reusable caches and parent experiments rather
than copying them into every run.

Bind this directory explicitly in the launcher and all worker requests. Keep
curves and QC at stable, discoverable paths under it, and list those paths in the
run README. Check the actual artifacts before reporting them available; an empty
directory or pending request is not completed QC. Every experiment update must
include a clickable absolute link to this directory so Anna can inspect it
independently. Preserve frozen historical artifacts; apply layout changes to new
work without rewriting a live run's recorded paths.

Make the experiment root the entry point for finding its artifacts. Keep the
root README concise, with a small map to the config, reproduction records,
results, curves, checkpoints and QC, and label pending outputs explicitly. Use
Markdown when prose is useful; JSON/CSV, figures and galleries can remain in
their natural formats. Do not create a separate Markdown report for every worker
or artifact merely to satisfy discoverability.

Keep one canonical plot per scientific question, refreshed in place. Do not
duplicate the same learning curve across trainer and evaluator directories;
`training-run-hygiene` defines the combined training-and-validation figure.

In saved Markdown, use links relative to that Markdown file's directory, including
for outputs outside the repository. Verify local targets resolve from that
location. Leading-slash filesystem paths do not reliably open in VS Code Markdown
preview; reserve absolute clickable file links for chat. When the target is on
another host or unavailable locally, give its host and copyable path rather than
implying a working local link. Generated READMEs must follow this convention in
their producer, not through hand edits to generated files.

## Write A README That Says How To Remake The Output

For every new experiment, including exploratory scheduled smokes, automatically
write a reproduction bundle into its canonical output directory before execution:

- `README.md`: the hypothesis and changed settings; input/parent and split
  identities; exact environment setup, checkout, launch, resume and evaluation
  commands; resource requirements; and paths to checkpoints, metrics, curves and
  QC. Give enough information to reproduce the experiment without chat or shell
  history, including seeds, preprocessing and fixed readout settings through the
  saved configuration.
- A copy of the complete effective configuration actually used, plus its digest;
  a hash or a link to a mutable source configuration alone is insufficient.
- Git records from the execution checkout: full commit SHA, branch or detached
  state, `git status --short --branch --untracked-files=all`, submodule revisions
  when relevant, and staged/unstaged diffs. For permitted dirty exploratory runs,
  also snapshot every untracked file that execution depends on. An empty diff
  and clean status are meaningful records, not reasons to omit these files.
- The resolved environment path, Python and dependency versions (or immutable
  container digest), input manifest digests, exact command and scheduler receipts.

Capture these automatically at submission, verify their bindings at execution,
and preserve the original records on resume; append attempt-specific records
rather than replacing the original provenance. Keep credentials and PHI out of
the bundle. This requirement applies going forward; do not retrofit historical
experiments. Developer checks above remain exempt.

Every new experiment root needs a launcher-written `README.md` before it is
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

A generated README is rewritten every time its generator runs, so anything written
into it by hand is lost on the next re-render, silently and with exit 0. Either the
generator writes the results itself, from the run's own summary files, or hand-added
interpretation goes in a separate file (`NOTES.md`) that no producer ever writes.
Never append to a generated README by hand. A figure re-render that rewrote a
README erased its results section, and nobody noticed until the numbers were needed.

Scale the README's detail to what the artifact is for, while retaining the
reproduction bundle for every experiment. Developer checks remain exempt. A
reusable cache, export or decision-grade artifact needs enough schema and input
detail for its next consumer to rebuild and interpret it; a disposable mechanics
check needs only its command, commit and what it measured.

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
