# Magnetic Resonance in Medicine (MRM)

**Verified:** 2026-09-21 against the MRM Style Guide (Nov 2022) and the MRM
Author Guidelines and Information for Subscribers (Dec 2022), both PDFs linked
from the journal's author-guidelines page. The live HTML page returns 403 to
non-browser requests, so it could not be checked directly; **confirm the limit
table in a browser before submitting.**
**Register:** `journal-imrad`

Wiley journal of the ISMRM. Readers are MRI physicists, engineers and
quantitative imaging researchers. A paper here argues about measurement: how
a quantity is acquired, what corrupts it, and how well it reproduces.

## Section skeleton

1. **Introduction** — why the question matters, what is known, what is
   missing, the hypothesis. Prior work is woven in; MRM asks authors to avoid
   "bulk" citations and to write explanatory text around each one. There is no
   Related Work section at this venue.
2. **Theory** *(optional)* — sits after the Introduction when mathematical
   derivation is needed. Selecting it changes the abstract's headings.
3. **Methods** — named exactly `Methods`. `Materials and Methods` is
   specifically called out as wrong.
4. **Results** — findings and observations, not a repetition of the figure
   captions.
5. **Discussion** — critical evaluation and interpretation.
6. **Conclusions**, then optional **Acknowledgments**, then **Data
   Availability Statement**, then References.

Appendices are permitted and discouraged, and they **count toward the word
limit**, so they are not a way to make room.

## Limits

| Article type | Body words | Figures + tables (combined) |
| --- | --- | --- |
| Research Article | 5000 | 10 |
| Rapid Communication | 3500 | 7 |
| Technical Note | 2800 | 5 |
| Letter to the Editor / Reply | 750 | 1 |
| Review / Guidelines | 7500 | 15 |
| Mini Review | 1200 | 2 |
| Review-Symposium | 5000 | 2 |

**What counts toward the body:** the text of Introduction, Methods, Results
and Discussion, **plus appendices when present**. Excluded: title page,
abstract, figure captions, tables, table captions, references, and revision
markings. Supporting Information is excluded, which makes it the real escape
valve — it is explicitly encouraged for figures, tables and scripts, with a
request to keep supporting *text* short.

Limits may be relaxed "in exceptional cases", with a warning that exceeding
them may reduce a paper's chances.

## Abstract

250 words maximum, structured, in the **passive voice**, avoiding the first
person. Headings verbatim:

    Purpose:  Methods:  Results:  Conclusion:

With a Theory section, `Purpose / Theory and Methods / Results / Conclusion`
is also accepted. Must be self-contained: no equations, and citations only
where unavoidable. Followed by three to six keywords.

## References

AMA Manual of Style, 10th edition, citation-sequence format: numbered in the
text, listed in numerical order. Journal abbreviations from the List of
Journals Indexed for MEDLINE. No fixed limit on the number of references.
"Submitted" and "in preparation" are not acceptable entries; private
communication is cited in the text, not in the list.

## Required apparatus

- **Data Availability Statement** — must appear in the main manuscript to
  appear in the final paper. For software, MRM asks for a link, preferably a
  DOI, **and the SHA-1 of the specific revision used**, maintained for at
  least five years. Preferred hosts are GitHub, BitBucket and SourceForge;
  XNAT for imaging data.
- Authorship follows ICMJE's four criteria, all required. MRM adds that anyone
  who participated in criterion 1 should be *offered* the chance at 2, 3 and 4.

## Review model

Single-blind by default; double-blind is elected at submission. Choosing
double-blind makes the authors responsible for anonymizing the title page,
acknowledgments, URLs and code links. Preprints are allowed and do not
prejudice the decision, but must be declared in the cover letter and uploaded
as "Supplementary Material for Review only".

## Submission mechanics

ScholarOne, <https://mc.manuscriptcentral.com/mrm>. Manuscript as `.doc`,
`.docx`, `.rtf` or `.tex`; Word is called preferred but LaTeX is fully
supported and papers are typeset directly from the author's LaTeX file. PDF
submission is allowed for an original submission but not a revision, and
loses the line numbers ScholarOne's own conversion generates.

Class files are Wiley's, from the journal's LaTeX page. Submit the `.tex`,
every class and style file, and the `.bbl`; if ScholarOne's compile fails,
leave the sources uploaded and add a locally built PDF.

Figures must be TIFF or EPS — **PDF figures are accepted only for LaTeX
submissions**, which is the one place LaTeX authors get a better deal. Widths
8.67 cm (1 column), 13.02 cm (1.5), 17.56 cm (2); page depth 24.13 cm. Line
art 1200 dpi, halftones 300 dpi, each file under 20 MB. Captions listed
together at the end of the text file, sub-panels labelled A, B, C, callouts
spelled "Figure 1". Word, Excel and PowerPoint figures are rejected.

## What reviewers here punish

- A precision claim without an accuracy statement beside it, and any
  reproducibility number reported without saying what it was computed over.
- Missing units, denominators or `n`, especially in a table.
- A method described too thinly to reproduce. This readership rebuilds things.
- Claiming an acquisition-specific measurement without independent evidence
  that the measurement is what it says it is.
