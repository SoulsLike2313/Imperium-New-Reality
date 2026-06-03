#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_ORGANS = [
    "ASTRONOMICON",
    "OFFICIO_AGENTIS",
    "DOCTRINARIUM",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]

DEFAULT_ALLOWED_PATHS = [
    "IMPERIUM_NEW_GENERATION/ARCHITECTURE/",
    "IMPERIUM_NEW_GENERATION/CONTRACTS/",
    "IMPERIUM_NEW_GENERATION/TASKS/",
    "IMPERIUM_NEW_GENERATION/TOOLS/",
    "IMPERIUM_NEW_GENERATION/REPORTS/",
]

DEFAULT_FORBIDDEN_PATHS = [
    "ORGANS/**",
    "SANCTUM/**",
    "IMPERIUM_TEST_VERSION/**",
    ".git/**",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build deterministic Astronomicon task formation outputs from owner intent."
    )
    parser.add_argument("--intent-file", required=True, help="Path to TASK_FORMATION_REQUEST json")
    parser.add_argument("--out-dir", required=True, help="Output directory for generated artifacts")
    parser.add_argument(
        "--record-file-name",
        default="TASK_FORMATION_RECORD_V0_1.generated.json",
        help="Output file name for generated formation record JSON",
    )
    parser.add_argument(
        "--report-file-name",
        default="TASK_FORMATION_REPORT_V0_1.md",
        help="Output file name for generated markdown summary",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("input request must be a JSON object")
    return data


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def to_token(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    return cleaned.upper() if cleaned else "UNSPECIFIED"


def derive_task_id(request: dict[str, Any]) -> str:
    hints = request.get("task_hints")
    if isinstance(hints, dict):
        suggested = str(hints.get("suggested_task_id", "")).strip()
        if suggested:
            return suggested
    request_id = str(request.get("request_id", "REQ-UNSPECIFIED"))
    return f"TASK-{to_token(request_id)}-DRAFT-V0_1"


def derive_summary(owner_intent: dict[str, Any]) -> str:
    summary = str(owner_intent.get("summary", "")).strip()
    if summary:
        return normalize_spaces(summary)
    raw_text = normalize_spaces(str(owner_intent.get("raw_text", "")))
    return raw_text[:140] if raw_text else "Owner intent summary missing."


def derive_allowed_forbidden(request: dict[str, Any]) -> tuple[list[str], list[str]]:
    constraints = request.get("constraints")
    if not isinstance(constraints, dict):
        return DEFAULT_ALLOWED_PATHS[:], DEFAULT_FORBIDDEN_PATHS[:]

    allowed = constraints.get("allowed_paths")
    forbidden = constraints.get("forbidden_paths")

    allowed_paths = (
        [str(item) for item in allowed if isinstance(item, str)] if isinstance(allowed, list) else []
    )
    forbidden_paths = (
        [str(item) for item in forbidden if isinstance(item, str)]
        if isinstance(forbidden, list)
        else []
    )

    return (
        allowed_paths if allowed_paths else DEFAULT_ALLOWED_PATHS[:],
        forbidden_paths if forbidden_paths else DEFAULT_FORBIDDEN_PATHS[:],
    )


def infer_owner_questions(request: dict[str, Any], summary_present: bool) -> list[str]:
    questions: list[str] = []
    contour = str(request.get("contour", "UNKNOWN"))
    if contour == "UNKNOWN":
        questions.append("Please confirm contour: PC, VM2, or VM3.")

    constraints = request.get("constraints")
    if not isinstance(constraints, dict):
        questions.append("Please provide explicit constraints.allowed_paths and constraints.forbidden_paths.")
    else:
        allowed = constraints.get("allowed_paths")
        forbidden = constraints.get("forbidden_paths")
        if not isinstance(allowed, list) or not allowed:
            questions.append("Please provide at least one allowed path for scope boundaries.")
        if not isinstance(forbidden, list) or not forbidden:
            questions.append("Please provide explicit forbidden paths.")
        no_live = constraints.get("no_live_runtime_claim")
        if no_live is not True:
            questions.append("Please confirm non-live runtime mode (`no_live_runtime_claim: true`).")

    if not summary_present:
        questions.append("Please provide a short owner_intent.summary for clearer task naming.")

    requested_outputs = request.get("requested_outputs")
    if isinstance(requested_outputs, list):
        required_outputs = {
            "task_kernel_draft",
            "stage_map_preview",
            "servitor_start_block",
            "owner_questions",
        }
        missing = sorted(required_outputs.difference(set(str(item) for item in requested_outputs)))
        if missing:
            questions.append(
                "Please confirm missing requested_outputs: " + ", ".join(missing) + "."
            )
    else:
        questions.append("Please provide requested_outputs list.")

    return questions


def build_stage_map(task_id: str) -> list[dict[str, Any]]:
    return [
        {
            "stage_id": "S1_INTAKE_NORMALIZE",
            "owner_organ": "ASTRONOMICON",
            "goal": "Normalize short owner intent into structured intake vectors.",
            "entry_state": "DRAFT",
            "exit_state": "REGISTERED",
            "exit_criteria": [
                "Owner intent summary is explicit",
                "Scope boundaries are declared",
            ],
            "evidence_expected": [
                "TASK_FORMATION_REQUEST_V0_1 input parsed",
                "STEP_PROOF_RECORDS entry for intake",
            ],
        },
        {
            "stage_id": "S2_ROLE_AND_GATES",
            "owner_organ": "OFFICIO_AGENTIS",
            "goal": "Align formation output with role contracts and mandatory gates.",
            "entry_state": "REGISTERED",
            "exit_state": "SCOPING_WITH_ORGANS",
            "exit_criteria": [
                "OFFICIO ACK/WARN exists",
                "No-fake-green constraints are explicit",
            ],
            "evidence_expected": [
                "OFFICIO_ROLE_ACK_OR_WARN.json",
                "GATE_ACK markdown",
            ],
        },
        {
            "stage_id": "S3_DRAFT_KERNEL_AND_STAGE_MAP",
            "owner_organ": "DOCTRINARIUM",
            "goal": "Generate draft kernel-compatible fields and stage map preview.",
            "entry_state": "SCOPING_WITH_ORGANS",
            "exit_state": "READY_FOR_SERVITOR",
            "exit_criteria": [
                "Task Kernel draft fields are present",
                "Stage map has bounded exit criteria",
            ],
            "evidence_expected": [
                "Generated TASK_FORMATION_RECORD_V0_1",
            ],
        },
        {
            "stage_id": "S4_VALIDATE_AND_RECEIPT",
            "owner_organ": "MECHANICUS",
            "goal": "Validate artifacts and produce report bundle evidence.",
            "entry_state": "READY_FOR_SERVITOR",
            "exit_state": "PASSED_WITH_WARNINGS",
            "exit_criteria": [
                "Validator status PASS or PASS_WITH_WARNINGS",
                "No forbidden paths touched",
            ],
            "evidence_expected": [
                "VALIDATOR_REPORT.json",
                "CHANGED_FILES_STATUS.md",
            ],
        },
        {
            "stage_id": "S5_OWNER_START_BLOCK",
            "owner_organ": "ADMINISTRATUM",
            "goal": "Deliver Servitor start block and owner-facing summary path.",
            "entry_state": "PASSED_WITH_WARNINGS",
            "exit_state": "CLOSED",
            "exit_criteria": [
                "Servitor start block has 2-5 lines",
                "Final report path is explicit",
            ],
            "evidence_expected": [
                "OWNER_REPORT_RU.md",
                "FINAL_RECEIPT.json",
            ],
        },
    ]


def build_servitor_start_block(task_id: str, contour: str, summary: str, auto_commit_push: bool) -> list[str]:
    closure_suffix = "commit+push if safe." if auto_commit_push else "manual closure after owner check."
    return [
        f"TASK: {task_id}",
        f"MODE: {contour} only. Work inside E:\\IMPERIUM and IMPERIUM_NEW_GENERATION only.",
        "READ FIRST: Task Formation contracts + Task Kernel Registry + Organ Packet Protocol.",
        f"GOAL: Convert short owner intent into draft kernel + stage map foundation ({summary}).",
        f"FINISH: proof records + validator report + receipt bundle + {closure_suffix}",
    ]


def build_task_kernel_draft(
    task_id: str,
    summary: str,
    allowed_paths: list[str],
    forbidden_paths: list[str],
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "task_title": f"Astronomicon Formation Draft: {summary}",
        "status": "DRAFT",
        "scope": {
            "mode": "bounded_foundation",
            "purpose": "Bridge owner short intent into a Task Kernel-ready draft object.",
            "non_goals": [
                "No live multi-organ runtime",
                "No autonomous rerun loop",
                "No production orchestration claim",
            ],
        },
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "required_organs": REQUIRED_ORGANS,
        "required_skills": [
            "agent.read_first_admission.v0_1",
            "agent.scope_boundary_control.v0_1",
            "agent.super_skepticism_loop.v0_1",
            "agent.proof_record_writer.v0_1",
        ],
        "evidence_policy": {
            "required_receipts": [
                "OFFICIO_ROLE_ACK_OR_WARN.json",
                "STEP_PROOF_RECORDS.jsonl",
                "VALIDATOR_REPORT.json",
                "FINAL_RECEIPT.json",
                "OWNER_REPORT_RU.md",
            ],
            "proof_record_required": True,
            "validator_required": True,
        },
        "task_kernel_contract_ref": "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json",
        "task_registry_index_ref": "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_REGISTRY_INDEX_V0_1.schema.json",
        "organ_packet_contract_ref": "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/ORGAN_PACKET_SET_V0_1.schema.json",
    }


def build_record(request: dict[str, Any]) -> dict[str, Any]:
    owner_intent = request.get("owner_intent")
    if not isinstance(owner_intent, dict):
        raise ValueError("owner_intent must be an object")

    raw_text = normalize_spaces(str(owner_intent.get("raw_text", "")))
    if not raw_text:
        raise ValueError("owner_intent.raw_text must not be empty")

    summary_raw = str(owner_intent.get("summary", "")).strip()
    summary_present = bool(summary_raw)
    summary = derive_summary(owner_intent)
    language = str(owner_intent.get("language", "UNKNOWN"))
    request_id = str(request.get("request_id", "REQ-UNSPECIFIED"))
    task_id = derive_task_id(request)
    formation_id = f"FORMATION-{to_token(request_id)}"
    contour = str(request.get("contour", "UNKNOWN"))

    constraints = request.get("constraints") if isinstance(request.get("constraints"), dict) else {}
    auto_commit_push = bool(constraints.get("auto_commit_push", False)) if isinstance(constraints, dict) else False

    allowed_paths, forbidden_paths = derive_allowed_forbidden(request)
    owner_questions = infer_owner_questions(request, summary_present)
    stage_map_preview = build_stage_map(task_id)

    task_kernel_draft = build_task_kernel_draft(
        task_id=task_id,
        summary=summary,
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
    )

    limitations = [
        "Foundation-only output. No live multi-organ orchestration claim.",
        "No autonomous Servitor run/rerun runtime is implemented in this version.",
    ]
    if constraints and constraints.get("no_live_runtime_claim") is not True:
        limitations.append("Input did not explicitly enforce no_live_runtime_claim=true.")

    self_verdict = "STRONG_WITH_WARNINGS" if owner_questions else "PROVED"

    return {
        "schema_version": "0.1",
        "formation_id": formation_id,
        "source_request_id": request_id,
        "task_id": task_id,
        "owner_intent": {
            "raw_text": raw_text,
            "summary": summary,
            "language": language,
        },
        "scope": {
            "mode": "bounded_foundation",
            "purpose": "Transform short owner intent into deterministic Astronomicon formation artifacts.",
            "non_goals": [
                "No live organ packet runtime",
                "No autonomous execution orchestrator",
                "No production readiness claim",
            ],
        },
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "required_organs": REQUIRED_ORGANS,
        "task_kernel_draft": task_kernel_draft,
        "stage_map_preview": stage_map_preview,
        "servitor_start_block": build_servitor_start_block(
            task_id=task_id,
            contour=contour,
            summary=summary,
            auto_commit_push=auto_commit_push,
        ),
        "owner_questions": owner_questions,
        "limitations": limitations,
        "self_verdict": self_verdict,
    }


def build_markdown(record: dict[str, Any], intent_path: Path) -> str:
    lines: list[str] = []
    lines.append("# Astronomicon Task Formation Report V0.1")
    lines.append("")
    lines.append("## Input")
    lines.append(f"- intent_file: `{intent_path.as_posix()}`")
    lines.append(f"- request_id: `{record['source_request_id']}`")
    lines.append("")
    lines.append("## Formation Output")
    lines.append(f"- formation_id: `{record['formation_id']}`")
    lines.append(f"- task_id: `{record['task_id']}`")
    lines.append(f"- self_verdict: `{record['self_verdict']}`")
    lines.append("")
    lines.append("## Scope Boundaries")
    lines.append("- allowed_paths:")
    for path in record["allowed_paths"]:
        lines.append(f"  - `{path}`")
    lines.append("- forbidden_paths:")
    for path in record["forbidden_paths"]:
        lines.append(f"  - `{path}`")
    lines.append("")
    lines.append("## Required Organs")
    for organ in record["required_organs"]:
        lines.append(f"- {organ}")
    lines.append("")
    lines.append("## Stage Map Preview")
    for stage in record["stage_map_preview"]:
        lines.append(
            f"- {stage['stage_id']} ({stage['owner_organ']}): {stage['goal']}"
        )
    lines.append("")
    lines.append("## Servitor Start Block (2-5 lines)")
    for line in record["servitor_start_block"]:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## Owner Questions")
    if record["owner_questions"]:
        for question in record["owner_questions"]:
            lines.append(f"- {question}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Limitations")
    for limitation in record["limitations"]:
        lines.append(f"- {limitation}")
    lines.append("")
    lines.append("## Truth Statement")
    lines.append("- Foundation-only; no live multi-organ orchestration claim.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    intent_path = Path(args.intent_file).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    request = read_json(intent_path)
    record = build_record(request)

    record_path = out_dir / args.record_file_name
    report_path = out_dir / args.report_file_name

    record_path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    report_path.write_text(build_markdown(record, intent_path), encoding="utf-8")

    print(record_path.as_posix())
    print(report_path.as_posix())
    print(f"self_verdict={record['self_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
