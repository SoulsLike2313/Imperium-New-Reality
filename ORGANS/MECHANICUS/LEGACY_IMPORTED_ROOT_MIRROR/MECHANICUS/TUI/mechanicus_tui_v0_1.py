from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Any, Dict

HERE = Path(__file__).resolve()
NEWGEN_ROOT = HERE.parents[2]
COMMON_ROOT = NEWGEN_ROOT / "ORGAN_AGENT_COMMON"
if str(COMMON_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMON_ROOT))

from organ_agent_runtime_v0_1 import (
    HAVE_RICH,
    build_verdict_payload,
    read_organ_bundle,
    render_tui,
    utc_now,
)

TASK_ID_DEFAULT = "TASK-20260524-NEWGEN-CORE-ORGAN-FORM-TUI-WAVE1-VM3-V0_1"
ORGAN_ID = "MECHANICUS"
ORGAN_ROOT = HERE.parents[1]
COLOR = "red"


def _probe_rich() -> Dict[str, Any]:
    try:
        import rich  # type: ignore

        return {
            "available": True,
            "version": importlib.metadata.version("rich"),
            "module_path": str(Path(rich.__file__).resolve()),
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def build_payload(task_id: str) -> Dict[str, Any]:
    bundle = read_organ_bundle(ORGAN_ROOT)
    state = bundle.get("state", {})
    gates = bundle.get("gate_catalog", {}).get("gates", [])
    applied_rules = [str(g.get("gate_id", "")) for g in gates if isinstance(g, dict)]
    rich_probe = _probe_rich()
    payload = build_verdict_payload(
        organ_id=ORGAN_ID,
        task_id=task_id,
        mode="SMOKE",
        verdict="PASS" if rich_probe.get("available") else "BLOCK",
        applied_rules=applied_rules,
        required_actions=state.get("required_actions", []),
        forbidden_actions=state.get("forbidden_actions", []),
        evidence_required=[],
        evidence_refs=state.get("evidence_refs", []),
        not_proven=[
            "full production-grade tool admission framework",
            "autonomic remediation loops",
        ],
        owner_question=None,
    )
    payload["rich_probe"] = rich_probe
    payload["generated_at_utc"] = utc_now()
    return {"bundle": bundle, "verdict_payload": payload}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave1 Mechanicus Rich TUI.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--plain-json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = build_payload(str(args.task_id))
    bundle = data["bundle"]
    verdict_payload = data["verdict_payload"]
    state = bundle.get("state", {})

    if args.plain_json:
        print(
            json.dumps(
                {
                    "organ_id": ORGAN_ID,
                    "rich_available": HAVE_RICH,
                    "smoke_mode": bool(args.smoke),
                    "responsibility": state.get("responsibility", ""),
                    "bundle": bundle,
                    "verdict": verdict_payload,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    render_tui(
        organ_title=ORGAN_ID,
        color=COLOR,
        responsibility=str(state.get("responsibility", "")),
        ask_map=state.get("servitor_ask", []),
        warn_block_map=state.get("warn_block_profile", []),
        bundle=bundle,
        verdict_payload=verdict_payload,
    )
    if args.smoke:
        print("SMOKE_OK_MECHANICUS_TUI_V0_1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
