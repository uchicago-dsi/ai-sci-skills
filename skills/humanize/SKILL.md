---
name: humanize
description: Edit prose so it sounds like the author and reads plainly - stripping formulaic AI phrasing and replacing jargon with what it actually means. Use only when the user explicitly invokes /humanize.
argument-hint: "[file, selection, or 'all'] [for <audience>] [as talk|journal-imrad]"
disable-model-invocation: true
allowed-tools: ["Read", "Grep", "Glob", "Edit", "Write", "Agent"]
metadata:
  source: adapted from pedrohcgs/claude-code-my-workflow
  version: 2.1.0
---

# `/humanize`

Revise the requested prose in place so it sounds like the author and so a reader
gets it on the first pass. This is an editing command, not an AI-detection claim
and not a report the user has to process.

Two jobs, one pass:

1. **Remove the machine register.** Formulaic transitions, inflated framing,
   announcements that something is important, stacked hedging, generic praise.
2. **Make it plainer.** Replace a term with what it does. Say the thing instead
   of naming the method that did it. Default to the plainer wording and make
   each technical term earn its place.

Neither job may change what is true.

## Resolve the target and the audience

- Use the file, passage, or scope in `$ARGUMENTS`. For `all`, include prose
  relevant to the current deliverable and exclude rendered output,
  dependencies, vendored material, data, and code.
- Plain is relative to a reader, so establish who is reading: the audience named
  in `$ARGUMENTS`, or the one the document itself names, or ask in one line.
  A specialist audience raises the bar for *which* terms are shared; it does not
  license jargon, and it never licenses a sentence that only makes sense to
  someone who already knows the answer.
- Read applicable project instructions and any documented voice profile
  (`voice-profile.md`, `STYLE.md`, or the local equivalent) before editing.
- Use American spelling unless the target or the venue says otherwise:
  center, normalization, hematocrit, behavior, labeled, analyze. British
  forms creep in from quoted sources and from earlier drafts, so check rather
  than assume.

## Resolve the register

Register is how a sentence sounds: contractions, person and voice, how much
jargon the reader shares, whether naming a method is the job or a lapse. It
differs enough between a slide and a manuscript that one set of defaults
cannot serve both, and the difference is not a single axis — a machine
learning conference paper and a clinical physics manuscript disagree with each
other about as much as either disagrees with a talk.

Load exactly one register file from `registers/` and apply it on top of
everything below:

- `talk.md` — slides, PI and progress updates, lab meetings, notes, chat,
  briefs. **This is the default when no register is named.**
- `journal-imrad.md` — a manuscript for a peer-reviewed journal in the
  Introduction / Methods / Results / Discussion tradition.
- `ml-conference.md` — a machine learning conference submission with open or
  semi-open review: ICLR, NeurIPS, ICML, CVPR.

Take the register from `$ARGUMENTS` when it is named. Otherwise use `talk.md`,
and say which register you used in the summary so a wrong guess is visible.
Never infer a register silently from the file type.

Where a register file and this file disagree, the register file wins: it exists
precisely to carry the rules that are not universal.

## Make each technical term earn its place

The threshold here is the talk register's. A journal register raises it: at a
venue, using the field's exact term is a correctness requirement rather than a
lapse. The register file sets how aggressive to be; the rule itself does not
change.

Replace a term with what it does unless **both** of these hold:

- the audience uses that exact word for that exact thing, routinely; and
- the plain phrasing would be longer, vaguer, or less accurate.

When a term does earn its place, the sentence around it should still land for a
reader who does not know it. When it does not, name the action and consequence
instead - and if the word is still worth having, put it in parentheses after the
plain version, not before it.

The failure this rule exists to catch is a sentence that names a method where it
should have stated what was done and why that matters. "The renderer integrates
the analytic curve over each exact acquired interval with a convergence-tested
quadrature; internal nodes are never treated as frames" names three methods and
states no consequence. What it meant: between two measured frames the bolus can
rise and fall a long way, so we integrate the fitted curve across each real gap
instead of joining the measured points with straight lines, and the extra time
points that integration needs never become data.

Two more habits worth naming:

- An abstract noun usually hides the verb that matters. Prefer "we checked that
  more sample points do not change the answer" over "convergence verification".
- A name for a quantity is not a statement about it. "Scale-free ratio 0.38"
  says nothing; "the model explains about two thirds of the signal, where 1.0
  means predicting zero" does.

## Be concise the way that helps

Concise means no wasted words, not fewer ideas. Cutting words that carry meaning
does not make prose shorter to read - it makes the reader go back.

Never cut:

- a unit, a denominator, or an `n`;
- the qualifier that makes a claim true rather than merely strong;
- the one clause that tells the reader why a number matters.

The most easily lost of these is the word separating a thing from the
measurement of it: "measured", "apparent", "reported", "estimated". Dropping
it reads as tightening and is often a change of claim. "The measured
amplitude is dominated by sampling position" is a result; "amplitude is
determined by where you sample" says the physical quantity changes with the
observer, which is false and which a reviewer will catch. The same slip runs
the other way: do not write a sentence that denies a property of the object
when what differs is the instrument. Coil sensitivity varying along a vessel
does not make two levels different blood; it makes the same concentration
produce different signal. Ask which noun the verb is really about.

Do cut: the sentence that restates the previous sentence, the preamble before
the point, the summary of what the reader just read, and any phrase that would
survive being deleted without the reader noticing.

Cut what the reader already assumes. A clause that claims credit for competent
practice tells them nothing and costs their attention: "and we check both
rather than assume them", "using standard methods", "after careful review".
The reader took the checking for granted the moment you described the
condition. **Where this applies depends on the register**: a Methods section
owes the reader the check as part of the rebuild recipe, while the same clause
in a talk or a Discussion is self-congratulation. The register file says which
case you are in.

Cut a contrast whose other half is just the negation of the first. "Dangerous
rather than harmless" asserts nothing, because harmless is what dangerous
already rules out; so do "a finding rather than a non-finding" and "we measured
it rather than guessing". The pattern also hides inside "not just X, but Y"
where Y is a restatement of X.

The test is not about the words. It is whether the reader, **at this point in
the text**, holds the belief being denied. A contrast can only correct an
expectation the writing has already created.

"The distortion is an overestimate rather than an attenuation" looks like it
earns its place, because attenuation is what most people expect of an arterial
measurement error. It does not, unless the text has said so first. If nothing
before it has told the reader that partial volume can only reduce the measured
value, "overestimate" already carries the direction and the second half only
says it is not the other one. Give the sentence that setup and the contrast
becomes load-bearing; leave the setup out and it is filler. So the fix is a
choice: add the expectation, or delete the antithesis.

"A bias change, not a precision change" survives in a passage that has just
been discussing precision. "Real rather than fake" survives nowhere.

When a contrast fails the test, keep the claim and cut the other half. The
sentence says exactly as much.

Lean is the target, not terse. The goal is prose with nothing in it that fails
to earn its space — which is a different instruction from making it short. A
sentence can be long and lean, and a short one can still carry a clause doing
no work.

The test is whether a first-time reader stops or re-reads. If a cut makes them
stop, it was not a cut.

## Never open a sentence with a digit

A sentence begins with a word, in every register. `49 examinations were
excluded` is wrong; `Forty-nine examinations were excluded` and `We excluded 49
examinations` are both right. This holds for a slide, a Slack message, a
caption, a table cell and a journal paragraph alike, because the reason is
typographic rather than stylistic: a period followed by a digit is ambiguous
with a decimal point.

Three repairs, best first:

1. **Rephrase so the sentence opens on a word.** `Contrast was present by the
   second frame in 49 examinations.` Almost always available, and usually
   better than what it replaced.
2. **Lead with the noun.** `Examinations excluded for early contrast numbered
   49.` Stiff, but legal.
3. **Spell it out.** Only for a small number carrying no unit. `Forty-nine` is
   fine; `Nine hundred and eighteen` is not, and `Five point four seconds` is
   absurd.

Never repair it by deleting the number, and never by moving it into the
previous sentence, where its denominator no longer sits beside it. Cutting a
denominator to fix a typographic problem trades a real error for a cosmetic
one.

In a marked-up document a number inside a macro is still a digit to the
reader, so check the rendered text rather than the source.

## Editing priorities

- State the actual point instead of announcing that it is important. Cut the
  stage directions that tell a reader how to receive a sentence rather than
  saying anything: "hold on to this", "note that", "it's worth emphasizing
  that", "keep this in mind", "remember that", "the key insight is". If the
  point needs weight, give it its own sentence or its own slide; an instruction
  to pay attention is not weight.
- Replace vague abstractions with the concrete subject, action, or consequence
  the text already supports.
- Prefer the shorter, more common word where it is exactly as accurate.
- Follow the register on contractions, person and voice. These are the rules
  that differ most between a slide and a manuscript, and guessing wrong is the
  most visible way to sound wrong.
- Vary sentence shape only where the rhythm has gone mechanical.
- Preserve uncertainty that belongs to the science; remove only stacked or empty
  hedging.
- Preserve the author's deliberate habits when documented or evident.

Do not change facts, numerical values, citations, paths, identifiers, code,
commands, config keys, schema names, or markup semantics. An identifier is a
literal: rewriting one to read better breaks the thing it points at. Do not edit
verbatim quotations or literal prompts unless the user includes them explicitly.

## Work under the hood

1. Delegate a bounded read-only pass when delegation is available. Give the
   worker the cross-agent rubric in `agents/humanize-auditor.md`,
   the exact target, the audience, **the register you resolved**, and any
   voice guidance; in Claude Code that
   rubric is the `humanize-auditor` subagent. Ask for high-confidence, actionable
   findings in both registers: machine phrasing and unearned jargon. Apply the
   rubric directly when delegation is unavailable.
2. Review the findings yourself. Ignore anything that flattens the author's
   voice, changes meaning, or swaps one generic phrase for another.
3. Edit the target directly.
4. Inspect the diff for meaning drift, dropped denominators, new repetition,
   broken markup, and changed literals.

## Finish

No audit report unless asked. Return the revised material or name the files
changed, name the register you applied, then a brief summary of the most
consequential edits. Say which
passages you left alone because changing them would alter meaning, and name any
term you kept along with why the audience needs it.

Adapted from Pedro H. C. Sant'Anna's `humanize` skill in
`pedrohcgs/claude-code-my-workflow` at commit
`9d371f0bf8a8bc99569feca3210ef5133af28d33`; see `THIRD_PARTY_NOTICES.md` in
this repository.
