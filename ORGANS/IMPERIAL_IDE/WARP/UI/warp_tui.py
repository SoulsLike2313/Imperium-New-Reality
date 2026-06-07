#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP TUI VIEW (V0.1)

Text rendering of a warp session: stages, plan, criteria, metrics, staged diffs
and the gate verdict. Stdlib + ANSI only. Use --smoke for a non-interactive
self-render against a synthetic session (used in validation).

Purple dark nebula metallic palette (ANSI 256 approximations).
"""
import argparse
import json
import os
import sys

NEBULA = "\033[38;5;141m"
PLASMA = "\033[38;5;177m"
GOLD = "\033[38;5;179m"
CHROME = "\033[38;5;252m"
MUTED = "\033[38;5;103m"
GREEN = "\033[38;5;78m"
AMBER = "\033[38;5;179m"
RED = "\033[38;5;167m"
RESET = "\033[0m"

STAGES = ["INTAKE", "PLAN", "BUILD", "VALIDATE", "GATE", "RELEASED"]
VERDICT_COLOR = {"RELEASE": GREEN, "HOLD": AMBER, "DISCARD": RED}


def _c(on, code, s):
    return (code + s + RESET) if on else s


def _box(title, lines, on, width=74):
    head = "╔ " + title + " "
    head += "═" * max(0, width - len(title) - 3) + "╗"
    out = [_c(on, GOLD, head)]
    for ln in lines:
        out.append(_c(on, CHROME, "║ ") + ln[: width - 2].ljust(width - 2) + _c(on, GOLD, "║"))
    out.append(_c(on, GOLD, "╚" + "═" * width + "╝"))
    return "\n".join(out)


def _stage_bar(current, on):
    parts = []
    reached = True
    for s in STAGES:
        if s == current:
            parts.append(_c(on, PLASMA, "[◉ %s]" % s))
            reached = False
        elif reached:
            parts.append(_c(on, GREEN, "✓ %s" % s))
        else:
            parts.append(_c(on, MUTED, "· %s" % s))
    return "  ".join(parts)


def render(manifest, on=True):
    out = []
    out.append("")
    out.append(_c(on, NEBULA, "  >>>  W A R P   Z O N E  —  HOT DEVELOPMENT WORKROOM"))
    out.append(_c(on, MUTED, "  ядро чистое · вся грязь и рантаймы здесь · продукт выходит только через GATE"))
    out.append("")
    out.append("  " + _c(on, MUTED, "session: ") + _c(on, CHROME, manifest.get("id", "?")) +
               "   " + _c(on, MUTED, "kind: ") + _c(on, GOLD, manifest.get("kind", "?")) +
               "   " + _c(on, MUTED, "trigger: ") + _c(on, GOLD, manifest.get("trigger", "?")))
    out.append("  " + _stage_bar(manifest.get("stage", "INTAKE"), on))
    out.append("")

    parts = manifest.get("participants", [])
    plines = ["%-9s %-22s %s" % (p["kind"], p["name"], p["mode"]) for p in parts] or ["(none)"]
    out.append(_box("⚙ PARTICIPANTS (всё работает внутри WARP)", plines, on))
    out.append("")

    plan = manifest.get("plan", [])
    pl = ["%2d. %s" % (i + 1, s) for i, s in enumerate(plan)] or ["(план не задан)"]
    out.append(_box("⁂ PLAN", pl, on))
    out.append("")

    crit = manifest.get("criteria", [])
    metrics = manifest.get("metrics", {})
    cl = []
    for c in crit:
        m = metrics.get(c.get("metric", c["id"]))
        mark = "?"
        if m is not None:
            mark = "✓" if m.get("value") == c.get("expect", True) else "✗"
        cl.append("%s %-26s req=%s  ev=%s" % (
            mark, c.get("id"), c.get("required", True),
            (m or {}).get("evidence_level", "-")))
    out.append(_box("◆ CRITERIA / METRICS (definition of done)", cl or ["(нет)"], on))
    out.append("")

    changes = manifest.get("changes", [])
    dl = ["%-40s zone=%-9s +%d/-%d" % (
        c["path"][:40], c["zone"], c["stats"]["added"], c["stats"]["removed"])
        for c in changes] or ["(нет стейдженых дифов)"]
    out.append(_box("± STAGED DIFFS (ядро НЕ тронуто)", dl, on))
    out.append("")

    g = manifest.get("gate_result")
    if g:
        vc = VERDICT_COLOR.get(g["verdict"], CHROME)
        gl = [_c(on, vc, "VERDICT: %s" % g["verdict"])]
        for r in g.get("reasons", [])[:6]:
            gl.append("  - " + r)
        if not g.get("reasons"):
            gl.append("  все критерии выполнены — продукт может быть выпущен")
        out.append(_box("⚠ RELEASE GATE", gl, on))
    else:
        out.append(_box("⚠ RELEASE GATE", ["(шлюз ещё не запущен)"], on))
    out.append("")
    return "\n".join(out)


def _sample_manifest():
    return {
        "id": "WARP-SAMPLE-000000", "kind": "THIRD_PARTY", "trigger": "manual",
        "stage": "GATE",
        "participants": [
            {"kind": "kernel", "name": "CORE", "mode": "read"},
            {"kind": "organ", "name": "MECHANICUS", "mode": "dry-run"},
            {"kind": "servitor", "name": "CAP-ALPHA", "mode": "dry-run"},
            {"kind": "cli", "name": "imperial_ide_cli", "mode": "dry-run"},
        ],
        "plan": ["собрать стороннее ПО", "прогнать тесты", "собрать метрики", "шлюз"],
        "criteria": [
            {"id": "builds", "metric": "builds", "required": True, "expect": True, "min_evidence": "E3"},
            {"id": "tests_pass", "metric": "tests_pass", "required": True, "expect": True, "min_evidence": "E4"},
        ],
        "metrics": {
            "builds": {"value": True, "evidence_level": "E3"},
            "tests_pass": {"value": True, "evidence_level": "E4"},
        },
        "changes": [
            {"path": "PRODUCTS/dashboard/app.py", "zone": "UNKNOWN", "stats": {"added": 120, "removed": 0}},
            {"path": "ORGANS/ASTRONOMICON/CORE/route.py", "zone": "CORE", "stats": {"added": 4, "removed": 2}},
        ],
        "gate_result": {"verdict": "RELEASE", "failed": [], "fake_green": [], "reasons": []},
    }


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    p = argparse.ArgumentParser()
    p.add_argument("--session")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--no-color", action="store_true")
    a = p.parse_args(argv)
    on = not a.no_color
    if a.smoke or not a.session:
        print(render(_sample_manifest(), on=on))
        return
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = os.environ.get("WARP_ROOT", os.path.join(package_root, "runtime"))
    mp = os.path.join(root, a.session, "session_manifest.json")
    if not os.path.isfile(mp):
        print("no manifest for %s" % a.session)
        return
    with open(mp, "r", encoding="utf-8") as fh:
        print(render(json.load(fh), on=on))


if __name__ == "__main__":
    main()
