# Faculty Submission Checklist — IndicWrite

**Project:** IndicWrite — Hinglish Smart Writing Assistant  
**Course:** CS3235 Working with LLMs, CIE3 Lab, RV University  
**Student:** Munnaluri Rishikesh · **USN:** 1RVU23CSE291  
**Due:** 6 November 2026, 10:00 AM IST.

## Evidence completed and retained on GitHub

- [x] Genuine pretrained AI4Bharat IndicXlit neural transliteration and source
- [x] Responsive Streamlit interface and real desktop/mobile browser screenshots
- [x] Forty real model predictions with authored references and quantitative error analysis
- [x] Character error rate **5.58%**, defined macro clipped word accuracy **82.67%**, exact sentence match **22/40**
- [x] Optional separately attributed real Hindi→English OPUS-MT (not IndicTrans2)
- [x] PDF faculty report with screenshots, limitations, architecture and references
- [x] Automated offline tests and real-model/browser workflows, including Unicode and export checks
- [x] Hash-manifested faculty ZIP in Actions workflow **Package verifiable IndicWrite faculty submission**
- [x] No credentials, model weights, databases or other repositories included
- [x] Genuine pretrained BharatGen rewriting **GPU execution**: 1 smoke + 10 cases privately verified on Tesla T4 (FP16); preliminary editorial review only
- [ ] Independent Hindi-expert meaning-preservation and larger-scale quality evaluation: **not completed**
- [ ] Genuine gated IndicTrans2 translation: **not executed** (optional)
- [ ] Public hosting and real public URL: **not verified**
- [ ] Complete accessibility/WCAG and native Windows tests: not performed
- [ ] Faculty upload to Google Classroom: requires student account and review; not submitted from GitHub

## Presentation and demonstration

Start in Ubuntu/WSL2 with Python 3.10 (the exact environment used for successful official IndicXlit CI). Run the README setup and `python scripts/smoke_indicxlit.py`. Use `streamlit run app.py` and try:

- `kal mujhe college jana hai!` → **observed genuine model output** `कल मुझे कॉलेज जाना है!`
- `namaste dosto, aap kaise ho?` — show multilingual script conversion
- `kal Python hai`, with `Python` in protected English terms — show mixed language handling
- `हिंदी 123!` — shows unchanged input without claiming AI generated it
- Clear, copy and TXT download; optional OPUS-MT English only if separate dependencies are installed

Avoid calling human-edited text a model rewrite. Keep the experimental Hindi mT5 grammar button disabled: real checkpoints failed quality screening.

## Where to find the artifacts

- Report: [reports/IndicWrite_CS3235_Project_Report.pdf](../reports/IndicWrite_CS3235_Project_Report.pdf)
- Predicted examples: [evaluation/results/predictions.csv](../evaluation/results/predictions.csv)
- Evaluation metrics: [evaluation/results/metrics.json](../evaluation/results/metrics.json)
- Failure examples: [evaluation/results/worst_cases.csv](../evaluation/results/worst_cases.csv)
- Real screenshots: [screenshots/](../screenshots)
- Live GitHub evidence: [Actions](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions)
- Faculty submission ZIP: download artifact from [Package verifiable IndicWrite faculty submission](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/workflows/submission-package.yml). Every ZIP includes `SUBMISSION_MANIFEST.json` with source SHA and hashes.

## Experimental BharatGen decision

The checkpoint's public license statements and history are inconsistent. The pinned pretrained BharatGen model successfully ran privately on a T4 GPU, with all 11 generations passing runtime checks. The raw generated outputs stay outside the public repo pending publishing permission. A private review found one technical-term fidelity problem among ten examples; broader independent human validation is still needed. Do not distribute its weights or outputs or publicly host it without licensing clarification. Evaluate real outputs and preserve meaning using the pre-registered review cases before enabling any rewrite feature.

**Submission integrity:** The faculty is entitled to see a clearly disclosed functional transliteration prototype rather than an invented full sovereign-model rewrite. The verified deliverables can be demonstrated even while public BharatGen distribution and hosting approvals remain outstanding.


## Verified local Docker fallback

- [x] Isolated Docker image built on GitHub Actions (run [40898600397](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40898600397)).
- [x] Real official IndicXlit inference executed inside the Docker image.
- [x] Localhost-bound Streamlit health probe passed.
- [ ] Public internet deployment, **intentionally blocked** until a supported, accurate Python runtime and account authorization are available; Python3.10 has reached EOL.

Use `docker compose -f compose.demo.yml up --build` in Docker Desktop on your Windows laptop, then visit http://127.0.0.1:8501. Do not publish port 8501 to 0.0.0.0 on the host.


## Final delivery check (29 October 2026)

The report has been regenerated after the Docker and CTranslate2 fidelity studies. The faculty ZIP should be downloaded from the **newest successful** [submission workflow run](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/workflows/submission-package.yml), not an older draft. Its manifest distinguishes verified private BharatGen T4 inference from unverified publication approval and private-GPU browser QA. Faculty Classroom upload is still a distinct student-controlled action, not automatically performed by publishing a GitHub ZIP.
