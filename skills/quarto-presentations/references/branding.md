# Branding And Local Templates

Keep shared Quarto mechanics separate from local identity.

## What Belongs Locally

- Person names, lab names, institution names, sponsor marks, logos, brand colors, required acknowledgments, and venue-specific paths.
- Cluster or workstation commands such as a named environment manager, login-node browser path, or site-specific PDF export workaround.
- Filled-in example talks that reveal unpublished work or private project details.

Put these in a project-local or user-local template, not in the shared skill.

## How To Adapt A Branded Deck

1. Inspect existing decks or local policy for required colors, fonts, logos, and footer rules.
2. Copy the shared template into a local template directory.
3. Replace `logos/primary.svg` and `logos/secondary.svg`, or add logo/image assets with clear names and alt text.
4. Wire branding through `custom.scss` and the included `_logos.html` file.
5. Keep paths relative to the rendered `slides.html`.
6. Render HTML, export PDF, and inspect representative pages.

## Footer Or Logo Bar Pattern

The shared template already includes this pattern with placeholder logos:

- Reserve vertical space in CSS, for example `--deck-bottom-safe: 84px`.
- Keep scientific content above the reserved strip.
- Check the printed PDF, not only the live deck. Chrome can paint fixed-position elements differently in print mode.
- If fixed elements cover slide numbers in PDF export, hide the fixed bar under `html.print-pdf` and redraw the bar on each `.pdf-page::after` so page content and slide numbers layer correctly.

Minimal structure:

```yaml
format:
  revealjs:
    include-after-body:
      - _logos.html
      - _autofit.html
```

```html
<div id="deck-logos">
  <img src="logos/primary.svg" alt="Primary organization logo">
  <img src="logos/secondary.svg" alt="Secondary organization logo">
</div>
```

```scss
:root {
  --deck-bottom-safe: 84px;
  --deck-logo-bar-height: 64px;
}

#deck-logos {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: var(--deck-logo-bar-height);
}
```

Treat the mechanism as shared and the identity assets as local. Upstream generic layout fixes; keep institution-specific logos, colors, and names in a local template.
