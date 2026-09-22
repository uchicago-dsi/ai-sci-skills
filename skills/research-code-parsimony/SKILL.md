---
name: research-code-parsimony
description: "Keep scoped implementation and review work from growing unnecessary code by identifying the real owner, real callers, and existing capability before adding surface. Use when writing, extending, or reviewing research code; for a dedicated cleanup pass over pre-existing debt, use a maintenance skill instead."
---

# Research Code Parsimony

## Establish The Contract And The Owner First

Before adding code, be able to state:

- the behavior or scientific contract being requested, including what must stay reproducible;
- the module, function, script, or config that already owns this behavior, and which callers actually exercise it;
- whether a maintained dependency or a native language/library capability already provides it.

Search before creating an owner. If none fits a genuinely new capability, create one clear owner rather than forcing unrelated behavior into an existing module.

## Reuse Before You Add

- Extend an understood existing owner instead of introducing a parallel one.
- Prefer a maintained dependency when it reduces ownership burden while meeting the scientific and operational contract. Check the standard library and present dependencies first.
- Parsimony means less code to own — not fewest files, shortest diff, or clever one-liners. Readable, explicit code beats a compressed version.
- Never satisfy the request by solving a smaller or easier scientific problem than the one asked for.

## Express Cohesive Families As Directories

Prefer a meaningful package hierarchy over a flat directory of long,
repeated-prefix filenames. When several modules belong to one scientific or
contract family, let the directory carry that context and give the modules
short role names: for example,
`training/concentration_field/diffusion/runtime.py` rather than
`training/concentration_field_diffusion_runtime.py`. A separate
`training/physics_field/direct_inverse/` can own its own data, objective, and QC
modules; genuinely shared training infrastructure stays at the shared level.
Group by cohesive ownership, not chronology, and add depth only when it makes
navigation and responsibilities clearer. Do not create speculative package
trees or duplicate a family merely to achieve symmetry.

Apply this preference when choosing a new owner's home. Existing flat families
can move in a bounded, authorized pass coordinated with their current owners;
this preference does not authorize reorganizing active work during another
task. Leave queued/running execution checkouts and immutable run artifacts
untouched. Move live imports, entrypoints, config references, and hashed
execution declarations together, updating valid source pins according to local
policy. Validate the affected execution paths and remove old module routes
without compatibility aliases. Completed runs retain their producing layout
through their pinned commits, not duplicate source at HEAD.

## Cut Over Instead Of Layering

When a change genuinely supersedes an existing implementation, retire it in the same scoped change:

- check executable readers — imports, configs, launchers, actively used notebooks, CI, current instructions; historical provenance mentions alone are not live callers;
- reroute live callers to the current owner;
- remove the superseded executable route along with helpers, flags, and declarations only it used;
- leave one clear current interface: no alias, shim, or duplicate path unless a transition was explicitly requested;
- retain scientific evidence — results, provenance, run records, completed-run configs — per local policy, even when the code that produced them goes away.

Retire only what your change supersedes. Note other sprawl you noticed rather than turning the task into a repository-wide cleanup.

## Review For Sprawl

When implementing or reviewing, flag:

- a second owner for behavior that already had one;
- near-copy versions of a function, script, or config differing only in constants;
- wrappers, indirection, or config knobs with a single caller and no stated reason;
- compatibility layers preserving a path nothing reads.

Different scientific conditions can warrant separate configs; judge duplicated behavior, not visual similarity. Keep justified model/config flexibility and diagnostics that make results interpretable. A review-only request authorizes findings, not applying changes.

## Preserve Local Rules

Explicit user requirements and project-local safety, provenance, retention, validation, execution, and scope rules outrank any impulse to simplify. Read local instructions rather than inventing universal experiment, retention, or testing policies.

## Validate And Report Proportionally

Match the check to the claim: imports and compilation check mechanics, not numerical equivalence or scientific validity. Exercise the affected contract when results could change, using the cheapest appropriate check local policy allows. Add tests or documentation only when justified and permitted, not as a ritual.

Report what you added, what you reused, what you retired and on what evidence, and which check you ran, proportional to the change.

Inspired by [Ponytail](https://github.com/DietrichGebert/ponytail)'s reuse-first approach to avoiding unnecessary code.


## Fail Fast, And Keep One Current Interface

- No silent fallbacks, no hidden defaults outside the config package, no
  compatibility shims, deprecated aliases, fallback CLI names, or duplicate
  control paths unless the user explicitly asks for a transition period. Keep one
  current interface and update the callers.
- Reproducibility comes from version control and pinned commits, never from
  backward-compatible code. A run reproduces because its commit, config, and input
  digests are recorded, so it runs against its own pinned commit where every field,
  key, schema, and signature still agree. Nothing in the current tree needs to keep
  working for older inputs, and a completed run needing its producing commit to
  replay is an acceptable cost, not an objection.
- So parsimony beats backward compatibility. Delete anything whose only remaining
  purpose is keeping an older input, artifact, or caller working, and delete it
  together with whatever declares it so the two cannot disagree. When a problem
  surfaces, clean aggressively rather than working around it: remove circular
  imports, generation chains, shims, and duplicated near-copies outright, and accept
  some short-term instability. A bug is cheaper to find and fix than a large body of
  tangled code is to carry.
- The one thing that earns its place is a field or branch a live owner actually
  reads. Establish that with a search rather than assuming, and say which readers
  you found.

## Delete What Your Own Change Supersedes

Deleting what your change supersedes is part of that change, not maintenance. When
a step replaces a mechanism, estimator, renderer, config, or owner, remove the
superseded implementation, its configs, and the helpers it alone used **in the same
commit**, reroute every live caller, and confirm no live reference survives.

History and the completed run's recorded commit preserve the exact producing
source, so a superseded path need not stay executable — and a still-runnable
invalid path is worse than an absent one, because a later reader cannot tell which
is current. This does not require a maintenance session and the maintenance-lane
rules do not restrict it.

## Prefer One Owner To Several Copies

- Before adding helpers, loaders, writers, metrics, plots, path builders, cache
  policies, CLIs, or training support, search for and extend the canonical owner,
  replace matching duplicates when safe, and keep model-specific code thin unless
  its contract genuinely differs.
- **Before changing a contract, find every place that enforces it.** A guard,
  horizon, schema, or output shape expressed in two places will disagree the moment
  one is edited, and the copy you did not change fails at the next run rather than
  at the edit. Prefer extracting one owner over updating several, and confirm no
  private copy survives. Search for the *decision*, not the symbol: a copy that
  reimplements the contract in another language shares no identifier with the
  original, so grepping the constant's name finds the Python enforcers and misses
  the `find` in a shell wrapper encoding the same rule. Expect the stale copy to be
  the one whose output nobody validates, because nothing fails when a README lies.
- Before adding a pipeline-stage owner likely to exceed ~300 lines, name the nearest
  existing owner and quantify their contract overlap. Extract substantial shared
  loading, feature, provenance, or reduction logic into one package owner before
  committing.
- Before importing or reusing a private helper from another script, inspect its
  exact signature and one current caller, then exercise its transitive
  serialized-input field contract on one real current row. A matching name is not an
  interface contract.

## Test A Serialization Boundary By Round Trip

At a CSV or JSON serialization boundary, normalize and validate typed fields
explicitly. Serialization is lossy about type in ways that stay invisible until a
consumer reads the file: an integer comes back as text, a missing identifier
deserializes as a float `NaN` and then enters numeric aggregation, a boolean becomes
the string `"False"` which is truthy.

An in-memory type match is not a serialization contract. Before any fan-out, exercise
the real path end to end on one real case — producer write, serialized read, and
whatever the reducer or finalizer validates — and require clean logs. Checking the
object you are about to write tests the wrong half; the defect lives in the round trip.

## Name By Role, Not By Chronology

- Name scripts, modules, entrypoints, and config files by their scientific or
  contract role. Do not use trailing implementation tags such as `_v1`, `_v2`, or
  `_v3` in live code filenames; history tracks source versions, and a successor
  must either keep the one canonical filename or take a human-meaningful name for a
  genuinely different mechanism. Update all callers and delete the superseded
  implementation rather than keeping both names. Explicit versions remain
  appropriate inside immutable serialized schema identifiers, artifact/run slugs,
  and provenance records where they distinguish incompatible stored contracts — but
  not in executable owner filenames.
- Use compact, descriptive, human-readable `snake_case` semantic slugs naming the
  artifact, the dataset or mechanism, and the main differing knob. Apply this to
  run and output directories and to run-name fields; keep details in config, queue
  items, or provenance. Avoid opaque-only IDs, double underscores, repeated parent
  context, and external-tool style unless required.
- Keep dates and timestamps in the README, notebook, provenance, or title text, not
  in repository-owned paths or slugs unless a tool requires them. Resolve collisions
  by updating, archiving, superseding, or adding a meaningful suffix that says what
  differs.
- Do not create parallel directories, duplicate notes or runbooks, repeated path
  segments, or convenience naming schemes. If the organization is wrong, do a
  bounded reorg: choose one owner, remove or reroute safe duplicates, update
  references, and record the ownership rule.
- Framework-imposed paths are exceptions, not style examples. Do not rename them in
  place, but report them through concise aliases where possible.
- Keep canonical paths copy-pasteable on one line without ellipses; define a concise
  variable such as `RUN=...` for nested artifacts.

## Retire Code Safely

- Before deleting a script or shared module, search its importers, wrappers,
  configs, and active docs; remove or reroute dependents in the same change, then
  import-check the surviving entrypoints.
- **Liveness is not a property of the tracked tree.** `git grep` omits untracked
  files unless told otherwise, so a module whose only callers are uncommitted work
  in progress scans as unreferenced. Three separate retirements in one session
  deleted live modules for exactly this reason, and the affected work had no run
  evidence either, because its run had not happened yet.
- A module named only in a hashed execution-surface declaration such as
  `EXECUTION_FILES` has zero importers and is still load-bearing: deleting it raises
  at run start, which no import check can see. Validate a retirement by running the
  execution-path check, not only by importing what survived.

## Do Not Edit A File A Process Is Executing

A shell reads its script incrementally and a long-running interpreter may reread or
lazily import, so shifting byte offsets under a live process can make it resume
mid-statement on text that was never a command. Check for a running instance first.
When one exists, either wait, or write the replacement to a new path and `mv` it
over the target so the running process keeps its original inode. An in-place edit
mutates that inode and is the operation to avoid.

## Scope A Guardrail To A Bounded Window

Scope a log or stream guardrail to a bounded window with an explicit boundary rather
than forbidding a marker anywhere in the artifact. Orderly teardown routinely emits
error text that healthy execution produced, so a rule that greps the whole artifact
rejects working runs.

Validate a rejection rule against a real passing artifact as well as against every
failure shape it must still catch. A guardrail proven only against the failure it was
written for is half tested; the question that matters is what makes it fire wrongly.

Never place a guardrail that can reject an already completed run immediately before an
irreversible reduction, and keep it outside any hash-bound owner set. Repairing a false
positive inside that set re-binds provenance, and the affected run can then no longer be
reduced under its own producing commit — so the fix for a spurious rejection destroys the
result it was trying to protect.

## Keep Formatter Churn Out Of Scoped Changes

Before applying a formatter to a legacy shared owner, check whether it would rewrite
unrelated lines. Format new files or edited regions without reformatting the rest of
the owner.

## Broaden A Helper On The Real Path

Before pushing a config-backed entrypoint, or extending a helper from a narrow case
set to a broader cohort, run the real structured config/prepare path at the broadest
intended scope and enumerate the helper's semantic preconditions. Compile, import,
or narrow-case checks are not sufficient.
