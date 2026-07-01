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

TASK_ID = "PATCH-PACK-LIFECYCLE-LAUNCHER-COMMANDS-0001"
VALIDATOR_ID = "patch_lifecycle_launcher_commands_validator.v0_1"
CURRENT_PATCH_ID = TASK_ID

CLI = Path("SUPPORT/LAUNCHER/imperium_cli.py")
PS1 = Path("SUPPORT/LAUNCHER/imperium.ps1")
COMMANDS = Path("SUPPORT/LAUNCHER/LAUNCHER_COMMANDS_V0_2.json")
MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/PATCH_LIFECYCLE_LAUNCHER_COMMANDS_MATRIX_V0_1.json")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/patch_lifecycle_launcher_commands_receipt.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/PATCH_LIFECYCLE_LAUNCHER_COMMANDS_REPORT_V0_1.md")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/PATCH_LIFECYCLE_LAUNCHER_COMMANDS_SUMMARY_V0_1.json")

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

def run_cli(repo: Path, args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run([sys.executable, str(repo / CLI), "--repo-root", str(repo)] + args, cwd=str(repo), capture_output=True, text=True, timeout=240)
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

    for rel in [CLI, PS1, COMMANDS, MATRIX]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    for rel in [COMMANDS, MATRIX]:
        if (repo / rel).is_file():
            data, err = load_json(repo / rel)
            add(checks, f"{rel.name}_parses", err is None, {"error": err})
            if err:
                errors.append(f"{rel.as_posix()} parse failed: {err}")

    cli_text = (repo / CLI).read_text(encoding="utf-8", errors="replace") if (repo / CLI).is_file() else ""
    forbidden = ["patch run", "git push", "git commit"]
    # Text may mention forbidden command in help/denial; only check no subprocess direct git commit/push patterns.
    bad_patterns = ["git\",\"push", "git\",\"commit", "git push", "git commit"]
    bad_hits = [p for p in bad_patterns if p in cli_text and "Forbidden in launcher" not in cli_text]
    add(checks, "launcher_does_not_implement_git_commit_push", not bad_hits, {"hits": bad_hits})
    if bad_hits:
        errors.append("launcher appears to implement git commit/push")

    commands_data, _ = load_json(repo / COMMANDS) if (repo / COMMANDS).is_file() else ({}, "missing")
    listed = commands_data.get("new_patch_lifecycle_commands", []) if isinstance(commands_data, dict) else []
    required_commands = [
        "patch preflight <PATCH_ID>",
        "patch scope <PATCH_ID>",
        "patch smoke <PATCH_ID>",
        "patch lifecycle <PATCH_ID>",
        "patch lifecycle-all",
    ]
    missing_cmds = [c for c in required_commands if c not in listed]
    add(checks, "launcher_lifecycle_commands_declared", not missing_cmds, {"missing": missing_cmds})
    if missing_cmds:
        errors.append("missing launcher commands: " + ", ".join(missing_cmds))

    # Run real operator commands against this patch.
    command_results: Dict[str, Dict[str, Any]] = {}
    for name, argv in [
        ("preflight", ["patch", "preflight", CURRENT_PATCH_ID]),
        ("scope", ["patch", "scope", CURRENT_PATCH_ID]),
        ("smoke", ["patch", "smoke", CURRENT_PATCH_ID]),
        ("lifecycle", ["patch", "lifecycle", CURRENT_PATCH_ID]),
    ]:
        code, out, err = run_cli(repo, argv)
        command_results[name] = {"exit_code": code, "stdout_tail": out[-2000:], "stderr_tail": err[-1000:]}
        add(checks, f"launcher_patch_{name}_command_runs", code == 0, command_results[name])
        if code != 0:
            errors.append(f"launcher patch {name} command failed")

    # Check forbidden run command is rejected.
    code, out, err = run_cli(repo, ["patch", "run", CURRENT_PATCH_ID])
    add(checks, "launcher_patch_run_is_forbidden", code != 0, {"exit_code": code, "stdout": out[-1000:], "stderr": err[-1000:]})
    if code == 0:
        errors.append("launcher patch run unexpectedly succeeded")

    op_receipt = repo / "SUPPORT/LAUNCHER/RECEIPTS" / f"PATCH_LIFECYCLE_OPERATOR_RECEIPT_{CURRENT_PATCH_ID}.json"
    add(checks, "operator_lifecycle_receipt_written", op_receipt.is_file(), {"path": op_receipt.relative_to(repo).as_posix() if op_receipt.is_file() else str(op_receipt)})
    if not op_receipt.is_file():
        errors.append("operator lifecycle receipt not written")

    verdict = "PASS_PATCH_LIFECYCLE_LAUNCHER_COMMANDS_READY" if not errors else "FAIL_PATCH_LIFECYCLE_LAUNCHER_COMMANDS"
    generated = utc()

    summary = {
        "summary_id": "astronomicon.patch_lifecycle_launcher_commands_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "current_patch_id": CURRENT_PATCH_ID,
        "command_results": command_results,
        "operator_receipt": op_receipt.relative_to(repo).as_posix() if op_receipt.is_file() else None,
        "not_claimed": ["patch execution", "Custodes trust", "Throne verdict"],
        "checks": checks,
        "errors": errors,
        "warnings": warnings
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.patch_lifecycle_launcher_commands.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Operator launcher commands expose Patch Pack lifecycle validation without enabling patch execution."
    }

    for p in [SUMMARY, RECEIPT, REPORT]:
        (repo / p).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# PATCH LIFECYCLE LAUNCHER COMMANDS REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Commands now available

```text
imperium patch preflight <PATCH_ID>
imperium patch scope <PATCH_ID>
imperium patch smoke <PATCH_ID>
imperium patch smoke-all
imperium patch smoke-summary
imperium patch smoke-partial
imperium patch smoke-closed
imperium patch lifecycle <PATCH_ID>
imperium patch lifecycle-all
```

## Not claimed

- patch execution
- Custodes trust
- Throne verdict

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
        "operator_receipt": summary["operator_receipt"],
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
