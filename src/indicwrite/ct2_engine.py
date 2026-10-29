"""Experimental third-party CTranslate2 conversion of AI4Bharat IndicXlit.

NOT the official Fairseq runtime. Its source and output parity must be verified
before production use. No silent fallback from official AI4Bharat inference.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from threading import RLock

CONVERTED_MODEL_ID = "Singla0009/all-indic-transliteration"
CONVERTED_SUBDIR = "indicxlit_ct2_fp32"
MODEL_REVISION = None  # Smoke experiment discovers immutable commit before pinning
_LOCK = RLock()


class CTranslate2IndicXlit:
    """Minimal explicit adapter compatible with the app's real IndicXlit protocol."""

    def __init__(self, translator, revision: str):
        self.translator = translator
        self.revision = revision

    def translit_word(self, word: str, topk: int = 1) -> dict[str, list[str]]:
        if not isinstance(word, str) or not word.isascii() or not word.isalpha():
            raise ValueError("CTranslate2 translit_word requires one ASCII alphabetic token.")
        if not 1 <= topk <= 4:
            raise ValueError("Requested candidates must be from 1 through 4.")
        tokens = ["__hi__"] + list(word.lower())
        results = self.translator.translate_batch(
            [tokens], beam_size=4, num_hypotheses=topk
        )
        if not results or not results[0].hypotheses:
            raise RuntimeError("Converted model returned no hypothesis.")
        converted = ["".join(tokens) for tokens in results[0].hypotheses]
        if not all(converted):
            raise RuntimeError("Converted model returned an empty output.")
        return {"hi": converted}


@lru_cache(maxsize=1)
def _load_cached():
    import ctranslate2
    from huggingface_hub import snapshot_download

    folder = snapshot_download(
        repo_id=CONVERTED_MODEL_ID,
        revision=MODEL_REVISION,
        allow_patterns=f"{CONVERTED_SUBDIR}/*",
    )
    path = Path(folder)
    model = ctranslate2.Translator(
        str(path / CONVERTED_SUBDIR),
        device="cpu",
        inter_threads=1,
        intra_threads=2,
    )
    return CTranslate2IndicXlit(model, revision=path.name)


def load_converted_indicxlit():
    with _LOCK:
        return _load_cached()
