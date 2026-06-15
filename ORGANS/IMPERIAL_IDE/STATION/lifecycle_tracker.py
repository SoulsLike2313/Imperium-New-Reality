from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGES = [
    "INTENT_CAPTURED",
    "CLASSIFIED",
    "ROUTE_PREVIEWED",
    "POLICY_CHECKED",
    "TASKPACK_BUILT",
    "TASKPACK_VALIDATED",
    "DRY_RUN_REGISTERED",
    "LIVE_REGISTERED",
    "LAUNCH_CARD_READY",
    "HANDOFF_READY",
    "EXECUTION_STARTED",
    "REPORT_DETECTED",
    "VALIDATION_DETECTED",
    "BUNDLE_GATE_CHECKED",
    "GIT_CLOSURE_CHECKED",
    "CLOSED_OR_BLOCKED",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_lifecycle(task_id: str) -> dict[str, Any]:
    return {
        "schema_version": "imperial_ide.lifecycle_state.v0_2",
        "task_id": task_id,
        "overall_state": "DRY_RUN",
        "stages": [
            {
                "stage": name,
                "state": "BLOCKED" if name == "EXECUTION_STARTED" else "UNKNOWN",
                "detail": "",
                "updated_at_utc": utc_now(),
            }
            for name in STAGES
        ],
        "execution_complete": False,
        "handoff_ready": False,
    }


def set_stage(state: dict[str, Any], stage: str, value: str, detail: str = "") -> None:
    if stage not in STAGES:
        raise ValueError(f"unknown lifecycle stage: {stage}")
    record = next(item for item in state["stages"] if item["stage"] == stage)
    record.update({"state": value, "detail": detail, "updated_at_utc": utc_now()})
    if stage == "HANDOFF_READY" and value in {"ACTIVE", "LIVE", "DRY_RUN"}:
        state["handoff_ready"] = True
    if stage == "EXECUTION_STARTED" and value in {"ACTIVE", "LIVE"}:
        state["execution_complete"] = True


def write_state(path: Path, state: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()


def smoke() -> dict[str, Any]:
    state = new_lifecycle("TASK-NEWREALITY-STATION-LIFECYCLE-SMOKE-PC-V0_1")
    set_stage(state, "INTENT_CAPTURED", "ACTIVE", "smoke intent")
    set_stage(state, "HANDOFF_READY", "DRY_RUN", "copy-ready Servitor Prime handoff")
    set_stage(state, "DRY_RUN_REGISTERED", "DRY_RUN", "dry-run registration state is separate")
    set_stage(state, "LIVE_REGISTERED", "BLOCKED", "live registration was not run")
    set_stage(state, "EXECUTION_STARTED", "BLOCKED", "real servitor execution remains gated")
    return {
        "status": "PASS_WITH_WARNINGS",
        "stage_count": len(state["stages"]),
        "required_stage_count": len(STAGES),
        "handoff_ready": state["handoff_ready"],
        "execution_complete": state["execution_complete"],
        "execution_started_state": next(
            item["state"] for item in state["stages"] if item["stage"] == "EXECUTION_STARTED"
        ),
    }
