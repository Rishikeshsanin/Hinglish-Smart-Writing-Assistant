"""Isolated, reproducible AI4Bharat dependencies for Streamlit Community Cloud.

Avoid changing Streamlit Cloud's shared/Conda pip installation. Our official
IndicXlit model relies on an older Fairseq/OmegaConf metadata resolver; build
it only inside a clean local Python venv with pip 23.3.2.

This function makes *no* changes to the main cloud interpreter, other apps,
GitHub, user documents, or private BharatGen research.
"""
from __future__ import annotations

import os
from pathlib import Path
import site
import subprocess
import sys
import time
import venv

VERSION = "py312-indicxlit-v1"
ROOT = Path.home() / ".cache" / "indicwrite" / VERSION
STAMP = ROOT / "MODEL_PACKAGES_READY"
PYTHON = ROOT / "bin" / "python"
LIB = ROOT / "lib" / "python3.12" / "site-packages"


def _run(*argv: str) -> None:
    try:
        subprocess.run(
        list(argv), check=True, timeout=1050, stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
        env={**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_NO_CACHE_DIR": "1"},
        )
    except subprocess.CalledProcessError as exc:
        # Avoid printing paths or input text in public Cloud UI; CI can inspect
        # the captured dependency error without leaking private user input.
        raise RuntimeError(
            f"Isolated-model dependency command failed (exit {exc.returncode}): "
            + (exc.stderr or "")[-1600:]
        ) from exc


def prepare_official_model() -> Path:
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("Cloud entrypoint requires Python 3.12.")
    if not STAMP.is_file() or not LIB.is_dir():
        ROOT.mkdir(parents=True, exist_ok=True)
        STAMP.unlink(missing_ok=True)
        venv.create(ROOT, with_pip=True, clear=True)
        _run(str(PYTHON), "-m", "pip", "install", "--upgrade",
             "pip==23.3.2", "setuptools<70", "wheel")
        _run(str(PYTHON), "-m", "pip", "install",
             "torch==2.6.0", "--index-url", "https://download.pytorch.org/whl/cpu")
        _run(str(PYTHON), "-m", "pip", "install", "ai4bharat-transliteration==1.1.3",
             "codemix-restore-shunyalabs==0.4.0")
        # Smoke-import the exact official checkpoint dependencies, not a dummy.
        _run(str(PYTHON), "-c",
             "import sys; sys.path.insert(0, %r); "
             "from indicwrite.fairseq_compat_loader import enable_compatibility; "
             "enable_compatibility(); import torch, fairseq, ai4bharat.transliteration;"
             "print('Official model dependencies loaded')" % str(Path(__file__).resolve().parents[1])) 
        STAMP.write_text(VERSION, encoding="ascii")
    if not LIB.is_dir():
        raise RuntimeError("Isolated official-model site-packages are unavailable")
    site.addsitedir(str(LIB))
    return LIB
