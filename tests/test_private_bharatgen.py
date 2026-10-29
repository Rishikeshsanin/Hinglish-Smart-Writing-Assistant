"""Local research gating and output safeguards; fake records are not inference."""
import pytest
from indicwrite.private_bharatgen import (
    RESEARCH_FLAGS, private_research_enabled, review_candidate, run_private_research,
)


def env_flags():
    return {name: "1" for name in RESEARCH_FLAGS}


def test_gate_closed_without_explicit_approval_or_private_address():
    env = env_flags()
    assert private_research_enabled(env, "127.0.0.1")
    assert private_research_enabled(env, "localhost")
    assert not private_research_enabled(env, "0.0.0.0")
    assert not private_research_enabled(env, None)
    assert not private_research_enabled(env, "example.com")
    for name in RESEARCH_FLAGS:
        settings = {**env, name: "0"}
        assert not private_research_enabled(settings, "127.0.0.1")


def test_cannot_infer_without_authorization_even_with_fake_engine():
    class Fake:
        def generate_record(self, original):
            raise AssertionError("Should not reach model")
    with pytest.raises(PermissionError):
        run_private_research("मैं घर में हूँ।", engine=Fake(), environment={}, server_address="127.0.0.1")


def test_preflight_blocks_invalid_input_before_model_use():
    class Fake:
        def generate_record(self, original):
            raise AssertionError("Should not reach model")
    with pytest.raises(ValueError):
        run_private_research("English only", engine=Fake(), environment=env_flags(), server_address="127.0.0.1")


def test_technical_terms_and_numbers_trigger_warning():
    result = review_candidate(
        "मैं Python 3 और Java 21 सीखता हूँ।",
        "मैं पायथन 4 और जावा सीखता हूँ।",
    )
    assert any("technical" in item for item in result)
    assert any("numeric" in item for item in result)


def test_negation_warning_and_unchanged_output():
    assert any("नहीं" in flag for flag in review_candidate("मैं नहीं गया।", "मैं गया।"))
    assert any("unchanged" in flag for flag in review_candidate("मैं आऊँगा।", "मैं आऊँगा।"))


def test_valid_fake_record_kept_as_suggestion_not_automatic_edit():
    class Fake:
        def generate_record(self, original):
            return {
                "runtime_candidate_ok": True,
                "candidate": "वह स्कूल जाती है।",
            }
    actual = run_private_research(
        "वह स्कूल जाता है।", engine=Fake(),
        environment=env_flags(), server_address="localhost",
    )
    assert actual["candidate"] == "वह स्कूल जाती है।"
    assert actual["original"] == "वह स्कूल जाता है।"
    assert actual["meaning_preservation"] == "REQUIRES_HUMAN_REVIEW"


def test_invalid_model_candidate_does_not_leak():
    class Fake:
        def generate_record(self, original):
            return {"runtime_candidate_ok": False, "candidate": "partial"}
    with pytest.raises(RuntimeError, match="Incomplete"):
        run_private_research("मैं घर जाता हूँ।", engine=Fake(), environment=env_flags(), server_address="127.0.0.1")
