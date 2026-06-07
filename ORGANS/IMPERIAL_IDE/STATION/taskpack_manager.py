from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from path_actions import actions_for_path

REQUIRED_ROOT_FILES = [
    "MANIFEST.json",
    "TASK_SPEC.md",
    "ACCEPTANCE_GATES.md",
    "OUTPUT_REQUIREMENTS.md",
    "TASK_ROUTE_MANIFEST_TEMPLATE.json",
    "TASK_START_ACK_TEMPLATE.json",
]


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return default


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generated_root(repo_root: Path) -> Path:
    return repo_root / "ORGANS" / "IMPERIAL_IDE" / "STATION" / "generated_taskpacks"


def _taskpack_dirs(repo_root: Path) -> list[Path]:
    root = generated_root(repo_root)
    if not root.is_dir():
        return []
    dirs = [item for item in root.iterdir() if item.is_dir()]
    dirs.sort(key=lambda item: (item.stat().st_mtime, item.name), reverse=True)
    return dirs


def _receipt_for(repo_root: Path, task_id: str) -> Path | None:
    receipt = (
        repo_root
        / "ORGANS"
        / "IMPERIAL_IDE"
        / "STATION"
        / "receipts"
        / "runtime"
        / f"{task_id}_registration_receipt.json"
    )
    return receipt if receipt.is_file() else None


def inspect_taskpack(repo_root: Path, taskpack_id: str = "") -> dict[str, Any]:
    repo = repo_root.resolve()
    dirs = _taskpack_dirs(repo)
    selected = None
    if taskpack_id:
        selected = next((item for item in dirs if item.name == taskpack_id), None)
    elif dirs:
        selected = dirs[0]
    if selected is None:
        return {
            "status": "BLOCKED",
            "reason": "generated_taskpack_not_found",
            "taskpack_id": taskpack_id,
            "generated_taskpacks_root": generated_root(repo).as_posix(),
        }
    extracted = selected / "EXTRACTED"
    manifest = _read_json(extracted / "MANIFEST.json", {})
    zip_path = selected / "TASKPACK.zip"
    root_files = sorted(path.name for path in extracted.iterdir() if path.is_file()) if extracted.is_dir() else []
    missing = [name for name in REQUIRED_ROOT_FILES if name not in root_files]
    receipt = _receipt_for(repo, selected.name)
    validation_status = "PASS" if zip_path.is_file() and not missing else "BLOCKED"
    return {
        "status": "PASS_WITH_WARNINGS" if validation_status == "PASS" else "BLOCKED",
        "taskpack_id": selected.name,
        "title": manifest.get("title", ""),
        "taskpack_path": selected.relative_to(repo).as_posix(),
        "taskpack_zip_path": zip_path.relative_to(repo).as_posix() if zip_path.is_file() else "",
        "latest_taskpack_sha256": _sha256(zip_path) if zip_path.is_file() else "",
        "extracted_path": extracted.relative_to(repo).as_posix(),
        "extracted_root_files_found": root_files,
        "missing_required_root_files": missing,
        "validation_status": validation_status,
        "dry_run_registration_status": "RECEIPT_FOUND" if receipt else "NOT_REGISTERED_BY_STATION_RUNTIME",
        "dry_run_registration_receipt": receipt.relative_to(repo).as_posix() if receipt else "",
        "live_promotion_available": validation_status == "PASS",
        "open_or_copy_actions_available": True,
        "path_actions": actions_for_path(repo, selected),
    }


def list_taskpacks(repo_root: Path, limit: int = 20) -> dict[str, Any]:
    repo = repo_root.resolve()
    items = [inspect_taskpack(repo, item.name) for item in _taskpack_dirs(repo)[:limit]]
    latest = items[0] if items else None
    return {
        "status": "PASS_WITH_WARNINGS" if items else "BLOCKED",
        "generated_taskpacks_found": len(items),
        "generated_taskpacks_root": generated_root(repo).relative_to(repo).as_posix(),
        "latest_taskpack_path": latest.get("taskpack_path", "") if latest else "",
        "latest_taskpack_sha256": latest.get("latest_taskpack_sha256", "") if latest else "",
        "items": items,
        "open_or_copy_actions_available": True,
    }


def validate_taskpack(repo_root: Path, taskpack_id: str = "") -> dict[str, Any]:
    inspected = inspect_taskpack(repo_root, taskpack_id)
    if inspected.get("status") == "BLOCKED":
        return inspected
    blockers = list(inspected.get("missing_required_root_files", []))
    return {
        **inspected,
        "status": "PASS" if not blockers else "BLOCKED",
        "blockers": blockers,
        "required_root_files": REQUIRED_ROOT_FILES,
        "dry_run_registration_visible": True,
        "live_promotion_availability_visible": True,
    }
