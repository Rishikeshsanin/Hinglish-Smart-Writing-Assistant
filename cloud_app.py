"""Supported Python 3.12 entrypoint for free Streamlit Community Cloud.

Uses official AI4Bharat IndicXlit weights. The pinned, attributed compatibility
patch is only for obsolete Fairseq/Hydra imports. It is not a substitute model.
BharatGen remains unavailable on this public service.
"""
from __future__ import annotations
import os,runpy
from pathlib import Path

os.environ["INDICWRITE_PY312_COMPAT"]="1"
os.environ["INDICWRITE_PRIVATE_BHARATGEN"]="0"
os.environ["INDICWRITE_ENABLE_LANGUAGE_SERVICES"]="0"
runpy.run_path(str(Path(__file__).with_name("app.py")),run_name="__main__")
