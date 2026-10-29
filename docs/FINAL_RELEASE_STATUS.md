# IndicWrite — Final verified release and faculty submission status

**As of 29 October 2026** · Student: **Munnaluri Rishikesh**, USN **1RVU23CSE291** · CS3235 CIE3, RV University · **Due 6 Nov 2026, 10:00 AM IST**.

## Final repository verification — 29 October 2026

The most recent completed offline CI run [40906533392](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40906533392) passed **93 tests with 8 optional skips**. The academic report was rebuilt successfully in [40906533300](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40906533300). The faculty ZIP workflow now independently checks every file against the SHA-256 manifest and rejects unsafe paths, model weights, credentials or private BharatGen outputs. [PR #15](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/pull/15) additionally verified the actual Docker Compose loopback service health, beyond the prior raw-image check.

**Private BharatGen runtime separation:** [PR #16](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/pull/16) adds a standalone Python3.12 local-only research interface, isolated from the tested Python3.10 IndicXlit runtime. Its real Streamlit widgets were tested **with fake inference only**. [PR #17](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/pull/17) supplies an opt-in private Colab T4 browser-QA notebook, **not yet executed**. [PR #18](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/pull/18) supplies a gitignored 10-case human-review CSV and aggregate-only scorer; an independent reviewer has **not yet completed** those ratings.

**External gate:** no public BharatGen hosting/output permission; no safe supported-runtime internet deployment; no Google Classroom submission. Private pinned BharatGen checkpoint inference of 11 generations was separately and genuinely verified in the earlier T4 evidence ZIP. A ready-to-review Gmail licensing inquiry is saved as a draft and **not sent**.

## Executed and verified

| Component | Actual evidence |
| --- | --- |
| AI4Bharat IndicXlit | Genuine pretrained model in Ubuntu/Python 3.10; recorded three-case smoke, official package and checkpoint |
| Transliteration evaluation | Forty genuine saved predictions; authored-test mean CER **5.58%**, mean word accuracy **82.67%**, exact sentence match **22/40** |
| Browser UI | Chromium desktop/mobile real-model conversion, Clear, UTF-8 TXT download and overflow checks passed (run 40891608196) |
| OPUS-MT translation | Separately attributed genuine Helsinki-NLP Hindi-to-English, not IndicTrans2; browser integration verified earlier |
| BharatGen private GPU research | Real pinned official Param-1-2.9B-Instruct on authorized Colab Tesla T4, Python 3.12/Transformers 4.56.2, FP16, **1 smoke + 10 registered generations** with correct EOS and no truncation; peak PyTorch allocated **~6.31 GiB** |
| Academic report | Rebuilt from actual metrics and screenshots, including the private BharatGen runtime summary, without publishing model outputs |
| Source and faculty ZIP | GitHub code, report, datasets and SHA-256 manifest, with no model weights, secrets or private generated outputs |

## Scope/limits that must remain visible

- **BharatGen quality is preliminary:** assistant non-expert editorial review found nine of ten cases acceptable or appropriately unchanged, one technical-term fidelity and grammar problem. This is **not independent human linguistic assessment**, nor broad rewrite accuracy.
- **BharatGen license:** research-license history and conflicting public model metadata require explicit clarification/approval before public dissemination of weights/generated outputs or model hosting. Raw private model output ZIP is deliberately not committed.
- **Private candidate UI:** exists behind explicit opt-ins and a loopback-only bind requirement; no real T4 Streamlit browser E2E has been performed. It never auto-applies edits and warns about changed numbers/English terms.
- **IndicTrans2:** official gated checkpoint was not accessed; independently attributed Helsinki OPUS-MT is the optional verified translation path.
- **Public deployment:** no reachable URL verified; Python 3.11 legacy Fairseq/Hydra compatibility experiment in archived PR #11 failed genuine model startup. Ubuntu/WSL2 Python 3.10 local demo remains the proven path.
- **Google Classroom submission:** not performed; requires student-controlled Classroom account and a final check of the faculty requirements.

## Where to verify

- [GitHub repository](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant)
- [Release coordinator issue #1](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/issues/1)
- [Research issue #2](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/issues/2)
- [Model smoke](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40870311669)
- [Genuine 40-case evaluation](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40870722731)
- [Latest updated browser QA](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40891608196)
- [Faculty report](../reports/IndicWrite_CS3235_Project_Report.pdf)
- [Faculty submission ZIP workflow](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/workflows/submission-package.yml)

**Academic integrity:** submit only the demonstrated features and explicitly describe the remaining limitations. This is a completed and demonstrable transliteration application with substantial, genuine Indian-language model research, not a verified public BharatGen writing service.


## Final safe hosting decision (2026-10-29)

The official AI4Bharat model was successfully exercised inside an isolated local-only Docker image ([run 40898600397](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40898600397)), including container build, pretrained smoke, and Streamlit localhost health. The private-GPU BharatGen UI still lacks real end-to-end browser testing and must not be served publicly pending license authorization.

Public deployment is explicitly **blocked** rather than silently degraded. On Python3.12, a third-party CT2 IndicXlit conversion had 40-case mean CER 11.54% vs official 5.58%; word accuracy 67.83% vs 82.67%; exact reference matches 6/40 vs 22/40. It was rejected, and experimental PR #13 closed without merge. Python3.11/Fairseq experimental PR #11 was also closed after authentic startup failure. Python3.10 is EOL; do not host this exact legacy runtime on an internet-facing free Streamlit service.


## Final technical handoff — protected research environments

- **Normal IndicWrite:** official AI4Bharat IndicXlit in isolated Python3.10 or local-only Docker, real browser smoke passed. This uses no BharatGen checkpoint and never silently substitutes a lower-quality third-party model.
- **Private rewriting study:** independent Python3.12/T4 Streamlit app, protected by all three opt-in flags and localhost binding, handles Hindi directly. Real pretrained BharatGen checkpoint inference previously succeeded in 11 private Colab generations; the **new UI widget tests use fake inference**, and **full real-GPU browser UI QA remains not executed**.
- **Independent human-language review:** a private 10-case reviewer rubric and aggregate-only scoring script are prepared; no independently scored quality result is claimed.
- **Release reproducibility:** the ZIP archive verifier now checks per-file SHA-256, required evidence and exclusion of unsafe/private content; Docker Compose loopback health has passed.
- **External blockers:** public BharatGen approval, supported-runtime public deployment, optional gated IndicTrans2 access, private GPU UI execution and faculty Google Classroom upload remain outstanding.
