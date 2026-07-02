#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "IMPERIUM-TUI-WINDOWED-AQUARIUM-LAUNCHER-0001"
VALIDATOR_ID = "imperium_tui_windowed_aquarium_launcher_validator.v0_1"

WINDOW = Path("SUPPORT/TUI/imperium_tui_window.ps1")
ACTIONS = Path("SUPPORT/TUI/IMPERIUM_TUI_ACTIONS_V0_1.json")
MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_MATRIX_V0_1.json")
README = Path("SUPPORT/TUI/README_IMPERIUM_TUI_WINDOWED_AQUARIUM_V0_1.md")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_tui_windowed_aquarium_launcher_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_REPORT_V0_1.md")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def run(repo: Path, cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=180, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    for rel in [WINDOW, ACTIONS, MATRIX, README]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    matrix, matrix_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "windowed_aquarium_matrix_parses", matrix_err is None, {"error": matrix_err})
    if matrix_err:
        errors.append("windowed aquarium matrix parse failed")
        matrix = {}

    actions, actions_err = load_json(repo / ACTIONS) if (repo / ACTIONS).is_file() else ({}, "missing")
    action_rows = actions.get("actions", []) if isinstance(actions, dict) else []
    add(checks, "actions_manifest_available", actions_err is None and len(action_rows) >= 8, {"error": actions_err, "count": len(action_rows)})
    if actions_err or len(action_rows) < 8:
        errors.append("actions manifest missing or too small")

    text = (repo / WINDOW).read_text(encoding="utf-8", errors="replace") if (repo / WINDOW).is_file() else ""
    required_markers = [
        "System.Windows.Forms",
        "RichTextBox",
        "ListBox",
        "Копировать лог",
        "Очистить лог",
        "Открыть папку логов",
        "Выполнить функцию",
        "Clipboard",
        "Add-Log",
        "Invoke-TuiAction",
        "-SelfTest"
    ]
    missing = [m for m in required_markers if m not in text]
    add(checks, "windowed_launcher_has_required_ui_markers", not missing, {"missing": missing})
    if missing:
        errors.append("windowed launcher missing UI markers")

    bad_patterns = [
        'git commit',
        'git push'
    ]
    # Allowed only as explicit hard law text in matrix/readme, not as command execution in PS1.
    dangerous = []
    for p in ["Start-Process git", "& git", "FileName = \"git\"", "FileName = 'git'"]:
        if p.lower() in text.lower():
            dangerous.append(p)
    add(checks, "windowed_launcher_does_not_execute_git", not dangerous, {"dangerous": dangerous})
    if dangerous:
        errors.append("windowed launcher may execute git")

    code, out, errout = run(repo, ["pwsh", str(repo / WINDOW), "-SelfTest"])
    add(checks, "windowed_launcher_selftest_passes", code == 0 and "PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_SELFTEST" in out, {"exit_code": code, "stdout_tail": out[-2000:], "stderr_tail": errout[-1200:]})
    if code != 0 or "PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_SELFTEST" not in out:
        errors.append("windowed launcher selftest failed")

    verdict = "PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_READY" if not errors else "FAIL_IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER"
    generated = utc()
    summary = {
        "summary_id": "astronomicon.imperium_tui_windowed_aquarium_launcher_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "action_count": len(action_rows),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "run_command": "pwsh SUPPORT/TUI/imperium_tui_window.ps1",
        "not_claimed": matrix.get("not_claimed", []) if isinstance(matrix, dict) else []
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_tui_windowed_aquarium_launcher.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Windowed terminal-launched TUI with separate aquarium log pane, Copy and Clear buttons."
    }

    for rel in [SUMMARY, RECEIPT, REPORT]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM TUI WINDOWED AQUARIUM LAUNCHER REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

This patch adds the intended operator shape:

- function list on the left;
- separate aquarium log pane on the right;
- Run button;
- Copy log button;
- Clear log button;
- Open logs folder button;
- actions still route through the validated console TUI and preserve transcripts.

## Run

```powershell
pwsh SUPPORT/TUI/imperium_tui_window.ps1
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
        "action_count": len(action_rows),
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
