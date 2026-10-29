# IndicWrite — Hinglish Smart Writing Assistant

**CS3235 · Working with LLMs · CIE3 Lab · RV University**

**Student:** Munnaluri Rishikesh · **USN:** 1RVU23CSE291

Convert Roman-script Hindi to Devanagari using **AI4Bharat IndicXlit**, with an interactive Streamlit interface. This is an academic application under active development, not a claim that all proposed features are complete.

## Current features

- Real-model IndicXlit wrapper via the official `ai4bharat-transliteration` Python package (no hardcoded generated results).
- Roman Hindi → Hindi script, preserving spaces, punctuation, digits, existing Devanagari, and explicitly preserved English terms.
- Streamlit UI with sample inputs, validation, comparison, and copyable output.
- Unit tests with a **fake engine**, clearly separate from an executable real-model smoke test.

**Model execution status:** Real AI4Bharat inference requires downloading the pretrained checkpoint on first use. Check `scripts/smoke_indicxlit.py` and GitHub Actions logs for an actual inference result. Unit tests passing **do not** establish model execution.

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
- [ ] Successful genuine IndicXlit inference with captured logs
- [ ] 40 evaluated representative cases and error analysis
- [ ] Verified smart rewriting and optional translation (if feasible)
- [ ] Actual running-app screenshots
- [ ] Academic PDF report

**Due:** November 6, 2026 at 10:00 AM IST.
