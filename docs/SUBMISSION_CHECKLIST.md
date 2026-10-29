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
- [ ] Genuine pretrained BharatGen rewriting execution with GPU and human review: **not verified**
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

The checkpoint's public license statements and history are inconsistent. No BharatGen model has yet run in the tested environment; a pinned GPU notebook is available for private research. Do not distribute its weights or outputs or publicly host it without licensing clarification. Evaluate real outputs and preserve meaning using the pre-registered review cases before enabling any rewrite feature.

**Submission integrity:** The faculty is entitled to see a clearly disclosed functional transliteration prototype rather than an invented full sovereign-model rewrite. The verified deliverables can be demonstrated even if the GPU experiment remains blocked.
