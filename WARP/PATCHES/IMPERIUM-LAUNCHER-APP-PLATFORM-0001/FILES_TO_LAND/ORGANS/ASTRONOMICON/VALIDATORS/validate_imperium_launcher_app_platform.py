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

TASK_ID = "IMPERIUM-LAUNCHER-APP-PLATFORM-0001"
VALIDATOR_ID = "imperium_launcher_app_platform_validator.v0_1"

APP = Path("SUPPORT/APP/imperium_launcher.ps1")
APP_DIRECT = Path("SUPPORT/APP/imperium_launcher_app.ps1")
CMD = Path("SUPPORT/APP/LAUNCH_IMPERIUM_APP.cmd")
MANIFEST = Path("SUPPORT/APP/IMPERIUM_LAUNCHER_APP_MANIFEST_V0_1.json")
THEME = Path("SUPPORT/APP/IMPERIUM_APP_THEME_V0_1.json")
MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/IMPERIUM_LAUNCHER_APP_PLATFORM_MATRIX_V0_1.json")
README = Path("SUPPORT/APP/README_IMPERIUM_LAUNCHER_APP_V0_1.md")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_launcher_app_platform_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_LAUNCHER_APP_PLATFORM_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_LAUNCHER_APP_PLATFORM_REPORT_V0_1.md")

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

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def run(repo: Path, cmd: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=240, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr

def extract_json_object(text: str) -> Any:
    if not text:
        return None
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

    for rel in [APP, APP_DIRECT, CMD, MANIFEST, THEME, MATRIX, README]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    manifest, manifest_err = load_json(repo / MANIFEST) if (repo / MANIFEST).is_file() else ({}, "missing")
    theme, theme_err = load_json(repo / THEME) if (repo / THEME).is_file() else ({}, "missing")
    matrix, matrix_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")

    add(checks, "app_manifest_parses", manifest_err is None, {"error": manifest_err})
    add(checks, "app_theme_parses", theme_err is None, {"error": theme_err})
    add(checks, "app_matrix_parses", matrix_err is None, {"error": matrix_err})
    if manifest_err: errors.append("app manifest parse failed")
    if theme_err: errors.append("app theme parse failed")
    if matrix_err: errors.append("app matrix parse failed")

    text = (repo / APP_DIRECT).read_text(encoding="utf-8", errors="replace") if (repo / APP_DIRECT).is_file() else ""
    required = matrix.get("required_ui_markers", []) if isinstance(matrix, dict) else []
    missing_markers = [m for m in required if m not in text]
    add(checks, "app_has_required_ui_markers", not missing_markers, {"missing": missing_markers})
    if missing_markers:
        errors.append("app missing UI markers: " + ", ".join(missing_markers))

    dangerous = []
    lower = text.lower()
    for p in ["start-process git", "& git", "filename = \"git\"", "filename = 'git'", "git commit", "git push"]:
        if p in lower:
            dangerous.append(p)
    add(checks, "app_does_not_execute_or_offer_git_land", not dangerous, {"dangerous": dangerous})
    if dangerous:
        errors.append("app contains forbidden git execution/land markers")

    code, out, err = run(repo, ["pwsh", str(repo / APP), "-SelfTest"])
    selftest = extract_json_object(out)
    selftest_verdict = selftest.get("verdict") if isinstance(selftest, dict) else None
    add(checks, "app_selftest_passes", code == 0 and str(selftest_verdict).startswith("PASS"), {
        "exit_code": code,
        "selftest_verdict": selftest_verdict,
        "stdout_tail": out[-2400:],
        "stderr_tail": err[-1200:],
    })
    if code != 0 or not str(selftest_verdict).startswith("PASS"):
        errors.append("app selftest failed")

    action_count = selftest.get("action_count") if isinstance(selftest, dict) else None
    add(checks, "app_selftest_reports_actions", isinstance(action_count, int) and action_count >= 8, {"action_count": action_count})
    if not isinstance(action_count, int) or action_count < 8:
        errors.append("app selftest action count below threshold")

    colors = theme.get("colors", {}) if isinstance(theme, dict) else {}
    color_keys = ["background", "panel", "text", "gold", "purple", "log_background", "log_text"]
    missing_colors = [k for k in color_keys if k not in colors]
    add(checks, "theme_has_imperium_color_tokens", not missing_colors, {"missing": missing_colors})
    if missing_colors:
        errors.append("theme missing Imperium color tokens")

    verdict = "PASS_IMPERIUM_LAUNCHER_APP_PLATFORM_READY" if not errors else "FAIL_IMPERIUM_LAUNCHER_APP_PLATFORM"
    generated = utc()
    summary = {
        "summary_id": "astronomicon.imperium_launcher_app_platform_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "action_count": action_count,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "run_command": "pwsh SUPPORT/APP/imperium_launcher.ps1",
        "selftest_command": "pwsh SUPPORT/APP/imperium_launcher.ps1 -SelfTest",
        "not_claimed": manifest.get("not_claimed", []) if isinstance(manifest, dict) else []
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_launcher_app_platform.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Imperium Launcher app platform validated: separate app shell, Imperium identity, aquarium logs, no hidden land."
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM LAUNCHER APP PLATFORM VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The Imperium Launcher now has a separate application-platform layer under `SUPPORT/APP`.

It is still script-first and auditable, but no longer merely a terminal menu.

## Run

```powershell
pwsh SUPPORT/APP/imperium_launcher.ps1
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
        "action_count": action_count,
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
