from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from path_actions import actions_for_path


def _safe_path(repo_root: Path, path_value: str | Path) -> Path:
    repo = repo_root.resolve()
    path = Path(path_value)
    resolved = (path if path.is_absolute() else repo / path).resolve()
    resolved.relative_to(repo)
    return resolved


def view_json_path(repo_root: Path, path_value: str | Path) -> dict[str, Any]:
    try:
        path = _safe_path(repo_root, path_value)
    except ValueError:
        return {
            "status": "BLOCKED",
            "reason": "path_outside_repo",
            "path": str(path_value),
            "raw_json_available": False,
        }
    if not path.is_file():
        return {
            "status": "BLOCKED",
            "reason": "json_file_not_found",
            "path": path.as_posix(),
            "raw_json_available": False,
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        return {
            "status": "BLOCKED",
            "reason": "json_parse_failed",
            "path": path.as_posix(),
            "error": str(exc),
            "raw_json_available": False,
        }
    raw_json = json.dumps(data, ensure_ascii=False, indent=2)
    return {
        "status": "PASS",
        "path": path.relative_to(repo_root.resolve()).as_posix(),
        "raw_json_available": True,
        "data": data,
        "raw_json": raw_json,
        "line_count": len(raw_json.splitlines()),
        "path_actions": actions_for_path(repo_root, path),
    }


def view_payload(title: str, payload: Any) -> dict[str, Any]:
    raw_json = json.dumps(payload, ensure_ascii=False, indent=2)
    return {
        "status": "PASS",
        "title": title,
        "raw_json_available": True,
        "data": payload,
        "raw_json": raw_json,
        "line_count": len(raw_json.splitlines()),
    }
