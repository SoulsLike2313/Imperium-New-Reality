#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_SIZE_CLASSES = {"SMALL", "MEDIUM", "LARGE", "MEGA"}
CONTEXT_BUDGET_CLASSES = {"LOW", "MEDIUM", "HIGH", "EXTREME"}
FILE_TOUCH_CLASSES = {"FILES_1_10", "FILES_10_30", "FILES_30_80", "FILES_80_PLUS"}
COMMAND_COUNT_CLASSES = {"CMDS_1_20", "CMDS_20_60", "CMDS_60_140", "CMDS_140_PLUS"}
EVIDENCE_VOLUME_CLASSES = {"EVIDENCE_LOW", "EVIDENCE_MEDIUM", "EVIDENCE_HIGH", "EVIDENCE_EXTREME"}
ACCURACY_RISKS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
CHECKPOINT_CADENCES = {"END_ONLY", "MILESTONE", "PER_STAGE"}


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


def task_control_root() -> Path:
    return Path(__file__).resolve().parents[1] / "TASK_CONTROL"


def default_volume_schema() -> Path:
    return task_control_root() / "TASK_VOLUME_CONTROL.schema.json"


def default_classes_path() -> Path:
    return task_control_root() / "TASK_VOLUME_CLASSES.json"


def normalize_allowed_scope(task_contract: dict[str, Any]) -> list[str]:
    if isinstance(task_contract.get("allowed_scope"), list):
        return [str(x) for x in task_contract["allowed_scope"]]
    if isinstance(task_contract.get("allowed_repo_write_scope"), list):
        return [str(x) for x in task_contract["allowed_repo_write_scope"]]
    return []


def infer_organs(scope: list[str]) -> set[str]:
    organs: set[str] = set()
    pattern = re.compile(r"ORGAN_AGENTS/([^/]+)/")
    for item in scope:
        match = pattern.search(item)
        if match:
            organs.add(match.group(1).strip().upper())
    return organs


def infer_task_size(organ_count: int, scope_count: int, check_count: int) -> str:
    if organ_count >= 6 or scope_count >= 10 or check_count >= 7:
        return "MEGA"
    if organ_count >= 3 or scope_count >= 6:
        return "LARGE"
    if organ_count >= 2 or scope_count >= 3:
        return "MEDIUM"
    return "SMALL"


def class_profile(task_size_class: str) -> dict[str, Any]:
    mapping: dict[str, dict[str, Any]] = {
        "SMALL": {
            "context_budget_class": "LOW",
            "expected_file_touch_class": "FILES_1_10",
            "expected_command_count_class": "CMDS_1_20",
            "expected_evidence_volume_class": "EVIDENCE_LOW",
            "accuracy_risk": "LOW",
            "checkpoint_required": False,
            "checkpoint_cadence": "END_ONLY",
        },
        "MEDIUM": {
            "context_budget_class": "MEDIUM",
            "expected_file_touch_class": "FILES_10_30",
            "expected_command_count_class": "CMDS_20_60",
            "expected_evidence_volume_class": "EVIDENCE_MEDIUM",
            "accuracy_risk": "MEDIUM",
            "checkpoint_required": False,
            "checkpoint_cadence": "MILESTONE",
        },
        "LARGE": {
            "context_budget_class": "HIGH",
            "expected_file_touch_class": "FILES_30_80",
            "expected_command_count_class": "CMDS_60_140",
            "expected_evidence_volume_class": "EVIDENCE_HIGH",
            "accuracy_risk": "HIGH",
            "checkpoint_required": True,
            "checkpoint_cadence": "PER_STAGE",
        },
        "MEGA": {
            "context_budget_class": "EXTREME",
            "expected_file_touch_class": "FILES_80_PLUS",
            "expected_command_count_class": "CMDS_140_PLUS",
            "expected_evidence_volume_class": "EVIDENCE_EXTREME",
            "accuracy_risk": "CRITICAL",
            "checkpoint_required": True,
            "checkpoint_cadence": "PER_STAGE",
        },
    }
    return mapping[task_size_class]


def recommended_phases(task_size_class: str) -> list[dict[str, Any]]:
    if task_size_class == "SMALL":
        return [
            {"phase_id": "S1", "phase_name": "single_pass", "goal": "bounded execution and report", "checkpoint_gate": True}
        ]
    if task_size_class == "MEDIUM":
        return [
            {"phase_id": "S1", "phase_name": "prepare", "goal": "intake and preflight", "checkpoint_gate": False},
            {"phase_id": "S2", "phase_name": "execute_and_report", "goal": "implementation and closure", "checkpoint_gate": True},
        ]
    if task_size_class == "LARGE":
        return [
            {"phase_id": "S1", "phase_name": "design", "goal": "schemas and control model", "checkpoint_gate": True},
            {"phase_id": "S2", "phase_name": "implementation", "goal": "bounded implementation", "checkpoint_gate": True},
            {"phase_id": "S3", "phase_name": "validation", "goal": "smoke and evidence checks", "checkpoint_gate": True},
            {"phase_id": "S4", "phase_name": "closure", "goal": "reports and commit", "checkpoint_gate": True},
        ]
    return [
        {"phase_id": "S1", "phase_name": "control_design", "goal": "task control docs and schemas", "checkpoint_gate": True},
        {"phase_id": "S2", "phase_name": "builders", "goal": "CLI tools and skeleton generators", "checkpoint_gate": True},
        {"phase_id": "S3", "phase_name": "validation", "goal": "compile/help/example checks", "checkpoint_gate": True},
        {"phase_id": "S4", "phase_name": "organ_alignment", "goal": "responsibility alignment", "checkpoint_gate": True},
        {"phase_id": "S5", "phase_name": "report_and_release", "goal": "reports, receipts, commit", "checkpoint_gate": True},
    ]


def classify_from_task_contract(task_contract: dict[str, Any]) -> dict[str, Any]:
    scope = normalize_allowed_scope(task_contract)
    organs = infer_organs(scope)
    organ_count = len(organs) if organs else int(task_contract.get("organ_count", 1) or 1)
    check_count = len(task_contract.get("required_checks", [])) if isinstance(task_contract.get("required_checks"), list) else 0
    task_size_class = infer_task_size(organ_count=organ_count, scope_count=len(scope), check_count=check_count)
    profile = class_profile(task_size_class)

    split_conditions = [
        "scope spans 3 or more organs",
        "required checks exceed 5 commands",
        "evidence references exceed one report package",
    ]
    if task_size_class == "MEGA":
        split_conditions.append("mixed control/docs/cli/report planes exceed single-pass safety")

    payload: dict[str, Any] = {
        "schema_version": "TASK_VOLUME_CONTROL_V0_1",
        "generated_at_utc": utc_now(),
        "task_id": str(task_contract.get("task_id", "UNKNOWN_TASK")),
        "task_size_class": task_size_class,
        "context_budget_class": profile["context_budget_class"],
        "organ_count": organ_count,
        "expected_file_touch_class": profile["expected_file_touch_class"],
        "expected_command_count_class": profile["expected_command_count_class"],
        "expected_evidence_volume_class": profile["expected_evidence_volume_class"],
        "accuracy_risk": profile["accuracy_risk"],
        "checkpoint_required": profile["checkpoint_required"],
        "checkpoint_cadence": profile["checkpoint_cadence"],
        "split_required_if": split_conditions,
        "continuation_protocol_required": task_size_class in {"LARGE", "MEGA"},
        "recommended_execution_phases": recommended_phases(task_size_class),
        "classification_trace": {
            "scope_count": len(scope),
            "required_checks_count": check_count,
            "organs_detected": sorted(organs),
            "source_schema_version": str(task_contract.get("schema_version", "")),
        },
    }
    return payload


def validate_task_volume(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    required = [
        "task_id",
        "task_size_class",
        "context_budget_class",
        "organ_count",
        "expected_file_touch_class",
        "expected_command_count_class",
        "expected_evidence_volume_class",
        "accuracy_risk",
        "checkpoint_required",
        "checkpoint_cadence",
        "split_required_if",
        "continuation_protocol_required",
        "recommended_execution_phases",
    ]
    for field in required:
        if field not in payload:
            errors.append(f"missing_field:{field}")

    task_size = str(payload.get("task_size_class", ""))
    if task_size and task_size not in TASK_SIZE_CLASSES:
        errors.append(f"invalid_task_size_class:{task_size}")

    context_class = str(payload.get("context_budget_class", ""))
    if context_class and context_class not in CONTEXT_BUDGET_CLASSES:
        errors.append(f"invalid_context_budget_class:{context_class}")

    file_class = str(payload.get("expected_file_touch_class", ""))
    if file_class and file_class not in FILE_TOUCH_CLASSES:
        errors.append(f"invalid_expected_file_touch_class:{file_class}")

    cmd_class = str(payload.get("expected_command_count_class", ""))
    if cmd_class and cmd_class not in COMMAND_COUNT_CLASSES:
        errors.append(f"invalid_expected_command_count_class:{cmd_class}")

    evidence_class = str(payload.get("expected_evidence_volume_class", ""))
    if evidence_class and evidence_class not in EVIDENCE_VOLUME_CLASSES:
        errors.append(f"invalid_expected_evidence_volume_class:{evidence_class}")

    accuracy_risk = str(payload.get("accuracy_risk", ""))
    if accuracy_risk and accuracy_risk not in ACCURACY_RISKS:
        errors.append(f"invalid_accuracy_risk:{accuracy_risk}")

    cadence = str(payload.get("checkpoint_cadence", ""))
    if cadence and cadence not in CHECKPOINT_CADENCES:
        errors.append(f"invalid_checkpoint_cadence:{cadence}")

    organ_count = payload.get("organ_count")
    if not isinstance(organ_count, int) or organ_count < 1:
        errors.append("invalid_organ_count")

    checkpoint_required = payload.get("checkpoint_required")
    if not isinstance(checkpoint_required, bool):
        errors.append("checkpoint_required_must_be_boolean")

    split_rules = payload.get("split_required_if")
    if not isinstance(split_rules, list) or not all(isinstance(x, str) and x.strip() for x in split_rules):
        errors.append("split_required_if_must_be_non_empty_string_list")

    continuation_required = payload.get("continuation_protocol_required")
    if not isinstance(continuation_required, bool):
        errors.append("continuation_protocol_required_must_be_boolean")

    phases = payload.get("recommended_execution_phases")
    if not isinstance(phases, list) or len(phases) == 0:
        errors.append("recommended_execution_phases_must_be_non_empty_list")
    else:
        for idx, phase in enumerate(phases):
            if not isinstance(phase, dict):
                errors.append(f"phase_{idx}_must_be_object")
                continue
            for field in ("phase_id", "phase_name", "goal", "checkpoint_gate"):
                if field not in phase:
                    errors.append(f"phase_{idx}_missing_field:{field}")

    if task_size in {"LARGE", "MEGA"}:
        if checkpoint_required is not True:
            errors.append("large_or_mega_requires_checkpoint_required_true")
        if isinstance(phases, list) and len(phases) < 2:
            errors.append("large_or_mega_requires_two_or_more_phases")
        if cadence not in {"PER_STAGE", "MILESTONE"}:
            warnings.append("large_or_mega_should_use_checkpoint_cadence_per_stage_or_milestone")

    if task_size == "MEGA" and continuation_required is not True:
        errors.append("mega_requires_continuation_protocol")

    return errors, warnings


def render_human_report(payload: dict[str, Any]) -> str:
    lines = [
        "TASK VOLUME REPORT",
        f"task_id: {payload.get('task_id', '')}",
        f"task_size_class: {payload.get('task_size_class', '')}",
        f"context_budget_class: {payload.get('context_budget_class', '')}",
        f"organ_count: {payload.get('organ_count', '')}",
        f"accuracy_risk: {payload.get('accuracy_risk', '')}",
        f"checkpoint_required: {payload.get('checkpoint_required', '')}",
        f"checkpoint_cadence: {payload.get('checkpoint_cadence', '')}",
        "recommended_phases:",
    ]
    for phase in payload.get("recommended_execution_phases", []):
        if not isinstance(phase, dict):
            continue
        lines.append(f"- {phase.get('phase_id', '?')}: {phase.get('phase_name', '?')} | gate={phase.get('checkpoint_gate', False)}")
    return "\n".join(lines)


def cmd_classify(args: argparse.Namespace) -> int:
    task_contract = load_json(Path(args.task_contract))
    payload = classify_from_task_contract(task_contract)
    if args.out:
        write_json(Path(args.out), payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    volume = load_json(Path(args.input))
    errors, warnings = validate_task_volume(volume)
    verdict = "PASS" if not errors else "FAIL_SCHEMA_VALIDATION"
    payload = {
        "schema_version": "TASK_VOLUME_VALIDATION_RESULT_V0_1",
        "generated_at_utc": utc_now(),
        "input": str(Path(args.input)),
        "schema_path": str(Path(args.schema)),
        "errors": errors,
        "warnings": warnings,
        "verdict": verdict,
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if not errors else 1


def cmd_report(args: argparse.Namespace) -> int:
    volume = load_json(Path(args.input))
    print(render_human_report(volume))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Task volume classifier and validator.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_classify = sub.add_parser("classify", help="Classify task contract into task volume control payload.")
    p_classify.add_argument("--task-contract", required=True)
    p_classify.add_argument("--out", default=None)

    p_validate = sub.add_parser("validate", help="Validate task volume control JSON payload.")
    p_validate.add_argument("--input", required=True)
    p_validate.add_argument("--schema", default=str(default_volume_schema()))

    p_report = sub.add_parser("report", help="Print human-readable report from task volume JSON.")
    p_report.add_argument("--input", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "classify":
        return cmd_classify(args)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "report":
        return cmd_report(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
