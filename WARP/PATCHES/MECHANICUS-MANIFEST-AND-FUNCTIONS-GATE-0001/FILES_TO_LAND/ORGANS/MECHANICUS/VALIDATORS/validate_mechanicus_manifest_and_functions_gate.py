#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, shutil
from pathlib import Path

TASK_ID = "MECHANICUS-MANIFEST-AND-FUNCTIONS-GATE-0001"
VALIDATOR_ID = "mechanicus_manifest_and_functions_gate_validator.v0_1"
REQUIRED_STATIC = [
    "ORGANS/MECHANICUS/MANIFEST.json",
    "ORGANS/MECHANICUS/FUNCTIONS.md",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_FUNCTION_REGISTRY_V0_1.json",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_MATRIX_V0_1.json",
    "ORGANS/MECHANICUS/TOOLS/build_mechanicus_manifest_and_functions_gate.py",
    "ORGANS/MECHANICUS/VALIDATORS/validate_mechanicus_manifest_and_functions_gate.py",
    "ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_PROSECUTOR_MATRIX_V0_1.json",
    "ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_CROWN_MATRIX_V0_1.json",
]
CONTROL_CHARS = {chr(i) for i in range(32)} - {"\n", "\r", "\t"}


def has_control_chars(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for idx, ch in enumerate(text):
        if ch in CONTROL_CHARS:
            line = text.count("\n", 0, idx) + 1
            col = idx - text.rfind("\n", 0, idx)
            hits.append({"line": line, "column": col, "ord": ord(ch)})
    return hits


def copy_files_to_land(files_to_land: Path, repo_root: Path):
    if not files_to_land.exists():
        raise FileNotFoundError(f"FILES_TO_LAND not found: {files_to_land}")
    for child in files_to_land.iterdir():
        dst = repo_root / child.name
        if child.is_dir():
            shutil.copytree(child, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, dst)


def load_builder(repo_root: Path):
    builder_path = repo_root / "ORGANS/MECHANICUS/TOOLS/build_mechanicus_manifest_and_functions_gate.py"
    spec = importlib.util.spec_from_file_location("build_mechanicus_manifest_and_functions_gate", builder_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {builder_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--files-to-land", default=None)
    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()

    if args.apply:
        if not args.files_to_land:
            raise SystemExit("--apply requires --files-to-land")
        copy_files_to_land(Path(args.files_to_land).resolve(), repo_root)

    errors = []
    warnings = []
    checks = []

    def check(name, status, details=None, error=None):
        checks.append({"name": name, "status": "PASS" if status else "FAIL", "details": details or {}})
        if not status and error:
            errors.append(error)

    for rel in REQUIRED_STATIC:
        p = repo_root / rel
        check(f"exists::{rel}", p.exists(), {"path": rel}, f"missing required static file: {rel}")
        if p.exists() and p.suffix.lower() in {".py", ".ps1", ".json", ".md"}:
            hits = has_control_chars(p)
            check(f"no_control_chars::{rel}", not hits, {"hits": hits[:10]}, f"control characters found in {rel}: {hits[:3]}")

    if not errors:
        builder = load_builder(repo_root)
        result = builder.build(repo_root, write_outputs=True)
        receipt = result["receipt"]
        report = result["report"]
        checks.append({"name": "builder_runs", "status": "PASS", "details": receipt})
        if receipt.get("errors"):
            errors.extend(receipt["errors"])
        check("receipt_verdict_pass", receipt.get("verdict") == "PASS_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_READY", {"verdict": receipt.get("verdict")}, "receipt verdict is not PASS_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_READY")
        check("no_organ_assembly_claim", receipt.get("organ_assembly_claim") is False, {"value": receipt.get("organ_assembly_claim")}, "organ assembly claim must remain false")
        check("no_six_gate_closure_claim", receipt.get("six_gate_closure_claim") is False, {"value": receipt.get("six_gate_closure_claim")}, "six gate closure claim must remain false")
        check("identity_and_functions_baseline", report.get("identity_gate_status") == "PASS_BASELINE" and report.get("functions_gate_status") == "PASS_BASELINE", {"identity": report.get("identity_gate_status"), "functions": report.get("functions_gate_status")}, "identity/functions gate baseline did not pass")
        warnings.extend(receipt.get("warnings", []))

    verdict = "PASS_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_READY" if not errors else "FAIL_MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE"
    output = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "receipt": "ORGANS/MECHANICUS/RECEIPTS/mechanicus_manifest_and_functions_gate_receipt.json",
        "summary": "ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_SUMMARY_V0_1.json",
        "report_json": "ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_REPORT_V0_1.json",
        "report_md": "ORGANS/MECHANICUS/REPORTS/MECHANICUS_MANIFEST_AND_FUNCTIONS_GATE_REPORT_V0_1.md",
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
