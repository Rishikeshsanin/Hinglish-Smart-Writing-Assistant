# IndicWrite — Final verified release and faculty submission status

**As of 29 October 2026** · Student: **Munnaluri Rishikesh**, USN **1RVU23CSE291** · CS3235 CIE3, RV University · **Due 6 Nov 2026, 10:00 AM IST**.

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
- **Public deployment:** no reachable URL verified; Python 3.11 legacy Fairseq/Hydra compatibility experiment in draft PR #11 failed genuine model startup. Ubuntu/WSL2 Python 3.10 local demo remains the proven path.
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
