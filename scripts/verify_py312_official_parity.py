"""Compare ALL 40 genuine Python3.12 outputs with saved official Python3.10.

Fails if even one output changes. This is not a metric approximation and does
not commit any new model-generated text into the repository.
"""
from __future__ import annotations
import csv,json,os,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"src"))
from indicwrite.core import parse_preserve_terms,transliterate_text
from indicwrite.engine import load_indicxlit
assert sys.version_info[:2]==(3,12)
assert os.environ.get("INDICWRITE_PY312_COMPAT")=="1"
with (root/"evaluation/cases.csv").open(encoding="utf-8-sig",newline="") as f:
    cases=list(csv.DictReader(f))
with (root/"evaluation/results/predictions.csv").open(encoding="utf-8-sig",newline="") as f:
    originals=list(csv.DictReader(f))
assert len(cases)==len(originals)==40
engine=load_indicxlit()
mismatches=[]
for i,(case,baseline) in enumerate(zip(cases,originals),1):
    assert case["id"]==baseline["id"]
    generated=transliterate_text(case["roman_text"],engine,parse_preserve_terms(case["preserve_english"]))
    if generated!=baseline["predicted_hindi"]:
        mismatches.append(case["id"])
    print(f"PY312_REAL_INDICXLIT_CASE {i:02}/40 parity={generated==baseline['predicted_hindi']}",flush=True)
summary={"model":"official AI4Bharat IndicXlit","python":"3.12",
"true_pretrained_inference":True,"cases":40,
"exact_parity_count":40-len(mismatches),"mismatch_ids":mismatches,
"quality_baseline_preserved":len(mismatches)==0}
print("PY312_OFFICIAL_INDICXLIT_PARITY",json.dumps(summary),flush=True)
assert not mismatches,"Model outputs differ; do NOT approve new runtime"
