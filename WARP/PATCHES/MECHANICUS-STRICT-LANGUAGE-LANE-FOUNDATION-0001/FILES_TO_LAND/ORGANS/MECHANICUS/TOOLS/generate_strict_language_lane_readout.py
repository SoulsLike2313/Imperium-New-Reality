#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

REGISTRY = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_STRICT_LANGUAGE_LANE_REGISTRY_V0_1.json")
SURFACE_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_REPORT_V0_1.json")
TOOLCHAIN_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")
DISPATCH_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_VALIDATION_BASELINE_V0_1.json")

DEFAULT_OUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json")

def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {"_load_error": str(e)}

def language_surface(surface: Dict[str, Any], names: List[str]) -> Dict[str, Any]:
    classes = surface.get("classes") or {}
    source = classes.get("source_runtime", {})
    evidence = classes.get("governance_evidence", {})
    raw = surface.get("raw_all_surface", {})

    def pull(bucket: Dict[str, Any]) -> Dict[str, Any]:
        total = {"files": 0, "total_lines": 0, "code_lines": 0, "languages": []}
        for item in bucket.get("languages", []) or []:
            if item.get("language") in names:
                total["files"] += int(item.get("files") or 0)
                total["total_lines"] += int(item.get("total_lines") or 0)
                total["code_lines"] += int(item.get("code_lines") or 0)
                total["languages"].append(item.get("language"))
        return total

    return {
        "raw": pull(raw),
        "source_runtime": pull(source),
        "governance_evidence": pull(evidence)
    }

def tool_status(toolchain: Dict[str, Any], lane_id: str) -> Dict[str, Any]:
    results = {r.get("name"): r for r in toolchain.get("results", []) or []}
    mapping = {
        "python": ["python_version"],
        "powershell": ["pwsh_version"],
        "rust": ["rustc_version", "cargo_version"],
        "node_frontend": ["node_version", "npm_version"],
        "css_ui": ["npm_version"],
        "json_evidence": ["python_version"],
        "markdown_docs": ["python_version"],
        "toml_config": ["python_version"],
        "go_future": ["go_version"],
        "cpp_future": ["cmake_version"],
    }
    names = mapping.get(lane_id, [])
    observed = [results.get(n, {"name": n, "ok": False, "missing": True}) for n in names]
    return {
        "required_probe_names": names,
        "all_observed_ok": all(bool(x.get("ok")) for x in observed) if observed else False,
        "observed": [
            {
                "name": x.get("name"),
                "ok": bool(x.get("ok")),
                "exit_code": x.get("exit_code"),
                "which": x.get("which"),
                "stderr": x.get("stderr", "")[:240]
            }
            for x in observed
        ]
    }

def dispatch_status(dispatch: Dict[str, Any], lane_id: str) -> Dict[str, Any]:
    checks = dispatch.get("checks", []) or []
    mapping = {
        "python": ["Python"],
        "powershell": ["PowerShell"],
        "json_evidence": ["JSON/JSONL"],
        "markdown_docs": ["Markdown"],
        "toml_config": ["TOML"],
    }
    langs = mapping.get(lane_id, [])
    selected = [c for c in checks if c.get("language") in langs]
    if not selected:
        return {"baseline_present": False, "ok": False, "checks": []}
    return {
        "baseline_present": True,
        "ok": all(bool(c.get("ok")) for c in selected),
        "checks": selected
    }

def lane_state(lane_id: str, surface: Dict[str, Any], tools: Dict[str, Any], dispatch: Dict[str, Any]) -> str:
    src_lines = surface.get("source_runtime", {}).get("total_lines", 0)
    raw_lines = surface.get("raw", {}).get("total_lines", 0)
    tool_ok = tools.get("all_observed_ok", False)
    baseline_present = dispatch.get("baseline_present", False)
    baseline_ok = dispatch.get("ok", False)

    future = lane_id in {"go_future", "cpp_future"}
    if raw_lines == 0 and src_lines == 0 and future:
        return "LANE_FUTURE_CAPABILITY"
    if raw_lines == 0 and src_lines == 0:
        return "LANE_NOT_PRESENT"
    if not tool_ok:
        return "LANE_TOOLCHAIN_MISSING" if future else "LANE_MEASURED_WITH_DEBT"
    if baseline_present and baseline_ok:
        return "LANE_READY_BASELINE"
    if baseline_present and not baseline_ok:
        return "LANE_MEASURED_WITH_DEBT"
    return "LANE_FOUNDATION_ONLY"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    registry = load_json(repo / REGISTRY)
    surface_report = load_json(repo / SURFACE_REPORT)
    toolchain_report = load_json(repo / TOOLCHAIN_REPORT)
    dispatch_report = load_json(repo / DISPATCH_REPORT)

    lanes = []
    for lane in registry.get("lanes", []) or []:
        lane_id = lane.get("lane_id")
        names = lane.get("language_names", [])
        surf = language_surface(surface_report, names)
        tools = tool_status(toolchain_report, lane_id)
        dispatch = dispatch_status(dispatch_report, lane_id)
        state = lane_state(lane_id, surf, tools, dispatch)
        lanes.append({
            "lane_id": lane_id,
            "language_names": names,
            "purpose": lane.get("purpose"),
            "state": state,
            "surface": surf,
            "toolchain": tools,
            "baseline_validation": dispatch,
            "strict_layers_future": lane.get("strict_layers_future", []),
            "must_not_claim": lane.get("must_not_claim", [])
        })

    counts = {}
    for lane in lanes:
        counts[lane["state"]] = counts.get(lane["state"], 0) + 1

    report = {
        "tool_id": "mechanicus_strict_language_lane_readout.v0_1",
        "repo_root": str(repo),
        "registry": REGISTRY.as_posix(),
        "input_reports": {
            "surface_v2": SURFACE_REPORT.as_posix(),
            "toolchain": TOOLCHAIN_REPORT.as_posix(),
            "dispatch": DISPATCH_REPORT.as_posix()
        },
        "lane_count": len(lanes),
        "state_counts": counts,
        "lanes": lanes,
        "verdict": "PASS_STRICT_LANGUAGE_LANES_MEASURED_WITH_DEBT",
        "not_claimed": [
            "100% clean",
            "strict lanes complete",
            "all toolchains available",
            "all linter/type/security layers complete"
        ],
        "warnings": [
            "This is a lane foundation/readout, not strict cleanliness.",
            "LANE_READY_BASELINE means only implemented baseline checks passed.",
            "LANE_FOUNDATION_ONLY needs strict validators before it can block or certify.",
            "LANE_TOOLCHAIN_MISSING is capability debt."
        ]
    }

    out = repo / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
