"""Unit tests of text plumbing only. The fake engine is NOT neural inference."""

import pytest

from indicwrite.core import (
    InputError, ModelOutputError, parse_preserve_terms, transliterate_text,
    validate_text, has_convertible_tokens,
)


class FakeEngine:
    def __init__(self):
        self.calls = []
        self.words = {
            "kal": "कल", "main": "मैं", "mujhe": "मुझे", "jana": "जाना",
            "hai": "है", "baje": "बजे", "aaunga": "आऊँगा",
            "namaste": "नमस्ते", "python": "पायथन",
        }

    def translit_word(self, word, topk=1):
        self.calls.append((word, topk))
        return {"hi": [self.words.get(word.casefold(), "अज्ञात")]}


def test_preserves_punctuation_spaces_numbers_existing_hindi():
    engine = FakeEngine()
    text = "Kal,  main 2 baje aaunga! AI ठीक है.\n"
    result = transliterate_text(text, engine)
    assert result == "कल,  मैं 2 बजे आऊँगा! AI ठीक है.\n"
    assert ("Kal", 1) in engine.calls
    assert all(token != "AI" for token, _ in engine.calls)


def test_explicit_english_words_remain_unchanged():
    engine = FakeEngine()
    result = transliterate_text(
        "kal Python hai", engine, preserve_terms=parse_preserve_terms("PYTHON, email")
    )
    assert result == "कल Python है"
    assert all(token != "Python" for token, _ in engine.calls)


def test_repeated_words_use_one_model_prediction():
    engine = FakeEngine()
    assert transliterate_text("kal kal kal", engine) == "कल कल कल"
    assert len(engine.calls) == 1


@pytest.mark.parametrize("value", ["", "  \n\t", "a" * 501, None])
def test_rejects_bad_input(value):
    with pytest.raises(InputError):
        transliterate_text(value, FakeEngine())


def test_caps_roman_word_count():
    with pytest.raises(InputError, match="80"):
        transliterate_text("kal " * 81, FakeEngine())


def test_preserve_terms_filter():
    assert parse_preserve_terms("Python, EMAIL,  , ") == {"python", "email"}


def test_invalid_model_response_not_silently_faked():
    class BrokenEngine:
        def translit_word(self, word, topk=1):
            return {"hi": []}

    with pytest.raises(ModelOutputError):
        transliterate_text("namaste", BrokenEngine())


def test_no_roman_characters_yields_unmodified_input():
    engine = FakeEngine()
    assert transliterate_text("हिंदी 123! 🎉", engine) == "हिंदी 123! 🎉"
    assert engine.calls == []


@pytest.mark.parametrize("bad", ["3d", "can't", "C++", "user@example.com", "e-mail"])
def test_unsupported_preservation_terms_raise_instead_of_ignoring(bad):
    with pytest.raises(InputError, match="unsupported"):
        parse_preserve_terms("Python, " + bad)


def test_preflight_rejects_81_tokens():
    with pytest.raises(InputError, match="80"):
        validate_text("kal " * 81)


def test_preflight_handles_exact_limits():
    assert len(validate_text("a" * 500)) == 1
    assert len(validate_text("kal " * 79 + "kal")) > 0


def test_preflight_skips_model_for_unmodified_hindi_and_protected_terms():
    assert not has_convertible_tokens(validate_text("हिंदी 123! 🎉"))
    assert not has_convertible_tokens(validate_text("Python AI"), {"python"})
    assert has_convertible_tokens(validate_text("kal Python AI"), {"python"})


def test_noop_with_no_model_is_not_an_inference_claim():
    assert transliterate_text("हिंदी 123!", None) == "हिंदी 123!"
    assert transliterate_text("Python AI", None, {"python"}) == "Python AI"


@pytest.mark.parametrize("source", [
    "café", "cafe\u0301", "naïve", "Zoë", "namस्ते",
    "user@example.com", "https://example.com/a?q=1",
    "www.example.org", "C++", "C#", "GPT-4", "3d",
])
def test_unicode_and_structured_tokens_bypass_model_entirely(source):
    engine = FakeEngine()
    assert transliterate_text(source, engine) == source
    assert engine.calls == []


def test_structured_identifiers_and_normal_hinglish_coexist():
    engine = FakeEngine()
    result = transliterate_text("kal C++ aur user@example.com hai!", engine)
    assert result == "कल C++ अज्ञात user@example.com है!"
    assert [word for word, _ in engine.calls] == ["kal", "aur", "hai"]
