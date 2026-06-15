from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ORGAN_AGENT_COMMON.root_resolution import default_runs_path  # noqa: E402
from tool_registry_reader import build_organ_tool_view, default_tool_index_path
try:
    from operator_shell_widgets import (
        activity_panel,
        bottom_event_panel,
        command_palette_panel,
        mission_panel,
        raw_detail_panel,
        tool_registry_panel,
        top_status_panel,
    )

    HAVE_OPERATOR_WIDGETS = True
except Exception:
    HAVE_OPERATOR_WIDGETS = False
    activity_panel = None  # type: ignore[assignment]
    bottom_event_panel = None  # type: ignore[assignment]
    command_palette_panel = None  # type: ignore[assignment]
    mission_panel = None  # type: ignore[assignment]
    raw_detail_panel = None  # type: ignore[assignment]
    tool_registry_panel = None  # type: ignore[assignment]
    top_status_panel = None  # type: ignore[assignment]

try:
    from textual_operator_shell import launch_textual_operator_shell, textual_runtime_available
except Exception:
    launch_textual_operator_shell = None  # type: ignore[assignment]

    def textual_runtime_available() -> bool:
        return False

try:
    from rich import box
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    HAVE_RICH = True
except Exception:
    HAVE_RICH = False
    box = None  # type: ignore[assignment]
    Console = None  # type: ignore[assignment]
    Layout = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]
    Text = None  # type: ignore[assignment]

TASK_ID_BASE_HALF = "TASK-20260519-ORGAN-AGENT-BASE-HALF-8-ORGANS-V0_1"
TASK_ID_IDENTITY_RICH = "TASK-20260519-ORGAN-AGENT-IDENTITY-HALF-RICH-SHELL-8-ORGANS-V0_1"
VISUAL_PASS_RICH = "PASS_RICH_OPERATOR_SHELL"
VISUAL_PASS_PLAIN = "PASS_PLAIN_OPERATOR_SHELL"
VISUAL_WARN_PLAIN_FALLBACK = "WARN_PLAIN_FALLBACK"
VISUAL_BLOCKED_NOT_IMPLEMENTED = "BLOCKED_SHELL_NOT_IMPLEMENTED"
VISUAL_FAIL_FAKE = "FAIL_FAKE_SHELL"
VISUAL_SHELL_VERSION = "v0.5"

SHELL_FUNCTION_KEY_MAP = {
    "f1": "status",
    "f2": "tools",
    "f3": "identity",
    "f4": "check",
    "f5": "where",
    "f6": "pack",
    "f7": "help",
}

BASE_COMMANDS = ["status", "check", "where", "identity", "tools", "pack", "shell", "help"]
BASE_REQUIRED_FILES = [
    "README.md",
    "AGENT_PROFILE.md",
    "agent_profile.json",
    "IDENTITY_BASELINE.md",
    "SHELL/SHELL_CONTRACT.md",
    "STATE/current_status.json",
    "REPORTS/base_half_check_report.json",
    "REPORTS/base_half_check_report.md",
    "EXAMPLES/README.md",
    "TESTS/README.md",
]
IDENTITY_REQUIRED_FILES = [
    "IDENTITY/IDENTITY_PROFILE.md",
    "IDENTITY/identity_profile.json",
    "IDENTITY/LORE_FUNCTIONS.md",
    "IDENTITY/lore_functions.json",
    "IDENTITY/DOMAIN_COMMANDS.md",
    "IDENTITY/domain_commands.json",
    "IDENTITY/SPECULUM_CHECKS.md",
]


@dataclass
class OrganConfig:
    organ_name: str
    organ_slug: str
    root: Path
    identity_summary: str
    domain_commands: Dict[str, str]
    domain_aliases: Dict[str, str] = field(default_factory=dict)

    @property
    def runtime_root(self) -> Path:
        runtime_base = os.environ.get("IMPERIUM_ORGAN_RUNTIME_ROOT")
        if runtime_base:
            base = Path(runtime_base)
        else:
            base = default_runs_path("COMMON_AGENT_CLI", "ORGAN_AGENT_IDENTITY_RICH_SHELL_RUNS", start=Path(__file__))
        return base / TASK_ID_IDENTITY_RICH / "ORGANS" / self.organ_name


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def _repo_root(start: Path) -> Path:
    current = start
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return start


def _git_info(repo_root: Path) -> Dict[str, Any]:
    def _run(*args: str) -> str:
        completed = subprocess.run(args, cwd=str(repo_root), capture_output=True, text=True)
        if completed.returncode != 0:
            return (completed.stderr or completed.stdout).strip()
        return completed.stdout.strip()

    return {
        "head": _run("git", "rev-parse", "HEAD"),
        "branch": _run("git", "branch", "--show-current"),
        "dirty": _run("git", "status", "--short"),
    }


def _visual_status() -> str:
    return VISUAL_PASS_RICH if HAVE_RICH else VISUAL_WARN_PLAIN_FALLBACK


def _renderer_mode() -> str:
    return "rich" if HAVE_RICH else "plain_fallback"


def _tool_registry_summary(config: OrganConfig) -> Dict[str, Any]:
    repo_root = _repo_root(config.root)
    try:
        view = build_organ_tool_view(organ_id=config.organ_name, index_path=default_tool_index_path(repo_root))
    except Exception as exc:
        return {
            "registry_source": str(default_tool_index_path(repo_root)),
            "registered_tool_count": 0,
            "available_tool_count": 0,
            "missing_tool_count": 0,
            "preview": [],
            "warnings": [f"tool_registry_summary_error:{exc}"],
        }

    relevant = view.get("relevant_tools", []) if isinstance(view.get("relevant_tools", []), list) else []
    available = view.get("available_tools", []) if isinstance(view.get("available_tools", []), list) else []
    missing = view.get("missing_tools", []) if isinstance(view.get("missing_tools", []), list) else []
    preview: List[str] = []
    for item in relevant[:6]:
        if isinstance(item, dict):
            tool_id = str(item.get("tool_id", "")).strip() or "UNKNOWN"
            status = str(item.get("availability_status", "")).strip() or "UNKNOWN"
            preview.append(f"{tool_id}:{status}")

    warnings: List[str] = []
    for warning in view.get("warnings", []) if isinstance(view.get("warnings", []), list) else []:
        warnings.append(str(warning))

    return {
        "registry_source": str(view.get("registry_source", default_tool_index_path(repo_root))),
        "registered_tool_count": len(relevant),
        "available_tool_count": len(available),
        "missing_tool_count": len(missing),
        "preview": preview,
        "warnings": warnings,
    }


def _all_supported_commands(config: OrganConfig) -> List[str]:
    return BASE_COMMANDS + list(config.domain_commands.keys())


def _canonical_domain_command(config: OrganConfig, token: str) -> Optional[str]:
    value = token.strip().lstrip("/").lower()
    if not value:
        return None
    if value in config.domain_commands:
        return value
    return config.domain_aliases.get(value)


def ensure_base_layout(config: OrganConfig) -> None:
    for rel in ["TOOLS", "LAUNCHERS", "SHELL", "STATE", "REPORTS", "RECEIPTS", "EXAMPLES", "TESTS", "IDENTITY"]:
        (config.root / rel).mkdir(parents=True, exist_ok=True)
    keep = config.root / "RECEIPTS" / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")


def _identity_required_rows(config: OrganConfig) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for rel in IDENTITY_REQUIRED_FILES:
        rows.append({"file": rel, "exists": (config.root / rel).exists()})
    return rows


def important_paths(config: OrganConfig) -> Dict[str, str]:
    return {
        "organ_root": str(config.root),
        "runner": str(config.root / "TOOLS" / f"{config.organ_slug}_agent_runner.py"),
        "launcher": str(config.root / "LAUNCHERS" / f"run_{config.organ_slug}_pc.ps1"),
        "identity_baseline_md": str(config.root / "IDENTITY_BASELINE.md"),
        "identity_profile_md": str(config.root / "IDENTITY" / "IDENTITY_PROFILE.md"),
        "identity_profile_json": str(config.root / "IDENTITY" / "identity_profile.json"),
        "lore_functions_json": str(config.root / "IDENTITY" / "lore_functions.json"),
        "domain_commands_json": str(config.root / "IDENTITY" / "domain_commands.json"),
        "profile_md": str(config.root / "AGENT_PROFILE.md"),
        "profile_json": str(config.root / "agent_profile.json"),
        "state_json": str(config.root / "STATE" / "current_status.json"),
        "check_json": str(config.root / "REPORTS" / "base_half_check_report.json"),
        "runtime_root": str(config.runtime_root),
    }


def _latest_receipt_path(config: OrganConfig) -> str:
    receipts = sorted(
        [p for p in (config.root / "RECEIPTS").glob("*.json") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return str(receipts[0]) if receipts else ""


def _latest_report_path(config: OrganConfig) -> str:
    report = config.root / "REPORTS" / "base_half_check_report.json"
    return str(report) if report.exists() else ""


def _shell_zone_payload(config: OrganConfig, warnings: List[str], latest_output: str = "Shell ready.") -> Dict[str, List[str]]:
    command_preview = ", ".join(_all_supported_commands(config))
    latest_report_path = _latest_report_path(config) or "none"
    latest_receipt_path = _latest_receipt_path(config) or "none"
    git = _git_info(_repo_root(config.root))
    renderer = _renderer_mode()
    tool_summary = _tool_registry_summary(config)
    merged_warnings = list(warnings) + list(tool_summary.get("warnings", []))
    primary_warning = merged_warnings[-1] if merged_warnings else "none"
    top = [
        f"organ: {config.organ_name}",
        f"organ_mission: {config.identity_summary}",
        f"backend_truth: head={git.get('head', '')} branch={git.get('branch', '')} dirty={'yes' if bool(git.get('dirty', '').strip()) else 'no'}",
        f"visual_status: {_visual_status()} | renderer: {renderer}",
    ]
    left = [
        "latest_output:",
        latest_output,
    ]
    right = [
        "active_command_list:",
        command_preview,
        "tool_registry:",
        f"path={tool_summary.get('registry_source', '')}",
        (
            "counts: registered="
            f"{tool_summary.get('registered_tool_count', 0)} "
            f"available={tool_summary.get('available_tool_count', 0)} "
            f"missing={tool_summary.get('missing_tool_count', 0)}"
        ),
        "tool_preview:",
        ", ".join(tool_summary.get("preview", [])) if tool_summary.get("preview") else "none",
    ]
    bottom = [
        f"latest_report_path: {latest_report_path}",
        f"latest_receipt_path: {latest_receipt_path}",
        f"warn_error_blocker: {primary_warning}",
    ]
    return {"top": top, "left": left, "right": right, "bottom": bottom}


def command_status(config: OrganConfig) -> Tuple[int, Path]:
    ensure_base_layout(config)
    repo = _repo_root(config.root)
    git = _git_info(repo)
    active_commands = _all_supported_commands(config)
    latest_report_path = _latest_report_path(config)
    latest_receipt_path = _latest_receipt_path(config)
    tool_summary = _tool_registry_summary(config)
    warning_code = VISUAL_WARN_PLAIN_FALLBACK if not HAVE_RICH else "none"
    if warning_code == "none" and tool_summary.get("warnings"):
        warning_code = str(tool_summary["warnings"][0])
    state_path = config.root / "STATE" / "current_status.json"
    payload: Dict[str, Any] = {
        "schema_version": "ORGAN_IDENTITY_RICH_STATUS_V0_1",
        "task_id": TASK_ID_IDENTITY_RICH,
        "base_half_task_id": TASK_ID_BASE_HALF,
        "organ": config.organ_name,
        "runner": f"{config.organ_slug}_agent_runner.py",
        "timestamp_utc": _utc_now(),
        "status": "READY",
        "visual_status": _visual_status(),
        "supported_commands": active_commands,
        "active_command_list": active_commands,
        "identity_summary": config.identity_summary,
        "paths": important_paths(config),
        "git": git,
        "backend_truth": {
            "head": git.get("head", ""),
            "branch": git.get("branch", ""),
            "dirty_state": "yes" if bool(git.get("dirty", "").strip()) else "no",
        },
        "latest_report_path": latest_report_path,
        "latest_receipt_path": latest_receipt_path,
        "tool_registry": tool_summary,
        "warn_error_blocker": warning_code,
        "renderer_status": {
            "renderer": _renderer_mode(),
            "rich_renderer_available": HAVE_RICH,
            "visual_status": _visual_status(),
            "fallback_reason": [] if HAVE_RICH else [VISUAL_WARN_PLAIN_FALLBACK],
        },
        "rich_renderer_available": HAVE_RICH,
    }
    if not HAVE_RICH:
        payload["warnings"] = [VISUAL_WARN_PLAIN_FALLBACK]
    _write_json(state_path, payload)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0, state_path


def _check_required_files(config: OrganConfig) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for rel in BASE_REQUIRED_FILES:
        rows.append({"file": rel, "exists": (config.root / rel).exists()})
    rows.extend(_identity_required_rows(config))
    runner = config.root / "TOOLS" / f"{config.organ_slug}_agent_runner.py"
    rows.append({"file": f"TOOLS/{config.organ_slug}_agent_runner.py", "exists": runner.exists()})
    launcher = config.root / "LAUNCHERS" / f"run_{config.organ_slug}_pc.ps1"
    rows.append({"file": f"LAUNCHERS/run_{config.organ_slug}_pc.ps1", "exists": launcher.exists()})
    return rows


def command_check(config: OrganConfig) -> Tuple[int, Path, Path]:
    ensure_base_layout(config)
    _, state_path = command_status(config)
    check_rows = _check_required_files(config)
    missing = [row["file"] for row in check_rows if not bool(row.get("exists"))]
    warnings = [VISUAL_WARN_PLAIN_FALLBACK] if not HAVE_RICH else []
    verdict = "PASS" if (not missing and not warnings) else "WARN"
    report = {
        "schema_version": "ORGAN_IDENTITY_RICH_CHECK_REPORT_V0_1",
        "task_id": TASK_ID_IDENTITY_RICH,
        "organ": config.organ_name,
        "timestamp_utc": _utc_now(),
        "verdict": verdict,
        "visual_status": _visual_status(),
        "supported_commands": _all_supported_commands(config),
        "state_file": str(state_path),
        "checks": check_rows,
        "missing": missing,
        "warnings": warnings,
        "notes": [
            "Identity Half + Rich Shell uses shared common CLI layer.",
            "Visual fallback must report WARN_PLAIN_FALLBACK if rich is unavailable.",
        ],
    }
    json_path = config.root / "REPORTS" / "base_half_check_report.json"
    md_path = config.root / "REPORTS" / "base_half_check_report.md"
    _write_json(json_path, report)

    lines = [
        f"# {config.organ_name} Identity Rich Shell Check Report",
        "",
        f"- task_id: `{TASK_ID_IDENTITY_RICH}`",
        f"- verdict: `{verdict}`",
        f"- visual_status: `{_visual_status()}`",
        f"- timestamp_utc: `{report['timestamp_utc']}`",
        "",
        "## Missing",
    ]
    if missing:
        lines.extend([f"- {item}" for item in missing])
    else:
        lines.append("- none")
    lines.extend(["", "## Commands", *[f"- {cmd}" for cmd in _all_supported_commands(config)], ""])
    if warnings:
        lines.extend(["## Warnings", *[f"- {warning}" for warning in warnings], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0, json_path, md_path


def command_where(config: OrganConfig) -> int:
    ensure_base_layout(config)
    payload = {"organ": config.organ_name, "paths": important_paths(config), "timestamp_utc": _utc_now()}
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


def command_identity(config: OrganConfig) -> int:
    ensure_base_layout(config)
    profile = _read_json(config.root / "agent_profile.json")
    if isinstance(profile, dict):
        allowed_statuses = {
            VISUAL_PASS_RICH,
            VISUAL_PASS_PLAIN,
            VISUAL_WARN_PLAIN_FALLBACK,
            VISUAL_BLOCKED_NOT_IMPLEMENTED,
            VISUAL_FAIL_FAKE,
        }
        profile_visual_status = str(profile.get("visual_status", "")).strip()
        if profile_visual_status and profile_visual_status not in allowed_statuses:
            profile["visual_status"] = _visual_status()
    payload = {
        "organ": config.organ_name,
        "summary": config.identity_summary,
        "profile": profile,
        "identity_profile": _read_json(config.root / "IDENTITY" / "identity_profile.json"),
        "lore_functions": _read_json(config.root / "IDENTITY" / "lore_functions.json"),
        "domain_commands": _read_json(config.root / "IDENTITY" / "domain_commands.json"),
        "identity_baseline_excerpt": _read_text(config.root / "IDENTITY_BASELINE.md")[:1200],
        "identity_profile_excerpt": _read_text(config.root / "IDENTITY" / "IDENTITY_PROFILE.md")[:1200],
        "timestamp_utc": _utc_now(),
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


def command_pack(config: OrganConfig) -> Tuple[int, Path]:
    ensure_base_layout(config)
    run_token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    pack_root = config.runtime_root / "PACKS" / f"run_{run_token}"
    pack_root.mkdir(parents=True, exist_ok=True)

    if not (config.root / "STATE" / "current_status.json").exists():
        command_status(config)
    if not (config.root / "REPORTS" / "base_half_check_report.json").exists():
        command_check(config)

    copies = [
        "AGENT_PROFILE.md",
        "agent_profile.json",
        "IDENTITY_BASELINE.md",
        "IDENTITY/IDENTITY_PROFILE.md",
        "IDENTITY/identity_profile.json",
        "IDENTITY/LORE_FUNCTIONS.md",
        "IDENTITY/lore_functions.json",
        "IDENTITY/DOMAIN_COMMANDS.md",
        "IDENTITY/domain_commands.json",
        "IDENTITY/SPECULUM_CHECKS.md",
        "STATE/current_status.json",
        "REPORTS/base_half_check_report.json",
        "REPORTS/base_half_check_report.md",
        "SHELL/SHELL_CONTRACT.md",
    ]
    copied: List[str] = []
    for rel in copies:
        src = config.root / Path(rel)
        if src.exists():
            dst = pack_root / Path(rel)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(rel)

    manifest = {
        "schema_version": "ORGAN_IDENTITY_RICH_PACK_V0_1",
        "task_id": TASK_ID_IDENTITY_RICH,
        "organ": config.organ_name,
        "pack_root": str(pack_root),
        "timestamp_utc": _utc_now(),
        "copied": copied,
        "commands": _all_supported_commands(config),
        "visual_status": _visual_status(),
    }
    _write_json(pack_root / "pack_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=True, indent=2))
    return 0, pack_root


def command_tools(config: OrganConfig) -> int:
    ensure_base_layout(config)
    repo_root = _repo_root(config.root)
    index_path = default_tool_index_path(repo_root)
    payload = build_organ_tool_view(organ_id=config.organ_name, index_path=index_path)
    payload["tool_registry_reader"] = str(Path(__file__).resolve().parent / "tool_registry_reader.py")
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    verdict = str(payload.get("verdict", "PASS"))
    return 0 if verdict in {"PASS", "WARN"} else 1


def _json_validity_report(config: OrganConfig) -> Dict[str, Any]:
    identity_dir = config.root / "IDENTITY"
    targets = [identity_dir / "identity_profile.json", identity_dir / "lore_functions.json", identity_dir / "domain_commands.json"]
    rows: List[Dict[str, Any]] = []
    for path in targets:
        ok = True
        error = ""
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                ok = False
                error = str(exc)
        else:
            ok = False
            error = "missing"
        rows.append({"path": str(path), "ok": ok, "error": error})
    failed = [row for row in rows if not row["ok"]]
    return {"checks": rows, "failed_count": len(failed)}


def _scope_drift(repo_root: Path) -> List[Dict[str, str]]:
    completed = subprocess.run(["git", "status", "--short"], cwd=str(repo_root), capture_output=True, text=True)
    lines = [line.rstrip() for line in completed.stdout.splitlines() if line.strip()]
    rows: List[Dict[str, str]] = []
    for line in lines:
        path = line[3:] if len(line) > 3 else line
        rows.append({"raw": line, "path": path})
    return rows


def _domain_output(config: OrganConfig, command: str) -> Dict[str, Any]:
    repo_root = _repo_root(config.root)
    domain_defs = _read_json(config.root / "IDENTITY" / "domain_commands.json")
    lore_defs = _read_json(config.root / "IDENTITY" / "lore_functions.json")
    description = config.domain_commands.get(command, "")
    raw_cmds = domain_defs.get("commands", {}) if isinstance(domain_defs, dict) else {}
    if isinstance(raw_cmds, dict):
        item = raw_cmds.get(command)
        if isinstance(item, dict):
            description = str(item.get("description", description))

    missing = [row["file"] for row in _identity_required_rows(config) if not row["exists"]]
    details: Dict[str, Any] = {
        "organ": config.organ_name,
        "command": command,
        "description": description,
        "identity_missing": missing,
        "git": _git_info(repo_root),
        "lore_function_count": len(lore_defs.get("functions", [])) if isinstance(lore_defs, dict) else 0,
    }
    warnings = [VISUAL_WARN_PLAIN_FALLBACK] if not HAVE_RICH else []

    if command == "fake-green-check":
        details["audit"] = {
            "check_report_exists": (config.root / "REPORTS" / "base_half_check_report.json").exists(),
            "identity_missing_count": len(missing),
            "status": "WARN" if missing else "PASS",
        }
    elif command == "scope-drift-check":
        drift = _scope_drift(repo_root)
        details["scope_drift"] = {"changed_paths_count": len(drift), "changed_paths_preview": drift[:20]}
    elif command == "hygiene-scan":
        details["hygiene"] = {"missing_count": len(missing), "missing": missing}
    elif command == "audit-claims":
        details["claims"] = {
            "state_json": str(config.root / "STATE" / "current_status.json"),
            "check_report_json": str(config.root / "REPORTS" / "base_half_check_report.json"),
            "identity_files_ready": len(missing) == 0,
        }
    elif command == "tool-list":
        tools = sorted([p.name for p in (config.root / "TOOLS").glob("*") if p.is_file()])
        details["tools"] = {"count": len(tools), "items": tools}
    elif command == "validator-check":
        details["validator"] = _json_validity_report(config)
    elif command == "capability-map":
        details["capability_map"] = {"base_commands": BASE_COMMANDS, "domain_commands": list(config.domain_commands.keys())}
    elif command == "script-receipt-check":
        receipts = sorted([p.name for p in (config.root / "RECEIPTS").glob("*.json") if p.is_file()])
        details["receipt_scan"] = {"count": len(receipts), "files": receipts[:20]}
    elif command == "task-route":
        details["route"] = ["intake", "decompose", "execute", "verify", "report"]
    elif command == "stage-map-outline":
        details["stage_map"] = ["S1 intake", "S2 planning", "S3 execution", "S4 checks", "S5 closure"]
    elif command == "ready-for-agent-check":
        details["readiness"] = {"missing_identity_files": len(missing), "ready": len(missing) == 0}
    elif command == "route-report":
        details["route_report"] = {"paths": important_paths(config), "next": "status -> check -> domain"}
    elif command == "priority-matrix":
        details["priority_matrix"] = [
            {"priority": "P0", "item": "truth checks", "status": "active"},
            {"priority": "P1", "item": "scope boundary", "status": "active"},
            {"priority": "P2", "item": "packaging", "status": "queued"},
        ]
    elif command == "campaign-plan-outline":
        details["campaign_plan"] = ["admission", "identity", "commands", "sweep", "bundle"]
    elif command == "resource-estimate":
        details["resource_estimate"] = {"domain_commands": len(config.domain_commands), "files_under_organ": len(list(config.root.rglob("*")))}
    elif command == "freeze-list":
        details["freeze"] = ["THRONE*", "CUSTODES*", "forbidden out-of-scope paths"]
    elif command == "lesson-register":
        examples = sorted([p.name for p in (config.root / "EXAMPLES").glob("*") if p.is_file()])
        details["lessons"] = {"example_files": examples}
    elif command == "training-pack-outline":
        details["training_pack"] = {"required": ["IDENTITY_PROFILE.md", "LORE_FUNCTIONS.md", "DOMAIN_COMMANDS.md", "SPECULUM_CHECKS.md"]}
    elif command == "skill-map":
        skills = sorted([p.name for p in (config.root / "skills").glob("*") if p.exists()])
        details["skills"] = {"count": len(skills), "items": skills[:20]}
    elif command == "example-check":
        examples = sorted([p.name for p in (config.root / "EXAMPLES").glob("*") if p.is_file()])
        details["examples"] = {"count": len(examples), "files": examples}
    elif command == "law-list":
        gate_registry = _read_json(repo_root / "ORGANS" / "DOCTRINARIUM" / "GATES" / "GATE_REGISTRY_V0_1.json")
        gate_ids: List[str] = []
        if isinstance(gate_registry, dict):
            for gate in gate_registry.get("gates", []):
                if isinstance(gate, dict) and "gate_id" in gate:
                    gate_ids.append(str(gate["gate_id"]))
        details["laws"] = {"gate_count": len(gate_ids), "gates_preview": gate_ids[:20]}
    elif command == "doctrine-check":
        doctrine_files = [
            "ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json",
            "ORGANS/DOCTRINARIUM/GATES/UNIVERSAL_GATE_LAWS_V0_1.md",
            "ORGANS/DOCTRINARIUM/GATES/BASE_MANDATORY_GATES_V0_1.md",
        ]
        details["doctrine"] = [{"file": rel, "exists": (repo_root / rel).exists()} for rel in doctrine_files]
    elif command == "violation-report":
        drift = _scope_drift(repo_root)
        forbidden_hits = [row for row in drift if ("THRONE" in row["path"].upper() or "CUSTODES" in row["path"].upper())]
        details["violations"] = {"forbidden_hits": len(forbidden_hits), "hits": forbidden_hits}
    elif command == "gate-before-work":
        details["gate_before_work"] = {
            "required_truth_checks": ["git status --short", "git rev-parse HEAD", "git branch --show-current"],
            "role_ack_required": True,
        }

    return {
        "schema_version": "ORGAN_DOMAIN_COMMAND_RESULT_V0_1",
        "task_id": TASK_ID_IDENTITY_RICH,
        "timestamp_utc": _utc_now(),
        "visual_status": _visual_status(),
        "warnings": warnings,
        "details": details,
    }


def command_domain(config: OrganConfig, command: str) -> int:
    ensure_base_layout(config)
    payload = _domain_output(config, command)
    receipt = config.root / "RECEIPTS" / f"domain_{command.replace('-', '_')}_latest.json"
    _write_json(receipt, payload)
    payload["receipt_path"] = str(receipt)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


def _suppress_stdout_call(fn: Any, *args: Any, **kwargs: Any) -> Any:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        return fn(*args, **kwargs)


def _command_descriptions(config: OrganConfig) -> Dict[str, str]:
    desc: Dict[str, str] = {
        "status": "Show dashboard/status operator overview.",
        "dashboard": "Show dashboard/status operator overview.",
        "tools": "Show compact tool registry capabilities.",
        "identity": "Show organ identity and mission.",
        "check": "Run integrity checks and summary verdict.",
        "help": "Show command palette and shell usage.",
        "where": "Show important paths and runtime roots.",
        "pack": "Build and export runtime package.",
        "raw": "Open explicit raw/detail mode.",
        "screenshot": "Save SVG screenshot for selected mode (or all).",
        "raw-status": "Show full JSON status payload.",
        "raw-tools": "Show full JSON tools payload.",
        "raw-identity": "Show full JSON identity payload.",
        "raw-check": "Show full JSON check payload.",
    }
    for cmd, cmd_desc in config.domain_commands.items():
        desc.setdefault(cmd, cmd_desc)
    return desc


def _command_palette_rows(config: OrganConfig) -> List[Tuple[str, str, str]]:
    order = [
        ("status", "F1"),
        ("tools", "F2"),
        ("identity", "F3"),
        ("check", "F4"),
        ("where", "F5"),
        ("pack", "F6"),
        ("help", "F7"),
    ]
    descriptions = _command_descriptions(config)
    rows: List[Tuple[str, str, str]] = []
    for cmd, key in order:
        rows.append((cmd, descriptions.get(cmd, ""), key))
    rows.append(("raw", "Open explicit raw/detail mode.", "R"))
    rows.append(("screenshot", "Save SVG screenshot for mode or all modes.", "S"))
    rows.append(("exit", "Close the operator shell.", "ESC"))
    for cmd in sorted(config.domain_commands.keys()):
        rows.append((cmd, descriptions.get(cmd, ""), "DOMAIN"))
    return rows


def _clip_text(value: str, limit: int = 120) -> str:
    text = value.strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _shorten_path(value: str, repo_root: Path, limit: int = 90) -> str:
    raw = value.strip().replace("\\", "/")
    if not raw:
        return raw
    root = str(repo_root).replace("\\", "/")
    lower_raw = raw.lower()
    lower_root = root.lower()
    if lower_raw.startswith(lower_root):
        raw = ".../" + raw[len(root) :].lstrip("/")
    if len(raw) <= limit:
        return raw
    parts = [part for part in raw.split("/") if part]
    if len(parts) >= 4:
        raw = "/".join([parts[0], "...", parts[-2], parts[-1]])
    return _clip_text(raw, limit)


def _resolve_visual_mode(command: str, detail: bool) -> Tuple[str, bool, str]:
    token = command.strip().lower()
    if token in {"dashboard", "status", "visual-status"}:
        return "status", detail, "dashboard"
    if token in {"tools", "visual-tools"}:
        return "tools", detail, "tools"
    if token in {"identity", "visual-identity"}:
        return "identity", detail, "identity"
    if token in {"check", "visual-check"}:
        return "check", detail, "check"
    if token in {"raw", "raw-status"}:
        return "status", True, "raw"
    if token == "raw-tools":
        return "tools", True, "raw"
    if token == "raw-identity":
        return "identity", True, "raw"
    if token == "raw-check":
        return "check", True, "raw"
    return token, detail, token


def _parse_shell_token(raw: str) -> Tuple[str, bool]:
    token = raw.strip().lstrip("/").lower()
    if not token:
        return "", False
    if token in {"dashboard", "status"}:
        return "dashboard", False
    if token in SHELL_FUNCTION_KEY_MAP:
        return SHELL_FUNCTION_KEY_MAP[token], False
    if token in {"r", "raw"}:
        return "raw", False
    if token in {"s", "screenshot"}:
        return "screenshot", False
    if token.startswith("visual-"):
        return token.replace("visual-", "", 1), False
    if token.startswith("details"):
        parts = token.split()
        target = parts[1] if len(parts) > 1 else "status"
        return target, True
    if token.startswith("raw-"):
        return token.replace("raw-", "", 1), True
    return token, False


def _visual_payload_for_command(config: OrganConfig, command: str, detail: bool) -> Dict[str, Any]:
    ensure_base_layout(config)
    repo_root = _repo_root(config.root)
    resolved_command, detail, mode_name = _resolve_visual_mode(command, detail)
    git = _git_info(repo_root)
    tool_summary = _tool_registry_summary(config)
    palette = _command_palette_rows(config)
    now = datetime.now(timezone.utc).strftime("%H:%M:%S")
    latest_report_path = _latest_report_path(config) or "none"
    latest_receipt_path = _latest_receipt_path(config) or "none"
    head_short = str(git.get("head", ""))[:7] if str(git.get("head", "")).strip() else "UNKNOWN"
    branch = str(git.get("branch", "")).strip() or "UNKNOWN"
    dirty = bool(str(git.get("dirty", "")).strip())
    visual_status = _visual_status()

    activity_rows: List[Tuple[str, str, str, str]] = []
    tool_rows: List[Tuple[str, str, str]] = []
    raw_payload: Dict[str, Any] = {}
    warn_count = len(tool_summary.get("warnings", []))
    error_count = 0
    block_count = 0
    latest_output = f"once_mode_command={mode_name}"

    if resolved_command == "status":
        _, state_path = _suppress_stdout_call(command_status, config)
        state = _read_json(state_path)
        raw_payload = state
        backend = state.get("backend_truth", {}) if isinstance(state, dict) else {}
        activity_rows = [
            (now, "Repository", _shorten_path(str(repo_root), repo_root), "OK"),
            (now, "Backend Truth", f"HEAD {backend.get('head', '')[:7]} | {backend.get('branch', '')}", "VERIFIED"),
            (now, "Worktree", "dirty" if dirty else "clean", "WARN" if dirty else "READY"),
            (now, "Visual Status", visual_status, "IN_SYNC"),
        ]
        warn_count += 1 if dirty else 0
    elif resolved_command == "tools":
        view = build_organ_tool_view(organ_id=config.organ_name, index_path=default_tool_index_path(repo_root))
        raw_payload = view
        relevant = view.get("relevant_tools", []) if isinstance(view.get("relevant_tools", []), list) else []
        for item in relevant[:10]:
            if isinstance(item, dict):
                tool_rows.append(
                    (
                        str(item.get("tool_id", "UNKNOWN")),
                        str(item.get("owner_organ", "UNKNOWN")),
                        str(item.get("availability_status", "UNKNOWN")),
                    )
                )
        activity_rows = [
            (now, "Registry Path", _shorten_path(str(view.get("registry_source", "")), repo_root, 78), "LOADED"),
            (now, "Registered", str(len(relevant)), "OK"),
            (now, "Available", str(len(view.get("available_tools", []))), "OK"),
            (now, "Missing", str(len(view.get("missing_tools", []))), "WARN" if len(view.get("missing_tools", [])) else "OK"),
        ]
        warn_count += len(view.get("warnings", [])) if isinstance(view.get("warnings", []), list) else 0
    elif resolved_command == "identity":
        profile = _read_json(config.root / "agent_profile.json")
        identity_profile = _read_json(config.root / "IDENTITY" / "identity_profile.json")
        raw_payload = {"profile": profile, "identity_profile": identity_profile}
        mission = str(identity_profile.get("mission", config.identity_summary)) if isinstance(identity_profile, dict) else config.identity_summary
        activity_rows = [
            (now, "Organ", config.organ_name, "OK"),
            (now, "Mission", _clip_text(mission, 96), "FOCUS"),
            (now, "Domain Commands", str(len(config.domain_commands)), "READY"),
            (now, "Identity Summary", _clip_text(config.identity_summary, 96), "SYNC"),
        ]
    elif resolved_command == "check":
        _, report_json, _ = _suppress_stdout_call(command_check, config)
        report = _read_json(report_json)
        raw_payload = report
        missing = report.get("missing", []) if isinstance(report.get("missing", []), list) else []
        warnings = report.get("warnings", []) if isinstance(report.get("warnings", []), list) else []
        verdict = str(report.get("verdict", "UNKNOWN"))
        check_warn = len(warnings)
        check_block = len(missing)
        verdict_state = "OK" if verdict == "PASS" else ("WARN" if verdict == "WARN" else "ERROR")
        activity_rows = [
            (now, "Check Verdict", verdict, verdict_state),
            (now, "PASS/WARN", f"PASS={1 if verdict == 'PASS' else 0} WARN={check_warn}", "INFO" if check_warn else "OK"),
            (now, "ERROR/BLOCK", f"ERROR={1 if verdict not in {'PASS', 'WARN'} else 0} BLOCK={check_block}", "BLOCK" if check_block else "OK"),
            (now, "Report", _shorten_path(str(report_json), repo_root, 78), "WRITTEN"),
        ]
        warn_count += len(warnings)
        block_count += len(missing)
    elif resolved_command == "where":
        raw_payload = {"organ": config.organ_name, "paths": important_paths(config), "timestamp_utc": _utc_now()}
        paths = raw_payload.get("paths", {}) if isinstance(raw_payload.get("paths"), dict) else {}
        activity_rows = [
            (now, "Organ Root", _shorten_path(str(paths.get("organ_root", "")), repo_root, 78), "READY"),
            (now, "Runner", _shorten_path(str(paths.get("runner", "")), repo_root, 78), "READY"),
            (now, "Runtime Root", _shorten_path(str(paths.get("runtime_root", "")), repo_root, 78), "READY"),
            (now, "Worktree", "dirty" if dirty else "clean", "WARN" if dirty else "OK"),
        ]
        warn_count += 1 if dirty else 0
    elif resolved_command == "pack":
        _, pack_root = _suppress_stdout_call(command_pack, config)
        manifest = _read_json(pack_root / "pack_manifest.json")
        raw_payload = manifest
        copied = manifest.get("copied", []) if isinstance(manifest.get("copied"), list) else []
        activity_rows = [
            (now, "Pack Root", _shorten_path(str(pack_root), repo_root, 78), "WRITTEN"),
            (now, "Copied Artifacts", str(len(copied)), "OK"),
            (now, "Visual Status", str(manifest.get("visual_status", "UNKNOWN")), "IN_SYNC"),
            (now, "Commands In Pack", str(len(manifest.get("commands", []))), "READY"),
        ]
    elif resolved_command == "help":
        payload = {
            "organ": config.organ_name,
            "commands": [row[0] for row in palette],
            "shell_usage": f"py -3 TOOLS/{config.organ_slug}_agent_runner.py shell",
            "visual_status": visual_status,
        }
        raw_payload = payload
        activity_rows = [
            (now, "Shell", "Visual Shell V0.5 with dashboard/tools/raw mode split", "READY"),
            (now, "Detail Mode", "Use raw mode or raw-* one-shot commands", "INFO"),
            (now, "Renderer", _renderer_mode(), "ACTIVE"),
            (now, "Command Count", str(len(palette)), "READY"),
        ]
    else:
        activity_rows = [
            (now, "Command", resolved_command, "UNKNOWN"),
            (now, "Hint", "Use help for available commands.", "WARN"),
        ]
        warn_count += 1

    bottom = [
        f"latest_report: {_shorten_path(latest_report_path, repo_root, 88)}",
        f"latest_receipt: {_shorten_path(latest_receipt_path, repo_root, 88)}",
        f"event_summary: WARN={warn_count} ERROR={error_count} BLOCK={block_count}",
    ]
    if detail and raw_payload:
        bottom.append("detail_mode: raw payload enabled by explicit request")

    return {
        "command": resolved_command,
        "mode": mode_name,
        "detail": detail,
        "palette": palette,
        "activity_rows": activity_rows,
        "tool_rows": tool_rows,
        "raw_payload": raw_payload,
        "warn_count": warn_count,
        "error_count": error_count,
        "block_count": block_count,
        "git_head_short": head_short,
        "git_branch": branch,
        "git_dirty": dirty,
        "visual_status": visual_status,
        "renderer": _renderer_mode(),
        "latest_output": latest_output,
        "bottom": bottom,
        "tool_summary": tool_summary,
    }


def _render_shell_command_view(
    config: OrganConfig,
    command: str,
    detail: bool,
    *,
    console: Optional[Console] = None,
) -> Dict[str, Any]:
    payload = _visual_payload_for_command(config, command, detail)
    tool_summary = payload["tool_summary"]
    palette = payload["palette"]
    activity_rows = payload["activity_rows"]
    tool_rows = payload["tool_rows"]
    bottom = payload["bottom"]
    visual_status = payload["visual_status"]
    renderer = payload["renderer"]
    warn_count = int(payload["warn_count"])
    error_count = int(payload["error_count"])
    block_count = int(payload["block_count"])

    if (
        HAVE_RICH
        and Console is not None
        and HAVE_OPERATOR_WIDGETS
        and top_status_panel is not None
        and activity_panel is not None
        and mission_panel is not None
        and command_palette_panel is not None
        and tool_registry_panel is not None
        and bottom_event_panel is not None
    ):
        render_console = console or Console()
        render_console.print(top_status_panel(payload, organ_name=config.organ_name, mission=config.identity_summary, shell_version=VISUAL_SHELL_VERSION))
        render_console.print(activity_panel(payload))
        render_console.print(mission_panel(payload, config.identity_summary))
        render_console.print(command_palette_panel(payload))
        render_console.print(tool_registry_panel(payload))
        render_console.print(bottom_event_panel(payload))
        if detail and raw_detail_panel is not None:
            render_console.print(raw_detail_panel(payload))
    else:
        mode_name = str(payload.get("mode", command)).upper()
        top_lines = [
            f"[=COG=] {config.organ_name} :: MECHANICUS VISUAL SHELL {VISUAL_SHELL_VERSION} :: MODE={mode_name}",
            f"mission: {config.identity_summary}",
            (
                f"backend_truth: head={payload['git_head_short']} branch={payload['git_branch']} "
                f"dirty={'yes' if payload['git_dirty'] else 'no'}"
            ),
            (
                f"visual_status: {visual_status} | renderer: {renderer} | commands: {len(palette)} "
                f"| warn: {warn_count} | error: {error_count} | block: {block_count}"
            ),
        ]
        print("TOP STATUS BAR")
        for line in top_lines:
            print(f"- {line}")
        print("LEFT WORK ZONE")
        for row in activity_rows:
            print(f"- {row[0]} | {row[1]} | {row[2]} | {row[3]}")
        print("RIGHT COMMAND ZONE")
        for cmd, summary, key in palette[:12]:
            print(f"- {cmd} :: {_clip_text(summary, 72)} :: [{key}]")
        print("TOOL REGISTRY")
        print(f"- path={tool_summary.get('registry_source', '')}")
        print(
            "- counts: registered="
            f"{tool_summary.get('registered_tool_count', 0)} "
            f"available={tool_summary.get('available_tool_count', 0)} "
            f"missing={tool_summary.get('missing_tool_count', 0)}"
        )
        for row in tool_rows[:10]:
            print(f"- tool={row[0]} owner={row[1]} status={row[2]}")
        print("BOTTOM EVENT BAR")
        for line in bottom:
            print(f"- {line}")
        print(f"RENDERER_MODE: {_renderer_mode()}")
        print(f"VISUAL_STATUS: {_visual_status()}")
        if detail:
            raw_json_text = json.dumps(payload.get("raw_payload", {}), ensure_ascii=True, indent=2)
            raw_json_text = raw_json_text if len(raw_json_text) <= 3500 else raw_json_text[:3500] + "\n...<truncated>..."
            print("DETAIL RAW PAYLOAD")
            print(raw_json_text)
    return payload


def command_shell_screenshot(config: OrganConfig, mode: str, output_path: Optional[str] = None) -> Tuple[int, str]:
    if not HAVE_RICH or Console is None:
        print("SCREENSHOT_UNAVAILABLE: rich renderer not available.")
        return 1, ""
    mode_token = mode.strip().lower()
    if mode_token == "all":
        exported: List[Dict[str, str]] = []
        for entry in ["dashboard", "tools", "identity", "check", "raw"]:
            code, path = command_shell_screenshot(config, entry, None)
            if code != 0:
                return code, ""
            exported.append({"mode": entry, "path": path})
        print("SHELL_SCREENSHOT_ALL_COUNT: 5")
        print("SHELL_SCREENSHOT_ALL_MODES: dashboard,tools,identity,check,raw")
        print("SHELL_SCREENSHOT_ALL_DONE: yes")
        return 0, json.dumps(exported, ensure_ascii=True)

    resolved_command, detail, mode_name = _resolve_visual_mode(mode, False)
    if resolved_command not in {"status", "tools", "identity", "check", "help", "where", "pack"}:
        print(f"SCREENSHOT_MODE_INVALID: {mode}")
        return 2, ""

    screenshot_root = config.root / "REPORTS" / "SCREENSHOTS"
    version_token = VISUAL_SHELL_VERSION.replace(".", "_")
    target = Path(output_path) if output_path else screenshot_root / f"mechanicus_{mode_name}_{version_token}.svg"
    if target.suffix.lower() != ".svg":
        target = target.with_suffix(".svg")
    target.parent.mkdir(parents=True, exist_ok=True)

    render_console = Console(record=True, width=190, force_terminal=True, color_system="truecolor")
    _render_shell_command_view(config, resolved_command, detail, console=render_console)
    render_console.save_svg(str(target), title=f"{config.organ_name}:{mode_name}:{VISUAL_SHELL_VERSION}")
    print(f"SHELL_SCREENSHOT_SVG: {target}")
    print(f"SHELL_SCREENSHOT_MODE: {mode_name}")
    return 0, str(target)


def _shell_dispatch(config: OrganConfig, raw: str) -> Tuple[int, bool]:
    token = raw.strip()
    if not token:
        return 0, False
    if token.lower() in {"exit", "quit", "/exit", "/quit", "esc", "/esc"}:
        return 0, True
    shell_token = token.strip().lstrip("/").lower()
    if shell_token == "s":
        code, _ = command_shell_screenshot(config, "dashboard")
        return code, False
    if shell_token.startswith("screenshot"):
        parts = shell_token.split()
        screenshot_mode = parts[1] if len(parts) > 1 else "dashboard"
        code, _ = command_shell_screenshot(config, screenshot_mode)
        return code, False

    parsed, detail = _parse_shell_token(token)
    if parsed == "screenshot":
        code, _ = command_shell_screenshot(config, "dashboard")
        return code, False
    if parsed in {"status", "dashboard", "tools", "identity", "check", "help", "raw"}:
        resolved_command, resolved_detail, _ = _resolve_visual_mode(parsed, detail)
        _render_shell_command_view(config, resolved_command, resolved_detail)
        return 0, False
    if parsed in {"where", "pack"} and not detail:
        if parsed == "where":
            command_where(config)
        else:
            command_pack(config)
        return 0, False

    domain = _canonical_domain_command(config, parsed)
    if domain and not detail:
        command_domain(config, domain)
        return 0, False

    print("Unknown shell command. Use help, dashboard/status, tools, identity, check, raw, screenshot, or exit.")
    return 2, False


def _can_launch_textual_shell(config: OrganConfig) -> bool:
    if config.organ_name != "MECHANICUS_AGENT":
        return False
    if not textual_runtime_available():
        return False
    if os.environ.get("IMPERIUM_DISABLE_TEXTUAL_SHELL", "").strip() == "1":
        return False
    return bool(sys.stdin.isatty() and sys.stdout.isatty())


def command_shell(config: OrganConfig, once: Optional[str], screenshot: Optional[str] = None) -> int:
    ensure_base_layout(config)
    if screenshot:
        return command_shell_screenshot(config, screenshot)[0]
    if once:
        code, _ = _shell_dispatch(config, once)
        return code

    if _can_launch_textual_shell(config) and launch_textual_operator_shell is not None:
        launched, reason = launch_textual_operator_shell(
            organ_name=config.organ_name,
            mission=config.identity_summary,
            payload_loader=lambda command, detail: _visual_payload_for_command(config, command, detail),
            shell_version=VISUAL_SHELL_VERSION,
            screenshot_dir=str(config.root / "REPORTS" / "SCREENSHOTS"),
        )
        if launched:
            return 0
        print(f"textual_shell_fallback_reason: {reason}")

    _render_shell_command_view(config, "status", detail=False)
    print("Type: dashboard/status, tools, identity, check, raw, screenshot [mode], f1..f7, r, s, exit")
    while True:
        try:
            raw = input(f"{config.organ_slug}> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        code, should_exit = _shell_dispatch(config, raw)
        if should_exit:
            return 0
        if code != 0:
            return code


def command_help(config: OrganConfig) -> int:
    payload = {
        "organ": config.organ_name,
        "runner": f"{config.organ_slug}_agent_runner.py",
        "commands": _all_supported_commands(config),
        "domain_commands": config.domain_commands,
        "shell_usage": f"py -3 TOOLS/{config.organ_slug}_agent_runner.py shell",
        "visual_status": _visual_status(),
        "warnings": [VISUAL_WARN_PLAIN_FALLBACK] if not HAVE_RICH else [],
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0


def run_cli(config: OrganConfig, argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog=f"{config.organ_slug}_agent_runner.py")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("check")
    sub.add_parser("where")
    sub.add_parser("identity")
    sub.add_parser("tools")
    sub.add_parser("pack")
    shell = sub.add_parser("shell")
    shell.add_argument("--once", default=None)
    shell.add_argument("--screenshot", default=None)
    sub.add_parser("help")
    for domain_command in config.domain_commands:
        sub.add_parser(domain_command)

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "status":
        return command_status(config)[0]
    if args.command == "check":
        return command_check(config)[0]
    if args.command == "where":
        return command_where(config)
    if args.command == "identity":
        return command_identity(config)
    if args.command == "tools":
        return command_tools(config)
    if args.command == "pack":
        return command_pack(config)[0]
    if args.command == "shell":
        return command_shell(config, args.once, args.screenshot)
    if args.command == "help":
        return command_help(config)

    domain = _canonical_domain_command(config, args.command)
    if domain:
        return command_domain(config, domain)
    return 2


__all__ = [
    "OrganConfig",
    "BASE_COMMANDS",
    "TASK_ID_BASE_HALF",
    "TASK_ID_IDENTITY_RICH",
    "ensure_base_layout",
    "run_cli",
]
