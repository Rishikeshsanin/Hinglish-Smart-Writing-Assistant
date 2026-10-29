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

Do **not** deploy BharatGen from this repository. Its Hugging Face license
metadata and repository license history are inconsistent, and the historical
BharatGen Research License requires written permission for a hosted service,
even when free. A public rewriting deployment is blocked until the owner gives
written clarification/permission and genuine inference passes quality review.

If hosting is attempted, create only a **new, isolated** service pointing at
this repository. Do not reuse or modify any other applications, databases, or
GitHub configuration. Never select paid tiers without explicit cost approval.
Record exact deployment URL, platform, Git SHA, real conversion and health
checks in the release ticket. Otherwise submit a verified local/WSL2 demo
without claiming a public deployment.

## Experimental rewrite

`python scripts/smoke_bharatgen.py --allow-model-download --allow-remote-code` runs the optional
genuine adapter **only when explicitly requested** and when checkpoint access,
remote-code review, disk/RAM, and licensing permit. It is not enabled in the
baseline Streamlit app; it has not yet been exercised. The model card advertises
an early instruct checkpoint whose outputs may be unreliable.

Use a separate Python 3.12 environment and `requirements-bharatgen.txt`.
The pinned stack passed CPU tokenizer/tiny-random-architecture checks only;
pretrained inference and CUDA are unverified. Follow
`notebooks/BharatGen_Real_Smoke_Colab.ipynb` for the GPU experiment and preserve
JSONL logs. The default device is CUDA with no automatic CPU offload. Explicit
`--device cpu` uses FP32 and requires over 10.66 GiB for weights alone.
Remote-code hashes and a fixed model revision identify reviewed code; they do
not sandbox it. Do not add this optional environment to baseline deployment.

The optional IndicTrans2 Hindi→English checkpoint is also not a deployment
dependency. Its Hugging Face files are gated behind user acceptance/contact
sharing; no token may be committed or added to application configuration.
