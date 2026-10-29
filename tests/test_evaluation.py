"""Metric tests exercise deterministic calculations, not neural predictions."""

from pathlib import Path
import csv
import importlib.util


def load_evaluation():
    path = Path(__file__).resolve().parents[1] / "evaluation/evaluate.py"
    spec = importlib.util.spec_from_file_location("indicwrite_evaluation", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_metric_known_perfect():
    assert load_evaluation().score("नमस्ते", "नमस्ते") == {
        "cer": 0.0, "wer": 0.0, "word_accuracy": 1.0, "exact_sentence_match": True
    }


def test_metric_one_substitution():
    fn = load_evaluation()
    assert fn.edit_distance("abc", "axc") == 1
    got = fn.score("नमस्ते भारत", "नमस्ते दुनिया")
    assert got["wer"] == 0.5
    assert got["word_accuracy"] == 0.5
    assert not got["exact_sentence_match"]


def test_reference_dataset_covers_eight_categories():
    path = Path(__file__).resolve().parents[1] / "evaluation/cases.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 40
    assert len({row["id"] for row in rows}) == 40
    cats = {row["category"] for row in rows}
    assert len(cats) == 8
    assert {row["category"] for row in rows if row["preserve_english"]} == {"code_mixing"}
