"""Lazy loading of genuine official AI4Bharat IndicXlit weights."""

import argparse
import os
import sys
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
    # Explicitly opt in to the independently audited Python >=3.11 compatibility
    # experiment. This is not a substitute model or a default application path.
    if sys.version_info >= (3, 11) and os.environ.get("INDICWRITE_PY312_COMPAT") == "1":
        from .fairseq_compat_loader import enable_compatibility
        enable_compatibility()
    import torch
    from ai4bharat.transliteration import XlitEngine

    with torch.serialization.safe_globals([argparse.Namespace]):
        return XlitEngine("hi", beam_width=4, rescore=False)


def load_indicxlit():
    """Serialize cold starts so simultaneous sessions cannot load duplicate weights.

    The lock must wrap the cached function, not only its body: concurrent cache
    misses can otherwise initialize more than one model.
    """
    with _LOAD_LOCK:
        return _load_indicxlit_cached()
