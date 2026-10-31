"""Explicit opt-in and package requirements for supported-Python experiment."""
import os
import sys
import pytest
from indicwrite.engine import _load_indicxlit_cached


def test_normal_environment_never_implicitly_loads_compatibility(monkeypatch):
    monkeypatch.delenv("INDICWRITE_PY312_COMPAT",raising=False)
    # Normal unit tests use fake engines. The real model is CI-only in the
    # dedicated Python 3.12 compatibility job.
    assert not os.environ.get("INDICWRITE_PY312_COMPAT")


def test_missing_external_compat_module_rejected(monkeypatch):
    from indicwrite import fairseq_compat_loader as shim
    monkeypatch.setattr(shim.importlib.metadata,"version",lambda _: "0.0.0")
    with pytest.raises(RuntimeError,match="Expected audited"):
        shim.enable_compatibility()
