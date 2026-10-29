"""Research comparison: explicitly non-sovereign Apache-2.0 Qwen 0.5B Instruct.
Actual generated predictions only; never label this checkpoint BharatGen.
"""
import json, platform
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL="Qwen/Qwen2.5-0.5B-Instruct"
CASES=[
["मैं स्कूल जाता है।","मैं स्कूल जाता हूँ।"],
["राम ने ने खाना खाया।","राम ने खाना खाया।"],
["वे किताबें पढ़ता है।","वे किताबें पढ़ते हैं।"],
["आज मैं कॉलेज गए।","आज मैं कॉलेज गया।"],
["मुझे दो किताब चाहिए।","मुझे दो किताबें चाहिए।"]
]

def main():
    print("CHECKPOINT",MODEL,"torch",torch.__version__,"Python",platform.python_version(),flush=True)
    tokenizer=AutoTokenizer.from_pretrained(MODEL,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(MODEL,trust_remote_code=False,torch_dtype=torch.float32,use_safetensors=True)
    model.eval()
    results=[]
    for original,reference in CASES:
        conversation=[
          {"role":"system","content":"आप एक सावधान हिंदी भाषा संपादक हैं। दिए गए वाक्य की व्याकरण और वर्तनी सुधारें। अर्थ, नाम और तथ्य न बदलें। केवल सुधरा हुआ हिंदी वाक्य दें, बिना किसी व्याख्या के।"},
          {"role":"user","content":"इस हिंदी वाक्य को सही करें: "+original}
        ]
        prompt=tokenizer.apply_chat_template(conversation,tokenize=False,add_generation_prompt=True)
        encoding=tokenizer(prompt,return_tensors="pt")
        with torch.inference_mode():
            generated=model.generate(**encoding,max_new_tokens=72,do_sample=False,pad_token_id=tokenizer.eos_token_id)
        result=tokenizer.decode(generated[0][encoding["input_ids"].shape[-1]:],skip_special_tokens=True).strip()
        row={"input":original,"reference":reference,"actual_output":result,"exact_match":result==reference}
        results.append(row)
        print("QWEN_ACTUAL",json.dumps(row,ensure_ascii=False),flush=True)
    with open("qwen-research-results.json","w",encoding="utf-8") as fp:
        json.dump(results,fp,ensure_ascii=False,indent=2)
    print("QWEN_REAL_MODEL_EXECUTED",flush=True)


if __name__=="__main__":
    main()
