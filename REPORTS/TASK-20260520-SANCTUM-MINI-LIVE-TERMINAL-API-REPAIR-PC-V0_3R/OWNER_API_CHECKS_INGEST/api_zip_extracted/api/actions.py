"""Allowlisted action endpoints for Sanctum Mini V0.3."""

from __future__ import annotations

import json
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MAX_ACTION_TIMEOUT_SECONDS = 30
MAX_HISTORY_ITEMS = 120

_TERMINAL_COMMAND_ALLOWLIST = (
    "status",
    "tools",
    "check",
    "identity",
    "where",
    "help",
    "raw",
    "screenshot",
    "clear",
)

_ACTION_HISTORY: list[dict[str, Any]] = []
_TERMINAL_HISTORY: list[dict[str, Any]] = []
_ACTION_HISTORY_LOCK = threading.Lock()
_TERMINAL_HISTORY_LOCK = threading.Lock()


@dataclass(frozen=True)
class ActionDefinition:
    action_id: str
    title_en: str
    title_ru: str
    safety: str
    mode: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _truncate(value: str, limit: int = 4000) -> str:
    if len(value) <= limit:
        return value
    return f"{value[:limit]}...[truncated]"


def _runner_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "ORGAN_AGENTS"
        / "MECHANICUS_AGENT"
        / "TOOLS"
        / "mechanicus_agent_runner.py"
    )


def _allowed_actions() -> list[ActionDefinition]:
    return [
        ActionDefinition(
            action_id="refresh_state",
            title_en="Refresh state",
            title_ru="Обновить состояние",
            safety="ALLOWLISTED_LOCAL_NO_SIDE_EFFECTS",
            mode="internal",
        ),
        ActionDefinition(
            action_id="mechanicus_visual_status",
            title_en="Mechanicus visual-status",
            title_ru="Механикус visual-status",
            safety="ALLOWLISTED_LOCAL_READ_ONLY",
            mode="command",
        ),
        ActionDefinition(
            action_id="mechanicus_visual_tools",
            title_en="Mechanicus visual-tools",
            title_ru="Механикус visual-tools",
            safety="ALLOWLISTED_LOCAL_READ_ONLY",
            mode="command",
        ),
        ActionDefinition(
            action_id="mechanicus_visual_check",
            title_en="Mechanicus visual-check",
            title_ru="Механикус visual-check",
            safety="ALLOWLISTED_LOCAL_READ_ONLY",
            mode="command",
        ),
        ActionDefinition(
            action_id="mechanicus_visual_identity",
            title_en="Mechanicus visual-identity",
            title_ru="Механикус visual-identity",
            safety="ALLOWLISTED_LOCAL_READ_ONLY",
            mode="command",
        ),
        ActionDefinition(
            action_id="mechanicus_screenshot_all",
            title_en="Mechanicus screenshot all",
            title_ru="Механикус screenshot all",
            safety="ALLOWLISTED_LOCAL_VISUAL_CAPTURE",
            mode="command",
        ),
        ActionDefinition(
            action_id="mechanicus_screenshot_command",
            title_en="Mechanicus screenshot command",
            title_ru="Команда screenshot",
            safety="DISPLAY_ONLY_SAFE_FALLBACK",
            mode="display",
        ),
        ActionDefinition(
            action_id="open_or_show_latest_report",
            title_en="Open/show latest report path",
            title_ru="Открыть/показать путь отчёта",
            safety="DISPLAY_ONLY_SAFE_FALLBACK",
            mode="display",
        ),
        ActionDefinition(
            action_id="open_or_show_screenshots_folder",
            title_en="Open/show screenshots path",
            title_ru="Открыть/показать путь скриншотов",
            safety="DISPLAY_ONLY_SAFE_FALLBACK",
            mode="display",
        ),
        ActionDefinition(
            action_id="show_api_state_json",
            title_en="Show API state JSON",
            title_ru="Показать API state JSON",
            safety="ALLOWLISTED_LOCAL_NO_SIDE_EFFECTS",
            mode="display",
        ),
        ActionDefinition(
            action_id="show_api_mechanicus_json",
            title_en="Show API mechanicus JSON",
            title_ru="Показать API mechanicus JSON",
            safety="ALLOWLISTED_LOCAL_NO_SIDE_EFFECTS",
            mode="display",
        ),
    ]


def _command_map(repo_root: Path) -> dict[str, list[str]]:
    runner = _runner_path(repo_root)
    runner_str = str(runner)
    return {
        "mechanicus_visual_status": [
            "python",
            runner_str,
            "shell",
            "--once",
            "visual-status",
        ],
        "mechanicus_visual_tools": [
            "python",
            runner_str,
            "shell",
            "--once",
            "visual-tools",
        ],
        "mechanicus_visual_check": [
            "python",
            runner_str,
            "shell",
            "--once",
            "visual-check",
        ],
        "mechanicus_visual_identity": [
            "python",
            runner_str,
            "shell",
            "--once",
            "visual-identity",
        ],
        "mechanicus_screenshot_all": [
            "python",
            runner_str,
            "shell",
            "--screenshot",
            "all",
        ],
    }


def terminal_allowlist() -> list[str]:
    return list(_TERMINAL_COMMAND_ALLOWLIST)


def list_actions(repo_root: Path, state: dict[str, Any]) -> list[dict[str, Any]]:
    commands = _command_map(repo_root)
    latest_report = (
        state.get("global_truth", {}).get("latest_report_path")
        if isinstance(state.get("global_truth"), dict)
        else None
    )
    latest_screenshot = (
        state.get("global_truth", {}).get("latest_screenshot_path")
        if isinstance(state.get("global_truth"), dict)
        else None
    )
    runner = _runner_path(repo_root)

    items: list[dict[str, Any]] = []
    for action in _allowed_actions():
        command_preview = None
        display_value = None
        if action.action_id in commands:
            command_preview = " ".join(commands[action.action_id])
            display_value = command_preview
        elif action.action_id == "mechanicus_screenshot_command":
            display_value = f"python {runner} shell --screenshot all"
        elif action.action_id == "open_or_show_latest_report":
            display_value = latest_report or "MISSING"
        elif action.action_id == "open_or_show_screenshots_folder":
            display_value = latest_screenshot or "MISSING"
        elif action.action_id == "show_api_state_json":
            display_value = "/api/state"
        elif action.action_id == "show_api_mechanicus_json":
            display_value = "/api/mechanicus"
        elif action.action_id == "refresh_state":
            display_value = "/api/state"

        items.append(
            {
                "action_id": action.action_id,
                "title_en": action.title_en,
                "title_ru": action.title_ru,
                "safety": action.safety,
                "mode": action.mode,
                "command_preview": command_preview,
                "display_value": display_value,
                "run_endpoint": "/api/actions/run",
            }
        )
    return items


def _append_with_limit(
    history: list[dict[str, Any]],
    lock: threading.Lock,
    item: dict[str, Any],
) -> None:
    with lock:
        history.insert(0, item)
        if len(history) > MAX_HISTORY_ITEMS:
            del history[MAX_HISTORY_ITEMS:]


def _append_action_history(item: dict[str, Any]) -> None:
    _append_with_limit(_ACTION_HISTORY, _ACTION_HISTORY_LOCK, item)


def _append_terminal_history(item: dict[str, Any]) -> None:
    _append_with_limit(_TERMINAL_HISTORY, _TERMINAL_HISTORY_LOCK, item)


def get_action_history() -> list[dict[str, Any]]:
    with _ACTION_HISTORY_LOCK:
        return list(_ACTION_HISTORY)


def get_terminal_history() -> list[dict[str, Any]]:
    with _TERMINAL_HISTORY_LOCK:
        return list(_TERMINAL_HISTORY)


def _result_base(
    *,
    action_id: str,
    command: str,
    safety: str,
    source: str,
    organ: str,
    started_at: str,
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "command": command,
        "organ": organ,
        "source": source,
        "safety": safety,
        "started_at_utc": started_at,
        "finished_at_utc": None,
        "duration_ms": 0,
        "status": "UNKNOWN",
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "stdout_summary": "",
        "stderr_summary": "",
        "command_or_path": None,
        "evidence_path": None,
    }


def _finalize_result(result: dict[str, Any], started_perf: float) -> dict[str, Any]:
    result["finished_at_utc"] = _utc_now()
    result["duration_ms"] = int((time.perf_counter() - started_perf) * 1000)
    stdout = str(result.get("stdout", "") or "")
    stderr = str(result.get("stderr", "") or "")
    result["stdout_summary"] = _truncate(stdout)
    result["stderr_summary"] = _truncate(stderr)
    return result


def _record_result(result: dict[str, Any], started_perf: float) -> dict[str, Any]:
    finalized = _finalize_result(result, started_perf)
    _append_action_history(dict(finalized))
    _append_terminal_history(dict(finalized))
    return finalized


def _display_result(
    *,
    action_id: str,
    command: str,
    safety: str,
    source: str,
    organ: str,
    started_at: str,
    started_perf: float,
    status: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    command_or_path: str | None,
    evidence_path: str | None,
) -> dict[str, Any]:
    result = _result_base(
        action_id=action_id,
        command=command,
        safety=safety,
        source=source,
        organ=organ,
        started_at=started_at,
    )
    result.update(
        {
            "status": status,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "command_or_path": command_or_path,
            "evidence_path": evidence_path,
        }
    )
    return _record_result(result, started_perf)


def _where_summary(repo_root: Path, state: dict[str, Any]) -> str:
    truth = state.get("global_truth", {}) if isinstance(state.get("global_truth"), dict) else {}
    report_path = truth.get("latest_report_path") or "MISSING"
    screenshot_path = truth.get("latest_screenshot_path") or "MISSING"
    reports_root = str(repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS")
    return "\n".join(
        [
            "MECHANICUS_AGENT PATH SUMMARY",
            f"latest_report_path: {report_path}",
            f"latest_screenshot_path: {screenshot_path}",
            f"reports_root: {reports_root}",
        ]
    )


def _help_text() -> str:
    return (
        "Allowed terminal commands:\n"
        "- status\n"
        "- tools\n"
        "- check\n"
        "- identity\n"
        "- where\n"
        "- help\n"
        "- raw\n"
        "- screenshot\n"
        "- clear\n"
        "\n"
        "Safety mode: static server-side allowlist mapping only."
    )


def run_action(
    action_id: str,
    repo_root: Path,
    state: dict[str, Any],
    *,
    source: str = "action_button",
    command_label: str | None = None,
    organ: str = "MECHANICUS_AGENT",
) -> dict[str, Any]:
    allowed = {item.action_id: item for item in _allowed_actions()}
    started_at = _utc_now()
    started_perf = time.perf_counter()
    command = command_label or action_id

    if action_id not in allowed:
        return _display_result(
            action_id=action_id,
            command=command,
            safety="BLOCKED_NOT_ALLOWLISTED",
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="BLOCK",
            exit_code=127,
            stdout="",
            stderr="Action is not allowlisted.",
            command_or_path=None,
            evidence_path=None,
        )

    definition = allowed[action_id]
    commands = _command_map(repo_root)

    if action_id == "refresh_state":
        return _display_result(
            action_id=action_id,
            command=command,
            safety=definition.safety,
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS",
            exit_code=0,
            stdout="Refresh acknowledged. Re-fetch /api/state.",
            stderr="",
            command_or_path="/api/state",
            evidence_path=None,
        )

    if action_id == "open_or_show_latest_report":
        latest_report = state.get("global_truth", {}).get("latest_report_path")
        return _display_result(
            action_id=action_id,
            command=command,
            safety=definition.safety,
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS" if latest_report else "WARN",
            exit_code=0,
            stdout=f"latest_report_path={latest_report or 'MISSING'}",
            stderr="",
            command_or_path=latest_report or "MISSING",
            evidence_path=latest_report,
        )

    if action_id == "open_or_show_screenshots_folder":
        latest_screenshot = state.get("global_truth", {}).get("latest_screenshot_path")
        target = str(Path(latest_screenshot).parent) if latest_screenshot else "MISSING"
        return _display_result(
            action_id=action_id,
            command=command,
            safety=definition.safety,
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS" if latest_screenshot else "WARN",
            exit_code=0,
            stdout=f"screenshots_folder={target}",
            stderr="",
            command_or_path=target,
            evidence_path=latest_screenshot,
        )

    if action_id == "show_api_state_json":
        return _display_result(
            action_id=action_id,
            command=command,
            safety=definition.safety,
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS",
            exit_code=0,
            stdout=json.dumps(state, ensure_ascii=False, indent=2),
            stderr="",
            command_or_path="/api/state",
            evidence_path=None,
        )

    if action_id == "show_api_mechanicus_json":
        return _display_result(
            action_id=action_id,
            command=command,
            safety=definition.safety,
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS",
            exit_code=0,
            stdout=json.dumps(state.get("mechanicus", {}), ensure_ascii=False, indent=2),
            stderr="",
            command_or_path="/api/mechanicus",
            evidence_path=None,
        )

    if action_id == "mechanicus_screenshot_command":
        runner = _runner_path(repo_root)
        command_display = f"python {runner} shell --screenshot all"
        return _display_result(
            action_id=action_id,
            command=command,
            safety=definition.safety,
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS",
            exit_code=0,
            stdout=f"screenshot_command={command_display}",
            stderr="",
            command_or_path=command_display,
            evidence_path=None,
        )

    mapped_command = commands.get(action_id)
    if not mapped_command:
        return _display_result(
            action_id=action_id,
            command=command,
            safety="BLOCKED_ACTION_MAPPING_MISSING",
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="BLOCK",
            exit_code=126,
            stdout="",
            stderr="Allowlisted action has no execution mapping.",
            command_or_path=None,
            evidence_path=None,
        )

    try:
        completed = subprocess.run(
            mapped_command,
            cwd=str(repo_root),
            text=True,
            capture_output=True,
            timeout=MAX_ACTION_TIMEOUT_SECONDS,
            check=False,
        )
        status = "PASS" if completed.returncode == 0 else "ERROR"
        evidence_path = None
        if action_id == "mechanicus_screenshot_all" and completed.returncode == 0:
            evidence_path = str(
                repo_root
                / "IMPERIUM_NEW_GENERATION"
                / "ORGAN_AGENTS"
                / "MECHANICUS_AGENT"
                / "REPORTS"
                / "SCREENSHOTS"
            )

        return _display_result(
            action_id=action_id,
            command=command,
            safety=definition.safety,
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status=status,
            exit_code=completed.returncode,
            stdout=(completed.stdout or "").strip(),
            stderr=(completed.stderr or "").strip(),
            command_or_path=" ".join(mapped_command),
            evidence_path=evidence_path,
        )
    except subprocess.TimeoutExpired as exc:
        return _display_result(
            action_id=action_id,
            command=command,
            safety="ALLOWLISTED_TIMEOUT_EXPIRED",
            source=source,
            organ=organ,
            started_at=started_at,
            started_perf=started_perf,
            status="ERROR",
            exit_code=124,
            stdout=(exc.stdout or "").strip() if exc.stdout else "",
            stderr=(exc.stderr or "").strip() if exc.stderr else "Timeout exceeded.",
            command_or_path=" ".join(mapped_command),
            evidence_path=None,
        )


def execute_terminal_command(
    organ: str,
    command: str,
    repo_root: Path,
    state: dict[str, Any],
) -> dict[str, Any]:
    started_at = _utc_now()
    started_perf = time.perf_counter()

    normalized_organ = (organ or "").strip() or "MECHANICUS_AGENT"
    normalized = (command or "").strip().lower()

    if normalized_organ != "MECHANICUS_AGENT":
        return _display_result(
            action_id="terminal_blocked_organ",
            command=normalized or command,
            safety="BLOCKED_ORGAN_NOT_SUPPORTED",
            source="terminal_manual",
            organ=normalized_organ,
            started_at=started_at,
            started_perf=started_perf,
            status="BLOCK",
            exit_code=127,
            stdout="",
            stderr="Only MECHANICUS_AGENT supports LIVE terminal commands.",
            command_or_path=None,
            evidence_path=None,
        )

    if not normalized:
        return _display_result(
            action_id="terminal_blocked_empty",
            command="",
            safety="BLOCKED_EMPTY_COMMAND",
            source="terminal_manual",
            organ=normalized_organ,
            started_at=started_at,
            started_perf=started_perf,
            status="BLOCK",
            exit_code=127,
            stdout="",
            stderr="Command is required.",
            command_or_path=None,
            evidence_path=None,
        )

    if normalized == "clear":
        return _display_result(
            action_id="terminal_clear",
            command=normalized,
            safety="FRONTEND_ONLY_CLEAR",
            source="terminal_manual",
            organ=normalized_organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS",
            exit_code=0,
            stdout="Terminal clear is handled on frontend.",
            stderr="",
            command_or_path="frontend://clear",
            evidence_path=None,
        )

    if normalized not in _TERMINAL_COMMAND_ALLOWLIST:
        return _display_result(
            action_id="terminal_blocked_not_allowlisted",
            command=normalized,
            safety="BLOCKED_NOT_ALLOWLISTED",
            source="terminal_manual",
            organ=normalized_organ,
            started_at=started_at,
            started_perf=started_perf,
            status="BLOCK",
            exit_code=127,
            stdout="",
            stderr="Command is not in the Mechanicus terminal allowlist.",
            command_or_path=None,
            evidence_path=None,
        )

    if normalized == "help":
        return _display_result(
            action_id="terminal_help",
            command=normalized,
            safety="ALLOWLISTED_TERMINAL_HELP",
            source="terminal_manual",
            organ=normalized_organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS",
            exit_code=0,
            stdout=_help_text(),
            stderr="",
            command_or_path="manual_allowlist_help",
            evidence_path=None,
        )

    if normalized == "where":
        return _display_result(
            action_id="terminal_where",
            command=normalized,
            safety="ALLOWLISTED_TERMINAL_PATH_SUMMARY",
            source="terminal_manual",
            organ=normalized_organ,
            started_at=started_at,
            started_perf=started_perf,
            status="PASS",
            exit_code=0,
            stdout=_where_summary(repo_root, state),
            stderr="",
            command_or_path="path_summary",
            evidence_path=state.get("global_truth", {}).get("latest_report_path"),
        )

    mapped_action = {
        "status": "mechanicus_visual_status",
        "tools": "mechanicus_visual_tools",
        "check": "mechanicus_visual_check",
        "identity": "mechanicus_visual_identity",
        "raw": "show_api_mechanicus_json",
    }.get(normalized)

    if normalized == "screenshot":
        mapped_action = "mechanicus_screenshot_all" if _runner_path(repo_root).exists() else "mechanicus_screenshot_command"

    if not mapped_action:
        return _display_result(
            action_id="terminal_mapping_missing",
            command=normalized,
            safety="BLOCKED_ACTION_MAPPING_MISSING",
            source="terminal_manual",
            organ=normalized_organ,
            started_at=started_at,
            started_perf=started_perf,
            status="BLOCK",
            exit_code=126,
            stdout="",
            stderr="Allowlisted command has no server mapping.",
            command_or_path=None,
            evidence_path=None,
        )

    return run_action(
        mapped_action,
        repo_root,
        state,
        source="terminal_manual",
        command_label=normalized,
        organ=normalized_organ,
    )
