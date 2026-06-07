from __future__ import annotations

from pathlib import Path
from typing import Any

IGNORED_RUNTIME_PREFIXES = [
    "ORGANS/IMPERIAL_IDE/STATION/receipts/runtime/",
    "ORGANS/IMPERIAL_IDE/STATION/generated_taskpacks/",
    "ORGANS/IMPERIAL_IDE/STATION/runtime/",
    "ORGANS/IMPERIAL_IDE/STATION/RUNTIME/",
    "ORGANS/IMPERIAL_IDE/OPS/STAGING/",
    "ORGANS/IMPERIAL_IDE/OPS/RUNTIME/",
    "ORGANS/IMPERIAL_IDE/OPS/runtime/",
    "ORGANS/IMPERIAL_IDE/WARP/RUNTIME/",
    "ORGANS/IMPERIAL_IDE/WARP/runtime/",
]


def normalize_repo_path(repo_root: Path, path: str | Path) -> str:
    repo = repo_root.resolve()
    resolved = (path if isinstance(path, Path) else Path(path))
    resolved = resolved if resolved.is_absolute() else repo / resolved
    try:
        return resolved.resolve().relative_to(repo).as_posix()
    except ValueError:
        return resolved.resolve().as_posix()


def is_runtime_receipt_path(repo_root: Path, path: str | Path) -> bool:
    relative = normalize_repo_path(repo_root, path)
    return any(relative.startswith(prefix) for prefix in IGNORED_RUNTIME_PREFIXES)


def policy_summary(repo_root: Path) -> dict[str, Any]:
    return {
        "status": "PASS_WITH_WARNINGS",
        "ignored_runtime_prefixes": IGNORED_RUNTIME_PREFIXES,
        "runtime_receipts_tracked": False,
        "runtime_receipts_gitignored": True,
        "report_receipts_tracked_only_for_explicit_report_finalization": True,
        "repo_root": repo_root.resolve().as_posix(),
    }
