#!/usr/bin/env python3
"""Doctrinarium preflight resolver for NewGen read-first gate spine v0.1."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc


def _require_keys(data: Dict[str, Any], keys: List[str], label: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise RuntimeError(f"{label} is missing keys: {', '.join(missing)}")


def _dedupe_preserve_order(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    result: List[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def build_preflight(task_type: str, spine_root: Path) -> Dict[str, Any]:
    declaration_index_path = spine_root / "declaration_index_v0_1.json"
    gate_registry_path = spine_root / "gate_registry_v0_1.json"

    declaration_index = _load_json(declaration_index_path)
    gate_registry = _load_json(gate_registry_path)

    _require_keys(
        declaration_index,
        ["declarations", "task_type_read_sets", "not_proven_boundary"],
        "declaration_index_v0_1.json",
    )
    _require_keys(
        gate_registry,
        ["gates", "task_type_gate_sets", "forbidden_pattern_catalog", "global_pass_criteria", "global_fail_criteria"],
        "gate_registry_v0_1.json",
    )

    task_read_sets = declaration_index["task_type_read_sets"]
    task_gate_sets = gate_registry["task_type_gate_sets"]

    if task_type not in task_read_sets or task_type not in task_gate_sets:
        supported = sorted(set(task_read_sets.keys()) & set(task_gate_sets.keys()))
        raise RuntimeError(
            f"Unsupported task_type '{task_type}'. Supported task types: {', '.join(supported)}"
        )

    declaration_by_id: Dict[str, Dict[str, Any]] = {
        item["declaration_id"]: item
        for item in declaration_index["declarations"]
        if isinstance(item, dict) and "declaration_id" in item
    }
    gate_by_id: Dict[str, Dict[str, Any]] = {
        item["gate_id"]: item
        for item in gate_registry["gates"]
        if isinstance(item, dict) and "gate_id" in item
    }
    pattern_by_id: Dict[str, Dict[str, Any]] = {
        item["pattern_id"]: item
        for item in gate_registry["forbidden_pattern_catalog"]
        if isinstance(item, dict) and "pattern_id" in item
    }

    required_declaration_ids: List[str] = list(task_read_sets[task_type])
    active_gate_ids: List[str] = list(task_gate_sets[task_type])

    required_declarations: List[Dict[str, Any]] = []
    missing_declaration_paths: List[str] = []
    for declaration_id in required_declaration_ids:
        declaration = declaration_by_id.get(declaration_id)
        if declaration is None:
            raise RuntimeError(
                f"Declaration id '{declaration_id}' is referenced by task_type '{task_type}' but not defined"
            )

        primary_path = declaration.get("primary_path")
        supporting_paths = declaration.get("supporting_paths", [])

        if isinstance(primary_path, str) and not (spine_root.parent.parent.parent / primary_path).exists():
            missing_declaration_paths.append(primary_path)

        for supporting_path in supporting_paths:
            if isinstance(supporting_path, str) and not (spine_root.parent.parent.parent / supporting_path).exists():
                missing_declaration_paths.append(supporting_path)

        required_declarations.append(
            {
                "declaration_id": declaration_id,
                "display_name": declaration.get("display_name"),
                "status": declaration.get("status"),
                "primary_path": primary_path,
                "supporting_paths": supporting_paths,
                "source_notes": declaration.get("source_notes"),
            }
        )

    active_gates: List[Dict[str, Any]] = []
    forbidden_pattern_ids: List[str] = []
    pass_criteria: List[str] = list(gate_registry.get("global_pass_criteria", []))
    fail_criteria: List[str] = list(gate_registry.get("global_fail_criteria", []))
    evidence_required: List[str] = ["preflight_output_json"]

    for gate_id in active_gate_ids:
        gate = gate_by_id.get(gate_id)
        if gate is None:
            raise RuntimeError(
                f"Gate id '{gate_id}' is referenced by task_type '{task_type}' but not defined"
            )

        gate_forbidden = gate.get("forbidden_patterns", [])
        if isinstance(gate_forbidden, list):
            forbidden_pattern_ids.extend(
                [pattern for pattern in gate_forbidden if isinstance(pattern, str)]
            )

        gate_pass = gate.get("pass_criteria", [])
        if isinstance(gate_pass, list):
            pass_criteria.extend([item for item in gate_pass if isinstance(item, str)])

        gate_fail = gate.get("fail_criteria", [])
        if isinstance(gate_fail, list):
            fail_criteria.extend([item for item in gate_fail if isinstance(item, str)])

        gate_evidence = gate.get("evidence_required", [])
        if isinstance(gate_evidence, list):
            evidence_required.extend([item for item in gate_evidence if isinstance(item, str)])

        active_gates.append(
            {
                "gate_id": gate_id,
                "severity": gate.get("severity"),
                "source_declarations": gate.get("source_declarations", []),
            }
        )

    forbidden_pattern_ids = _dedupe_preserve_order(forbidden_pattern_ids)
    forbidden_patterns: List[Dict[str, Any]] = []
    for pattern_id in forbidden_pattern_ids:
        pattern = pattern_by_id.get(pattern_id)
        forbidden_patterns.append(
            {
                "pattern_id": pattern_id,
                "pattern": None if pattern is None else pattern.get("pattern"),
                "block_code": None if pattern is None else pattern.get("block_code"),
            }
        )

    status = "PASS"
    if missing_declaration_paths:
        status = "BLOCK_MISSING_DECLARATION_PATHS"

    result: Dict[str, Any] = {
        "schema_id": "newgen_doctrinarium_preflight_output_v0_1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "task_type": task_type,
        "status": status,
        "required_declarations": required_declarations,
        "active_gates": active_gates,
        "forbidden_patterns": forbidden_patterns,
        "pass_criteria": _dedupe_preserve_order(pass_criteria),
        "fail_criteria": _dedupe_preserve_order(fail_criteria),
        "evidence_required": _dedupe_preserve_order(evidence_required),
        "not_proven_boundary": declaration_index.get("not_proven_boundary", []),
        "missing_declaration_paths": _dedupe_preserve_order(missing_declaration_paths),
        "source_files": {
            "declaration_index": str(declaration_index_path),
            "gate_registry": str(gate_registry_path),
        },
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve Doctrinarium read-first requirements for a task type."
    )
    parser.add_argument(
        "--task-type",
        required=True,
        help="Task type to resolve (for example: core_task, visual_cockpit)",
    )
    parser.add_argument(
        "--output",
        help="Optional output path for JSON result.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON instead of pretty JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spine_root = Path(__file__).resolve().parents[1]

    try:
        payload = build_preflight(task_type=args.task_type, spine_root=spine_root)
    except RuntimeError as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}, ensure_ascii=False, indent=2))
        return 2

    if args.compact:
        json_text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    else:
        json_text = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_text + "\n", encoding="utf-8")

    print(json_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
