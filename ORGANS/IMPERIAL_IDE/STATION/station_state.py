from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ALLOWED_STATES = {
    "LIVE",
    "DRY_RUN",
    "BLOCKED",
    "CANDIDATE",
    "ACTIVE",
    "WARNING",
    "FAILED",
    "UNKNOWN",
}


def find_repo_root(start: Path | None = None) -> Path:
    cursor = (start or Path.cwd()).resolve()
    for candidate in (cursor, *cursor.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / "ORGANS").is_dir():
            return candidate
    raise RuntimeError("repo_root_not_found")


def read_json(path: Path, default: Any = None) -> Any:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            return json.load(handle)
    except (OSError, ValueError, json.JSONDecodeError):
        return default


def git(repo_root: Path, *args: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    return {
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _latest_dirs(root: Path, limit: int = 10) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    items = [item for item in root.iterdir() if item.is_dir()]
    items.sort(key=lambda item: (item.stat().st_mtime, item.name), reverse=True)
    return [
        {
            "name": item.name,
            "path": item.as_posix(),
            "modified": item.stat().st_mtime,
        }
        for item in items[:limit]
    ]


def _latest_files(root: Path, patterns: tuple[str, ...], limit: int = 20) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    found: list[Path] = []
    for pattern in patterns:
        found.extend(path for path in root.rglob(pattern) if path.is_file())
    unique = list({path.resolve(): path for path in found}.values())
    unique.sort(key=lambda path: (path.stat().st_mtime, path.as_posix()), reverse=True)
    return [
        {
            "name": path.name,
            "path": path.as_posix(),
            "modified": path.stat().st_mtime,
        }
        for path in unique[:limit]
    ]


class StationState:
    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or find_repo_root()).resolve()

    def rel(self, relative: str) -> Path:
        return self.repo_root / relative

    def component(self, relative: str, live_statuses: set[str] | None = None) -> dict[str, Any]:
        data = read_json(self.rel(relative), {})
        raw = str(data.get("status", "UNKNOWN"))
        live_statuses = live_statuses or {"ACTIVE", "CANON_ACTIVE"}
        state = "ACTIVE" if raw in live_statuses or raw.startswith("ACTIVE") else "CANDIDATE"
        if not data:
            state = "UNKNOWN"
        return {"state": state, "path": relative, "data": data}

    def git_state(self) -> dict[str, Any]:
        branch = git(self.repo_root, "rev-parse", "--abbrev-ref", "HEAD")
        head = git(self.repo_root, "rev-parse", "HEAD")
        origin = git(self.repo_root, "rev-parse", "origin/master")
        porcelain = git(self.repo_root, "status", "--porcelain=v1")
        dirty = [line for line in porcelain["stdout"].splitlines() if line.strip()]
        return {
            "state": "WARNING" if dirty else "LIVE",
            "branch": branch["stdout"],
            "head": head["stdout"],
            "origin_master": origin["stdout"],
            "head_equals_origin_master": bool(head["stdout"]) and head["stdout"] == origin["stdout"],
            "dirty": dirty,
            "dirty_count": len(dirty),
        }

    def task_state(self) -> dict[str, Any]:
        current_path = self.rel("ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json")
        current = read_json(current_path, {})
        registered = self.rel("ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED")
        tasks = sorted((item.name for item in registered.iterdir() if item.is_dir()), reverse=True) if registered.is_dir() else []
        return {
            "state": "LIVE" if current else "UNKNOWN",
            "current": current,
            "registered_count": len(tasks),
            "latest_registered": tasks[:10],
        }

    def agent_state(self) -> dict[str, Any]:
        registry_path = self.rel("ORGANS/IMPERIAL_IDE/AGENTS/agent_registry.json")
        runtime_path = self.rel("ORGANS/IMPERIAL_IDE/AGENTS/agent_runtime_state.json")
        registry = read_json(registry_path, {"agents": []})
        runtime = read_json(runtime_path, {"agents": []})
        return {
            "state": "ACTIVE" if registry.get("agents") else "UNKNOWN",
            "registry_path": registry_path.relative_to(self.repo_root).as_posix(),
            "agent_count": len(registry.get("agents", [])),
            "agents": registry.get("agents", []),
            "runtime": runtime,
        }

    def safety_state(self) -> dict[str, Any]:
        policy = read_json(self.rel("ORGANS/MECHANICUS/REGISTRY/command_policy.json"), {})
        ops = read_json(self.rel("ORGANS/IMPERIAL_IDE/OPS/INTEGRATION_STATUS.json"), {})
        staged_result = git(self.repo_root, "diff", "--cached", "--name-only")
        staged_paths = [line.strip().replace("\\", "/") for line in staged_result["stdout"].splitlines() if line.strip()]
        runtime_markers = (
            "ORGANS/IMPERIAL_IDE/STATION/generated_taskpacks/",
            "ORGANS/IMPERIAL_IDE/STATION/receipts/runtime/",
            "ORGANS/IMPERIAL_IDE/WARP/RUNTIME/",
            "ORGANS/IMPERIAL_IDE/OPS/STAGING/",
        )
        secret_names = re.compile(r"(?i)(^|/)(\.env|.*credential.*|.*secret.*|.*private[_-]?key.*)$")
        runtime_paths_staged = [path for path in staged_paths if path.startswith(runtime_markers)]
        secret_paths_staged = [path for path in staged_paths if secret_names.search(path)]
        push_allowed = not runtime_paths_staged and not secret_paths_staged
        return {
            "state": "ACTIVE",
            "real_servitor_execution_enabled": False,
            "live_llm_backend_enabled": False,
            "unsafe_shell_available": False,
            "arbitrary_shell_allowed": bool(policy.get("arbitrary_shell_execution_allowed", False)),
            "dry_run_default": bool(policy.get("dry_run_required_by_default", True)),
            "live_registration_enabled": True,
            "live_registration_scope": "LOCAL_PC_VALIDATED_GENERATED_TASKPACK_ONLY",
            "unknown_tool_blocked": "execute_unregistered_tool" in policy.get("blocked_actions", []),
            "secrets_staged": bool(secret_paths_staged),
            "secret_paths_staged": secret_paths_staged,
            "runtime_paths_staged": bool(runtime_paths_staged),
            "staged_runtime_paths": runtime_paths_staged,
            "vm2_action": False,
            "vm3_action": False,
            "destructive_cleanup": False,
            "push_allowed_state": "GATED_BY_VALIDATION_SCOPE_SECRET_AND_TASK_POLICY" if push_allowed else "BLOCKED_BY_STAGED_SAFETY_FINDING",
            "ops_status": ops.get("status", "UNKNOWN"),
            "result": "PASS_WITH_WARNINGS" if push_allowed else "BLOCKED",
        }

    def reports_state(self) -> dict[str, Any]:
        root = self.rel("REPORTS")
        summaries = _latest_files(root, ("*OWNER_SUMMARY*.md", "*owner_summary*.md"), 15)
        reports = _latest_dirs(root, 15)
        return {"state": "LIVE" if reports else "UNKNOWN", "latest": reports, "owner_summaries": summaries}

    def receipts_state(self) -> dict[str, Any]:
        roots = [self.rel("REPORTS"), self.rel("ORGANS/IMPERIAL_IDE/RECEIPTS")]
        found: list[dict[str, Any]] = []
        for root in roots:
            found.extend(_latest_files(root, ("*receipt*.json", "*RECEIPT*.json"), 100))
        found.sort(key=lambda item: (item["modified"], item["path"]), reverse=True)
        return {"state": "LIVE" if found else "UNKNOWN", "latest": found[:20], "count": len(found)}

    def snapshot(self) -> dict[str, Any]:
        git_state = self.git_state()
        return {
            "schema_version": "imperial_ide.operational_state.v0_2",
            "state": "ACTIVE",
            "repo": {"state": "LIVE", "root": self.repo_root.as_posix()},
            "git_closure": git_state,
            "task": self.task_state(),
            "agents": self.agent_state(),
            "safety": self.safety_state(),
            "ops": self.component("ORGANS/IMPERIAL_IDE/OPS/INTEGRATION_STATUS.json"),
            "warp": self.component("ORGANS/IMPERIAL_IDE/WARP/INTEGRATION_STATUS.json"),
            "metaos": self.component("ORGANS/IMPERIAL_IDE/METAOS/INTEGRATION_STATUS.json"),
            "mechanicus": self.component("ORGANS/MECHANICUS/REGISTRY/command_policy.json"),
            "astronomicon": {
                "state": "LIVE",
                "inbox": "ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED",
                "registration_skill": "ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/astronomicon_taskpack_registration_skill_v0_1.py",
                "skill_found": self.rel("ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/astronomicon_taskpack_registration_skill_v0_1.py").is_file(),
            },
            "reports": self.reports_state(),
            "receipts": self.receipts_state(),
        }
