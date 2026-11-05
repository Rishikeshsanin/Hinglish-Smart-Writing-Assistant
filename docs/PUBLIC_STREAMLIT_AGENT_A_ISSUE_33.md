# Issue #33 — Streamlit backend and public QA (5 November 2026)

This work covers only the IndicWrite Streamlit Cloud backend and external public browser QA. It does not alter the frontend, other repositories, hosted URL, model, evaluation, or provider configuration.

## Protected original setup

- Existing URL: https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/
- Repo branch / entrypoint: main / cloud_app.py, Python 3.12, lightweight root requirements.txt.
- Official checkpoint: AI4Bharat IndicXlit (ai4bharat-transliteration==1.1.3), with legacy dependencies isolated in a pip23 venv.
- 40 real-model historical predictions and metrics (5.58% macro CER, 82.67% word accuracy, 22/40 exact) are **unchanged**, and are not an official benchmark.
- Public BharatGen/grammar/IndicTrans2 research is still disabled. No credentials, weights, private results, or extra hosting.

## Confirmed baseline incident

On 5 November the rerun of https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/41414939039 tried the live Streamlit URL six times. Playwright never saw the Convert to Hindi control; the job failed. It did **not** run hosted model inference. Earlier user screenshots from 2 November displayed a real hosted IndicXlit result, but are not evidence of current uptime or unattended verification.

The **actual screenshot artifact** from run 41414939039 was downloaded and visually inspected. It explicitly displays Streamlit's **Zzzz / This app has gone to sleep due to inactivity** screen and the **Yes, get this app back up!** public wake control. Thus a sleeping provider app is the confirmed reason the Convert control was absent *in that failed run*. This does not explain whether model bootstrap succeeds after waking. Authenticated Streamlit runtime logs have not been accessed in this PR.

## Improvements in the draft PR

- A Linux process file lock prevents overlapping venv install attempts. The lock is stored outside the directory cleared by venv rebuild; failed installs do not write the ready stamp.
- Cloud logs print dependency stage durations, available disk MB at first install, cache hits, and real official checkpoint load times. They do not print user inputs or secrets.
- Independent Playwright detects the observed sleeping-provider screen, clicks its public wake control, gives the original app up to four minutes to initialize and then checks conversion. It captures screenshots per failed attempt, body excerpt, accessible button labels, HTTP status, JS errors, diagnostics JSON and a browser trace on failure.
- The test separates provider asleep, HTTP errors, provider/app error messages, app not rendered, partially rendered app, and visible-but-mismatched selector; no missing-button outcome is called a successful conversion.
- It requires fresh real hosted Devanagari output for three distinct Roman Hindi sentences, with expected tokens and punctuation preserved. Logs capture the exact observed output and browser wait time. The test does not create substitute predictions.
- Browser CI now runs on pull requests and can be manually dispatched; its artifact is retained on both success and failure.

**Important:** A PR-triggered external browser tests the existing deployed version from main, not the draft branch. Genuine official model parity in CI is also not evidence that a free Streamlit worker has enough RAM or disk.

## Evidence interpretation

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Offline pytest pass | Code contracts | Any pretrained model ran |
| Official Python3.12 real-model parity | Authentic checkpoint predictions match historical results on CI runner | Cloud memory or uptime |
| PUBLIC_UI_READY | Public web control appeared | Model inference worked |
| Three PUBLIC_INDICXLIT_CONVERSION_PASS records plus passing diagnostic JSON | Three hosted browser conversions were actually rendered | Permanent uptime |
| PUBLIC_UI_BLOCKED / PUBLIC_INFERENCE_FAILED / PUBLIC_CONVERSION_TIMEOUT | Public release gate is blocked | Model quality failure |

Cloud server log markers include INDICWRITE_CLOUD_MODEL_VENV_BUILD, INDICWRITE_CLOUD_MODEL_VENV_READY, INDICWRITE_CLOUD_MODEL_VENV_CACHE_HIT, INDICWRITE_OFFICIAL_MODEL_COLD_LOAD_OK, and failure equivalents. Cold-load durations shown by server and per-conversion wall times by browser must be compared only after actual hosted runs. No hosted RAM or startup data are fabricated.

## Release gate: coordinator actions only

1. Review PR #37 and inspect Actions logs for the offline tests, original-model parity and new independent public smoke. Record exact SHA, run URLs, outputs and evidence artifacts.
2. If approved, coordinator merges; this branch owner will **not** merge.
3. Keep the existing app and URL. Let Community Cloud sync main. If needed, use the signed-in Streamlit Cloud dashboard to reboot **the same app** and inspect fresh build/runtime logs, including the model-load stage markers. Do not recreate it.
4. Run the existing public smoke workflow **after actual deployment**, and archive exact output, diagnostics JSON and screenshots; prefer two separate passing runs before claiming public stability.
5. If Cloud cannot install or run the authentic model under free RAM/disk/time limits, record actual provider logs and mark public acceptance **blocked**. Do not substitute an unverified public API or alternate checkpoint.

**Zero-cost fallback:** docs/LOCAL_DOCKER_DEMO.md describes the previously verified loopback-only original-checkpoint demo for faculty. It is a genuine local fallback, **not** a public-deployment success claim.
