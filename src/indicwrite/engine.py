"""Lazy loading of genuine official AI4Bharat IndicXlit weights."""

import argparse
import os
import sys
import time
from functools import lru_cache
from threading import RLock


_LOAD_LOCK = RLock()


@lru_cache(maxsize=1)
def _load_indicxlit_cached():
    """Load the pretrained model only when a user converts text.

    First call may download official weights; errors intentionally propagate.
    Fairseq's older checkpoint includes argparse.Namespace. PyTorch >=2.6
    defaults to restricted weights-only loading, so explicitly allowlist only
    this standard-library type while loading the official pretrained model.
    No untrusted user-supplied checkpoint paths are supported.
    """
    # Community Cloud host installs Streamlit only. This uses a separate venv
    # with the *original* AI4Bharat package; it never substitutes a web API.
    if os.environ.get("INDICWRITE_CLOUD_LAZY_BOOTSTRAP") == "1":
        from .cloud_bootstrap import prepare_official_model
        prepare_official_model()
    if sys.version_info >= (3, 11) and os.environ.get("INDICWRITE_PY312_COMPAT") == "1":
        from .fairseq_compat_loader import enable_compatibility
        enable_compatibility()
    import torch
    from ai4bharat.transliteration import XlitEngine

    with torch.serialization.safe_globals([argparse.Namespace]):
        return XlitEngine("hi", beam_width=4, rescore=False)


def load_indicxlit():
    """Serialize cold requests and record timing without logging user input.

    The lock wraps the cached function: concurrent cache misses must not
    download and initialize duplicate copies of the official neural model.
    """
    with _LOAD_LOCK:
        cold = _load_indicxlit_cached.cache_info().currsize == 0
        started = time.monotonic()
        if cold:
            print("INDICWRITE_OFFICIAL_MODEL_COLD_LOAD_START", flush=True)
        try:
            model = _load_indicxlit_cached()
        except Exception as exc:
            if cold:
                print(
                    "INDICWRITE_OFFICIAL_MODEL_COLD_LOAD_FAILED "
                    f"kind={type(exc).__name__} "
                    f"elapsed_seconds={time.monotonic() - started:.2f}",
                    flush=True,
                )
            raise
        if cold:
            print(
                "INDICWRITE_OFFICIAL_MODEL_COLD_LOAD_OK "
                f"elapsed_seconds={time.monotonic() - started:.2f}",
                flush=True,
            )
        return model
