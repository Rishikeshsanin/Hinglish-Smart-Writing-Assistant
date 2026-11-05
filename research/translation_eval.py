"""Opt-in OPUS-MT evaluation. NEVER generates sample predictions or human scores.

This is separate from the original 40 IndicXlit cases and private BharatGen.
Generated candidate sentences and reviewer forms stay in gitignored private_research.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from indicwrite.language_services import (
    TRANSLATION_MODEL, load_hi_en, translate_optional,
)

CASE_FIELDS = ("id", "category", "input_hindi", "review_focus")
REVIEW_FIELDS = (
    "reviewer_id", "adequacy_score_1_to_5", "fluency_score_1_to_5",
    "entities_numbers_preserved", "invented_information", "reviewer_notes",
)
PRIVATE_DIR = ROOT / "private_research"
DEFAULT_CASES = ROOT / "research/translation_cases.csv"
DEFAULT_OUTPUT = PRIVATE_DIR / "opus-mt-translation-review.csv"


def read_cases(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != CASE_FIELDS:
            raise ValueError("Expected exactly: " + ", ".join(CASE_FIELDS))
        rows = list(reader)
    if len(rows) < 10 or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Require at least 10 unique translation case IDs")
    if any(not all(row.get(col, "").strip() for col in CASE_FIELDS) for row in rows):
        raise ValueError("Every translation case field must be complete")
    return rows


def private_path(path: Path) -> Path:
    """Never write generated user/model sentences into a tracked repository path."""
    resolved = path.expanduser().resolve()
    if not resolved.is_relative_to(PRIVATE_DIR.resolve()):
        raise ValueError("Evaluation output must stay inside gitignored private_research/")
    return resolved


def generate_real_predictions(cases: Path, output: Path) -> dict[str, object]:
    """The caller must explicitly opt in; only a real pretrained model is used."""
    output = private_path(output)
    fixed = read_cases(cases)
    resources = load_hi_en()  # real checkpoint or loud failure: no synthetic fallback
    result_rows = []
    for case in fixed:
        start = time.perf_counter()
        record = translate_optional(
            case["input_hindi"],
            environment={"INDICWRITE_ENABLE_LANGUAGE_SERVICES": "1"},
            resources=resources,
        )
        result_rows.append({
            **case,
            "model_id": record["model_id"],
            "model_output": record["candidate"],
            "automatic_warnings": " | ".join(record["warnings"]),
            "latency_ms": f"{(time.perf_counter() - start) * 1000:.2f}",
            **{field: "" for field in REVIEW_FIELDS},
        })
    # Complete in-memory generation first; no misleading partial model data.
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(output.name + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result_rows[0]))
        writer.writeheader()
        writer.writerows(result_rows)
    temp.replace(output)
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": TRANSLATION_MODEL,
        "checkpoint_family": "Helsinki-NLP OPUS-MT, NOT IndicTrans2",
        "python": platform.python_version(),
        "case_count": len(result_rows),
        "generation": "real_pretrained_inference",
        "human_review": "PENDING",
        "quality_claim": "NONE",
    }
    output.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return metadata


def _score(value: str, field: str) -> int:
    if not isinstance(value, str) or value.strip() not in {"1", "2", "3", "4", "5"}:
        raise ValueError(f"{field} must be a completed integer score from 1 to 5")
    return int(value)


def _boolean(value: str, field: str) -> bool:
    if not isinstance(value, str) or value.strip().lower() not in {"true", "false"}:
        raise ValueError(f"{field} must be true or false")
    return value.strip().lower() == "true"


def summarize_reviews(rows: list[dict[str, str]]) -> dict[str, object]:
    """Aggregates only genuine supplied human scores; does not infer correctness."""
    if not rows or len({row.get("id") for row in rows}) != len(rows):
        raise ValueError("Require unique, nonempty reviewed rows")
    for row in rows:
        if not row.get("id") or not row.get("model_output", "").strip():
            raise ValueError("Missing case ID or generated candidate")
        if row.get("model_id") != TRANSLATION_MODEL:
            raise ValueError("Incorrect model attribution; cannot call this OPUS-MT")
        if not row.get("reviewer_id", "").strip():
            raise ValueError(f"{row['id']}: an actual reviewer identifier is required")
    adequacy = [_score(r.get("adequacy_score_1_to_5", ""), "adequacy") for r in rows]
    fluency = [_score(r.get("fluency_score_1_to_5", ""), "fluency") for r in rows]
    preserved = [
        _boolean(r.get("entities_numbers_preserved", ""), "entities_numbers_preserved")
        for r in rows
    ]
    invented = [_boolean(r.get("invented_information", ""), "invented_information")
                for r in rows]
    count = len(rows)
    return {
        "reviewed_cases": count,
        "mean_adequacy_1_to_5": round(sum(adequacy) / count, 3),
        "mean_fluency_1_to_5": round(sum(fluency) / count, 3),
        "entity_number_preservation_rate": round(sum(preserved) / count, 3),
        "invented_information_rate": round(sum(invented) / count, 3),
        "review_method": "Human adequacy/fluency 1-5 and manually checked entity/number/hallucination flags; NOT automatic semantic verification.",
        "limitations": "Small authored evaluation, not a bilingual expert benchmark; reviewers must disclose expertise and conflicts.",
    }


def summarize_private(path: Path, cases: Path) -> dict[str, object]:
    path = private_path(path)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected = {item["id"] for item in read_cases(cases)}
    actual = [row.get("id", "") for row in rows]
    if len(rows) != len(expected) or set(actual) != expected:
        raise ValueError("Every fixed translation case must be independently reviewed once")
    metadata_path = path.with_suffix(".metadata.json")
    if not metadata_path.is_file():
        raise ValueError("Missing real-generation metadata; refuse unverifiable output")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if (metadata.get("model_id") != TRANSLATION_MODEL
            or metadata.get("case_count") != len(expected)
            or metadata.get("generation") != "real_pretrained_inference"):
        raise ValueError("Incompatible generation metadata; cannot summarize")
    result = summarize_reviews(rows)
    path.with_suffix(".summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", action="store_true")
    mode.add_argument("--summarize", action="store_true")
    parser.add_argument("--allow-model-download", action="store_true")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.generate:
        if not args.allow_model_download:
            parser.error("Real inference requires explicit --allow-model-download")
        evidence = generate_real_predictions(args.cases, args.output)
        print(f"Real OPUS-MT generations: {evidence['case_count']} (private). Human scores PENDING.")
    else:
        aggregate = summarize_private(args.output, args.cases)
        print(json.dumps(aggregate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
