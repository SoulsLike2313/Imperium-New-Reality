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
    env = os.environ.get("IMPERIUM_ROOT")
    candidates = [env] if env else []
    candidates.extend(os.path.dirname(PKG_ROOT) for _ in [0])
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
    with open(os.path.join(PKG_ROOT, "SERVITORS", "capsules.config.json"), "r",
              encoding="utf-8") as fh:
        return json.load(fh)["capsules"]


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
        lines.append("%s %s  %s  cooldown:%ss" % (
            c(A["plasma_hot"], G["cog"]),
            c(A["chrome"], cap["label"].ljust(16)),
            c(A["gold"], cap["organ"].ljust(16)),
            cap.get("rate_limit_cooldown_s", 8)))
    lines.append("")
    lines.append(c(A["text_muted"],
                   "candidate capsule state only; real and persistent execution blocked"))
    box("%s SERVITOR CAPSULES" % G["cog"], lines, color=A["gold"])


def render_menu():
    lines = [
        "%s  [1] Organ panels" % c(A["plasma"], G["star"]),
        "%s  [2] Servitor capsules" % c(A["plasma"], G["cog"]),
        "%s  [3] Dispatch task (dry-run)" % c(A["plasma"], G["diamond"]),
        "%s  [4] Mechanicus dry-run bridge status" % c(A["plasma"], G["diamond"]),
        "%s  [q] Quit" % c(A["alert_red"], G["skull"]),
    ]
    box("%s COMMAND MENU" % G["aquila"], lines, color=A["chrome"])


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
    print(c(A["ok_green"], "\n[SMOKE] all TUI surfaces rendered. full_gui_implemented=false; "
            "tui_render=PASS"))
    return 0


def interactive():
    banner()
    while True:
        render_menu()
        try:
            choice = input(c(A["gold"], "\n  %s command > " % G["aquila"])).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if choice == "1":
            render_panels()
        elif choice == "2":
            render_capsules()
        elif choice == "3":
            task = input(c(A["plasma"], "  task text > ")).strip()
            print(c(A["nebula_bright"],
                    "  [DRY_RUN] would round-robin '%s' across active capsules." % task))
        elif choice == "4":
            bridge_status()
        elif choice in ("q", "quit", "exit"):
            print(c(A["gold"], "  %s Ave Omnissiah." % G["aquila"]))
            break
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
