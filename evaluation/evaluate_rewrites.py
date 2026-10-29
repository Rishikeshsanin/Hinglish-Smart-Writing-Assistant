"""Generate genuine BharatGen rewrites and summarize completed human review.

Generation downloads and executes the real checkpoint. It never supplies cached
or invented predictions. Human judgements are deliberately separate because
grammar and meaning preservation cannot be established by string similarity.
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

from indicwrite.param_rewrite import BharatGenRewriter, MODEL_ID, MODEL_REVISION

CASE_FIELDS = ("id", "category", "input_hindi", "preservation_targets")
REVIEW_FIELDS = (
    "grammar_score_1_to_5",
    "meaning_score_1_to_5",
    "preservation_pass",
    "added_information",
    "reviewer_notes",
)


def load_cases(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or tuple(rows[0]) != CASE_FIELDS:
        raise ValueError(f"Expected columns: {', '.join(CASE_FIELDS)}")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate rewrite case IDs")
    if any(not all(row[field].strip() for field in CASE_FIELDS) for row in rows):
        raise ValueError("Every rewrite case field must be non-empty")
    return rows


def _parse_bool(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise ValueError(f"{field} must be true or false")
    return normalized == "true"


def summarize_reviews(rows: list[dict[str, str]]) -> dict[str, object]:
    if not rows:
        raise ValueError("No review rows supplied")
    ids = [row.get("id", "") for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate review case IDs")
    scored = []
    for row in rows:
        if not row.get("model_output", "").strip():
            raise ValueError(f"{row.get('id', 'unknown')}: missing genuine model output")
        try:
            grammar = int(row["grammar_score_1_to_5"])
            meaning = int(row["meaning_score_1_to_5"])
        except (KeyError, ValueError) as exc:
            raise ValueError(f"{row.get('id', 'unknown')}: invalid review score") from exc
        if grammar not in range(1, 6) or meaning not in range(1, 6):
            raise ValueError(f"{row.get('id', 'unknown')}: scores must be 1 through 5")
        preservation = _parse_bool(row.get("preservation_pass", ""), "preservation_pass")
        added = _parse_bool(row.get("added_information", ""), "added_information")
        scored.append((grammar, meaning, preservation, added))
    count = len(scored)
    return {
        "reviewed_cases": count,
        "mean_grammar_score": round(sum(item[0] for item in scored) / count, 3),
        "mean_meaning_score": round(sum(item[1] for item in scored) / count, 3),
        "preservation_pass_rate": round(sum(item[2] for item in scored) / count, 3),
        "added_information_rate": round(sum(item[3] for item in scored) / count, 3),
        "method": "Manual review; grammar and meaning scored 1-5. Binary factual-target preservation and added-information checks.",
    }


def generate(cases_path: Path, output_path: Path) -> None:
    cases = load_cases(cases_path)
    engine = BharatGenRewriter.load()
    rows = []
    for index, case in enumerate(cases, 1):
        started = time.perf_counter()
        output = engine.rewrite(case["input_hindi"])
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        rows.append({
            **case,
            "model_output": output,
            "latency_ms": latency_ms,
            **{field: "" for field in REVIEW_FIELDS},
        })
        print(f"{index:02d}/{len(cases)} {case['id']} {latency_ms:.2f} ms", flush=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
        "revision": MODEL_REVISION,
        "python": platform.python_version(),
        "case_count": len(rows),
        "review_status": "PENDING: fill all review fields, then run --summarize",
    }
    output_path.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Genuine outputs saved to {output_path}; human review is still pending.")


def summarize(path: Path) -> None:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected_ids = {row["id"] for row in load_cases(ROOT / "evaluation/rewrite_cases.csv")}
    actual_ids = {row.get("id", "") for row in rows}
    if actual_ids != expected_ids or len(rows) != len(expected_ids):
        raise ValueError("Reviewed CSV must contain every fixed rewrite case exactly once")
    result = summarize_reviews(rows)
    destination = path.with_suffix(".summary.json")
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", action="store_true")
    mode.add_argument("--summarize", type=Path, metavar="REVIEWED_CSV")
    parser.add_argument("--allow-model-download", action="store_true")
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation/rewrite_cases.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation/results/bharatgen_rewrites.csv")
    args = parser.parse_args()
    if args.generate:
        if not args.allow_model_download:
            parser.error("--generate requires --allow-model-download")
        generate(args.cases, args.output)
    else:
        summarize(args.summarize)


if __name__ == "__main__":
    main()
