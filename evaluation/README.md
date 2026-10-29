# Evaluation protocol (not yet executed)

The [40-case test dataset](cases.csv) is **manually authored** for this application; it is **not** Aksharantar and has **not** been checked by a Hindi linguist. A future supplementary evaluation can use official Aksharantar word pairs after confirming split/licensing details. Manual references may have valid alternatives.

Eight categories × five cases: ordinary Hinglish, spelling variation, loanwords, names, punctuation, code mixing, numbers, and ambiguity.

## Run genuine evaluation

After the official IndicXlit smoke test has passed and dependencies are installed:

```bash
python evaluation/evaluate.py
```

This script loads the **real** AI4Bharat pretrained model and generates CSV predictions. It does not include canned or stubbed responses.

Outputs are written under `evaluation/results/` (intentionally ignored until reviewed):

- `predictions.csv` — all 40 real predictions and per-case metrics
- `metrics.json` — macro sentence-level aggregate results and per-category metrics
- `worst_cases.csv` — the ten highest-CER failures for human analysis

**Measurements:** Unicode code-point Levenshtein character error rate (CER), whitespace word error rate (WER), `max(0, 1 - WER)` word accuracy and exact-sentence match rate. CER can exceed 100% due to insertions. Errors due to loanword spelling and contextual ambiguity should be discussed qualitatively; sentence rewriting must receive separate human evaluation.

**Status:** Prepared only; no computed scores or real-model predictions have been asserted. Do not submit this section as completed evaluation until the script has run on the pretrained checkpoint.
