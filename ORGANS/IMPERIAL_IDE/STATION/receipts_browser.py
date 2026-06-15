from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reports_browser import _category
from path_actions import actions_for_path


def _receipt_summary(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeError):
        return path.name
    for key in ("status", "verdict", "result", "receipt_type", "task_id"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return f"{key}: {value}"[:240]
    return path.name


def list_receipts(repo_root: Path, limit: int = 50) -> dict[str, Any]:
    repo = repo_root.resolve()
    roots = [repo / "REPORTS", repo / "ORGANS" / "IMPERIAL_IDE" / "STATION" / "receipts"]
    found: list[Path] = []
    for root in roots:
        if root.is_dir():
            found.extend(path for path in root.rglob("*.json") if "receipt" in path.name.lower())
    unique = list({path.resolve(): path for path in found}.values())
    unique.sort(key=lambda item: (item.stat().st_mtime, item.as_posix()), reverse=True)
    latest = [
        {
            "name": path.name,
            "path": path.relative_to(repo).as_posix(),
            "category": _category(path.name),
            "summary": _receipt_summary(path),
            "path_actions": actions_for_path(repo, path),
        }
        for path in unique[:limit]
    ]
    return {
        "status": "PASS_WITH_WARNINGS" if latest else "BLOCKED",
        "filters": ["safety", "validation", "git", "admission", "resolver", "launch", "lifecycle"],
        "count": len(unique),
        "latest": latest,
        "raw_json_available": True,
        "open_or_copy_actions_available": True,
    }
