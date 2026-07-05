#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TOOL_ID = "mechanicus_task_tool_composition_planner.v0_3_hard_safe"

LANE_READOUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json")
TOOLCHAIN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")
INVENTORY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_INVENTORY_V0_1.json")
DEFAULT_OUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")

DEMANDS = [
    {
        "demand_id": "python_validator_or_scanner",
        "keywords": ["validator", "scan", "scanner", "census", "receipt", "report", "json", "matrix", "валидатор", "скан", "отчет", "отчёт", "матриц"],
        "preferred_lanes": ["python", "json_evidence", "markdown_docs"],
        "required_validators": ["python py_compile", "json parse", "receipt shape"],
        "typical_tools": ["python", "Mechanicus inventory scanner", "language validation dispatch"]
    },
    {
        "demand_id": "warp_runner_or_windows_operator",
        "keywords": ["pwsh", "powershell", "runner", "run_", "warp", "patch pack", "task pack", "таск пак", "патч пак"],
        "preferred_lanes": ["powershell", "python", "json_evidence"],
        "required_validators": ["pwsh version", "runner receipt", "no direct master mutation"],
        "typical_tools": ["pwsh", "WARP runner", "git"]
    },
    {
        "demand_id": "tauri_app_or_cockpit",
        "keywords": ["tauri", "cockpit", "app", "webview", "frontend", "ui", "ux", "приложение", "кокпит", "интерфейс"],
        "preferred_lanes": ["node_frontend", "css_ui", "rust", "json_evidence"],
        "required_validators": ["npm build", "cargo check", "runtime FPS proof", "UX proof receipt"],
        "typical_tools": ["node", "npm", "rustc", "cargo", "Tauri app shell"]
    },
    {
        "demand_id": "rust_backend_or_compiled_gate",
        "keywords": ["rust", "cargo", "compiled", "tauri backend", "strict gate", "безопасность", "строгий", "компил"],
        "preferred_lanes": ["rust", "json_evidence"],
        "required_validators": ["cargo check", "cargo fmt", "cargo clippy future"],
        "typical_tools": ["rustc", "cargo"]
    },
    {
        "demand_id": "visual_ui_polish",
        "keywords": ["css", "style", "animation", "ornament", "gothic", "metal", "fps", "visual", "reference", "готика", "орнамент", "анимация", "визуал", "реф"],
        "preferred_lanes": ["css_ui", "node_frontend", "json_evidence"],
        "required_validators": ["CSS structural scan", "FPS proof", "reference fidelity report", "no CSS monolith"],
        "typical_tools": ["CSS lane", "Tauri app", "FPS watchdog"]
    },
    {
        "demand_id": "game_engine_or_procedural_world",
        "keywords": ["game", "engine", "godot", "bevy", "unity", "unreal", "игра", "движок", "процедур"],
        "preferred_lanes": ["node_frontend", "rust", "css_ui", "go_future", "cpp_future"],
        "required_validators": ["engine capability proof", "runtime performance proof", "asset pipeline proof"],
        "typical_tools": ["game engine candidate", "runtime profiler", "asset pipeline"]
    },
    {
        "demand_id": "external_repo_product_work",
        "keywords": ["external repo", "внешний репозиторий", "продукт", "рынок", "script", "скрипт", "repo analysis", "репо"],
        "preferred_lanes": ["python", "powershell", "json_evidence", "markdown_docs"],
        "required_validators": ["repo scan", "language lane selection", "task-specific tool admission"],
        "typical_tools": ["python", "git", "pwsh", "Mechanicus tool inventory"]
    }
]

DEFAULT_LANE_STATES = {
    "python": "LANE_READY_BASELINE",
    "powershell": "LANE_READY_BASELINE",
    "rust": "LANE_READY_BASELINE",
    "node_frontend": "LANE_READY_BASELINE",
    "css_ui": "LANE_READY_BASELINE",
    "json_evidence": "LANE_MEASURED_WITH_DEBT",
    "markdown_docs": "LANE_READY_BASELINE",
    "toml_config": "LANE_READY_BASELINE",
    "go_future": "LANE_FUTURE_CAPABILITY",
    "cpp_future": "LANE_FUTURE_CAPABILITY"
}

WEIGHTS = {
    "requirement_fit": 25,
    "availability_and_admission": 20,
    "cleanliness_validation_coverage": 20,
    "reliability_and_receipts": 15,
    "cost_and_runtime_weight": 10,
    "maintainability_no_monolith": 10,
}

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = json.loads(json.dumps(data, ensure_ascii=False, default=str))
    path.write_text(json.dumps(safe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def safe_load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {"_load_error": str(e), "_path": path.as_posix()}
    return {}

def read_task(repo: Path, task_text: Optional[str], task_file: Optional[str], patch_id: Optional[str]) -> Tuple[str, str]:
    try:
        if task_text:
            return "inline_task_text", task_text
        if task_file:
            p = repo / task_file
            return task_file, p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""
        if patch_id:
            for rel in [f"WARP/PATCHES/{patch_id}/PATCH_PACK.md", f"WARP/PATCHES/{patch_id}/TASK_PACK.md"]:
                p = repo / rel
                if p.is_file():
                    return rel, p.read_text(encoding="utf-8", errors="replace")
            return f"WARP/PATCHES/{patch_id}", ""
    except Exception as e:
        return "task_read_exception", repr(e)
    return "empty_task", ""

def lane_states_from_readout(readout: Dict[str, Any]) -> Dict[str, str]:
    states = dict(DEFAULT_LANE_STATES)
    try:
        for lane in readout.get("lanes", []) or []:
            lane_id = str(lane.get("lane_id", ""))
            state = str(lane.get("state", ""))
            if lane_id and state:
                states[lane_id] = state
    except Exception:
        pass
    return states

def classify(text: str) -> List[Dict[str, Any]]:
    lowered = " " + (text or "").lower().replace("\n", " ") + " "
    out = []
    for demand in DEMANDS:
        hits = [kw for kw in demand["keywords"] if kw.lower() in lowered]
        if hits:
            out.append({
                "demand_id": demand["demand_id"],
                "score": min(100, 20 + len(hits) * 14),
                "matched_keywords": hits,
                "preferred_lanes": demand["preferred_lanes"],
                "required_validators": demand["required_validators"],
                "typical_tools": demand["typical_tools"]
            })
    out.sort(key=lambda x: x["score"], reverse=True)
    if not out:
        out.append({
            "demand_id": "unknown_or_low_signal_task",
            "score": 25,
            "matched_keywords": [],
            "preferred_lanes": ["python", "json_evidence", "markdown_docs"],
            "required_validators": ["Owner clarification", "Mechanicus research/readout"],
            "typical_tools": ["python", "Mechanicus planner"]
        })
    return out

def score_for_demand(demand: Dict[str, Any], lane_states: Dict[str, str]) -> Dict[str, Any]:
    preferred = list(demand.get("preferred_lanes") or [])
    ready = debt = future = missing = 0
    lane_rows = []
    for lane_id in preferred:
        state = lane_states.get(lane_id, "LANE_UNKNOWN")
        lane_rows.append({"lane_id": lane_id, "state": state})
        if state == "LANE_READY_BASELINE":
            ready += 1
        elif state == "LANE_MEASURED_WITH_DEBT":
            debt += 1
        elif state == "LANE_FUTURE_CAPABILITY":
            future += 1
        else:
            missing += 1

    total = max(1, len(preferred))
    requirement_fit = min(100, int(demand.get("score", 0)) + 20)
    availability = max(0, int((ready / total) * 100) - debt * 10 - future * 20 - missing * 25)
    cleanliness = max(0, min(100, 50 + ready * 10 - debt * 12 - future * 18 - missing * 20))
    reliability = max(0, min(100, 55 + ready * 8 - debt * 10 - future * 16 - missing * 20))
    heavy = demand.get("demand_id") in {"game_engine_or_procedural_world", "tauri_app_or_cockpit", "visual_ui_polish"}
    cost = 60 if heavy else 82
    if future or missing:
        cost = max(20, cost - 20)
    maintainability = 82 if len(preferred) <= 4 else 65

    weighted = (
        requirement_fit * WEIGHTS["requirement_fit"] +
        availability * WEIGHTS["availability_and_admission"] +
        cleanliness * WEIGHTS["cleanliness_validation_coverage"] +
        reliability * WEIGHTS["reliability_and_receipts"] +
        cost * WEIGHTS["cost_and_runtime_weight"] +
        maintainability * WEIGHTS["maintainability_no_monolith"]
    ) / 100.0

    if weighted >= 85:
        verdict = "RECOMMENDED_PRIMARY_STACK"
    elif weighted >= 70:
        verdict = "ACCEPTABLE_WITH_DEBT"
    elif weighted >= 50:
        verdict = "POSSIBLE_REWORK_REQUIRED"
    else:
        verdict = "NOT_RECOMMENDED_OR_CAPABILITY_MISSING"

    return {
        "demand_id": demand.get("demand_id"),
        "score_0_to_100": round(weighted, 2),
        "verdict": verdict,
        "preferred_lanes": preferred,
        "lane_states": lane_rows,
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

def tool_ok(toolchain: Dict[str, Any], name: str) -> bool:
    try:
        for row in toolchain.get("results", []) or []:
            if row.get("name") == name:
                return bool(row.get("ok"))
    except Exception:
        pass
    return False

def inventory_has_engine(inventory: Dict[str, Any]) -> bool:
    try:
        text = " ".join((str(r.get("name", "")) + " " + str(r.get("path_or_command", ""))).lower() for r in inventory.get("records", []) or [])
        return any(x in text for x in ["godot", "bevy", "unity", "unreal", "game engine"])
    except Exception:
        return False

def gaps(text: str, classifications: List[Dict[str, Any]], toolchain: Dict[str, Any], inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    lowered = (text or "").lower()
    out = []

    if any(c.get("demand_id") == "game_engine_or_procedural_world" for c in classifications) and not inventory_has_engine(inventory):
        out.append({
            "capability_id": "GAME_ENGINE_CAPABILITY_NOT_INVENTORIED",
            "severity": "OWNER_VISIBLE_GAP",
            "meaning": "Game/procedural engine requested or implied, but no admitted engine is inventoried."
        })
    if ("go" in lowered or "golang" in lowered) and not tool_ok(toolchain, "go_version"):
        out.append({
            "capability_id": "GO_TOOLCHAIN_MISSING",
            "severity": "CAPABILITY_DEBT",
            "meaning": "Go requested or implied, but go toolchain is missing."
        })
    if any(x in lowered for x in ["c++", "cpp", "cmake"]) and not tool_ok(toolchain, "cmake_version"):
        out.append({
            "capability_id": "CPP_CMAKE_TOOLCHAIN_MISSING",
            "severity": "CAPABILITY_DEBT",
            "meaning": "C++/CMake requested or implied, but CMake/compiler capability is missing."
        })
    if any(x in lowered for x in ["strict", "build", "runtime", "cargo check", "npm build", "строг"]):
        out.append({
            "capability_id": "STRICT_BUILD_LANE_REQUIRED",
            "severity": "NEXT_VALIDATOR_REQUIRED",
            "meaning": "Task asks for strict/build/runtime confidence; a separate strict lane must run."
        })
    if any(x in lowered for x in ["reference", "fidelity", "реф", "pixel", "ui", "ux"]):
        out.append({
            "capability_id": "UI_REFERENCE_FIDELITY_TOOLING_REQUIRED_IF_TARGET_UI",
            "severity": "CONDITIONAL_GAP",
            "meaning": "UI/reference work needs dedicated fidelity proof; CSS alone cannot prove target UI."
        })
    if classifications and classifications[0].get("demand_id") == "unknown_or_low_signal_task":
        out.append({
            "capability_id": "UNKNOWN_TASK_DEMAND_LOW_SIGNAL",
            "severity": "OWNER_CLARIFICATION_OR_RESEARCH_REQUIRED",
            "meaning": "Task text did not strongly match known demand classes."
        })
    return out

def make_plan(repo: Path, task_text: Optional[str], task_file: Optional[str], patch_id: Optional[str]) -> Dict[str, Any]:
    source, text = read_task(repo, task_text, task_file, patch_id)
    readout = safe_load_json(repo / LANE_READOUT)
    toolchain = safe_load_json(repo / TOOLCHAIN)
    inventory = safe_load_json(repo / INVENTORY)

    states = lane_states_from_readout(readout)
    classifications = classify(text)
    combos = [score_for_demand(c, states) for c in classifications]
    combos.sort(key=lambda x: x["score_0_to_100"], reverse=True)
    recommended = combos[0] if combos else None

    validators: List[str] = []
    for combo in combos[:3]:
        for item in combo.get("required_validators", []):
            if item not in validators:
                validators.append(item)

    missing = gaps(text, classifications, toolchain, inventory)
    blockers = [m for m in missing if m.get("severity") in {"OWNER_VISIBLE_GAP", "OWNER_CLARIFICATION_OR_RESEARCH_REQUIRED"}]

    return {
        "tool_id": TOOL_ID,
        "generated_at_utc": utc(),
        "repo_root": str(repo),
        "task_source": source,
        "task_text_preview": (text or "")[:1200],
        "task_demand_classification": classifications,
        "candidate_combinations_with_scores": combos,
        "recommended_tool_stack": recommended,
        "recommended_language_lanes": recommended.get("preferred_lanes", []) if isinstance(recommended, dict) else [],
        "required_validators": validators,
        "missing_capabilities": missing,
        "owner_visible_blockers": blockers,
        "verdict": "PLAN_READY_WITH_CAPABILITY_GAPS" if missing else "PLAN_READY",
        "not_claimed": ["task executed", "runtime proof", "dependencies installed", "100% clean", "strict build pass"],
        "warnings": [
            "Tool composition plan is advisory and does not execute the task.",
            "Missing capabilities must remain visible until resolved or Owner-waived.",
            "Strict build/runtime validators remain separate lanes."
        ]
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--task-text", default=None)
    ap.add_argument("--task-file", default=None)
    ap.add_argument("--patch-id", default=None)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    out = repo / args.out

    try:
        plan = make_plan(repo, args.task_text, args.task_file, args.patch_id)
    except Exception as e:
        plan = {
            "tool_id": TOOL_ID,
            "generated_at_utc": utc(),
            "repo_root": str(repo),
            "verdict": "PLAN_READY_WITH_PLANNER_EXCEPTION_DEBT",
            "task_source": "planner_exception",
            "task_text_preview": "",
            "task_demand_classification": [{
                "demand_id": "planner_exception_rework",
                "score": 1,
                "matched_keywords": [],
                "preferred_lanes": ["python", "json_evidence"],
                "required_validators": ["fix planner exception"],
                "typical_tools": ["python"]
            }],
            "candidate_combinations_with_scores": [{
                "demand_id": "planner_exception_rework",
                "score_0_to_100": 1,
                "verdict": "POSSIBLE_REWORK_REQUIRED",
                "preferred_lanes": ["python", "json_evidence"],
                "lane_states": [],
                "dimensions": {},
                "required_validators": ["fix planner exception"],
                "typical_tools": ["python"]
            }],
            "recommended_tool_stack": {
                "demand_id": "planner_exception_rework",
                "score_0_to_100": 1,
                "verdict": "POSSIBLE_REWORK_REQUIRED",
                "preferred_lanes": ["python", "json_evidence"]
            },
            "recommended_language_lanes": ["python", "json_evidence"],
            "required_validators": ["fix planner exception"],
            "missing_capabilities": [{"capability_id": "PLANNER_EXCEPTION", "severity": "REWORK_REQUIRED", "meaning": repr(e)}],
            "owner_visible_blockers": [{"capability_id": "PLANNER_EXCEPTION", "severity": "REWORK_REQUIRED", "meaning": repr(e)}],
            "exception_trace_tail": traceback.format_exc()[-4000:],
            "not_claimed": ["task executed", "runtime proof", "dependencies installed", "100% clean", "strict build pass"],
            "warnings": ["Planner exception was captured and written as debt."]
        }
    write_json(out, plan)
    print(json.dumps(plan, ensure_ascii=False, indent=2, default=str))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
