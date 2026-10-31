"""Model installer isolation and Community Cloud host dependency contract."""
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


def test_cloud_host_is_pip_only_and_official_model_stays_in_separate_venv():
    cloud = (ROOT/"requirements.txt").read_text()
    assert "streamlit>=1.42,<2" in cloud
    assert "ai4bharat-transliteration" not in cloud
    assert "fairseq" not in cloud.lower().splitlines()[-1]
    assert not (ROOT/"environment.yml").exists()
    assert (ROOT/".python-version").read_text().strip() == "3.12"
    local = (ROOT/"requirements-local.txt").read_text()
    assert "ai4bharat-transliteration==1.1.3" in local
    assert "streamlit>=1.37,<2" in local
    assert (ROOT/"docs/legacy-conda-environment.yml").is_file()
    for dockerfile in ("Dockerfile.demo", "Dockerfile.cloud"):
        source = (ROOT/dockerfile).read_text()
        assert "requirements-local.txt" in source


def test_cloud_entrypoint_keeps_private_model_disabled():
    script = (ROOT/"cloud_app.py").read_text()
    ast.parse(script)
    assert 'INDICWRITE_PRIVATE_BHARATGEN"] = "0"' in script
    assert "prepare_official_model()" in script
