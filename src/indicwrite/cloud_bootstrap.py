"""Isolated AI4Bharat IndicXlit installer for free Streamlit Community Cloud.

The host installs only Streamlit. At first real conversion, install the same
official AI4Bharat checkpoint dependencies in a private Python 3.12 venv with
legacy pip, without mutating host pip or any other app. Log stages, never text
submitted by users. File locking protects concurrent worker *processes*.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import site
import subprocess
import sys
import time
import venv

VERSION = "py312-indicxlit-v1"  # Preserve cache and frozen original-model parity.
ROOT = Path.home() / ".cache" / "indicwrite" / VERSION
STAMP = ROOT / "MODEL_PACKAGES_READY"
PYTHON = ROOT / "bin" / "python"
LIB = ROOT / "lib" / "python3.12" / "site-packages"
LOCK = ROOT.parent / (VERSION + ".lock")


def _safe_stderr(stderr: str) -> str:
    """Redact URL credentials in unexpected pip error output."""
    return re.sub(r"(https?://)[^\s/@]+:[^\s/@]+@", r"\1[redacted]@", stderr)[-1600:]


def _run(*argv: str) -> None:
    stage = "dependency_install" if "install" in argv else "dependency_import_check"
    started = time.monotonic()
    print("INDICWRITE_CLOUD_STAGE_START " + stage, flush=True)
    try:
        subprocess.run(
            list(argv), check=True, timeout=1050, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
            env={**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_NO_CACHE_DIR": "1"},
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Isolated official-model {stage} timed out after 1050s") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Isolated official-model {stage} failed (exit {exc.returncode}): "
            + _safe_stderr(exc.stderr or "")
        ) from exc
    finally:
        print(
            "INDICWRITE_CLOUD_STAGE_END " + stage
            + f" elapsed_seconds={time.monotonic() - started:.2f}", flush=True
        )


def prepare_official_model() -> Path:
    """Idempotent, process-safe installation; returns original-model site packages.

    The stamp is written *only* after successful official-library smoke-import.
    A crash or failed installation leaves no valid stamp and is retried.
    """
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("Cloud entrypoint requires Python 3.12.")
    if os.name != "posix":
        raise RuntimeError("Cloud isolated model bootstrap requires Linux (POSIX).")

    # This lock lives OUTSIDE ROOT: venv.create(clear=True) must never erase it.
    # File descriptors are released automatically if a worker is killed.
    import fcntl

    ROOT.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("a+", encoding="ascii") as lock:
        started_wait = time.monotonic()
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        print(
            f"INDICWRITE_CLOUD_LOCK_ACQUIRED wait_seconds={time.monotonic() - started_wait:.2f}",
            flush=True,
        )
        ready = STAMP.is_file() and LIB.is_dir() and PYTHON.is_file()
        if ready:
            print("INDICWRITE_CLOUD_MODEL_VENV_CACHE_HIT", flush=True)
        else:
            started = time.monotonic()
            free_mb = shutil.disk_usage(ROOT.parent).free // (1024 * 1024)
            print(f"INDICWRITE_CLOUD_MODEL_VENV_BUILD free_disk_mb={free_mb}", flush=True)
            ROOT.mkdir(parents=True, exist_ok=True)
            STAMP.unlink(missing_ok=True)
            venv.create(ROOT, with_pip=True, clear=True)
            _run(str(PYTHON), "-m", "pip", "install", "--upgrade",
                 "pip==23.3.2", "setuptools<70", "wheel")
            _run(str(PYTHON), "-m", "pip", "install",
                 "torch==2.6.0", "--index-url", "https://download.pytorch.org/whl/cpu")
            _run(str(PYTHON), "-m", "pip", "install",
                 "ai4bharat-transliteration==1.1.3",
                 "codemix-restore-shunyalabs==0.4.0")
            # Genuine official package import plus audited Python 3.12 shim.
            # This is an import check, NOT a claim that weights were inferred.
            _run(str(PYTHON), "-c",
                 "import sys; sys.path.insert(0, %r); "
                 "from indicwrite.fairseq_compat_loader import enable_compatibility; "
                 "enable_compatibility(); import torch, fairseq, ai4bharat.transliteration; "
                 "print('Official model dependencies loaded')"
                 % str(Path(__file__).resolve().parents[1]))
            STAMP.write_text(VERSION, encoding="ascii")
            print(
                f"INDICWRITE_CLOUD_MODEL_VENV_READY elapsed_seconds={time.monotonic() - started:.2f}",
                flush=True,
            )
        if not LIB.is_dir():
            raise RuntimeError("Isolated official-model site-packages are unavailable")
        site.addsitedir(str(LIB))
    return LIB
