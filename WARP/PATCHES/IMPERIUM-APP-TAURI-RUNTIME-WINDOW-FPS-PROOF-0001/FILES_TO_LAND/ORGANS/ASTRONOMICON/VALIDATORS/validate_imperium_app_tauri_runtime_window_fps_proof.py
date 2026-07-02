#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "IMPERIUM-APP-TAURI-RUNTIME-WINDOW-FPS-PROOF-0001"
VALIDATOR_ID = "imperium_app_tauri_runtime_window_fps_proof_validator.v0_1"

MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF_MATRIX_V0_1.json")
PROOF_RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_proof_run_receipt.json")
APP_ROOT = Path("SUPPORT/APP_TAURI")
APP_RECEIPTS = Path("SUPPORT/APP_TAURI/receipts")
APP_LOGS = Path("SUPPORT/APP_TAURI/logs")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_runtime_window_fps_proof_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF_REPORT_V0_1.md")

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

def cmd_text(tokens: List[str]) -> str:
    def q(x: str) -> str:
        if any(ch in x for ch in " &()[]{}^=;!'+,`~"):
            return '"' + x.replace('"', r'\"') + '"'
        return x
    return " ".join(q(str(x)) for x in tokens)

def kill_tree(pid: int):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, text=True, timeout=30)
    else:
        try:
            os.kill(pid, 15)
        except Exception:
            pass

def newest_runtime_receipt(repo: Path, started_ts: float) -> Path | None:
    receipts_dir = repo / APP_RECEIPTS
    if not receipts_dir.exists():
        return None
    candidates = []
    for p in receipts_dir.glob("*runtime_fps_proof_receipt.json"):
        try:
            if p.stat().st_mtime >= started_ts:
                candidates.append(p)
        except OSError:
            pass
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--timeout-seconds", type=int, default=300)
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    app = repo / APP_ROOT
    app_logs = repo / APP_LOGS
    app_logs.mkdir(parents=True, exist_ok=True)
    (repo / APP_RECEIPTS).mkdir(parents=True, exist_ok=True)

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    matrix, matrix_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "runtime_fps_matrix_parses", matrix_err is None, {"error": matrix_err})
    if matrix_err:
        errors.append("runtime FPS matrix missing or invalid")
        matrix = {}

    proof, proof_err = load_json(repo / PROOF_RECEIPT) if (repo / PROOF_RECEIPT).is_file() else ({}, "missing")
    proof_ok = proof_err is None and isinstance(proof, dict) and str(proof.get("verdict", "")).startswith("PASS")
    add(checks, "tauri_install_build_compile_proof_is_pass", proof_ok, {"error": proof_err, "verdict": proof.get("verdict") if isinstance(proof, dict) else None})
    if not proof_ok:
        errors.append("Tauri proof-run receipt is not PASS")

    missing_files = []
    for rel in matrix.get("required_files", []):
        if not (repo / rel).is_file():
            missing_files.append(rel)
    add(checks, "runtime_required_files_exist", not missing_files, {"missing": missing_files})
    if missing_files:
        errors.append("runtime proof required files missing")

    js_text = (repo / "SUPPORT/APP_TAURI/src/main.js").read_text(encoding="utf-8", errors="replace") if (repo / "SUPPORT/APP_TAURI/src/main.js").is_file() else ""
    rust_text = (repo / "SUPPORT/APP_TAURI/src-tauri/src/main.rs").read_text(encoding="utf-8", errors="replace") if (repo / "SUPPORT/APP_TAURI/src-tauri/src/main.rs").is_file() else ""
    missing_js = [m for m in matrix.get("required_frontend_markers", []) if m not in js_text]
    missing_rust = [m for m in matrix.get("required_rust_markers", []) if m not in rust_text]
    add(checks, "frontend_runtime_fps_markers_present", not missing_js, {"missing": missing_js})
    add(checks, "rust_runtime_fps_command_markers_present", not missing_rust, {"missing": missing_rust})
    if missing_js:
        errors.append("frontend runtime FPS markers missing")
    if missing_rust:
        errors.append("Rust runtime FPS command markers missing")

    command_results: List[Dict[str, Any]] = []
    runtime_receipt_data: Dict[str, Any] | None = None
    runtime_receipt_rel: str | None = None
    stdout_log = app_logs / "runtime_window_fps_proof_tauri_dev_stdout.log"
    stderr_log = app_logs / "runtime_window_fps_proof_tauri_dev_stderr.log"

    if not errors:
        started_ts = time.time()
        command = ["cmd.exe", "/d", "/s", "/c", cmd_text(["npm", "run", "tauri:dev"])] if os.name == "nt" else ["npm", "run", "tauri:dev"]
        started_at = utc()

        with stdout_log.open("w", encoding="utf-8", errors="replace") as out, stderr_log.open("w", encoding="utf-8", errors="replace") as err:
            proc = subprocess.Popen(
                command,
                cwd=str(app),
                stdout=out,
                stderr=err,
                text=True,
                env={**os.environ, "NO_COLOR": "1"},
            )

            receipt_path = None
            deadline = time.time() + args.timeout_seconds
            try:
                while time.time() < deadline:
                    receipt_path = newest_runtime_receipt(repo, started_ts)
                    if receipt_path:
                        break
                    if proc.poll() is not None:
                        break
                    time.sleep(1.0)
            finally:
                if proc.poll() is None:
                    kill_tree(proc.pid)
                    time.sleep(1.0)

        exit_code = proc.poll()
        if exit_code is None:
            exit_code = "KILLED_AFTER_RECEIPT_OR_TIMEOUT"

        command_result = {
            "command": ["npm", "run", "tauri:dev"],
            "actual_command": command,
            "cwd": APP_ROOT.as_posix(),
            "exit_code": exit_code,
            "started_at_utc": started_at,
            "finished_at_utc": utc(),
            "stdout_log": str(stdout_log.relative_to(repo)),
            "stderr_log": str(stderr_log.relative_to(repo)),
            "stdout_tail": stdout_log.read_text(encoding="utf-8", errors="replace")[-6000:] if stdout_log.exists() else "",
            "stderr_tail": stderr_log.read_text(encoding="utf-8", errors="replace")[-6000:] if stderr_log.exists() else "",
        }
        command_results.append(command_result)

        receipt_path = newest_runtime_receipt(repo, started_ts)
        runtime_receipt_found = receipt_path is not None
        add(checks, "tauri_dev_window_created_runtime_fps_receipt", runtime_receipt_found, command_result)
        if not runtime_receipt_found:
            errors.append("Tauri dev runtime did not produce runtime FPS proof receipt")
        else:
            runtime_receipt_rel = str(receipt_path.relative_to(repo)).replace("\\", "/")
            runtime_receipt_data, receipt_err = load_json(receipt_path)
            receipt_pass = receipt_err is None and isinstance(runtime_receipt_data, dict) and runtime_receipt_data.get("verdict") == "PASS_TAURI_RUNTIME_WINDOW_FPS_LOCK_PROVEN"
            add(checks, "runtime_fps_lock_receipt_is_pass", receipt_pass, {"receipt": runtime_receipt_rel, "error": receipt_err, "receipt_data": runtime_receipt_data})
            if not receipt_pass:
                errors.append("runtime FPS lock receipt is not PASS")

            if isinstance(runtime_receipt_data, dict):
                payload = runtime_receipt_data.get("payload", {})
                avg = payload.get("average_fps") if isinstance(payload, dict) else None
                sample_count = payload.get("sample_count") if isinstance(payload, dict) else None
                slow_ratio = payload.get("slow_frame_ratio") if isinstance(payload, dict) else None
                metrics_ok = isinstance(avg, (int, float)) and avg >= 59.5 and isinstance(sample_count, int) and sample_count >= 180 and isinstance(slow_ratio, (int, float)) and slow_ratio <= 0.05
                add(checks, "runtime_fps_metrics_meet_strict_gate", metrics_ok, {"average_fps": avg, "sample_count": sample_count, "slow_frame_ratio": slow_ratio})
                if not metrics_ok and "runtime FPS lock receipt is not PASS" not in errors:
                    errors.append("runtime FPS metrics do not meet strict gate")

    verdict = "PASS_IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF_READY" if not errors else "FAIL_IMPERIUM_APP_TAURI_RUNTIME_WINDOW_FPS_PROOF"
    generated = utc()

    summary = {
        "summary_id": "astronomicon.imperium_app_tauri_runtime_window_fps_proof_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "checks": checks,
        "command_results": command_results,
        "runtime_receipt": runtime_receipt_rel,
        "runtime_receipt_data": runtime_receipt_data,
        "errors": errors,
        "warnings": warnings,
        "proof_level": "RUNTIME_WINDOW_AND_WEBVIEW_FPS_LOCK" if verdict.startswith("PASS") else "BLOCKED",
        "next_stage": "IMPERIUM-APP-TAURI-EYES-ROOM-FOUNDATION-0001",
        "not_claimed": matrix.get("not_claimed", []) if isinstance(matrix, dict) else [],
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_app_tauri_runtime_window_fps_proof.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Tauri runtime proof: tauri:dev window opened long enough for WebView requestAnimationFrame FPS lock receipt."
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    commands_md = "\n".join(
        f"- `{'PASS' if 'runtime_fps_proof' in str(r.get('stdout_tail','')) or runtime_receipt_rel else 'RUN'}` — `{' '.join(r.get('command', []))}` exit=`{r.get('exit_code')}`"
        for r in command_results
    ) or "- none"

    (repo / REPORT).write_text(f"""# IMPERIUM APP TAURI RUNTIME WINDOW FPS PROOF REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

This is the first local runtime proof for the Tauri application.

It opens the Tauri dev window, lets the WebView measure `requestAnimationFrame` frame cadence, writes an app-side FPS receipt through the Rust bridge, then closes the process tree.

## Commands

{commands_md}

## Runtime receipt

```text
{runtime_receipt_rel or "none"}
```

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
        "runtime_receipt": runtime_receipt_rel,
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
