from __future__ import annotations

import json
from typing import Any, Iterable

from rich.box import SIMPLE_HEAVY
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from operator_shell_skin import MECHANICUS_COLORS, clip_text, state_color, title_line


def _as_rows(values: Iterable[tuple[str, str, str, str]]) -> Table:
    table = Table(box=SIMPLE_HEAVY, show_header=True, expand=True, padding=(0, 1))
    table.add_column("TIME", style=MECHANICUS_COLORS["text_dim"], width=10)
    table.add_column("ITEM", style=MECHANICUS_COLORS["text_main"], width=22)
    table.add_column("DETAIL", style=MECHANICUS_COLORS["text_main"])
    table.add_column("STATE", width=11)
    for t_value, item, detail, state in values:
        style = state_color(state)
        table.add_row(t_value, item, clip_text(detail, 92), f"[{style}]{state}[/]")
    return table


def _normalize_tool_status(token: str) -> str:
    normalized = token.strip().upper()
    if normalized in {"NOT_FOUND_ON_PC", "NOT_FOUND_ON_VM2"}:
        return "MISSING"
    if normalized == "BLOCKED_NOT_ADMITTED":
        return "ERROR"
    if normalized == "UNKNOWN_NEEDS_PROBE":
        return "WARN"
    return normalized


def _status_color(token: str) -> str:
    normalized = _normalize_tool_status(token)
    if normalized.startswith("AVAILABLE"):
        return MECHANICUS_COLORS["accent_green"]
    if normalized in {"KNOWN_NOT_INSTALLED", "WARN"}:
        return MECHANICUS_COLORS["accent_amber"]
    if normalized in {"MISSING", "ERROR"}:
        return MECHANICUS_COLORS["accent_red"]
    return MECHANICUS_COLORS["accent_cyan"]


def _status_counts(payload: dict[str, Any]) -> dict[str, int]:
    counts = {
        "AVAILABLE_BOTH": 0,
        "AVAILABLE_PC": 0,
        "AVAILABLE_VM2": 0,
        "KNOWN_NOT_INSTALLED": 0,
        "MISSING": 0,
        "WARN": 0,
        "ERROR": 0,
    }
    rows = payload.get("tool_rows", [])
    if rows:
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) != 3:
                continue
            status = _normalize_tool_status(str(row[2]))
            if status in counts:
                counts[status] += 1
        return counts

    tool_summary = payload.get("tool_summary", {}) if isinstance(payload.get("tool_summary"), dict) else {}
    preview = tool_summary.get("preview", []) if isinstance(tool_summary.get("preview"), list) else []
    for token in preview:
        item = str(token)
        _, _, status = item.partition(":")
        normalized = _normalize_tool_status(status)
        if normalized in counts:
            counts[normalized] += 1
    return counts


def top_status_panel(payload: dict[str, Any], organ_name: str, mission: str, shell_version: str) -> Panel:
    text = Text.from_markup(title_line(organ_name=organ_name, mission=mission, shell_version=shell_version))
    metric = Table(box=SIMPLE_HEAVY, show_header=True, expand=True, padding=(0, 1))
    metric.add_column("MODE", style=MECHANICUS_COLORS["accent_cyan"], width=12)
    metric.add_column("HEAD", style=MECHANICUS_COLORS["accent_cyan"], width=10)
    metric.add_column("VISUAL", style=MECHANICUS_COLORS["text_main"], width=22)
    metric.add_column("RENDERER", style=MECHANICUS_COLORS["text_main"], width=10)
    metric.add_column("WORKTREE", style=MECHANICUS_COLORS["text_main"], width=10)
    metric.add_column("WARN", style=MECHANICUS_COLORS["accent_amber"], width=6)
    metric.add_column("ERROR", style=MECHANICUS_COLORS["accent_red"], width=7)
    metric.add_column("BLOCK", style=MECHANICUS_COLORS["accent_red"], width=7)
    mode = str(payload.get("mode", "dashboard")).upper()
    visual = str(payload.get("visual_status", "UNKNOWN"))
    renderer = str(payload.get("renderer", "unknown"))
    worktree = "DIRTY" if bool(payload.get("git_dirty", False)) else "CLEAN"
    worktree_style = MECHANICUS_COLORS["accent_amber"] if worktree == "DIRTY" else MECHANICUS_COLORS["accent_green"]
    metric.add_row(
        mode,
        str(payload.get("git_head_short", "UNKNOWN")),
        visual,
        renderer,
        f"[{worktree_style}]{worktree}[/]",
        str(payload.get("warn_count", 0)),
        str(payload.get("error_count", 0)),
        str(payload.get("block_count", 0)),
    )
    return Panel(
        Group(text, metric),
        title="TOP STATUS BAR",
        border_style=MECHANICUS_COLORS["panel_border_accent"],
        padding=(0, 1),
    )


def activity_panel(payload: dict[str, Any]) -> Panel:
    rows = payload.get("activity_rows", [])
    safe_rows: list[tuple[str, str, str, str]] = []
    for row in rows:
        if isinstance(row, tuple) and len(row) == 4:
            safe_rows.append((str(row[0]), str(row[1]), str(row[2]), str(row[3])))
        elif isinstance(row, list) and len(row) == 4:
            safe_rows.append((str(row[0]), str(row[1]), str(row[2]), str(row[3])))
    return Panel(
        _as_rows(safe_rows),
        title="LEFT WORK ZONE // CURRENT ACTIVITY",
        border_style=MECHANICUS_COLORS["panel_border"],
    )


def mission_panel(payload: dict[str, Any], mission: str) -> Panel:
    latest_output = str(payload.get("latest_output", "")).strip() or "shell_ready"
    mode = str(payload.get("mode", "dashboard")).strip().upper()
    content = Text.from_markup(
        f"[bold {MECHANICUS_COLORS['accent_amber']}]MISSION FOCUS[/]\n"
        f"[{MECHANICUS_COLORS['text_main']}]{clip_text(mission, 110)}[/]\n\n"
        f"[bold {MECHANICUS_COLORS['accent_cyan']}]MODE:[/] [{MECHANICUS_COLORS['text_main']}]{mode}[/]\n"
        f"[{MECHANICUS_COLORS['accent_copper']}]Tools / Scripts / Validators / Registry[/]\n"
        f"[{MECHANICUS_COLORS['text_dim']}]Ownership: Mechanicus tooling execution corridor[/]\n"
        f"[{MECHANICUS_COLORS['text_dim']}]Forge. Verify. Automate.[/]\n"
        f"[{MECHANICUS_COLORS['text_muted']}]By the Omnissiah.[/]\n\n"
        f"[{MECHANICUS_COLORS['text_dim']}]latest_output: {clip_text(latest_output, 110)}[/]"
    )
    return Panel(
        content,
        title="LEFT WORK ZONE // MISSION FOCUS",
        border_style=MECHANICUS_COLORS["panel_border_accent"],
        padding=(0, 1),
    )


def command_palette_panel(payload: dict[str, Any]) -> Panel:
    table = Table(box=SIMPLE_HEAVY, show_header=True, expand=True, padding=(0, 1))
    table.add_column("CMD", style=MECHANICUS_COLORS["accent_cyan"], width=14)
    table.add_column("SUMMARY", style=MECHANICUS_COLORS["text_main"])
    table.add_column("KEY", style=MECHANICUS_COLORS["accent_amber"], width=9)
    active_mode = str(payload.get("mode", "dashboard")).strip().lower()
    active_cmd = "status" if active_mode == "dashboard" else active_mode
    for cmd, summary, key in payload.get("palette", [])[:16]:
        token = str(cmd).strip().lower()
        if token == active_cmd:
            cmd_cell = f"[bold {MECHANICUS_COLORS['accent_copper']}]> {cmd}[/]"
        else:
            cmd_cell = f"[{MECHANICUS_COLORS['accent_cyan']}]{cmd}[/]"
        table.add_row(cmd_cell, clip_text(str(summary), 62), str(key))
    return Panel(
        table,
        title="COMMAND ZONE // OPERATOR PALETTE",
        border_style=MECHANICUS_COLORS["panel_border_soft"],
    )


def tool_registry_panel(payload: dict[str, Any]) -> Panel:
    tool_summary = payload.get("tool_summary", {}) if isinstance(payload.get("tool_summary"), dict) else {}
    counts = _status_counts(payload)

    summary_cards = Table(box=SIMPLE_HEAVY, show_header=False, expand=True, padding=(0, 1))
    summary_cards.add_column("R", style=MECHANICUS_COLORS["accent_cyan"])
    summary_cards.add_column("A", style=MECHANICUS_COLORS["accent_green"])
    summary_cards.add_column("N", style=MECHANICUS_COLORS["accent_amber"])
    summary_cards.add_column("M", style=MECHANICUS_COLORS["accent_red"])
    summary_cards.add_column("W", style=MECHANICUS_COLORS["accent_amber"])
    summary_cards.add_column("E", style=MECHANICUS_COLORS["accent_red"])
    summary_cards.add_row(
        f"registered {tool_summary.get('registered_tool_count', 0)}",
        f"available {tool_summary.get('available_tool_count', 0)}",
        f"known_not_installed {counts.get('KNOWN_NOT_INSTALLED', 0)}",
        f"missing {counts.get('MISSING', 0)}",
        f"warn {counts.get('WARN', 0)}",
        f"error {counts.get('ERROR', 0)}",
    )

    table = Table(box=SIMPLE_HEAVY, show_header=True, expand=True, padding=(0, 1))
    table.add_column("TOOL", style=MECHANICUS_COLORS["accent_cyan"], width=24)
    table.add_column("OWNER", style=MECHANICUS_COLORS["text_main"], width=21)
    table.add_column("STATUS", style=MECHANICUS_COLORS["text_main"], width=18)

    rows = payload.get("tool_rows", [])
    if rows:
        for row in rows[:12]:
            if not isinstance(row, (list, tuple)) or len(row) != 3:
                continue
            status_value = _normalize_tool_status(str(row[2]))
            status_style = _status_color(status_value)
            table.add_row(str(row[0]), str(row[1]), f"[{status_style}]{status_value}[/]")
    else:
        preview = tool_summary.get("preview", []) if isinstance(tool_summary.get("preview"), list) else []
        for token in preview[:10]:
            tool_id, _, status = str(token).partition(":")
            status_value = _normalize_tool_status(status or "WARN")
            status_style = _status_color(status_value)
            table.add_row(tool_id or str(token), "MECHANICUS_AGENT", f"[{status_style}]{status_value}[/]")

    caption = (
        "registered="
        f"{tool_summary.get('registered_tool_count', 0)} "
        f"available={tool_summary.get('available_tool_count', 0)} "
        f"missing={tool_summary.get('missing_tool_count', 0)}"
    )
    registry_source = str(tool_summary.get("registry_source", ""))
    registry_line = Text.from_markup(
        f"[{MECHANICUS_COLORS['text_dim']}]path: {clip_text(registry_source, 112)}[/]"
    )
    badges = Text()
    for key in ["AVAILABLE_BOTH", "AVAILABLE_PC", "AVAILABLE_VM2", "KNOWN_NOT_INSTALLED", "MISSING", "WARN", "ERROR"]:
        color = _status_color(key)
        badges.append(f" {key}:{counts.get(key, 0)} ", style=f"bold {color}")
        badges.append(" ", style=MECHANICUS_COLORS["text_muted"])
    return Panel(
        Group(registry_line, summary_cards, badges, table),
        title=f"TOOL REGISTRY // CAPABILITY OVERVIEW [{caption}]",
        border_style=MECHANICUS_COLORS["panel_border_accent"],
    )


def bottom_event_panel(payload: dict[str, Any]) -> Panel:
    lines = payload.get("bottom", []) if isinstance(payload.get("bottom"), list) else []
    text = Text()
    mode = str(payload.get("mode", "dashboard")).upper()
    text.append(f"mode: {mode}\n", style=MECHANICUS_COLORS["accent_cyan"])
    for line in lines:
        text.append(f"{line}\n", style=MECHANICUS_COLORS["text_dim"])
    text.append(
        f"event_summary: WARN={payload.get('warn_count', 0)} "
        f"ERROR={payload.get('error_count', 0)} "
        f"BLOCK={payload.get('block_count', 0)}",
        style=MECHANICUS_COLORS["accent_amber"],
    )
    return Panel(
        text,
        title="BOTTOM EVENT BAR",
        border_style=MECHANICUS_COLORS["panel_border_soft"],
        padding=(0, 1),
    )


def raw_detail_panel(payload: dict[str, Any]) -> Panel:
    raw = payload.get("raw_payload", {})
    dump = json.dumps(raw, ensure_ascii=True, indent=2)
    if len(dump) > 8000:
        dump = dump[:8000] + "\n...<truncated>..."
    return Panel(
        Text(dump, style=MECHANICUS_COLORS["text_main"]),
        title="RAW DETAIL MODE (EXPLICIT)",
        border_style=MECHANICUS_COLORS["accent_amber"],
        padding=(0, 1),
    )
