from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

KNOWN_FRESH_ZIP = (
    "REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-USABILITY-STATION-AGENTIC-WORKFLOW-PC-V0_2/"
    "agent_registry_receipt.zip"
)
KNOWN_OLDER_ZIP = (
    "REPORTS/TASK-NEWREALITY-MECHANICUS-IMPERIAL-IDE-CONTROL-SHELL-TUI-PC-V0_1/"
    "astronomicon_dashboard_integration_receipt.zip"
)

SECRET_RE = re.compile(r"(?i)(^|/)(\.env|.*credential.*|.*secret.*|.*token.*|.*private[_-]?key.*)$")
LOCAL_CONFIG_RE = re.compile(r"(?i)(^|/)(\.vscode/|\.idea/|.*local.*config.*|.*machine.*config.*)")
RUNTIME_PREFIXES = (
    "ORGANS/IMPERIAL_IDE/STATION/receipts/runtime/",
    "ORGANS/IMPERIAL_IDE/STATION/generated_taskpacks/",
    "ORGANS/IMPERIAL_IDE/WARP/RUNTIME/",
    "ORGANS/IMPERIAL_IDE/OPS/STAGING/",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.rstrip("\r\n")


def _current_task_id(repo_root: Path) -> str:
    path = repo_root / "ORGANS" / "ASTRONOMICON" / "TASK_REGISTRY" / "current_expected_task.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return ""
    return str(data.get("task_id", ""))


def _parse_porcelain(line: str) -> dict[str, Any]:
    status = line[:2]
    path = line[3:].replace("\\", "/")
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return {
        "raw": line,
        "status": status,
        "path": path,
        "is_staged": status[0] not in {" ", "?"},
        "is_untracked": status == "??",
    }


def _classify_path(path: str, status: str, task_id: str) -> dict[str, Any]:
    current_report_prefix = f"REPORTS/{task_id}/" if task_id else ""
    current_taskpack_prefix = f"ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/{task_id}/" if task_id else ""
    stage_allowed = False
    push_blocking = False
    category = "UNKNOWN_REVIEW_REQUIRED"
    recommendation = "Review manually before staging or pushing."

    if SECRET_RE.search(path):
        category = "SECRET_RISK"
        push_blocking = True
        recommendation = "Do not stage or push. Move through secret handling policy."
    elif LOCAL_CONFIG_RE.search(path):
        category = "LOCAL_CONFIG"
        push_blocking = True
        recommendation = "Do not stage local machine config."
    elif path.startswith(RUNTIME_PREFIXES):
        category = "GENERATED_TASKPACK_RUNTIME" if "generated_taskpacks" in path else "RUNTIME_ARTIFACT"
        recommendation = "Leave unstaged unless a task explicitly promotes this runtime artifact."
    elif path == KNOWN_FRESH_ZIP:
        category = "FRESH_TASK_OUTPUT_CANDIDATE"
        recommendation = "Known prior-task report ZIP. Keep unstaged for this task or close in its source task."
    elif path == KNOWN_OLDER_ZIP:
        category = "OLD_UNRELATED_ARTIFACT"
        recommendation = "Known older unrelated report ZIP. Keep unstaged; quarantine only with owner approval."
    elif current_report_prefix and path.startswith(current_report_prefix):
        category = "CANONICAL_REPORT_ARTIFACT"
        stage_allowed = True
        recommendation = "Stage after validation with the current task outputs."
    elif current_taskpack_prefix and path.startswith(current_taskpack_prefix):
        category = "STAGE_CANDIDATE"
        stage_allowed = True
        recommendation = "Stage as current Astronomicon task admission evidence."
    elif path in {
        "ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json",
        "ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json",
    }:
        category = "STAGE_CANDIDATE"
        stage_allowed = True
        recommendation = "Stage as current Astronomicon registry update."
    elif path.startswith("ORGANS/IMPERIAL_IDE/"):
        category = "STAGE_CANDIDATE"
        stage_allowed = True
        recommendation = "Stage after Python/JSON validation."
    elif path.startswith("ORGANS/MECHANICUS/") or path.startswith("ORGANS/ADMINISTRATUM/"):
        category = "STAGE_CANDIDATE"
        stage_allowed = True
        recommendation = "Stage only if task validation names this path."
    elif path.endswith(".zip") and path.startswith("REPORTS/"):
        category = "QUARANTINE_CANDIDATE"
        recommendation = "Do not stage in this task; owner-approved cleanup can quarantine later."
    elif status.strip():
        category = "UNKNOWN_REVIEW_REQUIRED"
        push_blocking = True

    return {
        "category": category,
        "stage_allowed": stage_allowed,
        "push_blocking": push_blocking,
        "recommended_action": recommendation,
    }


def classify_dirty(repo_root: Path) -> dict[str, Any]:
    repo = repo_root.resolve()
    task_id = _current_task_id(repo)
    porcelain = _git(repo, "status", "--porcelain=v1", "-uall")
    lines = [line for line in porcelain.splitlines() if line.strip()]
    items = []
    for line in lines:
        parsed = _parse_porcelain(line)
        classification = _classify_path(parsed["path"], parsed["status"], task_id)
        items.append({**parsed, **classification})

    secret_items = [item for item in items if item["category"] == "SECRET_RISK"]
    runtime_items = [item for item in items if item["category"] in {"RUNTIME_ARTIFACT", "GENERATED_TASKPACK_RUNTIME"}]
    unknown_items = [item for item in items if item["category"] == "UNKNOWN_REVIEW_REQUIRED"]
    staged_blockers = [
        item for item in items
        if item["is_staged"] and (item["push_blocking"] or not item["stage_allowed"])
    ]
    stage_candidates = [item for item in items if item["stage_allowed"]]
    quarantine_candidates = [
        item for item in items
        if item["category"] in {"QUARANTINE_CANDIDATE", "OLD_UNRELATED_ARTIFACT"}
    ]
    if secret_items or staged_blockers or unknown_items:
        push_allowed_state = "BLOCKED_BY_DIRTY_CLASSIFICATION"
    elif items:
        push_allowed_state = "ALLOWED_AFTER_STAGING_VALIDATED_IN_SCOPE_ONLY_WITH_WARNINGS"
    else:
        push_allowed_state = "ALLOWED_CLEAN"

    return {
        "status": "PASS_WITH_WARNINGS" if push_allowed_state != "BLOCKED_BY_DIRTY_CLASSIFICATION" else "BLOCKED",
        "task_id": task_id,
        "dirty_count": len(items),
        "classified_items": items,
        "known_zip_1_classification": next((item for item in items if item["path"] == KNOWN_FRESH_ZIP), None),
        "known_zip_2_classification": next((item for item in items if item["path"] == KNOWN_OLDER_ZIP), None),
        "secrets_detected": bool(secret_items),
        "secret_items": secret_items,
        "runtime_artifacts_detected": bool(runtime_items),
        "runtime_items": runtime_items,
        "stage_candidates": stage_candidates,
        "quarantine_candidates": quarantine_candidates,
        "unknown_items": unknown_items,
        "staged_blockers": staged_blockers,
        "push_allowed_state": push_allowed_state,
        "recommended_action": (
            "Stage only validated in-scope task outputs; keep known unrelated ZIPs unstaged; do not delete files."
            if items else
            "Repository has no dirty paths."
        ),
        "timestamp": utc_now(),
    }
