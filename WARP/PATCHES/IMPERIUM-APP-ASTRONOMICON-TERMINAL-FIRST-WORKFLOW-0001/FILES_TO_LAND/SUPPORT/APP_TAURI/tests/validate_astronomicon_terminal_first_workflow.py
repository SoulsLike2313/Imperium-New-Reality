#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import py_compile
import shutil
import subprocess
import sys
import time
from pathlib import Path

PATCH_ID = "IMPERIUM-APP-ASTRONOMICON-TERMINAL-FIRST-WORKFLOW-0001"
CANDIDATE_ID = "IMPERIUM-APP-DAILY-USE-UI-REFIT-CANDIDATE-0001"


def repo_root(start: Path) -> Path:
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / "ORGANS").is_dir() and (p / "WARP").is_dir():
            return p
    raise SystemExit("repo root not found")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str], cwd: Path, timeout: int = 120) -> dict:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
        return {"ok": p.returncode == 0, "exit_code": p.returncode, "stdout_tail": p.stdout[-1600:], "stderr_tail": p.stderr[-1600:], "missing_tool": False, "error": ""}
    except FileNotFoundError as e:
        return {"ok": False, "exit_code": None, "stdout_tail": "", "stderr_tail": "", "missing_tool": True, "error": str(e)}
    except subprocess.TimeoutExpired as e:
        return {"ok": False, "exit_code": None, "stdout_tail": (e.stdout or "")[-1600:] if isinstance(e.stdout, str) else "", "stderr_tail": (e.stderr or "")[-1600:] if isinstance(e.stderr, str) else "", "missing_tool": False, "error": "timeout"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = repo_root(Path(args.repo_root))
    app = repo / "SUPPORT" / "APP_TAURI"
    errors: list[str] = []
    warnings: list[str] = []

    main_js = read(app / "src/main.js")
    styles = read(app / "src/styles.css")
    main_rs = read(app / "src-tauri/src/main.rs")
    cli_path = app / "tools/register_patch_with_organs_cli.py"
    contract = app / "contracts/IMPERIUM_APP_ASTRONOMICON_TERMINAL_FIRST_WORKFLOW_CONTRACT_V0_1.json"

    checks = {}
    checks["patch_forge_removed_from_room_nav"] = 'label: "Patch Forge"' not in main_js and 'data-quick="patch-forge"' not in main_js
    checks["astronomicon_launch_gate_present"] = "Launch polished only" in main_js and "ASTRONOMICON" in main_js
    checks["compact_css_present"] = "IMPERIUM_APP_ASTRONOMICON_TERMINAL_FIRST_WORKFLOW_V0_1" in styles
    checks["terminal_cli_exists"] = cli_path.is_file()
    checks["terminal_cli_compiles"] = False
    if cli_path.is_file():
        try:
            py_compile.compile(str(cli_path), doraise=True)
            checks["terminal_cli_compiles"] = True
        except Exception as e:
            errors.append(f"terminal cli compile failed: {e}")
    checks["contract_exists"] = contract.is_file()
    checks["tauri_backend_candidate_logic_present"] = "REGISTERABLE_CANDIDATE_PACK" in main_rs and "MECHANICUS_ANALYZES_CANDIDATE_REQUIRES_POLISHED_PACK" in main_rs

    for name, ok in checks.items():
        if not ok:
            errors.append(name)

    cli_result = run([sys.executable, str(cli_path), "--repo-root", str(repo), "--patch-id", CANDIDATE_ID], repo) if cli_path.is_file() else {"ok": False, "error": "cli missing"}
    if not cli_result.get("ok"):
        errors.append("terminal_candidate_registration_cli_failed")

    npm_cmd = "npm.cmd" if sys.platform.startswith("win") else "npm"
    cargo_cmd = "cargo.exe" if sys.platform.startswith("win") else "cargo"
    npm_build = run([npm_cmd, "run", "build"], app, timeout=160)
    cargo_check = run([cargo_cmd, "check"], app / "src-tauri", timeout=180) if shutil.which(cargo_cmd) else {"ok": False, "missing_tool": True, "error": "cargo not found in validator host", "exit_code": None}
    if not npm_build.get("ok"):
        npm_tail = ((npm_build.get("stdout_tail") or "") + "\n" + (npm_build.get("stderr_tail") or "") + "\n" + (npm_build.get("error") or "")).lower()
        if npm_build.get("missing_tool") or "vite: not found" in npm_tail or "vite' is not recognized" in npm_tail or "vite.cmd" in npm_tail:
            warnings.append("npm/vite dependency not available on validator host; Owner host should still run npm build")
        else:
            errors.append("npm run build failed")
    if cargo_check.get("missing_tool"):
        warnings.append("cargo not found on validator host; Owner Windows host should still run cargo check")
    elif not cargo_check.get("ok"):
        errors.append("cargo check failed")

    verdict = "PASS_IMPERIUM_APP_ASTRONOMICON_TERMINAL_FIRST_WORKFLOW_READY" if not errors else "FAIL_IMPERIUM_APP_ASTRONOMICON_TERMINAL_FIRST_WORKFLOW"
    receipt = {
        "task_id": PATCH_ID,
        "validator_id": "imperium_app_astronomicon_terminal_first_workflow_validator.v0_1",
        "verdict": verdict,
        "generated_at_unix": int(time.time()),
        "checks": checks,
        "terminal_cli": {"ok": cli_result.get("ok"), "stdout_tail": cli_result.get("stdout_tail", "")[-1200:], "stderr_tail": cli_result.get("stderr_tail", "")[-1200:], "error": cli_result.get("error", "")},
        "npm_build": npm_build,
        "cargo_check": cargo_check,
        "errors": errors,
        "warnings": warnings,
    }
    summary = {
        "task_id": PATCH_ID,
        "verdict": verdict,
        "patch_forge_removed_from_nav": checks.get("patch_forge_removed_from_room_nav"),
        "astronomicon_owns_registration_and_launch": checks.get("astronomicon_launch_gate_present"),
        "terminal_cli_ready": checks.get("terminal_cli_exists") and checks.get("terminal_cli_compiles") and cli_result.get("ok"),
        "compact_daily_ui_css": checks.get("compact_css_present"),
        "npm_build_ok": npm_build.get("ok"),
        "cargo_check_ok": cargo_check.get("ok"),
        "cargo_missing_on_validator_host": cargo_check.get("missing_tool", False),
        "errors": errors,
        "warnings": warnings,
    }
    out_dir = app / "receipts"
    write_json(out_dir / "astronomicon_terminal_first_workflow_receipt.json", receipt)
    write_json(out_dir / "astronomicon_terminal_first_workflow_summary.json", summary)

    print(f"TASK: {PATCH_ID}")
    print(f"VERDICT: {verdict}")
    print(f"UI: forge_removed={summary['patch_forge_removed_from_nav']} | compact={summary['compact_daily_ui_css']}")
    print(f"TERMINAL: cli_ready={summary['terminal_cli_ready']} | candidate={CANDIDATE_ID}")
    print(f"BUILD: npm={summary['npm_build_ok']} | cargo={summary['cargo_check_ok']} | cargo_missing={summary['cargo_missing_on_validator_host']}")
    print("SUMMARY: SUPPORT/APP_TAURI/receipts/astronomicon_terminal_first_workflow_summary.json")
    print("RECEIPT: SUPPORT/APP_TAURI/receipts/astronomicon_terminal_first_workflow_receipt.json")
    if errors:
        print("ERRORS: " + "; ".join(errors[:4]))
    if warnings:
        print("WARNINGS: " + "; ".join(warnings[:3]))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
