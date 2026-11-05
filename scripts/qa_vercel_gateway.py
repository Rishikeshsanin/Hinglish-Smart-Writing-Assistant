#!/usr/bin/env python3
"""Verify the LIVE Vercel landing page is an accessible gateway, not a fake AI.

No API mocking, no credentials, no model inference. Native Streamlit model
inference is tested separately by scripts/qa_product_release.py.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

URL = "https://indicwrite-public-web.vercel.app/"
NATIVE = "https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/"
VIEWPORTS = [("mobile-320", 320, 700), ("mobile-390", 390, 844),
             ("tablet-768", 768, 1024), ("desktop-1440", 1440, 900)]
OUTPUT = Path(os.getenv("INDICWRITE_GATEWAY_QA_DIR", "gateway-qa"))


def run():
    from playwright.sync_api import expect, sync_playwright

    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"target": URL, "native": NATIVE, "timestamp_utc": datetime.now(
        timezone.utc).isoformat(), "commit": os.getenv("GITHUB_SHA", "local-unknown"),
        "run_url": "https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/"
                   + os.environ["GITHUB_RUN_ID"] if os.getenv("GITHUB_RUN_ID") else None,
        "mode": "live-vercel-browser", "real_model_executed_here": False,
        "viewports": [], "page_errors": [], "status": "FAIL"}
    started = time.monotonic()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            try:
                for label, width, height in VIEWPORTS:
                    context = browser.new_context(viewport={"width": width, "height": height},
                                                  locale="en-IN")
                    page = context.new_page()
                    page.on("pageerror", lambda error: report["page_errors"].append(str(error)))
                    response = page.goto(URL, wait_until="domcontentloaded", timeout=60000)
                    assert response and response.status == 200, (
                        f"{label}: live Vercel returned HTTP {response.status if response else 'no response'}"
                    )
                    expect(page.get_by_role("heading", name="Your words, beautifully written in Hindi.")).to_be_visible(timeout=20000)
                    link = page.get_by_role("link", name="Open native IndicWrite converter, hosted on Streamlit")
                    expect(link).to_be_visible()
                    assert link.get_attribute("href") == NATIVE, (
                        f"{label}: native converter URL differs from approved production link"
                    )
                    assert page.get_by_text("This Vercel page is a gateway", exact=False).count()
                    assert page.locator("textarea").count() == 0, (
                        "Vercel must not pretend to run official model inference"
                    )
                    overflow = page.evaluate(
                        "document.documentElement.scrollWidth > window.innerWidth + 4"
                    )
                    assert not overflow, f"Horizontal overflow on {width}px viewport"
                    if label == "desktop-1440":
                        page.keyboard.press("Tab")
                        focus = page.evaluate(
                            "document.activeElement && document.activeElement.textContent.trim()"
                        )
                        assert focus == "Skip to content", f"Keyboard skip link inaccessible: {focus!r}"
                        report["keyboard_skip_link"] = True
                    page.screenshot(path=str(OUTPUT / f"{label}.png"), full_page=True)
                    report["viewports"].append({
                        "name": label, "width": width, "http_status": response.status,
                        "no_horizontal_overflow": True, "approved_cta_present": True
                    })
                    if label == "desktop-1440":
                        # User-visible click: verify target navigation actually works.
                        link.click(timeout=20000)
                        page.wait_for_url(NATIVE + "*", wait_until="domcontentloaded", timeout=60000)
                        report["native_link_navigation"] = page.url.startswith(NATIVE)
                    context.close()
                assert not report["page_errors"], report["page_errors"]
                assert report.get("native_link_navigation"), "Native CTA navigation was not verified"
                report["status"] = "PASS"
                print("LIVE_VERCEL_GATEWAY_BROWSER_PASS", URL, "native=", NATIVE, flush=True)
                return 0
            finally:
                browser.close()
    except Exception as exc:
        report["failure"] = repr(exc)
        print(f"LIVE_VERCEL_GATEWAY_BROWSER_FAIL: {exc!r}", file=sys.stderr, flush=True)
        return 1
    finally:
        report["duration_seconds"] = round(time.monotonic() - started, 2)
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "evidence.json").write_text(json.dumps(
            report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(run())
