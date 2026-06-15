#!/usr/bin/env python3
"""Checker for Officio role registry and body block identity presence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
ROLE_REGISTRY_PATH = ROOT / "ROLES" / "role_registry_v0_1.json"
BODY_MANIFEST_PATH = ROOT / "BODY" / "officio_agentis_body_manifest_v0_1.json"

REQUIRED_ROLES = {
    "LOGOS_PRIME",
    "SERVITOR_PRIME",
    "LOGOS_SPECULUM",
    "ADVISOR_SERVITOR",
}

REQUIRED_BLOCK_IDS = {
    "OFFICIO_AGENTIS_BODY_V0_1",
    "OFFICIO_SERVITOR_ENTRY_CONTRACT_V0_1",
    "OFFICIO_ROLE_REGISTRY_V0_1",
    "OFFICIO_AGENT_CONTROL_POLICY_V0_1",
    "OFFICIO_GHOST_EVOLVE_CONTRACT_V0_1",
    "OFFICIO_STOP_WARN_PASS_GRAMMAR_V0_1",
    "OFFICIO_TASKPACK_ACCEPTANCE_GATE_V0_1",
    "OFFICIO_FINAL_RESPONSE_CONTRACT_V0_1",
    "OFFICIO_TUI_READONLY_INSPECTOR_V0_1",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    if not ROLE_REGISTRY_PATH.exists():
        errors.append(f"Missing file: {ROLE_REGISTRY_PATH.as_posix()}")
        role_registry: Dict[str, Any] = {}
    else:
        role_registry = load_json(ROLE_REGISTRY_PATH)

    if not BODY_MANIFEST_PATH.exists():
        errors.append(f"Missing file: {BODY_MANIFEST_PATH.as_posix()}")
        body_manifest: Dict[str, Any] = {}
    else:
        body_manifest = load_json(BODY_MANIFEST_PATH)

    active_roles = set(role_registry.get("active_roles", []))
    missing_roles = sorted(REQUIRED_ROLES - active_roles)
    if missing_roles:
        errors.append(f"Missing required active roles: {', '.join(missing_roles)}")

    role_items = role_registry.get("roles", [])
    role_ids = {str(item.get("role_id", "")).strip() for item in role_items if isinstance(item, dict)}
    missing_role_definitions = sorted(REQUIRED_ROLES - role_ids)
    if missing_role_definitions:
        errors.append(f"Missing role definitions: {', '.join(missing_role_definitions)}")

    blocks = body_manifest.get("blocks", [])
    block_ids = {str(item.get("block_id", "")).strip() for item in blocks if isinstance(item, dict)}
    missing_blocks = sorted(REQUIRED_BLOCK_IDS - block_ids)
    if missing_blocks:
        errors.append(f"Missing required block ids: {', '.join(missing_blocks)}")

    default_role = str(role_registry.get("default_role", "")).strip()
    if default_role and default_role not in role_ids:
        warnings.append(f"default_role points to unknown role: {default_role}")
    if not default_role:
        warnings.append("default_role is empty")

    status = "PASS"
    if errors:
        status = "FAIL"
    elif warnings:
        status = "WARN"

    return {
        "checker_id": "officio_role_registry_checker_v0_1",
        "generated_at_utc": utc_now(),
        "status": status,
        "inputs": {
            "role_registry_path": ROLE_REGISTRY_PATH.as_posix(),
            "body_manifest_path": BODY_MANIFEST_PATH.as_posix(),
        },
        "required_roles": sorted(REQUIRED_ROLES),
        "required_block_ids": sorted(REQUIRED_BLOCK_IDS),
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "active_roles_count": len(active_roles),
            "role_definition_count": len(role_items) if isinstance(role_items, list) else 0,
            "block_count": len(blocks) if isinstance(blocks, list) else 0,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Officio role registry and block identities.")
    parser.add_argument("--output", help="Optional output report JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
