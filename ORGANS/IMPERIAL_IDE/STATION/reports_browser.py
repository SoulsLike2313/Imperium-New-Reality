from __future__ import annotations

from pathlib import Path
from typing import Any

from path_actions import actions_for_path


def _category(name: str) -> str:
    upper = name.upper()
    if "SAFETY" in upper:
        return "safety"
    if "VALIDATION" in upper or "SMOKE" in upper:
        return "validation"
    if "GIT" in upper or "CLOSURE" in upper or "PUSH" in upper:
        return "git"
    if "ADMISSION" in upper:
        return "admission"
    if "RESOLVER" in upper:
        return "resolver"
    if "LAUNCH" in upper or "HANDOFF" in upper:
        return "launch"
    if "LIFECYCLE" in upper:
        return "lifecycle"
    return "report"


def _summary(path: Path) -> str:
    if path.suffix.lower() not in {".md", ".txt"}:
        return path.name
    try:
        for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            clean = line.strip(" #\t")
            if clean:
                return clean[:240]
    except OSError:
        pass
    return path.name


def list_reports(repo_root: Path, limit: int = 30) -> dict[str, Any]:
    repo = repo_root.resolve()
    root = repo / "REPORTS"
    if not root.is_dir():
        return {"status": "BLOCKED", "reason": "reports_root_not_found", "latest": []}
    dirs = [item for item in root.iterdir() if item.is_dir()]
    dirs.sort(key=lambda item: (item.stat().st_mtime, item.name), reverse=True)
    latest: list[dict[str, Any]] = []
    for directory in dirs[:limit]:
        files = [item for item in directory.iterdir() if item.is_file()]
        files.sort(key=lambda item: (item.stat().st_mtime, item.name), reverse=True)
        latest.append({
            "name": directory.name,
            "path": directory.relative_to(repo).as_posix(),
            "category": _category(directory.name),
            "file_count": len(files),
            "summary": _summary(files[0]) if files else directory.name,
            "latest_files": [
                {
                    "name": file.name,
                    "path": file.relative_to(repo).as_posix(),
                    "category": _category(file.name),
                    "summary": _summary(file),
                }
                for file in files[:8]
            ],
            "path_actions": actions_for_path(repo, directory),
        })
    return {
        "status": "PASS_WITH_WARNINGS" if latest else "BLOCKED",
        "filters": ["safety", "validation", "git", "admission", "resolver", "launch", "lifecycle"],
        "latest": latest,
        "raw_json_available": True,
        "open_or_copy_actions_available": True,
    }
