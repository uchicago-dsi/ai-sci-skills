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

Printing the index without reading it is a performative check, not a real one.
Read the output and stop on an unexpected path, or use an explicit pathspec so the
index cannot decide what you commit.
