#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import py_compile
import subprocess
import sys
from pathlib import Path
from typing import Any

REQUIRED = [
    "ORGANS/ASTRONOMICON/TOOLS/build_astronomicon_patch_pack_inventory.py",
    "ORGANS/MECHANICUS/TOOLS/build_mechanicus_code_topology.py",
    "SUPPORT/APP_TAURI/tools/imperium_core_self_analyze.py",
    "SUPPORT/APP_TAURI/contracts/IMPERIUM_CORE_SELF_ANALYSIS_CONTRACT_V0_1.json",
]


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def has_control_chars(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    hits = []
    allowed = {9, 10, 13}
    for i, b in enumerate(data):
        if b < 32 and b not in allowed:
            hits.append({"offset": i, "byte": b})
            if len(hits) >= 5:
                break
    return hits


def run_py(repo_root: Path, script: str, args: list[str]) -> dict[str, Any]:
    cmd = [sys.executable, str(repo_root / script), "--repo-root", str(repo_root), *args]
    try:
        proc = subprocess.run(cmd, cwd=str(repo_root), text=True, capture_output=True, timeout=180)
        return {"ok": proc.returncode == 0, "exit_code": proc.returncode, "stdout_tail": proc.stdout.splitlines()[-6:], "stderr_tail": proc.stderr.splitlines()[-6:]}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "stdout_tail": [], "stderr_tail": []}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    errors = []
    warnings = []
    checks = []

    for item in REQUIRED:
        path = repo_root / item
        exists = path.exists()
        checks.append({"name": f"exists::{item}", "status": "PASS" if exists else "FAIL"})
        if not exists:
            errors.append(f"missing required file: {item}")
            continue
        hits = has_control_chars(path)
        checks.append({"name": f"no_control_chars::{item}", "status": "PASS" if not hits else "FAIL", "details": {"hits": hits}})
        if hits:
            errors.append(f"control chars in {item}: {hits}")
        if path.suffix == ".py":
            try:
                py_compile.compile(str(path), doraise=True)
                checks.append({"name": f"py_compile::{item}", "status": "PASS"})
            except Exception as exc:
                checks.append({"name": f"py_compile::{item}", "status": "FAIL", "details": {"error": str(exc)}})
                errors.append(f"python compile failed: {item}: {exc}")
        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
                checks.append({"name": f"json_parse::{item}", "status": "PASS"})
            except Exception as exc:
                checks.append({"name": f"json_parse::{item}", "status": "FAIL", "details": {"error": str(exc)}})
                errors.append(f"json parse failed: {item}: {exc}")

    run = {"ok": False}
    if not errors:
        run = run_py(repo_root, "SUPPORT/APP_TAURI/tools/imperium_core_self_analyze.py", ["--compact"])
        checks.append({"name": "self_analyze_runs", "status": "PASS" if run.get("ok") else "FAIL", "details": run})
        if not run.get("ok"):
            errors.append("self analysis tool failed")

    summary_path = repo_root / "SUPPORT" / "APP_TAURI" / "receipts" / "imperium_core_self_analysis_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        checks.append({"name": "summary_verdict", "status": "PASS" if summary.get("verdict") == "PASS_IMPERIUM_CORE_SELF_ANALYSIS_READY" else "FAIL", "details": {"verdict": summary.get("verdict")}})
        if summary.get("core_v1_claim") is not False:
            errors.append("core_v1_claim must remain false")
        if summary.get("real_execution_gateway_claim") is not False:
            errors.append("real execution gateway claim must remain false")
    elif not errors:
        errors.append("summary not generated")

    verdict = "PASS_IMPERIUM_CORE_SELF_ANALYSIS_VALIDATION_READY" if not errors else "FAIL_IMPERIUM_CORE_SELF_ANALYSIS_VALIDATION"
    result = {
        "task_id": "IMPERIUM-CORE-SELF-ANALYSIS-0001",
        "validator_id": "validate_imperium_core_self_analysis.v0_1",
        "verdict": verdict,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
    out_dir = repo_root / "SUPPORT" / "APP_TAURI" / "receipts"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "imperium_core_self_analysis_validation_receipt.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"VERDICT: {verdict}")
    if run.get("stdout_tail"):
        print("SELF_ANALYZE: " + " | ".join(run["stdout_tail"][:4]))
    if errors:
        print("ERRORS: " + " | ".join(errors[:4]))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
