# Private BharatGen GPU interface — Python 3.12 only

This separate Streamlit interface solves a practical runtime mismatch:
official IndicXlit / legacy Fairseq is tested in **Python 3.10**,
whereas the **real pinned BharatGen model** passed GPU inference in **Python 3.12**.
Do not install both into one Python interpreter or claim the joined pipeline
has been browser-verified.

The standalone `research/private_bharatgen_app.py` accepts Devanagari Hindi
directly and runs the pinned model on a local T4 or compatible CUDA GPU.
The core `app.py` remains the regular Roman→Hindi converter and runs separately.

## Private setup

Use an isolated Python 3.12 environment with GPU-enabled PyTorch and the
reviewed pinned model source and checkpoint. Install:

```bash
python -m pip install -r requirements-private-research.txt
```

Review the [BharatGen Research License](https://huggingface.co/bharatgenai/Param-1-2.9B-Instruct/blob/13498f81c10fba9d716ea2969d00df3538c10ca7/LICENSE)
and the checked custom-code SHA-256 entries in
`src/indicwrite/param_rewrite.py`.

Explicitly set the three acknowledgment flags, then launch the app **only**
bound to localhost:

```bash
INDICWRITE_PRIVATE_BHARATGEN=1 \
INDICWRITE_REVIEWED_BHARATGEN_CODE=1 \
INDICWRITE_ACKNOWLEDGE_BHARATGEN_LICENSE=1 \
PYTHONPATH=src streamlit run research/private_bharatgen_app.py --server.address=127.0.0.1
```

Open http://127.0.0.1:8501. Paste Hindi directly; generate a proposal;
check the original sentence, warnings and facts; confirm your review before
downloading. **No auto-application, no public outputs, no hosting tunnel,
no database and no logging of original sentences.**

The dedicated [private UI test workflow](../.github/workflows/private-ui-contract.yml)
uses real Streamlit UI widgets with a **fake model** to check gate, interaction
and reset behavior. It cannot prove pretrained inference. The pretrained
checkpoint's actual T4 generation was previously verified privately on
eleven sentences. A combined real GPU+browser run of this new interface still
requires a permitted GPU session and is **not yet claimed**.

**Security note:** The loopback-only setting protects the service from direct
network exposure on the host. Do not tunnel or reverse-proxy this port,
and do not enable the feature on a public platform.
