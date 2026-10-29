"""Tests for wiring and validation; not claims of neural model execution."""

import pytest

from indicwrite.language_services import (
    GEC_MODEL, TRANSLATION_MODEL, generate_hindi_gec,
    generate_english, validate_hindi, LanguageModelError,
)


class FakeTokens:
    def __init__(self, length):
        self.shape = (1, length)

    def to(self, device):
        return self


class FakeTokenizer:
    def __init__(self, value, length=20):
        self.value = value
        self.length = length
        self.inputs = []

    def __call__(self, text, **kwargs):
        self.inputs.append(text)
        return {"input_ids": FakeTokens(self.length)}

    def batch_decode(self, tokens, **kwargs):
        return [self.value]


class FakeModel:
    def __init__(self):
        self.calls = []

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        return [[1, 2, 3]]


def test_model_ids_are_explicit_and_separate_from_bharatgen_indictrans2():
    assert GEC_MODEL == "manavdhamecha77/GEC-mT5-Small-Hindi"
    assert TRANSLATION_MODEL == "Helsinki-NLP/opus-mt-hi-en"


def test_hindi_validation():
    assert validate_hindi("  मैं यहाँ हूँ। ") == "मैं यहाँ हूँ।"
    for bad in ("", "  ", "hello", "अ" * 501, None):
        with pytest.raises(ValueError):
            validate_hindi(bad)


def test_gec_calls_generation_and_uses_author_prefix():
    tokenizer = FakeTokenizer("मैं स्कूल जाता हूँ।")
    model = FakeModel()
    output = generate_hindi_gec("मैं स्कूल जाता है।", (tokenizer, model, "cpu"))
    assert output == "मैं स्कूल जाता हूँ।"
    assert tokenizer.inputs == ["correct this: मैं स्कूल जाता है।"]
    assert len(model.calls) == 1


def test_translation_calls_model_not_dictionary():
    tokenizer = FakeTokenizer("I am at home.")
    model = FakeModel()
    output = generate_english("मैं घर में हूँ।", (tokenizer, model, "cpu"))
    assert output == "I am at home."
    assert len(model.calls) == 1


def test_gec_does_not_silently_truncate():
    with pytest.raises(ValueError, match="128"):
        generate_hindi_gec("मैं यहाँ हूँ।", (FakeTokenizer("anything", 129), FakeModel(), "cpu"))


def test_empty_model_reply_is_error():
    with pytest.raises(LanguageModelError):
        generate_english("मैं यहाँ हूँ।", (FakeTokenizer(""), FakeModel(), "cpu"))

def test_wrong_script_correction_rejected():
    from indicwrite.language_services import validate_rewrite_candidate
    with pytest.raises(LanguageModelError, match="script"):
        validate_rewrite_candidate("मैं स्कूल जाता है।", "আমি স্কুলে যাবে?")


def test_changed_number_rejected():
    from indicwrite.language_services import validate_rewrite_candidate
    with pytest.raises(LanguageModelError, match="number"):
        validate_rewrite_candidate("मेरे पास 2 किताब हैं।", "मेरे पास 3 किताब हैं।")


def test_valid_hindi_candidate_passes_safeguard():
    from indicwrite.language_services import validate_rewrite_candidate
    assert validate_rewrite_candidate("मैं स्कूल जाता है।", "मैं स्कूल जाता हूँ।") == "मैं स्कूल जाता हूँ।"
