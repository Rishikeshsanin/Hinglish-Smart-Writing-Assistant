"""Real model parity research: third-party CTranslate2 ≠ official checkpoint.

Runs forty actual dataset inferences with the converted weights and compares
against the immutable official IndicXlit evaluation results. It does not
overwrite the official stored predictions, metrics or report.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from indicwrite.ct2_engine import load_converted_indicxlit
from indicwrite.core import transliterate_text, parse_preserve_terms
from evaluation.evaluate import score

ROOT = Path(__file__).resolve().parents[1]


def main():
    with (ROOT / "evaluation/cases.csv").open(encoding="utf-8-sig", newline="") as fh:
        records = list(csv.DictReader(fh))
    with (ROOT / "evaluation/results/predictions.csv").open(encoding="utf-8-sig", newline="") as fh:
        official = {item["id"]: item for item in csv.DictReader(fh)}
    assert len(records) == 40 == len(official)
    t0 = time.perf_counter()
    engine = load_converted_indicxlit()
    cold_s = round(time.perf_counter() - t0, 3)
    results = []
    for row in records:
        started = time.perf_counter()
        actual = transliterate_text(
            row["roman_text"], engine,
            preserve_terms=parse_preserve_terms(row["preserve_english"]),
        )
        scores = score(row["reference_hindi"], actual)
        base = official[row["id"]]["predicted_hindi"]
        results.append({
            "id": row["id"], "category": row["category"],
            "converted_output": actual, "official_output": base,
            "exact_official_parity": actual == base,
            "latency_s": round(time.perf_counter() - started, 4),
            **scores,
        })
        print(json.dumps({"id": row["id"], "actual": actual, "parity": actual == base}, ensure_ascii=False), flush=True)
    report = {
        "engine": "Third-party converted CTranslate2 AI4Bharat IndicXlit; not the official runtime",
        "model": engine.revision, "model_id": "Singla0009/all-indic-transliteration",
        "cases": 40,
        "match_to_official_output_count": sum(row["exact_official_parity"] for row in results),
        "mean_cer": round(sum(row["cer"] for row in results) / 40, 6),
        "mean_word_accuracy": round(sum(row["word_accuracy"] for row in results) / 40, 6),
        "exact_reference_match_count": sum(row["exact_sentence_match"] for row in results),
        "cold_load_seconds": cold_s,
        "results": results,
    }
    output = ROOT / "ct2-real-evidence.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REAL_CT2_PARITY_EVIDENCE", json.dumps({
        k: v for k, v in report.items() if k != "results"
    }, ensure_ascii=False), flush=True)
    # Only real output suffices as research smoke. Quality approval is independent.
    assert all(any("\u0900" <= ch <= "\u097f" for ch in rec["converted_output"]) for rec in results)
    print("REAL_CONVERTED_INDICXLIT_40_CASE_EVALUATION_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
