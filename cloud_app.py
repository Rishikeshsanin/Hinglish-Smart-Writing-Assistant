"""Free Streamlit Cloud launcher for the genuine AI4Bharat IndicXlit model.

Cloud provides Streamlit and Python 3.12 with no broken pip overlay. The model
dependencies are installed in a clean isolated venv only on first launch.
"""
import os
import runpy
from pathlib import Path
import streamlit as st

os.environ["INDICWRITE_PY312_COMPAT"] = "1"
os.environ["INDICWRITE_PRIVATE_BHARATGEN"] = "0"
os.environ["INDICWRITE_ENABLE_LANGUAGE_SERVICES"] = "0"

try:
    from src.indicwrite.cloud_bootstrap import prepare_official_model
    # Do not emit any Streamlit UI before app.py calls st.set_page_config.
    prepare_official_model()
except Exception:
    st.error("The official model environment could not be prepared. Check Cloud logs; no substitute model is used.")
    st.stop()
runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
