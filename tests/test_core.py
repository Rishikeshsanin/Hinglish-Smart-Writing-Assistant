"""Unit tests of text plumbing only. The fake engine is NOT neural inference."""

import pytest

from indicwrite.core import (
    InputError, ModelOutputError, parse_preserve_terms, transliterate_text,
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
    assert parse_preserve_terms("Python, EMAIL,  , 3d, can't") == {"python", "email"}


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
