#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMPERIAL IDE :: TUI  (V0.1)  -- drawn entirely in code.

WHY A TUI (in addition to the GUI):
  - Runs over SSH / inside a bare terminal / on a headless box where Tkinter
    or a display server is not available.
  - Same theme tokens as the GUI (THEME/imperium_theme.json) so the look is
    consistent across surfaces.
  - Pure stdlib + ANSI escape codes. No curses dependency required, so it works
    in Windows Terminal, ConHost (with VT enabled), and any POSIX terminal.

MODES:
  python imperial_tui.py            interactive menu loop
  python imperial_tui.py --smoke    non-interactive render smoke (CI / receipts)

The TUI is read/dry-run first, mirroring the control-shell safety boundary.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.dirname(HERE)
IDE_ROOT = os.path.dirname(PKG_ROOT)
STATION_ROOT = os.path.join(IDE_ROOT, "STATION")
if STATION_ROOT not in sys.path:
    sys.path.insert(0, STATION_ROOT)

from station_router import route as station_route

OPERATIONAL_MENU = [
    ("Dashboard", "station"),
    ("Daily Ops", "daily-ops"),
    ("Next Action", "next-action"),
    ("Task Flow", "task-flow"),
    ("Show Summary", "show-summary"),
    ("Full JSON", "full-json"),
    ("Taskpack Manager", "taskpack-manager"),
    ("Taskpack Inspect", "taskpack-inspect"),
    ("Task Console", "task-console"),
    ("Build Taskpack", "build-taskpack"),
    ("Register Taskpack", "register-taskpack"),
    ("Live Registration Promotion", "live-registration-promote"),
    ("Launch Card", "launch-card"),
    ("Handoff Card", "handoff-card"),
    ("Agents and Servitors", "agents"),
    ("Astronomicon", "task-console"),
    ("Mechanicus", "safety"),
    ("WARP", "station"),
    ("MetaOS", "station"),
    ("Reports", "reports-latest"),
    ("Receipts", "receipts-latest"),
    ("Dirty Classifier", "dirty-classifier"),
    ("Safety Center 2.0", "safety"),
    ("Lifecycle", "lifecycle"),
    ("Git Closure", "git-closure"),
    ("Settings", "settings"),
]

with open(os.path.join(PKG_ROOT, "THEME", "imperium_theme.json"), "r",
          encoding="utf-8") as fh:
    THEME = json.load(fh)
A = THEME["ansi_256"]
G = THEME["glyphs"]


def enable_vt():
    """Enable ANSI/VT processing on Windows ConHost."""
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
        except Exception:
            pass
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def fg(code):
    return "\x1b[38;5;%dm" % code


def bg(code):
    return "\x1b[48;5;%dm" % code


RESET = "\x1b[0m"
BOLD = "\x1b[1m"


def supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    return True


USE_COLOR = supports_color()


def c(code, text, bold=False):
    if not USE_COLOR:
        return text
    return (BOLD if bold else "") + fg(code) + text + RESET


def nebula_bar(width):
    """Horizontal nebula gradient using 256-color ramp void->nebula->plasma."""
    ramp = [233, 234, 235, 53, 54, 55, 91, 92, 93, 98, 99, 135, 134, 133, 132]
    out = []
    for i in range(width):
        idx = ramp[int(i / max(1, width) * (len(ramp) - 1))]
        out.append(bg(idx) + " " + RESET if USE_COLOR else " ")
    return "".join(out)


def box(title, lines, width=74, color=A["gold"]):
    tl, tr, bl, br = G["tl"], G["tr"], G["bl"], G["br"]
    h, v = G["h"], G["v"]
    t = " %s " % title
    top = tl + t + h * (width - 2 - len(t)) + tr
    print(c(color, top, bold=True))
    for ln in lines:
        raw = _visible(ln)
        pad = width - 2 - len(raw)
        if pad < 0:
            ln = ln[:width - 2]
            pad = 0
        print(c(color, v) + " " + ln + " " * (pad - 1 if pad else 0) +
              c(color, v))
    print(c(color, bl + h * (width - 2) + br, bold=True))


def _visible(s):
    """Length of string ignoring ANSI escapes."""
    import re
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def banner():
    w = 74
    print()
    print(nebula_bar(w))
    print(c(A["chrome"], "   %s  I M P E R I A L   I D E   \u2014   N E B U L A   T U I" %
            G["aquila"], bold=True))
    print(c(A["gold"], "   CONTROL SHELL WORKBENCH \u00b7 V0.1 \u00b7 dry-run gateway active"))
    print(nebula_bar(w))
    print()


def load_panels():
    repo_root = discover_repo_root()
    env = os.environ.get("IMPERIUM_ROOT")
    candidates = [env] if env else []
    candidates.extend([repo_root, os.path.dirname(PKG_ROOT)])
    for root in candidates:
        if not root:
            continue
        path = os.path.join(root, "ORGANS", "IMPERIAL_IDE", "SHELL", "panel_registry.json")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8-sig") as fh:
                return json.load(fh)["panels"]
    sample = os.path.join(PKG_ROOT, "GUI", "sample_panels.json")
    with open(sample, "r", encoding="utf-8") as fh:
        return json.load(fh)["panels"]


def load_capsules():
    repo_root = discover_repo_root()
    env = os.environ.get("IMPERIUM_ROOT")
    candidates = [env] if env else []
    candidates.extend([repo_root, os.path.dirname(PKG_ROOT)])
    for root in candidates:
        if not root:
            continue
        path = os.path.join(root, "ORGANS", "IMPERIAL_IDE", "AGENTS", "agent_registry.json")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8-sig") as fh:
                data = json.load(fh)
            current_path = os.path.join(root, "ORGANS", "ASTRONOMICON", "TASK_REGISTRY", "current_expected_task.json")
            current_task = ""
            if os.path.isfile(current_path):
                try:
                    with open(current_path, "r", encoding="utf-8-sig") as ch:
                        current_task = json.load(ch).get("task_id", "")
                except Exception:
                    current_task = ""
            return [
                {
                    "label": item.get("servitor_name", item.get("agent_id", "")),
                    "organ": item.get("agent_id", ""),
                    "owner_organ": item.get("owner_organ", ""),
                    "mode": item.get("execution_mode", ""),
                    "handoff_mode": item.get("handoff_mode", ""),
                    "status": item.get("status", ""),
                    "role": item.get("role", ""),
                    "allowed_actions": item.get("allowed_actions", []),
                    "blocked_actions": item.get("blocked_actions", []),
                    "current_task_id": current_task or item.get("current_task_id", ""),
                    "rate_limit_cooldown_s": 0,
                }
                for item in data.get("agents", [])
            ]
    with open(os.path.join(PKG_ROOT, "SERVITORS", "capsules.config.json"), "r",
              encoding="utf-8") as fh:
        return json.load(fh)["capsules"]


def discover_repo_root():
    env = os.environ.get("IMPERIUM_ROOT")
    if env and os.path.isdir(os.path.join(env, "ORGANS")):
        return env
    cur = HERE
    for _ in range(10):
        if os.path.isdir(os.path.join(cur, "ORGANS")) and os.path.isfile(os.path.join(cur, "AGENTS.md")):
            return cur
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    return ""


def status_glyph(status):
    s = (status or "").upper()
    if "PASS_WITH" in s:
        return c(A["warn_amber"], G["diamond"])
    if s.startswith("PASS") or s == "ACTIVE":
        return c(A["ok_green"], G["diamond"])
    if "BLOCK" in s:
        return c(A["alert_red"], G["skull"])
    return c(A["metal"], G["diamond"])


def render_panels():
    panels = load_panels()
    lines = []
    for i, p in enumerate(panels, 1):
        lines.append("%s %s %s  %s" % (
            c(A["plasma"], "%2d" % i),
            status_glyph(p.get("current_status")),
            c(A["chrome"], p.get("title", p["panel_id"]).ljust(22)),
            c(A["text_muted"], p.get("owner_organ", ""))))
    box("%s ORGAN PANELS" % G["star"], lines, color=A["nebula_bright"])


def render_capsules():
    caps = load_capsules()
    lines = []
    for cap in caps:
        lines.append("%s %s  %s  %s  %s" % (
            c(A["plasma_hot"], G["cog"]),
            c(A["gold"], cap["organ"].ljust(18)),
            c(A["chrome"], cap["label"][:20].ljust(20)),
            c(A["text_muted"], (cap.get("owner_organ") or "").ljust(12)),
            c(A["text_muted"], cap.get("status") or ("cooldown:%ss" % cap.get("rate_limit_cooldown_s", 8)))))
        lines.append("    mode:%s handoff:%s current:%s" % (
            cap.get("mode", ""),
            cap.get("handoff_mode", ""),
            cap.get("current_task_id", "")[:44],
        ))
        lines.append("    allow:%s" % ", ".join(cap.get("allowed_actions", [])[:3]))
        lines.append("    block:%s" % ", ".join(cap.get("blocked_actions", [])[:3]))
    lines.append("")
    lines.append(c(A["text_muted"],
                   "real 12-servitor registry is PRIMARY; legacy Alpha/Beta/Gamma is debug-only"))
    lines.append(c(A["text_muted"],
                   "Servitor Prime mode: EXTERNAL_HANDOFF_ONLY; real execution remains gated"))
    box("%s SERVITOR ROSTER" % G["cog"], lines, color=A["gold"])


def render_menu():
    lines = []
    for index, (label, _) in enumerate(OPERATIONAL_MENU, 1):
        lines.append("%s  [%02d] %s" % (c(A["plasma"], G["diamond"]), index, label))
    lines.append("%s  [q] Quit" % c(A["alert_red"], G["skull"]))
    box("%s COMMAND MENU" % G["aquila"], lines, color=A["chrome"])


def render_station_result(title, command, args=None):
    if command == "settings":
        bridge_status()
        return {"status": "PASS_WITH_WARNINGS", "surface": "SETTINGS"}
    try:
        result = station_route(command, args or [])
    except Exception as exc:
        result = {"status": "BLOCKED", "reason": str(exc), "command": command}
    raw = json.dumps(result, ensure_ascii=False, indent=2).splitlines()
    lines = _summary_lines(command, result)
    lines.append("")
    lines.append("Full JSON: python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py full-json")
    lines.append("Preview:")
    lines.extend(line[:68] for line in raw[:16])
    if len(raw) > 16:
        lines.append("... preview truncated; Full JSON command shows complete payload")
    color = A["alert_red"] if result.get("status") == "BLOCKED" else A["nebula_bright"]
    box("%s %s" % (G["star"], title.upper()), lines, color=color)
    return result


def _summary_lines(command, result):
    lines = ["status: %s" % result.get("status", "UNKNOWN")]
    if command in {"daily-ops", "operator-board"}:
        board = result.get("board", {})
        lines.extend([
            "surface: DAILY OPERATIONS",
            "current task: %s" % board.get("current_task", {}).get("task_id", ""),
            "agents: %s" % board.get("agent_roster_summary", {}).get("agent_count", 0),
            "dirty: %s paths" % board.get("dirty_state", {}).get("dirty_count", 0),
            "next: %s" % board.get("next_recommended_action", {}).get("next_action", ""),
        ])
    elif command == "agents":
        lines.extend([
            "real servitors visible: %s" % result.get("agent_count", 0),
            "current task: %s" % result.get("current_expected_task_id", ""),
            "execution: gated",
        ])
    elif command in {"taskpack-manager", "taskpack-inspect"}:
        lines.extend([
            "generated taskpacks: %s" % result.get("generated_taskpacks_found", "selected"),
            "latest/selected: %s" % result.get("taskpack_id", result.get("latest_taskpack_path", "")),
            "next: inspect, validate, open, copy path, or review promotion",
        ])
    elif command == "next-action":
        lines.append("next: %s" % result.get("next_action", ""))
    elif command == "dirty-classifier":
        lines.extend([
            "dirty_count: %s" % result.get("dirty_count", 0),
            "unclassified: %s" % result.get("unclassified_count", 0),
            "push gate: %s" % result.get("push_allowed_state", ""),
        ])
    elif command == "git-closure":
        lines.extend([
            "dirty_count: %s" % result.get("dirty_count", 0),
            "push gate: %s" % result.get("push_allowed_state", ""),
            "next: stage only validated current task outputs",
        ])
    else:
        lines.append("next: use Full JSON for complete machine-readable state")
    return lines[:12]


def bridge_status():
    lines = [
        c(A["ok_green"], "dry_run_gateway      : ACTIVE"),
        c(A["ok_green"], "real_execution       : BLOCKED (default)"),
        c(A["warn_amber"], "unknown_tool         : -> BLOCKED, executed=false"),
        c(A["text_muted"], "bridge_path          : ORGANS/MECHANICUS/IDE_BRIDGE/"),
        c(A["text_muted"], "                       mechanicus_ide_bridge.py"),
    ]
    box("%s MECHANICUS BRIDGE" % G["cog"], lines, color=A["nebula_bright"])


def smoke():
    """Non-interactive render of every surface for receipts / CI."""
    banner()
    render_panels()
    print()
    render_capsules()
    print()
    bridge_status()
    print()
    render_menu()
    station = render_station_result("Daily Ops Smoke", "daily-ops")
    required = {
        "station-ux-smoke", "taskpack-manager", "taskpacks", "taskpack-list", "taskpack-inspect",
        "taskpack-validate", "taskpack-open", "taskpack-copy-path",
        "show-json", "full-json", "show-summary", "launch-card", "handoff-card", "reports-latest",
        "receipts-latest", "dirty-classifier", "safety", "live-registration-promote",
        "agents", "agent-status", "lifecycle", "git-closure", "daily-ops",
        "next-action", "operator-board", "task-flow", "task-flow-smoke",
    }
    commands = {command for _, command in OPERATIONAL_MENU} | {
        "station-ux-smoke", "operator-board", "taskpacks", "taskpack-list", "agent-status",
        "taskpack-validate", "taskpack-open", "taskpack-copy-path", "task-flow-smoke", "show-json",
    }
    labels_ok = all(label for label, _ in OPERATIONAL_MENU) and required <= commands
    status = "PASS_WITH_WARNINGS" if station.get("status") != "BLOCKED" and labels_ok else "BLOCKED"
    print(c(A["ok_green"] if status != "BLOCKED" else A["alert_red"],
            "\n[SMOKE] operational menus=%s; station=%s; tui_render=%s" %
            (len(OPERATIONAL_MENU), station.get("status"), status)))
    return 0 if status != "BLOCKED" else 2


def interactive():
    banner()
    while True:
        render_menu()
        try:
            choice = input(c(A["gold"], "\n  %s command > " % G["aquila"])).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if choice in ("q", "quit", "exit"):
            print(c(A["gold"], "  %s Ave Omnissiah." % G["aquila"]))
            break
        try:
            index = int(choice) - 1
        except ValueError:
            index = -1
        if 0 <= index < len(OPERATIONAL_MENU):
            label, command = OPERATIONAL_MENU[index]
            args = []
            if command in {"task-console", "build-taskpack", "register-taskpack"}:
                task = input(c(A["plasma"], "  task title (blank=sample) > ")).strip()
                if task:
                    args.append(task)
            if command == "register-taskpack":
                live = input(c(A["warn_amber"], "  type LIVE for governed local registration; Enter=dry-run > ")).strip()
                if live == "LIVE":
                    args.insert(0, "live")
            render_station_result(label, command, args)
            if label == "Agents and Servitors":
                render_capsules()
            elif label == "Astronomicon":
                render_panels()
        else:
            print(c(A["alert_red"], "  unknown command"))
    return 0


def main(argv):
    enable_vt()
    if "--smoke" in argv or "--no-color" in argv:
        global USE_COLOR
        if "--no-color" in argv:
            USE_COLOR = False
        if "--smoke" in argv:
            return smoke()
    return interactive()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
