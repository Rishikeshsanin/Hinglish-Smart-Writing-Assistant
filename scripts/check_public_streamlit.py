"""Independent, unmocked Chromium verification of the existing public IndicWrite URL.

Never treats a loaded Streamlit shell as proof of neural inference. Reports a
distinct outage/selector/convert outcome and writes screenshots and JSON even
on failure. No new deployment, model substitution, or secrets are involved.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import time
from datetime import datetime, timezone

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

URL = "https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/"
EVIDENCE = Path(os.environ.get("INDICWRITE_PUBLIC_QA_DIR", "public-qa"))
CASES = (
    ("kal mujhe college jana hai!", ("कल", "जाना"), "!"),
    ("namaste dosto, aap kaise ho?", ("नमस्ते", "कैसे"), "?"),
    ("aaj mausam bahut accha hai.", ("आज", "मौसम"), "."),
)
BUTTON = re.compile(r"Convert to Hindi", flags=re.IGNORECASE)
HINDI = re.compile(r"[\u0900-\u097f]")
ERROR_PATTERNS = (
    "this app has gone to sleep",
    "this app is in the oven",
    "this app is not available",
    "this app does not exist",
    "there was a problem starting",
    "error running app",
    "application error",
    "connection error",
    "you do not have access",
    "is currently unavailable",
)


def classify_page(body: str, buttons: list[str], http_status: int | None) -> str:
    """Diagnose an absent control without pretending the model was exercised."""
    lower = body.lower()
    if http_status is not None and http_status >= 400:
        return "http_unavailable"
    if "this app has gone to sleep" in lower:
        return "provider_asleep"
    if any(phrase in lower for phrase in ERROR_PATTERNS):
        return "provider_or_app_error"
    if "convert to hindi" in lower or any("convert to hindi" in b.lower() for b in buttons):
        return "selector_mismatch"
    if "express yourself" in lower or "indicwrite / ai4bharat" in lower:
        return "app_render_incomplete"
    return "app_not_rendered"


def verify_output(source: str, output: str, required: tuple[str, ...], punctuation: str) -> None:
    """Assertions on browser-extracted output, not generated sample predictions."""
    if not output or output == source or not HINDI.search(output):
        raise AssertionError("No distinct Devanagari inference was rendered")
    if len(HINDI.findall(output)) < 5:
        raise AssertionError("Output is too short to substantiate sentence conversion")
    if any(piece not in output for piece in required):
        raise AssertionError("Observed output did not contain expected Hindi tokens")
    if punctuation not in output:
        raise AssertionError("Original punctuation was not preserved")


def screenshot(page, name: str) -> None:
    try:
        page.screenshot(path=str(EVIDENCE / name), full_page=True, timeout=12000)
    except Exception as exc:
        print("PUBLIC_QA_SCREENSHOT_FAILED", type(exc).__name__, flush=True)


def wait_for_app_control(page, timeout_seconds: int):
    """Return the actual Streamlit document (Cloud often uses an iframe)."""
    deadline = time.monotonic() + timeout_seconds
    last_error = ""
    while time.monotonic() < deadline:
        remaining_ms = max(500, int((deadline - time.monotonic()) * 1000))
        try:
            view = (
                page.frame_locator('iframe[title="streamlitApp"]')
                if page.locator('iframe[title="streamlitApp"]').count() else page
            )
            view.get_by_role("button", name=BUTTON).wait_for(
                state="visible", timeout=min(3500, remaining_ms)
            )
            print("PUBLIC_APP_CONTROL_CONTEXT " +
                  ("streamlit_iframe" if view is not page else "top_level"), flush=True)
            return view
        except (PlaywrightTimeout, RuntimeError) as exc:
            last_error = f"{type(exc).__name__}: {str(exc)[:200]}"
            time.sleep(1)
    raise TimeoutError(
        f"PUBLIC_CONTROL_TIMEOUT after {timeout_seconds}s; "
        f"last_playwright_error={last_error}"
    )


def snapshot(page, attempt: int, http_status: int | None, error: str | None) -> dict:
    try:
        body = page.locator("body").inner_text(timeout=5000)
    except Exception:
        body = ""
    try:
        buttons = [text.strip() for text in page.get_by_role("button").all_inner_texts(timeout=5000)]
    except Exception:
        buttons = []
    iframe_excerpt = ""
    iframe_buttons = []
    has_iframe = False
    try:
        has_iframe = bool(page.locator('iframe[title="streamlitApp"]').count())
        if has_iframe:
            inner = page.frame_locator('iframe[title="streamlitApp"]')
            iframe_excerpt = inner.locator("body").inner_text(timeout=5000)[:1500]
            iframe_buttons = inner.get_by_role("button").all_inner_texts(timeout=5000)[:20]
    except Exception as exc:
        iframe_excerpt = "unavailable: " + type(exc).__name__
    state = {
        "iframe_found": has_iframe,
        "iframe_button_labels": iframe_buttons,
        "iframe_body_excerpt": iframe_excerpt,
        "attempt": attempt,
        "http_status": http_status,
        "page_url": page.url,
        "page_title": "",
        "button_labels": buttons[:20],
        "body_excerpt": body[:1500],
        "error": error,
        "classification": classify_page(body, buttons, http_status),
    }
    try:
        state["page_title"] = page.title(timeout=3000)
    except Exception:
        pass
    return state


def convert(view, source: str, required: tuple[str, ...], punctuation: str,
            previous_output: str | None, max_seconds: int) -> tuple[str, float]:
    started = time.monotonic()
    area = view.locator('[data-testid="stTextArea"] textarea').first
    area.fill(source, timeout=15000)
    view.get_by_role("button", name=BUTTON).click(timeout=20000)
    success = view.get_by_text("Generated by IndicXlit", exact=True)
    failure = view.get_by_text("IndicXlit inference could not run.", exact=False)
    code = view.locator('[data-testid="stCode"]').first
    while time.monotonic() - started < max_seconds:
        if failure.count():
            raise RuntimeError("PUBLIC_INFERENCE_FAILED: Streamlit reported an actual inference error")
        if success.count() and code.count():
            output = code.inner_text(timeout=5000).strip()
            if output and output != previous_output:
                verify_output(source, output, required, punctuation)
                return output, round(time.monotonic() - started, 2)

        time.sleep(2)
    raise TimeoutError(f"PUBLIC_CONVERSION_TIMEOUT after {max_seconds}s; no verified fresh result")


def check() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    report = {
        "url": URL,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "test_type": "real_external_chromium_no_mocks",
        "verified": False,
        "attempts": [],
        "conversions": [],
        "failure": None,
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 900}, locale="en-IN")
        context.tracing.start(screenshots=True, snapshots=True)
        page = None
        try:
            for attempt in range(1, 5):
                if page is not None:
                    page.close()
                page = context.new_page()
                js_errors = []
                page.on("pageerror", lambda error: js_errors.append(str(error)[:350]))
                status = None
                error = None
                print(f"PUBLIC_APP_ATTEMPT {attempt}/4", flush=True)
                try:
                    response = page.goto(URL, wait_until="domcontentloaded", timeout=45000)
                    status = response.status if response else None
                    # Cloud embeds the actual Streamlit app in a child iframe.
                    # The sleeping outer wrapper must be woken first.
                    try:
                        view = wait_for_app_control(page, 12)
                    except TimeoutError:
                        wake = page.get_by_text("Yes, get this app back up!", exact=False)
                        if wake.count():
                            screenshot(page, f"provider-asleep-{attempt}.png")
                            print(
                                f"PUBLIC_STREAMLIT_ASLEEP attempt={attempt} requesting_wake",
                                flush=True,
                            )
                            wake.first.click(timeout=20000)
                            report["wake_requested"] = True
                            view = wait_for_app_control(page, 240)
                            print(
                                f"PUBLIC_STREAMLIT_WAKE_SUCCEEDED attempt={attempt}",
                                flush=True,
                            )
                        else:
                            view = wait_for_app_control(page, 70)
                    report["attempts"].append({
                        "attempt": attempt, "http_status": status,
                        "classification": "conversion_control_visible",
                        "page_url": page.url,
                    })
                    screenshot(page, "public-ready.png")
                    print(f"PUBLIC_UI_READY attempt={attempt} http={status}", flush=True)
                    break
                except Exception as exc:
                    error = f"{type(exc).__name__}: {str(exc)[:300]}"
                    entry = snapshot(page, attempt, status, error)
                    entry["javascript_errors"] = js_errors[:10]
                    report["attempts"].append(entry)
                    screenshot(page, f"attempt-{attempt}.png")
                    print("PUBLIC_UI_UNAVAILABLE " + json.dumps(entry, ensure_ascii=False), flush=True)
                    if attempt == 4:
                        raise RuntimeError("PUBLIC_UI_BLOCKED category=" + entry["classification"]) from exc
                    time.sleep(20)
            assert page is not None
            prior = None
            for index, (source, required, punct) in enumerate(CASES, 1):
                try:
                    output, elapsed = convert(
                        view, source, required, punct, prior,
                        max_seconds=900 if index == 1 else 240,
                    )
                except Exception:
                    screenshot(page, f"conversion-{index}-failed.png")
                    raise
                prior = output
                record = {"case": index, "input": source, "output": output,
                          "duration_seconds": elapsed, "punctuation_preserved": True}
                report["conversions"].append(record)
                screenshot(page, f"conversion-{index}.png")
                print("PUBLIC_INDICXLIT_CONVERSION_PASS " +
                      json.dumps(record, ensure_ascii=False), flush=True)
            report["verified"] = True
            print("PUBLIC_INDICXLIT_3_CASE_EXTERNAL_BROWSER_PASS", flush=True)
        except Exception as exc:
            report["failure"] = f"{type(exc).__name__}: {str(exc)[:600]}"
            print("PUBLIC_QA_FAILED " + report["failure"], flush=True)
            raise
        finally:
            (EVIDENCE / "diagnostics.json").write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            try:
                context.tracing.stop(path=str(EVIDENCE / "browser-trace.zip") if not report["verified"] else None)
            finally:
                context.close()
                browser.close()


if __name__ == "__main__":
    check()
