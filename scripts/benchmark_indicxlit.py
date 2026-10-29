"""Measured genuine IndicXlit memory and latency evidence (Linux CPU)."""
from __future__ import annotations
import json, platform, resource, sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from indicwrite.engine import load_indicxlit
from indicwrite.core import transliterate_text
t=time.perf_counter()
engine=load_indicxlit()
cold_s=round(time.perf_counter()-t,3)
cases=[]
for source in ("kal mujhe college jana hai!","mera phone 2026 mein aaya.","namaste dosto, aap kaise ho?"):
    started=time.perf_counter()
    actual=transliterate_text(source,engine)
    assert any("\u0900"<=c<="\u097f" for c in actual)
    cases.append({"input":source,"real_output":actual,"seconds":round(time.perf_counter()-started,3)})
assert sys.platform=="linux"
result={"platform":platform.platform(),"python":platform.python_version(),
        "cold_load_seconds":cold_s,
        "peak_process_rss_mib":round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1),
        "cases":cases,"scope":"Linux process only; not full Streamlit multiuser deployment RSS"}
out=Path(__file__).resolve().parents[1]/"evaluation/results/indicxlit-resource-probe.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print("REAL_INDICXLIT_RESOURCE_PROBE",json.dumps(result,ensure_ascii=False),flush=True)
