#!/usr/bin/env python3
"""Export Officio role packs and generate taskpack gate blocks."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

TASK_ID_DEFAULT = "TASK-NEWGEN-OFFICIO-LANGUAGE-ROLE-GATE-GHOST-EVOLVE-PC-V0_1"
OFFICIO_ROOT = Path(__file__).resolve().parents[1]
ROLE_PACKS_DIR = OFFICIO_ROOT / "ROLE_PACKS"
CONTRACTS_DIR = OFFICIO_ROOT / "CONTRACTS"
TEMPLATES_DIR = OFFICIO_ROOT / "TEMPLATES"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any], compact: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if compact:
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    else:
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")


def discover_role_packs() -> List[Path]:
    if not ROLE_PACKS_DIR.exists():
        return []
    return sorted(ROLE_PACKS_DIR.glob("*.json"))


def resolve_role_pack(paths: List[Path], role_id: str) -> Path:
    normalized = role_id.strip().upper()
    for path in paths:
        payload = load_json(path)
        if str(payload.get("role_id", "")).upper() == normalized:
            return path
    raise RuntimeError(f"Role pack not found for role_id={role_id}")


def render_gate_block(
    *,
    task_id: str,
    role_pack: Dict[str, Any],
    allowed_paths: List[str],
    forbidden_paths: List[str],
    gatepack_path: str,
    gatepack_sha256: str,
) -> str:
    required_acks = role_pack.get("required_acks", [])
    stop_conditions = role_pack.get("stop_conditions", [])
    forbidden_actions = role_pack.get("forbidden_actions", [])

    required_acks_text = ", ".join(str(item) for item in required_acks)
    stop_lines = "\n".join(f"- {item}" for item in stop_conditions)
    forbidden_lines = "\n".join(f"- {item}" for item in forbidden_actions)

    return (
        f"# OFFICIO GATE BLOCK ({role_pack.get('role_id', 'UNKNOWN')})\n\n"
        f"GATE_ACK:\n"
        f"- task_id: {task_id}\n"
        f"- role_id: {role_pack.get('role_id', '')}\n"
        f"- owner_facing_language: {role_pack.get('owner_facing_language', '')}\n"
        f"- technical_artifact_language: {role_pack.get('technical_artifact_language', '')}\n"
        f"- gatepack_path: {gatepack_path}\n"
        f"- gatepack_sha256: {gatepack_sha256}\n"
        f"- required_acks: {required_acks_text}\n"
        f"- allowed_write_paths: {', '.join(allowed_paths)}\n"
        f"- forbidden_paths: {', '.join(forbidden_paths)}\n"
        f"- verdict: PASS\n\n"
        "STOP_CONDITIONS:\n"
        f"{stop_lines}\n\n"
        "FORBIDDEN_ACTIONS:\n"
        f"{forbidden_lines}\n\n"
        "OFFICIO_REFERENCES:\n"
        f"- {CONTRACTS_DIR.as_posix()}/OFFICIO_LANGUAGE_GATE_CONTRACT_V0_1.md\n"
        f"- {CONTRACTS_DIR.as_posix()}/OFFICIO_ROLE_ACK_CONTRACT_V0_1.md\n"
        f"- {CONTRACTS_DIR.as_posix()}/OFFICIO_RESPONSE_CONTRACT_V0_1.md\n"
        f"- {CONTRACTS_DIR.as_posix()}/OFFICIO_STOP_CONDITIONS_V0_1.md\n"
        f"- {CONTRACTS_DIR.as_posix()}/OFFICIO_FORBIDDEN_BEHAVIORS_V0_1.md\n"
        f"- {TEMPLATES_DIR.as_posix()}/TASKPACK_OFFICIO_GATE_TEMPLATE_V0_1.md\n"
    )


def export_role_pack(
    *,
    role_pack_path: Path,
    output_dir: Path,
    task_id: str,
    gatepack_path: str,
    gatepack_sha256: str,
    allowed_paths: List[str],
    forbidden_paths: List[str],
    compact: bool,
) -> Dict[str, Any]:
    role_pack = load_json(role_pack_path)
    role_id = str(role_pack.get("role_id", "UNKNOWN")).strip()
    role_slug = role_id.lower()

    role_export_path = output_dir / f"{role_slug}_role_pack_export_v0_1.json"
    gate_block_path = output_dir / f"{role_slug}_taskpack_gate_block_v0_1.md"

    write_json(role_export_path, role_pack, compact=compact)
    gate_block = render_gate_block(
        task_id=task_id,
        role_pack=role_pack,
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        gatepack_path=gatepack_path,
        gatepack_sha256=gatepack_sha256,
    )
    gate_block_path.parent.mkdir(parents=True, exist_ok=True)
    gate_block_path.write_text(gate_block, encoding="utf-8")

    return {
        "role_id": role_id,
        "source_role_pack": str(role_pack_path),
        "role_pack_export_path": str(role_export_path),
        "taskpack_gate_block_path": str(gate_block_path),
        "required_acks": role_pack.get("required_acks", []),
        "stop_conditions_count": len(role_pack.get("stop_conditions", [])),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Officio role packs with taskpack gate blocks.")
    parser.add_argument("--output-dir", required=True, help="Directory for exported role packs and gate blocks.")
    parser.add_argument("--report", help="Optional JSON report output path.")
    parser.add_argument("--role-id", help="If provided, export only this role_id.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--gatepack-path", default="TASKPACK_UNSPECIFIED")
    parser.add_argument("--gatepack-sha256", default="SHA256_UNSPECIFIED")
    parser.add_argument(
        "--allowed-path",
        action="append",
        default=["IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/**"],
        help="Allowed write path entries for gate block (repeatable).",
    )
    parser.add_argument(
        "--forbidden-path",
        action="append",
        default=[
            "SANCTUM/**",
            "src/**",
            "IMPERIUM_TEST_VERSION/**",
        ],
        help="Forbidden path entries for gate block (repeatable).",
    )
    parser.add_argument("--compact", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    report_path = Path(args.report) if args.report else None
    role_pack_paths = discover_role_packs()
    if not role_pack_paths:
        raise SystemExit("No role packs found under IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/ROLE_PACKS")

    if args.role_id:
        role_pack_paths = [resolve_role_pack(role_pack_paths, args.role_id)]
        export_scope = "single_role"
    else:
        export_scope = "all_roles"

    exports: List[Dict[str, Any]] = []
    for role_pack_path in role_pack_paths:
        item = export_role_pack(
            role_pack_path=role_pack_path,
            output_dir=output_dir,
            task_id=args.task_id,
            gatepack_path=args.gatepack_path,
            gatepack_sha256=args.gatepack_sha256,
            allowed_paths=args.allowed_path,
            forbidden_paths=args.forbidden_path,
            compact=args.compact,
        )
        exports.append(item)

    report: Dict[str, Any] = {
        "task_id": args.task_id,
        "status": "PASS",
        "generated_at_utc": utc_now(),
        "export_scope": export_scope,
        "exports": exports,
        "notes": [
            "Exporter mirrors role pack content and emits a reusable taskpack gate block per role.",
            "Gate block is contract-first and does not claim full autonomous enforcement.",
        ],
    }

    if report_path:
        write_json(report_path, report, compact=args.compact)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
