"""Optional REAL, separately attributed model-backed language services.

These are not BharatGen or IndicTrans2. They use an open Hindi GEC checkpoint
and an open Hindi->English translation checkpoint. No example sentences, rules,
or fixed responses are returned as model predictions.
"""
from __future__ import annotations

from functools import lru_cache
from contextlib import nullcontext

GEC_MODEL = "manavdhamecha77/GEC-mT5-Small-Hindi"
TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-hi-en"
MAX_TEXT_CHARS = 500


class LanguageModelError(RuntimeError):
    """Requested model is unavailable or failed to generate usable output."""


def validate_hindi(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please convert or enter Hindi text first.")
    text = text.strip()
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError("Hindi text exceeds the 500-character limit.")
    if not any("\u0900" <= char <= "\u097f" for char in text):
        raise ValueError("The input must contain Devanagari Hindi.")
    return text


@lru_cache(maxsize=1)
def load_hindi_gec():
    """Lazy-load the public MIT-licensed Hindi grammar correction model."""
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(GEC_MODEL, trust_remote_code=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        GEC_MODEL, trust_remote_code=False, use_safetensors=True
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device


@lru_cache(maxsize=1)
def load_hi_en():
    """Lazy-load Apache-2.0 Helsinki OPUS-MT; NOT AI4Bharat IndicTrans2."""
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(TRANSLATION_MODEL, trust_remote_code=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        TRANSLATION_MODEL, trust_remote_code=False
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    return tokenizer, model, device


def _inference_context():
    # A fake model injected by unit tests does not need PyTorch installed.
    # Production model loaders always import PyTorch and fail loudly without it.
    try:
        import torch
    except ModuleNotFoundError:
        return nullcontext()
    return torch.inference_mode()


def generate_hindi_gec(text: str, resources=None) -> str:
    """Run genuine MT5 generation. Do not claim output is always an improvement."""
    sentence = validate_hindi(text)
    tokenizer, model, device = resources if resources is not None else load_hindi_gec()
    # The model author's training uses the literal 'correct this: ' prefix.
    encoded = tokenizer(
        "correct this: " + sentence, return_tensors="pt",
        truncation=False
    )
    if encoded["input_ids"].shape[-1] > 128:
        raise ValueError("Sentence is too long for the Hindi grammar model (128 tokens).")
    encoded = {k: v.to(device) for k, v in encoded.items()}
    with _inference_context():
        outputs = model.generate(**encoded, max_new_tokens=128, num_beams=4)
    candidate = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    if not candidate or not candidate[0].strip():
        raise LanguageModelError("Hindi GEC model returned an empty prediction.")
    return candidate[0].strip()


def generate_english(text: str, resources=None) -> str:
    """Run actual pretrained Hindi->English translation, without substitution."""

    sentence = validate_hindi(text)
    tokenizer, model, device = resources if resources is not None else load_hi_en()
    encoded = tokenizer(sentence, return_tensors="pt", truncation=False)
    if encoded["input_ids"].shape[-1] > 256:
        raise ValueError("Sentence is too long for the translation model (256 tokens).")
    encoded = {k: v.to(device) for k, v in encoded.items()}
    with _inference_context():
        outputs = model.generate(**encoded, max_new_tokens=160, num_beams=4)
    candidate = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    if not candidate or not candidate[0].strip():
        raise LanguageModelError("Translation model returned an empty prediction.")
    return candidate[0].strip()
