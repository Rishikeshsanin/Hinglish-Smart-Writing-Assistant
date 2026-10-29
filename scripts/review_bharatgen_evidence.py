"""Private review workflow for actual pinned BharatGen JSONL evidence.

This does NOT claim independent expert assessment. Candidate text stays in
a gitignored private folder and is never printed or committed by this script.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SAFE=ROOT/"private_research"
FIELDS=["case_id","original_hindi","candidate_hindi","grammar_0_2",
        "meaning_0_2","entities_0_2","unnecessary_edit_0_2","reviewer","notes"]


def _evidence_lines(path: Path) -> list[str]:
    if path.suffix==".zip":
        with zipfile.ZipFile(path) as archive:
            # Avoid zip-slip/extraction; read one known file directly.
            names=[name for name in archive.namelist() if name=="ten-cases.jsonl"]
            if len(names)!=1:
                raise ValueError("Expected exactly one ten-cases.jsonl in private evidence ZIP")
            return archive.read(names[0]).decode("utf-8").splitlines()
    return path.read_text(encoding="utf-8").splitlines()


def build_private_review(path: Path, output: Path) -> int:
    data=[json.loads(line) for line in _evidence_lines(path) if line.strip()]
    records=[x for x in data if x.get("event")=="generation"]
    if len(records)!=10 or len({r.get("case_id") for r in records})!=10:
        raise ValueError("The expected 10 unique real-generation records were not found.")
    if any(not r.get("runtime_candidate_ok") or not r.get("candidate") for r in records):
        raise ValueError("Invalid or truncated model candidate; review sheet not written.")
    if output.resolve().parent!=SAFE.resolve():
        raise ValueError("Review output must stay in the repository's ignored private_research folder")
    SAFE.mkdir(parents=True,exist_ok=True)
    with output.open("x",encoding="utf-8",newline="") as out:
        writer=csv.DictWriter(out,fieldnames=FIELDS)
        writer.writeheader()
        for item in records:
            writer.writerow({
                "case_id":item["case_id"],
                "original_hindi":item["input"],
                "candidate_hindi":item["candidate"],
            })
    return len(records)


def aggregate_review(path: Path) -> dict:
    with path.open(encoding="utf-8",newline="") as fh:
        records=list(csv.DictReader(fh))
    if len(records)!=10 or len({r["case_id"] for r in records})!=10:
        raise ValueError("Human review must include exactly 10 unique case IDs.")
    rating_fields=("grammar_0_2","meaning_0_2","entities_0_2","unnecessary_edit_0_2")
    if any(not str(r.get("reviewer","")).strip() for r in records):
        raise ValueError("Missing human-reviewer attribution; not an independent expert score.")
    for row in records:
        for field in rating_fields:
            if row.get(field) not in {"0","1","2"}:
                raise ValueError(f"Case {row['case_id']} requires a 0–2 human rating for {field}")
    mean={field:round(sum(int(row[field]) for row in records)/10,2) for field in rating_fields}
    return {
        "total_cases":len(records),"reviewer_attributed":True,
        "grammaticality_mean_0_2":mean["grammar_0_2"],
        "meaning_mean_0_2":mean["meaning_0_2"],
        "entities_mean_0_2":mean["entities_0_2"],
        "unnecessary_edits_mean_0_2":mean["unnecessary_edit_0_2"],
        "acceptable_meaning_and_entities_count":sum(
            row["meaning_0_2"]=="2" and row["entities_0_2"]=="2" for row in records
        ),
        "limitations":"Self-authored ten-case human review; not certified independent expert assessment.",
    }


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--create-from-zip",type=Path)
    parser.add_argument("--summarize",type=Path)
    args=parser.parse_args()
    if bool(args.create_from_zip)==bool(args.summarize):
        parser.error("Select exactly one of --create-from-zip or --summarize")
    if args.create_from_zip:
        output=SAFE/"bharatgen-human-review.csv"
        count=build_private_review(args.create_from_zip,output)
        print(f"PRIVATE_REVIEW_TEMPLATE_CREATED: {output} ({count} actual cases; do not commit or share publicly)")
    else:
        summary=aggregate_review(args.summarize)
        print("HUMAN_REVIEW_AGGREGATE_ONLY",json.dumps(summary,ensure_ascii=False))


if __name__=="__main__":
    main()
