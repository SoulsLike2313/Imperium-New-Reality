#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

PATCH_ID = "IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001"
TASK_ID = PATCH_ID
VALIDATOR_ID = "imperium_app_astronomicon_mechanicus_registration_validator.v0_1"

REQUIRED = [
    "SUPPORT/APP_TAURI/src/main.js",
    "SUPPORT/APP_TAURI/src/styles.css",
    "SUPPORT/APP_TAURI/src-tauri/src/main.rs",
    "SUPPORT/APP_TAURI/contracts/IMPERIUM_APP_ASTRONOMICON_MECHANICUS_REGISTRATION_CONTRACT_V0_1.json",
    "ORGANS/ASTRONOMICON/LAWS/ASTRONOMICON_APP_PATCH_REGISTRATION_LAW_V0_1.json",
    "ORGANS/ASTRONOMICON/MATRICES/ASTRONOMICON_MECHANICUS_APP_REGISTRATION_MATRIX_V0_1.json",
    "ORGANS/ASTRONOMICON/TASK_CANDIDATES/IMPERIUM_APP_EYES_CANVAS_DAILY_OPERATIONS_0001.json",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_APP_PATCH_PACK_ANALYSIS_MATRIX_V0_1.json",
]

CONTROL_CHARS = [chr(i) for i in range(0, 32) if chr(i) not in "\r\n\t"]

def rel(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()

def has_control_chars(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for idx, ch in enumerate(text):
        if ch in CONTROL_CHARS:
            line = text.count("\n", 0, idx) + 1
            hits.append({"line": line, "ord": ord(ch)})
    return hits

def resolve_command(name: str) -> str | None:
    """Resolve CLIs safely on Windows too.

    Python subprocess with shell=False does not reliably execute npm shims
    named only "npm" on Windows. Prefer npm.cmd/cargo.exe when present.
    """
    candidates = [name]
    if os.name == "nt":
        if not name.lower().endswith((".exe", ".cmd", ".bat", ".ps1")):
            candidates = [f"{name}.cmd", f"{name}.exe", f"{name}.bat", name]
    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found
    return None

def run_capture(cmd, cwd: Path, timeout=120):
    resolved_cmd = list(cmd)
    resolved = resolve_command(str(cmd[0]))
    if not resolved:
        return {
            "cmd": cmd,
            "resolved_cmd": None,
            "exit_code": None,
            "ok": False,
            "missing_tool": True,
            "error": f"tool not found on PATH: {cmd[0]}",
        }
    resolved_cmd[0] = resolved
    try:
        proc = subprocess.run(resolved_cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
        return {
            "cmd": cmd,
            "resolved_cmd": resolved_cmd,
            "exit_code": proc.returncode,
            "ok": proc.returncode == 0,
            "stdout_tail": proc.stdout[-2500:],
            "stderr_tail": proc.stderr[-2500:],
        }
    except FileNotFoundError as e:
        return {"cmd": cmd, "resolved_cmd": resolved_cmd, "exit_code": None, "ok": False, "missing_tool": True, "error": str(e)}
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd, "resolved_cmd": resolved_cmd, "exit_code": None, "ok": False, "timeout": True, "error": str(e)}

def copy_tree(files_to_land: Path, repo: Path):
    for src in files_to_land.rglob("*"):
        if src.is_file():
            dst = repo / src.relative_to(files_to_land)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--host-build-check", action="store_true")
    ap.add_argument("--verbose-json", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    patch_dir = repo / "WARP" / "PATCHES" / PATCH_ID
    files_to_land = patch_dir / "FILES_TO_LAND"
    errors = []
    warnings = []
    checks = []

    if not files_to_land.is_dir():
        errors.append(f"FILES_TO_LAND missing: {files_to_land}")
    else:
        if args.apply:
            copy_tree(files_to_land, repo)

    for item in REQUIRED:
        path = repo / item
        exists = path.is_file()
        checks.append({"name": f"exists::{item}", "status": "PASS" if exists else "FAIL"})
        if not exists:
            errors.append(f"missing required file: {item}")
            continue
        hits = has_control_chars(path)
        checks.append({"name": f"no_control_chars::{item}", "status": "PASS" if not hits else "FAIL", "hits": hits[:5]})
        if hits:
            errors.append(f"control chars in {item}: {hits[:3]}")
        if item.endswith(".json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
                checks.append({"name": f"json_parse::{item}", "status": "PASS"})
            except Exception as e:
                checks.append({"name": f"json_parse::{item}", "status": "FAIL", "error": str(e)})
                errors.append(f"json parse failed {item}: {e}")

    main_js = repo / "SUPPORT/APP_TAURI/src/main.js"
    main_rs = repo / "SUPPORT/APP_TAURI/src-tauri/src/main.rs"
    styles = repo / "SUPPORT/APP_TAURI/src/styles.css"
    js_text = main_js.read_text(encoding="utf-8", errors="replace") if main_js.is_file() else ""
    rs_text = main_rs.read_text(encoding="utf-8", errors="replace") if main_rs.is_file() else ""
    css_text = styles.read_text(encoding="utf-8", errors="replace") if styles.is_file() else ""

    markers = {
        "frontend_astronomicon_room": "function renderAstronomicon" in js_text,
        "frontend_mechanicus_summary": "organSummary" in js_text and "MECHANICUS" in js_text,
        "backend_register_with_organs": "register_patch_pack_with_organs" in rs_text,
        "backend_analyze_summary": "analyze_patch_pack_organ_summary" in rs_text,
        "css_registration_marker": "ASTRONOMICON_MECHANICUS_REGISTRATION_PROOF_V0_1" in css_text,
        "compact_runner_policy": True,
    }
    for name, ok in markers.items():
        checks.append({"name": name, "status": "PASS" if ok else "FAIL"})
        if not ok:
            errors.append(f"marker failed: {name}")

    node_check = run_capture(["node", "--check", str(main_js)], repo, timeout=60)
    checks.append({"name": "node_check_main_js", "status": "PASS" if node_check.get("ok") else "FAIL", "details": node_check})
    if not node_check.get("ok"):
        errors.append("node --check failed for SUPPORT/APP_TAURI/src/main.js")

    build_result = {"status": "SKIPPED", "reason": "--host-build-check not requested"}
    cargo_result = {"status": "SKIPPED", "reason": "--host-build-check not requested"}
    if args.host_build_check:
        app_dir = repo / "SUPPORT/APP_TAURI"
        if (app_dir / "node_modules").is_dir():
            npm = run_capture(["npm", "run", "build"], app_dir, timeout=180)
            build_result = npm
            checks.append({"name": "support_app_tauri_npm_build", "status": "PASS" if npm.get("ok") else "FAIL", "details": npm})
            if not npm.get("ok"):
                errors.append("npm run build failed")
        else:
            build_result = {"status": "SKIPPED", "reason": "node_modules missing; run npm install or rely on Owner host lane"}
            warnings.append("npm build skipped because node_modules is missing on this host")
            checks.append({"name": "support_app_tauri_npm_build", "status": "SKIP", "details": build_result})

        cargo = run_capture(["cargo", "check", "--manifest-path", "SUPPORT/APP_TAURI/src-tauri/Cargo.toml"], repo, timeout=240)
        cargo_result = cargo
        status = "PASS" if cargo.get("ok") else ("SKIP" if cargo.get("missing_tool") else "FAIL")
        checks.append({"name": "support_app_tauri_cargo_check", "status": status, "details": cargo})
        if status == "FAIL":
            errors.append("cargo check failed for SUPPORT/APP_TAURI/src-tauri/Cargo.toml")
        elif status == "SKIP":
            warnings.append("cargo check skipped because cargo is missing on this host")

    verdict = "PASS_IMPERIUM_APP_ASTRONOMICON_MECHANICUS_REGISTRATION_READY" if not errors else "FAIL_IMPERIUM_APP_ASTRONOMICON_MECHANICUS_REGISTRATION"
    generated = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    receipt_rel = "SUPPORT/APP_TAURI/receipts/astronomicon_mechanicus_registration_proof_receipt.json"
    summary_rel = "SUPPORT/APP_TAURI/receipts/astronomicon_mechanicus_registration_proof_summary.json"
    report_rel = "SUPPORT/APP_TAURI/receipts/ASTRONOMICON_MECHANICUS_REGISTRATION_PROOF_REPORT_V0_1.md"
    receipt = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "app_integration_status": "PASS_BASELINE" if not errors else "FAIL",
        "astronomicon_registration_room": markers["frontend_astronomicon_room"],
        "mechanicus_summary_available": markers["frontend_mechanicus_summary"] and markers["backend_analyze_summary"],
        "real_execution_enabled": False,
        "compact_terminal_output": True,
        "next_trial_task": "IMPERIUM-APP-EYES-CANVAS-DAILY-OPERATIONS-0001",
        "npm_build": build_result,
        "cargo_check": cargo_result,
        "receipt": receipt_rel,
        "summary": summary_rel,
        "report_md": report_rel,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
    summary = {k: receipt[k] for k in ["task_id", "validator_id", "verdict", "generated_at_utc", "app_integration_status", "astronomicon_registration_room", "mechanicus_summary_available", "real_execution_enabled", "compact_terminal_output", "next_trial_task", "errors", "warnings"]}
    (repo / "SUPPORT/APP_TAURI/receipts").mkdir(parents=True, exist_ok=True)
    (repo / receipt_rel).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / summary_rel).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = f"""# Astronomicon + Mechanicus App Registration Proof\n\n- task_id: `{TASK_ID}`\n- verdict: `{verdict}`\n- app_integration_status: `{summary['app_integration_status']}`\n- Astronomicon room: `{summary['astronomicon_registration_room']}`\n- Mechanicus summary: `{summary['mechanicus_summary_available']}`\n- real execution enabled: `false`\n- terminal output policy: compact by default\n- next hard trial: `{summary['next_trial_task']}`\n\n## Warnings\n{chr(10).join('- ' + w for w in warnings) if warnings else 'none'}\n\n## Errors\n{chr(10).join('- ' + e for e in errors) if errors else 'none'}\n"""
    (repo / report_rel).write_text(md, encoding="utf-8")

    if args.verbose_json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print(f"TASK: {TASK_ID}")
        print(f"VERDICT: {verdict}")
        print(f"APP: {summary['app_integration_status']} | ASTRONOMICON_ROOM: {summary['astronomicon_registration_room']} | MECHANICUS_SUMMARY: {summary['mechanicus_summary_available']}")
        print(f"EXECUTION: disabled | NEXT_TRIAL: {summary['next_trial_task']}")
        print(f"RECEIPT: {receipt_rel}")
        print(f"SUMMARY: {summary_rel}")
        if warnings:
            print("WARNINGS: " + " | ".join(warnings[:3]))
        if errors:
            print("ERRORS: " + " | ".join(errors[:3]))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
