# Register: ml-conference

A submission to a machine learning conference with open or semi-open review —
ICLR, NeurIPS, ICML, CVPR and their neighbours.

The reader is a researcher with several papers to review in the same window,
reading fast and deciding early whether this one is worth close attention.
Reviews are public and quotable, and a reviewer who misreads a sentence says
so in writing. This register sits between `talk` and `journal-imrad`: it keeps
the direct voice of a talk and the formality of a manuscript.

## Voice

- **Active voice and the first person.** "We show", not "it is shown". This is
  the sharpest difference from journal-imrad, where person and voice follow
  the house style. Here the first person is expected in every section,
  including the abstract and the method. Use the passive only where the agent
  genuinely is not the point.
- **No contractions.** Active voice is not informality, and a reader of this
  file will assume otherwise. "Cannot", not "can't" — the same rule as
  journal-imrad and the opposite of talk. The paper is direct, not casual.
- **Front-load.** The first sentence of a paragraph carries its point and the
  rest supports it. A reviewer skimming reads first sentences, so a paragraph
  that builds to its claim in the last line has spent its one chance. Same for
  a section, and for the abstract.
- Sentences may run longer than in a talk, but keep them unnested. A clause
  the reader has to hold open while another resolves is the first casualty of
  fast reading.

## Jargon threshold

Low — lower than journal-imrad. The field's shared vocabulary is large, and
spelling out a standard term reads as padding: attention, KL, logits, linear
probe, held-out, teacher forcing all stay, unglossed.

The cost sits elsewhere. **Invented notation and one-off abbreviations are
expensive**, because a reviewer will not page back to find your definition.
They will guess, and the guess goes into the review.

- Introduce a symbol in the sentence that first uses it, and re-gloss it at a
  distant reuse rather than sending the reader hunting.
- Delete an abbreviation you coined and used four times. The lines it saves
  are not worth the lookup.
- A name for your own component is a label, not an argument. If the paper
  cannot say in one clause what the component does, the name is hiding it.

## Naming methods

**The Method section is exposition, not a rebuild recipe** — reproduction
detail goes to the appendix — so the journal-imrad rule inverts here. State
the idea in words first: what the method does and why that should work, then
the equations that implement it. A Method section opening on notation makes
the reader reconstruct the idea from the machinery.

In Experiments, name the setup precisely: baselines, data, and the compute and
tuning budget each arm received. That is what makes the comparison checkable.

## Routine checks

Cut the clauses claiming credit for competent practice — "we carefully tuned",
"following standard protocol", "after extensive experimentation".

Keep, with a number, any check that establishes the comparison is fair:
matched budgets across arms, the seeds, the tuning protocol applied to the
baseline as well as the method. To a reviewer that is evidence, not diligence.

## Hedging

**Under-claiming is punished about as hard as over-claiming.** A result stated
as a maybe invites a reviewer to discount it, and vagueness reads as an author
who does not know what they found. Say what the result shows, with the
condition it holds under.

- One hedge, the accurate one. Strike stacked hedges: "may potentially
  suggest", "appears to possibly indicate".
- The scope condition is not a hedge. Keep the datasets, the model scale, the
  regime where it held.
- Do not upgrade in the other direction. An abstract claim the experiments do
  not support is the most common reason a reviewer turns negative; check each
  one against the section meant to support it.
- State a limitation plainly. One a reviewer finds unaided costs far more.

## Contribution lists

The bulleted contributions ending the Introduction are a convention reviewers
look for. When editing one, make every bullet a **claim** rather than an
activity — "we study the effect of depth" is an activity, "depth beyond eight
layers does not improve accuracy on any of the three benchmarks" is a claim —
and keep the bullets parallel in grammatical form, one contribution each. Do
not add or drop a contribution while editing prose; that is the author's call.

## Numbers

Units, denominator and `n`, where `n` here has two parts that are easy to
conflate: the size of the evaluation set and the number of seeds. Give both,
and report spread across seeds rather than the mean alone — a single-seed
difference is not a result, and saying so is more persuasive than hiding it.
Confirm the arms match on data, compute and tuning budget, and say what they
match on. Bold in a results table is a claim; if the gap is inside the seed
spread, it is not one.

## What not to touch

On top of the core rule against changing literals: leave `\cite{}`, `\ref{}`,
equation numbering, float placement and every venue style-file command exactly
as they are.

**Do not introduce an identifying detail during an edit.** Review is
double-blind and enforced on the supplementary material as well as the main
text, with desk rejection as the penalty. An author name, a lab, a repository
URL, a cluster name, an internal codename, or a self-citation rewritten into
the first person all break it.

## Venue facts

Page limits, required statements, LLM-usage disclosure and the section
skeleton live in `paper-structure/venues/<venue>.md`, installed at
`~/.claude/skills/paper-structure/venues/` and `~/.codex/skills/...`. Read the
venue's file rather than assuming; these change between years far more often
than a journal's house style does. Apply its **Abstract** and **References**
sections, the two that change how prose is written rather than how it is
organized.

One consequence for editing: these venues budget **pages, not words**, and
figures compete with prose for the same space. Trimming three words from a
line that does not reflow saves nothing. Cut whole sentences, paragraphs and
redundant panels, and report how many lines a cut actually recovered.

If the venue has no file yet, write one from `venues/_template.md` before
editing.
