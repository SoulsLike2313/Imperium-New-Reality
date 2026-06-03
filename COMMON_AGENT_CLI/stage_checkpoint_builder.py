#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DECISION_OPTIONS = ["ACCEPT", "REQUEST_FIX", "CONTINUE_WITH_NOTES", "STOP", "SPLIT_REQUIRED"]
STAGE_TYPES = {"PLAN", "IMPLEMENT", "VERIFY", "INTEGRATE", "REPORT", "HANDOFF"}
STATUS_VALUES = {"READY_FOR_REVIEW", "NEEDS_FIX", "BLOCKED", "ACCEPTED"}
ORGAN_IDS = [
    "STRATEGIUM_AGENT",
    "ASTRONOMICON_AGENT",
    "ADMINISTRATUM_AGENT",
    "OFFICIO_AGENTIS_AGENT",
    "INQUISITION_AGENT",
    "MECHANICUS_AGENT",
    "SCHOLA_IMPERIALIS_AGENT",
    "DOCTRINARIUM_AGENT",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def current_git_head(cwd: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(cwd), text=True).strip()
    except Exception:
        return "UNKNOWN"


def current_git_status_short(cwd: Path) -> list[str]:
    try:
        out = subprocess.check_output(["git", "status", "--short"], cwd=str(cwd), text=True)
        return [line for line in out.splitlines() if line.strip()]
    except Exception:
        return ["UNKNOWN"]


def build_checkpoint(args: argparse.Namespace) -> dict[str, Any]:
    cwd = Path.cwd()
    before_head = args.before_head or current_git_head(cwd)
    before_status = args.before_status if args.before_status else current_git_status_short(cwd)
    after_head = args.after_head or before_head
    after_status = args.after_status if args.after_status else before_status

    organ_checks = {organ: args.organ_default for organ in ORGAN_IDS}

    payload: dict[str, Any] = {
        "schema_version": "STAGE_CHECKPOINT_V0_1",
        "generated_at_utc": utc_now(),
        "task_id": args.task_id,
        "stage_id": args.stage_id,
        "stage_name": args.stage_name,
        "stage_type": args.stage_type,
        "before_state": {
            "git_head": before_head,
            "git_status_short": before_status,
            "notes": [],
        },
        "after_state": {
            "git_head": after_head,
            "git_status_short": after_status,
            "notes": [],
        },
        "touched_files": [],
        "diff_summary": args.diff_summary,
        "evidence_links": args.evidence if args.evidence else ["REPORTS/<task>/stage_checkpoint_evidence.md"],
        "warnings": [],
        "errors": [],
        "blockers": [],
        "organ_checks": organ_checks,
        "owner_decision_options": DECISION_OPTIONS,
        "owner_decision_required": True,
        "checkpoint_status": args.checkpoint_status,
        "notes": [],
    }
    return payload


def validate_checkpoint(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    required = [
        "task_id",
        "stage_id",
        "stage_name",
        "stage_type",
        "before_state",
        "after_state",
        "touched_files",
        "diff_summary",
        "evidence_links",
        "warnings",
        "errors",
        "blockers",
        "organ_checks",
        "owner_decision_options",
        "owner_decision_required",
        "checkpoint_status",
    ]
    for field in required:
        if field not in payload:
            errors.append(f"missing_field:{field}")

    stage_type = str(payload.get("stage_type", ""))
    if stage_type and stage_type not in STAGE_TYPES:
        errors.append(f"invalid_stage_type:{stage_type}")

    checkpoint_status = str(payload.get("checkpoint_status", ""))
    if checkpoint_status and checkpoint_status not in STATUS_VALUES:
        errors.append(f"invalid_checkpoint_status:{checkpoint_status}")

    if not isinstance(payload.get("evidence_links"), list) or len(payload.get("evidence_links", [])) == 0:
        errors.append("evidence_links_must_be_non_empty_list")

    for field in ("warnings", "errors", "blockers", "touched_files"):
        if not isinstance(payload.get(field), list):
            errors.append(f"{field}_must_be_list")

    if not isinstance(payload.get("owner_decision_required"), bool):
        errors.append("owner_decision_required_must_be_boolean")

    options = payload.get("owner_decision_options")
    if not isinstance(options, list):
        errors.append("owner_decision_options_must_be_list")
    else:
        missing = sorted(list(set(DECISION_OPTIONS) - set(str(x) for x in options)))
        if missing:
            errors.append("missing_owner_decision_options:" + ",".join(missing))

    organ_checks = payload.get("organ_checks")
    if not isinstance(organ_checks, dict):
        errors.append("organ_checks_must_be_object")
    else:
        for organ in ORGAN_IDS:
            if organ not in organ_checks:
                errors.append(f"missing_organ_check:{organ}")
            else:
                token = str(organ_checks.get(organ, ""))
                if token not in {"PASS", "WARN", "BLOCKED"}:
                    errors.append(f"invalid_organ_check_status:{organ}:{token}")

    for field in ("before_state", "after_state"):
        state = payload.get(field)
        if not isinstance(state, dict):
            errors.append(f"{field}_must_be_object")
            continue
        if "git_head" not in state or "git_status_short" not in state:
            errors.append(f"{field}_missing_git_fields")
        if not isinstance(state.get("git_status_short", []), list):
            errors.append(f"{field}.git_status_short_must_be_list")

    if isinstance(payload.get("blockers"), list) and payload.get("blockers") and payload.get("checkpoint_status") == "READY_FOR_REVIEW":
        warnings.append("checkpoint_status_ready_with_blockers")

    return errors, warnings


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "STAGE CHECKPOINT REPORT",
        f"task_id: {payload.get('task_id', '')}",
        f"stage: {payload.get('stage_id', '')} | {payload.get('stage_name', '')}",
        f"stage_type: {payload.get('stage_type', '')}",
        f"checkpoint_status: {payload.get('checkpoint_status', '')}",
        "owner_decision_options:",
    ]
    for item in payload.get("owner_decision_options", []):
        lines.append(f"- {item}")
    lines.append("organ_checks:")
    organ_checks = payload.get("organ_checks", {})
    if isinstance(organ_checks, dict):
        for organ in ORGAN_IDS:
            lines.append(f"- {organ}: {organ_checks.get(organ, 'UNKNOWN')}")
    return "\n".join(lines)


def cmd_create(args: argparse.Namespace) -> int:
    payload = build_checkpoint(args)
    if args.out:
        write_json(Path(args.out), payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    payload = load_json(Path(args.input))
    errors, warnings = validate_checkpoint(payload)
    verdict = "PASS" if not errors else "FAIL_SCHEMA_VALIDATION"
    result = {
        "schema_version": "STAGE_CHECKPOINT_VALIDATION_RESULT_V0_1",
        "generated_at_utc": utc_now(),
        "input": str(Path(args.input)),
        "errors": errors,
        "warnings": warnings,
        "verdict": verdict,
    }
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if not errors else 1


def cmd_report(args: argparse.Namespace) -> int:
    payload = load_json(Path(args.input))
    print(render_report(payload))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and validate stage checkpoint payloads.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create checkpoint skeleton JSON.")
    p_create.add_argument("--task-id", required=True)
    p_create.add_argument("--stage-id", required=True)
    p_create.add_argument("--stage-name", required=True)
    p_create.add_argument("--stage-type", required=True, choices=sorted(STAGE_TYPES))
    p_create.add_argument("--checkpoint-status", default="READY_FOR_REVIEW", choices=sorted(STATUS_VALUES))
    p_create.add_argument("--organ-default", default="PASS", choices=["PASS", "WARN", "BLOCKED"])
    p_create.add_argument("--diff-summary", default="No diff summary provided yet.")
    p_create.add_argument("--evidence", action="append", default=[])
    p_create.add_argument("--before-head", default=None)
    p_create.add_argument("--after-head", default=None)
    p_create.add_argument("--before-status", action="append", default=[])
    p_create.add_argument("--after-status", action="append", default=[])
    p_create.add_argument("--out", default=None)

    p_validate = sub.add_parser("validate", help="Validate checkpoint JSON payload.")
    p_validate.add_argument("--input", required=True)

    p_report = sub.add_parser("report", help="Print human-readable checkpoint report.")
    p_report.add_argument("--input", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "create":
        return cmd_create(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "report":
        return cmd_report(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
