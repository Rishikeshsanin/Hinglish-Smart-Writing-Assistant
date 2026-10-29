# IndicWrite — Hinglish Smart Writing Assistant

**CS3235 · Working with LLMs · CIE3 Lab · RV University**

**Student:** Munnaluri Rishikesh · **USN:** 1RVU23CSE291

Convert Roman-script Hindi to Devanagari using **AI4Bharat IndicXlit**, with an interactive Streamlit interface. This is an academic application under active development, not a claim that all proposed features are complete.

## Current features

- Real-model IndicXlit wrapper via the official `ai4bharat-transliteration` Python package (no hardcoded generated results).
- Roman Hindi → Hindi script, preserving spaces, punctuation, digits, existing Devanagari, and explicitly preserved English terms.
- Streamlit UI with sample inputs, validation, comparison, and copyable output.
- 40 offline tests, clearly separate from executable real-model smoke tests.

**Model execution status:** VERIFIED on Ubuntu 22.04 / Python 3.10 in [genuine IndicXlit smoke run #40870311669](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40870311669), with official downloaded neural weights. Unit tests remain distinct from real inference.

**Optional-model evidence:** OPUS-MT Hindi→English ran successfully on two smoke cases. Four separate Hindi rewrite candidates were genuinely executed but failed the quality gate: one produced mixed-script output, one corrected only 1/5 cases, Qwen2.5-0.5B corrected 2/5 with severe drift elsewhere, and Qwen3-0.6B corrected 0/5. Grammar rewriting therefore remains disabled by default. A pinned BharatGen adapter and 12-case evaluation protocol exist, but no genuine BharatGen output has been recorded. IndicTrans2 remains an investigated, gated path rather than an executed feature.

## Quick start (Windows / PowerShell)

Install Python 3.10 (not the system Python 3.14) and create an isolated environment:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
$env:PYTHONPATH="src"
python scripts/smoke_indicxlit.py
streamlit run app.py
```

> **Compatibility warning:** the official IndicXlit Python package (1.1.3, published in 2022) pulls in legacy `fairseq` and other dependencies. On Windows, installation may require WSL2 Ubuntu or a Linux cloud environment. If dependency resolution fails, record the exact error; do not substitute fake conversion. CPU model loading may download files and take time.

On Linux/macOS use:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
PYTHONPATH=src python scripts/smoke_indicxlit.py
PYTHONPATH=src streamlit run app.py
```

### Tests (no network or model required)

```bash
python -m pip install pytest
PYTHONPATH=src python -m pytest -q
```

The tests use a controlled **stub** to verify text handling; the smoke script is the required genuine-model check.

## Architecture

```text
Roman-Hindi input → validation / tokenization → IndicXlit XlitEngine (hi)
                 → Devanagari text → side-by-side Streamlit output
```

The engine loads once per Python process. Roman tokens are sent individually to `XlitEngine.translit_word(..., topk=1)`; existing non-Roman characters, punctuation, and digit tokens are preserved. Users can list explicit English words that must remain unchanged. Automatic language identification is **not** implemented, and ambiguous Hinglish words may be transliterated incorrectly.

## References & attribution

- [AI4Bharat IndicXlit official repository](https://github.com/AI4Bharat/IndicXlit) (MIT)
- [Official Python API](https://github.com/AI4Bharat/IndicXlit/tree/master/app)
- [PyPI ai4bharat-transliteration 1.1.3](https://pypi.org/project/ai4bharat-transliteration/)
- [Aksharantar dataset](https://huggingface.co/datasets/ai4bharat/Aksharantar)
- [BharatGen Param-1-2.9B-Instruct](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct) — **experimental adapter; real inference not yet executed**
- [AI4Bharat IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) — **feasibility investigated; gated checkpoint not executed**

## Faculty deliverables tracker

- [x] Source structure and initial application
- [x] Stubbed text-handling tests and real-model smoke-test script
- [x] Successful genuine IndicXlit inference with captured logs
- [x] 40 real-model cases, recorded predictions and error analysis (macro CER 5.58%, word accuracy 82.67%; handcrafted test set)
- [ ] Verified smart rewriting and optional translation (if feasible)
- [x] Actual Chromium desktop/mobile screenshots and browser QA
- [x] Academic PDF report, generated from measured evidence and actual screenshots

**Due:** November 6, 2026 at 10:00 AM IST.

## Evidence links (executed, not simulated)

- [Real model smoke run](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40870311669)
- [Real IndicXlit → OPUS-MT browser run](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40879090261)
- [40-case evaluated predictions](evaluation/results/predictions.csv) · [Metrics](evaluation/results/metrics.json) · [Failure examples](evaluation/results/worst_cases.csv)
- [Real desktop screenshot](screenshots/desktop.png) · [Real mobile screenshot](screenshots/mobile.png) · [Browser QA trace](screenshots/browser-qa.json)

**Observed custom dataset metrics:** 40 test cases; macro CER 5.58%; macro word accuracy 82.67%; exact-match rate 55%. These figures are not official Aksharantar benchmark results. The worst category was spelling variation (49.33% mean word accuracy).

## Faculty report

- [Download the committed academic report (PDF)](reports/IndicWrite_CS3235_Project_Report.pdf)
- [Read the academic report source](docs/REPORT.md)
- [Reproducible report renderer](scripts/build_faculty_report.py)
- [Report generation CI](.github/workflows/report.yml)

**Scope disclosure:** The genuine transliteration MVP, evaluation, and browser QA are complete. BharatGen rewriting and optional IndicTrans2 translation are not verified or integrated. This is not a claim that the entire original multi-model project is finished.


## Additional real-model findings (October 29, 2026)

The optional language-service models can be installed with `python -m pip install -r requirements-language-services.txt`.
Run `INDICWRITE_ENABLE_LANGUAGE_SERVICES=1 PYTHONPATH=src streamlit run app.py` to expose the separately attributed **Helsinki-NLP OPUS-MT Hindi-to-English** model. It is *not* IndicTrans2. The public Apache-2.0 checkpoint produced two coherent actual translations on GitHub Actions run [40876423545](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40876423545).

**Grammar is intentionally disabled by default**, including in the optional environment. Two genuine MIT Hindi mT5 checkpoints failed quality review. Apache-2.0 Qwen2.5-0.5B and Qwen3-0.6B experiments scored 2/5 and 0/5 exact corrections respectively, with meaning loss or language drift. For controlled research only, set `INDICWRITE_ENABLE_GEC_EXPERIMENTAL=1`; outputs are checked for script drift and exact numeral preservation but still require human scrutiny. None of these models is BharatGen.

The BharatGen repository history contains a restrictive Research License even though the live metadata currently advertises Apache-2.0 and the license file has changed. Public output/hosting therefore remains blocked pending written clarification. We do not publicly host it or claim to have executed it. The original 40-case IndicXlit evaluation remains unchanged and is not a grammar accuracy measure.
