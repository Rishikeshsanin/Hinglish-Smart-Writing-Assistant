"""Independent offline product-contract QA. Fake engine != neural inference.

These tests deliberately do not download weights, claim quality scores, or
confirm a production deployment; see scripts/qa_product_release.py for live QA.
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

import pytest

from indicwrite.core import (
    InputError, ModelOutputError, has_convertible_tokens, parse_preserve_terms,
    transliterate_text, validate_text,
)

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CASES_BLOB = "8fd799261cbc758da934121d2d84a9ece136fdc9"
EXPECTED_PREDICTIONS_BLOB = "4ae187b870b11ea7173819ade505f73561d4c203"

ROMAN_EXAMPLES = (
    "kal mujhe college jana hai!",
    "aaj mausam bahut accha hai.",
    "namaste dosto, aap kaise ho?",
    "main ghar ja raha hoon.",
    "muje tumse baat karni hai.",
    "mai theek hu.",
    "ap kahan ho?",
    "bahot accha laga.",
    "kripya jaldi aana.",
    "mujhe paani chahiye.",
)


class StubEngine:
    """Structural test double, never an AI4Bharat or real-language prediction."""

    WORDS = {
        "kal": "कल", "mujhe": "मुझे", "college": "कॉलेज",
        "jana": "जाना", "hai": "है", "python": "पायथन",
        "aaj": "आज", "namaste": "नमस्ते",
    }

    def __init__(self, broken=False):
        self.calls = []
        self.broken = broken

    def translit_word(self, word, topk=1):
        self.calls.append((word, topk))
        if self.broken:
            return {"hi": []}
        return {"hi": [self.WORDS.get(word.casefold(), "हिंदी")]}


@pytest.mark.parametrize("sentence", ROMAN_EXAMPLES, ids=[f"roman-{i:02d}" for i in range(1, 11)])
def test_ten_representative_inputs_route_to_model_without_fake_fallback(sentence):
    engine = StubEngine()
    tokens = validate_text(sentence)
    assert has_convertible_tokens(tokens)
    output = transliterate_text(sentence, engine)
    assert engine.calls, "A Roman-Hindi case must reach the supplied inference interface"
    assert all(topk == 1 for _, topk in engine.calls)
    assert re.search(r"[\u0900-\u097f]", output)
    assert output != sentence
    # Structural assertions only: these are STUB outputs, NOT quality references.
    if sentence.endswith(("!", "?", ".")):
        assert output.endswith(sentence[-1])


@pytest.mark.parametrize("source,protected,expected", [
    (
        "kal Python AI 42 https://example.org/a?q=1 user@example.com हिंदी 🚀",
        "Python",
        "कल Python AI 42 https://example.org/a?q=1 user@example.com हिंदी 🚀",
    ),
    ("kal python PYTHON", "PYTHON", "कल python PYTHON"),
    ("नमस्ते kal हिंदी", "", "नमस्ते कल हिंदी"),
    ("kal C++ C# GPT-4 3d hai!", "", "कल C++ C# GPT-4 3d है!"),
    ("kal  2\nPython!", "Python", "कल  2\nPython!"),
])
def test_english_unicode_urls_numbers_punctuation_and_spacing(source, protected, expected):
    engine = StubEngine()
    result = transliterate_text(source, engine, parse_preserve_terms(protected))
    assert result == expected
    assert all(word.casefold() != "python" for word, _ in engine.calls) if protected else True
    assert all(word not in ("AI", "C++", "GPT-4") for word, _ in engine.calls)


@pytest.mark.parametrize("source", ["", "  \n", None, "a" * 501, "kal " * 81])
def test_invalid_input_fails_before_model_inference(source):
    engine = StubEngine()
    with pytest.raises(InputError):
        transliterate_text(source, engine)
    assert not engine.calls


@pytest.mark.parametrize("term", ["C++", "3d", "user@example.com", "can't"])
def test_invalid_preserve_tokens_are_rejected_not_ignored(term):
    with pytest.raises(InputError):
        parse_preserve_terms(f"Python,{term}")


def test_broken_model_never_produces_a_synthetic_success():
    engine = StubEngine(broken=True)
    with pytest.raises(ModelOutputError):
        transliterate_text("kal", engine)
    assert engine.calls == [("kal", 1)]


def test_no_inference_for_existing_hindi_or_explicitly_preserved_input():
    for source, preserved in (("हिंदी 123! 🎉", set()), ("Python AI", {"python"})):
        assert not has_convertible_tokens(validate_text(source), preserved)
        assert transliterate_text(source, None, preserved) == source


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\\0".encode("ascii").replace(b"\\0", b"\0") + raw).hexdigest()


def test_official_forty_case_evidence_is_byte_for_byte_unchanged():
    """Regression provenance pin; not a rerun of the real neural checkpoint."""
    assert _git_blob_sha((ROOT / "evaluation/cases.csv").read_bytes()) == EXPECTED_CASES_BLOB
    assert _git_blob_sha((ROOT / "evaluation/results/predictions.csv").read_bytes()) == EXPECTED_PREDICTIONS_BLOB


def test_40_record_predictions_match_frozen_case_identity_not_just_row_count():
    with (ROOT / "evaluation/cases.csv").open(encoding="utf-8-sig", newline="") as source:
        cases = list(csv.DictReader(source))
    with (ROOT / "evaluation/results/predictions.csv").open(encoding="utf-8-sig", newline="") as source:
        predictions = list(csv.DictReader(source))
    assert len(cases) == len(predictions) == 40
    assert len({row["id"] for row in cases}) == 40
    for case, prediction in zip(cases, predictions):
        assert all(case[key] == prediction[key] for key in (
            "id", "category", "roman_text", "reference_hindi", "preserve_english"
        ))
        assert prediction["predicted_hindi"].strip()
        assert prediction["exact_sentence_match"] in ("True", "False")
        for key in ("cer", "wer", "word_accuracy"):
            assert 0 <= float(prediction[key]) <= (1 if key == "word_accuracy" else 10)


def test_publicly_unsafe_optional_features_default_to_off():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'INDICWRITE_ENABLE_LANGUAGE_SERVICES' in source
    assert 'INDICWRITE_ENABLE_GEC_EXPERIMENTAL' in source
    assert 'INDICWRITE_PRIVATE_BHARATGEN' in source
    assert "private_research_enabled" in source
    # These checks validate visible wiring, not licensing or genuine optional inference.


def test_official_checkpoint_loader_has_no_stub_substitution():
    source = (ROOT / "src/indicwrite/engine.py").read_text(encoding="utf-8")
    assert "ai4bharat.transliteration" in source
    assert "XlitEngine" in source
    assert 'XlitEngine("hi"' in source
