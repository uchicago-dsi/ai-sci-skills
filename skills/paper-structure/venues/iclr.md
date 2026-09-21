# International Conference on Learning Representations (ICLR)

**Verified:** 2026-09-21 against the ICLR 2026 Author Guide
(<https://iclr.cc/Conferences/2026/AuthorGuide>) and the ICLR LLM policy page
(<https://iclr.cc/FAQ/LLM>). **Re-verify every cycle** — ICLR changes page
limits and required statements between years more often than a journal does.
**Register:** `ml-conference` *(not yet written; see the note at the end)*

Open-review machine learning conference. Reviewers are researchers reading
under time pressure with several papers each, and every review is public
alongside a rebuttal. A paper here argues that a method or an empirical
finding changes what the field should do.

## Section skeleton

1. **Introduction** — problem, gap, contribution. Most ICLR papers end it
   with an explicit bulleted contributions list; this is convention rather
   than a rule, and reviewers look for it.
2. **Related Work** — its own section, unlike a journal in the IMRaD
   tradition. It positions and compares rather than surveys. It may also sit
   after the method, which is a deliberate choice: late placement keeps the
   contribution first.
3. **Method** (or Approach) — the contribution itself. Not called Methods,
   and it is an exposition rather than a rebuild recipe; reproduction detail
   goes to the appendix.
4. **Experiments** — setup, baselines, results and ablations together, rather
   than a separate Results section. Ablations are effectively expected.
5. **Conclusion** — short. Often carries limitations and future work.
6. **Reproducibility Statement** *(optional)* and **Ethics Statement**
   *(optional)*, both at the end of the main text before the references.
   Neither counts toward the page limit.
7. **References**, then **Appendices**.

## Limits

| Stage | Main text | Figures + tables |
| --- | --- | --- |
| Submission | 9 pages | no separate limit; they consume page budget |
| Rebuttal and camera-ready | 10 pages | same |

**What counts toward the limit:** the main text only. References do not count.
Appendices do not count and may be any length, but *reviewers are not required
to read them* — anything load-bearing has to be in the main text. The
reproducibility statement, the ethics statement and an LLM-usage section also
do not count.

The page budget rather than a word budget changes how to plan: figures and
tables compete directly with prose, so a figure has to be worth the paragraph
it displaces.

## Abstract

Unstructured, a single paragraph, no enforced word count. Must be genuine and
informative at the abstract deadline, which precedes the full submission
deadline; placeholder or duplicate abstracts are removed.

## References

Whatever the `iclr2026.sty` style file produces, author-year in the text. No
limit, and references do not consume the page budget, so there is no reason
to cite thinly.

## Required apparatus

- **Reproducibility Statement** — optional, but its absence is noticed. It
  points at where the reproducibility effort lives rather than repeating
  detail.
- **Ethics Statement** — optional, one page maximum, encouraged for human
  subjects, sensitive data or foreseeable misuse.
- **LLM usage disclosure** — required when an LLM played a significant role in
  ideation or writing, as a separate appendix section describing its precise
  role. **Not disclosing significant use can lead to desk rejection.** LLMs
  cannot be authors.

## Review model

Double-blind, and enforced harshly: any paper revealing author identity in the
main text *or the supplementary material* is desk rejected. A related arXiv
preprint is acceptable provided it is cited in the third person.

## Submission mechanics

OpenReview. LaTeX only in practice, using `iclr2026.zip` from the
Master-Template repository. The abstract deadline is roughly a week before the
paper deadline and is binding.

## What reviewers here punish

- A missing ablation. A method with several components and no evidence about
  which one matters reads as unfinished.
- Weak or stale baselines, and comparisons that are not matched on compute,
  data or tuning budget.
- Claims in the abstract that the experiments do not support, which is the
  most common cause of a confident negative review.
- Load-bearing material hidden in the appendix, which reviewers are entitled
  to ignore.
- An unaddressed limitation that a reviewer finds themselves.

## Note

This file's register, `ml-conference`, is not written yet. Until it is, edit
ICLR prose with `journal-imrad` and override two things by hand: ICLR expects
the **active voice and the first person** ("we show"), and it tolerates a more
informal, direct register than a clinical journal.
