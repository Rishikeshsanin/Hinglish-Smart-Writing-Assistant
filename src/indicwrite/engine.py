"""Lazy loading of genuine official AI4Bharat IndicXlit weights."""

import argparse
from functools import lru_cache


@lru_cache(maxsize=1)
def load_indicxlit():
    """Load the pretrained model only when a user converts text.

    First call may download official weights; errors intentionally propagate.
    Fairseq's older checkpoint includes argparse.Namespace. PyTorch >=2.6
    defaults to restricted weights-only loading, so explicitly allowlist only
    this standard-library type while loading the official pretrained model.
    No untrusted user-supplied checkpoint paths are supported.
    """
    import torch
    from ai4bharat.transliteration import XlitEngine

    with torch.serialization.safe_globals([argparse.Namespace]):
        return XlitEngine("hi", beam_width=4, rescore=False)
