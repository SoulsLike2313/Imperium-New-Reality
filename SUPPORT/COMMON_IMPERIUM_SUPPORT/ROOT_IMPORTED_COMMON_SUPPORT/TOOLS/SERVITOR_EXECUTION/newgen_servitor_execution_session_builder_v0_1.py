#!/usr/bin/env python3
"""Build deterministic NewGen Servitor run/rerun foundation records.

This tool is foundation-only:
- does not execute live tasks,
- does not invoke live organ dialogue,
- does not claim production autonomy.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1"
PREV_SCOPE_TASK_ID = "TASK-20260521-NEWGEN-8-ORGAN-SCOPING-CORRIDOR-PC-V0_1"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build foundation Servitor execution session/run/rerun records."
    )
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument(
        "--out-dir",
        default="",
        help="Output directory. Defaults to report folder for the task.",
    )
    parser.add_argument(
        "--scope-merge-path",
        default="",
        help="Optional explicit path to ORGAN_SCOPE_MERGE_RECORD.generated.json",
    )
    parser.add_argument(
        "--task-kernel-path",
        default="IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/EXAMPLES/SAMPLE_TASK_KERNEL_OBJECT_V0_1.json",
    )
    parser.add_argument(
        "--formation-record-path",
        default="IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/EXAMPLES/SAMPLE_TASK_FORMATION_RECORD_V0_1.json",
    )
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


def resolve_scope_merge_path(repo_root: Path, explicit: str) -> Path:
    if explicit.strip():
        return (repo_root / explicit).resolve()
    return (
        repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "REPORTS"
        / PREV_SCOPE_TASK_ID
        / "ORGAN_SCOPE_MERGE_RECORD.generated.json"
    ).resolve()


def build_inputs(
    repo_root: Path,
    scope_path: Path,
    task_kernel_path: Path,
    formation_path: Path,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    scope_data, scope_status = read_json(scope_path)
    kernel_data, kernel_status = read_json(task_kernel_path)
    formation_data, formation_status = read_json(formation_path)

    summary = {
        "scope_data": scope_data,
        "scope_status": scope_status,
        "kernel_data": kernel_data,
        "kernel_status": kernel_status,
        "formation_data": formation_data,
        "formation_status": formation_status,
    }

    inputs = [
        {
            "kind": "organ_scope_merge_record",
            "path": to_posix(scope_path, repo_root),
            "status": scope_status,
        },
        {
            "kind": "task_kernel_object",
            "path": to_posix(task_kernel_path, repo_root),
            "status": kernel_status,
        },
        {
            "kind": "astronomicon_formation_record",
            "path": to_posix(formation_path, repo_root),
            "status": formation_status,
        },
    ]
    return inputs, summary


def derive_truth_and_status(summary: dict[str, Any]) -> tuple[str, str, list[str]]:
    warnings: list[str] = []
    scope_status = summary["scope_status"]
    kernel_status = summary["kernel_status"]
    formation_status = summary["formation_status"]

    if scope_status != "READ":
        warnings.append("MISSING_SCOPE_MERGE_RECORD_WARN")
    if kernel_status != "READ":
        warnings.append("MISSING_TASK_KERNEL_WARN")
    if formation_status != "READ":
        warnings.append("MISSING_FORMATION_RECORD_WARN")

    truth_level = "PROVED_FOUNDATION" if not warnings else "SAMPLE_OR_WARN"
    session_status = "READY_FOR_RUN"
    if warnings:
        session_status = "AUTHORITY_ACKED_WITH_WARNINGS"
    if scope_status != "READ":
        session_status = "BLOCKED_NEEDS_OWNER"
        truth_level = "BLOCKED"
    return truth_level, session_status, warnings


def extract_scope_summary(summary: dict[str, Any], scope_path: Path) -> dict[str, Any]:
    scope_data = summary["scope_data"]
    scope_status = summary["scope_status"]
    organ_count: int | None = None
    readiness = "FOUNDATION_ONLY"
    scope_warnings: list[str] = []

    if isinstance(scope_data, dict):
        packet_sources = scope_data.get("packet_sources")
        if isinstance(packet_sources, list):
            organ_count = len(packet_sources)
            for item in packet_sources:
                if isinstance(item, dict):
                    source_type = str(item.get("source_type", ""))
                    if source_type == "LIVE_AGENT_RESPONSE":
                        scope_warnings.append("LIVE_SOURCE_PRESENT_REQUIRES_RECEIPT_WARN")
                    elif source_type in {"SAMPLE_PACKET", "FOUNDATION_STUB", "STATIC_FILE"}:
                        scope_warnings.append("NOT_LIVE_AGENT")
        readiness = str(scope_data.get("readiness", "FOUNDATION_ONLY"))
    else:
        scope_warnings.append("FOUNDATION_LIMITATION")

    scope_warnings = sorted(set(scope_warnings))
    return {
        "source_path": scope_path.as_posix(),
        "source_status": scope_status,
        "organ_count": organ_count,
        "readiness": readiness,
        "warnings": scope_warnings,
    }


def pick_task_id(default_task_id: str, summary: dict[str, Any]) -> str:
    scope = summary.get("scope_data")
    kernel = summary.get("kernel_data")
    formation = summary.get("formation_data")
    for obj in [scope, kernel, formation]:
        if isinstance(obj, dict):
            val = str(obj.get("task_id", "")).strip()
            if val:
                return val
    return default_task_id


def build_session(
    task_id: str,
    session_id: str,
    truth_level: str,
    session_status: str,
    inputs: list[dict[str, str]],
    organ_scope_summary: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    owner_questions: list[str] = []
    organ_questions: list[str] = []

    if "MISSING_SCOPE_MERGE_RECORD_WARN" in warnings:
        organ_questions.append("Provide or regenerate 8-organ scope merge record before live adapter planning.")
    if "MISSING_TASK_KERNEL_WARN" in warnings:
        owner_questions.append("Provide canonical Task Kernel object for execution binding.")
    if "MISSING_FORMATION_RECORD_WARN" in warnings:
        owner_questions.append("Provide Astronomicon formation record link for traceability.")

    if session_status == "BLOCKED_NEEDS_OWNER":
        owner_questions.append("Scope merge record is required for bounded session progression.")

    return {
        "schema_version": "0.1",
        "session_id": session_id,
        "task_id": task_id,
        "status": session_status,
        "truth_level": truth_level,
        "created_at_utc": utc_now(),
        "inputs": inputs,
        "organ_scope_summary": organ_scope_summary,
        "run_plan": [
            {
                "stage": "LOAD_AUTHORITY",
                "expected_artifact": "OFFICIO_ROLE_ACK_OR_WARN.json and DOCTRINARIUM_LAW_ACK_OR_WARN.json",
            },
            {
                "stage": "LOAD_TASK_AND_SCOPE",
                "expected_artifact": "SERVITOR_EXECUTION_SESSION.generated.json",
            },
            {
                "stage": "RUN_FOUNDATION_CHECK",
                "expected_artifact": "RUN_RECORD_001.generated.json",
            },
            {
                "stage": "DECIDE_RERUN_OR_PASS",
                "expected_artifact": "RERUN_DECISION_RECORD.generated.json",
            },
        ],
        "required_evidence": [
            "VALIDATOR_REPORT.json",
            "RUN_RECORD_001.generated.json",
            "RERUN_DECISION_RECORD.generated.json",
            "FINAL_RECEIPT.json",
        ],
        "owner_questions": sorted(set(owner_questions)),
        "organ_questions": sorted(set(organ_questions)),
        "no_fake_green_boundary": {
            "may_claim": [
                "deterministic Servitor execution session envelope",
                "foundation run/rerun decision records with explicit limitations",
            ],
            "may_not_claim": [
                "real autonomous Servitor execution",
                "live 8-organ dialogue",
                "production orchestration readiness",
                "successful real task execution beyond deterministic sample/session generation",
            ],
        },
    }


def build_run_record(
    task_id: str,
    session_id: str,
    scope_summary: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    status = "PASSED_WITH_EVIDENCE"
    failure_classification = "FOUNDATION_LIMITATION"
    check_scope = "PASS" if scope_summary.get("source_status") == "READ" else "WARN"
    check_truth = "PASS"
    check_rerun = "PASS"

    if scope_summary.get("source_status") != "READ":
        status = "FAILED_CLASSIFIED"
        failure_classification = "SCOPE_AMBIGUITY"

    if any(x in warnings for x in ["MISSING_TASK_KERNEL_WARN", "MISSING_FORMATION_RECORD_WARN"]):
        failure_classification = "FOUNDATION_LIMITATION"

    return {
        "schema_version": "0.1",
        "run_id": "RUN-001-FOUNDATION",
        "session_id": session_id,
        "task_id": task_id,
        "run_index": 1,
        "status": status,
        "started_at_utc": utc_now(),
        "checks": [
            {
                "check_id": "scope_record_available",
                "status": check_scope,
                "detail": str(scope_summary.get("source_status")),
            },
            {
                "check_id": "no_fake_green_boundary_present",
                "status": check_truth,
                "detail": "Foundation no-fake-green policy present in session record.",
            },
            {
                "check_id": "rerun_policy_present",
                "status": check_rerun,
                "detail": "Rerun decision record is generated deterministically.",
            },
        ],
        "failure_classification": failure_classification,
        "explanation_ru": (
            "Создан foundation run record. Это не live-исполнение, а проверка контура run/rerun с ограничениями."
        ),
        "evidence": [
            {
                "kind": "json",
                "path": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/SERVITOR_EXECUTION_SESSION.generated.json",
            },
            {
                "kind": "json",
                "path": "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1/RERUN_DECISION_RECORD.generated.json",
            },
        ],
    }


def build_rerun_decision(
    task_id: str,
    session_id: str,
    scope_summary: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    decision = "PASS_WITH_WARNINGS"
    reason = (
        "Foundation records were generated with explicit no-fake-green limits. "
        "Live autonomous execution remains out of scope."
    )
    next_action = "Integrate guarded live adapters and bind decisions to real execution receipts."

    questions: list[dict[str, str]] = []
    decision_warnings = sorted(set(warnings + ["Foundation-only; not live autonomous execution."]))

    if scope_summary.get("source_status") != "READ":
        decision = "ASK_ORGAN"
        reason = "Scope merge record is missing or unreadable for deterministic scoping handoff."
        next_action = "Regenerate 8-organ scope merge record and rerun builder."
        questions.append(
            {
                "target": "ORGAN_SCOPING_CORRIDOR",
                "question": "Please provide a valid ORGAN_SCOPE_MERGE_RECORD.generated.json artifact.",
            }
        )

    if "MISSING_TASK_KERNEL_WARN" in warnings:
        decision = "ASK_OWNER"
        reason = "Task Kernel object is missing; bounded execution binding is incomplete."
        next_action = "Owner should provide task kernel path or approve sample fallback."
        questions.append(
            {
                "target": "OWNER",
                "question": "Provide canonical Task Kernel object path for this execution session.",
            }
        )

    if "MISSING_FORMATION_RECORD_WARN" in warnings and decision == "PASS_WITH_WARNINGS":
        decision = "RERUN_ALLOWED"
        reason = "Formation record is missing but other core inputs are present in sample mode."
        next_action = "Rerun after adding formation record for full traceability."

    return {
        "schema_version": "0.1",
        "decision_id": "RERUN-DECISION-001",
        "session_id": session_id,
        "task_id": task_id,
        "decision": decision,
        "reason": reason,
        "next_action": next_action,
        "questions": questions,
        "warnings": decision_warnings,
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    task_id = args.task_id
    out_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir.strip()
        else (repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id).resolve()
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    scope_path = resolve_scope_merge_path(repo_root, args.scope_merge_path)
    kernel_path = (repo_root / args.task_kernel_path).resolve()
    formation_path = (repo_root / args.formation_record_path).resolve()

    inputs, summary = build_inputs(repo_root, scope_path, kernel_path, formation_path)
    truth_level, session_status, warnings = derive_truth_and_status(summary)
    scope_summary = extract_scope_summary(summary, scope_path)

    task_binding_id = pick_task_id(task_id, summary)
    session_id = f"SERVITOR-SESSION-{task_binding_id.replace('TASK-', '')}-V0_1"

    session = build_session(
        task_id=task_binding_id,
        session_id=session_id,
        truth_level=truth_level,
        session_status=session_status,
        inputs=inputs,
        organ_scope_summary=scope_summary,
        warnings=warnings,
    )
    run_record = build_run_record(
        task_id=task_binding_id,
        session_id=session_id,
        scope_summary=scope_summary,
        warnings=warnings,
    )
    rerun_decision = build_rerun_decision(
        task_id=task_binding_id,
        session_id=session_id,
        scope_summary=scope_summary,
        warnings=warnings,
    )

    write_json(out_dir / "SERVITOR_EXECUTION_SESSION.generated.json", session)
    write_json(out_dir / "RUN_RECORD_001.generated.json", run_record)
    write_json(out_dir / "RERUN_DECISION_RECORD.generated.json", rerun_decision)

    print((out_dir / "SERVITOR_EXECUTION_SESSION.generated.json").as_posix())
    print((out_dir / "RUN_RECORD_001.generated.json").as_posix())
    print((out_dir / "RERUN_DECISION_RECORD.generated.json").as_posix())
    print(f"decision={rerun_decision['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
