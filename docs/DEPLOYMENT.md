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
python -m pip install -r requirements-local.txt
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
remote-code review, disk/RAM, and licensing permit. It is disabled by default in the baseline Streamlit app; **pretrained inference subsequently ran successfully** in a private T4 Colab experiment (1 smoke + 10 cases). Public hosting remains blocked pending licensing clarification. The model card advertises
an early instruct checkpoint whose outputs may be unreliable.

Use a separate Python 3.12 environment and `requirements-bharatgen.txt`.
The pinned stack passed CPU tokenizer/tiny-random-architecture checks only;
Pretrained CUDA FP16 inference is now verified privately on Colab T4 (11 genuine generations, ~6.31 GiB peak allocated GPU memory). Follow
`notebooks/BharatGen_Real_Smoke_Colab.ipynb` for the GPU experiment and preserve
JSONL logs. The default device is CUDA with no automatic CPU offload. Explicit
`--device cpu` uses FP32 and requires over 10.66 GiB for weights alone.
Remote-code hashes and a fixed model revision identify reviewed code; they do
not sandbox it. Do not add this optional environment to baseline deployment.

The optional IndicTrans2 Hindi→English checkpoint is also not a deployment
dependency. Its Hugging Face files are gated behind user acceptance/contact
sharing; no token may be committed or added to application configuration.


## Verified local container and public-hosting decision (29 October 2026)

A new **local-only** container is defined in [Dockerfile.demo](../Dockerfile.demo) and [compose.demo.yml](../compose.demo.yml). CI [run 40898600397](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40898600397) successfully built the image, executed the genuine official pretrained IndicXlit smoke, and verified local Streamlit health. It binds to **127.0.0.1:8501** on the host and disables all private BharatGen and optional language-service flags. No other databases or services were modified.

**Do not publish the image as an internet-facing service.** Python 3.10 reached upstream end of life on 1 October 2026, and Streamlit Community Cloud only supports Python versions receiving security updates. The native 3.11 Fairseq compatibility experiment failed with OmegaConf/Hydra errors (archived PR #11). A third-party MIT CTranslate2 conversion was actually tested on Python 3.12 (closed PR #13, [run 40898008792](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40898008792)), but its 40-case quality was **worse**: 11.54% CER / 67.83% word accuracy / 6 exact matches compared with official 5.58% / 82.67% / 22 exact. It is not integrated or presented as the official runtime.

Until a **supported, equivalently accurate runtime** and account-authorized hosting are verified, the correct submission path is the well-tested localhost demo. Do not silently swap in an inferior model, open paid infrastructure, or claim a public URL.


## Supported Python 3.12 deployment update — October 31, 2026

The earlier Python3.10-only limitations above are historical. A newly verified **opt-in compatibility layer** from pinned ShunyaLabs `codemix-restore-shunyalabs==0.4.0` allows the **original official IndicXlit checkpoint** to run on Python3.12 with **40/40 exact historical parity**, proven in [run 41210696882](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41210696882). The exact `environment.yml` Conda specification for Streamlit Community Cloud passed real inference plus forty-case parity in [run 41211428287](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41211428287). A separate Python3.12 `Dockerfile.cloud` built, ran official pretrained inference and passed local Streamlit health in [run 41211613516](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41211613516).

**Preferred $0 provider:** Streamlit Community Cloud, app `cloud_app.py`, Python3.12, repo `Rishikeshsanin/Hinglish-Smart-Writing-Assistant`, branch `main`; no secrets or billing. The provider supports GitHub-connected free apps and checks `environment.yml` before `requirements.txt` in the same directory. The actual cloud app is still **NOT deployed** until account-owner GitHub login and Create App are completed. Verify externally before sharing any URL. The older Py3.10 `Dockerfile.demo` must remain local-only, and private BharatGen remains disabled.
