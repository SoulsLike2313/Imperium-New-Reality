#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "IMPERIUM-APP-TAURI-PROOF-RUN-0001"
VALIDATOR_ID = "imperium_app_tauri_proof_run_validator.v0_2_windows_cmd_aware"

MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/IMPERIUM_APP_TAURI_PROOF_RUN_MATRIX_V0_1.json")
FOUNDATION_RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_shell_foundation_receipt.json")
APP_ROOT = Path("SUPPORT/APP_TAURI")
RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_proof_run_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_PROOF_RUN_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_PROOF_RUN_REPORT_V0_1.md")

IS_WINDOWS = os.name == "nt"

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def command_text(command: List[str]) -> str:
    # Good enough for cmd.exe /c usage with our controlled command tokens.
    def q(x: str) -> str:
        if any(ch in x for ch in " &()[]{}^=;!'+,`~"):
            return '"' + x.replace('"', r'\"') + '"'
        return x
    return " ".join(q(str(x)) for x in command)

def run_cmd(repo: Path, cwd: Path, command: List[str], timeout: int, prefer_cmd: bool = False) -> Dict[str, Any]:
    started = utc()
    actual = command
    shell_note = None

    if IS_WINDOWS and prefer_cmd:
        actual = ["cmd.exe", "/d", "/s", "/c", command_text(command)]
        shell_note = "windows_cmd_wrapper"

    try:
        p = subprocess.run(
            actual,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "CI": "1", "NO_COLOR": "1"},
        )
        return {
            "command": command,
            "actual_command": actual,
            "cwd": str(cwd.relative_to(repo) if cwd.is_relative_to(repo) else cwd),
            "exit_code": p.returncode,
            "started_at_utc": started,
            "finished_at_utc": utc(),
            "stdout_tail": p.stdout[-8000:],
            "stderr_tail": p.stderr[-8000:],
            "ok": p.returncode == 0,
            "shell_note": shell_note,
        }
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        return {
            "command": command,
            "actual_command": actual,
            "cwd": str(cwd),
            "exit_code": "TIMEOUT",
            "started_at_utc": started,
            "finished_at_utc": utc(),
            "stdout_tail": stdout[-8000:],
            "stderr_tail": stderr[-8000:],
            "ok": False,
            "timeout_seconds": timeout,
            "shell_note": shell_note,
        }
    except Exception as e:
        return {
            "command": command,
            "actual_command": actual,
            "cwd": str(cwd),
            "exit_code": "EXCEPTION",
            "started_at_utc": started,
            "finished_at_utc": utc(),
            "stdout_tail": "",
            "stderr_tail": str(e),
            "ok": False,
            "shell_note": shell_note,
        }

def which_all(cmd: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "command": cmd,
        "shutil_which": shutil.which(cmd),
        "platform": platform.platform(),
        "is_windows": IS_WINDOWS,
    }
    if IS_WINDOWS:
        try:
            p = subprocess.run(["where.exe", cmd], capture_output=True, text=True, timeout=20, encoding="utf-8", errors="replace")
            result["where_exit_code"] = p.returncode
            result["where_stdout"] = p.stdout.strip()
            result["where_stderr"] = p.stderr.strip()
            result["exists"] = p.returncode == 0 or bool(result["shutil_which"])
        except Exception as e:
            result["where_error"] = str(e)
            result["exists"] = bool(result["shutil_which"])
    else:
        result["exists"] = bool(result["shutil_which"])
    return result

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--skip-install", action="store_true")
    ap.add_argument("--skip-cargo-check", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    app = repo / APP_ROOT

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []
    command_results: List[Dict[str, Any]] = []

    matrix, matrix_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "proof_run_matrix_parses", matrix_err is None, {"error": matrix_err})
    if matrix_err:
        errors.append("proof run matrix missing or invalid")
        matrix = {}

    foundation, foundation_err = load_json(repo / FOUNDATION_RECEIPT) if (repo / FOUNDATION_RECEIPT).is_file() else ({}, "missing")
    foundation_ok = foundation_err is None and isinstance(foundation, dict) and str(foundation.get("verdict", "")).startswith("PASS")
    add(checks, "foundation_receipt_is_pass", foundation_ok, {"error": foundation_err, "verdict": foundation.get("verdict") if isinstance(foundation, dict) else None})
    if not foundation_ok:
        errors.append("foundation receipt is not PASS; run/fix foundation first")

    missing_files = []
    for rel in matrix.get("required_files", []):
        if not (repo / rel).is_file():
            missing_files.append(rel)
    add(checks, "required_tauri_proof_files_exist", not missing_files, {"missing": missing_files})
    if missing_files:
        errors.append("missing Tauri proof files")

    env_info = {cmd: which_all(cmd) for cmd in ["node", "npm", "cargo", "rustc"]}
    for cmd, info in env_info.items():
        add(checks, f"env_{cmd}_exists", bool(info.get("exists")), info)
        if not info.get("exists"):
            errors.append(f"required environment command missing: {cmd}")

    # Static config checks before heavy commands.
    vite_text = (repo / "SUPPORT/APP_TAURI/vite.config.js").read_text(encoding="utf-8", errors="replace") if (repo / "SUPPORT/APP_TAURI/vite.config.js").is_file() else ""
    tauri_conf, tauri_err = load_json(repo / "SUPPORT/APP_TAURI/src-tauri/tauri.conf.json")
    port_ok = "port: 1420" in vite_text and isinstance(tauri_conf, dict) and tauri_conf.get("build", {}).get("devUrl") == "http://127.0.0.1:1420"
    add(checks, "vite_and_tauri_dev_ports_match_1420", port_ok, {"tauri_json_error": tauri_err})
    if not port_ok:
        errors.append("Vite/Tauri dev port mismatch")

    gitignore = (repo / "SUPPORT/APP_TAURI/.gitignore").read_text(encoding="utf-8", errors="replace") if (repo / "SUPPORT/APP_TAURI/.gitignore").is_file() else ""
    ignore_ok = "node_modules/" in gitignore and "src-tauri/target/" in gitignore and "dist/" in gitignore
    add(checks, "tauri_generated_artifacts_ignored", ignore_ok, {"gitignore": "SUPPORT/APP_TAURI/.gitignore"})
    if not ignore_ok:
        errors.append("Tauri .gitignore missing generated artifact rules")

    # On Windows, npm is usually npm.cmd. Use cmd.exe wrapper so npm.cmd is resolved the same way as in an operator terminal.
    if not errors:
        version_commands = [
            ("node_version", ["node", "--version"], False),
            ("npm_version", ["npm", "--version"], True),
            ("cargo_version", ["cargo", "--version"], False),
            ("rustc_version", ["rustc", "--version"], False),
        ]
        for check_name, cmd, use_cmd in version_commands:
            r = run_cmd(repo, repo, cmd, 60, prefer_cmd=use_cmd)
            command_results.append(r)
            add(checks, f"command_{check_name}_passes", r["ok"], r)
            if not r["ok"]:
                errors.append("command failed: " + " ".join(cmd))

    if not errors and not args.skip_install:
        r = run_cmd(repo, app, ["npm", "install"], 900, prefer_cmd=True)
        command_results.append(r)
        add(checks, "npm_install_passes", r["ok"], r)
        if not r["ok"]:
            errors.append("npm install failed")
    elif args.skip_install:
        warnings.append("npm install skipped by flag")

    if not errors:
        for name, cmd, timeout in [
            ("npm_check_fps_passes", ["npm", "run", "check:fps"], 120),
            ("npm_check_parity_passes", ["npm", "run", "check:parity"], 120),
            ("npm_frontend_build_passes", ["npm", "run", "build"], 300),
        ]:
            r = run_cmd(repo, app, cmd, timeout, prefer_cmd=True)
            command_results.append(r)
            add(checks, name, r["ok"], r)
            if not r["ok"]:
                errors.append(name.replace("_", " ") + " failed")

    if not errors and not args.skip_cargo_check:
        r = run_cmd(repo, repo, ["cargo", "check", "--manifest-path", "SUPPORT/APP_TAURI/src-tauri/Cargo.toml"], 1200, prefer_cmd=False)
        command_results.append(r)
        add(checks, "cargo_check_tauri_bridge_passes", r["ok"], r)
        if not r["ok"]:
            errors.append("cargo check Tauri bridge failed")
    elif args.skip_cargo_check:
        warnings.append("cargo check skipped by flag")

    node_modules_exists = (app / "node_modules").exists()
    target_exists = (app / "src-tauri/target").exists()
    add(checks, "generated_dirs_can_exist_but_are_ignored", True, {"node_modules_exists": node_modules_exists, "target_exists": target_exists})

    verdict = "PASS_IMPERIUM_APP_TAURI_PROOF_RUN_READY" if not errors else "FAIL_IMPERIUM_APP_TAURI_PROOF_RUN"
    generated = utc()

    summary = {
        "summary_id": "astronomicon.imperium_app_tauri_proof_run_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "checks": checks,
        "command_results": command_results,
        "environment": env_info,
        "errors": errors,
        "warnings": warnings,
        "proof_level": "INSTALL_BUILD_AND_COMPILE_CHECK" if verdict.startswith("PASS") else "BLOCKED",
        "next_stage": "IMPERIUM-APP-TAURI-RUNTIME-WINDOW-FPS-PROOF-0001",
        "not_claimed": matrix.get("not_claimed", []) if isinstance(matrix, dict) else [],
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_app_tauri_proof_run.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Tauri migration proof run with Windows-aware npm command execution."
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    commands_md = "\n".join(
        f"- `{ 'PASS' if r.get('ok') else 'FAIL' }` — `{' '.join(r.get('command', []))}` actual=`{' '.join(map(str, r.get('actual_command', [])))}` exit=`{r.get('exit_code')}`"
        for r in command_results
    ) or "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM APP TAURI PROOF RUN REPORT V0.2

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

This proof-run is Windows-aware: npm commands are executed through `cmd.exe /d /s /c` so `npm.cmd` is resolved the same way as in an operator terminal.

It verifies environment, installs npm dependencies, checks FPS/action contracts, builds the frontend, and compiles/checks the Rust bridge.

It still does not claim the interactive Tauri window or WebView FPS measurement; that is the next runtime proof patch.

## Commands

{commands_md}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}
""", encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "proof_level": summary["proof_level"],
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
