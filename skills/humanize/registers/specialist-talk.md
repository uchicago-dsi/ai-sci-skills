# Register: specialist-talk

Slides, briefs and emails for collaborators who are domain experts in the
measurement itself: an MRI physicist reviewing an imaging analysis, a
statistician reviewing a model, a clinician reviewing a cohort. Everything in
`talk.md` applies except where this file says otherwise.

The reader knows the field better than the author does, and has not seen any
of the work. They will judge each result by whether they can tell exactly what
was done. A result they cannot reconstruct reads as hand-waving, however
correct it is.

## Jargon threshold

Shared terms stay unglossed. Signal ratios, k-space, sequence names, relaxation
times, partial volume, a named curve family: the audience uses these daily, and
defining them reads as talking down. The aggressive plain-language rule in
`talk.md` does not apply to the field's own vocabulary.

The project's private vocabulary is the opposite case. A run name, an internal
arm label ("s0.4", "production prior arm"), a cohort code or a home-made metric
means nothing to this reader. Replace it with what it is, every time.

## Explaining an experiment

This is the rule that matters most. Every experiment gets, on its own slide or
in its own paragraph:

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

Do not compress an experiment into its conclusion. An expert who disagrees
needs to see the step they would have done differently.

## Figures

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

As in `talk.md`, and additionally: state the uncertainty on any number the
argument rests on, and the comparison it is paired against. Experts will ask.
