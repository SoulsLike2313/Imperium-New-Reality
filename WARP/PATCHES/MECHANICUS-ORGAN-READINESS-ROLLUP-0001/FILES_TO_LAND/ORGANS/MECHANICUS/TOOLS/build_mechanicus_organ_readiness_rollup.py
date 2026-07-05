#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "MECHANICUS-ORGAN-READINESS-ROLLUP-0001"
TOOL_ID = "mechanicus_organ_readiness_rollup_builder.v0_1"

ASSEMBLY_TARGET = Path("ORGANS/MECHANICUS/ASSEMBLY/ORGAN_ASSEMBLY_TARGET_V0_1.json")
PASSPORT = Path("ORGANS/MECHANICUS/PASSPORT/MECHANICUS_ORGAN_PASSPORT_V0_1.json")
FUNCTIONS = Path("ORGANS/MECHANICUS/FUNCTIONS.md")
MANIFEST = Path("ORGANS/MECHANICUS/MANIFEST.json")
LAW = Path("ORGANS/MECHANICUS/LAWS/MECHANICUS_ORGAN_READINESS_ROLLUP_LAW_V0_1.json")
MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_ORGAN_READINESS_ROLLUP_MATRIX_V0_1.json")
ROLLUP_JSON = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_V0_1.json")
ROLLUP_MD = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_V0_1.md")

BASELINE_CAPABILITY_RULES = [
    {
        "capability_id": "language_census_and_language_power_registry",
        "meaning": "Mechanicus can measure language surface and classify language roles.",
        "evidence": [
            "ORGANS/MECHANICUS/LAWS/MECHANICUS_LANGUAGE_CENSUS_AND_CODE_PURITY_LAW_V0_1.json",
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_LANGUAGE_POWER_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_LANGUAGE_SURFACE_V2_CLASSIFICATION_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_primary_organ_passport_and_language_census_receipt.json"
        ],
        "claim_boundary": "language census is evidence, not full code purity"
    },
    {
        "capability_id": "strict_language_lane_baseline",
        "meaning": "Mechanicus has baseline strict lanes for primary repo languages/formats.",
        "evidence": [
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_STRICT_LANGUAGE_LANE_REGISTRY_V0_1.json",
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_STRICT_LANGUAGE_LANE_BASELINE_EXPANSION_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_language_lane_baseline_expansion_receipt.json"
        ],
        "claim_boundary": "baseline lanes do not mean every language is lint/type/test clean"
    },
    {
        "capability_id": "json_evidence_strict_lane",
        "meaning": "Mechanicus can parse and classify JSON/JSONL evidence debt.",
        "evidence": [
            "ORGANS/MECHANICUS/LAWS/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_LAW_V0_1.json",
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_JSON_EVIDENCE_STRICT_LANE_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_json_evidence_strict_lane_receipt.json"
        ],
        "claim_boundary": "canonical parse cleanliness is not semantic correctness of every claim"
    },
    {
        "capability_id": "strict_build_lane_foundation",
        "meaning": "Mechanicus can run a foundation build lane across Python, PowerShell, Node frontend and Rust/Tauri checks on a prepared host.",
        "evidence": [
            "ORGANS/MECHANICUS/LAWS/MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_LAW_V0_1.json",
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_STRICT_BUILD_LANE_FOUNDATION_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_build_lane_foundation_receipt.json",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_build_lane_runner_exit_code_fix_v2_receipt.json"
        ],
        "claim_boundary": "build proof is host/profile-bound unless clean bootstrap proof exists"
    },
    {
        "capability_id": "tool_accumulation_and_admission_baseline",
        "meaning": "Mechanicus can inventory tools/candidates and declare admission/rework categories.",
        "evidence": [
            "ORGANS/MECHANICUS/LAWS/MECHANICUS_TOOL_ACCUMULATION_AND_ADMISSION_LAW_V0_1.json",
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_ADMISSION_GATE_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/TOOLS/scan_mechanicus_tool_inventory.py",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_tool_accumulation_and_admission_gate_receipt.json"
        ],
        "claim_boundary": "tool inventory is not full tool admission v2"
    },
    {
        "capability_id": "task_tool_composition_planner",
        "meaning": "Mechanicus can propose tool stacks, demand classes and gaps for tasks.",
        "evidence": [
            "ORGANS/MECHANICUS/LAWS/MECHANICUS_TASK_TOOL_COMPOSITION_PLANNER_LAW_V0_1.json",
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_COMPOSITION_SCORING_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_task_tool_composition_planner_receipt.json",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_task_tool_composition_planner_ultrasafe_hotfix_v2_receipt.json"
        ],
        "claim_boundary": "planner recommendation is advisory/scored, not execution authority"
    },
    {
        "capability_id": "ui_workshop_no_monolith_baseline",
        "meaning": "Mechanicus can declare UI workshop rules and detect monolith risk zones.",
        "evidence": [
            "ORGANS/MECHANICUS/LAWS/MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW_V0_1.json",
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_NO_MONOLITH_ARCHITECTURE_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/RECEIPTS/mechanicus_ui_workshop_and_no_monolith_law_receipt.json"
        ],
        "claim_boundary": "UI workshop law is not AAA visual acceptance or reference fidelity proof"
    },
    {
        "capability_id": "patch_pack_technical_preflight",
        "meaning": "Mechanicus can participate in patch pack technical preflight and file-to-land discipline.",
        "evidence": [
            "ORGANS/MECHANICUS/MATRICES/MECHANICUS_PATCH_PACK_TECHNICAL_PREFLIGHT_MATRIX_V0_1.json",
            "ORGANS/MECHANICUS/RECEIPTS/patch_pack_technical_preflight_receipt.json"
        ],
        "claim_boundary": "preflight support is not final land authority"
    },
    {
        "capability_id": "ide_warp_metaos_bridges_candidate",
        "meaning": "Mechanicus has bridge adapters toward IDE, WARP and MetaOS surfaces.",
        "evidence": [
            "ORGANS/MECHANICUS/IDE_BRIDGE/mechanicus_ide_bridge.py",
            "ORGANS/MECHANICUS/IDE_BRIDGE/warp_bridge_adapter.py",
            "ORGANS/MECHANICUS/IDE_BRIDGE/metaos_bridge_adapter.py",
            "ORGANS/MECHANICUS/IDE_BRIDGE/workbench_bridge_adapter.py"
        ],
        "claim_boundary": "bridge files are candidate infrastructure, not full operating system control"
    },
    {
        "capability_id": "evidence_vault_candidate",
        "meaning": "Mechanicus has evidence vault packager/sealer/batch executor candidates.",
        "evidence": [
            "ORGANS/MECHANICUS/EVIDENCE_VAULT/evidence_vault_packager_v0_1.py",
            "ORGANS/MECHANICUS/EVIDENCE_VAULT/evidence_vault_sealer_v0_1.py",
            "ORGANS/MECHANICUS/EVIDENCE_VAULT/evidence_vault_batch_pack_executor_v0_1.py"
        ],
        "claim_boundary": "evidence vault candidate is not full Administratum supersession ledger"
    }
]

NEXT_PATCH_QUEUE = [
    {"patch_id": "MECHANICUS-TOOL-ADMISSION-V2-0001", "priority": 10, "reason": "inventory must become admitted/risk-scored/passported tool reality"},
    {"patch_id": "MECHANICUS-DEPENDENCY-INVENTORY-0001", "priority": 20, "reason": "Mechanicus must know libraries, CLIs, modules and host dependencies"},
    {"patch_id": "MECHANICUS-CODE-CLEANLINESS-LANES-0001", "priority": 30, "reason": "build proof must be separated from lint/type/test/security proof"},
    {"patch_id": "MECHANICUS-TUI-LAUNCHER-0001", "priority": 40, "reason": "organ needs terminal-first launcher presence"},
    {"patch_id": "MECHANICUS-PERSONAL-VALIDATORS-0001", "priority": 50, "reason": "organ needs self flow/integrity validators"},
    {"patch_id": "CUSTODES-MECHANICUS-AUDIT-0001", "priority": 60, "reason": "Custodes must prosecute Mechanicus claims and validator honesty"},
    {"patch_id": "THRONE-MECHANICUS-CROWN-VERDICT-0001", "priority": 70, "reason": "Throne must crown or block Mechanicus assembly from current evidence"}
]

DEFERRED_FUTURE_CAPABILITIES = [
    {"capability_id": "local_model_membrane", "status": "DEFERRED_AFTER_CORE_V1", "meaning": "small local model may later translate Owner intent and explain routing/cost, but is not required for this patch or Core v1 validators"},
    {"capability_id": "safe_real_execution_gateway", "status": "FUTURE_AFTER_ADMISSION_AND_SANDBOX", "meaning": "real execution can exist only after tool admission v2, sandbox profile and receipts"},
    {"capability_id": "game_or_procedural_engine_inventory", "status": "FUTURE_GAP", "meaning": "game/procedural runtime capability must be inventoried before visual/simulation claims"},
    {"capability_id": "ui_reference_fidelity_gate", "status": "FUTURE_CONDITIONAL_GAP", "meaning": "visual work requires reference fidelity, screenshot/runtime/performance proof"}
]


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as exc:
        return None, str(exc)


def rel(path: Path) -> str:
    return path.as_posix()


def exists(repo: Path, p: str | Path) -> bool:
    return (repo / p).exists()


def count_files(repo: Path, base: str, pattern: str = "*") -> int:
    root = repo / base
    if not root.exists():
        return 0
    return sum(1 for p in root.rglob(pattern) if p.is_file() and "__pycache__" not in p.parts)


def capability_state(repo: Path, rule: Dict[str, Any]) -> Dict[str, Any]:
    evidence = rule["evidence"]
    present = [p for p in evidence if exists(repo, p)]
    missing = [p for p in evidence if not exists(repo, p)]
    ratio = round(len(present) / len(evidence), 3) if evidence else 0
    if ratio == 1:
        state = "PROVEN_BASELINE_OR_PRESENT_CANDIDATE"
    elif ratio >= 0.5:
        state = "PARTIAL_EVIDENCE_PRESENT"
    else:
        state = "NOT_PROVEN_OR_MISSING"
    return {
        "capability_id": rule["capability_id"],
        "state": state,
        "present_evidence": present,
        "missing_evidence": missing,
        "evidence_ratio": ratio,
        "meaning": rule["meaning"],
        "claim_boundary": rule["claim_boundary"]
    }


def map_assembly_gates(repo: Path, assembly_target: Dict[str, Any]) -> List[Dict[str, Any]]:
    gates = assembly_target.get("assembly_gates", {}) if isinstance(assembly_target, dict) else {}
    mapped: List[Dict[str, Any]] = []
    for gate_id, gate in gates.items():
        required = gate.get("required", True) if isinstance(gate, dict) else True
        proof_state = gate.get("proof_state", "UNKNOWN") if isinstance(gate, dict) else "UNKNOWN"
        evidence_paths = gate.get("evidence_paths", []) if isinstance(gate, dict) else []
        required_evidence = gate.get("required_evidence", []) if isinstance(gate, dict) else []
        present_evidence = [p for p in evidence_paths if exists(repo, p)]
        # The rollup is allowed to see nearby files but must not upgrade official proof state.
        nearby_counts = {}
        if gate_id == "organ_tools_docs_functions":
            nearby_counts = {
                "functions_md_exists": exists(repo, FUNCTIONS),
                "tool_files": count_files(repo, "ORGANS/MECHANICUS/TOOLS", "*.py"),
                "validator_files": count_files(repo, "ORGANS/MECHANICUS/VALIDATORS", "*.py"),
                "law_files": count_files(repo, "ORGANS/MECHANICUS/LAWS", "*.json"),
                "matrix_files": count_files(repo, "ORGANS/MECHANICUS/MATRICES", "*.json")
            }
        mapped.append({
            "gate_id": gate_id,
            "required": required,
            "official_assembly_proof_state": proof_state,
            "rollup_measured_state": "OFFICIAL_NOT_PROVEN" if proof_state == "NOT_PROVEN" else proof_state,
            "evidence_paths_declared": evidence_paths,
            "present_declared_evidence": present_evidence,
            "required_evidence": required_evidence,
            "nearby_non_closing_evidence": nearby_counts,
            "may_raise_assembled_claim": False
        })
    return mapped


def build_rollup(repo: Path) -> Dict[str, Any]:
    assembly_target, assembly_err = load_json(repo / ASSEMBLY_TARGET)
    passport, passport_err = load_json(repo / PASSPORT)
    law, law_err = load_json(repo / LAW)
    matrix, matrix_err = load_json(repo / MATRIX)
    capabilities = [capability_state(repo, r) for r in BASELINE_CAPABILITY_RULES]
    assembly_gate_map = map_assembly_gates(repo, assembly_target if isinstance(assembly_target, dict) else {})
    unproven_gates = [g["gate_id"] for g in assembly_gate_map if g.get("official_assembly_proof_state") != "PROVEN"]

    forbidden_claims = []
    if isinstance(assembly_target, dict):
        forbidden_claims = assembly_target.get("must_not_claim", [])
    if not forbidden_claims:
        forbidden_claims = [
            "organ_assembled", "operational_proven", "trust_proven", "throne_confirmed", "red_blue_resilient", "no_core_mutation_proven"
        ]

    blockers = []
    for gate_id in unproven_gates:
        blockers.append({"blocker_id": f"assembly_gate_unproven::{gate_id}", "severity": "BLOCKS_ORGAN_ASSEMBLED_CLAIM"})
    blockers.extend([
        {"blocker_id": "tool_admission_v2_not_done", "severity": "BLOCKS_FULL_TOOL_TRUST"},
        {"blocker_id": "dependency_inventory_not_done", "severity": "BLOCKS_REPRODUCIBILITY_TRUTH"},
        {"blocker_id": "code_cleanliness_lanes_not_done", "severity": "BLOCKS_100_PERCENT_CODE_CLEANLINESS_CLAIM"},
        {"blocker_id": "custodes_mechanicus_audit_not_done", "severity": "BLOCKS_TRUST_PROVEN_CLAIM"},
        {"blocker_id": "throne_mechanicus_crown_verdict_not_done", "severity": "BLOCKS_CROWN_CONFIRMED_CLAIM"}
    ])

    source_counts = {
        "mechanicus_tools_py": count_files(repo, "ORGANS/MECHANICUS/TOOLS", "*.py"),
        "mechanicus_validators_py": count_files(repo, "ORGANS/MECHANICUS/VALIDATORS", "*.py"),
        "mechanicus_laws_json": count_files(repo, "ORGANS/MECHANICUS/LAWS", "*.json"),
        "mechanicus_matrices_json": count_files(repo, "ORGANS/MECHANICUS/MATRICES", "*.json"),
        "mechanicus_receipts_json": count_files(repo, "ORGANS/MECHANICUS/RECEIPTS", "*.json"),
        "mechanicus_reports_files": count_files(repo, "ORGANS/MECHANICUS/REPORTS", "*")
    }

    return {
        "rollup_id": "mechanicus.organ_readiness_rollup.v0_1",
        "task_id": TASK_ID,
        "tool_id": TOOL_ID,
        "generated_at_utc": utc(),
        "status": "MEASURED_NOT_ASSEMBLED",
        "verdict": "PASS_ROLLUP_CREATED_MECHANICUS_NOT_ASSEMBLED",
        "repo_context": {
            "repo_root": str(repo),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "script_first": True,
            "llm_required_for_this_patch": False
        },
        "organ_identity": {
            "organ_id": "MECHANICUS",
            "passport_path": rel(PASSPORT),
            "passport_load_error": passport_err,
            "status_from_passport": passport.get("status") if isinstance(passport, dict) else None,
            "identity_is": passport.get("identity", {}).get("is", []) if isinstance(passport, dict) else [],
            "identity_is_not": passport.get("identity", {}).get("is_not", []) if isinstance(passport, dict) else [],
            "core_laws_from_passport": passport.get("core_laws", []) if isinstance(passport, dict) else []
        },
        "source_files": {
            "assembly_target": {"path": rel(ASSEMBLY_TARGET), "load_error": assembly_err},
            "passport": {"path": rel(PASSPORT), "load_error": passport_err},
            "functions": {"path": rel(FUNCTIONS), "exists": exists(repo, FUNCTIONS)},
            "manifest": {"path": rel(MANIFEST), "exists": exists(repo, MANIFEST)},
            "rollup_law": {"path": rel(LAW), "load_error": law_err},
            "rollup_matrix": {"path": rel(MATRIX), "load_error": matrix_err}
        },
        "source_counts": source_counts,
        "proven_baseline_capabilities": [c for c in capabilities if c["state"] == "PROVEN_BASELINE_OR_PRESENT_CANDIDATE"],
        "partial_or_candidate_capabilities": [c for c in capabilities if c["state"] != "PROVEN_BASELINE_OR_PRESENT_CANDIDATE"],
        "assembly_gate_map": assembly_gate_map,
        "organ_assembled_claim_allowed": False,
        "mechanicus_assembled": False,
        "forbidden_claims": forbidden_claims,
        "current_blockers": blockers,
        "next_patch_queue": NEXT_PATCH_QUEUE,
        "deferred_future_capabilities": DEFERRED_FUTURE_CAPABILITIES,
        "local_model_membrane_hook": {
            "status": "DEFERRED_AFTER_CORE_V1",
            "near_term_dependency": False,
            "core_v1_dependency": False,
            "purpose_later": "Translate Owner intent into IntentEnvelope and explain capability/risk/cost using script-generated reports.",
            "authority_later": "No PASS, no land, no arbitrary shell, no WARP bypass, no Owner override.",
            "machine_interface_candidate": "IntentEnvelope.json after Mechanicus/Strategium/Throne readiness gates exist"
        },
        "no_fake_green_guard": {
            "build_proof_is_not_code_purity": True,
            "tool_inventory_is_not_tool_admission_v2": True,
            "planner_is_not_execution_authority": True,
            "rollup_is_not_crown_verdict": True,
            "local_model_is_not_inner_authority": True
        }
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_md(rollup: Dict[str, Any]) -> str:
    caps = rollup.get("proven_baseline_capabilities", [])
    partial = rollup.get("partial_or_candidate_capabilities", [])
    gates = rollup.get("assembly_gate_map", [])
    blockers = rollup.get("current_blockers", [])
    queue = rollup.get("next_patch_queue", [])
    future = rollup.get("deferred_future_capabilities", [])

    def bullets(items, key="capability_id"):
        if not items:
            return "- none"
        return "\n".join(f"- `{i.get(key, i)}` — {i.get('meaning', i.get('reason', i.get('severity', '')))}" for i in items)

    gate_lines = []
    for g in gates:
        gate_lines.append(f"- `{g['gate_id']}` — official: `{g['official_assembly_proof_state']}`, rollup: `{g['rollup_measured_state']}`")
    gates_md = "\n".join(gate_lines) if gate_lines else "- none"
    q_md = "\n".join(f"- {q['priority']}. `{q['patch_id']}` — {q['reason']}" for q in queue) if queue else "- none"
    blockers_md = "\n".join(f"- `{b['blocker_id']}` — `{b['severity']}`" for b in blockers) if blockers else "- none"
    future_md = "\n".join(f"- `{f['capability_id']}` — `{f['status']}` — {f['meaning']}" for f in future) if future else "- none"
    counts_md = "\n".join(f"- `{k}`: `{v}`" for k, v in rollup.get("source_counts", {}).items())

    return f"""# MECHANICUS ORGAN READINESS ROLLUP V0.1

task_id: `{rollup['task_id']}`  
tool_id: `{rollup['tool_id']}`  
verdict: `{rollup['verdict']}`  
status: `{rollup['status']}`  
generated_at_utc: `{rollup['generated_at_utc']}`

## Meaning

This rollup is a current truth index for Mechanicus. It does **not** assemble the organ, does **not** crown it, and does **not** claim Core v1 readiness.

## Script-first boundary

- LLM required for this patch: `{rollup['repo_context']['llm_required_for_this_patch']}`
- Script-first foundation: `{rollup['repo_context']['script_first']}`
- Local model membrane: `DEFERRED_AFTER_CORE_V1`, not a current dependency.

## Source counts

{counts_md}

## Proven baseline / present candidate capabilities

{bullets(caps)}

## Partial or candidate capabilities

{bullets(partial)}

## Assembly gate map

{gates_md}

## Current blockers

{blockers_md}

## Forbidden claims

{chr(10).join('- `' + c + '`' for c in rollup.get('forbidden_claims', []))}

## Next patch queue

{q_md}

## Deferred future capabilities

{future_md}

## Local model membrane hook

The local model is recorded only as a future membrane. It may later translate Owner intent, explain capability/risk/cost, and route work to scripts, CLI Codex, Grok, cloud chat agents or Owner review. It must not set PASS, land patches, run arbitrary shell, bypass WARP, or override Owner authority.

## No fake-green guard

- Build proof is not code purity: `{rollup['no_fake_green_guard']['build_proof_is_not_code_purity']}`
- Tool inventory is not admission v2: `{rollup['no_fake_green_guard']['tool_inventory_is_not_tool_admission_v2']}`
- Planner is not execution authority: `{rollup['no_fake_green_guard']['planner_is_not_execution_authority']}`
- Rollup is not Crown verdict: `{rollup['no_fake_green_guard']['rollup_is_not_crown_verdict']}`
- Local model is not inner authority: `{rollup['no_fake_green_guard']['local_model_is_not_inner_authority']}`
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out-json", default=ROLLUP_JSON.as_posix())
    ap.add_argument("--out-md", default=ROLLUP_MD.as_posix())
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    rollup = build_rollup(repo)
    write_json(repo / args.out_json, rollup)
    md_path = repo / args.out_md
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_md(rollup), encoding="utf-8")
    print(json.dumps({
        "task_id": TASK_ID,
        "tool_id": TOOL_ID,
        "verdict": rollup["verdict"],
        "rollup_json": args.out_json,
        "rollup_md": args.out_md,
        "mechanicus_assembled": rollup["mechanicus_assembled"],
        "local_model_membrane": rollup["local_model_membrane_hook"]["status"]
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
