# IndicWrite web edition — canonical native app gateway

The free Vercel web build is now an accessible, responsive **landing page** that directs users to the existing [IndicWrite native Streamlit app](https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/).

## Why it no longer converts text on Vercel

The previous `web/public/app.js` made requests to `web/api/transliterate.js`, which depends on an external hosted AI4Bharat endpoint that has not been reliable in public browser verification. A successful Vercel build is **not** evidence of successful real-model conversion. The proxy file remains untouched for coordinator review but is **not called by the page**.

The **only canonical conversion UI** is `app.py`, launched through the existing `cloud_app.py` deployment. Its calls flow through `src/indicwrite/core.py` and `src/indicwrite/engine.py` to the official pretrained AI4Bharat IndicXlit checkpoint. No mock text, alternative model, API key, open CORS proxy, or new hosting service is introduced.

## User experience

- Responsive keyboard-accessible landing page at 320, 390, 768 and desktop widths.
- A labelled link opens the existing native app, including its protected-English terms, examples, real output, human-only review editor, copy, and UTF-8 downloads.
- Honest first-load warning; no promise of public uptime or unverified model results.
- Private BharatGen output and research-only features never appear on the public page.

## Tests

`cd web && npm test` validates the old proxy **with mocked upstream responses** and the new static landing-page contract. A mock proxy test is not evidence that the provider is available. For a **real** native-model Chromium flow, follow `scripts/browser_smoke.py` and the existing `browser-qa.yml` workflow, which must be run in an environment with official neural weights. No production deployment is triggered by this branch or a draft PR.
