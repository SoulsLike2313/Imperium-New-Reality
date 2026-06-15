#!/usr/bin/env python3
"""Generate Officio boot acknowledgement artifact for NewGen tasks."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc


def _required_paths_exist(paths: List[Path]) -> bool:
    return all(path.exists() for path in paths)


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_ack(
    boot_root: Path,
    task_id: str,
    task_type: str,
    taskpack_path: Path,
    preflight_json_path: Path,
    role_id: str,
    scope: str,
) -> Dict[str, Any]:
    template_path = boot_root / "officio_ack_template_v0_1.json"
    role_contract_path = boot_root / "officio_role_contract_v0_1.json"
    execution_contract_path = boot_root / "servitor_execution_contract_v0_1.md"
    language_contract_path = boot_root / "owner_facing_language_contract_v0_1.md"
    final_response_contract_path = boot_root / "final_response_contract_v0_1.md"

    template = _load_json(template_path)
    role_contract = _load_json(role_contract_path)
    preflight = _load_json(preflight_json_path)

    preflight_status = str(preflight.get("status", "UNKNOWN"))
    preflight_ok = preflight_status == "PASS"

    officio_contracts_ok = _required_paths_exist(
        [
            role_contract_path,
            execution_contract_path,
            language_contract_path,
            final_response_contract_path,
        ]
    )

    agents_md_path = boot_root.parent.parent / "AGENTS.md"

    boot_route_ack = {
        "read_newgen_agents_md": agents_md_path.exists(),
        "run_doctrinarium_preflight": preflight_ok,
        "read_officio_boot_contracts": officio_contracts_ok,
        "read_taskpack": taskpack_path.exists(),
        "publish_boot_ack": True,
    }

    all_ack = all(boot_route_ack.values())
    ack_verdict = "PASS" if all_ack else "STOP"

    payload: Dict[str, Any] = dict(template)
    payload["task_id"] = task_id
    payload["task_type"] = task_type
    payload["role_id"] = role_id
    payload["scope"] = scope
    payload["boot_route_ack"] = boot_route_ack
    payload["input_paths"] = {
        "agents_md": str(agents_md_path.relative_to(boot_root.parent.parent.parent)),
        "doctrinarium_preflight_json": str(preflight_json_path),
        "officio_role_contract": str(role_contract_path.relative_to(boot_root.parent.parent.parent)),
        "taskpack_path": str(taskpack_path),
    }
    payload["active_gates"] = [
        gate.get("gate_id")
        for gate in preflight.get("active_gates", [])
        if isinstance(gate, dict) and isinstance(gate.get("gate_id"), str)
    ]
    payload["required_declarations"] = [
        declaration.get("declaration_id")
        for declaration in preflight.get("required_declarations", [])
        if isinstance(declaration, dict) and isinstance(declaration.get("declaration_id"), str)
    ]
    payload["ack_verdict"] = ack_verdict
    payload["generated_at_utc"] = _now_utc()
    payload["checks"] = {
        "preflight_status": preflight_status,
        "taskpack_exists": taskpack_path.exists(),
        "officio_contracts_complete": officio_contracts_ok,
        "role_contract_schema": role_contract.get("schema_id"),
    }

    if "not_proven_boundary" not in payload:
        payload["not_proven_boundary"] = role_contract.get("not_proven_boundary", [])

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Officio boot ack for NewGen task start.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-type", required=True)
    parser.add_argument("--taskpack-path", required=True)
    parser.add_argument("--preflight-json", required=True)
    parser.add_argument("--output", help="Optional output file path for generated ack JSON")
    parser.add_argument("--role-id", default="VM3_SERVITOR")
    parser.add_argument("--scope", default="IMPERIUM_NEW_GENERATION only")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    boot_root = Path(__file__).resolve().parents[1]

    try:
        payload = build_ack(
            boot_root=boot_root,
            task_id=args.task_id,
            task_type=args.task_type,
            taskpack_path=Path(args.taskpack_path),
            preflight_json_path=Path(args.preflight_json),
            role_id=args.role_id,
            scope=args.scope,
        )
    except RuntimeError as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}, ensure_ascii=False, indent=2))
        return 2

    if args.compact:
        output = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    else:
        output = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
