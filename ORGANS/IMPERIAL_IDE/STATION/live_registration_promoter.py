from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from safety_center import safety_summary
from taskpack_manager import inspect_taskpack
from dirty_classifier import classify_dirty


CONFIRMATION_TOKEN = "LIVE"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return default


def promotion_state(repo_root: Path, taskpack_id: str = "", confirmation_token: str = "") -> dict[str, Any]:
    repo = repo_root.resolve()
    candidate = inspect_taskpack(repo, taskpack_id)
    current_expected_path = repo / "ORGANS" / "ASTRONOMICON" / "TASK_REGISTRY" / "current_expected_task.json"
    current_expected = _read_json(current_expected_path, {})
    safety = safety_summary(repo)
    dirty = classify_dirty(repo)
    blockers: list[str] = []
    if candidate.get("status") == "BLOCKED":
        blockers.append("generated taskpack is not available or valid")
    if safety.get("result") == "BLOCKED":
        blockers.append("safety center blocks promotion")
    if not candidate.get("taskpack_zip_path"):
        blockers.append("candidate ZIP path is missing")

    confirmed = confirmation_token == CONFIRMATION_TOKEN
    canon_task_id = str(current_expected.get("task_id", ""))
    candidate_task_id = str(candidate.get("taskpack_id", ""))
    base = {
        "task_id": candidate.get("taskpack_id", ""),
        "dry_run_default": True,
        "promotion_screen_available": True,
        "explicit_owner_confirmation_required": True,
        "confirmation_token_required": CONFIRMATION_TOKEN,
        "confirmation_received": confirmed,
        "candidate_state": "CANDIDATE_GENERATED_TASKPACK",
        "canon_state": "CURRENT_EXPECTED_TASK",
        "candidate_versus_canon_state": {
            "candidate_task_id": candidate_task_id,
            "canon_current_expected_task_id": canon_task_id,
            "same_task": candidate_task_id == canon_task_id,
        },
        "current_candidate_task": candidate,
        "current_expected_task": current_expected,
        "current_expected_task_impact_visible": True,
        "will_change": {
            "current_expected_task_path": current_expected_path.relative_to(repo).as_posix(),
            "new_expected_task_id": candidate.get("taskpack_id", ""),
            "scope": "LOCAL_PC_ONLY",
        },
        "safety_checks": safety,
        "dirty_state_checks": {
            "status": dirty.get("status"),
            "dirty_count": dirty.get("dirty_count"),
            "unclassified_count": dirty.get("unclassified_count"),
            "secrets_detected": dirty.get("secrets_detected"),
            "push_allowed_state": dirty.get("push_allowed_state"),
        },
        "scope_checks": {
            "remote_contours": "OUT_OF_SCOPE",
            "real_servitor_execution": "NOT_REQUIRED",
            "live_llm_backend": "NOT_REQUIRED",
        },
        "automatic_live_promotion_run": False,
        "blockers": blockers,
        "timestamp": utc_now(),
    }

    if blockers:
        return {**base, "status": "BLOCKED", "promotion_state": "REVIEW_BLOCKED", "result": "REVIEW_BLOCKED"}
    if not confirmed:
        return {
            **base,
            "status": "PASS_WITH_WARNINGS",
            "promotion_state": "REVIEW_AVAILABLE",
            "confirmation_state": "CONFIRMATION_REQUIRED",
            "result": "LIVE_NOT_RUN",
        }

    skill = (
        repo
        / "ORGANS"
        / "ASTRONOMICON"
        / "SKILLS"
        / "TASKPACK_REGISTRATION_SKILL"
        / "astronomicon_taskpack_registration_skill_v0_1.py"
    )
    if not skill.is_file():
        return {
            **base,
            "status": "BLOCKED",
            "promotion_state": "LIVE_FAILED",
            "result": "LIVE_FAILED",
            "blockers": ["Astronomicon registration skill not found"],
        }
    completed = subprocess.run(
        [
            sys.executable,
            str(skill),
            "--repo-root",
            str(repo),
            "--zip-path",
            str(repo / candidate["taskpack_zip_path"]),
            "--contour",
            "PC",
            "--print-launch-card",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    ok = completed.returncode == 0
    return {
        **base,
        "status": "PASS_WITH_WARNINGS" if ok else "BLOCKED",
        "promotion_state": "LIVE_REGISTERED" if ok else "LIVE_FAILED",
        "result": "LIVE_REGISTERED" if ok else "LIVE_FAILED",
        "automatic_live_promotion_run": False,
        "explicit_live_promotion_run": True,
        "exit_code": completed.returncode,
        "stdout": completed.stdout[-6000:],
        "stderr": completed.stderr[-2000:],
        "blockers": [] if ok else ["Astronomicon registration skill returned non-zero"],
    }
