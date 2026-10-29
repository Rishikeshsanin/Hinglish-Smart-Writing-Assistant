"""Live Chromium QA of actual IndicXlit + independent OPUS-MT translation."""

from pathlib import Path
import json
import re
from playwright.sync_api import sync_playwright, expect

OUTPUT=Path("screenshots")
OUTPUT.mkdir(exist_ok=True)
with sync_playwright() as play:
    browser=play.chromium.launch(headless=True,args=["--no-sandbox"])
    page=browser.new_page(viewport={"width":1440,"height":900})
    page.goto("http://127.0.0.1:8501",wait_until="domcontentloaded",timeout=30000)
    source=page.locator("textarea").first
    expect(source).to_be_visible(timeout=45000)
    source.fill("kal mujhe college jana hai!")
    source.press("Tab")
    page.get_by_role("button",name=re.compile("Convert to Hindi")).click()
    hindi_result=page.locator("[data-testid='stCode']").filter(has_text="कल मुझे कॉलेज जाना है!").first
    expect(hindi_result).to_be_visible(timeout=180000)
    # Poorly performing experimental Hindi model must never be offered as normal.
    grammar=page.get_by_role("button",name="Improve Hindi grammar (research)")
    expect(grammar).to_be_disabled()
    page.get_by_role("button",name="Translate to English").click()
    try:
        expect(page.get_by_text("English output — Helsinki-NLP OPUS-MT, not IndicTrans2")).to_be_visible(timeout=180000)
        english=page.locator("[data-testid='stCode'] code").last
        expect(english).to_be_visible(timeout=30000)
        observed=english.inner_text().strip()
        assert observed and re.search(r"[A-Za-z]",observed), f"No English model output: {observed!r}"
        print("OPUS_BROWSER_OUTPUT",observed,flush=True)
    except AssertionError:
        print("PAGE_DEBUG_START", flush=True)
        print(page.locator("body").inner_text()[-7000:], flush=True)
        print("PAGE_DEBUG_END", flush=True)
        page.screenshot(path=str(OUTPUT/"translation-debug.png"),full_page=True)
        raise
    page.screenshot(path=str(OUTPUT/"actual-english-translation.png"),full_page=True)
    page.get_by_role("button",name="Clear",exact=True).click()
    expect(source).to_have_value("")
    print("REAL_OPTIONAL_TRANSLATION_BROWSER_TEST_PASSED",flush=True)
    browser.close()
