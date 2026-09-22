# Register: journal-imrad

A manuscript for a peer-reviewed journal in the Introduction / Methods /
Results / Discussion tradition — MRM, JMRI, Radiology, Magnetic Resonance
Imaging and their neighbours.

Three readers, not one: a reviewer looking for what is wrong, a copy editor
applying a house style, and a scientist two years from now trying to rebuild
the work. The talk register optimizes for the first pass; this one optimizes
for the second and third.

## Voice

- **No contractions.** This is the sharpest difference from the talk register.
  "Cannot", not "can't". In a submitted manuscript a contraction reads as an
  unedited draft, and some house styles remove them anyway.
- **Person and voice follow the venue, not a default.** Many journals in this
  tradition require a passive abstract and discourage the first person; others
  do not care. Check the venue before imposing either. Where the venue is
  silent, prefer the active voice in Introduction and Discussion and accept the
  passive in Methods, where the agent is rarely the interesting part.
- **Name the agent when who did it is the claim.** An agentless construction
  that hides the authors reads as though someone else did the work: "an
  independent implementation reproduces the published width" sounds like a
  third party's result, when the point was that *we* checked it instead of
  assuming it. Wherever a sentence establishes that the authors verified
  something, say so.
- Sentences may be longer than in a talk, but no sentence should require a
  second pass to parse. Length is allowed; nesting is not.

## Jargon threshold

Moderate, and asymmetric by section. The shared vocabulary of a venue's
readership is large, and using the field's exact term is a correctness
requirement rather than a lapse: $K^{\mathrm{trans}}$, spoiled gradient echo,
intraclass correlation, repeatability coefficient all stay, unglossed.

The rule that still applies, everywhere: a sentence must not depend on the
reader already knowing the answer. Define a term once, at first use, when it is
specific to this work rather than to the field.

What to strike is invented vocabulary — a name this manuscript coined for its
own convenience and then used as though the field shared it.

## Naming methods

**Required in Methods, discouraged in Discussion.** This is the section
asymmetry that a single-register editor gets wrong.

- *Methods* must name the method precisely enough to rebuild from. Naming the
  quadrature rule, the trainer configuration, the erosion distance is the job.
  Do not rewrite a Methods sentence into a statement of consequence.
- *Results* states what was measured, in the units it was measured in.
- *Discussion* interprets. Here, and only here, prefer the consequence over the
  method name.

## Routine checks

**Keep them in Methods.** The opposite of the talk register. A reviewer needs
to see that the check happened, and "the inputs were validated against X" is
part of the rebuild recipe rather than a claim of diligence. Cut the same
clause from the Discussion, where it is self-congratulation.

## Numbers

Units, denominator and `n` are not negotiable, and in a manuscript they belong
in the table row rather than in prose or in a column label. State what set each
side of a ratio was computed over. Compare paired observations by their paired
difference, never by the difference of two marginal summaries.

## What not to touch

On top of the core rule against changing literals: leave citation commands,
cross-references, float placement, equation numbering and any journal class
macro exactly as they are. Rewriting `\cite{}`, `\ref{}` or a class-specific
command to read better breaks the document.

## Venue facts

Per-venue specifics live in `paper-structure/venues/<venue>.md`, installed at
`~/.claude/skills/paper-structure/venues/` and `~/.codex/skills/...`. Read the
venue's file and apply its **Abstract** and **References** sections, which are
the two that change how prose is written rather than how it is organized.

Two examples of why this cannot be a default: Magnetic Resonance in Medicine
requires a passive abstract with no first person, and names the section
`Methods` rather than `Materials and Methods`, while other journals in the
same tradition require neither.

If the venue has no file yet, write one from `venues/_template.md` before
editing. Guessing a house style is how a manuscript acquires a voice its
copy editor will strip.
