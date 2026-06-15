from __future__ import annotations

from typing import Dict

SHELL_VERSION_V0_5 = "v0.5"
# Backward-compat aliases for existing imports.
SHELL_VERSION_V0_4 = SHELL_VERSION_V0_5
SHELL_VERSION_V0_3 = SHELL_VERSION_V0_5

MECHANICUS_COLORS: Dict[str, str] = {
    "bg": "#050911",
    "panel_border": "#2f3948",
    "panel_border_soft": "#232c38",
    "panel_border_accent": "#9a5a34",
    "panel_border_warn": "#a57a3a",
    "accent_cyan": "#46d8ff",
    "accent_amber": "#f6b84f",
    "accent_red": "#ff5a52",
    "accent_green": "#63d97a",
    "accent_copper": "#d08a52",
    "text_main": "#dce3ea",
    "text_dim": "#94a0ad",
    "text_muted": "#74808c",
}

STATE_STYLE_MAP: Dict[str, str] = {
    "OK": MECHANICUS_COLORS["accent_green"],
    "READY": MECHANICUS_COLORS["accent_green"],
    "IN_SYNC": MECHANICUS_COLORS["accent_green"],
    "LOADED": MECHANICUS_COLORS["accent_green"],
    "VERIFIED": MECHANICUS_COLORS["accent_cyan"],
    "FOCUS": MECHANICUS_COLORS["accent_cyan"],
    "INFO": MECHANICUS_COLORS["accent_cyan"],
    "WARN": MECHANICUS_COLORS["accent_amber"],
    "ERROR": MECHANICUS_COLORS["accent_red"],
    "BLOCK": MECHANICUS_COLORS["accent_red"],
}


def clip_text(value: str, limit: int = 96) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def state_color(token: str) -> str:
    normalized = token.strip().upper().replace("-", "_")
    return STATE_STYLE_MAP.get(normalized, MECHANICUS_COLORS["text_main"])


def title_line(organ_name: str, mission: str, shell_version: str = SHELL_VERSION_V0_5) -> str:
    clipped_mission = clip_text(mission, 92)
    return (
        f"[bold {MECHANICUS_COLORS['accent_copper']}][COG-SIGIL][/] "
        f"[bold {MECHANICUS_COLORS['accent_red']}]MECHANICUS_AGENT[/] "
        f"[{MECHANICUS_COLORS['text_dim']}]//[/] "
        f"[bold {MECHANICUS_COLORS['accent_cyan']}]OPERATOR_CONSOLE[/] "
        f"[{MECHANICUS_COLORS['text_dim']}]//[/] "
        f"[{MECHANICUS_COLORS['accent_amber']}]shell {shell_version}[/]\n"
        f"[{MECHANICUS_COLORS['text_dim']}]{organ_name} :: {clipped_mission}[/]"
    )
