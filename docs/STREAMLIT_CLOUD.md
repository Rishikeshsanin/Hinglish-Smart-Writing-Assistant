# IndicWrite free Streamlit Cloud deployment — original official model

The **official AI4Bharat IndicXlit pretrained checkpoint** has now been
successfully run on supported **Python 3.12** with **40/40 exact prediction
parity** against the verified original Python 3.10 evaluation.
Evidence: [GitHub Actions run 41210696882](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41210696882).

This uses a pinned MIT-licensed external Fairseq/Hydra compatibility patch
from ShunyaLabs codemix-restore v0.4.0. The patch does not replace the
model. It monkey-patches legacy imports and the trusted checkpoint loader,
so this deployment must **never accept user-supplied checkpoint files**.

## Free account setup

Use [Streamlit Community Cloud](https://share.streamlit.io/) (free). Sign in with
GitHub and deploy:

- Repository: `Rishikeshsanin/Hinglish-Smart-Writing-Assistant`
- Branch: `main`
- Main file: `cloud_app.py`
- Python: **3.12**, if manually selectable
- Secrets: **none**
- Dependency spec: root `environment.yml` pins Python 3.12 and pip 23.3.2
  to install legacy Fairseq metadata on this runtime.

The project also has root `requirements.txt` for the old local demo;
Community Cloud prioritizes `environment.yml` over that requirements file
when selecting a dependency manager. No other projects/services are involved.

## Quality and hosting gates

1. Verify the deployed app actually loads the official weights from a cold
   start and converts `kal mujhe college jana hai!`.
2. Check narrow mobile viewport, Clear, copy/download and number protection.
3. Inspect memory; Community Cloud has variable memory allocation.
4. Confirm the public HTTPS URL works without authentication or billing.
5. Keep BharatGen and optional OPUS model off in this public deployment.

**Important:** A passing Python3.12 GitHub Actions inference run proves model
compatibility, **not** that Community Cloud's Conda environment installs every
dependency, that the service stays under memory limits, or that the public site
is available. No URL or production-readiness claim is made until those steps
pass. Do not enable paid tiers or use a cloud account with billing credits.
