# IndicWrite supported public release — independent evidence (5 November 2026)

## Product boundary and release state

IndicWrite has one authoritative free public AI converter:
<https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/>.
It uses the genuine original AI4Bharat IndicXlit Hindi checkpoint, not a
hardcoded dictionary or an unrelated hosted API. The premium Vercel public URL
<https://indicwrite-public-web.vercel.app/> is a gateway into that app;
it does not perform inference or advertise a second AI model.

**Core IndicXlit product: publicly functional and independently tested.**
This is **not** a claim of 24/7 uptime, full WCAG conformance, or a completed
multi-model Hindi rewriting product. Optional translation is local opt-in;
other experimental models remain disabled until their external gates clear.

## Recorded commits and tests

- Original 40-case dataset and genuine-model `predictions.csv` retained exactly.
  Historical model metrics: macro character-error rate 5.58%, mean clipped
  word accuracy 82.67%, exact-match rate 55% on the authored test set;
  these are not official Aksharantar benchmark results.
- Agent A reliability [PR #37](../pull/37), Agent B premium Streamlit + gateway
  [PR #38](../pull/38), Agent C safe features [PR #40](../pull/40),
  dependency fix [PR #41](../pull/41) merged before final QA.
- Integrated QA [PR #42](../pull/42) merged into `main` at
  `3567aa1b9f36b91db0030626856d0b3f6d769606`.
- Pull-request [real external Chromium run 42071288867](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/42071288867):
  **PASS**; 154 offline tests passed, 8 skipped; ten distinct real Hindi
  sentences and one protected English/URL/Unicode mixed case passed in the
  actual public native app.
- **Separate post-merge main verification:**
  [run 42073053397](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/42073053397)
  **PASS** on exact checkout SHA
  `3567aa1b9f36b91db0030626856d0b3f6d769606`.
  Actual external public Chromium output was logged, not mocked.
  The run includes screenshots and `browser-evidence.json` in
  `product-acceptance-public-browser`, artifact 13436298212.
  Offline unit + acceptance workflows each recorded **154 passed, 8 skipped**.

### Final merged-main Chromium evidence (run 42073053397)

| Public check | Recorded status |
| --- | --- |
| 10 distinct Roman-Hindi sentences | PASS (11 conversions incl. mixed case) |
| Real model success banner and Hindi output | PASS |
| Protected Python, uppercase AI, 42, HTTPS URL, existing Hindi, emoji | PASS |
| Blank and unsupported preserve-term errors | PASS |
| Original UTF-8 TXT download | PASS |
| Manual Hindi editor and reviewed UTF-8 TXT download | PASS |
| Browser clipboard copy | PASS |
| Native mobile/tablet/desktop (320, 390, 768, 1440 px) | PASS: no document overflow |
| Basic keyboard focus / Streamlit accessible controls | PASS |
| Clear stale output; JavaScript errors | PASS; none recorded |
| Public BharatGen/failed grammar feature disabled | PASS |
| Optional OPUS in free public hosting | Disabled as intended |
| Long-term uptime, memory, throughput, cold post-sleep resource stress | Not certified |
| Full screen-reader audit, WCAG contrast audit | Not certified |

Observed **external wall-clock** first UI availability was 7.07 seconds,
first conversion 7.02 seconds in this test session, and subsequent mixed-case
conversion 1.85 seconds. These are not model-only inference timings, a
controlled cold-install benchmark, or an uptime SLA.

### Genuine IndicXlit limitations observed in public output

These were NOT silently corrected, simulated, or replaced:
- `main ghar ja raha hoon.` → `मैन घर जा रहा हूँ.` ("main" ambiguity)
- `aaj mausam bahut accha hai!` → `आज मौसम बहुत अच्छ है!`
- `ap kahan ho?` → `एपी कहन हो?`
- `kal mujhe college jana hai!` → `कल मुझे कॉलेज जाना है!` (correct sample)

User-controlled English preservation and manual review are the honest
mitigations. No claim of automatic grammar correction or perfect semantics
is supported.

## Vercel web gateway and retired legacy route

After the full app became publicly usable, the Vercel frontend was retained
only as a polished landing page with a labelled CTA to the real Streamlit app.
The old `/api/transliterate` hosted-service endpoint is intentionally retired
with HTTP 410, an explicit canonical link, no wildcard CORS and no outbound
AI4Bharat call. New free Chromium acceptance in
`.github/workflows/vercel-gateway-live.yml` checks the actual existing
Vercel URL, real CTA navigation, mobile layout, keyboard skip-link, browser
errors and screenshots separately from actual Streamlit inference.

Vercel production build state and link testing must both be checked after
the gateway-hardening merge. READY alone is not evidence that a browser
can reach or navigate the site.

## AI capability matrix and external blockers

| Model/feature | What is genuinely demonstrated | Public release |
| --- | --- | --- |
| Original official AI4Bharat IndicXlit | Genuine weights, 40 recorded predictions, Python3.12 parity and public Chromium | **Enabled in Streamlit** |
| Helsinki-NLP OPUS-MT Hindi→English | Real prior model smoke/browser, separate from IndicTrans2; revised Python dependencies tested | **Off on free public host**; local opt-in only |
| Automatic Hindi grammar correction | Actual mT5/Qwen research trials showed wrong script or lost meaning | **Disabled** |
| BharatGen Param-1 research | Pinned genuine T4 private model inference: smoke + 10 frozen cases | **Private research only**; no raw outputs/public hosting without permission |
| Official IndicTrans2 | Gated checkpoint not accessed/executed | **Disabled** pending user-authorized gate acceptance and evaluation |

No private model outputs, weights, credentials or external project state are
contained in this release. The legal status of BharatGen public output is
unresolved; do not infer permission from inconsistent metadata. No external
model account terms were bypassed.

## What this document does and does not certify

The core production IndicWrite conversion flow has independently passed at the
release-candidate and merged-main commit levels. The separate Vercel landing
page requires its own public acceptance result after the final gateway changes.

No public release claim is made for advanced automatic rewriting, BharatGen,
or IndicTrans2. Full WCAG/accessibility certification, a multi-day uptime
measurement, authenticated faculty submission, and human bilingual quality
scoring of optional research models are also **not claimed**.
