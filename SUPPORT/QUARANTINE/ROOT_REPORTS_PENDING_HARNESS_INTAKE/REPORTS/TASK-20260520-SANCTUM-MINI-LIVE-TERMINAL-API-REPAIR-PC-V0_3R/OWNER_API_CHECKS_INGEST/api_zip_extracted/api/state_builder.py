"""State builder for Sanctum Mini API endpoints."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .actions import terminal_allowlist
from .mechanicus_adapter import build_mechanicus_snapshot


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run_git(repo_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(repo_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except OSError:
        return "UNKNOWN"
    if result.returncode != 0:
        return "UNKNOWN"
    return result.stdout.strip()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _build_organs(mechanicus_status: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "MECHANICUS_AGENT",
            "label_en": "Mechanicus",
            "label_ru": "Механикус",
            "status": mechanicus_status,
            "data_class": "REAL",
        },
        {
            "id": "ADMINISTRATUM_AGENT",
            "label_en": "Administratum",
            "label_ru": "Администратум",
            "status": "PLACEHOLDER",
            "data_class": "PLACEHOLDER",
        },
        {
            "id": "OFFICIO_AGENTIS_AGENT",
            "label_en": "Officio",
            "label_ru": "Оффицио",
            "status": "PLACEHOLDER",
            "data_class": "PLACEHOLDER",
        },
        {
            "id": "ASTRONOMICON_AGENT",
            "label_en": "Astronomicon",
            "label_ru": "Астрономикон",
            "status": "PLACEHOLDER",
            "data_class": "PLACEHOLDER",
        },
        {
            "id": "INQUISITION_AGENT",
            "label_en": "Inquisition",
            "label_ru": "Инквизиция",
            "status": "PLACEHOLDER",
            "data_class": "PLACEHOLDER",
        },
        {
            "id": "DOCTRINARIUM_AGENT",
            "label_en": "Doctrinarium",
            "label_ru": "Доктринариум",
            "status": "PLACEHOLDER",
            "data_class": "PLACEHOLDER",
        },
        {
            "id": "STRATEGIUM_AGENT",
            "label_en": "Strategium",
            "label_ru": "Стратегиум",
            "status": "PLACEHOLDER",
            "data_class": "PLACEHOLDER",
        },
        {
            "id": "SCHOLA_IMPERIALIS_AGENT",
            "label_en": "Schola",
            "label_ru": "Школа",
            "status": "PLACEHOLDER",
            "data_class": "PLACEHOLDER",
        },
        {
            "id": "CUSTODES",
            "label_en": "Custodes",
            "label_ru": "Кустодес",
            "status": "LOCKED",
            "data_class": "LOCKED",
        },
        {
            "id": "THRONE",
            "label_en": "Throne",
            "label_ru": "Трон",
            "status": "LOCKED",
            "data_class": "LOCKED",
        },
    ]


def _counts_by_status(organs: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"CONNECTED": 0, "PLACEHOLDER": 0, "LOCKED": 0, "MISSING": 0, "UNKNOWN": 0}
    for organ in organs:
        status = organ.get("status", "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _command_value(commands: list[dict[str, Any]], command_id: str, default: str = "MISSING") -> str:
    for command in commands:
        if command.get("id") == command_id:
            return str(command.get("value", default))
    return default


def _build_actions(commands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": "refresh_state",
            "title_en": "Refresh State",
            "title_ru": "Обновить состояние",
            "type": "action",
            "value": "refresh_state",
            "execution": "ALLOWLISTED_API_ACTION",
        },
        {
            "id": "mechanicus_visual_status",
            "title_en": "Run visual-status",
            "title_ru": "Запустить visual-status",
            "type": "action",
            "value": "mechanicus_visual_status",
            "execution": "ALLOWLISTED_API_ACTION",
        },
        {
            "id": "mechanicus_visual_tools",
            "title_en": "Run visual-tools",
            "title_ru": "Запустить visual-tools",
            "type": "action",
            "value": "mechanicus_visual_tools",
            "execution": "ALLOWLISTED_API_ACTION",
        },
        {
            "id": "mechanicus_visual_check",
            "title_en": "Run visual-check",
            "title_ru": "Запустить visual-check",
            "type": "action",
            "value": "mechanicus_visual_check",
            "execution": "ALLOWLISTED_API_ACTION",
        },
        {
            "id": "mechanicus_visual_identity",
            "title_en": "Run visual-identity",
            "title_ru": "Запустить visual-identity",
            "type": "action",
            "value": "mechanicus_visual_identity",
            "execution": "ALLOWLISTED_API_ACTION",
        },
        {
            "id": "mechanicus_screenshot_all",
            "title_en": "Run screenshot all",
            "title_ru": "Запустить screenshot all",
            "type": "action",
            "value": "mechanicus_screenshot_all",
            "execution": "ALLOWLISTED_API_ACTION",
        },
        {
            "id": "mechanicus_screenshot_command",
            "title_en": "Show screenshot command",
            "title_ru": "Показать команду screenshot",
            "type": "action",
            "value": "mechanicus_screenshot_command",
            "execution": "DISPLAY_ONLY_SAFE_FALLBACK",
        },
        {
            "id": "open_or_show_latest_report",
            "title_en": "Open/show latest report path",
            "title_ru": "Открыть/показать путь отчёта",
            "type": "action",
            "value": "open_or_show_latest_report",
            "execution": "DISPLAY_ONLY_SAFE_FALLBACK",
        },
        {
            "id": "open_or_show_screenshots_folder",
            "title_en": "Open/show screenshots folder",
            "title_ru": "Открыть/показать папку скриншотов",
            "type": "action",
            "value": "open_or_show_screenshots_folder",
            "execution": "DISPLAY_ONLY_SAFE_FALLBACK",
        },
        {
            "id": "show_api_state_json",
            "title_en": "Show API state JSON",
            "title_ru": "Показать API state JSON",
            "type": "action",
            "value": "show_api_state_json",
            "execution": "ALLOWLISTED_API_ACTION",
        },
        {
            "id": "show_api_mechanicus_json",
            "title_en": "Show API mechanicus JSON",
            "title_ru": "Показать API mechanicus JSON",
            "type": "action",
            "value": "show_api_mechanicus_json",
            "execution": "ALLOWLISTED_API_ACTION",
        },
        {
            "id": "legacy_open_tui_command",
            "title_en": "Legacy TUI command",
            "title_ru": "Legacy команда TUI",
            "type": "display",
            "value": _command_value(commands, "tui_dashboard"),
            "execution": "LEGACY_DISPLAY_ONLY",
        },
    ]


def build_state(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or _repo_root()
    generated_at_utc = _utc_now()

    head = _run_git(root, "rev-parse", "HEAD")
    branch = _run_git(root, "branch", "--show-current")
    status_short_raw = _run_git(root, "status", "--short")
    status_short = [line for line in status_short_raw.splitlines() if line.strip()] if status_short_raw != "UNKNOWN" else []
    worktree_clean = not status_short

    micro_log: list[dict[str, str]] = [
        {"timestamp_utc": generated_at_utc, "status": "PASS", "message": "loaded repo truth"},
    ]

    mechanicus, adapter_events = build_mechanicus_snapshot(root)
    for event in adapter_events:
        micro_log.append(
            {
                "timestamp_utc": generated_at_utc,
                "status": event.get("status", "UNKNOWN"),
                "message": event.get("message", ""),
            }
        )

    organs = _build_organs(mechanicus_status=mechanicus.get("status", "UNKNOWN"))
    counts = _counts_by_status(organs)

    warnings_count = len(mechanicus.get("warnings", [])) + (0 if worktree_clean else 1)
    errors_count = len(mechanicus.get("errors", []))
    blockers_count = len(mechanicus.get("blocks", []))

    freshness_reference = (
        mechanicus.get("latest_artifacts", {}).get("latest_report_path")
        or mechanicus.get("latest_artifacts", {}).get("latest_screenshot_path")
    )

    actions = _build_actions(mechanicus.get("commands", []))
    micro_log.append(
        {
            "timestamp_utc": generated_at_utc,
            "status": "PASS",
            "message": "API health ready",
        }
    )

    return {
        "schema_version": "SANCTUM_MINI_STATE_V0_3",
        "generated_at_utc": generated_at_utc,
        "server": {
            "status": "PASS",
            "api_status": "PASS",
            "active_organ": "MECHANICUS_AGENT",
            "connection_quality": mechanicus.get("connection_quality", "UNKNOWN"),
        },
        "repo": {
            "repo_root": str(root),
            "head": head,
            "branch": branch,
            "worktree_state": "CLEAN" if worktree_clean else "DIRTY",
            "worktree_clean": worktree_clean,
            "git_status_short": status_short,
        },
        "organs": organs,
        "mechanicus": mechanicus,
        "global_truth": {
            "connected_organs_count": counts.get("CONNECTED", 0),
            "placeholders_count": counts.get("PLACEHOLDER", 0),
            "locked_count": counts.get("LOCKED", 0),
            "warnings_count": warnings_count,
            "errors_count": errors_count,
            "blockers_count": blockers_count,
            "latest_evidence_path": mechanicus.get("latest_artifacts", {}).get("latest_evidence_path"),
            "latest_screenshot_path": mechanicus.get("latest_artifacts", {}).get("latest_screenshot_path"),
            "latest_report_path": mechanicus.get("latest_artifacts", {}).get("latest_report_path"),
            "freshness_reference": freshness_reference,
            "real_vs_placeholder": {
                "real": ["MECHANICUS_AGENT"],
                "placeholder": [
                    "ADMINISTRATUM_AGENT",
                    "OFFICIO_AGENTIS_AGENT",
                    "ASTRONOMICON_AGENT",
                    "INQUISITION_AGENT",
                    "DOCTRINARIUM_AGENT",
                    "STRATEGIUM_AGENT",
                    "SCHOLA_IMPERIALIS_AGENT",
                ],
                "locked": ["CUSTODES", "THRONE"],
            },
        },
        "actions": actions,
        "viewport": {
            "active_organ": "MECHANICUS_AGENT",
            "mode": "LIVE_TERMINAL_PRIMARY",
            "live_terminal_allowlist": terminal_allowlist(),
            "mechanicus_latest_screenshot_url": "/api/mechanicus/screenshot/latest",
            "fallback_note": "Default center tab is LIVE terminal; screenshot preview is in the EVIDENCE tab.",
        },
        "micro_log": micro_log[-20:],
        "truth_notes": [
            "Only Mechanicus is connected with real data in V0.3.",
            "Other organs are explicit placeholders.",
            "Throne and Custodes are locked placeholders.",
            "Actions are allowlisted API actions; no arbitrary shell execution.",
            "Primary center focus must remain LIVE terminal viewport for the active organ.",
        ],
    }


def build_health(repo_root: Path | None = None) -> dict[str, Any]:
    state = build_state(repo_root=repo_root)

    verdict = "PASS"
    if state["mechanicus"].get("status") != "CONNECTED":
        verdict = "ERROR"
    elif state["global_truth"]["warnings_count"] > 0:
        verdict = "WARN"

    return {
        "schema_version": "SANCTUM_MINI_HEALTH_V0_3",
        "generated_at_utc": state["generated_at_utc"],
        "status": verdict,
        "api_status": "PASS",
        "active_organ": "MECHANICUS_AGENT",
        "repo_head": state["repo"]["head"],
        "worktree_state": state["repo"]["worktree_state"],
        "connection_quality": state["server"]["connection_quality"],
    }
