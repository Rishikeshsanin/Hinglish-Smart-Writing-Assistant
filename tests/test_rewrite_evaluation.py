import csv
import importlib.util
from pathlib import Path

import pytest


def load_module():
    path = Path(__file__).resolve().parents[1] / "evaluation/evaluate_rewrites.py"
    spec = importlib.util.spec_from_file_location("rewrite_evaluation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rewrite_dataset_has_unique_fixed_cases():
    module = load_module()
    rows = module.load_cases(Path(__file__).resolve().parents[1] / "evaluation/rewrite_cases.csv")
    assert len(rows) == 12
    assert len({row["id"] for row in rows}) == 12
    assert {"agreement", "code_mixing", "numbers", "negation"} <= {
        row["category"] for row in rows
    }


def test_review_summary_uses_only_explicit_human_scores():
    module = load_module()
    rows = [
        {"id": "R01", "model_output": "वाक्य", "grammar_score_1_to_5": "4",
         "meaning_score_1_to_5": "5", "preservation_pass": "true",
         "added_information": "false"},
        {"id": "R02", "model_output": "दूसरा", "grammar_score_1_to_5": "2",
         "meaning_score_1_to_5": "3", "preservation_pass": "false",
         "added_information": "true"},
    ]
    assert module.summarize_reviews(rows) == {
        "reviewed_cases": 2,
        "mean_grammar_score": 3.0,
        "mean_meaning_score": 4.0,
        "preservation_pass_rate": 0.5,
        "added_information_rate": 0.5,
        "method": "Manual review; grammar and meaning scored 1-5. Binary factual-target preservation and added-information checks.",
    }


@pytest.mark.parametrize("field,value", [
    ("grammar_score_1_to_5", "0"),
    ("meaning_score_1_to_5", "6"),
    ("preservation_pass", "maybe"),
    ("added_information", ""),
])
def test_review_summary_rejects_invalid_or_missing_judgements(field, value):
    module = load_module()
    row = {"id": "R01", "model_output": "वाक्य", "grammar_score_1_to_5": "4",
           "meaning_score_1_to_5": "4", "preservation_pass": "true",
           "added_information": "false"}
    row[field] = value
    with pytest.raises(ValueError):
        module.summarize_reviews([row])


def test_case_loader_rejects_duplicate_ids(tmp_path):
    module = load_module()
    path = tmp_path / "cases.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=module.CASE_FIELDS)
        writer.writeheader()
        for _ in range(2):
            writer.writerow({"id": "R01", "category": "x", "input_hindi": "है",
                             "preservation_targets": "है"})
    with pytest.raises(ValueError, match="Duplicate"):
        module.load_cases(path)


def test_review_summary_rejects_duplicate_ids():
    module = load_module()
    row = {"id": "R01", "model_output": "वाक्य", "grammar_score_1_to_5": "4",
           "meaning_score_1_to_5": "4", "preservation_pass": "true",
           "added_information": "false"}
    with pytest.raises(ValueError, match="Duplicate"):
        module.summarize_reviews([row, row.copy()])
