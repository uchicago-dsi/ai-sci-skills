# Register: design-doc

A document that says how a system is supposed to work: what it stores, where,
in what shape, who owns each part, and what rules every consumer must obey.
Everything in `talk.md` applies except where this file says otherwise.

The reader is the person who decides how the system should work, usually the
PI. They read it to find the places where the system and their intent
disagree. A sentence they cannot follow is a disagreement they cannot see, so
readability is the first requirement and completeness the second. Someone who
already built the system is not the audience; they need the code.

## Shape

- **Lead each section with its rule in one plain sentence.** "Each exam is one
  physical scan session." Then why, in a sentence or two. Then the details a
  consumer needs. A reader skimming only the first sentence of every section
  should come away with the whole design.
- **One idea per paragraph.** If a paragraph covers a rule and two exceptions,
  give the exceptions their own short list.
- **Tables for anything that maps one thing to another**: what is stored
  where, which owner owns what, which status means what. Prose for reasons.
- **Mark what is decided, what is built, and what is open.** A decision says
  who made it and when: "(Anna, 2026-10-28)". Something planned but not built
  says "Planned". A choice nobody has approved says "Open:" at the start of its
  line, so the reader can find every one of them.
- **Short.** A section the reader has to scroll through is too long. Move
  procedures, command lines and history to the runbook, the notebook or the
  code, and leave a pointer.

## Jargon threshold

Aggressive, as in `talk.md`, with one difference: identifiers are allowed
because the reader will search for them. Write the plain description first and
the identifier after it, in backticks: "the split unit (`split_unit_key`), the
set of patient groups that must share one split role." Never let an
identifier stand alone as the subject of a sentence the first time it appears.

The system's private vocabulary — function names, stage names, schema
versions, internal status strings — appears only where a consumer must type it
or look it up, and then only after its plain meaning.

## What to leave out

- **How the code enforces a rule.** Say the rule and what happens when it is
  broken ("the registry refuses to publish"). Leave the function and the
  validation steps to the code.
- **History.** A design doc describes the system as it is meant to be. An
  incident earns one clause when it is the reason for a rule ("because one
  series ID was seen in two different studies"); the rest belongs in the
  notebook.
- **Counts that change every generation.** One example count is fine when it
  shows scale; current numbers live in the generation's provenance or the
  notebook.
- **Defensive clauses** that deny something nobody proposed. "Pending is not
  rejected" earns its place only if a reader would otherwise assume rejection.

## What never to leave out

- Every rule a consumer has to obey, and what happens when it is broken.
- Where each kind of record lives and what one row means.
- Who owns each part.
- Every open choice, marked "Open:".

A rule the design doc omits is a rule the reader cannot check, which defeats
the document.
