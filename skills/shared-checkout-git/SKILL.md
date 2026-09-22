---
name: shared-checkout-git
description: "Stage and commit safely when several agents or people share one working tree, so no one absorbs another owner's in-flight work. Use before any git add or git commit in a checkout that other agents are editing concurrently."
---

# Git In A Shared Checkout

The index is shared state. Two agents editing disjoint files are fine; two agents
touching the index are not.

## Give Each Bounded Change One Staging Owner

- Assign one explicit staging/commit owner per bounded change. Other agents may
  inspect or edit disjoint files, but they must not stage or commit while that
  owner is active.
- Immediately before staging, and again before committing, the owner must inspect
  the index and working tree, stage only the named paths, and stop if an unexpected
  staged path or an overlapping edit appears.
- Never use a shared `git add -A`, amend another agent's commit, or reset the shared
  index to repair a collision.
- A validation run across a populated index is a collision window, and the other
  owner's next commit will absorb whatever is sitting there.

## Stage And Commit As One Action

`git add` followed by a separate `git commit` is two actions, and another owner's
commit can land between them however fast you are. That absorbed two agents' work
in one day, one of them a 417-line file that ended up inside an unrelated commit.

So either run validation *before* staging, or hold the change unstaged until the
commit is issued:

```bash
git commit -- path/one path/two   # index cannot decide what you commit
```

## Enumerate Files, Never A Directory

A path-scoped commit takes the working-tree state of everything matching the
pathspec, so a directory in that pathspec silently widens the commit to every
modified file beneath it, including another owner's. `git commit -- scripts/`
intended to carry 21 files and carried 27: the extra six were a concurrent
owner's in-flight edits, which went from unstaged work in their tree to pinned
in someone else's commit. Their `git status` then reads clean, which is
misleading rather than reassuring, and the commit is not a valid execution pin
for either owner's change.

So enumerate the files. If the list is long enough to be tempting to collapse,
that is a sign the change should be several commits.

## Check The Resolved File List, Not The Index

Printing the index without reading it is a performative check, not a real one.
Read the output and stop on an unexpected path.

Reading the index is also the wrong object when the commit is path-scoped,
because such a commit bypasses the index entirely. An index verified to hold
exactly the intended paths gives real confidence about a staged commit and none
at all about `git commit -- <paths>`; that mismatch is how the six files above
got through a check that passed. Verify what the commit will actually take:

```bash
git commit --dry-run -- path/one path/two    # the resolved list, before it lands
```

Then compare that list against your own change set — ideally its source, such as
the isolated worktree or branch the work was developed in — rather than against
your memory of it. In a shared checkout the difference between the two is exactly
the other owner's work.
