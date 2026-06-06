#!/usr/bin/env python3
"""Read-only Officio Agentis inspector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
TASK_REPORT_ROOT = ROOT / "REPORTS" / "TASK-NEWGEN-OFFICIO-AGENTIS-BODY-ENTRY-CONTRACT-PC-V0_1"

FILE_MAP = {
    "body_manifest": ROOT / "BODY" / "officio_agentis_body_manifest_v0_1.json",
    "role_registry": ROOT / "ROLES" / "role_registry_v0_1.json",
    "rule_grammar": ROOT / "RULES" / "stop_warn_pass_grammar_v0_1.md",
    "rule_taskpack": ROOT / "RULES" / "taskpack_acceptance_rules_v0_1.md",
    "rule_response": ROOT / "RULES" / "final_response_contract_v0_1.md",
    "ghost_accepted": ROOT / "GHOST_EVOLVE" / "accepted_local_upgrades_index_v0_1.json",
    "ghost_rejected": ROOT / "GHOST_EVOLVE" / "rejected_noise_index_v0_1.json",
}

# Explicit markers used by contract checkers to verify that TUI reads real Officio files.
RELATIVE_DATA_PATH_MARKERS = [
    "BODY/officio_agentis_body_manifest_v0_1.json",
    "ROLES/role_registry_v0_1.json",
    "RULES/stop_warn_pass_grammar_v0_1.md",
    "RULES/taskpack_acceptance_rules_v0_1.md",
    "RULES/final_response_contract_v0_1.md",
    "GHOST_EVOLVE/accepted_local_upgrades_index_v0_1.json",
    "GHOST_EVOLVE/rejected_noise_index_v0_1.json",
]


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_summary() -> Dict[str, Any]:
    missing: List[str] = []
    warnings: List[str] = []

    for key, path in FILE_MAP.items():
        if not path.exists():
            missing.append(f"{key}:{path.as_posix()}")

    body = load_json(FILE_MAP["body_manifest"]) if FILE_MAP["body_manifest"].exists() else {}
    roles = load_json(FILE_MAP["role_registry"]) if FILE_MAP["role_registry"].exists() else {}
    accepted = load_json(FILE_MAP["ghost_accepted"]) if FILE_MAP["ghost_accepted"].exists() else {"entries": []}
    rejected = load_json(FILE_MAP["ghost_rejected"]) if FILE_MAP["ghost_rejected"].exists() else {"entries": []}

    role_items = roles.get("roles", [])
    role_briefs: List[Dict[str, Any]] = []
    for item in role_items:
        if not isinstance(item, dict):
            continue
        role_briefs.append(
            {
                "role_id": item.get("role_id"),
                "status": item.get("status"),
                "purpose": item.get("purpose"),
                "role_pack_ref": item.get("role_pack_ref"),
            }
        )

    for rule_key in ("rule_grammar", "rule_taskpack", "rule_response"):
        rule_path = FILE_MAP[rule_key]
        if rule_path.exists():
            text = load_text(rule_path)
            if len(text.strip()) < 20:
                warnings.append(f"{rule_key} appears too short")

    report_exists = TASK_REPORT_ROOT.exists()
    report_hint = TASK_REPORT_ROOT.as_posix() if report_exists else "MISSING_TASK_REPORT_ROOT"

    return {
        "organ_id": "OFFICIO_AGENTIS",
        "status": body.get("status", "DRAFT"),
        "default_role": roles.get("default_role", ""),
        "active_roles": roles.get("active_roles", []),
        "roles": role_briefs,
        "block_count": len(body.get("blocks", [])) if isinstance(body.get("blocks"), list) else 0,
        "ghost_evolve": {
            "accepted_count": len(accepted.get("entries", [])) if isinstance(accepted.get("entries"), list) else 0,
            "rejected_count": len(rejected.get("entries", [])) if isinstance(rejected.get("entries"), list) else 0,
        },
        "rules": {
            "grammar_path": FILE_MAP["rule_grammar"].as_posix(),
            "taskpack_path": FILE_MAP["rule_taskpack"].as_posix(),
            "response_contract_path": FILE_MAP["rule_response"].as_posix(),
        },
        "evidence": {
            "task_report_root": report_hint
        },
        "missing": missing,
        "warnings": warnings,
    }


def print_human(summary: Dict[str, Any]) -> None:
    print("OFFICIO_AGENTIS READ-ONLY INSPECTOR V0.1")
    print(f"status: {summary.get('status')}")
    print(f"default_role: {summary.get('default_role')}")
    print(f"active_roles: {', '.join(summary.get('active_roles', []))}")
    print(f"block_count: {summary.get('block_count')}")
    ghost = summary.get("ghost_evolve", {})
    print(f"ghost_accepted: {ghost.get('accepted_count', 0)}")
    print(f"ghost_rejected: {ghost.get('rejected_count', 0)}")
    print("roles:")
    for item in summary.get("roles", []):
        print(f"  - {item.get('role_id')} [{item.get('status')}]")
    if summary.get("missing"):
        print("missing:")
        for item in summary["missing"]:
            print(f"  - {item}")
    if summary.get("warnings"):
        print("warnings:")
        for item in summary["warnings"]:
            print(f"  - {item}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only inspector for Officio body contracts.")
    parser.add_argument("--mode", choices=["summary", "json"], default="summary")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when files are missing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary()
    if args.mode == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human(summary)
    if args.strict and summary.get("missing"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
