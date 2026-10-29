"""Unit tests use injected fake CTranslate2; no checkpoint inference claim."""
import pytest
from indicwrite.ct2_engine import CTranslate2IndicXlit


class FakeResult:
    hypotheses = [["न", "म", "स", "्", "त", "े"]]


class FakeTranslator:
    def __init__(self):
        self.requests = []

    def translate_batch(self, batch, **kwargs):
        self.requests.append((batch, kwargs))
        return [FakeResult()]


def test_converted_engine_dispatches_real_api_contract():
    fake = FakeTranslator()
    model = CTranslate2IndicXlit(fake, "fake-revision")
    assert model.translit_word("namaste") == {"hi": ["नमस्ते"]}
    assert fake.requests == [([["__hi__"] + list("namaste")], {"beam_size": 4, "num_hypotheses": 1})]


@pytest.mark.parametrize("word", ["", "has space", "मैं", "a1", None])
def test_converted_engine_rejects_invalid_words(word):
    with pytest.raises(ValueError):
        CTranslate2IndicXlit(FakeTranslator(), "fixture").translit_word(word)


def test_converted_engine_rejects_unsupported_topk():
    with pytest.raises(ValueError):
        CTranslate2IndicXlit(FakeTranslator(), "fixture").translit_word("namaste", topk=9)
