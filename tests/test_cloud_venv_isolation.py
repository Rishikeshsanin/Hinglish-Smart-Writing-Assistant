"""Model installer isolation: no installations or downloads during unit tests."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_isolated_installer_never_mutates_host_pip():
    source = (ROOT/"src/indicwrite/cloud_bootstrap.py").read_text()
    ast.parse(source)
    assert "pip==23.3.2" in source
    assert "with_pip=True, clear=True" in source
    assert '"ai4bharat-transliteration==1.1.3"' in source
    assert '"codemix-restore-shunyalabs==0.4.0"' in source
    assert "site.addsitedir(str(LIB))" in source
    assert 'pip install --upgrade pip' not in source


def test_conda_only_installs_managed_streamlit_not_model_or_old_pip():
    env = (ROOT/"environment.yml").read_text()
    assert "python=3.12" in env
    assert "streamlit" in env
    assert "  - pip:" not in env
    assert "  - pip=23" not in env


def test_cloud_entrypoint_keeps_private_model_disabled():
    script=(ROOT/"cloud_app.py").read_text()
    ast.parse(script)
    assert 'INDICWRITE_PRIVATE_BHARATGEN"] = "0"' in script
    assert "prepare_official_model()" in script
