from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
ASTRONOMICON_ROOT = HERE.parents[1]
DEFAULT_SCHEMA_PATH = ASTRONOMICON_ROOT / "TASK_ESSENCE" / "task_essence_schema_v0_1.json"
DEFAULT_FIXTURE_PATH = ASTRONOMICON_ROOT / "FIXTURES" / "task_essence_examples_v0_1.json"

REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "task_id",
    "task_summary",
    "primary_organ",
    "support_organs",
    "out_of_scope",
    "success_criteria",
    "risks_and_gates",
    "stop_conditions",
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _as_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field} must contain non-empty strings")
        out.append(item)
    return out


def validate_task_essence(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing required field: {field}")

    if errors:
        return errors

    if payload.get("schema_version") != "astronomicon.task_essence.v0_1":
        errors.append("schema_version must equal astronomicon.task_essence.v0_1")

    task_id = payload.get("task_id")
    if not isinstance(task_id, str) or not task_id.startswith("TASK-"):
        errors.append("task_id must be a string starting with TASK-")

    task_summary = payload.get("task_summary")
    if not isinstance(task_summary, str) or len(task_summary.strip()) < 8:
        errors.append("task_summary must be a string of at least 8 chars")

    primary_organ = payload.get("primary_organ")
    if not isinstance(primary_organ, str) or not primary_organ.strip():
        errors.append("primary_organ must be a non-empty string")

    for field in ("support_organs", "out_of_scope", "success_criteria", "stop_conditions"):
        try:
            _as_string_list(payload.get(field), field)
        except ValueError as exc:
            errors.append(str(exc))

    risks = payload.get("risks_and_gates")
    if not isinstance(risks, list) or not risks:
        errors.append("risks_and_gates must be a non-empty list")
    else:
        for idx, item in enumerate(risks):
            if not isinstance(item, dict):
                errors.append(f"risks_and_gates[{idx}] must be an object")
                continue
            gate_id = item.get("gate_id")
            risk = item.get("risk")
            if not isinstance(gate_id, str) or not gate_id.strip():
                errors.append(f"risks_and_gates[{idx}].gate_id must be non-empty string")
            if not isinstance(risk, str) or not risk.strip():
                errors.append(f"risks_and_gates[{idx}].risk must be non-empty string")

    return errors


def run_checker(schema_path: Path, fixture_path: Path) -> dict[str, Any]:
    _load_json(schema_path)
    fixture_payload = _load_json(fixture_path)

    examples = fixture_payload.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError("Fixture must contain non-empty examples list")

    example_results: list[dict[str, Any]] = []
    failed_examples = 0

    for raw in examples:
        if not isinstance(raw, dict):
            raise ValueError("Each example must be an object")

        example_id = str(raw.get("example_id", "UNKNOWN_EXAMPLE"))
        expected_verdict = str(raw.get("expected_verdict", "PASS"))
        payload = raw.get("payload")
        if not isinstance(payload, dict):
            raise ValueError(f"Example {example_id} payload must be an object")

        errors = validate_task_essence(payload)
        actual_verdict = "PASS" if not errors else "BLOCK"

        if expected_verdict == "PASS" and actual_verdict != "PASS":
            failed_examples += 1

        example_results.append(
            {
                "example_id": example_id,
                "expected_verdict": expected_verdict,
                "actual_verdict": actual_verdict,
                "errors": errors,
            }
        )

    overall_verdict = "PASS" if failed_examples == 0 else "BLOCK"

    return {
        "schema_version": "astronomicon.task_essence_checker_report.v0_1",
        "checker": "astronomicon_task_essence_checker_v0_1.py",
        "schema_path": str(schema_path),
        "fixture_path": str(fixture_path),
        "checked_examples": len(example_results),
        "failed_examples": failed_examples,
        "verdict": overall_verdict,
        "example_results": example_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Astronomicon task essence fixtures.")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA_PATH))
    parser.add_argument("--fixtures", default=str(DEFAULT_FIXTURE_PATH))
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_checker(Path(args.schema), Path(args.fixtures))

    if args.output:
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
