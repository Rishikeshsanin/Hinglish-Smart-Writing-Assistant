"""Lazy loading of genuine official AI4Bharat IndicXlit weights."""

from functools import lru_cache


@lru_cache(maxsize=1)
def load_indicxlit():
    """Load the pretrained model only when a user converts text.

    First call may download weights; errors intentionally propagate to UI.
    No offline or hardcoded substitution is permitted.
    """
    from ai4bharat.transliteration import XlitEngine

    return XlitEngine("hi", beam_width=4, rescore=False)
