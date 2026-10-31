# Streamlit Cloud pip bootstrap (31 October 2026)

The first live Community Cloud installation failed **before** installing
project dependencies. The platform had pip 26 modules already present,
while Conda overlaid pip 23.3.2. The leftover new pip
`pip._internal.build_env` **package** shadowed the correct pip 23
`pip._internal.build_env.py` **module**, leading to:

```
ImportError: cannot import name 'open_rich_spinner' from pip._internal.cli.spinners
```

Why not just upgrade pip? Pip 25.3 cannot process legacy OmegaConf 2.0.6
invalid metadata and falls back to a broken Fairseq 0.12.1 sdist. That
failed in isolated GitHub Actions, with zero changes to production.

The root `sitecustomize.py` contains an exact-version import hook:
**only** when pip 23.3.2 is detected, import its old
`pip._internal.build_env.py` instead of the stale pip 26 package.
It does not change model code, disable errors, delete packages or
modify unrelated imports. GitHub Actions
`cloud-pip-overlay.yml` explicitly reproduces the mixed-file
environment and tests `pip --help`.

This is a defensive compatibility workaround, not a claim that the
actual Streamlit app has deployed. After it passes CI, the updated
`environment.yml` should trigger a Cloud rebuild. Check the actual
live logs for *successful installation and real model inference*.
