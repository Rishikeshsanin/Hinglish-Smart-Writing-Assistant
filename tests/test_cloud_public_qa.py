"""Offline Issue #33 regressions. Stubbed checks are NOT live model evidence."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types

import pytest


ROOT = Path(__file__).resolve().parents[1]


def public_script(monkeypatch):
    # Pure classifier/assertion unit tests do not download a browser.
    package = types.ModuleType("playwright")
    package.__path__ = []
    sync = types.ModuleType("playwright.sync_api")
    sync.TimeoutError = TimeoutError
    sync.sync_playwright = lambda: None
    monkeypatch.setitem(sys.modules, "playwright", package)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync)
    spec = importlib.util.spec_from_file_location(
        "indicwrite_public_browser_qa", ROOT / "scripts/check_public_streamlit.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_failure_categories_distinguish_selector_from_provider(monkeypatch):
    module = public_script(monkeypatch)
    assert module.classify_page("This app has gone to sleep", [], 200) == "provider_or_app_error"
    assert module.classify_page("", [], 503) == "http_unavailable"
    assert module.classify_page("✦ Convert to Hindi", [], 200) == "selector_mismatch"
    assert module.classify_page("Express yourself.", [], 200) == "app_render_incomplete"
    assert module.classify_page("Loading", [], None) == "app_not_rendered"


def test_public_real_output_contract_detects_missing_output_and_punctuation(monkeypatch):
    module = public_script(monkeypatch)
    module.verify_output("kal mujhe college jana hai!", "कल मुझे कॉलेज जाना है!", ("कल", "जाना"), "!")
    with pytest.raises(AssertionError):
        module.verify_output("kal mujhe college jana hai!", "kal mujhe college jana hai!", ("कल",), "!")
    with pytest.raises(AssertionError):
        module.verify_output("kal mujhe college jana hai!", "कल मुझे कॉलेज जाना है", ("कल",), "!")
    with pytest.raises(AssertionError):
        module.verify_output("kal mujhe college jana hai!", "कल मुझे घर जाना है!", ("मौसम",), "!")


def test_public_browser_checks_multiple_distinct_inputs(monkeypatch):
    module = public_script(monkeypatch)
    assert len(module.CASES) >= 3
    assert len({case[0] for case in module.CASES}) == len(module.CASES)
    assert module.URL == "https://hinglish-smart-writing-assistant-indicwrite-rishi.streamlit.app/"
    workflow = (ROOT / ".github/workflows/public-streamlit-smoke.yml").read_text()
    assert "pull_request:" in workflow and "workflow_dispatch:" in workflow
    assert "if: always()" in workflow and "public-qa/" in workflow


def test_cloud_bootstrap_cache_reuse_and_failed_install_retry(monkeypatch, tmp_path):
    import indicwrite.cloud_bootstrap as mod
    root = tmp_path / "model"
    lib = root / "lib" / "python3.12" / "site-packages"
    py = root / "bin" / "python"
    stamp = root / "MODEL_PACKAGES_READY"
    monkeypatch.setattr(mod, "ROOT", root)
    monkeypatch.setattr(mod, "LIB", lib)
    monkeypatch.setattr(mod, "PYTHON", py)
    monkeypatch.setattr(mod, "STAMP", stamp)
    monkeypatch.setattr(mod, "LOCK", tmp_path / "model.lock")
    monkeypatch.setattr(mod.sys, "version_info", (3, 12, 16))
    monkeypatch.setattr(mod.os, "name", "posix")
    commands = []
    added = []
    def fake_venv(path, *, with_pip, clear):
        assert path == root and with_pip and clear
        lib.mkdir(parents=True, exist_ok=True)
        py.parent.mkdir(parents=True, exist_ok=True)
        py.write_text("fake-python")
    def fake_run(*args):
        commands.append(args)
        if len(commands) == 1:
            raise RuntimeError("controlled pip failure")
    monkeypatch.setattr(mod.venv, "create", fake_venv)
    monkeypatch.setattr(mod, "_run", fake_run)
    monkeypatch.setattr(mod.site, "addsitedir", added.append)
    with pytest.raises(RuntimeError, match="controlled pip failure"):
        mod.prepare_official_model()
    assert not stamp.exists()
    assert mod.prepare_official_model() == lib
    assert stamp.read_text() == mod.VERSION
    install_count = len(commands)
    assert install_count == 5  # failed install + 4 successful pip/import stages
    assert mod.prepare_official_model() == lib
    assert len(commands) == install_count
    assert added == [str(lib), str(lib)]


def test_cloud_bootstrap_redacts_basic_url_credentials():
    from indicwrite.cloud_bootstrap import _safe_stderr
    out = _safe_stderr("Could not fetch https://name:secret@example.com/simple")
    assert "secret" not in out and "[redacted]" in out
