from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from dirty_classifier import classify_dirty


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    return completed.stdout.strip()


def plan_git_closure(repo_root: Path, read_only_new_dirty: bool | None = None) -> dict[str, Any]:
    repo = repo_root.resolve()
    dirty = classify_dirty(repo)
    items = dirty.get("classified_items", [])
    stage_candidates = [item for item in items if item.get("stage_allowed")]
    do_not_stage = [item for item in items if not item.get("stage_allowed")]
    stage_paths = [item["path"] for item in stage_candidates]
    recommended_commands = []
    if stage_paths:
        quoted = " ".join("'" + path.replace("'", "''") + "'" for path in stage_paths)
        recommended_commands.append(f"git add -- {quoted}")
        recommended_commands.append("git diff --cached --check")
        recommended_commands.append("git commit -m \"<TASK_ID> validated outputs\"")
        recommended_commands.append("git push origin master")
    else:
        recommended_commands.append("No staging recommended until validated in-scope outputs exist.")
    return {
        "status": dirty.get("status", "PASS_WITH_WARNINGS"),
        "branch": _git(repo, "branch", "--show-current"),
        "head": _git(repo, "rev-parse", "HEAD"),
        "origin_master": _git(repo, "rev-parse", "origin/master"),
        "head_equals_origin_master": _git(repo, "rev-parse", "HEAD") == _git(repo, "rev-parse", "origin/master"),
        "dirty_count": dirty.get("dirty_count", 0),
        "classified_dirty_table": items,
        "push_allowed_state": dirty.get("push_allowed_state"),
        "recommended_commands": recommended_commands,
        "what_not_to_stage": do_not_stage,
        "what_can_be_staged_after_validation": stage_candidates,
        "read_only_commands_caused_new_dirt": read_only_new_dirty,
        "recommended_action": dirty.get("recommended_action"),
    }
