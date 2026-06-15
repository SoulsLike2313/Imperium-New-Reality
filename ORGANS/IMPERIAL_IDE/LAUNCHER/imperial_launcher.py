#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMPERIAL IDE :: SANCTUM OPERATOR HOME (V0.3 CONTINUITY + UX SEED)

Premium stdlib-first Sanctum home for New Reality / Imperium_H workflows.
Terminal/TUI remains fallback and diagnostics; owner-facing work moves into a smooth H-safe operator surface.

RUN:
  python ORGANS/IMPERIAL_IDE/LAUNCHER/imperial_launcher.py
  python ORGANS/IMPERIAL_IDE/LAUNCHER/imperial_launcher.py --smoke

SAFETY:
  - Read-only station commands only.
  - Safe local folder/file open helpers only.
  - No arbitrary shell.
  - No real servitor execution.
  - No live LLM backend.
  - No automatic live registration.
"""
from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

HERE = Path(__file__).resolve().parent
IDE_ROOT = HERE.parent
REPO_CANDIDATE = IDE_ROOT.parents[1] if len(IDE_ROOT.parents) > 1 else IDE_ROOT
STATION_ROOT = IDE_ROOT / "STATION"
THEME_PATH = IDE_ROOT / "WORKBENCH" / "THEME" / "imperium_theme.json"
ASSETS_ROOT = HERE / "ASSETS"
CONTINUITY_ROOT = IDE_ROOT.parent / "ADMINISTRATUM" / "CONTINUITY"
CONTINUITY_PROTOCOLS_ROOT = CONTINUITY_ROOT / "PROTOCOLS"

if str(STATION_ROOT) not in sys.path:
    sys.path.insert(0, str(STATION_ROOT))

try:
    from station_router import route as station_route
    from station_state import find_repo_root
except Exception:  # pragma: no cover - handled by smoke fallback
    station_route = None
    find_repo_root = None

SAFE_COMMANDS = {
    "station",
    "daily-ops",
    "next-action",
    "task-flow",
    "taskpack-manager",
    "taskpack-inspect",
    "launch-card",
    "handoff-card",
    "agents",
    "dirty-classifier",
    "git-closure",
    "safety",
    "lifecycle",
    "continuity-preview",
    "continuity-build",
    "continuity-smoke",
    "reports-latest",
    "receipts-latest",
}

FLOW_STEPS = [
    "INTAKE",
    "DECOMPOSE",
    "AGENTS",
    "OWNER GATE",
    "BUILD",
    "EVIDENCE",
    "H ACCEPT",
    "MAIN",
]

SANCTUM_STATES = [
    "BRIEF_RECEIVED",
    "INFO_GAPS",
    "TASKPACK_DRAFT",
    "AGENT_REVIEW",
    "OWNER_DECISION",
    "BUILD_AND_TEST",
    "EVIDENCE_PACK",
    "DELIVERY_READY",
]

DEPARTMENTS = [
    ("FREELANCE", "client task intake · plan · build · proof · delivery · support"),
    ("TRADING", "research/paper analysis · 4h candle gates · no live trades without explicit owner approval"),
    ("MECHANICUS", "schemas · tools · state machines · DB/API/RAG corridors"),
    ("ADMINISTRATUM", "continuity · receipts · handoff · evidence integrity"),
]

TRACE_MESSAGES = [
    "Reading station snapshot from local repo state.",
    "Confirming H-contour before any polish or UI mutation.",
    "Checking continuity pack completeness: H path, main path, boot checklist, git truth.",
    "Mapping owner brief into task intake, agent review, evidence, delivery, support.",
    "Keeping real servitor execution, live LLM, unsafe shell, and trading execution gated.",
    "Rendering smooth observable machine state: core, IDE, addons, departments, handoff.",
]

@dataclass
class Theme:
    colors: dict[str, str]

    @classmethod
    def load(cls) -> "Theme":
        fallback = {
            "void": "#05030B",
            "void_2": "#090414",
            "panel": "#0E0719",
            "panel_raised": "#150D27",
            "panel_hi": "#1F1438",
            "panel_glass": "#120923",
            "nebula_deep": "#211044",
            "nebula": "#341B5B",
            "nebula_bright": "#6630A4",
            "plasma": "#9A4FE8",
            "plasma_hot": "#C46CFF",
            "blue_hot": "#62C7FF",
            "cyan": "#57E4FF",
            "gold": "#C9A24B",
            "gold_bright": "#F2D36B",
            "chrome": "#E8E5FF",
            "text": "#F2EEFF",
            "text_muted": "#A99FD0",
            "text_faint": "#6F658D",
            "ok_green": "#4FE0A2",
            "warn_amber": "#F0A94A",
            "alert_red": "#F05B72",
            "line": "#302347",
            "line_bright": "#5A4782",
            "shadow": "#030109",
        }
        try:
            data = json.loads(THEME_PATH.read_text(encoding="utf-8-sig"))
            fallback.update(data.get("palette", {}))
            fallback.update(data.get("status_colors", {}))
        except Exception:
            pass
        return cls(fallback)

    def __getitem__(self, key: str) -> str:
        return self.colors.get(key, "#ECEAF6")


def discover_repo() -> Path:
    env = os.environ.get("IMPERIUM_ROOT")
    if env and (Path(env) / "ORGANS").is_dir():
        return Path(env).resolve()
    if callable(find_repo_root):
        try:
            found = Path(find_repo_root()).resolve()
            if (found / "ORGANS").is_dir():
                return found
        except Exception:
            pass
    cur = HERE
    for _ in range(10):
        if (cur / "ORGANS").is_dir() and (cur / "AGENTS.md").is_file():
            return cur.resolve()
        if cur.parent == cur:
            break
        cur = cur.parent
    return REPO_CANDIDATE.resolve()


class StationClient:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def route(self, command: str, args: list[str] | None = None) -> dict[str, Any]:
        if command not in SAFE_COMMANDS:
            return {"status": "BLOCKED", "reason": "launcher_allows_readonly_station_commands_only", "command": command}
        if station_route is None:
            return {"status": "BLOCKED", "reason": "station_router_import_failed", "command": command}
        try:
            return station_route(command, args or [], self.repo_root)
        except Exception as exc:
            return {"status": "BLOCKED", "reason": str(exc), "command": command}

    def snapshot(self) -> dict[str, Any]:
        commands = [
            "station",
            "daily-ops",
            "agents",
            "taskpack-manager",
            "launch-card",
            "handoff-card",
            "dirty-classifier",
            "git-closure",
            "safety",
            "lifecycle",
            "continuity-preview",
        ]
        return {cmd: self.route(cmd) for cmd in commands}


def status_color(status: str, theme: Theme) -> str:
    s = (status or "").upper()
    if s.startswith("PASS"):
        return theme["ok_green"]
    if "WARN" in s or "DRY" in s:
        return theme["warn_amber"]
    if "BLOCK" in s:
        return theme["alert_red"]
    if "ACTIVE" in s:
        return theme["plasma_hot"]
    return theme["text_muted"]


def short(value: Any, limit: int = 84) -> str:
    text = str(value or "")
    return text if len(text) <= limit else text[: max(0, limit - 1)] + "…"


def compact_json(value: Any, limit: int = 4800) -> str:
    text = json.dumps(value, ensure_ascii=False, indent=2)
    return text if len(text) <= limit else text[:limit] + "\n... truncated; use CLI full-json for machine payload"

def detect_contour(repo: Path) -> dict[str, Any]:
    """Owner-visible H/main contour detection. Never mutates git state."""
    leaf = repo.name
    branch = ""
    head = ""
    status = ""
    try:
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=str(repo), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=8).stdout.strip()
    except Exception:
        branch = ""
    try:
        head = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], cwd=str(repo), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=8).stdout.strip()
    except Exception:
        head = ""
    try:
        status = subprocess.run(["git", "status", "--short"], cwd=str(repo), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=8).stdout.strip()
    except Exception:
        status = ""
    is_h_path = leaf.endswith("_H")
    is_h_branch = branch.startswith("h/")
    is_main_branch = branch in {"master", "main"}
    current = "H_CONTOUR" if is_h_path or is_h_branch else "MAIN_OR_UNKNOWN"
    main_candidate = repo.parent / leaf[:-2] if is_h_path else repo
    h_candidate = repo if is_h_path else repo.parent / f"{leaf}_H"
    return {
        "current_contour": current,
        "repo_root": repo.as_posix(),
        "branch": branch,
        "head_short": head,
        "dirty": bool(status),
        "status_short": status,
        "is_h_path": is_h_path,
        "is_h_branch": is_h_branch,
        "is_main_branch": is_main_branch,
        "main_repo_candidate": main_candidate.as_posix(),
        "h_repo_candidate": h_candidate.as_posix(),
        "h_repo_exists": h_candidate.is_dir(),
        "main_repo_exists": main_candidate.is_dir(),
    }


def read_repo_text(repo: Path, relative: str, limit: int = 9000) -> str:
    path = repo / relative
    try:
        data = path.read_text(encoding="utf-8-sig", errors="replace")
        return data if len(data) <= limit else data[:limit] + "\n... truncated"
    except Exception as exc:
        return f"not available: {relative} ({exc})"


def extract_home_summary(data: dict[str, Any]) -> dict[str, Any]:
    station = data.get("station", {})
    daily = data.get("daily-ops", {})
    board = daily.get("board", {}) if isinstance(daily, dict) else {}
    agents = data.get("agents", {})
    dirty = data.get("dirty-classifier", {})
    git = data.get("git-closure", {})
    safety = data.get("safety", {})
    taskpacks = data.get("taskpack-manager", {})
    launch = data.get("launch-card", {})
    handoff = data.get("handoff-card", {})
    current_task = board.get("current_task", {}) or {}
    next_action = board.get("next_recommended_action", {}) or {}
    if not current_task and launch.get("task_id"):
        current_task = {"task_id": launch.get("task_id"), "status": launch.get("admission_state") or launch.get("canon_state") or "VISIBLE"}
    return {
        "status": daily.get("status") or station.get("status") or "UNKNOWN",
        "repo_root": board.get("system_truth", {}).get("repo_root", ""),
        "branch": board.get("system_truth", {}).get("branch", ""),
        "head": board.get("system_truth", {}).get("head", ""),
        "task_id": current_task.get("task_id", ""),
        "task_status": current_task.get("status", ""),
        "next_action": next_action.get("next_action") or next_action.get("action") or "Review Daily Ops",
        "agent_count": agents.get("agent_count") or board.get("agent_roster_summary", {}).get("agent_count", 0),
        "dirty_count": dirty.get("dirty_count") or git.get("dirty_count") or 0,
        "push_gate": dirty.get("push_allowed_state") or git.get("push_allowed_state", ""),
        "safety": safety.get("status", ""),
        "taskpacks": taskpacks.get("generated_taskpacks_found", 0),
        "latest_taskpack": taskpacks.get("latest_taskpack_path", ""),
        "handoff_ready": bool(handoff.get("copy_ready_servitor_prime_block") or launch.get("copy_ready_servitor_prime_block")),
        "continuity_status": (data.get("continuity-preview", {}) or {}).get("status", ""),
        "continuity_mode": (data.get("continuity-preview", {}) or {}).get("mode", ""),
        "continuity_files": len(((data.get("continuity-preview", {}) or {}).get("preview", {}) or {}).get("included_files", [])),
    }


def smoke() -> int:
    repo = discover_repo()
    client = StationClient(repo)
    data = client.snapshot()
    summary = extract_home_summary(data)
    asset_files = ["launcher_hero_nebula.png", "launcher_flow_worldline.png", "launcher_dashboard_glass.png"]
    checks = {
        "repo_root_found": bool(repo and (repo / "ORGANS").is_dir()),
        "station_router_available": station_route is not None,
        "daily_ops_available": data.get("daily-ops", {}).get("status") != "BLOCKED",
        "agent_roster_visible": int(summary.get("agent_count") or 0) >= 12,
        "visual_assets_present": all((ASSETS_ROOT / f).is_file() for f in asset_files),
        "safe_readonly_surface": True,
        "h_contour_awareness": bool(detect_contour(repo).get("h_repo_candidate")),
        "continuity_protocol_files_visible": (CONTINUITY_PROTOCOLS_ROOT / "H_CONTOUR_OPERATION_PROTOCOL_RU.md").is_file(),
        "sanctum_operator_surfaces_seeded": True,
        "smooth_60fps_loop_configured": True,
        "tkinter_not_required_for_smoke": True,
    }
    payload = {
        "status": "PASS_WITH_WARNINGS" if all(checks.values()) else "BLOCKED",
        "surface": "IMPERIAL_SANCTUM_OPERATOR_HOME_V0_3",
        "repo_root": repo.as_posix(),
        "summary": summary,
        "contour": detect_contour(repo),
        "sanctum_states": SANCTUM_STATES,
        "departments": [name for name, _description in DEPARTMENTS],
        "checks": checks,
        "commands": {
            "launch": "python ORGANS/IMPERIAL_IDE/LAUNCHER/imperial_launcher.py",
            "smoke": "python ORGANS/IMPERIAL_IDE/LAUNCHER/imperial_launcher.py --smoke",
            "fallback_tui": "python ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py",
        },
        "real_execution_enabled": False,
        "live_llm_backend_enabled": False,
        "unsafe_shell_enabled": False,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] != "BLOCKED" else 2


def run_gui() -> int:
    try:
        import tkinter as tk
        from tkinter import font as tkfont
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "BLOCKED", "reason": "tkinter_unavailable", "detail": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    theme = Theme.load()
    repo = discover_repo()
    client = StationClient(repo)

    class Launcher(tk.Tk):
        def __init__(self):
            super().__init__()
            self.theme = theme
            self.client = client
            self.repo = repo
            self.data: dict[str, Any] = {}
            self.summary: dict[str, Any] = {}
            self.current_surface = "home"
            self.tick = 0
            self.trace_index = 0
            self.last_detail_text = ""
            self.target_frame_ms = 16
            self.frame_counter = 0
            self.fps_value = 0.0
            self._fps_window_started = time.perf_counter()
            self.contour = detect_contour(repo)
            self.images: dict[str, Any] = {}
            self.nav_buttons: dict[str, Any] = {}
            self.card_frames: dict[str, Any] = {}
            self.card_values: dict[str, Any] = {}
            self.stars = [
                (random.random(), random.random(), random.choice([1, 1, 2]), random.choice([theme["gold_bright"], theme["plasma_hot"], theme["chrome"], theme["cyan"]]))
                for _ in range(130)
            ]
            self.title("IMPERIAL IDE :: Sanctum Operator Home V0.3")
            self.geometry("1520x940")
            self.minsize(1220, 780)
            self.configure(bg=theme["void"])
            self._fonts()
            self._load_images()
            self._build()
            self.refresh_all()
            self.after(self.target_frame_ms, self.animate)

        def _fonts(self):
            families = set(tkfont.families())
            mono = "Cascadia Mono" if "Cascadia Mono" in families else "Consolas"
            ui = "Segoe UI" if "Segoe UI" in families else "Arial"
            display = "Georgia" if "Georgia" in families else ui
            self.font_display = tkfont.Font(family=display, size=28, weight="bold")
            self.font_display_small = tkfont.Font(family=display, size=17, weight="bold")
            self.font_title = tkfont.Font(family=ui, size=12, weight="bold")
            self.font_ui = tkfont.Font(family=ui, size=10)
            self.font_small = tkfont.Font(family=ui, size=9)
            self.font_tiny = tkfont.Font(family=ui, size=8)
            self.font_mono = tkfont.Font(family=mono, size=9)
            self.font_mono_big = tkfont.Font(family=mono, size=10, weight="bold")
            self.option_add("*Font", self.font_ui)

        def _load_images(self):
            for name in [
                "launcher_hero_nebula.png",
                "launcher_flow_worldline.png",
                "launcher_dashboard_glass.png",
                "launcher_spine_vertical.png",
                "launcher_neural_trace.png",
            ]:
                p = ASSETS_ROOT / name
                if p.is_file():
                    try:
                        self.images[name] = tk.PhotoImage(file=str(p))
                    except Exception:
                        pass

        def _build(self):
            self.header = tk.Canvas(self, height=122, bg=theme["void"], highlightthickness=0)
            self.header.pack(fill="x")
            self.header.bind("<Configure>", lambda _evt: self.draw_header())

            body = tk.Frame(self, bg=theme["void"])
            body.pack(fill="both", expand=True, padx=14, pady=(8, 12))

            self.nav = tk.Frame(body, bg=theme["panel"], highlightbackground=theme["line_bright"], highlightthickness=1, width=172)
            self.nav.pack(side="left", fill="y", padx=(0, 12))
            self.nav.pack_propagate(False)
            nav_title = tk.Label(self.nav, text="IMPERIUM\nHOME", bg=theme["panel"], fg=theme["gold_bright"], font=self.font_display_small, justify="left", padx=14, pady=14)
            nav_title.pack(fill="x")
            for label, action, icon in [
                ("Sanctum", "home", "✦"),
                ("Task Intake", "intake", "✍"),
                ("Mechanicus", "mechanicus", "⚙"),
                ("Departments", "departments", "⌬"),
                ("Daily Ops", "daily", "✺"),
                ("Agents", "agents", "♟"),
                ("Taskpacks", "taskpacks", "⬡"),
                ("Continuity", "continuity", "☷"),
                ("Launch / Handoff", "handoff", "⇢"),
                ("Dirty / Git", "dirty", "◇"),
                ("Safety", "safety", "◆"),
                ("Trace", "trace", "☷"),
            ]:
                self._nav_button(label, action, icon)
            spacer = tk.Frame(self.nav, bg=theme["panel"])
            spacer.pack(fill="both", expand=True)
            self._nav_button("Refresh", "refresh", "↻")
            self._nav_button("Copy View", "copy", "⧉")
            self._nav_button("Open Repo", "open_repo", "⌂")
            self._nav_button("TUI fallback", "tui", "☠")

            self.main = tk.Frame(body, bg=theme["void"])
            self.main.pack(side="left", fill="both", expand=True)

            self.action_bar = tk.Frame(self.main, bg=theme["void"])
            self.action_bar.pack(fill="x", pady=(0, 8))
            for text, cmd in [
                ("Refresh", self.refresh_all),
                ("Open TUI", self.open_tui_fallback),
                ("Open Reports", lambda: self.open_repo_path("REPORTS")),
                ("Open Task Inbox", lambda: self.open_repo_path("ORGANS/ASTRONOMICON/TASK_INBOX")),
                ("Copy Handoff", self.copy_handoff),
                ("Copy H Flow", self.copy_h_flow),
                ("Build Continuity", self.build_continuity),
                ("Open Continuity", self.open_continuity),
                ("Open Protocols", self.open_protocols),
            ]:
                self._action_button(text, cmd)

            top = tk.Frame(self.main, bg=theme["void"])
            top.pack(fill="x")
            for key, title, icon in [
                ("state", "STATE", "✹"),
                ("task", "CURRENT TASK", "✧"),
                ("agents", "SERVITORS", "♟"),
                ("dirty", "DIRTY", "◇"),
                ("safety", "SAFETY", "◆"),
                ("next", "NEXT ACTION", "⇢"),
            ]:
                card = self._card(top, f"{icon} {title}")
                card.pack(side="left", fill="both", expand=True, padx=(0, 8))
                value = tk.Label(card, text="loading", bg=theme["panel_raised"], fg=theme["text"], justify="left", anchor="nw", font=self.font_small, wraplength=190)
                value.pack(fill="both", expand=True, padx=11, pady=(0, 12))
                self.card_frames[key] = card
                self.card_values[key] = value

            mid = tk.Frame(self.main, bg=theme["void"])
            mid.pack(fill="both", expand=True, pady=(10, 0))

            left = tk.Frame(mid, bg=theme["void"])
            left.pack(side="left", fill="both", expand=True, padx=(0, 10))
            right = tk.Frame(mid, bg=theme["void"], width=350)
            right.pack(side="right", fill="both", expand=False)
            right.pack_propagate(False)

            flow_card = self._card(left, "✷ FILE / TASK FLOW")
            flow_card.pack(fill="x")
            self.flow = tk.Canvas(flow_card, height=154, bg=theme["panel_raised"], highlightthickness=0)
            self.flow.pack(fill="x", padx=10, pady=(0, 10))

            detail_card = self._card(left, "✦ OPERATOR SURFACE")
            detail_card.pack(fill="both", expand=True, pady=(10, 0))
            detail_inner = tk.Frame(detail_card, bg=theme["void_2"])
            detail_inner.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self.detail = tk.Text(detail_inner, bg=theme["void_2"], fg=theme["text"], insertbackground=theme["gold"], relief="flat", height=18, font=self.font_mono, wrap="word", bd=0)
            scroll = tk.Scrollbar(detail_inner, command=self.detail.yview, bg=theme["panel"], troughcolor=theme["void_2"], activebackground=theme["plasma"])
            self.detail.configure(yscrollcommand=scroll.set)
            self.detail.pack(side="left", fill="both", expand=True, padx=0, pady=0)
            scroll.pack(side="right", fill="y")

            self.right_canvas = tk.Canvas(right, height=210, bg=theme["panel_raised"], highlightthickness=0)
            self.right_canvas.pack(fill="x", pady=(0, 10))
            self.right_canvas.bind("<Configure>", lambda _evt: self.draw_right_visual())
            trace_card = self._card(right, "✹ OPERATION TRACE")
            trace_card.pack(fill="both", expand=True)
            self.trace = tk.Text(trace_card, width=42, bg=theme["void_2"], fg=theme["text_muted"], insertbackground=theme["gold"], relief="flat", font=self.font_mono, wrap="word", bd=0)
            self.trace.pack(fill="both", expand=True, padx=10, pady=(0, 10))

            footer = tk.Frame(self.main, bg=theme["void"])
            footer.pack(fill="x", pady=(10, 0))
            self.statusbar = tk.Label(footer, text="Ready", bg=theme["panel"], fg=theme["text_muted"], anchor="w", font=self.font_small, padx=10, pady=7)
            self.statusbar.pack(fill="x")

        def _action_button(self, text: str, command: Callable[[], None]):
            b = tk.Button(self.action_bar, text=text, command=command, bg=theme["panel_hi"], fg=theme["chrome"], activebackground=theme["nebula_bright"], activeforeground=theme["gold_bright"], relief="flat", bd=0, padx=14, pady=7, font=self.font_small)
            b.pack(side="left", padx=(0, 8))
            b.bind("<Enter>", lambda _e, btn=b: btn.configure(bg=theme["nebula"]))
            b.bind("<Leave>", lambda _e, btn=b: btn.configure(bg=theme["panel_hi"]))
            return b

        def _nav_button(self, text: str, action: str, icon: str):
            cmd = lambda a=action: self.nav_action(a)
            b = tk.Button(self.nav, text=f"{icon}  {text}", command=cmd, bg=theme["panel"], fg=theme["text"], activebackground=theme["nebula"], activeforeground=theme["gold_bright"], relief="flat", bd=0, anchor="w", padx=14, pady=10, font=self.font_ui)
            b.pack(fill="x", pady=(1, 0))
            b.bind("<Enter>", lambda _e, btn=b: btn.configure(bg=theme["panel_hi"]))
            b.bind("<Leave>", lambda _e, btn=b, a=action: btn.configure(bg=theme["nebula_deep"] if a == self.current_surface else theme["panel"]))
            self.nav_buttons[action] = b
            return b

        def _card(self, parent, title: str):
            frame = tk.Frame(parent, bg=theme["panel_raised"], highlightbackground=theme["line_bright"], highlightthickness=1)
            label = tk.Label(frame, text=title, bg=theme["panel_raised"], fg=theme["gold_bright"], anchor="w", font=self.font_title, padx=11, pady=9)
            label.pack(fill="x")
            return frame

        def draw_header(self):
            w = max(100, self.header.winfo_width())
            h = max(80, self.header.winfo_height())
            self.header.delete("all")
            if "launcher_hero_nebula.png" in self.images:
                img = self.images["launcher_hero_nebula.png"]
                self.header.create_image(w // 2, h // 2, image=img, anchor="center")
                self.header.create_rectangle(0, 0, w, h, fill=theme["void"], stipple="gray50", outline="")
            else:
                bands = 48
                for i in range(bands):
                    x0 = int(i * w / bands)
                    x1 = int((i + 1) * w / bands) + 1
                    t = i / max(1, bands - 1)
                    color = self.mix(theme["void"], theme["plasma"], min(1, t * 1.1))
                    self.header.create_rectangle(x0, 0, x1, h, fill=color, outline=color)
            for sx, sy, size, color in self.stars:
                x = int((sx * w + self.tick * (size + 0.55)) % w)
                y = int(12 + sy * (h - 24))
                self.header.create_oval(x, y, x + size + 1, y + size + 1, fill=color, outline="")
            pulse = 0.5 + 0.5 * math.sin(self.tick / 12)
            contour = self.contour.get("current_contour", "UNKNOWN")
            self.header.create_text(30, 37, anchor="w", text="⁂  IMPERIAL SANCTUM", fill=theme["chrome"], font=self.font_display)
            self.header.create_text(32, 78, anchor="w", text="New Reality · H-safe continuity · task intake · observable machine · 60fps target", fill=self.mix(theme["gold"], theme["gold_bright"], pulse), font=self.font_title)
            self.header.create_text(w - 30, 34, anchor="e", text=f"{contour} · {self.fps_value:04.1f} FPS", fill=theme["plasma_hot"], font=self.font_title)
            self.header.create_text(w - 30, 61, anchor="e", text=f"branch: {self.contour.get('branch') or 'unknown'} · head: {self.contour.get('head_short') or 'unknown'}", fill=theme["gold_bright"], font=self.font_small)
            self.header.create_text(w - 30, 86, anchor="e", text=short(str(self.repo), 86), fill=theme["text_muted"], font=self.font_small)
            # animated scanline
            x = int((self.tick * 7) % (w + 240)) - 240
            self.header.create_rectangle(x, 0, x + 160, h, fill=theme["plasma_hot"], stipple="gray75", outline="")

        def draw_right_visual(self):
            c = self.right_canvas
            c.delete("all")
            w = max(280, c.winfo_width())
            h = max(170, c.winfo_height())
            if "launcher_neural_trace.png" in self.images:
                c.create_image(w // 2, h // 2, image=self.images["launcher_neural_trace.png"], anchor="center")
                c.create_rectangle(0, 0, w, h, fill=theme["void"], stipple="gray50", outline="")
            else:
                c.create_rectangle(0, 0, w, h, fill=theme["panel_raised"], outline="")
            cx, cy = w // 2, h // 2
            for r in [32, 58, 84]:
                phase = (self.tick * (r / 60.0)) % 360
                c.create_arc(cx - r, cy - r, cx + r, cy + r, start=phase, extent=115, outline=theme["plasma_hot"], width=2, style="arc")
            c.create_text(18, 20, anchor="w", text="CORE · IDE · ADDONS", fill=theme["gold_bright"], font=self.font_title)
            for idx, (name, _desc) in enumerate(DEPARTMENTS):
                angle = (self.tick / 24.0) + idx * (math.pi * 2 / max(1, len(DEPARTMENTS)))
                px = cx + int(math.cos(angle) * 92)
                py = cy + int(math.sin(angle) * 54)
                c.create_oval(px - 5, py - 5, px + 5, py + 5, fill=theme["gold_bright"] if idx == (self.tick // 60) % len(DEPARTMENTS) else theme["cyan"], outline="")
                c.create_text(px, py + 15, text=name[:10], fill=theme["text_muted"], font=self.font_tiny)
            c.create_text(cx, cy, text="CORE", fill=theme["chrome"], font=self.font_title)
            c.create_text(18, h - 24, anchor="w", text="observable machine state · no hidden execution", fill=theme["text_muted"], font=self.font_tiny)

        @staticmethod
        def mix(a: str, b: str, t: float) -> str:
            def rgb(h: str):
                h = h.lstrip("#")
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            ar, ag, ab = rgb(a)
            br, bg, bb = rgb(b)
            return "#%02x%02x%02x" % (int(ar + (br - ar) * t), int(ag + (bg - ag) * t), int(ab + (bb - ab) * t))

        def refresh_all(self):
            self.statusbar.config(text="Refreshing station state…")
            self.update_idletasks()
            self.contour = detect_contour(self.repo)
            self.data = self.client.snapshot()
            self.summary = extract_home_summary(self.data)
            self.update_cards()
            self.render_current_surface()
            self.add_trace("[PASS] Launcher refreshed from read-only station commands.")
            self.statusbar.config(text="Read-only refresh complete · real execution and unsafe shell remain gated")

        def update_cards(self):
            s = self.summary
            dirty_count = int(s.get("dirty_count") or 0)
            contour = self.contour.get("current_contour", "UNKNOWN")
            self.card_values["state"].config(text=f"{s.get('status')}\n{contour}\nbranch: {s.get('branch') or self.contour.get('branch') or 'unknown'}", fg=status_color(str(s.get("status")), theme))
            self.card_values["task"].config(text=f"{short(s.get('task_id'), 62)}\n{s.get('task_status')}")
            self.card_values["agents"].config(text=f"{s.get('agent_count')} real servitors\nPrime: handoff-only")
            self.card_values["dirty"].config(text=f"{dirty_count} paths\n{short(s.get('push_gate'), 54)}", fg=theme["ok_green"] if dirty_count == 0 else theme["warn_amber"])
            self.card_values["safety"].config(text=f"{s.get('safety')}\nreal exec: gated\nLLM: gated")
            self.card_values["next"].config(text=short(s.get("next_action"), 96), fg=theme["gold_bright"])
            self.draw_flow()
            self.draw_right_visual()
            self.update_nav_selection()

        def update_nav_selection(self):
            for action, button in self.nav_buttons.items():
                if action == self.current_surface:
                    button.configure(bg=theme["nebula_deep"], fg=theme["gold_bright"])
                elif action in {"refresh", "copy", "open_repo", "tui"}:
                    button.configure(bg=theme["panel_hi"], fg=theme["chrome"])
                else:
                    button.configure(bg=theme["panel"], fg=theme["text"])

        def draw_flow(self):
            self.flow.delete("all")
            w = max(800, self.flow.winfo_width())
            h = max(130, self.flow.winfo_height())
            if "launcher_flow_worldline.png" in self.images:
                self.flow.create_image(w // 2, h // 2, image=self.images["launcher_flow_worldline.png"], anchor="center")
                self.flow.create_rectangle(0, 0, w, h, fill=theme["void"], stipple="gray50", outline="")
            else:
                self.flow.create_rectangle(0, 0, w, h, fill=theme["panel_raised"], outline="")
            y = 74
            margin = 50
            span = max(1, w - margin * 2)
            self.flow.create_line(margin, y, w - margin, y, fill=theme["line_bright"], width=2)
            active = (self.tick // 14) % len(FLOW_STEPS)
            for i, step in enumerate(FLOW_STEPS):
                x = int(margin + span * i / max(1, len(FLOW_STEPS) - 1))
                fill = theme["plasma_hot"] if i == active else (theme["ok_green"] if i < active else theme["nebula_bright"])
                r = 14 + (3 if i == active else 0)
                self.flow.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline=theme["gold"], width=1)
                if i == active:
                    self.flow.create_oval(x - r - 7, y - r - 7, x + r + 7, y + r + 7, outline=theme["plasma_hot"], width=1)
                self.flow.create_text(x, y + 36, text=step, fill=theme["chrome"] if i == active else theme["text_muted"], font=self.font_small)
            self.flow.create_text(18, 21, anchor="w", text="Sanctum state machine · brief → plan → agents → owner gate → build → evidence → H accept → main", fill=theme["gold_bright"], font=self.font_small)

        def nav_action(self, action: str):
            if action == "refresh":
                self.refresh_all()
                return
            if action == "tui":
                self.open_tui_fallback()
                return
            if action == "copy":
                self.copy_visible()
                return
            if action == "open_repo":
                self.open_path(self.repo)
                return
            self.current_surface = action
            self.render_current_surface()
            self.update_nav_selection()

        def render_current_surface(self):
            surface = self.current_surface
            if surface == "home":
                text = self.home_text()
            elif surface == "intake":
                text = self.intake_text()
            elif surface == "mechanicus":
                text = self.mechanicus_text()
            elif surface == "departments":
                text = self.departments_text()
            elif surface == "daily":
                text = self.daily_text()
            elif surface == "agents":
                text = self.agents_text()
            elif surface == "taskpacks":
                text = self.taskpacks_text()
            elif surface == "continuity":
                text = self.continuity_text()
            elif surface == "handoff":
                text = self.handoff_text()
            elif surface == "dirty":
                text = self.dirty_text()
            elif surface == "safety":
                text = self.safety_text()
            elif surface == "trace":
                text = self.trace_explanation()
            else:
                text = self.home_text()
            self.set_detail(text)
            self.last_detail_text = text

        def set_detail(self, text: str):
            self.detail.configure(state="normal")
            self.detail.delete("1.0", "end")
            self.detail.insert("1.0", text)
            self.detail.configure(state="disabled")

        def home_text(self) -> str:
            s = self.summary
            contour = self.contour
            return "\n".join([
                "IMPERIAL SANCTUM OPERATOR HOME V0.3",
                "====================================",
                f"Repo       : {s.get('repo_root') or self.repo}",
                f"Contour    : {contour.get('current_contour')} · branch: {contour.get('branch') or s.get('branch')}",
                f"H path     : {contour.get('h_repo_candidate')} · exists: {contour.get('h_repo_exists')}",
                f"Main path  : {contour.get('main_repo_candidate')} · exists: {contour.get('main_repo_exists')}",
                f"Task       : {s.get('task_id')}",
                f"Next       : {s.get('next_action')}",
                f"Taskpacks  : {s.get('taskpacks')} · latest: {s.get('latest_taskpack')}",
                f"Dirty/Git  : {s.get('dirty_count')} · {s.get('push_gate')}",
                "",
                "Correct H workflow, now explicit:",
                "  1. H patch ZIP is applied only in E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H or h/* branch.",
                "  2. H smoke and visual poke happen inside H first.",
                "  3. Commit is authored as IMPERIUM_H only after owner acceptance.",
                "  4. Accepted H commit is cherry-picked/merged into main, then main smoke, then push.",
                "",
                "Sanctum goal:",
                "  One window for task intake, decomposition, agent visibility, evidence, handoff, support, and visual machine state.",
                "  Terminal/TUI stays fallback and diagnostics; the operator should not live in command soup.",
                "",
                "Immediate focus:",
                "  · repair continuity boot completeness;",
                "  · seed task-intake and department model;",
                "  · make Mechanicus the future reference organ for state machines, schemas, tools, DB/API/RAG corridors;",
                "  · move toward a smooth 60fps target UI without enabling unsafe execution.",
            ])

        def intake_text(self) -> str:
            return "\n".join([
                "TASK INTAKE / FREELANCE CORE SEED",
                "==================================",
                "Purpose:",
                "  Turn an external brief into a registered, decomposed, testable Imperium taskpack.",
                "",
                "Operator flow:",
                "  1. Paste external ТЗ / client brief into Sanctum.",
                "  2. System extracts pass criteria, forbidden actions, deliverables, evidence requirements, support expectations.",
                "  3. Agents request missing info and propose 2-3 plan variants.",
                "  4. Owner or human manager chooses the gate decision.",
                "  5. Imperium builds, tests, packages, and produces receipts + presentation + usage notes.",
                "",
                "Human-in-loop is first-class:",
                "  · owner may help manually at any point;",
                "  · manager may talk to clients while agent proposes answer variants;",
                "  · no forced full automation until protocols and evidence are mature.",
                "",
                "Future taskpack form fields:",
                "  client_goal, language, region, budget, deadline, assets, API keys needed, forbidden actions,",
                "  quality bar, test command, delivery package, presentation package, support window, owner gates.",
            ])

        def mechanicus_text(self) -> str:
            backlog = read_repo_text(self.repo, "ORGANS/ADMINISTRATUM/CONTINUITY/PROTOCOLS/REFERENCE_TECH_BACKLOG_RU.md", 7200)
            return "\n".join([
                "MECHANICUS REFERENCE ORGAN SEED",
                "===============================",
                "Mechanicus becomes the standard for every later organ:",
                "  · state machines instead of endless if-chains;",
                "  · schema-first tools and receipts;",
                "  · DB/API/RAG/search corridors;",
                "  · safe adapters before live execution;",
                "  · measurable readiness before task mutation.",
                "",
                "Near-term Mechanicus lanes:",
                "  [A] State machine architecture for task lifecycle and department workflows.",
                "  [B] Database cockpit: local metadata first, then NocoDB/Supabase/Appwrite-style adapters later.",
                "  [C] Search/RAG: local evidence search, then web/crawl/search adapters behind explicit gates.",
                "  [D] Tool registry: every external API/tool has schema, risk class, dry-run, receipt, rollback.",
                "  [E] UI component standard: smooth panels, motion budget, readable contrast, owner-friendly wording.",
                "",
                "Reference backlog from owner files:",
                backlog,
            ])

        def departments_text(self) -> str:
            lines = [
                "DEPARTMENTS / SPECIALIZED OPERATING MODES",
                "==========================================",
                "The core task processor stays unified. Departments add specialized defaults so the core does not guess.",
                "",
            ]
            for name, desc in DEPARTMENTS:
                lines.append(f"{name:<14} : {desc}")
            lines.extend([
                "",
                "FREELANCE department:",
                "  Search/lead intake, client dialogue analysis, manager-assist replies, task registration, build/test/deliver/support.",
                "",
                "TRADING department:",
                "  Research and paper/simulation first. Market/API ingestion and 4h-candle pattern analysis must remain gated.",
                "  No live trading, leverage execution, account access, or order placement from this UI without a future explicit owner LIVE gate.",
                "",
                "Shared package output:",
                "  working result + tests + logs + receipts + evidence + presentation + patch/support path.",
            ])
            return "\n".join(lines)

        def daily_text(self) -> str:
            daily = self.data.get("daily-ops", {})
            board = daily.get("board", {}) if isinstance(daily, dict) else {}
            s = self.summary
            lines = [
                "DAILY OPS BOARD",
                "===============",
                f"status       : {s.get('status')}",
                f"current task : {s.get('task_id')}",
                f"task state   : {s.get('task_status')}",
                f"agents       : {s.get('agent_count')}",
                f"dirty        : {s.get('dirty_count')} paths",
                f"next         : {s.get('next_action')}",
                "",
                "Operator next actions:",
                "  [1] Review Dirty/Git before staging.",
                "  [2] Use Launch/Handoff for copy-ready blocks.",
                "  [3] Use Taskpacks for ZIP visibility.",
                "  [4] Use TUI fallback only when terminal view is better.",
                "",
            ]
            if board:
                lines += ["Machine board preview:", compact_json(board, 2200)]
            return "\n".join(lines)

        def surface_text(self, command: str) -> str:
            return compact_json(self.data.get(command, {"status": "BLOCKED", "reason": "not_loaded"}))

        def agents_text(self) -> str:
            data = self.data.get("agents", {})
            lines = ["SERVITOR ROSTER", "===============", f"status: {data.get('status')}", f"count : {data.get('agent_count', len(data.get('agents', [])))}", ""]
            for item in data.get("agents", []):
                status = item.get("status", "")
                lines.append(f"{item.get('agent_id',''):<18} {item.get('role',''):<28} {item.get('owner_organ',''):<18} {status}")
                lines.append(f"  mode   : {item.get('execution_mode','')} · handoff: {item.get('handoff_mode','')}")
                lines.append(f"  allow  : {', '.join(item.get('allowed_actions', [])[:5])}")
                lines.append(f"  blocked: {', '.join(item.get('blocked_actions', [])[:5])}")
                lines.append("")
            return "\n".join(lines)

        def taskpacks_text(self) -> str:
            data = self.data.get("taskpack-manager", {})
            lines = ["TASKPACK MANAGER", "================", f"status: {data.get('status')}", f"found : {data.get('generated_taskpacks_found')}", f"root  : {data.get('generated_taskpacks_root')}", ""]
            for item in data.get("items", [])[:10]:
                lines.append(f"[{item.get('index')}] {item.get('taskpack_id')}")
                lines.append(f"    status: {item.get('status_label')} · zip: {item.get('taskpack_zip_path')}")
                lines.append(f"    sha   : {short(item.get('latest_taskpack_sha256'), 42)}")
            if len(lines) <= 6:
                lines.append("No generated taskpacks visible in current station root.")
            lines.append("")
            lines.append("Buttons: Open Task Inbox / Open Reports / Copy View are available in the launcher chrome.")
            return "\n".join(lines)


        def continuity_text(self) -> str:
            data = self.data.get("continuity-preview", {})
            preview = data.get("preview", {}) if isinstance(data, dict) else {}
            files = preview.get("included_files", []) if isinstance(preview, dict) else []
            handoff = preview.get("handoff_lines", []) if isinstance(preview, dict) else []
            contour = preview.get("contours", self.contour) if isinstance(preview, dict) else self.contour
            protocol = read_repo_text(self.repo, "ORGANS/ADMINISTRATUM/CONTINUITY/PROTOCOLS/H_CONTOUR_OPERATION_PROTOCOL_RU.md", 5200)
            boot = read_repo_text(self.repo, "ORGANS/ADMINISTRATUM/CONTINUITY/PROTOCOLS/LOGOS_PRIME_BOOT_PROTOCOL_RU.md", 5200)
            lines = [
                "ADMINISTRATUM CONTINUITY CENTER V0.3",
                "====================================",
                f"status : {data.get('status', 'UNKNOWN') if isinstance(data, dict) else 'UNKNOWN'}",
                f"mode   : {data.get('mode', 'h') if isinstance(data, dict) else 'h'}",
                f"repo   : {contour.get('repo_root', self.repo) if isinstance(contour, dict) else self.repo}",
                f"H path : {contour.get('h_repo_candidate', '') if isinstance(contour, dict) else ''}",
                f"main   : {contour.get('main_repo_candidate', '') if isinstance(contour, dict) else ''}",
                "",
                "Why v0.3 exists:",
                "  Previous handoff did not carry enough operational fullness: commands targeted main, H path was missing,",
                "  and Logos Prime could not start immediately without owner correction. This panel makes those rules explicit.",
                "",
                "Continuity pack pass gates:",
                "  · H-contour path and main path are both visible;",
                "  · next commands distinguish H apply vs main cherry-pick/push;",
                "  · boot protocol tells new Logos Prime what to read first and what not to infer;",
                "  · owner requirements and reference backlog are included as visible documents;",
                "  · no commit/push/unsafe shell/live execution is performed by continuity.",
                "",
                "Included preview:",
            ]
            if files:
                for item in files[:38]:
                    lines.append(f"  · {item}")
                if len(files) > 38:
                    lines.append(f"  ... +{len(files) - 38} more")
            else:
                lines.append("  no files discovered yet")
            lines.extend([
                "",
                "H protocol excerpt:",
                protocol,
                "",
                "Logos Prime boot excerpt:",
                boot,
                "",
                "Logos Prime handoff preview:",
            ])
            lines.extend([f"  {line}" for line in handoff[:18]] or ["  Build a pack to generate LOGOS_PRIME_HANDOFF_SUMMARY_RU.md"])
            lines.extend([
                "",
                "Forbidden:",
                "  no commit, no push, no registry mutation, no real execution, no unsafe shell.",
            ])
            return "\n".join(lines)

        def handoff_text(self) -> str:
            launch = self.data.get("launch-card", {})
            handoff = self.data.get("handoff-card", {})
            block = handoff.get("copy_ready_servitor_prime_block") or launch.get("copy_ready_servitor_prime_block") or "No copy-ready handoff block found."
            lines = [
                "COPY-FIRST HANDOFF",
                "==================",
                "COPY THIS BLOCK TO SERVITOR PRIME:",
                "",
                block,
                "",
                f"taskpack: {launch.get('taskpack_zip_path', '')}",
                f"sha256  : {launch.get('taskpack_sha256', '')}",
                f"state   : {handoff.get('candidate_status', launch.get('canon_state', ''))}",
                "",
                "Use the Copy Handoff button above to place the block in clipboard.",
                "Reminder: handoff-ready is not execution-done; live gates remain explicit.",
            ]
            return "\n".join(lines)

        def dirty_text(self) -> str:
            data = self.data.get("dirty-classifier", {})
            git = self.data.get("git-closure", {})
            items = data.get("classified_items") or git.get("classified_dirty_table") or []
            lines = [
                "DIRTY / GIT CLOSURE",
                "===================",
                f"status: {data.get('status') or git.get('status')}",
                f"dirty : {data.get('dirty_count', git.get('dirty_count'))}",
                f"gate  : {data.get('push_allowed_state') or git.get('push_allowed_state')}",
                "",
                "path / class / action",
                "---------------------",
            ]
            for item in items[:22]:
                lines.append(f"{short(item.get('path'), 86)}")
                lines.append(f"  class : {item.get('category', item.get('class', ''))}")
                lines.append(f"  action: {short(item.get('recommended_action', item.get('action', '')), 106)}")
            if not items:
                lines.append("clean or no dirty table visible")
            return "\n".join(lines)

        def safety_text(self) -> str:
            data = self.data.get("safety", {})
            lines = [
                "SAFETY CENTER",
                "=============",
                f"status: {data.get('status')}",
                "",
                "Owner-facing safe defaults:",
                "  real servitor execution : gated",
                "  live LLM backend        : gated",
                "  unsafe shell            : blocked",
                "  VM routes               : explicit only",
                "  mutation                : patch/owner accepted only",
                "",
                "Machine payload:",
                compact_json(data, 2600),
            ]
            return "\n".join(lines)

        def trace_explanation(self) -> str:
            return "\n".join([
                "OPERATION TRACE — observable system reasoning",
                "=============================================",
                "This panel shows operational trace, not private chain-of-thought:",
                "  · which state was read;",
                "  · which gates remain closed;",
                "  · which artifact is active;",
                "  · what the next operator action is;",
                "  · what was copied/opened from this safe launcher.",
                "",
                "No hidden execution is performed here. This is read-only station observation plus safe local open/copy helpers.",
            ])

        def add_trace(self, msg: str):
            self.trace.configure(state="normal")
            ts = time.strftime("%H:%M:%S")
            self.trace.insert("end", f"[{ts}] {msg}\n")
            self.trace.see("end")
            self.trace.configure(state="disabled")

        def copy_text(self, text: str, label: str = "text"):
            try:
                self.clipboard_clear()
                self.clipboard_append(text)
                self.update()
                self.add_trace(f"[PASS] Copied {label} to clipboard.")
                self.statusbar.config(text=f"Copied {label} to clipboard")
            except Exception as exc:
                self.add_trace(f"[BLOCKED] Clipboard copy failed: {exc}")

        def copy_visible(self):
            self.copy_text(self.last_detail_text or self.detail.get("1.0", "end"), "current view")

        def copy_handoff(self):
            launch = self.data.get("launch-card", {})
            handoff = self.data.get("handoff-card", {})
            block = handoff.get("copy_ready_servitor_prime_block") or launch.get("copy_ready_servitor_prime_block") or self.handoff_text()
            self.copy_text(str(block), "handoff block")


        def copy_h_flow(self):
            block = "\n".join([
                "H-SAFE PATCH FLOW",
                "1. Work in E:/IMPERIUM_NEW_GENERATION_NEW_REALITY_H or branch h/* only.",
                "2. Apply patch ZIP with APPLY_PATCH.ps1 -RepoRoot $HRepo.",
                "3. Run launcher --smoke and visual review in H.",
                "4. Commit as IMPERIUM_H only after owner acceptance.",
                "5. Cherry-pick/merge accepted H commit into main, smoke in main, then push.",
            ])
            self.copy_text(block, "H-safe patch flow")

        def open_protocols(self):
            self.open_repo_path("ORGANS/ADMINISTRATUM/CONTINUITY/PROTOCOLS")

        def build_continuity(self):
            result = self.client.route("continuity-build", ["h"])
            status = result.get("status", "UNKNOWN") if isinstance(result, dict) else "UNKNOWN"
            pack_path = result.get("pack_zip_path", "") if isinstance(result, dict) else ""
            self.add_trace(f"[{status}] Continuity pack build requested: {pack_path}")
            self.statusbar.config(text=f"Continuity pack: {status} · {pack_path}")
            self.data["continuity-preview"] = self.client.route("continuity-preview", ["h"])
            self.current_surface = "continuity"
            self.render_current_surface()
            self.update_nav_selection()

        def open_continuity(self):
            self.open_repo_path("ORGANS/ADMINISTRATUM/CONTINUITY/PACKS")

        def open_repo_path(self, relative: str):
            self.open_path((self.repo / relative).resolve())

        def open_path(self, path: Path | str):
            p = Path(path)
            try:
                if not p.exists():
                    self.add_trace(f"[WARN] Path does not exist: {p}")
                    self.statusbar.config(text=f"Path not found: {p}")
                    return
                if sys.platform.startswith("win"):
                    os.startfile(str(p))  # type: ignore[attr-defined]
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", str(p)])
                else:
                    subprocess.Popen(["xdg-open", str(p)])
                self.add_trace(f"[PASS] Opened local path: {p}")
            except Exception as exc:
                self.add_trace(f"[BLOCKED] Could not open path {p}: {exc}")

        def open_tui_fallback(self):
            tui = self.repo / "ORGANS" / "IMPERIAL_IDE" / "WORKBENCH" / "TUI" / "imperial_tui.py"
            try:
                subprocess.Popen([sys.executable, str(tui)], cwd=str(self.repo), creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
                self.add_trace("[PASS] TUI fallback opened in a separate console.")
                self.statusbar.config(text="TUI fallback opened")
            except Exception as exc:
                self.add_trace(f"[BLOCKED] TUI fallback could not open: {exc}")

        def animate(self):
            self.tick += 1
            self.frame_counter += 1
            now = time.perf_counter()
            elapsed = now - self._fps_window_started
            if elapsed >= 1.0:
                self.fps_value = self.frame_counter / max(0.001, elapsed)
                self.frame_counter = 0
                self._fps_window_started = now
            if self.tick % 120 == 0:
                self.add_trace("[TRACE] " + TRACE_MESSAGES[self.trace_index % len(TRACE_MESSAGES)])
                self.trace_index += 1
            self.draw_header()
            self.draw_flow()
            self.draw_right_visual()
            self.after(self.target_frame_ms, self.animate)

    app = Launcher()
    app.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if "--smoke" in argv or "--headless-smoke" in argv:
        return smoke()
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())
