"""Experimental integration for BharatGen Param-1-2.9B-Instruct.

IMPORTANT: This module is not part of the verified IndicXlit MVP.
It performs real Transformers inference if explicitly executed and model files
can be downloaded. No hardcoded/generated example is returned as a result.
"""

from __future__ import annotations

from dataclasses import dataclass

MODEL_ID = "bharatgenai/Param-1-2.9B-Instruct"
# Pin remote custom code and weights to an immutable repository revision. Update
# only after reviewing the new model files and rerunning genuine inference.
MODEL_REVISION = "2024ac968cf289ba1cb6fde112a9abb437813b79"
MAX_INPUT_CHARS = 500
MAX_NEW_TOKENS = 120


class RewriteError(RuntimeError):
    """Raised when model inference fails or no usable text is returned."""


def build_messages(hindi: str) -> list[dict[str, str]]:
    """Construct a conservative Hindi rewriting instruction for the real model."""
    if not isinstance(hindi, str) or not hindi.strip():
        raise ValueError("Hindi text is required.")
    if len(hindi) > MAX_INPUT_CHARS:
        raise ValueError(f"Maximum Hindi input is {MAX_INPUT_CHARS} characters.")
    if not any("\u0900" <= ch <= "\u097f" for ch in hindi):
        raise ValueError("Provide Hindi (Devanagari) text; transliterate first.")
    return [
        {
            "role": "system",
            "content": (
                "आप एक हिंदी लेखन-सुधार सहायक हैं। व्याकरण और स्पष्टता "
                "सुधारें। नाम, तथ्य, समय, संख्या और मूल अर्थ न बदलें। "
                "नई जानकारी न जोड़ें। केवल सुधरा हुआ हिंदी वाक्य लिखें, "
                "बिना भूमिका या व्याख्या के।"
            ),
        },
        {
            "role": "user",
            "content": "वाक्य सुधारें:\n" + hindi.strip(),
        },
    ]


@dataclass
class BharatGenRewriter:
    tokenizer: object
    model: object

    @classmethod
    def load(cls) -> "BharatGenRewriter":
        """Download/load official model only through explicit experimental entrypoint.

        ~2.9B bf16 parameters => ~5.8 GB weights alone. Requires enough CPU/GPU
        memory and optional dependencies; never called by default Streamlit app.
        Trust remote code only after personally reviewing the HF model source.
        """
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            trust_remote_code=False,
        )
        # T4 GPUs common in free notebooks do not support BF16; choose FP16 there.
        # BF16 is preferred when the CUDA device supports it.
        if not torch.cuda.is_available():
            # FP32 is the broadly supported CPU path. It needs substantially
            # more RAM than the GPU path, so CPU execution is discouraged.
            dtype = torch.float32
        elif torch.cuda.is_bf16_supported():
            dtype = torch.bfloat16
        else:
            dtype = torch.float16
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            trust_remote_code=True,
            torch_dtype=dtype,
            device_map="auto",
            low_cpu_mem_usage=True,
        )
        model.eval()
        return cls(tokenizer=tokenizer, model=model)

    def rewrite(self, hindi: str) -> str:
        """Run real forward generation and return only newly decoded tokens."""
        import torch

        messages = build_messages(hindi)
        inputs = self.tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            add_generation_prompt=True,
        )
        inputs = inputs.to(self.model.device)
        with torch.inference_mode():
            generated = self.model.generate(
                inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                use_cache=False,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=(
                    self.tokenizer.pad_token_id
                    if self.tokenizer.pad_token_id is not None
                    else self.tokenizer.eos_token_id
                ),
            )
        if len(generated) == 0:
            raise RewriteError("Model generated no sequences.")
        new_tokens = generated[0][inputs.shape[-1]:]
        output = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        if not output:
            raise RewriteError("BharatGen generated an empty response.")
        return output
