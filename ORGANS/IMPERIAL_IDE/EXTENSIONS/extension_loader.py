from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REQUIRED = {
    "extension_id", "name", "status", "owner_organ", "panels", "commands",
    "tool_permissions", "risk_class", "receipts_required", "validation_required",
}
FORBIDDEN_PERMISSIONS = {"unrestricted_execution", "arbitrary_shell", "real_shell", "remote_route_vm2", "remote_route_vm3"}


def _load(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _validate_record(record: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED - set(record))
    permissions = set(record.get("permissions", [])) | set(record.get("tool_permissions", []))
    forbidden = sorted(permissions & FORBIDDEN_PERMISSIONS)
    unrestricted = bool(record.get("unrestricted_execution"))
    status = "PASS" if not missing and not forbidden and not unrestricted else "BLOCKED"
    return {
        "extension_id": record.get("extension_id"),
        "status": status,
        "missing_fields": missing,
        "forbidden_permissions": forbidden,
        "unrestricted_execution": unrestricted,
    }


def validate_extensions(repo_root: Path) -> dict[str, Any]:
    registry_path = repo_root / "ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_registry.json"
    example_path = repo_root / "ORGANS/IMPERIAL_IDE/EXTENSIONS/example_mechanicus_extension.json"
    try:
        registry = _load(registry_path)
        example = _load(example_path)
    except Exception as exc:
        return {"status": "BLOCKED", "error": str(exc)}
    records = list(registry.get("extensions", [])) + [example]
    validations = [_validate_record(record) for record in records]
    blocked = [item for item in validations if item["status"] == "BLOCKED"]
    return {
        "status": "PASS" if not blocked else "BLOCKED",
        "extension_registry_loaded": True,
        "example_extension_loaded": True,
        "extension_count": len(records),
        "validations": validations,
        "unrestricted_execution_permissions_found": sum(
            len(item["forbidden_permissions"]) + int(item["unrestricted_execution"]) for item in validations
        ),
    }
