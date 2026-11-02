"""Cloud entrypoint: show Streamlit UI before initializing official neural weights.

Model packages are installed into an isolated venv ON FIRST CONVERSION, not
on every page visit. This avoids blocking Streamlit startup/health checks.
The official AI4Bharat checkpoint remains mandatory for any conversion.
"""
import os
import runpy
from pathlib import Path

os.environ["INDICWRITE_PY312_COMPAT"] = "1"
os.environ["INDICWRITE_PRIVATE_BHARATGEN"] = "0"
os.environ["INDICWRITE_ENABLE_LANGUAGE_SERVICES"] = "0"
os.environ["INDICWRITE_CLOUD_LAZY_BOOTSTRAP"] = "1"

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
