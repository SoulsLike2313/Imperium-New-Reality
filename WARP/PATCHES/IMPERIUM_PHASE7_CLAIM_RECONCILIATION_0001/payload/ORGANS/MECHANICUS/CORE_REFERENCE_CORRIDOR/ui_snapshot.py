"""Backend-owned snapshot contract for the Thin Imperium IDE."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import TASK_STATE_ROUTE
from .organ_ledger import GREAT_NINE, THRONE
from .real_diff import build_real_diff
from .live_ui_evidence import summarize_live_evidence


PANEL_ORDER = (
    ("new_task", "New Task"),
    ("task_state", "Task State"),
    ("great_nine_throne", "Great Nine + Throne"),
    ("owner_decisions", "Owner Decisions"),
    ("warp", "WARP"),
    ("capability_registry", "Capability Registry"),
    ("execution_trace", "Execution Trace"),
    ("evidence", "Evidence"),
    ("diff", "Diff"),
    ("checkpoints", "Checkpoints"),
    ("known_gaps", "Known Gaps"),
)


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default



def _fields(values: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "label": str(label),
            "value": json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else str(value),
            "tone": "block" if str(value).startswith(("BLOCK", "FAIL")) else "debt" if any(token in str(value) for token in ("PENDING", "DEBT", "NOT_PROVEN", "SCAFFOLD")) else "proven",
        }
        for label, value in values.items()
    ]


def _card(card_id: str, title: str, values: dict[str, Any]) -> dict[str, Any]:
    return {"id": card_id, "title": title, "fields": _fields(values)}


def _available(action_id: str, task: dict[str, Any], registry: dict[str, Any], checkpoint_count: int) -> tuple[bool, str]:
    state = task.get("current_state", "NOT_PROVEN")
    decisions = {item.get("decision") or item.get("decision_type") for item in task.get("owner_decisions", []) if isinstance(item, dict)}
    warp_state = task.get("warp", {}).get("state", "NOT_REGISTERED")
    if action_id == "refresh_state":
        return True, "Read-only backend refresh."
    if action_id == "create_test_task":
        return (not bool(task), "Only one current task is allowed.")
    if action_id == "approve_launch":
        return (state == "OWNER_LAUNCH_APPROVAL", "Owner click is recorded as the launch decision.")
    if action_id == "stop_task":
        return (bool(task) and state != "IMMUTABLE_EVIDENCE", "Owner may stop an active task.")
    if action_id == "continue_checkpoint":
        return (checkpoint_count > 0, "A semantic checkpoint is required.")
    if action_id == "accept_risk":
        return (bool(task), "Risk acceptance is recorded; it does not erase warnings.")
    if action_id == "create_exact_head_warp":
        return (state == "EXACT_HEAD_WARP" and not task.get("warp", {}).get("path"), "Requires launch approval and an absent WARP.")
    if action_id == "run_core_diagnostic":
        active = any(item.get("capability_id") == "CORE_DIAGNOSTIC" and item.get("admission_state") == "ACTIVE" for item in registry.get("capabilities", []))
        return (active and bool(task.get("warp", {}).get("path")), "Requires the ACTIVE admitted diagnostic and a WARP.")
    if action_id in {"accept_result", "reject_result", "request_rework"}:
        return (state == "OWNER_ACCEPT_OR_REJECT", "Only the Owner review state accepts this decision.")
    if action_id == "prepare_land_plan":
        return (state == "LAND_PLAN_OR_DISCARD" and "ACCEPT_RESULT" in decisions, "Preparation only; it never lands.")
    if action_id == "forbid_land":
        return (state in {"OWNER_ACCEPT_OR_REJECT", "LAND_PLAN_OR_DISCARD"}, "Owner may prohibit land at review.")
    if action_id == "discard_warp":
        return (warp_state in {"REJECTED", "FAILED_CONTAINED", "READY_FOR_REVIEW"}, "Discard requires a review/rejection state.")
    if action_id == "destroy_warp":
        return (warp_state == "DISCARDED", "Destroy requires an explicit discarded state and confirmation.")
    return False, "Unknown backend action is denied."


def build_ui_snapshot(context: Any, report_root: Path | str) -> dict[str, Any]:
    report = Path(report_root).resolve()
    task = _load(report / "TASK_STATE.json", {})
    registry = _load(report / "CAPABILITY_REGISTRY.json", {"capabilities": [], "ui_actions": [], "extension_points": []})
    organ_ledger = _load(report / "ORGAN_PARTICIPATION_LEDGER.json", {"records": [], "overall_verdict": "NOT_PROVEN"})
    claim_status = _load(report / "CURRENT_CLAIM_STATUS.json", {})
    evidence_index = _load(report / "EVIDENCE_INDEX.json", _load(report / "evidence" / "EVIDENCE_INDEX.json", {"entries": {}, "state": "NOT_PROVEN"}))
    live_evidence = summarize_live_evidence(report)
    checkpoints = _load(report / "CHECKPOINT_INDEX.json", _load(report / "checkpoints" / "CHECKPOINT_INDEX.json", {"entries": {}}))
    checkpoint_entries = checkpoints.get("entries", {})
    checkpoint_count = len(checkpoint_entries) if isinstance(checkpoint_entries, (dict, list)) else 0
    worktree = Path(context.worktree_root)
    reality = Path(context.reality_root)
    real_diff = build_real_diff(worktree, reality, str(task.get("base_head", "")))

    panels: dict[str, dict[str, Any]] = {
        panel_id: {"id": panel_id, "title": title, "status": "NOT_PROVEN", "summary": "Backend evidence is not available.", "cards": [], "actions": []}
        for panel_id, title in PANEL_ORDER
    }
    panels["new_task"].update(
        status="REGISTERED" if task else "NOT_PROVEN",
        summary="One authoritative task transaction; no UI-local task truth.",
        cards=[_card("task_identity", "Task Identity", {"task_id": task.get("task_id", "NONE"), "type": task.get("task_type", "NOT_PROVEN"), "created_by": task.get("created_by", "NOT_PROVEN")})],
    )
    panels["task_state"].update(
        status=task.get("current_state", "NOT_PROVEN"),
        summary="Persisted atomic state loaded from TASK_STATE.json.",
        cards=[_card("current_state", "Current Transaction", {"state": task.get("current_state", "NOT_PROVEN"), "version": task.get("state_version", "NOT_PROVEN"), "base_head": task.get("base_head", "NOT_PROVEN"), "strategy": task.get("selected_strategy", {}).get("strategy_id", task.get("selected_strategy", "NOT_PROVEN"))})],
    )
    latest_by_organ: dict[str, dict[str, Any]] = {}
    for item in organ_ledger.get("records", []):
        latest_by_organ[item.get("organ_id", "")] = item
    current_organs = claim_status.get("organs", {}) if isinstance(claim_status.get("organs"), dict) else {}
    organ_cards = []
    for organ_id in [*GREAT_NINE, THRONE]:
        historical = latest_by_organ.get(organ_id, {})
        current = current_organs.get(organ_id, {}) if isinstance(current_organs.get(organ_id), dict) else {}
        current_verdict = current.get("verdict", "NOT_PROVEN")
        current_confidence = current.get("confidence", 0)
        current_refs = current.get("evidence_refs", [])
        claim_state = current.get("claim_state", "HISTORICAL_NOT_PROMOTED")
        organ_cards.append(
            _card(
                organ_id.lower(),
                organ_id,
                {
                    "phase": current.get("phase", "PHASE7_CURRENT_TRUTH"),
                    "verdict": current_verdict,
                    "confidence": current_confidence,
                    "evidence_refs": current_refs,
                    "claim_state": claim_state,
                    "historical_verdict": historical.get("verdict", "NONE"),
                },
            )
        )
    organ_ring_verdict = claim_status.get("organ_ring_verdict", "NOT_PROVEN")
    panels["great_nine_throne"].update(
        status=organ_ring_verdict,
        summary=(
            "Current Phase 7 claim authority; historical ledger PASS rows are not promoted "
            "without current organ-specific evidence."
        ),
        cards=organ_cards,
    )
    panels["owner_decisions"].update(
        status="PENDING_OWNER_REVIEW" if task.get("current_state") == "OWNER_ACCEPT_OR_REJECT" else "RECORDED" if task.get("owner_decisions") else "NOT_PROVEN",
        summary="Throne advises; only Owner decisions change owner gates.",
        cards=[_card("decision_log", "Decision Log", {"count": len(task.get("owner_decisions", [])), "decisions": task.get("owner_decisions", [])})],
    )
    warp = task.get("warp", {})
    panels["warp"].update(status=warp.get("state", "NOT_PROVEN"), summary="External Git worktree lifecycle; tracked WARP archives are legacy.", cards=[_card("warp_identity", "Managed WARP", {"warp_id": warp.get("warp_id", "NOT_PROVEN"), "path": warp.get("path", "NOT_PROVEN"), "state": warp.get("state", "NOT_PROVEN"), "base_head": warp.get("base_head", task.get("base_head", "NOT_PROVEN"))})])
    capability_cards = [_card(item.get("capability_id", "unknown").lower(), item.get("capability_id", "UNKNOWN"), {"admission": item.get("admission_state", "NOT_PROVEN"), "effect": item.get("actual_effect_class", "NOT_PROVEN"), "timeout": item.get("timeout_seconds", "NOT_PROVEN"), "trust": item.get("trust_level", "NOT_PROVEN")}) for item in registry.get("capabilities", [])]
    panels["capability_registry"].update(status="DEFAULT_DENY_ACTIVE" if registry.get("default_policy") == "DENY" else "BLOCK", summary="CLI and Tauri consume this exact registry digest.", cards=capability_cards)
    evidence_entries = evidence_index.get("entries", {})
    evidence_count = len(evidence_entries) if isinstance(evidence_entries, (dict, list)) else 0
    live_count = int(live_evidence.get("count", 0))
    total_event_count = evidence_count + live_count
    live_blocked = str(live_evidence.get("verdict", "")).startswith("BLOCK")
    panels["execution_trace"].update(
        status="BLOCK" if live_blocked else "PROVEN" if total_event_count else "NOT_PROVEN",
        summary="Exact argv and process outcomes come from the sealed base index plus append-only canonical live UI evidence.",
        cards=[
            _card(
                "trace_summary",
                "Trace Summary",
                {
                    "events": total_event_count,
                    "base_events": evidence_count,
                    "live_ui_count": live_count,
                    "index_state": evidence_index.get("state", "NOT_PROVEN"),
                    "live_index_state": live_evidence.get("state", "ABSENT"),
                    "latest_ui_request": live_evidence.get("latest_action_request_id") or "NONE",
                    "latest_ui_event": live_evidence.get("latest_event_id") or "NONE",
                    "live_error": live_evidence.get("error") or "NONE",
                },
            )
        ],
    )
    panels["evidence"].update(
        status="BLOCK" if live_blocked else evidence_index.get("state", "NOT_PROVEN"),
        summary="The finalized base index remains immutable; live UI diagnostics use a separate canonical EvidenceStore index.",
        cards=[
            _card(
                "evidence_index",
                "Evidence Index",
                {
                    "count": total_event_count,
                    "base_count": evidence_count,
                    "live_ui_count": live_count,
                    "index_hash": evidence_index.get("content_sha256", "NOT_PROVEN"),
                    "live_index_hash": live_evidence.get("index_hash") or "ABSENT",
                    "latest_ui_evidence": live_evidence.get("latest_evidence_id") or "NONE",
                    "latest_ui_request": live_evidence.get("latest_action_request_id") or "NONE",
                },
            )
        ],
    )
    changed_file_rows = [
        {
            "status": item.get("status", "?"),
            "path": item.get("path", ""),
            "old_path": item.get("old_path"),
            "insertions": item.get("insertions", 0),
            "deletions": item.get("deletions", 0),
            "binary": item.get("binary", False),
        }
        for item in real_diff.get("files", [])
    ]
    panels["diff"].update(
        status=real_diff.get("verdict", "NOT_PROVEN"),
        summary="Committed base-to-result changes are measured separately from WARP and Reality dirty state.",
        cards=[
            _card(
                "git_range",
                "Committed Range",
                {
                    "base_head": real_diff.get("base_head", "NOT_PROVEN"),
                    "result_head": real_diff.get("result_head", "NOT_PROVEN"),
                    "merge_base": real_diff.get("merge_base", "NOT_PROVEN"),
                    "ahead_count": real_diff.get("ahead_count", 0),
                    "behind_count": real_diff.get("behind_count", 0),
                    "files_changed": real_diff.get("files_changed", 0),
                    "insertions": real_diff.get("insertions", 0),
                    "deletions": real_diff.get("deletions", 0),
                    "binary_files": real_diff.get("binary_files", 0),
                    "renamed_files": real_diff.get("renamed_files", 0),
                },
            ),
            _card(
                "git_changed_files",
                "Changed Files",
                {
                    "count": real_diff.get("files_changed", 0),
                    "truncated": real_diff.get("files_truncated", False),
                    "files": changed_file_rows,
                },
            ),
            _card(
                "git_patch_preview",
                "Compact Patch",
                {
                    "available": real_diff.get("patch_available", False),
                    "sha256": real_diff.get("patch_sha256", "NOT_PROVEN"),
                    "truncated": real_diff.get("patch_preview_truncated", False),
                    "preview": real_diff.get("patch_preview", ""),
                },
            ),
            _card(
                "git_boundary",
                "Working Tree Boundary",
                {
                    "worktree_dirty_count": real_diff.get("worktree_dirty_count", 0),
                    "worktree_status": real_diff.get("worktree_status", []),
                    "reality_head": real_diff.get("reality_head", "NOT_PROVEN"),
                    "reality_dirty_count": real_diff.get("reality_dirty_count", 0),
                    "reality_status": real_diff.get("reality_status", []),
                    "errors": real_diff.get("errors", []),
                },
            ),
        ],
    )
    panels["checkpoints"].update(status="PROVEN" if checkpoint_count else "NOT_PROVEN", summary="Only semantic checkpoints; partial restore remains blocked.", cards=[_card("checkpoint_index", "Checkpoint Index", {"count": checkpoint_count, "partial_restore": "NOT_IMPLEMENTED_BLOCK"})])
    gaps_path = report / "KNOWN_GAPS.md"
    gaps = [line[2:].strip() for line in gaps_path.read_text(encoding="utf-8").splitlines() if line.startswith("- ")] if gaps_path.is_file() else ["Known gaps artifact not generated yet."]
    panels["known_gaps"].update(status="WITH_DEBT" if gaps else "PROVEN", summary="No scaffold or deferred feature is shown as operational.", cards=[_card("gap_list", "Open Gaps", {"count": len(gaps), "items": gaps})])

    actions_by_panel: dict[str, list[dict[str, Any]]] = {panel_id: [] for panel_id, _ in PANEL_ORDER}
    for action in registry.get("ui_actions", []):
        enabled, reason = _available(action.get("action_id", ""), task, registry, checkpoint_count)
        rendered = {"id": action.get("action_id"), "label": action.get("label"), "enabled": enabled, "reason": reason, "confirmation": action.get("effect") in {"OWNER_DECISION", "MANAGED_WARP_DESTRUCTIVE"}, "payload_schema": action.get("payload_schema", {"type": "object"})}
        actions_by_panel.get(action.get("panel_id", ""), []).append(rendered)
    for panel_id, actions in actions_by_panel.items():
        panels[panel_id]["actions"] = actions

    return {
        "contract_id": "IMPERIUM_CORE_REFERENCE_CORRIDOR_THIN_IDE_V0_1",
        "task_id": task.get("task_id", "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "backend_truth": True,
        "ui_local_truth_allowed": False,
        "panels": [panels[panel_id] for panel_id, _ in PANEL_ORDER],
    }

