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


def test_added_number_rejected():
    from indicwrite.language_services import validate_rewrite_candidate
    with pytest.raises(LanguageModelError, match="number"):
        validate_rewrite_candidate("मेरे पास 2 किताब हैं।", "मेरे पास 2 या 3 किताबें हैं।")


def test_valid_hindi_candidate_passes_safeguard():
    from indicwrite.language_services import validate_rewrite_candidate
    assert validate_rewrite_candidate("मैं स्कूल जाता है।", "मैं स्कूल जाता हूँ।") == "मैं स्कूल जाता हूँ।"


def test_public_optional_gates_fail_closed_even_when_env_is_set(monkeypatch):
    from indicwrite.language_services import (
        capability_status, rewrite_optional, translate_indictrans2,
        LanguageFeatureDisabled,
    )
    assert not capability_status("opus_hi_en", {})["enabled"]
    assert capability_status("opus_hi_en", {"INDICWRITE_ENABLE_LANGUAGE_SERVICES": "1"})["enabled"]
    assert not capability_status("indictrans2", {"INDICWRITE_ENABLE_LANGUAGE_SERVICES": "1"})["enabled"]
    assert not capability_status("hindi_gec", {"INDICWRITE_ENABLE_GEC_EXPERIMENTAL": "1"})["enabled"]
    assert not capability_status("bharatgen_public", {})["enabled"]
    with pytest.raises(LanguageFeatureDisabled):
        rewrite_optional("मैं यहाँ हूँ।", environment={"INDICWRITE_ENABLE_GEC_EXPERIMENTAL": "1"})
    with pytest.raises(LanguageFeatureDisabled):
        translate_indictrans2("मैं यहाँ हूँ।")
    with pytest.raises(ValueError, match="Unknown"):
        capability_status("not_a_real_model", {})


def test_optional_translation_never_loads_when_disabled(monkeypatch):
    from indicwrite import language_services as service
    monkeypatch.setattr(service, "load_hi_en", lambda: (_ for _ in ()).throw(AssertionError("download attempted")))
    with pytest.raises(service.LanguageFeatureDisabled):
        service.translate_optional("मैं यहाँ हूँ।", environment={})


def test_optional_translation_returns_real_model_attribution_not_a_quality_claim():
    from indicwrite.language_services import translate_optional
    tokenizer = FakeTokenizer("I am learning Python 4.")
    model = FakeModel()
    record = translate_optional(
        "मैं Python 3 सीख रहा हूँ।",
        environment={"INDICWRITE_ENABLE_LANGUAGE_SERVICES": "1"},
        resources=(tokenizer, model, "cpu"),
    )
    assert record["model_id"] == TRANSLATION_MODEL
    assert record["model_family"] == "OPUS-MT (not IndicTrans2)"
    assert record["meaning_preservation"] == "REQUIRES_HUMAN_REVIEW"
    assert not record["auto_apply"]
    assert len(model.calls) == 1
    assert any("numeric" in warning for warning in record["warnings"])


def test_unicode_digits_english_terms_and_negation_are_monitored():
    from indicwrite.language_services import preservation_warnings
    alerts = preservation_warnings(
        "मैं Python ३ सीखना नहीं चाहता।",
        "मैं Java ४ सीखना चाहता।",
    )
    assert any("numeric" in warning for warning in alerts)
    assert any("technical" in warning for warning in alerts)
    assert any("नहीं" in warning for warning in alerts)


def test_code_mixed_hindi_rewrite_preserving_term_is_allowed():
    from indicwrite.language_services import validate_rewrite_candidate
    source = "मैं Python सीखता है।"
    assert validate_rewrite_candidate(source, "मैं Python सीखता हूँ।") == "मैं Python सीखता हूँ।"


def test_dropped_english_term_or_negation_rejected():
    from indicwrite.language_services import validate_rewrite_candidate
    with pytest.raises(LanguageModelError, match="English term"):
        validate_rewrite_candidate("मैं Python सीखता है।", "मैं पायथन सीखता हूँ।")
    with pytest.raises(LanguageModelError, match="cue"):
        validate_rewrite_candidate("मैं नहीं जाता है।", "मैं जाता हूँ।")


def test_non_english_translation_output_is_rejected():
    with pytest.raises(LanguageModelError, match="English"):
        generate_english("मैं यहाँ हूँ।", (FakeTokenizer("मैं यहाँ हूँ।"), FakeModel(), "cpu"))
