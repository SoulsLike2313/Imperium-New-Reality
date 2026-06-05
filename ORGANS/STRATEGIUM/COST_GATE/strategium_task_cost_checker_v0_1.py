#!/usr/bin/env python3
"""Validate Strategium task budget, cost, and KPD receipts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BUDGET_CLASSES = ["TINY", "SMALL", "SMALL_TO_MEDIUM", "MEDIUM", "LARGE"]
BUDGET_REQUIRED = [
    "schema_version",
    "task_id",
    "budget_class_planned",
    "max_files_changed_target",
    "stop_if_scope_expands",
    "planned_scope",
    "required_receipts",
    "unknown_measurement_policy",
    "next_task_budget_recommendation",
]
COST_REQUIRED = [
    "schema_version",
    "task_id",
    "budget_class_planned",
    "actual_cost_class",
    "files_changed_count",
    "commands_run_count",
    "validators_run_count",
    "wall_time_minutes",
    "token_usage",
    "owner_intervention_count",
    "scope_expansion_count",
    "kpd_verdict",
    "next_task_budget_recommendation",
]
KPD_REQUIRED = [
    "schema_version",
    "task_id",
    "kpd_before",
    "kpd_after",
    "kpd_delta",
    "verdict",
    "evidence_paths",
    "next_route",
]
UNKNOWN_FIELDS = [
    "commands_run_count",
    "validators_run_count",
    "wall_time_minutes",
    "token_usage",
    "owner_intervention_count",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read_json(path: Path) -> tuple[Any | None, str]:
    if not path.is_file():
        return None, "file missing"
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return None, "UTF-8 BOM detected"
    try:
        return json.loads(raw.decode("utf-8")), ""
    except UnicodeDecodeError as exc:
        return None, f"UTF-8 decode error: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"JSON decode error at line {exc.lineno} column {exc.colno}: {exc.msg}"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def add_error(errors: list[dict[str, Any]], file_id: str, field: str, message: str) -> None:
    errors.append({"file": file_id, "field": field, "message": message})


def require_fields(payload: dict[str, Any], required: list[str], file_id: str, errors: list[dict[str, Any]]) -> None:
    for field in required:
        if field not in payload:
            add_error(errors, file_id, field, "required field missing")


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_unknown_with_reason(value: Any) -> bool:
    return isinstance(value, dict) and value.get("status") == "UNKNOWN_WITH_REASON" and is_non_empty_string(value.get("reason"))


def is_non_negative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def is_non_negative_number(value: Any) -> bool:
    return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool) and value >= 0


def validate_budget(payload: Any) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    file_id = "TASK_BUDGET_CARD"
    if not isinstance(payload, dict):
        add_error(errors, file_id, "$", "root must be object")
        return errors
    require_fields(payload, BUDGET_REQUIRED, file_id, errors)
    if payload.get("schema_version") != "strategium.task_budget_card.v0_1":
        add_error(errors, file_id, "schema_version", "unexpected schema version")
    if payload.get("budget_class_planned") not in BUDGET_CLASSES:
        add_error(errors, file_id, "budget_class_planned", "unknown or missing budget class")
    if not is_non_negative_integer(payload.get("max_files_changed_target")):
        add_error(errors, file_id, "max_files_changed_target", "must be non-negative integer")
    if not isinstance(payload.get("stop_if_scope_expands"), bool):
        add_error(errors, file_id, "stop_if_scope_expands", "must be boolean")
    for field in ("planned_scope", "required_receipts"):
        value = payload.get(field)
        if not isinstance(value, list) or not value or not all(is_non_empty_string(item) for item in value):
            add_error(errors, file_id, field, "must be non-empty string array")
    if not is_non_empty_string(payload.get("unknown_measurement_policy")):
        add_error(errors, file_id, "unknown_measurement_policy", "must be non-empty string")
    if not is_non_empty_string(payload.get("next_task_budget_recommendation")):
        add_error(errors, file_id, "next_task_budget_recommendation", "must be non-empty string")
    return errors


def validate_cost(payload: Any, budget_payload: Any) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    file_id = "TASK_COST_RECEIPT"
    if not isinstance(payload, dict):
        add_error(errors, file_id, "$", "root must be object")
        return errors
    require_fields(payload, COST_REQUIRED, file_id, errors)
    if payload.get("schema_version") != "strategium.task_cost_receipt.v0_1":
        add_error(errors, file_id, "schema_version", "unexpected schema version")
    for field in ("budget_class_planned", "actual_cost_class"):
        if payload.get(field) not in BUDGET_CLASSES:
            add_error(errors, file_id, field, "unknown budget class")
    if isinstance(budget_payload, dict) and budget_payload.get("budget_class_planned") != payload.get("budget_class_planned"):
        add_error(errors, file_id, "budget_class_planned", "does not match task budget card")
    if not is_non_negative_integer(payload.get("files_changed_count")):
        add_error(errors, file_id, "files_changed_count", "must be non-negative integer")
    for field in UNKNOWN_FIELDS:
        value = payload.get(field)
        valid = is_non_negative_number(value) or is_unknown_with_reason(value)
        if not valid:
            add_error(errors, file_id, field, "must be non-negative number or UNKNOWN_WITH_REASON object")
    if not is_non_negative_integer(payload.get("scope_expansion_count")):
        add_error(errors, file_id, "scope_expansion_count", "must be non-negative integer")
    planned = payload.get("budget_class_planned")
    actual = payload.get("actual_cost_class")
    if planned in BUDGET_CLASSES and actual in BUDGET_CLASSES and BUDGET_CLASSES.index(actual) > BUDGET_CLASSES.index(planned):
        if not is_non_empty_string(payload.get("overrun_reason")):
            add_error(errors, file_id, "overrun_reason", "required when actual cost exceeds planned budget")
    if not is_non_empty_string(payload.get("kpd_verdict")):
        add_error(errors, file_id, "kpd_verdict", "must be non-empty string")
    if not is_non_empty_string(payload.get("next_task_budget_recommendation")):
        add_error(errors, file_id, "next_task_budget_recommendation", "must be non-empty string")
    return errors


def validate_kpd(payload: Any, expected_task_id: str | None) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    file_id = "KPD_DELTA_RECEIPT"
    if not isinstance(payload, dict):
        add_error(errors, file_id, "$", "root must be object")
        return errors
    require_fields(payload, KPD_REQUIRED, file_id, errors)
    if payload.get("schema_version") != "strategium.kpd_delta_receipt.v0_1":
        add_error(errors, file_id, "schema_version", "unexpected schema version")
    if expected_task_id and payload.get("task_id") != expected_task_id:
        add_error(errors, file_id, "task_id", "does not match task budget card")
    for field in ("kpd_before", "kpd_after", "kpd_delta", "verdict", "next_route"):
        if not is_non_empty_string(payload.get(field)):
            add_error(errors, file_id, field, "must be non-empty string")
    evidence_paths = payload.get("evidence_paths")
    if not isinstance(evidence_paths, list) or not evidence_paths or not all(is_non_empty_string(item) for item in evidence_paths):
        add_error(errors, file_id, "evidence_paths", "must be non-empty string array")
    return errors


def validate_set(budget_path: Path, cost_path: Path, kpd_path: Path) -> dict[str, Any]:
    budget_payload, budget_error = read_json(budget_path)
    cost_payload, cost_error = read_json(cost_path)
    kpd_payload, kpd_error = read_json(kpd_path)
    errors: list[dict[str, Any]] = []
    for file_id, error in (
        ("TASK_BUDGET_CARD", budget_error),
        ("TASK_COST_RECEIPT", cost_error),
        ("KPD_DELTA_RECEIPT", kpd_error),
    ):
        if error:
            add_error(errors, file_id, "$", error)
    if not budget_error:
        errors.extend(validate_budget(budget_payload))
    if not cost_error:
        errors.extend(validate_cost(cost_payload, budget_payload))
    expected_task_id = budget_payload.get("task_id") if isinstance(budget_payload, dict) else None
    if not kpd_error:
        errors.extend(validate_kpd(kpd_payload, expected_task_id))
    task_id = budget_payload.get("task_id") if isinstance(budget_payload, dict) else ""
    if isinstance(cost_payload, dict) and task_id and cost_payload.get("task_id") != task_id:
        add_error(errors, "TASK_COST_RECEIPT", "task_id", "does not match task budget card")
    verdict = "PASS" if not errors else "BLOCK"
    return {
        "task_id": task_id or "UNKNOWN",
        "budget_card": to_posix(budget_path),
        "cost_receipt": to_posix(cost_path),
        "kpd_delta_receipt": to_posix(kpd_path),
        "error_count": len(errors),
        "errors": errors,
        "verdict": verdict,
    }


def run_fixtures(checker_path: Path) -> dict[str, Any]:
    root = checker_path.parent / "FIXTURES"
    cases = [
        ("positive_minimal", "PASS"),
        ("negative_missing_budget_class", "BLOCK"),
    ]
    results = []
    for name, expected in cases:
        case_root = root / name
        result = validate_set(case_root / "TASK_BUDGET_CARD.json", case_root / "TASK_COST_RECEIPT.json", case_root / "KPD_DELTA_RECEIPT.json")
        result["fixture_name"] = name
        result["expected_verdict"] = expected
        result["expectation_met"] = result["verdict"] == expected
        results.append(result)
    verdict = "PASS" if all(item["expectation_met"] for item in results) else "BLOCK"
    return {
        "schema_version": "strategium.task_cost_checker_fixture_report.v0_1",
        "created_at_utc": utc_now(),
        "fixtures_root": to_posix(root),
        "results": results,
        "verdict": verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Strategium cost gate receipts.")
    parser.add_argument("--budget-card")
    parser.add_argument("--cost-receipt")
    parser.add_argument("--kpd-delta")
    parser.add_argument("--out")
    parser.add_argument("--run-fixtures", action="store_true")
    parser.add_argument("--allow-block-exit-zero", action="store_true")
    args = parser.parse_args()

    if args.run_fixtures:
        report = run_fixtures(Path(__file__).resolve())
    else:
        if not (args.budget_card and args.cost_receipt and args.kpd_delta):
            parser.error("--budget-card, --cost-receipt, and --kpd-delta are required unless --run-fixtures is used")
        report = {
            "schema_version": "strategium.task_cost_checker_report.v0_1",
            "created_at_utc": utc_now(),
            "result": validate_set(Path(args.budget_card), Path(args.cost_receipt), Path(args.kpd_delta)),
        }
        report["verdict"] = report["result"]["verdict"]

    if args.out:
        write_json(Path(args.out), report)
    else:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    if report.get("verdict") == "PASS" or args.allow_block_exit_zero:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
