"""Repair a narrow pip overlay collision on Streamlit Community Cloud.

Community Cloud pre-installs pip 26, then Conda places pip 23.3.2 over it.
Since pip 26 has pip._internal.build_env as a *package* while pip 23 uses
build_env.py as a *module*, the leftover newer package shadows the old
module and imports functions missing in pip 23. This MetaPathFinder selects
the correct pip 23 module for that exact name.

No application behavior, dependencies, model outputs, other imports or
filesystem files are changed. This script intentionally does nothing for
any pip version other than the pinned 23.3.2.
"""
from __future__ import annotations

import importlib.abc
import importlib.util
from pathlib import Path
import sys


class _LegacyPipBuildEnvFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname != "pip._internal.build_env":
            return None
        try:
            import pip
            if pip.__version__ != "23.3.2":
                return None
            legacy = Path(pip.__file__).resolve().parent / "_internal" / "build_env.py"
            if not legacy.is_file():
                return None
            return importlib.util.spec_from_file_location(fullname, legacy)
        except (ImportError, OSError, ValueError):
            return None


if not any(isinstance(item, _LegacyPipBuildEnvFinder) for item in sys.meta_path):
    sys.meta_path.insert(0, _LegacyPipBuildEnvFinder())
