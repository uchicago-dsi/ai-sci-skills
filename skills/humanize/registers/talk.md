# Register: talk

Slides, PI and progress updates, lab meetings, notes, chat, briefs. This is
the default when `/humanize` is invoked with no register.

The reader is listening or skimming, once, with no chance to re-read. Nothing
here is going to a copy editor.

## Voice

- **Contractions by default**: "can't", "don't", "isn't", "doesn't", "won't",
  "we're", "it's", "there's". The uncontracted form reads as stiff rather than
  precise, and "cannot" is the most frequent offender. Expand one only where
  the full form does real work: genuine emphasis ("this does **not** change
  the answer"), a contraction that is ambiguous or hard to say aloud, or a
  quotation.
- First person and active voice throughout. "We found", not "it was found".
- Short sentences. If a sentence needs a comma to survive being read aloud,
  it is two sentences.

## Jargon threshold

Aggressive. Say what something does instead of naming the method that did it.
A term survives only if this specific audience says that exact word for that
exact thing, routinely, and the plain version would be longer, vaguer, or less
accurate. When a term survives, the sentence around it still has to land for
someone who does not know it.

A project's private vocabulary never survives: a run name, an internal arm
label, a cohort code or a home-made metric means nothing to anyone outside the
work. Replace it with what it is, every time.

## Naming methods

Don't, unless the method is the point. A method name in a talk is a promise of
detail the audience cannot follow and will not remember. State what was done
and what followed from it.

## Routine checks

Cut them. A clause claiming credit for competent practice — "we validated the
inputs", "using standard methods", "after careful review" — tells the audience
nothing and costs their attention. Name a check only where it is a finding: it
failed, it was the hard part, or a reader would expect it to have been
skipped.

## Explaining an experiment

Every slide that shows a result explains the experiment behind it and
interprets it, whoever the audience. A result the reader cannot reconstruct
reads as hand-waving, however correct it is. Every experiment gets, on its
own slide or in its own paragraph:

- **The question**, stated as a question or as the claim the slide makes. A
  title such as "Short answer: …" is unreadable unless the question it answers
  is on the same slide.
- **The data**: which measurement, at which locations (which vessel, which
  levels along it, what ROI), in how many exams or participants, from which
  protocols.
- **What was done to it**: what was fitted, what was held fixed, what was
  shifted or scaled and by what, what was left out and predicted. Say the
  operation concretely ("each level's curve was shifted in time by its own
  fitted delay and divided by its own gain"), not by the name of the method.
- **What a positive result would look like**, and what was seen instead.
- **What it means**: one sentence interpreting the result for the argument,
  after the figure has been walked through.

## Figures

Every figure on a slide is explained and interpreted, not only shown.

- Explain every element: what each axis is, with units; what each colour,
  line, marker and bar means; what was aligned or shifted before plotting.
  The caption or speaker text walks through the figure before stating the
  result.
- Every axis is labelled and every label is readable at projection size. A
  figure too small to read is not on the slide yet.
- Show the quantity in its natural form when one exists: a curve against
  time, on linear axes, the way the audience is used to seeing it. A derived
  summary (an exceedance curve, a log-scaled distribution, a profile of a
  likelihood) needs its own explanation, and is usually a second figure
  beside the natural one, not a replacement for it.
- Log scales only where the data span orders of magnitude, and the caption
  says so.

## Numbers

Every number still carries its units, its denominator and its `n`. A talk
audience is the *easiest* place to mislead with a bare ratio, because nobody
can go back and check.
