# IndicWrite — Hinglish Smart Writing Assistant

**CS3235 · Working with LLMs · CIE3 Lab · RV University**

**Student:** Munnaluri Rishikesh · **USN:** 1RVU23CSE291

Convert Roman-script Hindi to Devanagari using **AI4Bharat IndicXlit**, with an interactive Streamlit interface. This is an academic application under active development, not a claim that all proposed features are complete.

## Current features

- Real-model IndicXlit wrapper via the official `ai4bharat-transliteration` Python package (no hardcoded generated results).
- Roman Hindi → Hindi script, preserving spaces, punctuation, digits, existing Devanagari, and explicitly preserved English terms.
- Streamlit UI with sample inputs, validation, comparison, and copyable output.
- Unit tests with a **fake engine**, clearly separate from an executable real-model smoke test.

**Model execution status:** VERIFIED on Ubuntu 22.04 / Python 3.10 in [genuine IndicXlit smoke run #40870311669](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40870311669), with official downloaded neural weights. Unit tests remain distinct from real inference.

**Not yet integrated:** BharatGen Param-1 rewriting and IndicTrans2 translation. Neither is represented as available or executed.

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
- [BharatGen Param-1-2.9B-Instruct](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct) — **planned, not executed**
- [AI4Bharat IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) — **planned, not executed**

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
- [40-case evaluated predictions](evaluation/results/predictions.csv) · [Metrics](evaluation/results/metrics.json) · [Failure examples](evaluation/results/worst_cases.csv)
- [Real desktop screenshot](screenshots/desktop.png) · [Real mobile screenshot](screenshots/mobile.png) · [Browser QA trace](screenshots/browser-qa.json)

**Observed custom dataset metrics:** 40 test cases; macro CER 5.58%; macro word accuracy 82.67%; exact-match rate 55%. These figures are not official Aksharantar benchmark results. The worst category was spelling variation (49.33% mean word accuracy).

## Faculty report

- [Download the committed academic report (PDF)](reports/IndicWrite_CS3235_Project_Report.pdf)
- [Read the academic report source](docs/REPORT.md)
- [Reproducible report renderer](scripts/build_faculty_report.py)
- [Report generation CI](.github/workflows/report.yml)

**Scope disclosure:** The genuine transliteration MVP, evaluation, and browser QA are complete. BharatGen rewriting and optional IndicTrans2 translation are not yet integrated. This is not a claim that the entire original multi-model project is finished.
