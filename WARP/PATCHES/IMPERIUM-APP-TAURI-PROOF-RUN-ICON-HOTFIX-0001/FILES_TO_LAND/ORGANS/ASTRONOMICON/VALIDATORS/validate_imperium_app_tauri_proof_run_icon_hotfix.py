#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-TAURI-PROOF-RUN-ICON-HOTFIX-0001"
VALIDATOR_ID = "imperium_app_tauri_proof_run_icon_hotfix_validator.v0_1"

PROOF_VALIDATOR = Path("ORGANS/ASTRONOMICON/VALIDATORS/validate_imperium_app_tauri_proof_run.py")
PROOF_RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_proof_run_receipt.json")
ICON_ICO = Path("SUPPORT/APP_TAURI/src-tauri/icons/icon.ico")
ICON_PNG = Path("SUPPORT/APP_TAURI/src-tauri/icons/icon.png")
TAURI_CONF = Path("SUPPORT/APP_TAURI/src-tauri/tauri.conf.json")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_app_tauri_proof_run_icon_hotfix_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_PROOF_RUN_ICON_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_APP_TAURI_PROOF_RUN_ICON_HOTFIX_REPORT_V0_1.md")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    ico = repo / ICON_ICO
    png = repo / ICON_PNG
    add(checks, "tauri_windows_icon_ico_exists", ico.is_file() and ico.stat().st_size > 0, {"path": ICON_ICO.as_posix(), "bytes": ico.stat().st_size if ico.is_file() else 0})
    add(checks, "tauri_icon_png_exists", png.is_file() and png.stat().st_size > 0, {"path": ICON_PNG.as_posix(), "bytes": png.stat().st_size if png.is_file() else 0})
    if not ico.is_file() or ico.stat().st_size <= 0:
        errors.append("Tauri Windows icon.ico missing")
    if not png.is_file() or png.stat().st_size <= 0:
        errors.append("Tauri icon.png missing")

    conf, conf_err = load_json(repo / TAURI_CONF)
    icons = conf.get("bundle", {}).get("icon", []) if isinstance(conf, dict) else []
    icon_conf_ok = conf_err is None and "icons/icon.ico" in icons
    add(checks, "tauri_conf_references_icon_ico", icon_conf_ok, {"error": conf_err, "icons": icons})
    if not icon_conf_ok:
        errors.append("tauri.conf.json does not reference icons/icon.ico")

    proof_ok = False
    proof_stdout = ""
    proof_stderr = ""
    proof_code = None
    if not errors:
        p = subprocess.run(
            ["python", str(repo / PROOF_VALIDATOR), "--repo-root", str(repo), "--apply"],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=1800,
            encoding="utf-8",
            errors="replace",
        )
        proof_code = p.returncode
        proof_stdout = p.stdout[-5000:]
        proof_stderr = p.stderr[-3000:]
        proof_ok = p.returncode == 0 and "PASS_IMPERIUM_APP_TAURI_PROOF_RUN_READY" in p.stdout

    add(checks, "proof_run_passes_after_icon_hotfix", proof_ok, {
        "exit_code": proof_code,
        "stdout_tail": proof_stdout,
        "stderr_tail": proof_stderr,
    })
    if not proof_ok and not errors:
        errors.append("proof run still does not pass after adding Tauri icon")

    proof_receipt, proof_err = load_json(repo / PROOF_RECEIPT) if (repo / PROOF_RECEIPT).is_file() else ({}, "missing")
    receipt_ok = proof_err is None and isinstance(proof_receipt, dict) and str(proof_receipt.get("verdict", "")).startswith("PASS")
    add(checks, "proof_receipt_is_pass_after_icon_hotfix", receipt_ok, {
        "error": proof_err,
        "verdict": proof_receipt.get("verdict") if isinstance(proof_receipt, dict) else None
    })
    if not receipt_ok and not errors:
        errors.append("proof receipt is not PASS after icon hotfix")

    verdict = "PASS_IMPERIUM_APP_TAURI_PROOF_RUN_ICON_HOTFIX_READY" if not errors else "FAIL_IMPERIUM_APP_TAURI_PROOF_RUN_ICON_HOTFIX"
    generated = utc()

    summary = {
        "summary_id": "astronomicon.imperium_app_tauri_proof_run_icon_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Adds required Tauri Windows icon resources and reruns the Tauri proof-run."
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_app_tauri_proof_run_icon_hotfix.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM APP TAURI PROOF RUN ICON HOTFIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The Tauri proof-run reached Rust/Tauri build script execution and failed because Windows resource generation required:

```text
SUPPORT/APP_TAURI/src-tauri/icons/icon.ico
```

This patch adds a minimal Imperium icon and explicitly references it in `tauri.conf.json`, then reruns the proof-run.

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
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
