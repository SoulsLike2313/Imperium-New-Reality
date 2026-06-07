from __future__ import annotations

from pathlib import Path
from typing import Any


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def normalize_repo_path(repo_root: Path, path_value: str | Path) -> dict[str, Any]:
    repo = repo_root.resolve()
    raw = Path(path_value)
    path = raw if raw.is_absolute() else repo / raw
    path = path.resolve()
    inside_repo = False
    relative = path.as_posix()
    try:
        relative = path.relative_to(repo).as_posix()
        inside_repo = True
    except ValueError:
        pass
    return {
        "path": path.as_posix(),
        "relative_path": relative,
        "inside_repo": inside_repo,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
    }


def actions_for_path(repo_root: Path, path_value: str | Path) -> dict[str, Any]:
    info = normalize_repo_path(repo_root, path_value)
    literal = _ps_quote(info["path"])
    return {
        **info,
        "copy_path_command": f"Set-Clipboard -Value {literal}",
        "open_path_command": f"Invoke-Item -LiteralPath {literal}",
        "show_json_command": (
            "python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py show-json "
            + _ps_quote(info["relative_path"])
            if info["inside_repo"]
            else ""
        ),
        "action_mode": "COPY_READY_COMMANDS_ONLY",
        "executed": False,
    }


def actions_for_paths(repo_root: Path, paths: list[str | Path]) -> list[dict[str, Any]]:
    return [actions_for_path(repo_root, path) for path in paths]
