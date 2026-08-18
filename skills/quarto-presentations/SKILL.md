---
name: quarto-presentations
description: "Create, edit, render, preview, and export Quarto reveal.js slide decks for scientific and technical presentations. Use when the agent works on .qmd slides, reveal.js layout, speaker notes, figure sidecars, slide PDF export, or reusable deck templates."
---

# Quarto Presentations

## Scope

- Own the presentation mechanics: Quarto `.qmd` structure, reveal.js format, templates, rendering, PDF export, figures, speaker notes, and layout checks.
- Use the current project's narrative, branding, and environment policy when present. Keep lab-specific names, paths, logos, colors, clusters, and personal workflow facts out of the shared skill.
- Prefer text-based Quarto edits. Do not move the user to PowerPoint, Keynote, or Google Slides unless they ask.

## Start Or Locate A Deck

- If a deck already exists, edit the `.qmd` directly and preserve its local template, theme, and output conventions.
- If starting a new deck, first look for a project-local or lab-local Quarto template. Use that when branding or site policy matters.
- If no local template exists, copy this skill's `assets/_template/` directory and replace the slide content:

```bash
cp -R /path/to/quarto-presentations/assets/_template ./my-talk
```

- The bundled template includes a full-width bottom logo panel and placeholder logos under `logos/`. Replace those assets with local brand files, keeping the same relative paths or updating `_logos.html`.
- Keep reusable branding in a local template. Do not hard-code one person's institution, name, logos, or cluster paths into a shared deck scaffold.
- Avoid putting body content before the first slide heading; reveal.js can turn it into a blank first slide.

## Build And Preview

- Use the project's existing Quarto environment and command style. If none is documented, start with plain `quarto`.
- Activate a conda/mamba Quarto env rather than calling its `bin/quarto` by absolute path. The
  conda-forge package resolves `QUARTO_SHARE_PATH`, `QUARTO_DENO`, and `QUARTO_PANDOC` from
  activation scripts; without them the launcher guesses its own share directory, guesses wrong,
  and reports `cat: .../share/version: No such file or directory`. That message means unactivated,
  not broken — do not reinstall on the strength of it:

```bash
micromamba run -n quarto quarto --version   # works
"$PREFIX/envs/quarto/bin/quarto" --version  # fails on the missing version file
```

- Run `quarto check` before a first export in an unfamiliar environment. It names the missing
  piece directly, including whether any Chromium is present for PDF printing.
- Preview while editing:

```bash
quarto preview slides.qmd
```

- Render with the format declared in frontmatter:

```bash
quarto render slides.qmd
```

- Do not pass `--to pdf` or `--to html` for reveal.js decks unless the deck explicitly documents that path. It can bypass the reveal.js slide format and produce article-like output.
- Keep heavy analyses out of the deck. Prefer sidecar scripts that write finished figures to `figures/`, then reference those files from slides.

## Export PDF

- First render HTML, then print the reveal.js `?print-pdf` view.
- Prefer the Playwright helper when available because it waits for reveal's print pages, images, fonts, and MathJax:

```bash
quarto render slides.qmd
python /path/to/quarto-presentations/scripts/print_reveal_pdf_playwright.py \
  slides.html slides.pdf
```

- Printing needs a real browser, and the Playwright package being importable does not mean one is
  downloaded. Fetch the headless shell once and point the cache at project or scratch storage,
  because the default `~/.cache/ms-playwright` is over 100 MB and home quotas on shared clusters
  are small:

```bash
export PLAYWRIGHT_BROWSERS_PATH=/path/to/project/.cache/ms-playwright
python -m playwright install chromium
```

- Export that same `PLAYWRIGHT_BROWSERS_PATH` when running the helper, or it will look in the
  default cache and report no browser despite the download.

- If Playwright is unavailable but Chrome or Chromium is installed, use the CDP helper:

```bash
python /path/to/quarto-presentations/scripts/print_reveal_pdf_cdp.py \
  slides.html slides.pdf
```

- If a live `quarto preview` browser is open, run render and PDF export as separate commands and verify the PDF changed before trusting it.
- Confirm the PDF has one page per slide by comparing `pdfinfo` pages against the deck's slide
  count. More pages than slides means a slide overflowed onto a continuation page:

```bash
pdfinfo slides.pdf | sed -n '1,40p'
grep -c '^## ' slides.qmd          # plus one for the title slide
pdftoppm -png -r 100 -f 1 -l 3 slides.pdf ./slides-check
```

- Equal counts are not enough on their own. A slide taller than the page can drop its closing
  line instead of spilling, so the page total still matches while the takeaway is silently gone
  from the print view but visible in HTML. Grep the extracted PDF text for the last line of each
  content-heavy slide:

```bash
pdftotext slides.pdf - | grep -c 'the closing phrase'
```

- Fix overflow by trimming the cells or lines that wrap, then shrinking type — in that order.
  Wrapping table cells cost several lines each, so shortening them recovers more room than a
  font change and keeps the deck readable:

```markdown
::: {style="font-size: 0.7em"}
| a | wide | table |
|---|---|---|
:::
```

- Write rasterized check images beside the deck or into its run directory, not `/tmp`. Slides can
  carry unpublished or protected content, and shared temp directories are world-traversable.

## Layout Rules

- Inspect representative pages in the exported PDF, not only the live preview. Print layout is the final artifact.
- Preserve scientific figure aspect ratios. Use one of `width` or `height`, not both, unless the source already has the target ratio.
- Add `.nostretch` and explicit sizing to single-image slides if reveal.js makes an image too large:

```markdown
![](figures/result.png){.nostretch width="72%" fig-align="center"}
```

- Treat shrunk or inconsistent slide titles as overflow evidence. Trim text, split the slide, or use columns instead of shipping a scaled-down slide.
- Use speaker notes for talk track, not dense on-slide prose:

```markdown
::: {.notes}
What to say out loud.
:::
```

## Sourcing Claims

- Any quantitative or empirical claim a reader could challenge needs a resolvable
  reference on the slide that makes it. That covers effect sizes, rates, percentages,
  cohort or sample counts, performance figures, and "studies show" statements. Common
  knowledge in the audience's own field does not, and neither do numbers computed from
  the project's own data, which cite the producing script or artifact instead.
- A resolvable reference means author, year, venue, and a DOI or URL a reader can open.
  An opaque token from a search tool, a bare model recollection, or a claim inherited
  from an intermediate document that itself lacks a citation is not a reference. When a
  source document's citations are unresolvable, treat its claims as unsourced and find
  the primary source before putting a number on a slide.
- Verify the reference resolves and reports the number being cited. Check publication
  status while doing so: retracted, withdrawn, and preprint-only work must be labelled
  as such wherever the number appears.
- Put the citation on the same slide, small, rather than in a closing bibliography a
  reader cannot map back to the claim:

```markdown
::: {style="font-size: 0.6em"}
Vreemann et al., *Breast Cancer Res Treat* 2018. <https://doi.org/10.1007/s10549-018-4688-z>
:::
```

- If a claim cannot be sourced, cut it or restate it as the project's own observation
  with its provenance. Do not keep a striking number because it is striking.

## Branding And Local Templates

- Keep the shared skill neutral. Read `references/branding.md` when adapting a branded template, logo bar, footer, or institution-specific style.
- If a local template improves through real use, port generic fixes back to that local template. Only upstream changes that are institution-neutral.
