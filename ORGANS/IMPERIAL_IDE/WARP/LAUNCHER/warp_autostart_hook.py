#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP AUTOSTART HOOK (V0.1)

Drop-in hook the IDE / Astronomicon calls the moment a task is accepted, so the
warp zone opens AUTOMATICALLY (your "либо автоматически когда стартует
задача" path). The manual path is just the WARP button calling the same
function with trigger='manual'.

Contract: a task descriptor (dict or JSON file) with at least {task, kind}.
Returns the opened session manifest dict.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(os.path.dirname(HERE), "ENGINE")
sys.path.insert(0, ENGINE)

from warp_zone import WarpSession  # noqa: E402

AUTOSTART_REGISTERED = False


def open_for_task(task_descriptor, trigger="auto", core_root=None, warp_root=None):
    """Explicit candidate hook; it is not registered for automatic startup."""
    if isinstance(task_descriptor, str) and os.path.isfile(task_descriptor):
        with open(task_descriptor, "r", encoding="utf-8") as fh:
            task_descriptor = json.load(fh)
    if isinstance(task_descriptor, str):
        task_descriptor = {"task": task_descriptor, "kind": "THIRD_PARTY"}

    s = WarpSession(
        task=task_descriptor.get("task", "unnamed task"),
        kind=task_descriptor.get("kind", "THIRD_PARTY"),
        core_root=core_root or os.environ.get("IMPERIUM_ROOT"),
        warp_root=warp_root or os.environ.get("WARP_ROOT"),
        trigger=trigger,
    )
    # Auto-register everything that 'comes online' for the task.
    s.register("kernel", "CORE", mode="read")
    for organ in task_descriptor.get("organs", ["MECHANICUS", "ASTRONOMICON", "INQUISITION"]):
        s.register("organ", organ, mode="dry-run")
    for cap in task_descriptor.get("servitors", ["CAP-ALPHA", "CAP-BETA"]):
        s.register("servitor", cap, mode="dry-run")
    for api in task_descriptor.get("apis", []):
        s.register("api", api, mode="dry-run")
    s.register("cli", "imperial_ide_cli", mode="dry-run")
    if task_descriptor.get("plan"):
        s.set_plan(task_descriptor["plan"])
    if task_descriptor.get("criteria"):
        s.set_criteria(task_descriptor["criteria"])
    s.advance("PLAN")
    s.save_manifest()
    return s.manifest()


if __name__ == "__main__":
    td = sys.argv[1] if len(sys.argv) > 1 else {"task": "demo", "kind": "THIRD_PARTY"}
    print(json.dumps(open_for_task(td, trigger="auto"), ensure_ascii=False, indent=2))
