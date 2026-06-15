from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dirty_classifier import classify_dirty


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return default


def safety_summary(repo_root: Path) -> dict[str, Any]:
    repo = repo_root.resolve()
    policy = _read_json(repo / "ORGANS" / "MECHANICUS" / "REGISTRY" / "command_policy.json", {})
    dirty = classify_dirty(repo)
    arbitrary_shell = bool(policy.get("arbitrary_shell_execution_allowed", False))
    result = "PASS_WITH_WARNINGS"
    if dirty.get("secrets_detected") or dirty.get("staged_blockers") or arbitrary_shell:
        result = "BLOCKED"
    return {
        "status": result,
        "real_servitor_execution": {
            "allowed_now": False,
            "reason": "No owner-approved real execution gate is open.",
            "future_gate": "Dedicated real servitor execution task with receipts.",
        },
        "live_llm_backend": {
            "allowed_now": False,
            "reason": "No live LLM secrets/backend gate is open.",
            "future_gate": "Dedicated LLM backend task with secret policy.",
        },
        "unsafe_shell": {
            "allowed_now": False,
            "reason": "Mechanicus policy keeps unknown and unsafe commands blocked.",
        },
        "arbitrary_shell": {
            "allowed_now": arbitrary_shell,
            "reason": "Must remain false for this task.",
        },
        "dry_run_default": bool(policy.get("dry_run_required_by_default", True)),
        "live_registration": {
            "allowed_now": True,
            "scope": "LOCAL_PC_VALIDATED_GENERATED_TASKPACK_ONLY",
            "confirmation_required": True,
        },
        "live_registration_scope": "LOCAL_PC_VALIDATED_GENERATED_TASKPACK_ONLY",
        "push_gate": dirty.get("push_allowed_state"),
        "dirty_state": {
            "dirty_count": dirty.get("dirty_count", 0),
            "push_allowed_state": dirty.get("push_allowed_state"),
            "recommended_action": dirty.get("recommended_action"),
        },
        "secrets_state": {
            "secrets_detected": dirty.get("secrets_detected", False),
            "secret_items": dirty.get("secret_items", []),
        },
        "runtime_state": {
            "runtime_artifacts_detected": dirty.get("runtime_artifacts_detected", False),
            "runtime_items": dirty.get("runtime_items", []),
        },
        "remote_contours": {
            "VM2": "DISABLED_OUT_OF_SCOPE",
            "VM3": "DISABLED_OUT_OF_SCOPE",
        },
        "destructive_cleanup": {
            "allowed_now": False,
            "reason": "Deletion/quarantine requires owner-approved batch plan.",
        },
        "real_servitor_execution_enabled": False,
        "live_llm_backend_enabled": False,
        "unsafe_shell_available": False,
        "arbitrary_shell_allowed": arbitrary_shell,
        "remote_contours_enabled": False,
        "destructive_cleanup_enabled": False,
        "push_gate_state": dirty.get("push_allowed_state"),
        "result": result,
    }
