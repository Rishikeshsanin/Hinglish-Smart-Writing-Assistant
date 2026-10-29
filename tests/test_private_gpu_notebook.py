"""Static and privacy checks: Colab notebook is a plan, not executed GPU QA."""
import json
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[1] / "notebooks/BharatGen_Private_UI_GPU_QA.ipynb"


def test_private_gpu_ui_notebook_is_valid_and_never_opens_public_tunnels():
    doc=json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert doc["nbformat"] == 4
    assert all(not c.get("outputs") for c in doc["cells"] if c["cell_type"] == "code")
    code="\n".join("".join(c["source"]) for c in doc["cells"])
    for required in ("127.0.0.1", "private_bharatgen_app.py", "expect_download", "SOURCE_COMMIT", "real_pretrained_ui_success"):
        assert required in code
    for disallowed in ("ngrok.connect(", "cloudflared tunnel", "share=True", "server.address=0.0.0.0"):
        assert disallowed not in code
    for cell in doc["cells"]:
        if cell["cell_type"] == "code":
            compile("".join(cell["source"]), "Colab code cell", "exec")
