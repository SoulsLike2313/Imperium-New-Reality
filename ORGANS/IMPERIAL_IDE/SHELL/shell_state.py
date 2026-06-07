from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID = "TASK-NEWREALITY-IMPERIAL-IDE-OPERATIONAL-USABILITY-STATION-AGENTIC-WORKFLOW-PC-V0_2"


def find_repo_root(start: Path | None = None) -> Path:
    cursor = (start or Path.cwd()).resolve()
    for candidate in (cursor, *cursor.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / "ORGANS").exists():
            return candidate
    raise RuntimeError("repo_root_not_found")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


class RepositoryState:
    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or find_repo_root()).resolve()

    def rel(self, relative: str) -> Path:
        return self.repo_root / relative

    def read_json(self, relative: str) -> Any:
        return load_json(self.rel(relative))

    def git(self, *args: str) -> dict[str, Any]:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return {
            "args": list(args),
            "exit_code": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }

    def governance(self) -> dict[str, Any]:
        path = "ORGANS/_CORE_GOVERNANCE/GOVERNANCE_INDEX.json"
        try:
            data = self.read_json(path)
            return {"found": True, "path": path, "data": data}
        except Exception as exc:
            return {"found": False, "path": path, "error": str(exc)}

    def current_task(self) -> dict[str, Any]:
        path = "ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json"
        try:
            data = self.read_json(path)
            return {"found": True, "path": path, "data": data}
        except Exception as exc:
            return {"found": False, "path": path, "error": str(exc)}

    def registered_tasks(self, limit: int = 50) -> dict[str, Any]:
        relative = "ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED"
        root = self.rel(relative)
        if not root.exists():
            return {"found": False, "path": relative, "tasks": [], "count": 0}
        tasks = sorted((item.name for item in root.iterdir() if item.is_dir()), reverse=True)
        return {"found": True, "path": relative, "tasks": tasks[:limit], "count": len(tasks)}

    def reports(self, limit: int = 50) -> dict[str, Any]:
        relative = "REPORTS"
        root = self.rel(relative)
        if not root.exists():
            return {"found": False, "path": relative, "reports": [], "count": 0}
        items = [item for item in root.iterdir() if item.is_dir()]
        items.sort(key=lambda item: (item.stat().st_mtime, item.name), reverse=True)
        reports = [{"name": item.name, "path": item.relative_to(self.repo_root).as_posix()} for item in items[:limit]]
        return {"found": True, "path": relative, "reports": reports, "count": len(items)}

    def latest_report(self) -> dict[str, Any]:
        listing = self.reports(limit=1)
        latest = listing["reports"][0] if listing.get("reports") else None
        if latest:
            report_path = self.rel(latest["path"])
            latest["file_count"] = sum(1 for item in report_path.rglob("*") if item.is_file())
        return {"found": latest is not None, "latest_report": latest}

    def receipts(self, limit: int = 100) -> dict[str, Any]:
        roots = [self.rel("REPORTS"), self.rel("ORGANS/IMPERIAL_IDE/RECEIPTS")]
        found: list[dict[str, Any]] = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*receipt*.json"):
                if path.is_file():
                    found.append({
                        "path": path.relative_to(self.repo_root).as_posix(),
                        "modified": path.stat().st_mtime,
                    })
        found.sort(key=lambda item: (item["modified"], item["path"]), reverse=True)
        for item in found:
            item.pop("modified", None)
        return {"found": bool(found), "receipts": found[:limit], "count": len(found)}

    def shell_json_paths(self) -> list[str]:
        return [
            "ORGANS/IMPERIAL_IDE/SHELL/panel_registry.json",
            "ORGANS/IMPERIAL_IDE/SHELL/command_palette.json",
            "ORGANS/IMPERIAL_IDE/SHELL/shell_command_receipt.schema.json",
            "ORGANS/IMPERIAL_IDE/SHELL/shell_command_history.json",
            "ORGANS/IMPERIAL_IDE/WORKSPACE/workspace_state.json",
            "ORGANS/IMPERIAL_IDE/EXTENSIONS/extension_registry.json",
            "ORGANS/IMPERIAL_IDE/EXTENSIONS/example_mechanicus_extension.json",
            "ORGANS/IMPERIAL_IDE/WORKBENCH/INTEGRATION_STATUS.json",
            "ORGANS/IMPERIAL_IDE/WARP/INTEGRATION_STATUS.json",
            "ORGANS/IMPERIAL_IDE/METAOS/INTEGRATION_STATUS.json",
            "ORGANS/IMPERIAL_IDE/OPS/INTEGRATION_STATUS.json",
            "ORGANS/IMPERIAL_IDE/OPS/TEMPLATES/task_templates.json",
            "ORGANS/IMPERIAL_IDE/STATION/station_panels.json",
            "ORGANS/IMPERIAL_IDE/STATION/operational_state.schema.json",
            "ORGANS/IMPERIAL_IDE/STATION/lifecycle_stage.schema.json",
            "ORGANS/IMPERIAL_IDE/STATION/lifecycle_state.json",
            "ORGANS/IMPERIAL_IDE/AGENTS/agent_registry.json",
            "ORGANS/IMPERIAL_IDE/AGENTS/servitor_roster.json",
            "ORGANS/IMPERIAL_IDE/AGENTS/agent_card.schema.json",
            "ORGANS/IMPERIAL_IDE/AGENTS/agent_status.schema.json",
            "ORGANS/IMPERIAL_IDE/AGENTS/agent_runtime_state.json",
            "ORGANS/MECHANICUS/IDE_BRIDGE/workbench_warp_metaos_bridge_policy.json",
            "ORGANS/ADMINISTRATUM/BUNDLE_GATES/bundle_gate_policy.json",
            "ORGANS/MECHANICUS/REGISTRY/tool_registry.json",
            "ORGANS/MECHANICUS/REGISTRY/capability_registry.json",
            "ORGANS/MECHANICUS/REGISTRY/command_policy.json",
        ]

    def validate_json(self) -> dict[str, Any]:
        parsed: list[str] = []
        missing: list[str] = []
        invalid: list[dict[str, str]] = []
        for relative in self.shell_json_paths():
            path = self.rel(relative)
            if not path.exists():
                missing.append(relative)
                continue
            try:
                load_json(path)
                parsed.append(relative)
            except Exception as exc:
                invalid.append({"path": relative, "error": str(exc)})
        status = "PASS" if not missing and not invalid else "BLOCKED"
        return {"status": status, "parsed": parsed, "missing": missing, "invalid": invalid}

    def git_status(self) -> dict[str, Any]:
        branch = self.git("status", "-sb")
        porcelain = self.git("status", "--porcelain=v1")
        head = self.git("rev-parse", "HEAD")
        origin = self.git("rev-parse", "origin/master")
        return {
            "branch": branch,
            "porcelain": porcelain,
            "head": head.get("stdout"),
            "origin_master": origin.get("stdout"),
            "head_equals_origin_master": bool(head.get("stdout")) and head.get("stdout") == origin.get("stdout"),
        }

    def overview(self) -> dict[str, Any]:
        governance = self.governance()
        current = self.current_task()
        tasks = self.registered_tasks(limit=10)
        reports = self.reports(limit=10)
        return {
            "repo_root": self.repo_root.as_posix(),
            "governance_status": governance.get("data", {}).get("status") if governance.get("found") else "MISSING",
            "current_task": current.get("data", {}).get("task_id") if current.get("found") else None,
            "registered_task_count": tasks.get("count", 0),
            "report_count": reports.get("count", 0),
            "full_gui_implemented": False,
        }
