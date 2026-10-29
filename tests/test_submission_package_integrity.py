"""Security and integrity tests for self-contained faculty submission archive."""

import hashlib
import json
import zipfile

import pytest
from scripts.verify_submission_package import (
    REQUIRED, validate_entry_path, verify_submission_zip
)


def create_fixture(path, *, tamper=False, hidden=False, omitted=False):
    files = {name: b"test" for name in REQUIRED}
    files["reports/IndicWrite_CS3235_Project_Report.pdf"] = b"%PDF-1.7\nfixture"
    files["evaluation/results/metrics.json"] = b'{"overall":{"count":40}}'
    files["docs/README.txt"] = b"ordinary"
    if hidden:
        files["bharatgen-20261029-private.jsonl"] = b"private model output"
    if omitted:
        files.pop("app.py")
    manifest = {
        "source_commit": "a" * 40,
        "files": {k: hashlib.sha256(v).hexdigest() for k, v in files.items()},
        "not_verified": ["Public model deployment"]
    }
    with zipfile.ZipFile(path, "w") as z:
        for name, content in files.items():
            z.writestr(name, b"corrupted" if tamper and name == "app.py" else content)
        z.writestr("SUBMISSION_MANIFEST.json", json.dumps(manifest))


def test_manifest_verification_succeeds_for_consistent_archive(tmp_path):
    target = tmp_path / "valid.zip"
    create_fixture(target)
    report = verify_submission_zip(str(target))
    assert report["files_checked"] == len(REQUIRED) + 1
    assert report["digests_match"]
    assert report["metric_case_count"] == 40


@pytest.mark.parametrize("name", [
    "../other-repo/token", "/absolute/path", ".git/config",
    "models/weights.safetensors", "private_bharatgen_evidence.zip",
    "bharatgen-run.jsonl", "secrets.toml", ".env",
])
def test_unsafe_private_archive_entries_are_rejected(name):
    with pytest.raises(ValueError):
        validate_entry_path(name)


@pytest.mark.parametrize("options,match", [
    ({"tamper": True}, "SHA-256 mismatch"),
    ({"hidden": True}, "Forbidden"),
    ({"omitted": True}, "Faculty deliverables"),
])
def test_tampered_or_incomplete_zip_rejected(tmp_path, options, match):
    target = tmp_path / "bad.zip"
    create_fixture(target, **options)
    with pytest.raises(ValueError, match=match):
        verify_submission_zip(str(target))
