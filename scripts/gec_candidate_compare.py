"""Run a second, public MIT-licensed Hindi grammatical error correction checkpoint.

This is experimental research: compares raw-input (author's example) vs
instruction prefix. Outputs are genuine neural predictions, not fixtures.
"""
import json
import platform
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
MODEL="Rucha-Ambaliya/mt5-small-indic-gec"
CASES=[
    ("मैं स्कूल जाता है।","मैं स्कूल जाता हूँ।"),
    ("राम ने ने खाना खाया।","राम ने खाना खाया।"),
    ("वे किताबें पढ़ता है।","वे किताबें पढ़ते हैं।"),
    ("आज मैं कॉलेज गए।","आज मैं कॉलेज गया।"),
    ("मुझे दो किताब चाहिए।","मुझे दो किताबें चाहिए।"),
]


def devanagari_ratio(text):
    letters=[c for c in text if c.isalpha()]
    return sum("\u0900"<=c<="\u097f" for c in letters)/len(letters) if letters else 0.0


def main():
    print("Model",MODEL,"PyTorch",torch.__version__,"Python",platform.python_version(),flush=True)
    tok=AutoTokenizer.from_pretrained(MODEL,trust_remote_code=False)
    model=AutoModelForSeq2SeqLM.from_pretrained(MODEL,trust_remote_code=False,use_safetensors=True)
    model.eval()
    rows=[]
    for prefix in ("","correct this: "):
        for source,reference in CASES:
            encoded=tok(prefix+source,return_tensors="pt",max_length=128,truncation=True)
            with torch.inference_mode():
                output=model.generate(**encoded,max_new_tokens=96,num_beams=4)
            decoded=tok.batch_decode(output,skip_special_tokens=True)[0].strip()
            ratio=round(devanagari_ratio(decoded),3)
            row={"prefix":prefix,"input":source,"reference":reference,
                 "real_output":decoded,"devanagari_ratio":ratio,"exact_match":decoded==reference}
            rows.append(row)
            print("OBSERVED",json.dumps(row,ensure_ascii=False),flush=True)
    Path("gec-candidate-evidence.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    print("BOTH_PROMPT_VARIANTS_MODEL_EXECUTED",flush=True)
    # A successful inference run is NOT evidence of grammatical quality.
    assert any(row["real_output"] for row in rows)


if __name__=="__main__":
    main()
