# Local demonstration and deployment considerations

## Reproducible classroom demo

Use **Python 3.10** in an isolated environment on Linux/WSL2; the official
`ai4bharat-transliteration` pulls legacy Fairseq. Actual GitHub Actions run
[40870311669](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40870311669)
proves that Linux/Python 3.10 could load the official pretrained model and
produce genuine Hindi predictions.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install 'pip==23.3.2' 'setuptools<70' wheel
python -m pip install -r requirements.txt
python scripts/smoke_indicxlit.py
PYTHONPATH=src streamlit run app.py
```

Open the local Streamlit URL, type `kal mujhe college jana hai!`, convert,
inspect `कल मुझे कॉलेज जाना है!`, copy result, and clear. It is important to
demonstrate **actual inference**, not merely repeat output in the README.

## Hosting options

A public demo is **not verified**. Streamlit Community Cloud's published
memory resources are approximately 2.7 GB maximum and 2 CPUs; it may be
insufficient for modern PyTorch+legacy Fairseq, and BharatGen ~5.8GB raw bf16
weights certainly will not fit under that cap. Test actual peak RSS before
choosing a service.

If hosting is attempted, create only a **new, isolated** service pointing at
this repository. Do not reuse or modify any other applications, databases, or
GitHub configuration. Never select paid tiers without explicit cost approval.
Record exact deployment URL, platform, Git SHA, real conversion and health
checks in the release ticket. Otherwise submit a verified local/WSL2 demo
without claiming a public deployment.

## Experimental rewrite

`python scripts/smoke_bharatgen.py --allow-model-download` runs the optional
genuine adapter **only when explicitly requested** and when checkpoint access,
remote-code review, disk/RAM, and licensing permit. It is not enabled in the
baseline Streamlit app; it has not yet been exercised. The model card advertises
an early instruct checkpoint whose outputs may be unreliable.
