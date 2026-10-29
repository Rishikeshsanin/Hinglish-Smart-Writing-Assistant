"""Pure text-processing boundary around AI4Bharat's real IndicXlit engine.

This module never generates Hindi text itself: all Roman-Hindi tokens requiring
transliteration are sent to the supplied model object.
"""

from __future__ import annotations

import re
from typing import Protocol

ROMAN_TOKEN = re.compile(r"[A-Za-z]+")
TOKENIZER = re.compile(r"[A-Za-z]+|[^A-Za-z]+")
MAX_CHARS = 500
MAX_ROMAN_WORDS = 80


class IndicXlitProtocol(Protocol):
    def translit_word(self, word: str, topk: int = 1) -> dict[str, list[str]]: ...


class InputError(ValueError):
    """Input exceeds resource limits or contains no meaningful text."""


class ModelOutputError(RuntimeError):
    """Official model returned a response inconsistent with its documented API."""


def parse_preserve_terms(raw: str) -> set[str]:
    """Parse a user-controlled comma-separated set of English tokens."""
    if not isinstance(raw, str):
        raise InputError("Preserved terms must be comma-separated text.")
    terms = [item.strip() for item in raw.split(",") if item.strip()]
    invalid = [item for item in terms if not ROMAN_TOKEN.fullmatch(item)]
    if invalid:
        raise InputError(
            "Preserved terms currently accept A-Z words only; unsupported: "
            + ", ".join(invalid[:5])
        )
    return {term.casefold() for term in terms}


def validate_text(text: str) -> list[str]:
    """Reject invalid text before the heavyweight AI4Bharat model is loaded."""
    if not isinstance(text, str):
        raise InputError("Input must be text.")
    if not text.strip():
        raise InputError("Enter a Roman-Hindi sentence to continue.")
    if len(text) > MAX_CHARS:
        raise InputError(f"Maximum input is {MAX_CHARS} characters.")
    tokens = TOKENIZER.findall(text)
    roman_count = sum(bool(ROMAN_TOKEN.fullmatch(token)) for token in tokens)
    if roman_count > MAX_ROMAN_WORDS:
        raise InputError(f"Maximum input is {MAX_ROMAN_WORDS} Roman-script words.")
    return tokens


def has_convertible_tokens(tokens: list[str], preserve_terms: set[str] | None = None) -> bool:
    """Check whether inference is necessary; skip model for fully preserved input."""
    protected = {term.casefold() for term in (preserve_terms or set())}
    return any(
        ROMAN_TOKEN.fullmatch(token)
        and token.casefold() not in protected
        and not (token.isupper() and 2 <= len(token) <= 6)
        for token in tokens
    )


def transliterate_text(
    text: str,
    engine: IndicXlitProtocol,
    preserve_terms: set[str] | None = None,
) -> str:
    """Roman-Hindi → Devanagari using IndicXlit; never fake model results.

    Non-ASCII text, spaces, numbers, and punctuation are retained byte-for-byte.
    English words are inherently ambiguous: an explicit preserve list and
    all-uppercase acronyms (2–6 letters) stay in Latin script.
    """
    tokens = validate_text(text)
    protected = {term.casefold() for term in (preserve_terms or set())}
    output: list[str] = []
    cache: dict[str, str] = {}

    for token in tokens:
        if not ROMAN_TOKEN.fullmatch(token):
            output.append(token)
            continue
        if token.casefold() in protected or (token.isupper() and 2 <= len(token) <= 6):
            output.append(token)
            continue
        key = token.casefold()
        if key not in cache:
            response = engine.translit_word(token, topk=1)
            if not isinstance(response, dict):
                raise ModelOutputError(f"Expected model dictionary for {token!r}.")
            guesses = response.get("hi")
            if not isinstance(guesses, list) or not guesses or not isinstance(guesses[0], str) or not guesses[0].strip():
                raise ModelOutputError(f"No Hindi prediction from IndicXlit for {token!r}.")
            cache[key] = guesses[0]
        output.append(cache[key])

    return "".join(output)
