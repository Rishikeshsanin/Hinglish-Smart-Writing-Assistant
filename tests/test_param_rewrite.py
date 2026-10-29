"""Source-level tests only; model weights/inference not used here."""

import pytest

from indicwrite.param_rewrite import build_messages, MODEL_ID


def test_model_identifier_is_real():
    assert MODEL_ID == "bharatgenai/Param-1-2.9B-Instruct"


def test_hindi_prompt_preserves_meaning():
    messages = build_messages("कल मुझे कॉलेज जाना है।")
    assert [m["role"] for m in messages] == ["system", "user"]
    assert "मूल अर्थ न बदलें" in messages[0]["content"]
    assert messages[1]["content"].endswith("कल मुझे कॉलेज जाना है।")


@pytest.mark.parametrize("text", ["", "    ", "hello world", "अ" * 501])
def test_hindi_rewrite_validation(text):
    with pytest.raises(ValueError):
        build_messages(text)


def test_rewrite_request_not_a_hardcoded_prediction():
    messages = build_messages("मेरा नाम राहुल है।")
    assert "मेरा नाम राहुल है।" in messages[1]["content"]
    assert "सुधरा हुआ हिंदी वाक्य" in messages[0]["content"]

def test_model_has_explicit_experimental_loader():
    from indicwrite.param_rewrite import BharatGenRewriter
    assert callable(BharatGenRewriter.load)
