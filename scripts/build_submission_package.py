"""Create an evidence-preserving faculty submission ZIP from committed files."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
name="IndicWrite_CS3235_CIE3_Submission"
out=ROOT/"submission"/(name+".zip")
required=[
 "app.py","README.md","AGENTS.md","requirements.txt","requirements-language-services.txt",
 "evaluation/cases.csv","evaluation/results/metrics.json",
 "evaluation/results/predictions.csv","evaluation/results/worst_cases.csv",
 "screenshots/desktop.png","screenshots/mobile.png",
 "reports/IndicWrite_CS3235_Project_Report.pdf",
]
for rel in required:
    assert (ROOT/rel).is_file(), f"Missing required evidence: {rel}"
pdf=(ROOT/"reports/IndicWrite_CS3235_Project_Report.pdf").read_bytes()
assert pdf.startswith(b"%PDF-"), "Academic report is not a real PDF"
included=[]
for pattern in (
 "app.py","README.md","AGENTS.md","requirements*.txt",".python-version",
 "src/**/*.py","scripts/**/*.py","tests/**/*.py","evaluation/*.py","evaluation/*.csv",
 "evaluation/*.md","evaluation/results/*.json","evaluation/results/*.csv",
 "docs/*.md","screenshots/*.png","screenshots/*.json","reports/*.pdf",
 "notebooks/*.ipynb",".github/workflows/*.yml",".streamlit/*.toml",
):
    for item in ROOT.glob(pattern):
        if item.is_file() and item not in included and not any(
            part.startswith(".env") or part in {".venv","__pycache__","models","checkpoints"}
            for part in item.relative_to(ROOT).parts
        ):
            included.append(item)
commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
manifest={
 "project":"IndicWrite — Hinglish Smart Writing Assistant",
 "student":"Munnaluri Rishikesh","usn":"1RVU23CSE291",
 "source_commit":commit,
 "scope":"Verified IndicXlit MVP and independently-attributed optional OPUS translation",
 "not_verified":["BharatGen pretrained inference","IndicTrans2 gated checkpoint","public hosted URL"],
 "files":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in included}
}
out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as zipfile_obj:
    for item in included:
        zipfile_obj.write(item,arcname=str(item.relative_to(ROOT)))
    zipfile_obj.writestr("SUBMISSION_MANIFEST.json",json.dumps(manifest,ensure_ascii=False,indent=2))
print("SUBMISSION_ARCHIVE_VERIFIED",out,out.stat().st_size,len(included),"files",commit)
