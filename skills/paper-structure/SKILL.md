---
name: paper-structure
description: "Organize a scientific manuscript for a specific venue: fix the claim it argues, load the venue's own section skeleton and limits, budget words before drafting, and keep each section doing only its own job. Use when planning, drafting, restructuring, or auditing a paper, abstract, or rebuttal, or when deciding what belongs in which section or what to cut to fit a limit."
---

# Paper structure

Organization, not sentences. This skill decides what goes where and how much
room it gets. For how a sentence sounds, use `humanize` with the register the
venue file names. For whether a number is trustworthy, use `sensemaking`. For
whether a claim outruns its evidence, use `skeptical-labmate`.

Structure is not universal. A clinical physics manuscript puts Methods before
Results and weaves prior work through the Introduction and Discussion; a
machine learning conference paper gives Related Work its own section and wants
a reproducibility statement; some high-profile journals put Methods last. So
the skeleton comes from the venue, never from habit.

## Start by loading the venue

Read `venues/<venue>.md` before anything else. If the venue has no file, write
one from `venues/_template.md` first — it takes fifteen minutes and every
later decision depends on it. If the venue is genuinely undecided, pick the
most likely one, say so, and expect to restructure.

Check the `verified` date in the file. Limits and required sections change
between cycles. If it is more than a year old, confirm the numbers against the
venue's own page before trusting them for a submission.

## Fix the spine before writing anything

Write one sentence that is the paper's claim. Not the topic, not the area: the
thing a reader should believe afterwards that they did not believe before.

Every section then earns its place against that sentence. A section that does
not advance it, support it, or bound it is cut or demoted to supplementary
material, however much work it represents.

Two failure modes this catches early:

- **Two spines.** If the sentence needs an "and", you may have two papers. Not
  always — a method and its validation are one spine — but check, because a
  two-spine paper reads as unfocused at every venue and reviewers say so.
- **A spine that is a description.** "We built a pipeline for X" is a topic. "X
  is determined by Y, not by Z" is a claim. The second can be wrong, which is
  what makes it worth reading.

## Budget words before drafting

Take the limit from the venue file, along with its definition of what counts —
venues differ on whether appendices, captions, and statements are included.
Allocate to sections before writing, and count as you go using the venue's own
definition rather than a whole-file word count.

A budget is what makes cutting a decision rather than a panic. When a section
runs over, the question is which of its paragraphs is doing the least for the
spine, not which sentence can be squeezed.

Leave 5 to 10 percent unspent. Revision adds words more often than it removes
them, and reviewer responses need somewhere to go.

## Give each section one job

The names come from the venue file. The jobs below hold across venues even
when the names differ.

**Introduction.** Why the question matters, what is known, what is missing,
and what this paper does about it. The last paragraph is the load-bearing one:
it states the gap and the claim, and at most venues it states the hypothesis.
Prior work belongs here in narrative form — woven around the argument, not
listed. Where the venue has a separate Related Work section, that section
compares and positions; the Introduction still has to carry the gap.

**Methods.** A rebuild recipe. Enough for a competent reader to reproduce the
work without asking you a question. This is the one section where naming the
method precisely is the job rather than a lapse, and where stating a routine
check is required rather than self-congratulation.

**Where the cohort goes** depends on the venue's genre, and getting this
wrong is a common import from the wrong tradition. In a clinical or
epidemiological journal, Methods gives eligibility and recruitment and Results
opens with a patient-characteristics table, because who was studied is a
finding. In a methods or physics journal the cohort is apparatus: it belongs
in Methods entirely, and Results is about the measurement. Check what the
venue's own recent papers do before moving anything.

The exception worth looking for: if a cohort property is an **independent
variable** in the analysis rather than only a description — a scanner field
strength, a sampling rate, an acquisition parameter you stratify by — then its
distribution has a claim on Results even at a methods venue, because the
reader needs it to judge the stratification.

**A Methods paragraph that reasons is a Discussion paragraph in the wrong
place.** This is the most frequent structural defect in a Methods section, and
it hides well because each sentence is true. The tell is a "so", "therefore"
or "which means" joining a fact about the setup to a consequence for the
results. State the fact in Methods; put the consequence in the Discussion,
where it probably already is — check, because the duplicate is usually
verbatim.

**Results.** What was measured, in the units it was measured in, with its
denominator and its `n`. States; does not interpret. The commonest structural
defect in a draft is a Results paragraph that has started explaining why the
number came out that way — move that sentence to the Discussion and the
Results section gets shorter and better.

**Discussion.** Interprets. What the work establishes, how it relates to what
was known, what it cannot settle, and what follows. Does not restate Results
numbers; a number appears here only when the interpretation cannot be stated
without it. Limitations are stated plainly and specifically — "single
institution, so transfer to other scanners is untested" rather than "further
work is needed".

**Abstract.** Written last, from the finished paper. Follow the venue's
structure exactly; several venues enforce headings, a word count, and a voice.

## Figures and tables

- Each one answers a question the text asks. If you cannot name the question,
  it is supplementary.
- The caption stands alone. A reader who sees only the figure and its caption
  should get the point without hunting for the paragraph.
- The text says what the figure shows, not that it exists. "Amplitude falls
  with depth (Figure 2)" beats "Figure 2 shows the relationship between
  amplitude and depth".
- Count figures and tables against the venue's combined limit from the start.
  Discovering at the end that two must go is how a good panel gets cut for the
  wrong reason.

## Making a negative result do work

A result that failed to help is evidence, and it reads as failure only when it
is placed as one.

- Put it where it supports the spine, not in a section of its own at the end.
- State what it rules out, not what it did not achieve.
- Give the mechanism. "The exclusions cannot help, because the contaminant is
  stable within a patient and therefore sits in the between-patient term" is a
  finding. "The exclusions did not improve reproducibility" is a null.
- If the negative result is the paper's main contribution, the spine sentence
  should say so, and the Introduction should promise it.

## Checking for redundancy

A manuscript repeats itself in ways its author cannot see, because the person
who just wrote a paragraph is the worst-placed reader to notice it restates
something three thousand words earlier. Use the `redundancy-auditor` subagent,
which reads the document fresh and returns a claim map: every claim, where it
appears, and whether each appearance states, previews, restates, interprets or
bounds it. Redundancy shows up as a claim appearing in a role it should not.

Run it at two moments and not continuously. A draft in progress repeats itself
for good reasons, and re-auditing after every edit spends a full read to learn
nothing changed.

- **When a section is finished**, scoped to that section.
- **When the whole draft is finished**, across sections, before any prose
  editing. Cutting a duplicated paragraph is worth more than polishing both
  copies of it.

Tell the auditor the venue, since venues differ on how much restatement they
expect. Some restatement is required — the abstract restates the paper, the
Discussion may open by stating what was established — and the auditor is told
not to flag those.

Keep the claim map. It answers two later questions cheaply: whether the
abstract claims anything the paper does not show, and whether every result
gets interpreted somewhere. The `claim-evidence-auditor` reads it rather than
rebuilding it.

## Checking that the evidence is there

Separately from redundancy, every claim and every reported number should be
traceable to the artifact or citation behind it. Record the link inline, where
the number is written, rather than in a table that drifts out of step with the
prose; in a LaTeX manuscript an `\ev{value}{source}` macro that typesets as
the value alone costs the reader nothing and makes the ledger greppable.

Then run the `claim-evidence-auditor`, which returns a verdict per item:
traced, drifted, cited, miscited, unsupported or stale. The verdict worth
building for is **drifted** — the source exists and the manuscript's value no
longer matches it. Transcription error between a notebook and a manuscript is
invisible on rereading, survives every round of prose editing, and is what
gets corrected after publication. Check the digits, the units and the
denominator separately, since a number can be right and its `n` wrong.

This pass does not judge whether the evidence is *sufficient* for the claim.
That is overclaiming, and `skeptical-labmate` owns it. Keeping them apart is
what stops the evidence check from becoming a general review nobody runs.

### Filling numbers is a different job from checking them

A draft accumulates placeholders faster than anyone fills them, and the
numbers usually exist already in a notebook or a run output. That work is
mechanical and worth delegating, to `draft-number-filler` — but to a
different agent than the one that audits, and with write access the auditor
does not have.

The reason is not tidiness. An agent that writes a number into the manuscript
from the notebook and then audits the manuscript against the notebook will
report every number it wrote as verified. The audit would confirm only that
the agent can copy. An auditor earns its verdict by checking work it did not
do.

The separation that matters is writing versus checking, and only that. Do not
also forbid the filler from writing a number that happens to be final:
finality is not a property of the number or of who typed it, but of its
source — a value is final when the run it came from is the run being
published. Ask that of the whole ledger once the last run lands, rather than
tracking it per number while drafting. What the filler owes you is an
accurate record of which run each value came from; what the auditor owes you
is a check it could not have rigged.

## Three moments to use this skill

**Before drafting.** Load the venue, write the spine, lay out the skeleton as
empty section files, budget words, and write each section's job as a comment
inside it. The comments become the outline you draft against and get deleted
last.

**While drafting.** When unsure where a paragraph belongs, ask which section's
job it is doing. A paragraph that is doing two jobs is two paragraphs in two
sections.

**At revision.** Audit against structure rather than prose: does each section
still do only its job, does every figure answer a named question, does the
count fit, does the abstract match what the paper ended up showing. Run the
`redundancy-auditor` across the whole draft. Then hand the prose to `humanize`
with the venue's register — in that order, because cutting a duplicated
paragraph is cheaper than editing it twice.

## Adding a venue

`venues/_template.md` is the schema, and `venues/README.md` says what each
field is for. Fill it from the venue's own author guide, record where the
facts came from and the date, and mark anything you could not verify rather
than guessing. A wrong limit is worse than a missing one, because nobody
rechecks a number that is already written down.
