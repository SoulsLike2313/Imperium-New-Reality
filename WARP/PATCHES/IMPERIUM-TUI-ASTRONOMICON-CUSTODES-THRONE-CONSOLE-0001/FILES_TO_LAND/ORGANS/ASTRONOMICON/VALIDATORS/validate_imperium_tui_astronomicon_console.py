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

TASK_ID = "IMPERIUM-TUI-ASTRONOMICON-CUSTODES-THRONE-CONSOLE-0001"
VALIDATOR_ID = "imperium_tui_astronomicon_console_validator.v0_1"

TUI = Path("SUPPORT/TUI/imperium_tui.py")
PS1 = Path("SUPPORT/TUI/imperium_tui.ps1")
ACTIONS = Path("SUPPORT/TUI/IMPERIUM_TUI_ACTIONS_V0_1.json")
README = Path("SUPPORT/TUI/README_IMPERIUM_TUI_ASTRONOMICON_V0_1.md")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/imperium_tui_astronomicon_console_receipt.json")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_TUI_ASTRONOMICON_CONSOLE_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/IMPERIUM_TUI_ASTRONOMICON_CONSOLE_REPORT_V0_1.md")

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

    for rel in [TUI, PS1, ACTIONS, README]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    actions, err = load_json(repo / ACTIONS) if (repo / ACTIONS).is_file() else ({}, "missing")
    add(checks, "tui_actions_manifest_parses", err is None, {"error": err})
    if err:
        errors.append("TUI actions manifest parse failed")
        actions = {}

    rows = actions.get("actions", []) if isinstance(actions, dict) else []
    add(checks, "tui_has_minimum_russian_actions", len(rows) >= 8, {"count": len(rows)})
    if len(rows) < 8:
        errors.append("TUI action count below threshold")

    missing_ru = [a.get("id") for a in rows if not a.get("ru_label") or not a.get("ru_description")]
    add(checks, "all_actions_have_russian_labels_and_descriptions", not missing_ru, {"missing": missing_ru})
    if missing_ru:
        errors.append("some actions are missing Russian labels/descriptions")

    missing_aquarium = [a.get("id") for a in rows if a.get("aquarium_log_required") is not True]
    add(checks, "all_actions_require_aquarium_logs", not missing_aquarium, {"missing": missing_aquarium})
    if missing_aquarium:
        errors.append("some actions do not require aquarium logs")

    forbidden_text = (repo / TUI).read_text(encoding="utf-8", errors="replace").lower() if (repo / TUI).is_file() else ""
    forbidden_hits = []
    for phrase in ["git commit", "git push"]:
        if phrase in forbidden_text and f"запрещено tui: {phrase}" not in forbidden_text:
            forbidden_hits.append(phrase)
    add(checks, "tui_does_not_implement_git_commit_push", not forbidden_hits, {"hits": forbidden_hits})
    if forbidden_hits:
        errors.append("TUI contains forbidden git operations outside explicit rejection")

    code, out, errout = run(repo, [sys.executable, str(repo / TUI), "--repo-root", str(repo), "--list-actions"])
    add(checks, "tui_list_actions_runs", code == 0, {"exit_code": code, "stdout_tail": out[-1200:], "stderr_tail": errout[-1200:]})
    if code != 0:
        errors.append("TUI list-actions failed")

    code, out, errout = run(repo, [sys.executable, str(repo / TUI), "--repo-root", str(repo), "--action", "status"])
    add(checks, "tui_status_action_runs_and_logs", code == 0 and "Лог аквариума" in out, {"exit_code": code, "stdout_tail": out[-1600:], "stderr_tail": errout[-1200:]})
    if code != 0 or "Лог аквариума" not in out:
        errors.append("TUI status action failed or did not show aquarium log")

    code, out, errout = run(repo, [sys.executable, str(repo / TUI), "--repo-root", str(repo), "--action", "throne-readout"])
    add(checks, "tui_throne_readout_runs", code == 0 and "throne_self_validation_score" in out, {"exit_code": code, "stdout_tail": out[-1600:], "stderr_tail": errout[-1200:]})
    if code != 0 or "throne_self_validation_score" not in out:
        errors.append("TUI throne readout failed")

    verdict = "PASS_IMPERIUM_TUI_ASTRONOMICON_CONSOLE_READY" if not errors else "FAIL_IMPERIUM_TUI_ASTRONOMICON_CONSOLE"
    generated = utc()
    summary = {
        "summary_id": "astronomicon.imperium_tui_console_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "action_count": len(rows),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "not_claimed": ["full IDE visual abstraction", "visual/AAA layer resumed", "Great Nine assembled", "Core v1 ready"]
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.imperium_tui_console.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Russian TUI for Astronomicon/Custodes/Throne with aquarium terminal logs."
    }

    for rel in [SUMMARY, RECEIPT, REPORT]:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM TUI ASTRONOMICON CONSOLE VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The Owner now has a Russian terminal TUI focused on Astronomicon, Custodes prosecution, and Throne Crown order.

Every callable action must show an aquarium log in the terminal and write a transcript under `SUPPORT/TUI/LOGS`.

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Not claimed

- full IDE visual abstraction
- visual/AAA layer resumed
- Great Nine assembled
- Core v1 ready
""", encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "action_count": len(rows),
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
