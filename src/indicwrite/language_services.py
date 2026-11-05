"""Optional REAL, separately attributed model-backed language services.

These are not BharatGen or IndicTrans2. They use an open Hindi GEC checkpoint
and an open Hindi->English translation checkpoint. No example sentences, rules,
or fixed responses are returned as model predictions.
"""
from __future__ import annotations

from functools import lru_cache
from contextlib import nullcontext
from collections import Counter
import os
import re
from typing import Mapping

GEC_MODEL = "manavdhamecha77/GEC-mT5-Small-Hindi"
TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-hi-en"
MAX_TEXT_CHARS = 500


class LanguageModelError(RuntimeError):
    """Requested model is unavailable or failed to generate usable output."""


class LanguageFeatureDisabled(LanguageModelError):
    """A feature cannot be exposed because its opt-in or release gate is closed."""


def capability_status(
    feature: str, environment: Mapping[str, str] | None = None,
) -> dict[str, str | bool]:
    """Metadata-only public contract: never downloads weights or implies quality."""
    env = os.environ if environment is None else environment
    if feature == "opus_hi_en":
        enabled = env.get("INDICWRITE_ENABLE_LANGUAGE_SERVICES") == "1"
        return {
            "feature": feature, "enabled": enabled,
            "model_id": TRANSLATION_MODEL, "provider": "Helsinki-NLP",
            "model_family": "OPUS-MT",
            "evidence": "Two real-model smoke sentences and one browser flow; NOT a quality benchmark.",
            "reason": "Opt-in OPUS-MT Hindi to English; quality requires human review."
                      if enabled else "Set INDICWRITE_ENABLE_LANGUAGE_SERVICES=1 in a supported local environment.",
        }
    if feature == "hindi_gec":
        return {
            "feature": feature, "enabled": False, "model_id": GEC_MODEL,
            "provider": "Independent research checkpoint",
            "reason": "Known grammar checkpoint failed real-output quality review; research-only API is not a product feature.",
        }
    if feature == "indictrans2":
        return {
            "feature": feature, "enabled": False,
            "model_id": "ai4bharat/indictrans2-indic-en-dist-200M",
            "provider": "AI4Bharat",
            "reason": "Gated model access not granted or tested; no unauthorized checkpoint download or substitute.",
        }
    if feature == "bharatgen_public":
        return {
            "feature": feature, "enabled": False,
            "model_id": "bharatgenai/Param-1-2.9B-Instruct",
            "provider": "BharatGen",
            "reason": "Conflicting historical license terms, no public-output permission or independent quality review.",
        }
    raise ValueError(f"Unknown optional language feature: {feature}")


_LATIN_TERM = re.compile(r"[A-Za-z][A-Za-z0-9_+.#-]*")
_DIGIT_GROUP = re.compile(r"\d+", flags=re.UNICODE)
_MEANING_CUES = ("नहीं", "शायद", "अगर", "बिना", "मत")


def preservation_warnings(
    source: str, candidate: str, *, translation: bool = False,
) -> list[str]:
    """Conservative string-level alerts, NOT an automatic semantic certification.

    This can miss paraphrased negation, changed roles, dates in words, omitted
    entities, hallucinations and word-sense errors. Human review is mandatory.
    """
    if not isinstance(source, str) or not isinstance(candidate, str):
        raise TypeError("Source and candidate must be text.")
    warnings: list[str] = []
    if Counter(_DIGIT_GROUP.findall(source)) != Counter(_DIGIT_GROUP.findall(candidate)):
        warnings.append("Digits or numeric quantities changed; verify facts manually.")
    before = Counter(x.casefold() for x in _LATIN_TERM.findall(source))
    after = Counter(x.casefold() for x in _LATIN_TERM.findall(candidate))
    if any(after[term] < count for term, count in before.items()):
        warnings.append("An English name or technical term changed or disappeared.")
    if not translation:
        for cue in _MEANING_CUES:
            if cue in source and cue not in candidate:
                warnings.append(f"Meaning-bearing cue {cue!r} was removed.")
    if source.strip() == candidate.strip():
        warnings.append("The model returned the text unchanged; no correction was needed or made.")
    return warnings


def translate_optional(
    text: str, *, environment: Mapping[str, str] | None = None, resources=None,
) -> dict[str, object]:
    """Agent-facing opt-in contract. No model download while disabled.

    Use generate_english() only in already-authorized research smoke tests or
    the legacy opt-in UI. A successful generation is NOT proven translation quality.
    """
    capability = capability_status("opus_hi_en", environment)
    if not capability["enabled"]:
        raise LanguageFeatureDisabled(str(capability["reason"]))
    source = validate_hindi(text)
    output = generate_english(source, resources)
    return {
        "source": source,
        "candidate": output,
        "model_id": TRANSLATION_MODEL,
        "model_family": "OPUS-MT (not IndicTrans2)",
        "warnings": preservation_warnings(source, output, translation=True),
        "meaning_preservation": "REQUIRES_HUMAN_REVIEW",
        "auto_apply": False,
    }


def rewrite_optional(text: str, *, environment: Mapping[str, str] | None = None) -> str:
    """Fail closed: unsuccessful mT5/Qwen candidates must not be product features."""
    capability = capability_status("hindi_gec", environment)
    raise LanguageFeatureDisabled(str(capability["reason"]))


def translate_indictrans2(text: str, *, environment: Mapping[str, str] | None = None) -> str:
    """Never relabel the real Helsinki model as gated AI4Bharat IndicTrans2."""
    capability = capability_status("indictrans2", environment)
    raise LanguageFeatureDisabled(str(capability["reason"]))


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


def validate_rewrite_candidate(original: str, candidate: str) -> str:
    """Research-only hard reject for obvious script and preservation failures.

    Passing these checks never certifies grammar or meaning preservation.
    """
    if not isinstance(candidate, str) or not candidate.strip():
        raise LanguageModelError("Grammar model returned empty text.")
    candidate = candidate.strip()
    letters = [ch for ch in candidate if ch.isalpha()]
    proportion = (
        sum(chr(0x0900) <= ch <= chr(0x097f) for ch in letters) / len(letters)
        if letters else 0.0
    )
    if proportion < 0.85:
        raise LanguageModelError("Grammar model drifted into a different script; prediction rejected.")
    warnings = preservation_warnings(original, candidate)
    for warning in warnings:
        if "numeric" in warning:
            raise LanguageModelError("Grammar model changed, added, or omitted a number; prediction rejected.")
        if "technical term" in warning:
            raise LanguageModelError("Grammar model changed an English term; prediction rejected.")
        if "Meaning-bearing cue" in warning:
            raise LanguageModelError("Grammar model removed a meaning-bearing cue; prediction rejected.")
    return candidate


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
    return validate_rewrite_candidate(sentence, candidate[0])


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
    output = candidate[0].strip()
    if not re.search(r"[A-Za-z]", output):
        raise LanguageModelError("Translation model did not return English text.")
    return output
