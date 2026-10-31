# IndicWrite — Streamlit Community Cloud recovery (1 November 2026)

## Deployment target

- **Existing public URL:** https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/
- **Repo / branch:** Rishikeshsanin/Hinglish-Smart-Writing-Assistant / `main`
- **Entrypoint:** `cloud_app.py`
- **Supported runtime:** Python **3.12** (declared in `.python-version`)
- **Dependency manager:** standard lightweight root `requirements.txt` (Streamlit host only; no Conda).
- **Actual AI model:** original AI4Bharat IndicXlit checkpoint. The `cloud_app.py` launcher installs it in an isolated venv using `pip==23.3.2` and pinned ShunyaLabs Python3.12 compatibility patch. It never downgrades the host pip or switches to a different model.
- **Disabled on public hosting:** BharatGen research and experimental optional language-service checkpoints.

For local/WSL2 and both Docker builds use `requirements-local.txt` (the exact original dependencies). The former Cloud `environment.yml` is archived as `docs/legacy-conda-environment.yml` and is **not** selected by Streamlit. This avoids the provider's Conda installation failure while preserving historical evidence and model test reproducibility.

## Failure chronology and technical evidence

1. 31 Oct 15:02 UTC: the former mixed pip/Conda setup failed before app startup with `ImportError: cannot import name 'open_rich_spinner'`. PR #25 separated the old Fairseq dependencies into a clean model-only venv; run [41218875342](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41218875342) verified the *real original* checkpoint and **40/40 historical output parity** on Python3.12.
2. PRs #26 and #27 added error logging and independent public Chromium QA. Public run [41223619626](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41223619626) failed: six visits to the real URL never showed the Convert button. No public model inference happened.
3. A user-authorized reboot at **17:37 UTC 31 Oct** spent almost 48 minutes resolving Conda. At **18:25:30 UTC** Cloud reported Python dependencies installed from `environment.yml`, then **18:25:35 UTC** `installer returned a non-zero exit code`, and **18:25:38 UTC** `streamlit: ERROR (spawn error)`, plus local health connection refused on 8501.
4. The **1 Nov pip-only recovery PR** removes `environment.yml` from repository root, sets `.python-version` to 3.12, retains original requirements for the local/Docker paths, and adds independent host-environment CI. This is a new deployment attempt **not an already proven public success**.

Streamlit's official [dependency selection docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) prefer a single dependency file. With the root Conda file absent, Community Cloud uses root `requirements.txt`. Official [manage-app docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app) cover reboot, server logs, and automatic dependency reinstallation on a GitHub change.

## Acceptance gates before submission

1. GitHub PR checks pass (pip-only host, isolated authentic model, offline unit tests, and unaffected Docker/local demo if triggered).
2. Merge the reviewed PR to `main` **only after green checks**. The changed `requirements.txt` triggers a normal Streamlit dependency refresh without deleting the app or URL.
3. Inspect **new** Cloud build/runtime logs. If bootstrap fails, use its server-side `IndicWrite: isolated official-model bootstrap failed` traceback. Do not guess at a new cause from old logs.
4. Run the existing independent GitHub Actions public browser test on the deployed URL and verify actual input `kal mujhe college jana hai!` produces real Hindi-script model output. Archive the real screenshot.
5. Verify mobile layout, copy/download and attribution, then update the faculty report and submission package with **only demonstrated public results**.

**Never** delete/recreate the user's existing app, enable billing, touch another repository, expose raw BharatGen output, or substitute an inferior transliteration model. If public deployment remains impossible, the already tested isolated Docker/local demo is an honest fallback for academic submission.
