#!/usr/bin/env python3
"""Print a Quarto reveal.js HTML deck to PDF through Chrome DevTools Protocol."""

from __future__ import annotations

import argparse
import base64
import itertools
import json
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request


COMMON_CHROME_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path, help="Rendered reveal.js HTML file")
    parser.add_argument("pdf", type=Path, help="Output PDF path")
    parser.add_argument("--chrome", type=Path, default=None, help="Chrome or Chromium executable")
    parser.add_argument("--timeout-s", type=float, default=60.0)
    return parser.parse_args()


def find_chrome(explicit: Path | None) -> str:
    if explicit:
        if explicit.exists():
            return str(explicit)
        raise FileNotFoundError(explicit)
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        path = shutil.which(name)
        if path:
            return path
    for path in COMMON_CHROME_PATHS:
        if Path(path).exists():
            return path
    raise SystemExit("Could not find Chrome/Chromium. Pass --chrome or use the Playwright helper.")


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_tabs(port: int, timeout_s: float) -> list[dict]:
    deadline = time.time() + timeout_s
    url = f"http://127.0.0.1:{port}/json/list"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return json.load(response)
        except Exception:
            time.sleep(0.2)
    raise SystemExit("Chrome debugger endpoint never came up")


def main() -> None:
    args = parse_args()
    html_path = args.html.resolve()
    pdf_path = args.pdf.resolve()
    if not html_path.exists():
        raise FileNotFoundError(html_path)

    try:
        import websocket
    except ImportError as exc:
        raise SystemExit(
            "The websocket-client package is required for the CDP helper. "
            "Install websocket-client or use print_reveal_pdf_playwright.py."
        ) from exc

    chrome = find_chrome(args.chrome)
    port = free_port()
    profile = tempfile.mkdtemp(prefix="quarto_cdp_chrome_")
    proc = subprocess.Popen(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            f"--user-data-dir={profile}",
            f"--remote-debugging-port={port}",
            "--remote-allow-origins=*",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        tabs = wait_for_tabs(port, args.timeout_s)
        page = next(tab for tab in tabs if tab.get("type") == "page")
        ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=args.timeout_s)
        ids = itertools.count(1)

        def cmd(method: str, **params):
            request_id = next(ids)
            ws.send(json.dumps({"id": request_id, "method": method, "params": params}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == request_id:
                    if "error" in msg:
                        raise SystemExit(f"CDP error from {method}: {msg['error']}")
                    return msg["result"]

        def evaluate(expr: str):
            result = cmd("Runtime.evaluate", expression=expr, returnByValue=True)
            return result["result"].get("value")

        cmd("Page.enable")
        cmd("Page.navigate", url=f"{html_path.as_uri()}?print-pdf")

        deadline = time.time() + args.timeout_s
        pages = 0
        while time.time() < deadline:
            pages = evaluate(
                "document.readyState === 'complete' "
                "? document.querySelectorAll('.reveal .pdf-page').length : 0"
            ) or 0
            if pages > 0:
                stable = evaluate("document.querySelectorAll('.reveal .pdf-page').length")
                time.sleep(1.0)
                if evaluate("document.querySelectorAll('.reveal .pdf-page').length") == stable:
                    break
            time.sleep(0.5)
        if pages == 0:
            raise SystemExit("reveal never produced .pdf-page elements")

        result = cmd(
            "Page.printToPDF",
            printBackground=True,
            preferCSSPageSize=True,
            displayHeaderFooter=False,
            transferMode="ReturnAsBase64",
        )
        pdf_path.write_bytes(base64.b64decode(result["data"]))
        print(f"wrote {pdf_path}: {pages} reveal pdf-pages")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    main()
