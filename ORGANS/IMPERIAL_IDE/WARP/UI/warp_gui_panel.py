#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP GUI PANEL (V0.1)

A Tkinter panel + the mandatory WARP BUTTON. Two ways the warp opens, exactly
as you asked:
  * automatically when a task starts (call WarpPanel.open_for_task(...) from the
    IDE's task-start hook), or
  * manually, by pressing the big WARP button.

Can run standalone for a look (python warp_gui_panel.py) or be embedded into the
Imperial IDE workbench (see DOCS/WARP_INTEGRATION_RU.md).

Purple dark nebula metallic theme. Real tool execution is never triggered from
here — the panel drives the warp stage machine + gate only.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(os.path.dirname(HERE), "ENGINE")
sys.path.insert(0, ENGINE)

VOID = "#05030B"
PANEL = "#0F0A1C"
PANEL2 = "#171029"
NEBULA = "#3A1E5C"
NEBULA2 = "#5B2E8A"
PLASMA = "#B96BFF"
GOLD = "#C9A24B"
CHROME = "#D6D6E6"
TEXT = "#ECEAF6"
MUTED = "#9A93B5"
GREEN = "#4FB58A"
AMBER = "#D8923A"
RED = "#B5354A"
VERDICT_COLOR = {"RELEASE": GREEN, "HOLD": AMBER, "DISCARD": RED}
STAGES = ["INTAKE", "PLAN", "BUILD", "VALIDATE", "GATE", "RELEASED"]


class WarpPanel:
    def __init__(self, parent, core_root=None, warp_root=None):
        import tkinter as tk
        self.tk = tk
        self.core_root = core_root or os.environ.get("IMPERIUM_ROOT")
        self.warp_root = warp_root or os.environ.get(
            "WARP_ROOT", os.path.join(os.getcwd(), "WARP", "runtime"))
        self.session = None
        self.frame = tk.Frame(parent, bg=VOID)

        header = tk.Frame(self.frame, bg=NEBULA)
        header.pack(fill="x")
        tk.Label(header, text="⊕  WARP ZONE  —  HOT DEVELOPMENT WORKROOM",
                 bg=NEBULA, fg=GOLD, font=("Consolas", 14, "bold")).pack(
            side="left", padx=12, pady=8)
        self.warp_btn = tk.Button(
            header, text="▶  ENTER WARP", command=self.on_warp_button,
            bg=NEBULA2, fg=CHROME, activebackground=PLASMA,
            font=("Consolas", 11, "bold"), relief="flat", padx=14, pady=4)
        self.warp_btn.pack(side="right", padx=12, pady=6)

        self.stage_lbl = tk.Label(self.frame, text=self._stage_text("INTAKE"),
                                  bg=VOID, fg=MUTED, font=("Consolas", 10))
        self.stage_lbl.pack(fill="x", padx=12, pady=(8, 4))

        body = tk.Frame(self.frame, bg=VOID)
        body.pack(fill="both", expand=True, padx=12, pady=6)
        self.diff_box = self._titled_text(body, "± STAGED DIFFS (ядро НЕ тронуто)")
        self.metric_box = self._titled_text(body, "◆ CRITERIA / METRICS")
        self.log_box = self._titled_text(body, "⚡ WARP LOG")

        self.status = tk.Label(self.frame, bg=NEBULA, fg=CHROME, anchor="w",
                               font=("Consolas", 9),
                               text="  warp: idle  │  kernel: read-only  │  release: gated")
        self.status.pack(fill="x", side="bottom")

    # ---- layout helpers ----
    def _titled_text(self, parent, title):
        tk = self.tk
        wrap = tk.Frame(parent, bg=PANEL, highlightbackground=GOLD,
                        highlightthickness=1)
        wrap.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(wrap, text=title, bg=PANEL, fg=GOLD,
                 font=("Consolas", 10, "bold")).pack(anchor="w", padx=8, pady=4)
        txt = tk.Text(wrap, bg=PANEL2, fg=TEXT, insertbackground=CHROME,
                      font=("Consolas", 9), relief="flat", height=14, width=34,
                      wrap="none")
        txt.pack(fill="both", expand=True, padx=6, pady=6)
        return txt

    def _stage_text(self, current):
        out = []
        reached = True
        for s in STAGES:
            if s == current:
                out.append("[◉ %s]" % s); reached = False
            elif reached:
                out.append("✓ %s" % s)
            else:
                out.append("· %s" % s)
        return "   ".join(out)

    def _log(self, msg):
        self.log_box.insert("end", "[%s] %s\n" % (time.strftime("%H:%M:%S"), msg))
        self.log_box.see("end")

    # ---- actions ----
    def on_warp_button(self):
        self.open_for_task({"task": "manual warp session", "kind": "THIRD_PARTY"},
                           trigger="manual")

    def open_for_task(self, task_descriptor, trigger="auto"):
        from warp_zone import WarpSession
        s = WarpSession(task=task_descriptor.get("task", "task"),
                        kind=task_descriptor.get("kind", "THIRD_PARTY"),
                        core_root=self.core_root, warp_root=self.warp_root,
                        trigger=trigger)
        s.register("kernel", "CORE", mode="read")
        s.register("organ", "MECHANICUS", mode="dry-run")
        s.register("servitor", "CAP-ALPHA", mode="dry-run")
        s.advance("PLAN")
        s.save_manifest()
        self.session = s
        self.stage_lbl.config(text=self._stage_text(s.stage), fg=PLASMA)
        self.status.config(text="  warp: %s  │  trigger: %s  │  kernel: read-only"
                                % (s.id, trigger))
        self._log("WARP opened (%s): %s" % (trigger, s.id))
        self.refresh()
        return s

    def refresh(self):
        if not self.session:
            return
        self.diff_box.delete("1.0", "end")
        for c in self.session.changes:
            self.diff_box.insert("end", "%s\n  zone=%s  +%d/-%d\n" % (
                c["path"], c["zone"], c["stats"]["added"], c["stats"]["removed"]))
        self.metric_box.delete("1.0", "end")
        for c in self.session.criteria:
            m = self.session.metrics.get(c.get("metric", c["id"]))
            self.metric_box.insert("end", "%s  ev=%s\n" % (
                c.get("id"), (m or {}).get("evidence_level", "-")))

    def run_gate(self):
        if not self.session:
            return
        res = self.session.run_gate()
        self.stage_lbl.config(text=self._stage_text(self.session.stage))
        self._log("GATE verdict: %s" % res["verdict"])
        self.status.config(fg=VERDICT_COLOR.get(res["verdict"], CHROME),
                           text="  GATE: %s" % res["verdict"])
        return res

    def pack(self, **kw):
        self.frame.pack(**kw)
        return self


def _standalone():
    import tkinter as tk
    root = tk.Tk()
    root.title("WARP ZONE — standalone preview")
    root.configure(bg=VOID)
    root.geometry("1100x640")
    WarpPanel(root).pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    _standalone()
