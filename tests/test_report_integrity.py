"""Ensure the PDF authoring source cannot drift from saved real-model metrics."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_report_figures_match_recorded_evidence():
    report = (ROOT / "docs/REPORT.md").read_text(encoding="utf-8")
    metrics = json.loads((ROOT / "evaluation/results/metrics.json").read_text(encoding="utf-8"))
    overall = metrics["overall"]
    assert overall["count"] == 40
    for value in (
        f"{overall['mean_cer'] * 100:.2f}%",
        f"{overall['mean_word_accuracy'] * 100:.2f}%",
        f"{overall['exact_sentence_match_rate'] * 100:.0f}%",
    ):
        assert value in report


def test_each_report_category_line_matches_real_metrics():
    report = (ROOT / "docs/REPORT.md").read_text(encoding="utf-8")
    section = report.split("### 6.1 Performance by category", 1)[1].split("## 7.", 1)[0]
    metrics = json.loads((ROOT / "evaluation/results/metrics.json").read_text(encoding="utf-8"))
    labels = {
        "ordinary": "Ordinary Hinglish", "spelling_variation": "Spelling variation",
        "loanwords": "Loanwords", "names": "Names", "punctuation": "Punctuation",
        "code_mixing": "Code mixing", "numbers": "Numbers", "ambiguous": "Ambiguous",
    }
    for key, label in labels.items():
        row = metrics["by_category"][key]
        expected = (
            f"| {label} | {row['count']} | {row['mean_cer']*100:.2f}% | "
            f"{row['mean_word_accuracy']*100:.2f}% | "
            f"{row['exact_sentence_match_rate']*100:.0f}% |"
        )
        assert expected in section, key
