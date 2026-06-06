#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ["ADMINISTRATUM_AGENT", "CUSTODES_AGENT", "MECHANICUS_AGENT"]


def count_json_units(obj):
    if isinstance(obj, dict):
        return len(obj) + sum(count_json_units(v) for v in obj.values())
    if isinstance(obj, list):
        return len(obj) + sum(count_json_units(v) for v in obj)
    return 1


def non_empty_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def count_agent(agent: str) -> int:
    base = ROOT / "ORGAN_AGENTS" / agent
    manifest = json.loads((base / "agent_manifest.json").read_text(encoding="utf-8"))
    units = 0
    units += count_json_units(manifest)
    units += non_empty_lines(base / "role_contract.md")
    units += non_empty_lines(base / "operating_rules.md")
    units += non_empty_lines(base / "memory" / "working_memory.json")
    units += non_empty_lines(base / "brain_node" / "README.md")
    units += non_empty_lines(base / "skills" / "README.md")
    units += non_empty_lines(base / "runner" / "README.md")
    return units


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = {"agents": {}, "target_future_min_per_agent": 3000}
    for agent in AGENTS:
        result["agents"][agent] = {"current_units": count_agent(agent)}

    result["summary"] = {
        "total_units_first_three": sum(v["current_units"] for v in result["agents"].values()),
        "note": "Baseline counter only. No filler generation used.",
    }

    out = ROOT / "REPORTS" / "FIRST_THREE_AGENT_UNIT_BASELINE_V0_1.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for name, info in result["agents"].items():
            print(f"{name}: {info['current_units']}")
        print(f"TOTAL: {result['summary']['total_units_first_three']}")
        print(f"UNITS_JSON: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
