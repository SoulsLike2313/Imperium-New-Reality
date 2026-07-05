#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TOOL_ID = "mechanicus_task_tool_composition_planner.v0_2_ultrasafe"

TAXONOMY = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TASK_CAPABILITY_DEMAND_TAXONOMY_V0_1.json")
SCORING = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_COMPOSITION_SCORING_MATRIX_V0_1.json")
INVENTORY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_INVENTORY_V0_1.json")
LANE_READOUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json")
TOOLCHAIN = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")
DEFAULT_OUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TASK_TOOL_COMPOSITION_PLAN_V0_1.json")

FALLBACK_TAXONOMY = {
    "demand_classes": [
        {
            "demand_id": "python_validator_or_scanner",
            "keywords": ["validator", "scan", "scanner", "census", "receipt", "report", "json", "matrix", "валидатор", "скан", "отчет", "отчёт"],
            "preferred_lanes": ["python", "json_evidence", "markdown_docs"],
            "required_validators": ["python py_compile", "json parse", "receipt shape"],
            "typical_tools": ["python", "Mechanicus inventory scanner", "language validation dispatch"]
        },
        {
            "demand_id": "warp_runner_or_windows_operator",
            "keywords": ["pwsh", "powershell", "runner", "run_", "warp", "patch pack", "таск пак", "патч пак"],
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
            "keywords": ["rust", "cargo", "compiled", "tauri backend", "strict gate", "безопасность", "строгий"],
            "preferred_lanes": ["rust", "json_evidence"],
            "required_validators": ["cargo check", "cargo fmt", "cargo clippy future"],
            "typical_tools": ["rustc", "cargo"]
        },
        {
            "demand_id": "visual_ui_polish",
            "keywords": ["css", "style", "animation", "ornament", "gothic", "metal", "fps", "visual", "reference", "готика", "орнамент", "анимация"],
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
            "keywords": ["external repo", "внешний репозиторий", "продукт", "рынок", "script", "скрипт", "repo analysis"],
            "preferred_lanes": ["python", "powershell", "json_evidence", "markdown_docs"],
            "required_validators": ["repo scan", "language lane selection", "task-specific tool admission"],
            "typical_tools": ["python", "git", "pwsh", "Mechanicus tool inventory"]
        }
    ]
}

FALLBACK_SCORING = {
    "dimensions": [
        {"id": "requirement_fit", "weight": 25},
        {"id": "availability_and_admission", "weight": 20},
        {"id": "cleanliness_validation_coverage", "weight": 20},
        {"id": "reliability_and_receipts", "weight": 15},
        {"id": "cost_and_runtime_weight", "weight": 10},
        {"id": "maintainability_no_monolith", "weight": 10}
    ],
    "verdict_bands": [
        {"min": 85, "verdict": "RECOMMENDED_PRIMARY_STACK"},
        {"min": 70, "verdict": "ACCEPTABLE_WITH_DEBT"},
        {"min": 50, "verdict": "POSSIBLE_REWORK_REQUIRED"},
        {"min": 0, "verdict": "NOT_RECOMMENDED_OR_CAPABILITY_MISSING"}
    ]
}

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def load_json(repo: Path, path: Path, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    full = repo / path
    if not full.is_file():
        data = dict(fallback or {})
        if fallback is None:
            return {}
        data["_fallback_used"] = True
        data["_missing_source"] = path.as_posix()
        return data
    try:
        return json.loads(full.read_text(encoding="utf-8-sig"))
    except Exception as e:
        data = dict(fallback or {})
        data["_fallback_used"] = fallback is not None
        data["_load_error"] = str(e)
        data["_source"] = path.as_posix()
        return data

def read_task(repo: Path, task_text: Optional[str], task_file: Optional[str], patch_id: Optional[str]) -> Tuple[str, str]:
    if task_text:
        return "inline_task_text", task_text
    if task_file:
        p = repo / task_file
        if p.is_file():
            return p.as_posix(), p.read_text(encoding="utf-8", errors="replace")
        return task_file, ""
    if patch_id:
        for rel in [f"WARP/PATCHES/{patch_id}/PATCH_PACK.md", f"WARP/PATCHES/{patch_id}/TASK_PACK.md"]:
            p = repo / rel
            if p.is_file():
                return rel, p.read_text(encoding="utf-8", errors="replace")
        return f"WARP/PATCHES/{patch_id}", ""
    return "empty_task", ""

def norm(text: str) -> str:
    return " " + re.sub(r"\s+", " ", (text or "").lower()) + " "

def classify_demands(text: str, taxonomy: Dict[str, Any]) -> List[Dict[str, Any]]:
    t = norm(text)
    out: List[Dict[str, Any]] = []
    for demand in taxonomy.get("demand_classes", []) or []:
        hits = [kw for kw in demand.get("keywords", []) if str(kw).lower() in t]
        if hits:
            out.append({
                "demand_id": demand.get("demand_id"),
                "score": min(100, 20 + len(hits) * 14),
                "matched_keywords": hits,
                "preferred_lanes": demand.get("preferred_lanes", []),
                "required_validators": demand.get("required_validators", []),
                "typical_tools": demand.get("typical_tools", [])
            })
    out.sort(key=lambda x: x["score"], reverse=True)
    return out

def lane_map(readout: Dict[str, Any]) -> Dict[str, Any]:
    return {str(l.get("lane_id")): l for l in readout.get("lanes", []) or [] if isinstance(l, dict)}

def toolchain_map(toolchain: Dict[str, Any]) -> Dict[str, Any]:
    return {str(r.get("name")): r for r in toolchain.get("results", []) or [] if isinstance(r, dict)}

def score_stack(demand: Dict[str, Any], lanes: Dict[str, Any], scoring: Dict[str, Any]) -> Dict[str, Any]:
    preferred = list(demand.get("preferred_lanes", []) or [])
    lane_states = []
    ready = debt = missing = 0
    for lane_id in preferred:
        state = (lanes.get(lane_id) or {}).get("state", "LANE_UNKNOWN")
        lane_states.append({"lane_id": lane_id, "state": state})
        if state == "LANE_READY_BASELINE":
            ready += 1
        elif state == "LANE_MEASURED_WITH_DEBT":
            debt += 1
        else:
            missing += 1

    total = max(1, len(preferred))
    requirement_fit = min(100, int(demand.get("score", 0)) + 20)
    availability = max(0, int((ready / total) * 100) - debt * 10 - missing * 18)
    cleanliness = max(0, min(100, 45 + ready * 10 - debt * 10 - missing * 16 + len(demand.get("required_validators", [])) * 5))
    reliability = max(0, min(100, 50 + ready * 8 - debt * 8 - missing * 15))
    heavy = demand.get("demand_id") in {"game_engine_or_procedural_world", "tauri_app_or_cockpit", "visual_ui_polish"}
    cost = 60 if heavy else 82
    if missing:
        cost = max(0, cost - 18)
    maintainability = 82 if len(preferred) <= 4 else 65

    weights = {str(d.get("id")): int(d.get("weight", 0)) for d in scoring.get("dimensions", []) if isinstance(d, dict)}
    weighted = (
        requirement_fit * weights.get("requirement_fit", 25) +
        availability * weights.get("availability_and_admission", 20) +
        cleanliness * weights.get("cleanliness_validation_coverage", 20) +
        reliability * weights.get("reliability_and_receipts", 15) +
        cost * weights.get("cost_and_runtime_weight", 10) +
        maintainability * weights.get("maintainability_no_monolith", 10)
    ) / 100.0

    verdict = "NOT_RECOMMENDED_OR_CAPABILITY_MISSING"
    for band in sorted(scoring.get("verdict_bands", []) or [], key=lambda b: int(b.get("min", 0)), reverse=True):
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

def missing_capabilities(text: str, classified: List[Dict[str, Any]], toolchain: Dict[str, Any], inventory: Dict[str, Any]) -> List[Dict[str, Any]]:
    t = norm(text)
    tc = toolchain_map(toolchain)
    missing = []

    if any(d.get("demand_id") == "game_engine_or_procedural_world" for d in classified):
        records = inventory.get("records", []) or []
        names = " ".join(str(r.get("name", "")).lower() + " " + str(r.get("path_or_command", "")).lower() for r in records if isinstance(r, dict))
        if not any(x in names for x in ["godot", "bevy", "unity", "unreal", "engine"]):
            missing.append({"capability_id": "GAME_ENGINE_CAPABILITY_NOT_INVENTORIED", "severity": "OWNER_VISIBLE_GAP", "meaning": "Game/procedural engine requested or implied, but no admitted engine is inventoried."})

    if ("go" in t or "golang" in t) and not tc.get("go_version", {}).get("ok"):
        missing.append({"capability_id": "GO_TOOLCHAIN_MISSING", "severity": "CAPABILITY_DEBT", "meaning": "Go requested or implied, but go toolchain is missing."})

    if any(x in t for x in ["c++", "cpp", "cmake"]) and not tc.get("cmake_version", {}).get("ok"):
        missing.append({"capability_id": "CPP_CMAKE_TOOLCHAIN_MISSING", "severity": "CAPABILITY_DEBT", "meaning": "C++/CMake requested or implied, but CMake/compiler lane is missing."})

    if any(x in t for x in ["strict", "build", "runtime", "cargo check", "npm build", "строг"]):
        missing.append({"capability_id": "STRICT_BUILD_LANE_REQUIRED", "severity": "NEXT_VALIDATOR_REQUIRED", "meaning": "Task asks for strict/build/runtime confidence; a separate strict lane must run."})

    if any(x in t for x in ["reference", "fidelity", "реф", "pixel", "ui", "ux"]):
        missing.append({"capability_id": "UI_REFERENCE_FIDELITY_TOOLING_REQUIRED_IF_TARGET_UI", "severity": "CONDITIONAL_GAP", "meaning": "UI/reference work needs dedicated fidelity proof; CSS alone cannot prove target UI."})

    if not classified:
        missing.append({"capability_id": "UNKNOWN_TASK_DEMAND", "severity": "OWNER_CLARIFICATION_OR_RESEARCH_REQUIRED", "meaning": "No demand class matched this task."})
    return missing

def make_plan(repo: Path, task_text: Optional[str], task_file: Optional[str], patch_id: Optional[str]) -> Dict[str, Any]:
    source, text = read_task(repo, task_text, task_file, patch_id)
    taxonomy = load_json(repo, TAXONOMY, FALLBACK_TAXONOMY)
    scoring = load_json(repo, SCORING, FALLBACK_SCORING)
    inventory = load_json(repo, INVENTORY, {})
    readout = load_json(repo, LANE_READOUT, {})
    toolchain = load_json(repo, TOOLCHAIN, {})

    classified = classify_demands(text, taxonomy)
    lanes = lane_map(readout)
    combos = [score_stack(d, lanes, scoring) for d in classified]
    combos.sort(key=lambda x: x["score_0_to_100"], reverse=True)
    recommended = combos[0] if combos else None

    validators = []
    for c in combos[:3]:
        for v in c.get("required_validators", []):
            if v not in validators:
                validators.append(v)

    missing = missing_capabilities(text, classified, toolchain, inventory)
    blockers = [m for m in missing if m.get("severity") in {"OWNER_VISIBLE_GAP", "OWNER_CLARIFICATION_OR_RESEARCH_REQUIRED"}]

    return {
        "tool_id": TOOL_ID,
        "generated_at_utc": utc(),
        "repo_root": str(repo),
        "task_source": source,
        "task_text_preview": (text or "")[:1200],
        "task_demand_classification": classified,
        "candidate_combinations_with_scores": combos,
        "recommended_tool_stack": recommended,
        "recommended_language_lanes": recommended.get("preferred_lanes", []) if recommended else [],
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
            "verdict": "PLAN_WRITTEN_WITH_PLANNER_EXCEPTION_DEBT",
            "task_demand_classification": [],
            "candidate_combinations_with_scores": [],
            "recommended_tool_stack": None,
            "recommended_language_lanes": [],
            "required_validators": [],
            "missing_capabilities": [{"capability_id": "PLANNER_EXCEPTION", "severity": "REWORK_REQUIRED", "meaning": repr(e)}],
            "owner_visible_blockers": [{"capability_id": "PLANNER_EXCEPTION", "severity": "REWORK_REQUIRED", "meaning": repr(e)}],
            "exception_trace_tail": traceback.format_exc()[-4000:],
            "not_claimed": ["task executed", "runtime proof", "dependencies installed", "100% clean", "strict build pass"],
            "warnings": ["Planner exception recorded as debt; plan file was still written."]
        }
    write_json(out, plan)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
