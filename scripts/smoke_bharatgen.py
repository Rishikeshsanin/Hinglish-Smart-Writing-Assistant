"""Genuine checkpoint test. JSONL logs are runtime evidence, not quality scores."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from indicwrite.param_rewrite import BharatGenRewriter, MODEL_ID, MODEL_REVISION


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-model-download", action="store_true")
    parser.add_argument("--allow-remote-code", action="store_true")
    parser.add_argument("--device", choices=["cuda:0", "cpu"], default="cuda:0")
    parser.add_argument("--cases", type=Path)
    parser.add_argument("--output", type=Path, default=Path("bharatgen-smoke.jsonl"))
    args = parser.parse_args()
    if not (args.allow_model_download and args.allow_remote_code):
        parser.error("Review pinned code first; explicitly pass both --allow-model-download and --allow-remote-code.")
    # Exclusive create prevents a failed rerun from leaving an old success log.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as log:
        def emit(event):
            line = json.dumps(event, ensure_ascii=False)
            log.write(line + "\n")
            log.flush()
            print(line, flush=True)

        emit({"event": "start", "utc": datetime.now(timezone.utc).isoformat(),
              "model_id": MODEL_ID, "model_revision": MODEL_REVISION,
              "python": platform.python_version(), "device_requested": args.device,
              "meaning_preservation": "NOT_EVALUATED"})
        try:
            import torch
            packages = {p: importlib.metadata.version(p) for p in
                        ["torch", "transformers", "accelerate", "safetensors", "tokenizers", "huggingface-hub"]}
            git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                 capture_output=True, text=True)
            dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                   capture_output=True, text=True)
            emit({"event": "environment", "packages": packages,
                  "source_commit": git.stdout.strip() if git.returncode == 0 else None,
                  "source_dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
                  "adapter_sha256": hashlib.sha256((ROOT / "src/indicwrite/param_rewrite.py").read_bytes()).hexdigest(),
                  "cuda_build": torch.version.cuda,
                  "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None})
            if args.device.startswith("cuda"):
                if not torch.cuda.is_available():
                    raise RuntimeError("CUDA unavailable; no CPU fallback attempted.")
                torch.cuda.reset_peak_memory_stats()
                emit({"event": "gpu_memory_before", "free_total_bytes": list(torch.cuda.mem_get_info())})
            cases = [{"id": "smoke", "input": "सीता रोज़ स्कूल जाता है।"}]
            if args.cases:
                cases = json.loads(args.cases.read_text(encoding="utf-8"))
            if not cases:
                raise ValueError("No test cases supplied.")
            started = time.perf_counter()
            engine = BharatGenRewriter.load(allow_remote_code=True, device=args.device)
            emit({"event": "loaded", "seconds": time.perf_counter() - started,
                  "class": type(engine.model).__name__, "dtype": str(engine.model.dtype),
                  "device_map": {k: str(v) for k, v in engine.model.hf_device_map.items()},
                  "context_limit": engine.model.config.max_position_embeddings})
            passed = 0
            for case in cases:
                started = time.perf_counter()
                try:
                    record = engine.generate_record(case["input"])
                    if args.device.startswith("cuda"):
                        torch.cuda.synchronize()
                    record.update(event="generation", case_id=case["id"], seconds=time.perf_counter() - started)
                    emit(record)
                    passed += int(record["runtime_candidate_ok"])
                except Exception as exc:
                    emit({"event": "case_error", "case_id": case.get("id"),
                          "type": type(exc).__name__, "message": str(exc)})
            if args.device.startswith("cuda"):
                emit({"event": "gpu_peak", "allocated_bytes": torch.cuda.max_memory_allocated(),
                      "reserved_bytes": torch.cuda.max_memory_reserved()})
            ok = passed == len(cases)
            emit({"event": "summary", "cases": len(cases), "runtime_candidates_passed": passed,
                  "status": "REAL_MODEL_RUNTIME_PASS" if ok else "REAL_MODEL_RUNTIME_FAIL",
                  "quality": "NOT_EVALUATED; human review required"})
            return 0 if ok else 1
        except Exception as exc:
            emit({"event": "error", "type": type(exc).__name__, "message": str(exc),
                  "status": "FAILED; no inference success claim"})
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
