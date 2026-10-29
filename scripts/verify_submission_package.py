"""Independently verify SHA-256 manifest and privacy of faculty submission ZIP.

Usage: python scripts/verify_submission_package.py submission/<name>.zip
This never executes included source files or attempts to access private models.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import PurePosixPath
import re
import zipfile

REQUIRED = {
    "app.py", "README.md", "evaluation/cases.csv",
    "evaluation/results/metrics.json", "evaluation/results/predictions.csv",
    "screenshots/desktop.png", "screenshots/mobile.png",
    "reports/IndicWrite_CS3235_Project_Report.pdf",
}
FORBIDDEN_SUFFIXES = (".safetensors", ".pth", ".pt", ".ckpt", ".key", ".pem", ".pkl")
FORBIDDEN_BASENAMES = {"secrets.toml", ".env", "credentials.json", "token.json"}
PRIVATE_MARKERS = ("bharatgen-", "private_bharatgen_evidence", "private_bharatgen_output")


def validate_entry_path(name: str) -> None:
    path = PurePosixPath(name)
    if (
        not name or name.startswith("/") or "\\" in name
        or any(part in {".", "..", ".git", ".venv", "__pycache__"} for part in path.parts)
        or path.is_absolute()
    ):
        raise ValueError(f"Unsafe archive path: {name}")
    lower = name.lower()
    if (
        path.name.lower() in FORBIDDEN_BASENAMES
        or lower.endswith(FORBIDDEN_SUFFIXES)
        or any(marker in lower and lower.endswith((".jsonl", ".zip", ".log")) for marker in PRIVATE_MARKERS)
    ):
        raise ValueError(f"Forbidden private/weight/secret archive entry: {name}")


def verify_submission_zip(location: str) -> dict:
    with zipfile.ZipFile(location, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Archive contains duplicate paths")
        if "SUBMISSION_MANIFEST.json" not in names:
            raise ValueError("Missing submission manifest")
        for info in archive.infolist():
            validate_entry_path(info.filename)
            # Never accept symlinks embedded inside the faculty archive.
            if info.create_system == 3 and ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError("Archive symlink prohibited")
            if info.file_size > 20_000_000:
                raise ValueError(f"Unexpected large file: {info.filename}")
        manifest = json.loads(archive.read("SUBMISSION_MANIFEST.json"))
        declared = manifest.get("files")
        if not isinstance(declared, dict) or not declared:
            raise ValueError("Manifest lacks file digests")
        if set(declared) != set(names) - {"SUBMISSION_MANIFEST.json"}:
            raise ValueError("Manifest/ZIP file set mismatch")
        if not REQUIRED.issubset(declared):
            raise ValueError(f"Faculty deliverables missing: {sorted(REQUIRED - set(declared))}")
        if not re.fullmatch("[0-9a-f]{40}", str(manifest.get("source_commit", ""))):
            raise ValueError("Missing exact 40-character source commit")
        for name, expected in declared.items():
            digest = hashlib.sha256(archive.read(name)).hexdigest()
            if not isinstance(expected, str) or not re.fullmatch("[0-9a-f]{64}", expected):
                raise ValueError(f"Bad manifest hash for {name}")
            if digest != expected:
                raise ValueError(f"SHA-256 mismatch in {name}")
        if not archive.read("reports/IndicWrite_CS3235_Project_Report.pdf").startswith(b"%PDF-"):
            raise ValueError("Report is not a PDF")
        metrics = json.loads(archive.read("evaluation/results/metrics.json"))
        if metrics.get("overall", {}).get("count") != 40:
            raise ValueError("Expected 40 genuine evaluation cases")
        if not manifest.get("not_verified"):
            raise ValueError("Submission must preserve explicit limitations")
        return {
            "source_commit": manifest["source_commit"],
            "files_checked": len(declared),
            "digests_match": True,
            "private_outputs_included": False,
            "metric_case_count": metrics["overall"]["count"],
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("zipfile")
    args = parser.parse_args()
    print("SUBMISSION_ZIP_INDEPENDENTLY_VERIFIED", json.dumps(
        verify_submission_zip(args.zipfile), sort_keys=True
    ), flush=True)


if __name__ == "__main__":
    main()
