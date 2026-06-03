#!/usr/bin/env python3
"""Build Task State + Evidence Binder foundation artifacts for NewGen."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-TASK-STATE-EVIDENCE-BINDER-PC-V0_1"

INPUT_PATHS_DEFAULTS = {
    "task_kernel": "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/EXAMPLES/SAMPLE_TASK_KERNEL_OBJECT_V0_1.json",
    "scope_merge": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-8-ORGAN-SCOPING-CORRIDOR-PC-V0_1/ORGAN_SCOPE_MERGE_RECORD.generated.json",
    "servitor_session": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/SERVITOR_EXECUTION_SESSION.generated.json",
    "run_record": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/RUN_RECORD_001.generated.json",
    "rerun_decision": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/RERUN_DECISION_RECORD.generated.json",
}

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate NewGen task state transition proposal and evidence replay index."
    )
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--task-kernel-path", default=INPUT_PATHS_DEFAULTS["task_kernel"])
    parser.add_argument("--scope-merge-path", default=INPUT_PATHS_DEFAULTS["scope_merge"])
    parser.add_argument("--servitor-session-path", default=INPUT_PATHS_DEFAULTS["servitor_session"])
    parser.add_argument("--run-record-path", default=INPUT_PATHS_DEFAULTS["run_record"])
    parser.add_argument("--rerun-decision-path", default=INPUT_PATHS_DEFAULTS["rerun_decision"])
    return parser.parse_args()


def read_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    if not path.exists():
        return None, "MISSING"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data, "READ"
        return None, "READ_ERROR"
    except Exception:
        return None, "READ_ERROR"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def to_posix(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.resolve().as_posix()


def resolve_out_dir(repo_root: Path, task_id: str, out_dir: str) -> Path:
    if out_dir.strip():
        return Path(out_dir).resolve()
    return (repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id).resolve()


def collect_source_records(
    repo_root: Path,
    paths: dict[str, Path],
) -> tuple[list[dict[str, str]], dict[str, dict[str, Any] | None], list[str]]:
    source_records: list[dict[str, str]] = []
    data_map: dict[str, dict[str, Any] | None] = {}
    missing_warnings: list[str] = []

    for kind, path in paths.items():
        data, status = read_json(path)
        data_map[kind] = data
        truth_level = "PROVED_FOUNDATION_INPUT"
        if status == "MISSING":
            truth_level = "MISSING_INPUT_WARN"
            missing_warnings.append(f"MISSING_INPUT_WARN:{kind}")
        elif status != "READ":
            truth_level = "MISSING_INPUT_WARN"
            missing_warnings.append(f"READ_ERROR_WARN:{kind}")
        elif kind in {"task_kernel"}:
            truth_level = "FOUNDATION_SAMPLE_INPUT"

        source_records.append(
            {
                "record_kind": kind.upper(),
                "path": to_posix(path, repo_root),
                "status": status,
                "input_truth_level": truth_level,
            }
        )

    return source_records, data_map, missing_warnings


def any_live_risk(data_map: dict[str, dict[str, Any] | None]) -> bool:
    scope = data_map.get("scope_merge")
    if isinstance(scope, dict):
        packet_sources = scope.get("packet_sources")
        if isinstance(packet_sources, list):
            for item in packet_sources:
                if isinstance(item, dict) and str(item.get("source_type")) == "LIVE_AGENT_RESPONSE":
                    return True

    task_kernel = data_map.get("task_kernel")
    if isinstance(task_kernel, dict):
        if bool(task_kernel.get("live_orchestration", False)):
            return True
        truth_status = str(task_kernel.get("truth_status", "")).upper()
        if truth_status.startswith("LIVE_"):
            return True
    return False


def derive_state_transition(
    task_binding_id: str,
    source_records: list[dict[str, str]],
    data_map: dict[str, dict[str, Any] | None],
    missing_warnings: list[str],
    evidence_index_ref: str,
) -> dict[str, Any]:
    run_data = data_map.get("run_record") or {}
    rerun_data = data_map.get("rerun_decision") or {}
    session_data = data_map.get("servitor_session") or {}

    run_status = str(run_data.get("status", ""))
    rerun_decision = str(rerun_data.get("decision", "ASK_OWNER"))
    session_status = str(session_data.get("status", "CREATED"))

    current_state = "RUNNING"
    if run_status == "BLOCKED":
        current_state = "BLOCKED_NEEDS_OWNER"
    elif run_status in {"FAILED_CLASSIFIED"}:
        current_state = "RUN_FAILED_NEEDS_RERUN"
    elif run_status in {"PASSED_WITH_EVIDENCE"}:
        current_state = "PASSED_WITH_WARNINGS"

    proposed_state = "PASSED_WITH_WARNINGS"
    if rerun_decision in {"ASK_OWNER", "BLOCKED"}:
        proposed_state = "BLOCKED_NEEDS_OWNER"
    elif rerun_decision in {"ASK_ORGAN", "RERUN_REQUIRED", "RERUN_ALLOWED"}:
        proposed_state = "RUN_FAILED_NEEDS_RERUN"
    elif rerun_decision == "PASS_STRICT":
        proposed_state = "PASSED_STRICT"

    if missing_warnings:
        proposed_state = "PASSED_WITH_WARNINGS"

    live_risk = any_live_risk(data_map)
    fake_green_risk = bool(live_risk)

    failure_classification = "FOUNDATION_LIMITATION"
    if rerun_decision == "ASK_OWNER":
        failure_classification = "OWNER_DECISION_REQUIRED"
    elif rerun_decision == "ASK_ORGAN":
        failure_classification = "SCOPE_AMBIGUITY"
    elif fake_green_risk:
        failure_classification = "FAKE_GREEN_RISK"

    owner_escalation_required = rerun_decision in {"ASK_OWNER", "BLOCKED"}
    organ_escalation_required = rerun_decision in {"ASK_ORGAN"}

    confidence = "STRONG"
    if missing_warnings:
        confidence = "PLAUSIBLE"
    if fake_green_risk:
        confidence = "FAKE_GREEN_RISK"

    limitations = [
        "FOUNDATION_ONLY",
        "NOT_PRODUCTION_EXECUTOR",
        "No live organ dialogue is claimed.",
    ]
    limitations.extend(sorted(set(missing_warnings)))

    transition_reason = (
        "State transition proposal was derived from bounded NewGen records with deterministic foundation policy."
    )
    if missing_warnings:
        transition_reason += " Missing inputs were downgraded to WARN markers instead of fabricated truth."

    return {
        "schema_version": "0.1",
        "task_id": task_binding_id,
        "source_records": source_records,
        "current_task_state": current_state if session_status else "CREATED",
        "proposed_task_state": proposed_state,
        "transition_reason": transition_reason,
        "failure_classification": failure_classification,
        "rerun_decision": rerun_decision or "ASK_OWNER",
        "owner_escalation_required": owner_escalation_required,
        "organ_escalation_required": organ_escalation_required,
        "fake_green_risk": fake_green_risk,
        "evidence_index_ref": evidence_index_ref,
        "confidence": confidence,
        "foundation_limitations": limitations,
        "created_at_utc": utc_now(),
    }


def build_evidence_index(
    task_binding_id: str,
    data_map: dict[str, dict[str, Any] | None],
    paths: dict[str, Path],
    source_records: list[dict[str, str]],
) -> dict[str, Any]:
    session = data_map.get("servitor_session") or {}
    run_data = data_map.get("run_record") or {}
    rerun_data = data_map.get("rerun_decision") or {}
    scope = data_map.get("scope_merge") or {}

    session_id = str(session.get("session_id", "SESSION-MISSING"))
    run_id = str(run_data.get("run_id", "RUN-MISSING"))
    decision_id = str(rerun_data.get("decision_id", "DECISION-MISSING"))

    organ_packet_refs: list[str] = []
    packet_sources = scope.get("packet_sources")
    if isinstance(packet_sources, list):
        for item in packet_sources:
            if isinstance(item, dict):
                ref = str(item.get("path_or_note", "")).strip()
                if ref:
                    organ_packet_refs.append(ref)
    if not organ_packet_refs:
        organ_packet_refs.append(to_posix(paths["scope_merge"], Path.cwd()))

    evidence_items: list[dict[str, str]] = []
    missing_evidence: list[str] = []

    kind_map = {
        "task_kernel": "TASK_KERNEL",
        "scope_merge": "ORGAN_SCOPE_MERGE_RECORD",
        "servitor_session": "SERVITOR_SESSION",
        "run_record": "RUN_RECORD",
        "rerun_decision": "RERUN_DECISION",
    }
    replay_order: list[str] = []
    idx = 1
    for record in source_records:
        rec_kind = str(record.get("record_kind", "UNKNOWN"))
        status = str(record.get("status", "MISSING"))
        path = str(record.get("path", ""))
        evidence_id = f"EVID-{idx:03d}-{rec_kind}"
        idx += 1
        replay_order.append(evidence_id)
        e_status = "PRESENT" if status == "READ" else "MISSING"
        evidence_items.append(
            {
                "evidence_id": evidence_id,
                "kind": kind_map.get(rec_kind.lower(), rec_kind),
                "path_or_note": path,
                "status": e_status,
            }
        )
        if e_status != "PRESENT":
            missing_evidence.append(f"{rec_kind}:{path}")

    return {
        "schema_version": "0.1",
        "task_id": task_binding_id,
        "session_id": session_id,
        "run_ids": [run_id],
        "rerun_decision_ids": [decision_id],
        "organ_packet_refs": sorted(set(organ_packet_refs)),
        "task_kernel_ref": str(paths["task_kernel"].as_posix()),
        "evidence_items": evidence_items,
        "replay_order": replay_order,
        "missing_evidence": missing_evidence,
        "truth_claims_allowed": [
            "FOUNDATION_ONLY transition proposal generation",
            "Replay index creation from bounded known records",
            "Explicit missing evidence warnings",
        ],
        "truth_claims_forbidden": [
            "production orchestration is ready",
            "live autonomous execution is proven",
            "live organ dialogue is proven",
            "full visual brain readiness is proven",
        ],
        "created_at_utc": utc_now(),
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = resolve_out_dir(repo_root, args.task_id, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    input_paths = {
        "task_kernel": (repo_root / args.task_kernel_path).resolve(),
        "scope_merge": (repo_root / args.scope_merge_path).resolve(),
        "servitor_session": (repo_root / args.servitor_session_path).resolve(),
        "run_record": (repo_root / args.run_record_path).resolve(),
        "rerun_decision": (repo_root / args.rerun_decision_path).resolve(),
    }

    source_records, data_map, missing_warnings = collect_source_records(repo_root, input_paths)
    task_binding_id = args.task_id

    evidence_index_ref = "EVIDENCE_REPLAY_INDEX.generated.json"
    transition = derive_state_transition(
        task_binding_id=task_binding_id,
        source_records=source_records,
        data_map=data_map,
        missing_warnings=missing_warnings,
        evidence_index_ref=evidence_index_ref,
    )
    evidence_index = build_evidence_index(
        task_binding_id=task_binding_id,
        data_map=data_map,
        paths=input_paths,
        source_records=source_records,
    )

    transition_path = out_dir / "TASK_STATE_TRANSITION_PROPOSAL.generated.json"
    replay_path = out_dir / "EVIDENCE_REPLAY_INDEX.generated.json"
    write_json(transition_path, transition)
    write_json(replay_path, evidence_index)

    print(transition_path.as_posix())
    print(replay_path.as_posix())
    print(f"confidence={transition['confidence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
