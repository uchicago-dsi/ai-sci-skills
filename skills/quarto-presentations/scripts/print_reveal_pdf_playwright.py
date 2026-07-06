#!/usr/bin/env python3
"""Print a Quarto reveal.js HTML deck to PDF with Playwright Chromium."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="Rendered reveal.js HTML file")
    parser.add_argument("pdf", type=Path, help="Output PDF path")
    parser.add_argument("--timeout-ms", type=int, default=90000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    html_path = args.html.resolve()
    pdf_path = args.pdf.resolve()
    if not html_path.exists():
        raise FileNotFoundError(html_path)

    browser_cache = Path(sys.prefix) / "ms-playwright"
    if "PLAYWRIGHT_BROWSERS_PATH" not in os.environ and browser_cache.exists():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_cache)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed in this Python environment. "
            "Install playwright and a Chromium browser, or use print_reveal_pdf_cdp.py."
        ) from exc

    url = f"{html_path.as_uri()}?print-pdf"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(url, wait_until="networkidle", timeout=args.timeout_ms)
        page.wait_for_function(
            "() => document.querySelectorAll('.reveal .pdf-page').length > 0",
            timeout=args.timeout_ms,
        )
        page.wait_for_function(
            "() => Array.from(document.images).every((img) => img.complete)",
            timeout=args.timeout_ms,
        )
        page.evaluate(
            """
            () => new Promise((resolve) => {
              if (document.fonts && document.fonts.ready) {
                document.fonts.ready.then(resolve);
              } else {
                resolve();
              }
            })
            """
        )
        page.evaluate(
            """
            () => new Promise((resolve) => {
              if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise().then(resolve).catch(resolve);
              } else if (window.MathJax && window.MathJax.Hub) {
                window.MathJax.Hub.Queue(resolve);
              } else {
                resolve();
              }
            })
            """
        )
        page.wait_for_timeout(1000)
        page.pdf(path=str(pdf_path), print_background=True, prefer_css_page_size=True)
        pages = page.locator(".reveal .pdf-page").count()
        browser.close()
    print(f"wrote {pdf_path}: {pages} reveal pdf-pages")


if __name__ == "__main__":
    main()
