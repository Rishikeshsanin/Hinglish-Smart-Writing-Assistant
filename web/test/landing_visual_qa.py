"""Local Chromium checks for the static Vercel *gateway*, NOT native model inference.

Usage:
  pip install playwright==1.56.0
  python -m playwright install chromium
  python web/test/landing_visual_qa.py --output /tmp/indicwrite-ui-qa

Set CHROMIUM_PATH=/usr/bin/chromium to use a system Chromium instead.
This test loads the exact local HTML and CSS bytes directly (no network or model).
For official-model Streamlit conversion, use scripts/browser_smoke.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

WEB_ROOT = Path(__file__).resolve().parents[1]
PUBLIC = WEB_ROOT / "public"
NATIVE_URL = "https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/"
VIEWPORTS = ((320, 800), (390, 844), (768, 1024), (1440, 900))


def git_blob_sha(raw: bytes) -> str:
    """Allow auditors to compare rendered static source with GitHub blob SHA."""
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("/tmp/indicwrite-landing-qa"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    html_bytes = (PUBLIC / "index.html").read_bytes()
    css_bytes = (PUBLIC / "styles.css").read_bytes()
    html = html_bytes.decode("utf-8").replace('<link rel="stylesheet" href="/styles.css">', "")
    css = css_bytes.decode("utf-8")

    results = []
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        browser = playwright.chromium.launch(**options)
        try:
            for width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.set_content(html, wait_until="domcontentloaded")
                page.add_style_tag(content=css)
                assert page.get_by_role(
                    "heading", name="Your words, beautifully written in Hindi."
                ).is_visible()
                cta = page.get_by_role(
                    "link", name="Open native IndicWrite converter, hosted on Streamlit"
                )
                assert cta.is_visible()
                assert cta.get_attribute("href") == NATIVE_URL

                overflow = page.evaluate(
                    "document.documentElement.scrollWidth > window.innerWidth + 4"
                )
                assert not overflow, f"Horizontal page overflow at {width}px"
                assert not errors, f"Browser errors at {width}px: {errors}"

                screenshot = f"local-static-landing-{width}.png"
                page.screenshot(path=str(args.output / screenshot), full_page=True)
                page.keyboard.press("Tab")
                skip_focused = page.locator(".skip-link").evaluate(
                    "(element) => document.activeElement === element"
                )
                assert skip_focused, f"Keyboard skip link failed at {width}px"
                results.append({
                    "scope": "LOCAL STATIC VERCEL LANDING ONLY — NO MODEL INFERENCE",
                    "width": width,
                    "height": height,
                    "horizontal_overflow": overflow,
                    "cta_target_verified": True,
                    "skip_link_keyboard_focus": skip_focused,
                    "page_errors": errors,
                    "screenshot": screenshot,
                })
                page.close()
        finally:
            browser.close()

    evidence = {
        "source_blob_sha": {
            "web/public/index.html": git_blob_sha(html_bytes),
            "web/public/styles.css": git_blob_sha(css_bytes),
        },
        "checks": results,
    }
    (args.output / "local-static-landing-qa.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
