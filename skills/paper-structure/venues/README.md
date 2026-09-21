# Venue files

One file per publication venue, holding the facts that decide a manuscript's
structure. `paper-structure` reads the file before anything else; `humanize`
reads its **Register** field to pick an editing voice.

These are data, not instructions. They go stale — limits, required statements
and review models change between cycles. Every file records where its facts
came from and when they were checked, and every file is expected to be
re-verified against the venue's own page before a submission.

## Fields

| Field | Why it is here |
| --- | --- |
| **Verified** | The date the facts were checked and against what. A file older than a year is a lead, not a specification. |
| **Register** | Which `humanize` register applies. This is the link between structure and voice. |
| **Section skeleton** | Ordered sections with the venue's own names, and what each does *here*. This is the field that makes the file necessary: section order and naming are not universal. |
| **Limits** | Body length, what counts toward it, figures and tables, and whether they share a budget. |
| **Abstract** | Structured or not, headings, word count, voice, what is forbidden in it. |
| **References** | Style, in-text form, any limit. |
| **Required apparatus** | Data availability, reproducibility, ethics, limitations, conflict of interest, LLM disclosure — whatever this venue demands beyond the main sections. |
| **Review model** | Single or double blind, and what anonymization actually requires. |
| **Submission mechanics** | System, accepted file formats, class or style files, figure formats. |
| **What reviewers here punish** | The judgement layer. Not in any author guide, and the most useful part of the file once it is right. |

## Writing a new one

Copy `_template.md`. Fill it from the venue's own author guide, not from
memory and not from another paper's formatting. Mark anything you could not
verify as unverified rather than guessing: a wrong number that is written down
gets trusted, while a gap gets checked.
