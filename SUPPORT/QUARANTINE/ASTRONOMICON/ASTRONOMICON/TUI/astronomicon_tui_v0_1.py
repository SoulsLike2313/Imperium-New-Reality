from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
ASTRONOMICON_ROOT = HERE.parents[1]
DEFAULT_TASK_ID = "TASK-NEWGEN-VM3-ROUTE-REGISTRY-ASTRONOMICON-BODY-UBUNTU-V0_1"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object JSON at {path}")
    return payload


def build_snapshot(task_id: str) -> dict[str, Any]:
    route_map = _load_json(ASTRONOMICON_ROOT / "ROUTING" / "organ_route_map_v0_1.json")
    decision_registry = _load_json(ASTRONOMICON_ROOT / "ROUTING" / "route_decision_registry_v0_1.json")
    body_manifest = _load_json(ASTRONOMICON_ROOT / "BODY" / "astronomicon_body_manifest_v0_1.json")
    essence_examples = _load_json(ASTRONOMICON_ROOT / "FIXTURES" / "task_essence_examples_v0_1.json")
    route_examples = _load_json(ASTRONOMICON_ROOT / "FIXTURES" / "route_packet_examples_v0_1.json")

    route_families = route_map.get("route_families", [])
    decisions = decision_registry.get("decisions", [])

    return {
        "schema_version": "astronomicon.tui_snapshot.v0_1",
        "task_id": task_id,
        "organ": "ASTRONOMICON",
        "mode": "READ_ONLY_INSPECTOR",
        "body_purpose": body_manifest.get("purpose", ""),
        "route_family_count": len(route_families) if isinstance(route_families, list) else 0,
        "decision_count": len(decisions) if isinstance(decisions, list) else 0,
        "task_essence_example_count": len(essence_examples.get("examples", [])) if isinstance(essence_examples.get("examples"), list) else 0,
        "route_packet_example_count": len(route_examples.get("examples", [])) if isinstance(route_examples.get("examples"), list) else 0,
        "not_proven_boundary": [
            "Read-only inspector only",
            "No runtime WARP implementation",
            "No Agent IDE integration"
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Astronomicon read-only TUI inspector v0.1")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--plain-json", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = build_snapshot(str(args.task_id))

    if args.plain_json:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    else:
        print("ASTRONOMICON READ-ONLY INSPECTOR V0.1")
        print(f"Task ID: {snapshot['task_id']}")
        print(f"Body purpose: {snapshot['body_purpose']}")
        print(f"Route families: {snapshot['route_family_count']}")
        print(f"Route decisions: {snapshot['decision_count']}")
        print(f"Task essence examples: {snapshot['task_essence_example_count']}")
        print(f"Route packet examples: {snapshot['route_packet_example_count']}")
        print("Not proven boundary:")
        for item in snapshot["not_proven_boundary"]:
            print(f"- {item}")

    if args.smoke:
        print("SMOKE_OK_ASTRONOMICON_TUI_V0_1")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
