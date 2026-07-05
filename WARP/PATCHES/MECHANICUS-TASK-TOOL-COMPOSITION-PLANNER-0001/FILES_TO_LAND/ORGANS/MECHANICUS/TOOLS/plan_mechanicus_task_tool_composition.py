#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

TAXONOMY = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TASK_CAPABILITY_DEMAND_TAXONOMY_V0_1.json")
SCORING = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_COMPOSITION_SCORING_MATRIX_V0_1.json")
INVENTORY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_INVENTORY_V0_1.json")
LANE_READOUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json")
TOOLCHAIN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")
DEFAULT_OUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {"_load_error": str(e)}

def read_task(repo: Path, task_text: str | None, task_file: str | None, patch_id: str | None) -> Tuple[str, str]:
    if task_text:
        return "inline_task_text", task_text
    if task_file:
        p = repo / task_file
        if p.is_file():
            return p.as_posix(), p.read_text(encoding="utf-8", errors="replace")
        return task_file, ""
    if patch_id:
        candidates = [
            repo / "WARP" / "PATCHES" / patch_id / "PATCH_PACK.md",
            repo / "WARP" / "PATCHES" / patch_id / "TASK_PACK.md",
        ]
        for p in candidates:
            if p.is_file():
                return p.relative_to(repo).as_posix(), p.read_text(encoding="utf-8", errors="replace")
        return f"WARP/PATCHES/{patch_id}", ""
    return "empty_task", ""

def tokenize(text: str) -> str:
    return " " + re.sub(r"\s+", " ", text.lower()) + " "

def classify_demands(text: str, taxonomy: Dict[str, Any]) -> List[Dict[str, Any]]:
    t = tokenize(text)
    results = []
    for demand in taxonomy.get("demand_classes", []) or []:
        hits = []
        for kw in demand.get("keywords", []):
            if kw.lower() in t:
                hits.append(kw)
        score = min(100, len(hits) * 18)
        if hits:
            results.append({
                "demand_id": demand.get("demand_id"),
                "score": score,
                "matched_keywords": hits,
                "preferred_lanes": demand.get("preferred_lanes", []),
                "required_validators": demand.get("required_validators", []),
                "typical_tools": demand.get("typical_tools", [])
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def lane_map(readout: Dict[str, Any]) -> Dict[str, Any]:
    return {lane.get("lane_id"): lane for lane in readout.get("lanes", []) or []}

def toolchain_map(toolchain: Dict[str, Any]) -> Dict[str, Any]:
    return {r.get("name"): r for r in toolchain.get("results", []) or []}

def existing_tool_names(inventory: Dict[str, Any]) -> List[str]:
    names = []
    for rec in inventory.get("records", []) or []:
        if rec.get("admission_state") in {"ADMITTED_BASELINE", "ADMITTED_STRICT"}:
            names.append(str(rec.get("name") or rec.get("path_or_command") or ""))
    return names

def score_stack(demand: Dict[str, Any], lanes: Dict[str, Any], inventory: Dict[str, Any], scoring: Dict[str, Any]) -> Dict[str, Any]:
    preferred = demand.get("preferred_lanes", [])
    admitted_names = existing_tool_names(inventory)
    lane_states = []
    ready = 0
    debt = 0
    future_or_missing = 0
    for lane_id in preferred:
        state = (lanes.get(lane_id) or {}).get("state", "LANE_UNKNOWN")
        lane_states.append({"lane_id": lane_id, "state": state})
        if state == "LANE_READY_BASELINE":
            ready += 1
        elif state == "LANE_MEASURED_WITH_DEBT":
            debt += 1
        else:
            future_or_missing += 1

    total_lanes = max(1, len(preferred))
    requirement_fit = min(100, 55 + int(demand.get("score", 0)) // 2)
    availability = int((ready / total_lanes) * 100)
    if debt:
        availability = max(0, availability - 12 * debt)
    if future_or_missing:
        availability = max(0, availability - 22 * future_or_missing)

    validator_count = len(demand.get("required_validators", []))
    cleanliness = min(100, 35 + ready * 12 + validator_count * 8 - debt * 10 - future_or_missing * 18)
    reliability = min(100, 40 + ready * 10 + len(admitted_names[:10]) * 1 - debt * 8 - future_or_missing * 16)

    heavy = {"game_engine_or_procedural_world", "tauri_app_or_cockpit", "visual_ui_polish"}
    cost = 62 if demand.get("demand_id") in heavy else 82
    if future_or_missing:
        cost -= 20

    maintainability = 80 if len(preferred) <= 4 else 68
    if len(preferred) > 5:
        maintainability -= 15

    weights = {d["id"]: int(d["weight"]) for d in scoring.get("dimensions", []) if isinstance(d, dict)}
    weighted = (
        requirement_fit * weights.get("requirement_fit", 25) +
        availability * weights.get("availability_and_admission", 20) +
        cleanliness * weights.get("cleanliness_validation_coverage", 20) +
        reliability * weights.get("reliability_and_receipts", 15) +
        cost * weights.get("cost_and_runtime_weight", 10) +
        maintainability * weights.get("maintainability_no_monolith", 10)
    ) / 100.0

    verdict = "NOT_RECOMMENDED_OR_CAPABILITY_MISSING"
    for band in sorted(scoring.get("verdict_bands", []), key=lambda b: int(b.get("min", 0)), reverse=True):
        if weighted >= int(b.get("min", 0)):
            verdict = band.get("verdict")
            break

    return {
        "demand_id": demand.get("demand_id"),
        "score_0_to_100": round(weighted, 2),
        "verdict": verdict,
        "preferred_lanes": preferred,
        "lane_states": lane_states,
        "dimensions": {
            "requirement_fit": requirement_fit,
            "availability_and_admission": availability,
            "cleanliness_validation_coverage": cleanliness,
            "reliability_and_receipts": reliability,
            "cost_and_runtime_weight": cost,
            "maintainability_no_monolith": maintainability
        },
        "required_validators": demand.get("required_validators", []),
        "typical_tools": demand.get("typical_tools", [])
    }

def missing_capabilities(text: str, classified: List[Dict[str, Any]], lanes: Dict[str, Any], toolchain: Dict[str, Any], inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    missing = []
    t = tokenize(text)
    tc = toolchain_map(toolchain)

    if any(d.get("demand_id") == "game_engine_or_procedural_world" for d in classified):
        engine_names = [str(r.get("name", "")).lower() for r in inventory.get("records", []) or []]
        if not any(x in " ".join(engine_names) for x in ["godot", "bevy", "unity", "unreal", "engine"]):
            missing.append({
                "capability_id": "GAME_ENGINE_CAPABILITY_NOT_INVENTORIED",
                "severity": "OWNER_VISIBLE_GAP",
                "meaning": "Task asks for game/procedural engine capability, but no admitted engine tool is inventoried."
            })

    if "go" in t or "golang" in t:
        if not tc.get("go_version", {}).get("ok"):
            missing.append({"capability_id": "GO_TOOLCHAIN_MISSING", "severity": "CAPABILITY_DEBT", "meaning": "Go requested or implied, but go toolchain is missing."})

    if any(x in t for x in ["c++", "cpp", "cmake"]):
        if not tc.get("cmake_version", {}).get("ok"):
            missing.append({"capability_id": "CPP_CMAKE_TOOLCHAIN_MISSING", "severity": "CAPABILITY_DEBT", "meaning": "C++/CMake requested or implied, but cmake/compiler lane is missing."})

    if any(x in t for x in ["strict", "build", "runtime", "cargo check", "npm build", "строг"]):
        missing.append({
            "capability_id": "STRICT_BUILD_LANE_REQUIRED",
            "severity": "NEXT_VALIDATOR_REQUIRED",
            "meaning": "Task asks for strict/build/runtime confidence; planner can recommend but strict build lane must run separately."
        })

    if any(x in t for x in ["reference", "fidelity", "реф", "pixel", "ui"]):
        missing.append({
            "capability_id": "UI_REFERENCE_FIDELITY_TOOLING_REQUIRED_IF_TARGET_UI",
            "severity": "CONDITIONAL_GAP",
            "meaning": "UI/reference work needs a dedicated fidelity proof lane; visual similarity cannot be claimed from CSS alone."
        })

    if not classified:
        missing.append({
            "capability_id": "UNKNOWN_TASK_DEMAND",
            "severity": "OWNER_CLARIFICATION_OR_RESEARCH_REQUIRED",
            "meaning": "No demand class reached detection threshold."
        })

    return missing

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--task-text", default=None)
    ap.add_argument("--task-file", default=None)
    ap.add_argument("--patch-id", default=None)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    source, text = read_task(repo, args.task_text, args.task_file, args.patch_id)
    taxonomy = load_json(repo / TAXONOMY)
    scoring = load_json(repo / SCORING)
    inventory = load_json(repo / INVENTORY)
    readout = load_json(repo / LANE_READOUT)
    toolchain = load_json(repo / TOOLCHAIN)

    classified = classify_demands(text, taxonomy)
    lanes = lane_map(readout)
    combinations = [score_stack(d, lanes, inventory, scoring) for d in classified]
    combinations.sort(key=lambda x: x["score_0_to_100"], reverse=True)

    recommended = combinations[0] if combinations else None
    recommended_lanes = recommended.get("preferred_lanes", []) if recommended else []
    validators = []
    for c in combinations[:3]:
        for v in c.get("required_validators", []):
            if v not in validators:
                validators.append(v)

    missing = missing_capabilities(text, classified, lanes, toolchain, inventory)
    blockers = [m for m in missing if m.get("severity") in {"OWNER_VISIBLE_GAP", "OWNER_CLARIFICATION_OR_RESEARCH_REQUIRED"}]

    plan = {
        "tool_id": "mechanicus_task_tool_composition_planner.v0_1",
        "generated_at_utc": utc(),
        "repo_root": str(repo),
        "task_source": source,
        "task_text_preview": text[:1200],
        "task_demand_classification": classified,
        "candidate_combinations_with_scores": combinations,
        "recommended_tool_stack": recommended,
        "recommended_language_lanes": recommended_lanes,
        "required_validators": validators,
        "missing_capabilities": missing,
        "owner_visible_blockers": blockers,
        "verdict": "PLAN_READY_WITH_CAPABILITY_GAPS" if missing else "PLAN_READY",
        "not_claimed": [
            "task executed",
            "runtime proof",
            "dependencies installed",
            "100% clean",
            "strict build pass"
        ],
        "warnings": [
            "Tool composition plan is advisory and does not execute the task.",
            "Missing capabilities must remain visible until resolved or Owner-waived.",
            "Strict build/runtime validators remain separate lanes."
        ]
    }

    out = repo / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
