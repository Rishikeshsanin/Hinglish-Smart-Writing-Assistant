# IndicWrite — independent product QA and release gate (Agent D / issue #36)

**Audit timestamp:** 2026-11-05 UTC. **Source audited:** `main` at
[`4b9e2aeeb6d79bca5d08be26543b997084a885d7`](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/commit/4b9e2aeeb6d79bca5d08be26543b997084a885d7).
**Independent QA change branch:** `qa/issue-36-product-release-gates-20261105`.
**Current independent release verdict: BLOCKED / NOT CERTIFIED LIVE.**

This is a release-control record, not a claim that all checks passed. Keep
`AGENTS.md`, original official AI4Bharat IndicXlit, the 40-case predictions,
the existing Streamlit URL, and private BharatGen assets unchanged. Agent D
owns only this document, `tests/test_product_acceptance.py`,
`scripts/qa_product_release.py`, and
`.github/workflows/product-acceptance.yml`.

## Evidence levels (do not conflate)

1. **Recorded genuine pretrained inference:** historical official IndicXlit
   [smoke run 40870311669](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40870311669);
   [40-case predictions](../evaluation/results/predictions.csv);
   [local actual model Chromium run 41414939084](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41414939084).
   Offline tests in this QA PR use an explicitly labelled **stub**, not this checkpoint.
2. **Public human observation, not independent uptime certification:** the
   dated [deployment-evidence note](FINAL_DEPLOYMENT_EVIDENCE_2026-11-05.md)
   records the student's 2 Nov public Streamlit screenshot showing
   `kal muje college jana hai` -> `कल मुझे कॉलेज जाना है`.
3. **Most recent independent external production test: FAILED.**
   [Public Chromium run 41414939039](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41414939039)
   (attempt 3, updated 2026-11-05 15:10 UTC) did not reach the visible
   `Convert to Hindi` control after retrying. This does not disprove the
   human screenshot, but it **blocks a reliability/live release verdict**.
4. **The Vercel frontend is separate:** a READY build of
   `https://indicwrite-public-web.vercel.app/` does not prove official model
   inference. Its external API dependency is unavailable/unverified; test
   canonical native Streamlit conversion instead.
5. **Agent A/B/C work:** issues [#33](../issues/33), [#34](../issues/34),
   [#35](../issues/35) are independent. At initial audit, their new integrated
   PRs were absent; do not certify their code until submitted, inspected,
   merged by the coordinator, and tested against a new exact `main` SHA.

## Acceptance matrix

| Gate | Required verification | Audit state (5 Nov baseline) |
| --- | --- | --- |
| Official IndicXlit provenance | Model import + real checkpoint smoke and pinned 40-case evidence, not canned answers | **Recorded historical PASS**; new A integration pending |
| Ten representative Roman Hindi cases | Ten genuine Chromium public conversions; output saved with target/commit/time | **PENDING**; offline ten-case stub contract is NOT model QA |
| English, URLs, numbers and Unicode | Protected `Python`, acronym `AI`, URL, `42`, emoji, existing Hindi survive genuine output | **PENDING live**; offline contract covered |
| Invalid input and safe failure | Blank/over-limit text, invalid protected token, model API error, no fake fallback | **PENDING integrated browser**; pure core contract covered |
| Copy and Unicode download | Clipboard equals actual result, UTF-8 result and edited `.txt` bytes round-trip | **PENDING live**; browser runner records failures distinctly |
| 320 / 390 / 768 / 1440 px | Accessible controls, no document horizontal overflow; screenshots tagged live/local | **PENDING** across integrated UI |
| Keyboard and basic accessibility | Roman input accessible name, Tab focus, labels, no hidden focus trap | **PENDING browser**; screen-reader, contrast and WCAG review still manual |
| Clear/edit/error recovery | Clear removes stale results, human edit is not auto rewrite; no JS exceptions | **PENDING browser** |
| Cold/warm load and resources | Real external load attempts, cold inference vs warm inference, server logs/uptime/CPU/RAM | **BLOCKED**: no healthy public reliability trace; remote memory not measured |
| Optional Helsinki OPUS translation | Only if enabled; genuine model and attributed real output; never claim IndicTrans2 | **Historically local verified**, public disabled by default |
| Grammar rewrites | Disabled unless human meaning/number/script review and adequate quality evidence | **BLOCKED for enablement**: prior candidates failed |
| BharatGen | Loopback-only research, explicit acknowledgement, license resolution, private evidence withheld | **BLOCKED for public release** |
| IndicTrans2 | Legal gated checkpoint access + real inference + quality checks before enabling | **BLOCKED** |
| Integration and CI | A/B/C PRs reviewed and merged; QA CI and official neural parity green on final head | **PENDING** |
| Full LIVE release | Fresh public native real conversion, repeatable public stability, all enabled AI safe | **BLOCKED** |

## Reproducible commands

Offline evidence (safe on GitHub Actions, no neural weights or service access):

```bash
python -m pip install pytest
python -m pytest -q tests/test_product_acceptance.py
python -m pytest -q
python scripts/qa_product_release.py --mode inventory --artifacts qa-artifacts
```

Local real Streamlit browser acceptance (only after starting an actual local
`streamlit run app.py` with **original** installed IndicXlit weights):

```bash
python -m pip install playwright==1.56.0
python -m playwright install --with-deps chromium
python scripts/qa_product_release.py --mode browser --target local \
  --url http://127.0.0.1:8501/
```

Public real Chromium smoke, always against the *existing* canonical Streamlit
URL and never against a mock proxy:

```bash
python scripts/qa_product_release.py --mode browser --target public
python scripts/qa_product_release.py --mode browser --target public --ten-cases
```

The second command performs the ten-case extended real browser set; only log
that matrix as passed if it actually runs successfully. CI uses
[`product-acceptance.yml`](../.github/workflows/product-acceptance.yml):
every relevant PR runs all offline tests, while **manual
`workflow_dispatch`** executes the isolated public Chromium suite and
uploads screenshots/JSON on success or failure. Workflow dispatch will become
available on the default branch after coordinator merge. GitHub Actions should
retain the exact run URL, commit SHA, screenshots and JSON artifact for review.

Optional release decision (requires separately assembled, evidence-backed
coordinator integration JSON, *not* screenshots alone):

```bash
python scripts/qa_product_release.py --mode gate \
  --evidence qa-artifacts/browser-evidence.json \
  --integration qa-artifacts/coordinator-integration.json
```

The integration JSON needs independently verifiable booleans for
`agents_a_b_c_merged_into_main`, `all_required_ci_green`,
`enabled_model_quality_and_license_review`, and
`production_stability_review`, **with linked supporting evidence provided
outside this tool**. Passing the programmatic gate means only
`READY_FOR_COORDINATOR_REVIEW` — the lead still approves deployment. Missing
evidence returns `BLOCKED` with exit code 2.

## Required final coordinator handoff

- Exact final `main` SHA, Agent A/B/C PR numbers, merge SHAs, integration
  review, branch and workflow run URLs.
- Evidence-separated counts: offline stubs, genuine checkpoint inference,
  local Chromium, **external production Chromium**, ten real public inputs.
- Observed public text, English/URL/Unicode preservation, UTF-8 download bytes,
  clipboard bytes, browser screenshots for each viewport, accessibility review.
- Cold/warm timing and **measured** server health, memory, uptime/retry rate;
  never infer these from a successful page load.
- Translation, grammar, BharatGen and IndicTrans2 enablement/quality/legal
  status with private information excluded from PR logs and screenshots.
- Severity-classified regression list with clear owners. Any unresolved P0/P1
  production, accessibility or meaning-loss issue blocks full release.

**Decision rule:** keep the academic genuine-IndicXlit MVP distinct from the
full proposed multi-model product. The final full product is not `LIVE` until
the actual public native Streamlit conversion and all enabled capabilities
pass independent QA on integrated production, with no P0/P1 regressions.
