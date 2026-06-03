from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1"
DEFAULT_SCOPE_ROOT = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCOPE_PACKS/V0_1"
REQUIRED_SCOPE_FILES: dict[str, str] = {
    "code_quality_task": "scope_code_quality_task_v0_1.json",
    "json_schema_validation_task": "scope_json_schema_validation_task_v0_1.json",
    "mechanicus_tool_validation_task": "scope_mechanicus_tool_validation_task_v0_1.json",
    "repo_hygiene_task": "scope_repo_hygiene_task_v0_1.json",
    "taskpack_generation_task": "scope_taskpack_generation_task_v0_1.json",
    "controlled_tool_provision_task": "scope_controlled_tool_provision_task_v0_1.json",
}
REQUIRED_FIELDS: tuple[str, ...] = (
    "scope_id",
    "version",
    "purpose",
    "target_task_types",
    "required_gates",
    "required_receipts",
    "forbidden_actions",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def consume_scope_packs(task_id: str, repo_root: Path, scope_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    consumed_rows: list[dict[str, Any]] = []
    missing_scope_packs: list[str] = []
    all_required_gates: set[str] = set()
    all_forbidden_actions: set[str] = set()
    all_required_receipts: set[str] = set()

    for scope_id, filename in REQUIRED_SCOPE_FILES.items():
        scope_path = scope_root / filename
        if not scope_path.exists():
            missing_scope_packs.append(filename)
            errors.append(f"missing_scope_pack:{filename}")
            continue

        try:
            payload = load_json(scope_path)
        except Exception as exc:
            errors.append(f"invalid_json:{filename}:{exc}")
            continue

        if not isinstance(payload, dict):
            errors.append(f"invalid_payload_type:{filename}")
            continue

        missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
        if missing_fields:
            errors.append(f"missing_required_fields:{filename}:{','.join(missing_fields)}")

        scope_id_in_file = str(payload.get("scope_id", "")).strip()
        if scope_id_in_file and scope_id_in_file != scope_id:
            warnings.append(f"scope_id_mismatch:{filename}:{scope_id_in_file}!=expected:{scope_id}")

        required_gates = normalize_list(payload.get("required_gates"))
        required_receipts = normalize_list(payload.get("required_receipts"))
        forbidden_actions = normalize_list(payload.get("forbidden_actions"))
        canon_allowed = normalize_list(payload.get("canon_allowed"))
        sandbox_allowed = normalize_list(payload.get("sandbox_allowed"))

        all_required_gates.update(required_gates)
        all_required_receipts.update(required_receipts)
        all_forbidden_actions.update(forbidden_actions)

        consumed_rows.append(
            {
                "scope_id": scope_id,
                "scope_file": scope_path.relative_to(repo_root).as_posix(),
                "exists": True,
                "required_gates_count": len(required_gates),
                "required_receipts_count": len(required_receipts),
                "forbidden_actions_count": len(forbidden_actions),
                "canon_allowed_count": len(canon_allowed),
                "sandbox_allowed_count": len(sandbox_allowed),
            }
        )

    verdict = "PASS"
    if errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARN"

    return {
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "checker": "mechanicus_scope_pack_consumer_v0_1.py",
        "scope_root": scope_root.relative_to(repo_root).as_posix(),
        "required_scope_files": REQUIRED_SCOPE_FILES,
        "consumed_scope_packs": consumed_rows,
        "missing_scope_packs": missing_scope_packs,
        "summary": {
            "required_scope_count": len(REQUIRED_SCOPE_FILES),
            "consumed_scope_count": len(consumed_rows),
            "missing_scope_count": len(missing_scope_packs),
            "required_gate_union_count": len(all_required_gates),
            "forbidden_action_union_count": len(all_forbidden_actions),
            "required_receipt_union_count": len(all_required_receipts),
            "required_gate_union": sorted(all_required_gates),
            "forbidden_action_union": sorted(all_forbidden_actions)[:100],
        },
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consume Mechanicus scope packs and emit compact gate-ready report.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--scope-root", default=DEFAULT_SCOPE_ROOT)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    scope_root = (repo_root / args.scope_root).resolve()

    payload = consume_scope_packs(task_id=args.task_id, repo_root=repo_root, scope_root=scope_root)
    output = Path(args.output)
    if not output.is_absolute():
        output = (repo_root / output).resolve()
    write_json(output, payload)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": payload["verdict"],
                "consumed_scope_count": payload["summary"]["consumed_scope_count"],
                "missing_scope_count": payload["summary"]["missing_scope_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if payload["verdict"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
