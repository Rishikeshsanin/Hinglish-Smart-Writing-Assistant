"""Load a pinned, attributed third-party compatibility shim in isolation.

The official neural checkpoint remains AI4Bharat's. The patch fixes legacy
Fairseq/Hydra Python3.12 startup only; it never substitutes model weights.
Only enabled in research CI or a separately configured deployment.
"""
from __future__ import annotations
import importlib.metadata
import importlib.util
from pathlib import Path

PACKAGE="codemix-restore-shunyalabs"
VERSION="0.4.0"


def enable_compatibility() -> None:
    installed=importlib.metadata.version(PACKAGE)
    if installed != VERSION:
        raise RuntimeError(f"Expected audited {PACKAGE}=={VERSION}, found {installed}")
    dist=importlib.metadata.distribution(PACKAGE)
    source=Path(dist.locate_file("codemix_restore/compat/fairseq_patch.py"))
    if not source.is_file():
        raise RuntimeError("Pinned Fairseq Python 3.12 compatibility source unavailable")
    spec=importlib.util.spec_from_file_location("_indicwrite_external_fairseq_patch",str(source))
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load pinned Fairseq compatibility module")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_patch()
