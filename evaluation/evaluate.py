"""Evaluate the actual IndicXlit model; no cached or synthetic predictions.

Run from repository root: python evaluation/evaluate.py
Outputs are saved to evaluation/results (gitignored) only after full inference.
"""
from __future__ import annotations

import csv
import json
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from indicwrite.core import parse_preserve_terms, transliterate_text
from indicwrite.engine import load_indicxlit


def edit_distance(reference: list[str] | str, predicted: list[str] | str) -> int:
    """Levenshtein insertion/deletion/substitution count."""
    previous = list(range(len(predicted) + 1))
    for i, left in enumerate(reference, start=1):
        current = [i]
        for j, right in enumerate(predicted, start=1):
            current.append(min(
                current[j - 1] + 1,
                previous[j] + 1,
                previous[j - 1] + (left != right),
            ))
        previous = current
    return previous[-1]


def score(reference: str, predicted: str) -> dict[str, float | bool]:
    reference = unicodedata.normalize("NFC", reference.strip())
    predicted = unicodedata.normalize("NFC", predicted.strip())
    if not reference:
        raise ValueError("Empty reference is not eligible for evaluation.")
    ref_words, hyp_words = reference.split(), predicted.split()
    cer = edit_distance(reference, predicted) / len(reference)
    wer = edit_distance(ref_words, hyp_words) / len(ref_words)
    return {
        "cer": round(cer, 6),
        "wer": round(wer, 6),
        "word_accuracy": round(max(0.0, 1.0 - wer), 6),
        "exact_sentence_match": reference == predicted,
    }


def evaluate() -> None:
    with (ROOT / "evaluation/cases.csv").open(encoding="utf-8-sig", newline="") as fh:
        cases = list(csv.DictReader(fh))
    if len(cases) != 40:
        raise ValueError(f"Expected 40 reference cases, got {len(cases)}")
    if len({row["id"] for row in cases}) != 40:
        raise ValueError("Duplicate case IDs in dataset")
    print("Loading official pretrained IndicXlit model...", flush=True)
    engine = load_indicxlit()

    output_rows = []
    for index, case in enumerate(cases, 1):
        prediction = transliterate_text(
            case["roman_text"], engine,
            preserve_terms=parse_preserve_terms(case["preserve_english"]),
        )
        result = score(case["reference_hindi"], prediction)
        output_rows.append({**case, "predicted_hindi": prediction, **result})
        print(f"{index:02d}/{len(cases)} {case['category']} CER={result['cer']:.3f}", flush=True)

    categories: dict[str, list[dict]] = defaultdict(list)
    for row in output_rows:
        categories[row["category"]].append(row)

    def aggregate(rows: list[dict]) -> dict:
        return {
            "count": len(rows),
            "mean_cer": round(sum(r["cer"] for r in rows) / len(rows), 6),
            "mean_wer": round(sum(r["wer"] for r in rows) / len(rows), 6),
            "mean_word_accuracy": round(sum(r["word_accuracy"] for r in rows) / len(rows), 6),
            "exact_sentence_match_rate": round(
                sum(bool(r["exact_sentence_match"]) for r in rows) / len(rows), 6
            ),
        }

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": "AI4Bharat IndicXlit via ai4bharat-transliteration==1.1.3",
        "dataset": "40 self-authored IndicWrite test cases; NOT the official Aksharantar benchmark",
        "metric_notes": "CER is Unicode code-point Levenshtein / reference code points. "
                        "WER is whitespace-token edit distance / reference word count. "
                        "Word accuracy = max(0, 1 - WER). All means are macro means by sentence.",
        "overall": aggregate(output_rows),
        "by_category": {k: aggregate(v) for k, v in categories.items()},
    }
    destination = ROOT / "evaluation/results"
    destination.mkdir(parents=True, exist_ok=True)
    output_path = destination / "predictions.csv"
    with output_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    with (destination / "metrics.json").open("w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    with (destination / "worst_cases.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(sorted(output_rows, key=lambda row: row["cer"], reverse=True)[:10])
    print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
    print(f"Recorded actual predictions in {output_path}", flush=True)


if __name__ == "__main__":
    evaluate()
