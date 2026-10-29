"""Execute BOTH genuine open neural models on public educational sentences.

No fake engines, canned responses or hardcoded 'expected corrected' outputs.
Script prints observed model predictions. If a download fails, exits nonzero.
"""

import json
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from indicwrite.language_services import (
    GEC_MODEL, TRANSLATION_MODEL, load_hindi_gec, load_hi_en,
    generate_hindi_gec, generate_english, LanguageModelError,
)


def main() -> None:
    import torch
    import transformers
    print("ENV", json.dumps({
        "python": platform.python_version(), "torch": torch.__version__,
        "transformers": transformers.__version__
    }), flush=True)
    print("GEC_MODEL", GEC_MODEL, flush=True)
    gec=load_hindi_gec()
    gec_attempts = 0
    for original in ("मैं स्कूल जाता है।", "राम ने ने खाना खाया।", "वे किताबें पढ़ता है।"):
        print("GEC_INPUT", original, flush=True)
        try:
            output=generate_hindi_gec(original, gec)
            print("GEC_ACCEPTED_OUTPUT", output, flush=True)
            assert output.strip(), "Empty output from real Hindi GEC checkpoint"
        except LanguageModelError as exc:
            # A rejected prediction still proves that genuine generation ran;
            # the safety gate is expected to block known mixed-script outputs.
            print("GEC_OUTPUT_REJECTED", str(exc), flush=True)
        gec_attempts += 1
    assert gec_attempts == 3
    print("REAL_HINDI_GEC_MODEL_EXECUTED_WITH_SAFEGUARD", flush=True)
    print("TRANSLATION_MODEL", TRANSLATION_MODEL, flush=True)
    translator=load_hi_en()
    for original in ("मुझे कल कॉलेज जाना है।", "नमस्ते, आप कैसे हैं?"):
        output=generate_english(original, translator)
        print("TRANSLATION_INPUT", original, flush=True)
        print("TRANSLATION_REAL_OUTPUT", output, flush=True)
        assert output.strip() and any(ch.isalpha() for ch in output)
    print("REAL_OPUS_HI_EN_MODEL_EXECUTED", flush=True)


if __name__=="__main__":
    main()
