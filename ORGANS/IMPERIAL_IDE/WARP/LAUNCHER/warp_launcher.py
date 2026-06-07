#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP LAUNCHER (V0.1) — CLI entry into the warp zone.

The IDE calls this to OPEN a warp session when a task starts (auto) or when
you press the WARP button (manual). It also drives the stage machine and the
gate from the command line / servitors.

Usage:
  python warp_launcher.py open  --task "..." --kind THIRD_PARTY [--auto] [--core E:\\repo]
  python warp_launcher.py status --session WARP-...
  python warp_launcher.py gate   --session WARP-...
  python warp_launcher.py release --session WARP-...
  python warp_launcher.py discard --session WARP-... --reason "..."
  python warp_launcher.py list

The launcher is intentionally thin: the engine in ../ENGINE owns the logic.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(os.path.dirname(HERE), "ENGINE")
sys.path.insert(0, ENGINE)

from warp_zone import WarpSession, KINDS  # noqa: E402
import warp_gate as gate  # noqa: E402
from warp_eventlog import EventLog  # noqa: E402


def _warp_root():
    package_root = os.path.dirname(HERE)
    return os.environ.get("WARP_ROOT", os.path.join(package_root, "runtime"))


def _load_manifest(session):
    path = os.path.join(_warp_root(), session, "session_manifest.json")
    if not os.path.isfile(path):
        raise SystemExit("no manifest for session %s" % session)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def cmd_open(a):
    s = WarpSession(task=a.task, kind=a.kind, core_root=a.core,
                    warp_root=_warp_root(),
                    trigger="auto" if a.auto else "manual")
    # Register the standard participants that join every warp session.
    s.register("kernel", "CORE", mode="read")
    s.register("organ", "MECHANICUS", mode="dry-run")
    s.register("servitor", "CAP-ALPHA", mode="dry-run")
    s.register("cli", "imperial_ide_cli", mode="dry-run")
    s.advance("PLAN")
    s.save_manifest()
    print(json.dumps({"session": s.id, "workdir": s.workdir,
                      "trigger": s.trigger, "stage": s.stage},
                     ensure_ascii=False, indent=2))


def cmd_status(a):
    m = _load_manifest(a.session)
    print(json.dumps(m, ensure_ascii=False, indent=2))


def cmd_gate(a):
    m = _load_manifest(a.session)
    res = gate.evaluate(m.get("criteria", []), m.get("metrics", {}),
                        min_evidence=a.min_evidence)
    print(json.dumps(res, ensure_ascii=False, indent=2))


def cmd_list(a):
    root = _warp_root()
    if not os.path.isdir(root):
        print("[]")
        return
    out = []
    for d in sorted(os.listdir(root)):
        mp = os.path.join(root, d, "session_manifest.json")
        if os.path.isfile(mp):
            with open(mp, "r", encoding="utf-8") as fh:
                m = json.load(fh)
            out.append({"session": m["id"], "stage": m["stage"],
                        "task": m["task"], "kind": m["kind"]})
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_discard(a):
    log = EventLog(os.path.join(_warp_root(), a.session, "events.jsonl"))
    log.append("discard", reason=a.reason, via="launcher")
    print(json.dumps({"session": a.session, "discarded": True,
                      "reason": a.reason}, ensure_ascii=False))


def main(argv=None):
    p = argparse.ArgumentParser(prog="warp_launcher")
    sub = p.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("open")
    o.add_argument("--task", required=True)
    o.add_argument("--kind", default="THIRD_PARTY", choices=KINDS)
    o.add_argument("--core", default=os.environ.get("IMPERIUM_ROOT"))
    o.add_argument("--auto", action="store_true")
    o.set_defaults(fn=cmd_open)

    st = sub.add_parser("status"); st.add_argument("--session", required=True); st.set_defaults(fn=cmd_status)
    g = sub.add_parser("gate"); g.add_argument("--session", required=True); g.add_argument("--min-evidence", dest="min_evidence", default="E3"); g.set_defaults(fn=cmd_gate)
    ls = sub.add_parser("list"); ls.set_defaults(fn=cmd_list)
    d = sub.add_parser("discard"); d.add_argument("--session", required=True); d.add_argument("--reason", default=""); d.set_defaults(fn=cmd_discard)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
