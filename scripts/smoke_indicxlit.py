"""Executed real-model smoke test; must not be replaced by a stub."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from indicwrite.core import transliterate_text
from indicwrite.engine import load_indicxlit


def main() -> None:
    print("Initializing official AI4Bharat IndicXlit model...", flush=True)
    engine = load_indicxlit()
    for source in ("namaste", "kal mujhe college jana hai!", "mera phone 2026 mein aaya."):
        result = transliterate_text(source, engine)
        print(f"INPUT : {source}", flush=True)
        print(f"OUTPUT: {result}", flush=True)
        assert any("\u0900" <= ch <= "\u097f" for ch in result), "No Devanagari characters: model inference not verified"
    print("REAL_INDICXLIT_SMOKE_TEST_PASSED", flush=True)


if __name__ == "__main__":
    main()
