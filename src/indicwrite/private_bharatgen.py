"""Conservative, opt-in PRIVATE BharatGen review helper.

The genuine model and its outputs may only be used in an authorized private
academic context. This module never loads model weights merely upon import.
There is no public hosted API, silent fallback, or automatic edit acceptance.
"""
from __future__ import annotations
from functools import lru_cache
from threading import RLock
import os
from typing import Mapping

from .param_rewrite import build_messages, has_devanagari_letter
from .language_services import preservation_warnings

RESEARCH_FLAGS = (
    "INDICWRITE_PRIVATE_BHARATGEN",
    "INDICWRITE_REVIEWED_BHARATGEN_CODE",
    "INDICWRITE_ACKNOWLEDGE_BHARATGEN_LICENSE",
)
LOOPBACK_ADDRESSES = frozenset({"127.0.0.1", "localhost", "::1", "[::1]"})


def private_research_enabled(
    environment: Mapping[str, str] | None = None,
    server_address: str | None = None,
) -> bool:
    """Fail closed if consent flags or Streamlit localhost bind is absent."""
    env = os.environ if environment is None else environment
    return bool(
        server_address in LOOPBACK_ADDRESSES
        and all(env.get(flag) == "1" for flag in RESEARCH_FLAGS)
    )


def review_candidate(original: str, proposed: str) -> list[str]:
    """Private-only heuristic warnings, never an automatic human-quality pass.

    Meaning preservation requires actual human comparison even when the warning
    list is empty. No sentence is logged, uploaded, or automatically applied.
    """
    build_messages(original)
    if not isinstance(proposed, str) or not proposed.strip():
        raise ValueError("BharatGen returned an empty suggestion.")
    if not has_devanagari_letter(proposed):
        raise ValueError("BharatGen returned a non-Hindi suggestion.")
    return preservation_warnings(original, proposed)


_MODEL_LOCK = RLock()


@lru_cache(maxsize=1)
def _load_private_engine():
    from .param_rewrite import BharatGenRewriter
    return BharatGenRewriter.load(allow_remote_code=True, device="cuda:0")


def run_private_research(
    original: str,
    *,
    environment: Mapping[str, str] | None = None,
    server_address: str | None = None,
    engine=None,
) -> dict:
    """Generate only after explicit authorization, with no model substitution.

    The returned suggestion is never applied automatically. Callers must not
    write the record to public GitHub or enable on a remotely reachable app.
    """
    if not private_research_enabled(environment, server_address):
        raise PermissionError(
            "Private BharatGen research requires loopback-only hosting and all explicit acknowledgement flags."
        )
    build_messages(original)
    if engine is None:
        with _MODEL_LOCK:
            engine = _load_private_engine()
    record = engine.generate_record(original)
    if not isinstance(record, dict) or record.get("runtime_candidate_ok") is not True:
        raise RuntimeError("Incomplete or invalid pretrained model output; no edit was applied.")
    candidate = record["candidate"]
    return {
        "original": original,
        "candidate": candidate,
        "warnings": review_candidate(original, candidate),
        "model": "bharatgenai/Param-1-2.9B-Instruct",
        "meaning_preservation": "REQUIRES_HUMAN_REVIEW",
    }
