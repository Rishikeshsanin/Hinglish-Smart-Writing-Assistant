"""Render the academic report from committed text and genuine screenshots.

This never generates example predictions or fabricated measurements.
Usage: python scripts/build_faculty_report.py
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import markdown
from weasyprint import HTML

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/"docs"/"REPORT.md"
metrics=ROOT/"evaluation/results/metrics.json"
screenshots=[ROOT/"screenshots/desktop.png",ROOT/"screenshots/mobile.png"]
assert metrics.is_file(), "Evaluation must be executed first"
assert all(x.is_file() for x in screenshots), "Real screenshots must exist"
j=json.loads(metrics.read_text(encoding="utf-8"))
assert j["overall"]["count"]==40, "Only generate final PDF after 40 cases"
assert "IndicXlit" in j["model"]
from pathlib import Path
import re

def validate_report_against_metrics(report_text: str, metrics: dict) -> None:
    """Fail closed if a revised report silently cites old measured scores."""
    overall = metrics["overall"]
    assert overall["count"] == 40
    required = [
        f"{overall['mean_cer'] * 100:.2f}%",
        f"{overall['mean_word_accuracy'] * 100:.2f}%",
        f"{overall['exact_sentence_match_rate'] * 100:.0f}%",
    ]
    for number in required:
        assert number in report_text, f"Report metric drift: missing {number}"
    section = report_text.split("### 6.1 Performance by category", 1)[1].split("## 7.", 1)[0]
    labels = {
        "ordinary": "Ordinary Hinglish",
        "spelling_variation": "Spelling variation",
        "loanwords": "Loanwords",
        "names": "Names",
        "punctuation": "Punctuation",
        "code_mixing": "Code mixing",
        "numbers": "Numbers",
        "ambiguous": "Ambiguous",
    }
    for key, label in labels.items():
        row = metrics["by_category"][key]
        expected = (
            f"| {label} | {row['count']} | "
            f"{row['mean_cer'] * 100:.2f}% | "
            f"{row['mean_word_accuracy'] * 100:.2f}% | "
            f"{row['exact_sentence_match_rate'] * 100:.0f}% |"
        )
        assert expected in section, f"Report category drift: {key}"

md=source.read_text(encoding="utf-8")
validate_report_against_metrics(md, j)
assert "Not installed, integrated, or executed" in md, "Must disclose unimplemented features"
content=markdown.markdown(md,extensions=["tables","fenced_code"])
css="""
@page {size:A4; margin:17mm 16mm 18mm; @bottom-right {content:"IndicWrite • CS3235  |  " counter(page);
font-size:8pt;color:#697493}}
body {font-family:'DejaVu Sans','Noto Sans Devanagari',sans-serif;font-size:9.5pt;line-height:1.53;color:#252c46}
h1 {font-size:30pt;line-height:1.2;color:#292e72;margin:10mm 0 7mm}
h2 {font-size:15pt;color:#333982;padding:6px 0;border-bottom:1px solid #d7dcf1;break-after:avoid}
h3 {font-size:11pt;color:#333982;break-after:avoid}
p {margin:8px 0}
strong {color:#252e63}
table {border-collapse:collapse;width:100%;font-size:8pt;margin:11px 0 17px}
td,th {border:1px solid #dce0ef;padding:6px 8px;vertical-align:top;overflow-wrap:anywhere}
th {background:#e9ecfb;color:#333870;text-align:left}
tr {break-inside:avoid}
li {margin:0 0 5px}
pre {white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#f2f4fb;border-radius:6px;line-height:1.4;font-size:8pt}
code {font-size:8pt}
a {color:#3b4da3;overflow-wrap:anywhere}
img {display:block;max-width:100%;max-height:175mm;object-fit:contain;margin:12px auto;border:1px solid #e6e9ef}
img[alt*='mobile'] {max-width:65%}
h1+p {font-size:11pt}
"""
output=ROOT/"reports/IndicWrite_CS3235_Project_Report.pdf"
output.parent.mkdir(parents=True,exist_ok=True)
html="<html><head><meta charset='utf-8'><style>"+css+"</style></head><body>"+content+"</body></html>"
HTML(string=html,base_url=str(source.parent)).write_pdf(output)
print("Built report:",output,"bytes",output.stat().st_size,flush=True)
