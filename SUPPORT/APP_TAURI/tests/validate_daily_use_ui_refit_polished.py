#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

TASK_ID = "IMPERIUM-APP-DAILY-USE-UI-REFIT-POLISHED-0001"
VERDICT_PASS = "PASS_IMPERIUM_APP_DAILY_USE_UI_REFIT_POLISHED_READY"
VERDICT_FAIL = "FAIL_IMPERIUM_APP_DAILY_USE_UI_REFIT_POLISHED"


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for c in [cur, *cur.parents]:
        if (c/"SUPPORT"/"APP_TAURI").is_dir() and (c/"WARP").is_dir():
            return c
    raise SystemExit("Repo root not found")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def has_control_chars(path: Path) -> bool:
    data = path.read_bytes()
    return any((b < 32 and b not in (9,10,13)) for b in data)


def run_cmd(cmd: list[str], cwd: Path, timeout: int=120) -> dict:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
        return {"ok": p.returncode == 0, "exit_code": p.returncode, "missing_tool": False, "stdout_tail": "\n".join(p.stdout.splitlines()[-12:]), "stderr_tail": "\n".join(p.stderr.splitlines()[-12:]), "error": ""}
    except FileNotFoundError as e:
        return {"ok": False, "exit_code": None, "missing_tool": True, "stdout_tail": "", "stderr_tail": "", "error": str(e)}
    except subprocess.TimeoutExpired as e:
        return {"ok": False, "exit_code": None, "missing_tool": False, "timeout": True, "stdout_tail": str(e.stdout or "")[-1200:], "stderr_tail": str(e.stderr or "")[-1200:], "error": "timeout"}


def npm_cmd() -> str:
    return "npm.cmd" if os.name == "nt" else "npm"


def cargo_cmd() -> str:
    return "cargo.exe" if os.name == "nt" else "cargo"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    repo = find_repo_root(Path(args.repo_root))
    app = repo/"SUPPORT"/"APP_TAURI"
    main_js = app/"src"/"main.js"
    css = app/"src"/"styles.css"
    contract = app/"contracts"/"IMPERIUM_APP_DAILY_USE_UI_REFIT_POLISHED_CONTRACT_V0_1.json"
    errors: list[str] = []
    warnings = ["Polished UI refit proves daily cockpit baseline only; Eyes/Canvas is still a future pack.", "Launch gate remains Astronomicon-owned and Owner-reviewed."]
    checks = []
    required_files = [main_js, css, contract]
    for p in required_files:
        ok = p.is_file()
        checks.append({"name": f"exists::{p.relative_to(repo).as_posix()}", "ok": ok})
        if not ok: errors.append(f"missing file: {p.relative_to(repo).as_posix()}")
        elif has_control_chars(p): errors.append(f"control chars: {p.relative_to(repo).as_posix()}")
    main_text = read_text(main_js) if main_js.is_file() else ""
    css_text = read_text(css) if css.is_file() else ""
    markers = [
        "IMPERIUM_APP_DAILY_USE_UI_REFIT_POLISHED_V0_1",
        "COMPACT_PROOF_DIGEST_V0_1",
        "MECHANICUS_NODE_BOUNDARY_MAP_V0_1",
        "daily-use-proof-stack",
        "daily-proof-ledger",
        "aquariumLines.slice(-14)",
    ]
    for m in markers:
        ok = m in main_text or m in css_text
        checks.append({"name": f"marker::{m}", "ok": ok})
        if not ok: errors.append(f"missing marker: {m}")
    if "Patch Forge" in main_text and "PATCH_FORGE DEPRECATED" not in main_text:
        errors.append("Patch Forge appears as active daily UI label")
    npm = run_cmd([npm_cmd(), "run", "build"], app, timeout=150)
    cargo = run_cmd([cargo_cmd(), "check"], app/"src-tauri", timeout=180)
    if not npm.get("ok"):
        errors.append("npm run build failed")
    if not cargo.get("ok"):
        errors.append("cargo check failed")
    out_dir = app/"receipts"
    out_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "task_id": TASK_ID,
        "validator_id": "imperium_app_daily_use_ui_refit_polished_validator.v0_1",
        "generated_at_unix": int(time.time()),
        "verdict": VERDICT_FAIL if errors else VERDICT_PASS,
        "daily_ui_refit_status": "PASS_DAILY_COCKPIT_BASELINE" if not errors else "FAIL_DAILY_COCKPIT_BASELINE",
        "compact_proof_digest": "PASS" if not errors else "FAIL",
        "patch_forge_removed_from_daily_nav": "patch-forge" not in main_text.split("const roomList",1)[1].split("];",1)[0] if "const roomList" in main_text else False,
        "astronomicon_owns_registration_and_launch": "Launch polished only" in main_text and "Astronomicon owns registration" in main_text,
        "node_boundary_map_ready": "MECHANICUS_NODE_BOUNDARY_MAP_V0_1" in main_text,
        "proof_log_last_lines": 14 if "aquariumLines.slice(-14)" in main_text else None,
        "npm_build": npm,
        "cargo_check": cargo,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }
    summary = {
        "task_id": TASK_ID,
        "verdict": receipt["verdict"],
        "daily_ui_refit_status": receipt["daily_ui_refit_status"],
        "compact_proof_digest": receipt["compact_proof_digest"],
        "patch_forge_removed_from_daily_nav": receipt["patch_forge_removed_from_daily_nav"],
        "astronomicon_owns_registration_and_launch": receipt["astronomicon_owns_registration_and_launch"],
        "node_boundary_map_ready": receipt["node_boundary_map_ready"],
        "proof_log_last_lines": receipt["proof_log_last_lines"],
        "npm_build_ok": npm.get("ok"),
        "cargo_check_ok": cargo.get("ok"),
    }
    receipt_path = out_dir/"daily_use_ui_refit_polished_receipt.json"
    summary_path = out_dir/"daily_use_ui_refit_polished_summary.json"
    if args.apply:
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print(f"TASK: {TASK_ID}")
        print(f"VERDICT: {receipt['verdict']}")
        print(f"UI: compact_digest={summary['compact_proof_digest']} | node_map={summary['node_boundary_map_ready']} | log_lines={summary['proof_log_last_lines']}")
        print(f"BUILD: npm={summary['npm_build_ok']} | cargo={summary['cargo_check_ok']}")
        print(f"SUMMARY: {summary_path.relative_to(repo).as_posix()}")
        print(f"RECEIPT: {receipt_path.relative_to(repo).as_posix()}")
        if errors:
            print("ERRORS: " + "; ".join(errors[:4]))
        if warnings:
            print("WARNINGS: " + " | ".join(warnings[:2]))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
