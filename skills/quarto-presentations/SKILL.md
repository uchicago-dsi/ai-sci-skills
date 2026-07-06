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

- If Playwright is unavailable but Chrome or Chromium is installed, use the CDP helper:

```bash
python /path/to/quarto-presentations/scripts/print_reveal_pdf_cdp.py \
  slides.html slides.pdf
```

- If a live `quarto preview` browser is open, run render and PDF export as separate commands and verify the PDF changed before trusting it.
- Confirm the PDF has one page per slide. When Poppler tools are available:

```bash
pdfinfo slides.pdf | sed -n '1,40p'
pdftoppm -png -r 100 -f 1 -l 3 slides.pdf /tmp/slides-check
```

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

## Branding And Local Templates

- Keep the shared skill neutral. Read `references/branding.md` when adapting a branded template, logo bar, footer, or institution-specific style.
- If a local template improves through real use, port generic fixes back to that local template. Only upstream changes that are institution-neutral.
