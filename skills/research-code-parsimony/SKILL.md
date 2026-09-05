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
