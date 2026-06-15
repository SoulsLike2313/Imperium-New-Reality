#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanicus state machine seed v0.4.

Stdlib-only, read-only seed used to prevent future endless-if growth.
No live execution, no shell, no network, no mutation.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Dict, Tuple

STATES = [
    "INTAKE",
    "SPEC",
    "SCHEMA",
    "TOOL_MAP",
    "DRY_RUN",
    "EVIDENCE",
    "OWNER_GATE",
    "READY",
]

TRANSITIONS: Dict[Tuple[str, str], str] = {
    ("INTAKE", "brief_accepted"): "SPEC",
    ("SPEC", "pass_criteria_clear"): "SCHEMA",
    ("SCHEMA", "schemas_written"): "TOOL_MAP",
    ("TOOL_MAP", "tools_classified"): "DRY_RUN",
    ("DRY_RUN", "dry_run_passed"): "EVIDENCE",
    ("EVIDENCE", "receipts_ready"): "OWNER_GATE",
    ("OWNER_GATE", "owner_accepts"): "READY",
}

@dataclass(frozen=True)
class MachineSnapshot:
    state: str
    allowed_events: list[str]
    live_execution_enabled: bool = False
    unsafe_shell_enabled: bool = False
    live_llm_backend_enabled: bool = False


def allowed_events(state: str) -> list[str]:
    return sorted(event for (src, event), _dst in TRANSITIONS.items() if src == state)


def transition(state: str, event: str) -> MachineSnapshot:
    dst = TRANSITIONS.get((state, event))
    if not dst:
        raise ValueError(f"transition blocked: {state!r} + {event!r}")
    return MachineSnapshot(state=dst, allowed_events=allowed_events(dst))


def smoke() -> dict[str, object]:
    state = "INTAKE"
    path = [state]
    for event in ["brief_accepted", "pass_criteria_clear", "schemas_written", "tools_classified", "dry_run_passed", "receipts_ready", "owner_accepts"]:
        snap = transition(state, event)
        state = snap.state
        path.append(state)
    return {
        "status": "PASS_WITH_WARNINGS",
        "organ": "MECHANICUS",
        "surface": "MECHANICUS_STATE_MACHINE_SEED_V0_4",
        "states": STATES,
        "path": path,
        "final_state": state,
        "live_execution_enabled": False,
        "unsafe_shell_enabled": False,
        "live_llm_backend_enabled": False,
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if "--smoke" in argv or not argv:
        print(json.dumps(smoke(), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"status":"BLOCKED", "reason":"only --smoke is supported in v0.4 seed"}, ensure_ascii=False, indent=2))
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
