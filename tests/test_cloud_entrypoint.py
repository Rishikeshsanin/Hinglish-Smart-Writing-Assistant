"""Deployment compatibility flag is explicit; no real model in unit tests."""
from pathlib import Path
def test_cloud_entrypoint_is_separate_and_keeps_private_model_off():
    source=(Path(__file__).resolve().parents[1]/"cloud_app.py").read_text(encoding="utf-8")
    assert 'INDICWRITE_PY312_COMPAT"] = "1"' in source
    assert 'INDICWRITE_PRIVATE_BHARATGEN"] = "0"' in source
    assert 'INDICWRITE_ENABLE_LANGUAGE_SERVICES"] = "0"' in source
    compile(source,"cloud_app.py","exec")
