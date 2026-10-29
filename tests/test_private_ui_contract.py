"""Actual Streamlit AppTest widget flow, using a clearly fake GPU engine.

Not a pretrained BharatGen inference test. Private app never uses Fairseq.
"""
from __future__ import annotations

from pathlib import Path

import pytest

st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest
import indicwrite.private_bharatgen as service

APP = str(Path(__file__).resolve().parents[1] / "research/private_bharatgen_app.py")


def test_research_ui_locked_without_explicit_local_authorization(monkeypatch):
    monkeypatch.delenv("INDICWRITE_PRIVATE_BHARATGEN", raising=False)
    monkeypatch.setattr(st, "get_option", lambda _: "127.0.0.1")
    page = AppTest.from_file(APP).run()
    assert not page.exception
    assert page.error
    assert "locked" in page.error[0].message
    assert not page.button


def test_private_ui_requires_review_before_download_and_resets_on_edit(monkeypatch):
    for flag in service.RESEARCH_FLAGS:
        monkeypatch.setenv(flag, "1")
    monkeypatch.setattr(st, "get_option", lambda _: "127.0.0.1")
    calls = []

    def fake_inference(original, *, server_address):
        calls.append((original, server_address))
        return {
            "original": original,
            "candidate": "वह लड़की रोज़ स्कूल जाती है।",
            "warnings": [],
            "model": "TEST_ONLY_FAKE",
            "meaning_preservation": "REQUIRES_HUMAN_REVIEW",
        }

    monkeypatch.setattr(service, "run_private_research", fake_inference)
    page = AppTest.from_file(APP).run()
    assert not page.exception
    page.text_area[0].set_value("वह लड़की रोज़ स्कूल जाता है।").run()
    page.button[0].click().run()
    assert calls == [("वह लड़की रोज़ स्कूल जाता है।", "127.0.0.1")]
    assert "वह लड़की रोज़ स्कूल जाती है।" in [x.value for x in page.code]
    assert not page.checkbox[0].value
    page.checkbox[0].check().run()
    assert page.checkbox[0].value
    page.text_area[0].set_value("मैं कॉलेज में हूँ।").run()
    assert not page.checkbox
    assert not page.code
