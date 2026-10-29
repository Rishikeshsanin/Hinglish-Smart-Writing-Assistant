"""EXPERIMENTAL genuine BharatGen smoke test; never silently mocked.

Install optional requirements after consulting Hugging Face license and source.
This downloads ~5.8 GB of model parameters and needs adequate memory.
"""
from __future__ import annotations
import argparse
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from indicwrite.param_rewrite import BharatGenRewriter, MODEL_ID, MODEL_REVISION


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-model-download",
        action="store_true",
        help="Explicitly acknowledge downloading ~6GB of pretrained weights.",
    )
    args = parser.parse_args()
    if not args.allow_model_download:
        parser.error(
            "BharatGen checkpoint requires a multi-GB download and review "
            "of trust_remote_code. Re-run with --allow-model-download when ready."
        )

    import torch

    print(f"Python={platform.python_version()} PyTorch={torch.__version__}", flush=True)
    print(f"Loading genuine model: {MODEL_ID}@{MODEL_REVISION}", flush=True)
    engine = BharatGenRewriter.load()
    original = "मुझे कल कॉलेज में असाइनमेंट सबमिट करना है।"
    rewritten = engine.rewrite(original)
    print("INPUT:", original, flush=True)
    print("BHARATGEN_OUTPUT:", rewritten, flush=True)
    assert any("\u0900" <= ch <= "\u097f" for ch in rewritten), "Model did not emit Hindi"
    print("REAL_BHARATGEN_SMOKE_TEST_PASSED", flush=True)


if __name__ == "__main__":
    main()
