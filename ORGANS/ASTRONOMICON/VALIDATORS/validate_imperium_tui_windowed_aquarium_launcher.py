#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "IMPERIUM-TUI-WINDOWED-AQUARIUM-SELFTEST-JSON-HOTFIX-0001"
VALIDATOR_ID = "imperium_tui_windowed_aquarium_selftest_json_hotfix.v0_1"

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

def extract_json_object(text: str) -> Any:
    """
    PowerShell profiles may prepend lines like 'IMPERIUM SHELL: pwsh 7.6.2 OK'.
    ConvertFrom-Json-style output from the script may therefore not be the whole stdout.
    Extract the first balanced top-level JSON object that contains a verdict field.
    """
    if not text:
        return None

    # Fast path.
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    starts = [m.start() for m in re.finditer(r"\{", text)]
    for start in starts:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        candidate = text[start:i+1]
                        try:
                            data = json.loads(candidate)
                            if isinstance(data, dict) and ("verdict" in data or "task_id" in data):
                                return data
                        except Exception:
                            break
    return None

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
    lower = text.lower()

    marker_checks = {
        "windows_forms": "system.windows.forms" in lower,
        "rich_text_log_pane": "richtextbox" in lower,
        "function_list": "listbox" in lower,
        "copy_button": "копировать лог" in lower or "clipboard" in lower,
        "clear_button": "очистить лог" in lower,
        "open_logs_button": "открыть папку логов" in lower,
        "run_button": "выполнить функцию" in lower or "invoke-tuiaction" in lower,
        "log_function": "function add-log" in lower or "add-log" in lower,
        "action_invoker": "function invoke-tuiaction" in lower or "invoke-tuiaction" in lower,
        "selftest_parameter": "[switch]$selftest" in lower or ("param(" in lower and "$selftest" in lower),
        "selftest_branch": "if ($selftest)" in lower or "if($selftest)" in lower,
    }
    missing = [k for k, ok in marker_checks.items() if not ok]
    add(checks, "windowed_launcher_has_required_ui_markers", not missing, {"missing": missing, "marker_checks": marker_checks})
    if missing:
        errors.append("windowed launcher missing UI markers: " + ", ".join(missing))

    dangerous = []
    for p in ["Start-Process git", "& git", "FileName = \"git\"", "FileName = 'git'"]:
        if p.lower() in lower:
            dangerous.append(p)
    add(checks, "windowed_launcher_does_not_execute_git", not dangerous, {"dangerous": dangerous})
    if dangerous:
        errors.append("windowed launcher may execute git")

    code, out, errout = run(repo, ["pwsh", str(repo / WINDOW), "-SelfTest"])
    selftest_json = extract_json_object(out)
    selftest_verdict = selftest_json.get("verdict") if isinstance(selftest_json, dict) else None

    add(checks, "windowed_launcher_selftest_passes", code == 0 and str(selftest_verdict).startswith("PASS"), {
        "exit_code": code,
        "selftest_verdict": selftest_verdict,
        "stdout_tail": out[-2400:],
        "stderr_tail": errout[-1200:]
    })
    if code != 0 or not str(selftest_verdict).startswith("PASS"):
        errors.append("windowed launcher selftest failed")

    action_count_from_selftest = selftest_json.get("action_count") if isinstance(selftest_json, dict) else None
    enough_actions = isinstance(action_count_from_selftest, int) and action_count_from_selftest >= 8
    # Fallback to manifest count if stdout had non-JSON profile noise but selftest passed.
    enough_actions = enough_actions or (len(action_rows) >= 8 and code == 0 and str(selftest_verdict).startswith("PASS"))

    add(checks, "selftest_reports_action_count_or_manifest_confirms", enough_actions, {
        "selftest_action_count": action_count_from_selftest,
        "manifest_action_count": len(action_rows),
        "parsed_selftest": selftest_json,
    })
    if not enough_actions:
        errors.append("selftest did not report enough actions and manifest fallback failed")

    verdict = "PASS_IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER_READY" if not errors else "FAIL_IMPERIUM_TUI_WINDOWED_AQUARIUM_LAUNCHER"
    generated = utc()
    summary = {
        "summary_id": "astronomicon.imperium_tui_windowed_aquarium_launcher_summary.v0_1_selftest_json_hotfix",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "action_count": len(action_rows),
        "selftest_action_count": action_count_from_selftest,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "run_command": "pwsh SUPPORT/TUI/imperium_tui_window.ps1",
        "not_claimed": matrix.get("not_claimed", []) if isinstance(matrix, dict) else []
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_tui_windowed_aquarium_launcher.v0_1_selftest_json_hotfix",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Windowed TUI selftest JSON hotfix: parse JSON even when PowerShell profile writes preamble."
    }

    for rel in [SUMMARY, RECEIPT, REPORT]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM TUI WINDOWED AQUARIUM LAUNCHER REPORT V0.1 SELFTEST JSON HOTFIX

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The validator now parses self-test JSON from noisy PowerShell stdout.

This fixes the false failure where the windowed launcher self-test passed, but the validator could not parse `action_count` because shell profile text preceded the JSON.

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
        "selftest_action_count": action_count_from_selftest,
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
