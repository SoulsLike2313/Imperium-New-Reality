#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMPERIAL IDE :: GUI WORKBENCH  (V0.1)
Purple Dark Nebula Metallic Warhammer Imperium style.

WHY PYTHON / TKINTER:
  - The existing Imperial IDE control shell is Python stdlib-first.
  - Tkinter ships with CPython on Windows -> zero pip install, "just run".
  - The GUI is a thin, themed cockpit OVER the already-validated shell router
    and the Mechanicus dry-run bridge. It does not invent new authority.

SAFETY BOUNDARY (inherited from the control shell):
  - Read-only / dry-run first. No arbitrary shell. Unknown tools -> BLOCKED.
  - Servitor dispatch is queued through capsules; real execution stays gated.

RUN:
  python imperial_gui_workbench.py
  (auto-detects repo root; falls back to bundled sample data if not found)
"""
import json
import os
import subprocess
import sys
import threading
import queue
import time
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, font as tkfont
except Exception as exc:  # pragma: no cover
    sys.stderr.write("Tkinter is required (ships with standard CPython): %s\n" % exc)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.dirname(HERE)

OPERATIONAL_ACTIONS = [
    ("DASHBOARD", "station"),
    ("DAILY OPS", "daily-ops"),
    ("NEXT", "next-action"),
    ("SUMMARY", "show-summary"),
    ("FULL JSON", "full-json"),
    ("TASKPACKS", "taskpack-manager"),
    ("INSPECT", "taskpack-inspect"),
    ("NEW TASK", "new-task"),
    ("BUILD", "build-taskpack"),
    ("REGISTER DRY", "register-taskpack"),
    ("LAUNCH", "launch-card"),
    ("HANDOFF", "handoff-card"),
    ("AGENTS", "agents"),
    ("REPORTS", "reports-latest"),
    ("RECEIPTS", "receipts-latest"),
    ("DIRTY", "dirty-classifier"),
    ("LIFECYCLE", "lifecycle"),
    ("SAFETY 2.0", "safety"),
    ("PROMOTE", "live-registration-promote"),
    ("GIT", "git-closure"),
]


# --------------------------------------------------------------------------
# Theme loading (single source of truth = THEME/imperium_theme.json)
# --------------------------------------------------------------------------
def load_theme():
    path = os.path.join(PKG_ROOT, "THEME", "imperium_theme.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


THEME = load_theme()
C = THEME["palette"]
STATUS_C = THEME["status_colors"]


# --------------------------------------------------------------------------
# Repo discovery -- find the live New Reality root if we are running on the PC.
# Degrade gracefully to bundled sample data inside the package otherwise.
# --------------------------------------------------------------------------
def discover_repo_root():
    # 1) explicit env override
    env = os.environ.get("IMPERIUM_ROOT")
    if env and os.path.isdir(os.path.join(env, "ORGANS")):
        return env, "env:IMPERIUM_ROOT"
    # 2) walk upward looking for an ORGANS/ + AGENTS.md root
    cur = HERE
    for _ in range(8):
        if os.path.isdir(os.path.join(cur, "ORGANS")) and os.path.isfile(
            os.path.join(cur, "AGENTS.md")
        ):
            return cur, "discovered:walk-up"
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    # 3) common Windows scope-lock location
    guess = r"E:\\IMPERIUM_NEW_GENERATION_NEW_REALITY"
    if os.path.isdir(os.path.join(guess, "ORGANS")):
        return guess, "guess:E-drive"
    return None, "sample-mode"


REPO_ROOT, REPO_SOURCE = discover_repo_root()


def cli_path():
    if REPO_ROOT:
        p = os.path.join(REPO_ROOT, "ORGANS", "IMPERIAL_IDE", "SHELL", "imperial_ide_cli.py")
        if os.path.isfile(p):
            return p
    return None


def load_panels():
    """Read the live panel registry if present, else bundled defaults."""
    if REPO_ROOT:
        p = os.path.join(REPO_ROOT, "ORGANS", "IMPERIAL_IDE", "SHELL", "panel_registry.json")
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict) and "panels" in data:
                    return data["panels"]
                if isinstance(data, list):
                    return data
            except Exception:
                pass
    sample = os.path.join(PKG_ROOT, "GUI", "sample_panels.json")
    with open(sample, "r", encoding="utf-8") as fh:
        return json.load(fh)["panels"]


def load_capsules():
    if REPO_ROOT:
        roster = os.path.join(REPO_ROOT, "ORGANS", "IMPERIAL_IDE", "AGENTS", "servitor_roster.json")
        if os.path.isfile(roster):
            try:
                with open(roster, "r", encoding="utf-8-sig") as fh:
                    data = json.load(fh)
                return [
                    {
                        "capsule_id": item.get("agent_id", ""),
                        "label": item.get("servitor_name", item.get("agent_id", "")),
                        "organ": item.get("agent_id", ""),
                        "rate_limit_cooldown_s": 0,
                        "command_template": [],
                        "status": item.get("status", ""),
                        "mode": item.get("mode", ""),
                    }
                    for item in data.get("servitors", [])
                ]
            except Exception:
                pass
    path = os.path.join(PKG_ROOT, "SERVITORS", "capsules.config.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)["capsules"]


# --------------------------------------------------------------------------
# Servitor capsule model (GUI-side controller).
# Each capsule is an isolated worker that owns ONE servitor CLI session and a
# task queue. Holding 2-3 capsules lets the operator round-robin work so a
# single agent's rate limit never stalls the whole line.
# --------------------------------------------------------------------------
class Capsule:
    def __init__(self, spec):
        self.id = spec["capsule_id"]
        self.label = spec.get("label", self.id)
        self.organ = spec.get("organ", "OFFICIO_AGENTIS")
        self.command_template = spec.get("command_template", [])
        self.cooldown_s = spec.get("rate_limit_cooldown_s", 8)
        self.state = "IDLE"
        self.tasks = queue.Queue()
        self.history = []
        self.current = None
        self.last_dispatch = 0.0
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self.state = "ACTIVE"
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        self.state = "IDLE"

    def enqueue(self, task_text):
        self.tasks.put(task_text)

    def _loop(self):
        while not self._stop.is_set():
            try:
                task = self.tasks.get(timeout=0.4)
            except queue.Empty:
                if self.state == "ACTIVE" and self.current is None:
                    self.state = "WAITING"
                continue
            # rate-limit aware spacing
            gap = time.time() - self.last_dispatch
            if gap < self.cooldown_s:
                time.sleep(self.cooldown_s - gap)
            self.current = task
            self.state = "RUNNING"
            self.last_dispatch = time.time()
            result = self._dispatch(task)
            self.history.append(result)
            self.current = None
            self.state = "WAITING"

    def _dispatch(self, task):
        """Return a dry-run capsule receipt without executing a process."""
        ts = datetime.utcnow().isoformat() + "Z"
        return {"ts": ts, "capsule": self.id, "task": task, "mode": "DRY_RUN",
                "rc": 0,
                "executed": False,
                "real_execution_blocked": True,
                "out": "DRY_RUN queued for %s; real capsule execution is blocked." % self.organ}


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------
class Workbench(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("\u2042 IMPERIAL IDE :: WORKBENCH  \u2014  Nebula Console V0.1")
        self.geometry("1280x800")
        self.minsize(1060, 680)
        self.configure(bg=C["void"])
        self._init_fonts()
        self._init_style()
        self.panels = load_panels()
        self.capsules = [Capsule(s) for s in load_capsules()]
        self.active_panel = self.panels[0]["panel_id"] if self.panels else None
        self._build_header()
        self._build_body()
        self._build_statusbar()
        self.after(700, self._tick)

    # ---- styling ----
    def _init_fonts(self):
        fams = set(tkfont.families())
        def pick(cands, size, weight="normal"):
            for c in cands:
                if c in fams:
                    return tkfont.Font(family=c, size=size, weight=weight)
            return tkfont.Font(size=size, weight=weight)
        self.f_display = pick(["Trajan Pro", "Georgia", "Times New Roman"], 20, "bold")
        self.f_h = pick(["Segoe UI Semibold", "Segoe UI", "Verdana"], 12, "bold")
        self.f_ui = pick(["Segoe UI", "Verdana", "Helvetica"], 10)
        self.f_mono = pick(["Cascadia Mono", "Consolas", "Courier New"], 10)
        self.f_mono_s = pick(["Cascadia Mono", "Consolas", "Courier New"], 9)

    def _init_style(self):
        st = ttk.Style(self)
        try:
            st.theme_use("clam")
        except Exception:
            pass
        st.configure("TFrame", background=C["panel"])
        st.configure("Void.TFrame", background=C["void"])
        st.configure("Raised.TFrame", background=C["panel_raised"])
        st.configure("TLabel", background=C["panel"], foreground=C["text"],
                     font=self.f_ui)
        st.configure("Muted.TLabel", background=C["panel"], foreground=C["text_muted"])
        st.configure("Head.TLabel", background=C["panel"], foreground=C["gold"],
                     font=self.f_h)
        st.configure("Treeview", background=C["panel_raised"],
                     fieldbackground=C["panel_raised"], foreground=C["text"],
                     rowheight=24, font=self.f_ui, borderwidth=0)
        st.configure("Treeview.Heading", background=C["nebula_deep"],
                     foreground=C["chrome"], font=self.f_h, relief="flat")
        st.map("Treeview", background=[("selected", C["nebula_bright"])],
               foreground=[("selected", C["text"])])

    # ---- header with procedural nebula gradient + aquila ----
    def _build_header(self):
        self.header = tk.Canvas(self, height=84, bg=C["void"], highlightthickness=0)
        self.header.pack(fill="x", side="top")
        self.header.bind("<Configure>", self._paint_header)

    def _paint_header(self, _evt=None):
        cv = self.header
        cv.delete("all")
        w = cv.winfo_width() or 1280
        h = 84
        # vertical nebula gradient void -> nebula_deep
        steps = 42
        c0 = _hex_rgb(C["void"]); c1 = _hex_rgb(C["nebula_deep"])
        for i in range(steps):
            t = i / (steps - 1)
            col = _mix(c0, c1, t * 0.9)
            cv.create_rectangle(0, i * h / steps, w, (i + 1) * h / steps,
                                outline="", fill=_rgb_hex(col))
        # plasma star field
        import random
        random.seed(7)
        for _ in range(70):
            x = random.random() * w; y = random.random() * h
            r = random.choice([0, 0, 1, 1, 2])
            col = random.choice([C["plasma"], C["chrome"], C["nebula_bright"], C["gold"]])
            cv.create_oval(x - r, y - r, x + r, y + r, outline="", fill=col)
        # gold rule line
        cv.create_line(0, h - 2, w, h - 2, fill=C["gold"], width=2)
        cv.create_line(0, h - 5, w, h - 5, fill=C["bronze"], width=1)
        # title
        cv.create_text(28, 30, anchor="w", text="\u2042  IMPERIAL  IDE",
                       fill=C["chrome"], font=self.f_display)
        cv.create_text(30, 58, anchor="w",
                       text="NEBULA  CONSOLE  \u00b7  CONTROL  SHELL  WORKBENCH  V0.1",
                       fill=C["gold"], font=self.f_mono_s)
        mode = "LIVE REPO" if REPO_ROOT else "SAMPLE MODE"
        cv.create_text(w - 24, 30, anchor="e",
                       text="\u2699 %s" % mode,
                       fill=C["plasma_hot"] if REPO_ROOT else C["warn_amber"],
                       font=self.f_h)
        cv.create_text(w - 24, 56, anchor="e",
                       text=(REPO_ROOT or "bundled sample data"),
                       fill=C["text_muted"], font=self.f_mono_s)

    # ---- body: organ sidebar | panel view | servitor rack ----
    def _build_body(self):
        body = ttk.Frame(self, style="Void.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # left: organ / panel sidebar
        side = ttk.Frame(body, style="Raised.TFrame", width=232)
        side.grid(row=0, column=0, sticky="ns")
        side.grid_propagate(False)
        ttk.Label(side, text="\u25C6  ORGAN PANELS", style="Head.TLabel",
                  background=C["panel_raised"]).pack(anchor="w", padx=14, pady=(14, 6))
        self.panel_buttons = {}
        for p in self.panels:
            b = tk.Label(side, text="  \u2737  " + p.get("title", p["panel_id"]),
                         bg=C["panel_raised"], fg=C["text_muted"], anchor="w",
                         font=self.f_ui, padx=8, pady=6, cursor="hand2")
            b.pack(fill="x", padx=8, pady=1)
            b.bind("<Button-1>", lambda e, pid=p["panel_id"]: self.select_panel(pid))
            b.bind("<Enter>", lambda e, w=b: w.configure(bg=C["panel_hi"]))
            b.bind("<Leave>", lambda e, w=b, pid=p["panel_id"]:
                   w.configure(bg=C["nebula_deep"] if pid == self.active_panel
                               else C["panel_raised"]))
            self.panel_buttons[p["panel_id"]] = b

        # center: panel detail
        center = ttk.Frame(body, style="TFrame")
        center.grid(row=0, column=1, sticky="nsew", padx=1)
        center.rowconfigure(3, weight=1)
        center.columnconfigure(0, weight=1)
        self.panel_title = ttk.Label(center, text="", style="Head.TLabel")
        self.panel_title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))
        self.panel_sub = ttk.Label(center, text="", style="Muted.TLabel")
        self.panel_sub.grid(row=1, column=0, sticky="w", padx=16)
        actions = tk.Frame(center, bg=C["panel"])
        actions.grid(row=2, column=0, sticky="ew", padx=12, pady=(8, 0))
        for label, command in OPERATIONAL_ACTIONS:
            self._metal_button(
                actions, label, lambda cmd=command: self.run_station_command(cmd), small=True
            ).pack(side="left", padx=2)
        self.panel_tree = ttk.Treeview(center, columns=("k", "v"), show="headings",
                                       height=10)
        self.panel_tree.heading("k", text="FIELD")
        self.panel_tree.heading("v", text="VALUE")
        self.panel_tree.column("k", width=220, anchor="w")
        self.panel_tree.column("v", width=520, anchor="w")
        self.panel_tree.grid(row=3, column=0, sticky="nsew", padx=16, pady=12)

        # right: servitor capsule rack
        rack = ttk.Frame(body, style="Raised.TFrame", width=320)
        rack.grid(row=0, column=2, sticky="ns")
        rack.grid_propagate(False)
        ttk.Label(rack, text="\u2699  SERVITOR ROSTER", style="Head.TLabel",
                  background=C["panel_raised"]).pack(anchor="w", padx=14, pady=(14, 6))
        self.capsule_widgets = {}
        for cap in self.capsules:
            self._build_capsule_card(rack, cap)
        # dispatch box
        disp = tk.Frame(rack, bg=C["panel_raised"])
        disp.pack(fill="x", padx=10, pady=(8, 12))
        ttk.Label(disp, text="DISPATCH TASK (round-robin)", style="Muted.TLabel",
                  background=C["panel_raised"]).pack(anchor="w")
        self.task_entry = tk.Entry(disp, bg=C["void_2"], fg=C["text"],
                                   insertbackground=C["gold"], font=self.f_mono,
                                   relief="flat")
        self.task_entry.pack(fill="x", pady=4, ipady=4)
        self.task_entry.bind("<Return>", lambda e: self.dispatch_round_robin())
        self._metal_button(disp, "\u2737  DISPATCH", self.dispatch_round_robin).pack(
            fill="x")

        # bottom log console
        self.console = tk.Text(self, height=9, bg=C["void_2"], fg=C["text"],
                               insertbackground=C["gold"], font=self.f_mono_s,
                               relief="flat", padx=12, pady=8, wrap="word")
        self.console.pack(fill="x", side="bottom")
        self.console.tag_config("ok", foreground=C["ok_green"])
        self.console.tag_config("warn", foreground=C["warn_amber"])
        self.console.tag_config("err", foreground=C["alert_red"])
        self.console.tag_config("dim", foreground=C["text_muted"])
        self.console.tag_config("plasma", foreground=C["plasma_hot"])
        self._rr_index = 0
        self.select_panel(self.active_panel)
        self.log("Workbench online. Repo source: %s" % REPO_SOURCE, "plasma")
        if not REPO_ROOT:
            self.log("Running in SAMPLE MODE \u2014 bundled data only. Set "
                     "IMPERIUM_ROOT to your repo to go live.", "warn")

    def _build_capsule_card(self, parent, cap):
        card = tk.Frame(parent, bg=C["void_2"], highlightbackground=C["line_bright"],
                        highlightthickness=1)
        card.pack(fill="x", padx=10, pady=5)
        top = tk.Frame(card, bg=C["void_2"])
        top.pack(fill="x", padx=8, pady=(6, 2))
        led = tk.Canvas(top, width=14, height=14, bg=C["void_2"], highlightthickness=0)
        led.pack(side="left")
        dot = led.create_oval(2, 2, 12, 12, fill=C["metal"], outline=C["chrome"])
        tk.Label(top, text=cap.label, bg=C["void_2"], fg=C["chrome"],
                 font=self.f_h).pack(side="left", padx=6)
        state_lbl = tk.Label(card, text="IDLE", bg=C["void_2"], fg=C["text_muted"],
                             font=self.f_mono_s)
        state_lbl.pack(anchor="w", padx=10)
        meta = tk.Label(card, text="organ: %s" % cap.organ, bg=C["void_2"],
                        fg=C["text_faint"], font=self.f_mono_s)
        meta.pack(anchor="w", padx=10)
        btns = tk.Frame(card, bg=C["void_2"])
        btns.pack(fill="x", padx=8, pady=6)
        self._metal_button(btns, "START", lambda c=cap: self.start_capsule(c),
                           small=True).pack(side="left", padx=(0, 4))
        self._metal_button(btns, "STOP", lambda c=cap: self.stop_capsule(c),
                           small=True).pack(side="left", padx=4)
        self._metal_button(btns, "SEND", lambda c=cap: self.dispatch_to(c),
                           small=True).pack(side="left", padx=4)
        self.capsule_widgets[cap.id] = (led, dot, state_lbl)

    def _metal_button(self, parent, text, cmd, small=False):
        b = tk.Label(parent, text=text, bg=C["metal_dark"], fg=C["chrome"],
                     font=self.f_mono_s if small else self.f_h,
                     padx=10, pady=4 if small else 6, cursor="hand2")
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.configure(bg=C["nebula_bright"], fg=C["text"]))
        b.bind("<Leave>", lambda e: b.configure(bg=C["metal_dark"], fg=C["chrome"]))
        return b

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=C["nebula_deep"], height=24)
        bar.pack(fill="x", side="bottom")
        self.status = tk.Label(bar, text="\u2042 Ave Omnissiah \u00b7 dry-run gateway active",
                               bg=C["nebula_deep"], fg=C["gold"], font=self.f_mono_s,
                               anchor="w")
        self.status.pack(side="left", padx=12)

    # ---- behaviour ----
    def select_panel(self, pid):
        self.active_panel = pid
        for k, w in self.panel_buttons.items():
            if k == pid:
                w.configure(bg=C["nebula_deep"], fg=C["gold_bright"])
            else:
                w.configure(bg=C["panel_raised"], fg=C["text_muted"])
        panel = next((p for p in self.panels if p["panel_id"] == pid), None)
        if not panel:
            return
        self.panel_title.configure(text="\u25C6  " + panel.get("title", pid).upper())
        self.panel_sub.configure(
            text="owner: %s   \u00b7   risk: %s   \u00b7   status: %s" % (
                panel.get("owner_organ", "?"), panel.get("risk_class", "?"),
                panel.get("current_status", "?")))
        self.panel_tree.delete(*self.panel_tree.get_children())
        for k, v in panel.items():
            if isinstance(v, (list, dict)):
                v = json.dumps(v, ensure_ascii=False)
            self.panel_tree.insert("", "end", values=(k, v))
        self.log("Opened panel: %s" % pid, "dim")

    def run_station_command(self, command):
        cli = cli_path()
        if not cli or not REPO_ROOT:
            self.log("BLOCKED: live repository shell is unavailable.", "err")
            return
        argv = [sys.executable, cli, command, "--compact"]
        task_text = self.task_entry.get().strip()
        if task_text and command in {"new-task", "build-taskpack", "register-taskpack", "launch-card", "lifecycle"}:
            argv.insert(-1, task_text)
        try:
            completed = subprocess.run(
                argv,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
                check=False,
            )
            payload = json.loads(completed.stdout)
            data = payload.get("data", payload)
            self.panel_tree.delete(*self.panel_tree.get_children())
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                self.panel_tree.insert("", "end", values=(key, str(value)[:1000]))
            status = payload.get("receipt", {}).get("status", data.get("status", "UNKNOWN"))
            self.log("Station %s -> %s" % (command, status),
                     "err" if status == "BLOCKED" else "ok")
        except Exception as exc:
            self.log("BLOCKED: station command failed: %s" % exc, "err")

    def start_capsule(self, cap):
        cap.start()
        self.log("Capsule %s STARTED" % cap.id, "ok")

    def stop_capsule(self, cap):
        cap.stop()
        self.log("Capsule %s STOPPED" % cap.id, "warn")

    def dispatch_to(self, cap):
        task = self.task_entry.get().strip()
        if not task:
            self.log("No task text to dispatch.", "err")
            return
        if cap.state in ("IDLE",):
            cap.start()
        cap.enqueue(task)
        self.log("\u2192 %s queued to %s" % (task, cap.id), "plasma")
        self.task_entry.delete(0, "end")

    def dispatch_round_robin(self):
        task = self.task_entry.get().strip()
        if not task:
            return
        if not self.capsules:
            return
        cap = self.capsules[self._rr_index % len(self.capsules)]
        self._rr_index += 1
        self.dispatch_to(cap)

    def log(self, msg, tag="dim"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.console.insert("end", "[%s] " % ts, "dim")
        self.console.insert("end", msg + "\n", tag)
        self.console.see("end")

    def _tick(self):
        active = 0
        for cap in self.capsules:
            widget = self.capsule_widgets.get(cap.id)
            if not widget:
                continue
            led, dot, state_lbl = widget
            colmap = {"RUNNING": C["plasma_hot"], "ACTIVE": C["nebula_bright"],
                      "WAITING": C["gold"], "IDLE": C["metal"]}
            col = colmap.get(cap.state, C["metal"])
            led.itemconfig(dot, fill=col)
            qd = cap.tasks.qsize()
            state_lbl.configure(text="%s  \u00b7  queue:%d  \u00b7  done:%d" % (
                cap.state, qd, len(cap.history)), fg=col)
            if cap.state in ("RUNNING", "ACTIVE", "WAITING"):
                active += 1
            # drain finished history into console once
            while cap.history and not getattr(cap, "_logged", None) or \
                    (cap.history and len(cap.history) > getattr(cap, "_seen", 0)):
                idx = getattr(cap, "_seen", 0)
                if idx >= len(cap.history):
                    break
                r = cap.history[idx]
                cap._seen = idx + 1
                tag = "ok" if r["rc"] == 0 else "err"
                self.log("\u2714 %s [%s] %s" % (r["capsule"], r["mode"],
                                                 r["out"][:120]), tag)
        self.status.configure(
            text="\u2042 capsules active: %d/%d  \u00b7  dry-run gateway active  "
                 "\u00b7  %s" % (active, len(self.capsules),
                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.after(700, self._tick)


# --------------------------------------------------------------------------
# color helpers
# --------------------------------------------------------------------------
def _hex_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rgb_hex(t):
    return "#%02X%02X%02X" % (int(t[0]), int(t[1]), int(t[2]))


def _mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def smoke():
    required_panels = {
        "operational_dashboard", "station_task_console", "station_taskpack_builder",
        "live_registration_gate", "station_launch_card", "agent_roster",
        "servitor_matrix", "task_lifecycle", "reports_browser", "receipts_browser",
        "safety_center", "station_git_closure", "warp_workspace", "metaos_router",
        "station_mechanicus_tools", "station_settings", "taskpack_manager",
        "dirty_classifier", "live_registration_promotion", "json_summary_viewer",
        "handoff_card", "daily_ops_shell",
    }
    panel_ids = {panel.get("panel_id") for panel in load_panels()}
    payload = {
        "status": "PASS_WITH_WARNINGS" if required_panels <= panel_ids else "BLOCKED",
        "surface": "WORKBENCH_GUI_CANDIDATE",
        "mode": "LIVE_READ_ONLY" if REPO_ROOT else "SAMPLE",
        "repo_root": REPO_ROOT,
        "repo_source": REPO_SOURCE,
        "panel_count": len(load_panels()),
        "capsule_count": len(load_capsules()),
        "tkinter_imported": True,
        "window_created": False,
        "real_execution_blocked": True,
        "full_ide_complete": False,
        "operational_action_commands": [command for _, command in OPERATIONAL_ACTIONS],
        "operational_actions_wired": cli_path() is not None,
        "required_station_panels_present": sorted(required_panels & panel_ids),
        "missing_station_panels": sorted(required_panels - panel_ids),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--smoke" in argv:
        return smoke()
    app = Workbench()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
