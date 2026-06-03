"""Mechanicus data adapter for Sanctum Mini V0.2."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _to_iso_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _looks_like_mechanicus_report_dir(report_dir: Path) -> bool:
    if not report_dir.exists() or not report_dir.is_dir():
        return False

    screenshot_dir = report_dir / "SCREENSHOTS"
    if screenshot_dir.exists():
        if any(screenshot_dir.glob("mechanicus_*.svg")):
            return True
        if any(screenshot_dir.glob("mechanicus_*.png")):
            return True

    probe_patterns = (
        "MECHANICUS*.md",
        "MECHANICUS*.json",
        "mechanicus_*.json",
        "mechanicus_*.md",
        "SHELL_TRANSCRIPT_DASHBOARD.txt",
    )
    for pattern in probe_patterns:
        if any(report_dir.glob(pattern)):
            return True
    return False


def _latest_mechanicus_report_dirs(reports_root: Path, limit: int = 8) -> list[Path]:
    if not reports_root.exists():
        return []
    report_dirs = [
        child
        for child in reports_root.iterdir()
        if child.is_dir() and _looks_like_mechanicus_report_dir(child)
    ]
    report_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return report_dirs[:limit]


def _pick_primary_file(paths: list[Path], contains: str = "") -> Path | None:
    if not paths:
        return None
    if contains:
        contains_upper = contains.upper()
        preferred = [path for path in paths if contains_upper in path.name.upper()]
        if preferred:
            preferred.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return preferred[0]
    paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return paths[0]


def _collect_reports(report_dirs: list[Path], repo_root: Path, limit: int = 6) -> tuple[list[dict[str, Any]], list[Path]]:
    items: list[dict[str, Any]] = []
    receipt_paths: list[Path] = []
    for report_dir in report_dirs[:limit]:
        md_files = list(report_dir.glob("*.md"))
        json_files = list(report_dir.glob("*.json"))
        primary_md = _pick_primary_file(md_files, contains="REPORT")
        primary_json = _pick_primary_file(json_files, contains="mechanicus")
        task_receipt = report_dir / "TASK_RECEIPT.json"
        if task_receipt.exists():
            receipt_paths.append(task_receipt)

        items.append(
            {
                "task_id": report_dir.name,
                "path": str(report_dir),
                "path_repo_relative": _rel(report_dir, repo_root),
                "latest_report_md": str(primary_md) if primary_md else None,
                "latest_report_json": str(primary_json) if primary_json else None,
                "task_receipt": str(task_receipt) if task_receipt.exists() else None,
                "modified_at_utc": _to_iso_utc(report_dir.stat().st_mtime),
            }
        )
    return items, receipt_paths


def _collect_screenshots(
    report_dirs: list[Path],
    repo_root: Path,
    limit: int = 10,
) -> list[dict[str, Any]]:
    screenshot_candidates: list[Path] = []
    for report_dir in report_dirs:
        screenshot_root = report_dir / "SCREENSHOTS"
        if not screenshot_root.exists():
            continue
        for ext in ("*.png", "*.svg", "*.jpg", "*.jpeg", "*.webp"):
            screenshot_candidates.extend(screenshot_root.glob(ext))
    screenshot_candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    items: list[dict[str, Any]] = []
    for screenshot in screenshot_candidates[:limit]:
        task_dir = screenshot.parents[1] if len(screenshot.parents) > 1 else screenshot.parent
        items.append(
            {
                "file_name": screenshot.name,
                "path": str(screenshot),
                "path_repo_relative": _rel(screenshot, repo_root),
                "source_task_id": task_dir.name,
                "modified_at_utc": _to_iso_utc(screenshot.stat().st_mtime),
            }
        )
    return items


def _build_tool_registry_summary(tool_index: dict[str, Any] | None) -> dict[str, Any]:
    if not tool_index:
        return {
            "status": "MISSING",
            "counts": {},
            "top_unavailable_tools": [],
            "generated_at_utc": None,
        }

    tools = tool_index.get("tools", [])
    unavailable: list[dict[str, Any]] = []
    for tool in tools:
        pc_status = str(tool.get("pc_status", "UNKNOWN"))
        if not pc_status.startswith("AVAILABLE"):
            unavailable.append(
                {
                    "tool_id": tool.get("tool_id"),
                    "pc_status": pc_status,
                    "combined_status": tool.get("combined_status"),
                }
            )

    return {
        "status": "CONNECTED",
        "counts": tool_index.get("counts", {}),
        "top_unavailable_tools": unavailable[:6],
        "generated_at_utc": tool_index.get("generated_at_utc") or tool_index.get("updated_at_utc"),
    }


def _build_commands(runner_path: Path, latest_report_path: str | None, latest_screenshot_path: str | None) -> list[dict[str, Any]]:
    runner_cmd = f"python {runner_path.as_posix()}"
    commands = [
        {
            "id": "tui_dashboard",
            "title_en": "Open Mechanicus TUI command",
            "title_ru": "Команда запуска Mechanicus TUI",
            "type": "command",
            "value": f"{runner_cmd} shell --once dashboard",
        },
        {
            "id": "visual_status",
            "title_en": "Run visual-status",
            "title_ru": "Запуск visual-status",
            "type": "command",
            "value": f"{runner_cmd} shell --once visual-status",
        },
        {
            "id": "visual_tools",
            "title_en": "Run visual-tools",
            "title_ru": "Запуск visual-tools",
            "type": "command",
            "value": f"{runner_cmd} shell --once visual-tools",
        },
        {
            "id": "visual_check",
            "title_en": "Run visual-check",
            "title_ru": "Запуск visual-check",
            "type": "command",
            "value": f"{runner_cmd} shell --once visual-check",
        },
        {
            "id": "visual_identity",
            "title_en": "Run visual-identity",
            "title_ru": "Запуск visual-identity",
            "type": "command",
            "value": f"{runner_cmd} shell --once visual-identity",
        },
        {
            "id": "screenshot_all",
            "title_en": "Run screenshot all",
            "title_ru": "Запуск screenshot all",
            "type": "command",
            "value": f"{runner_cmd} shell --screenshot all",
        },
    ]

    commands.append(
        {
            "id": "open_latest_report",
            "title_en": "Open latest report path",
            "title_ru": "Открыть путь к последнему отчёту",
            "type": "path",
            "value": latest_report_path or "MISSING",
        }
    )
    commands.append(
        {
            "id": "open_screenshots",
            "title_en": "Open screenshots folder/path",
            "title_ru": "Открыть путь к скриншотам",
            "type": "path",
            "value": latest_screenshot_path or "MISSING",
        }
    )
    commands.append(
        {
            "id": "show_api_json",
            "title_en": "Show API JSON",
            "title_ru": "Показать API JSON",
            "type": "url",
            "value": "/api/state",
        }
    )
    return commands


def build_mechanicus_snapshot(repo_root: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    now_utc = _utc_now()
    events: list[dict[str, str]] = []

    mechanicus_root = repo_root / "IMPERIUM_NEW_GENERATION" / "ORGAN_AGENTS" / "MECHANICUS_AGENT"
    reports_root = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS"
    tool_index_path = mechanicus_root / "TOOL_REGISTRY" / "TOOL_INDEX.json"
    state_path = mechanicus_root / "state" / "current_status.json"
    profile_path = mechanicus_root / "agent_profile.json"
    runner_path = mechanicus_root / "TOOLS" / "mechanicus_agent_runner.py"

    warnings: list[str] = []
    errors: list[str] = []
    blocks: list[str] = []
    missing_data: list[str] = []

    if mechanicus_root.exists():
        events.append({"status": "PASS", "message": "loaded Mechanicus root"})
    else:
        errors.append("MECHANICUS_ROOT_MISSING")
        missing_data.append(str(mechanicus_root))
        events.append({"status": "ERROR", "message": "missing Mechanicus root"})

    tool_index = _read_json(tool_index_path) if tool_index_path.exists() else None
    if tool_index:
        events.append({"status": "PASS", "message": "loaded tool registry"})
    else:
        warnings.append("TOOL_REGISTRY_MISSING_OR_INVALID")
        missing_data.append(str(tool_index_path))
        events.append({"status": "WARN", "message": "missing tool registry"})

    profile_data = _read_json(profile_path) if profile_path.exists() else None
    state_data = _read_json(state_path) if state_path.exists() else None
    if state_data:
        events.append({"status": "PASS", "message": "loaded Mechanicus state"})
    else:
        warnings.append("MECHANICUS_STATE_MISSING_OR_INVALID")
        missing_data.append(str(state_path))
        events.append({"status": "WARN", "message": "missing Mechanicus state"})

    report_dirs = _latest_mechanicus_report_dirs(reports_root)
    if report_dirs:
        events.append({"status": "PASS", "message": f"found Mechanicus report dirs: {len(report_dirs)}"})
    else:
        warnings.append("MECHANICUS_REPORTS_NOT_FOUND")
        events.append({"status": "WARN", "message": "missing Mechanicus report dirs"})

    reports, receipt_paths = _collect_reports(report_dirs, repo_root)
    screenshots = _collect_screenshots(report_dirs, repo_root)

    if screenshots:
        events.append({"status": "PASS", "message": f"found screenshots: {len(screenshots)}"})
    else:
        warnings.append("MECHANICUS_SCREENSHOTS_NOT_FOUND")
        events.append({"status": "WARN", "message": "missing screenshots"})

    if receipt_paths:
        events.append({"status": "PASS", "message": f"found receipts: {len(receipt_paths)}"})
    else:
        warnings.append("MECHANICUS_RECEIPTS_NOT_FOUND")
        events.append({"status": "WARN", "message": "missing task receipts"})

    latest_report = reports[0]["path"] if reports else None
    latest_screenshot = screenshots[0]["path"] if screenshots else None
    latest_receipt = str(receipt_paths[0]) if receipt_paths else None

    connection_status = "CONNECTED" if (mechanicus_root.exists() and tool_index_path.exists()) else "MISSING"
    connection_quality = "PASS" if connection_status == "CONNECTED" and not errors else "WARN"

    identity = {
        "organ_id": "MECHANICUS_AGENT",
        "display_name": "Mechanicus",
        "profile_source": str(profile_path),
        "profile_version": (profile_data or {}).get("schema_version"),
        "profile_task_id": (profile_data or {}).get("task_id"),
    }

    snapshot = {
        "generated_at_utc": now_utc,
        "status": connection_status,
        "connection_quality": connection_quality,
        "identity": identity,
        "paths": {
            "repo_root": str(repo_root),
            "mechanicus_root": str(mechanicus_root),
            "tool_registry": str(tool_index_path),
            "runner": str(runner_path),
            "reports_root": str(reports_root),
        },
        "tool_registry": _build_tool_registry_summary(tool_index),
        "state_excerpt": state_data if isinstance(state_data, dict) else {},
        "latest_reports": reports,
        "latest_screenshots": screenshots,
        "latest_receipts": [str(path) for path in receipt_paths[:5]],
        "latest_artifacts": {
            "latest_evidence_path": latest_receipt or latest_report,
            "latest_screenshot_path": latest_screenshot,
            "latest_report_path": latest_report,
        },
        "warnings": warnings,
        "errors": errors,
        "blocks": blocks,
        "missing_data": missing_data,
    }

    snapshot["commands"] = _build_commands(runner_path, latest_report, latest_screenshot)
    return snapshot, events
