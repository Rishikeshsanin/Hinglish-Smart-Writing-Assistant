# Evaluation protocol and executed results (2026-10-29)

The [40-case test dataset](cases.csv) is **manually authored** for this application; it is **not** Aksharantar and has **not** been checked by a Hindi linguist. A future supplementary evaluation can use official Aksharantar word pairs after confirming split/licensing details. Manual references may have valid alternatives.

Eight categories × five cases: ordinary Hinglish, spelling variation, loanwords, names, punctuation, code mixing, numbers, and ambiguity.

## Run genuine evaluation

After the official IndicXlit smoke test has passed and dependencies are installed:

```bash
python evaluation/evaluate.py
```

This script loads the **real** AI4Bharat pretrained model and generates CSV predictions. It does not include canned or stubbed responses.

Outputs were generated on GitHub Actions run [40870722731](https://github.com/Rishikeshsanin/Hinglish-Smart-Writing-Assistant/actions/runs/40870722731) and committed after successful real inference under `evaluation/results/`:

- `predictions.csv` — all 40 real predictions and per-case metrics
- `metrics.json` — macro sentence-level aggregate results and per-category metrics
- `worst_cases.csv` — the ten highest-CER failures for human analysis

**Measurements:** Unicode code-point Levenshtein character error rate (CER), whitespace word error rate (WER), `max(0, 1 - WER)` word accuracy and exact-sentence match rate. CER can exceed 100% due to insertions. Errors due to loanword spelling and contextual ambiguity should be discussed qualitatively; sentence rewriting must receive separate human evaluation.

**Status:** Executed against the official pretrained model. Results: 40 cases, macro CER **5.58%**, macro WER **17.33%**, macro word accuracy **82.67%**, exact sentence match **55%**. Spelling variations performed worst (49.33% word accuracy). These are manually authored reference sentences; no broad benchmark accuracy claim is made.
