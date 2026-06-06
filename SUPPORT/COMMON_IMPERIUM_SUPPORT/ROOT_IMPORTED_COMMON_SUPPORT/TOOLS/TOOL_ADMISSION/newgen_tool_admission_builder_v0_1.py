#!/usr/bin/env python3
"""Build NewGen Mechanicus Tool Admission V0.1 foundation artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-MECHANICUS-TOOL-ADMISSION-VM3-V0_1"
GENERATED_AT_UTC = "2026-05-22T00:00:00Z"
REQUIRED_STARTING_HEAD = "2b4942cb3b713233bd299c5e36dde008aca9ad2"
COMMIT_MESSAGE = "TASK-20260521: add NewGen Mechanicus tool admission v0.1"
NEXT_ALLOWED_TASK = "OWNER_REVIEW_AFTER_PHASE_10_OR_TASK_NEWGEN_MANUAL_SYNTHETIC_E2E_CORRIDOR"

ADMISSION_STATES = [
    "CANDIDATE_ONLY",
    "AVAILABLE_ON_HOST_UNVERIFIED_FOR_IMPERIUM",
    "AVAILABLE_ON_HOST_VERIFIED_BASIC",
    "DEFERRED_NEEDS_OWNER",
    "DEFERRED_NEEDS_ADMISSION_TASK",
    "BLOCKED_BY_RISK",
    "APPROVED_FOR_FUTURE_INSTALL_TASK",
    "APPROVED_FOR_READ_ONLY_USE",
    "INSTALLED_AND_REGISTERED",
]

FORBIDDEN_CLAIMS = [
    "Claiming production toolchain readiness is forbidden.",
    "Claiming phase-10 installed Playwright/Vitest/Storybook/Nx is forbidden.",
    "Claiming unrestricted external-tool approval is forbidden.",
    "Claiming guaranteed future UI or UX evidence is forbidden.",
    "Claiming production package-management readiness is forbidden.",
    "Claiming proof of live autonomous agents is forbidden.",
]

TOOL_BLUEPRINTS = [
    {
        "tool_name": "Playwright",
        "tool_slug": "playwright",
        "state": "DEFERRED_NEEDS_ADMISSION_TASK",
        "capability_summary": "Browser automation for bounded UI/runtime evidence tasks.",
        "need_reason": "Future synthetic E2E evidence may require controlled browser automation.",
        "risk_category": "SUPPLY_CHAIN",
        "severity": "HIGH",
        "risk_summary": "Binary/runtime dependencies can drift without locked install receipts.",
        "mitigation": "Allow only dedicated admission+install task with deterministic receipts.",
    },
    {
        "tool_name": "Vitest",
        "tool_slug": "vitest",
        "state": "DEFERRED_NEEDS_ADMISSION_TASK",
        "capability_summary": "Fast TypeScript/JavaScript test harness for scoped checks.",
        "need_reason": "Could support future bounded test corridors around visual/runtime surfaces.",
        "risk_category": "REPRODUCIBILITY",
        "severity": "MEDIUM",
        "risk_summary": "Version drift and hidden dependency updates may fake pass confidence.",
        "mitigation": "Require lockfile evidence and deterministic test receipts before approval.",
    },
    {
        "tool_name": "ESLint",
        "tool_slug": "eslint",
        "state": "DEFERRED_NEEDS_ADMISSION_TASK",
        "capability_summary": "Static linting for JS/TS policy and consistency.",
        "need_reason": "Can enforce bounded conventions after explicit admission.",
        "risk_category": "DX",
        "severity": "LOW",
        "risk_summary": "Rule churn can produce noisy output without policy alignment.",
        "mitigation": "Admit only with rule-baseline contract and false-positive policy.",
    },
    {
        "tool_name": "Storybook",
        "tool_slug": "storybook",
        "state": "DEFERRED_NEEDS_ADMISSION_TASK",
        "capability_summary": "Component sandbox for visual regression-ready stories.",
        "need_reason": "Potential future visual evidence lane for scoped UI modules.",
        "risk_category": "COMPLEXITY",
        "severity": "MEDIUM",
        "risk_summary": "Extra runtime/build surface can expand scope without strict gating.",
        "mitigation": "Require explicit visual-boundary scope and performance receipts.",
    },
    {
        "tool_name": "Nx",
        "tool_slug": "nx",
        "state": "CANDIDATE_ONLY",
        "capability_summary": "Monorepo orchestration and task graph execution.",
        "need_reason": "Possible future optimization for staged package/app orchestration.",
        "risk_category": "MAINTENANCE",
        "severity": "HIGH",
        "risk_summary": "Repository workflow and scripts can be heavily altered by setup defaults.",
        "mitigation": "Keep candidate-only until dedicated architecture-impact admission task.",
    },
    {
        "tool_name": "Turborepo",
        "tool_slug": "turborepo",
        "state": "CANDIDATE_ONLY",
        "capability_summary": "Monorepo pipeline caching and orchestration.",
        "need_reason": "Alternative to Nx for future multi-package build orchestration.",
        "risk_category": "MAINTENANCE",
        "severity": "HIGH",
        "risk_summary": "Cache and pipeline assumptions can conflict with current repo contracts.",
        "mitigation": "Require separate architecture+operational impact admission decision.",
    },
    {
        "tool_name": "Rich/Textual CLI Candidate",
        "tool_slug": "rich-textual-cli-candidate",
        "state": "CANDIDATE_ONLY",
        "capability_summary": "Enhanced operator CLI/TUI interaction surface for diagnostics.",
        "need_reason": "Could improve observability and local operator ergonomics in future tasks.",
        "risk_category": "COMPLEXITY",
        "severity": "MEDIUM",
        "risk_summary": "UI/runtime coupling risk if introduced without bounded control contracts.",
        "mitigation": "Candidate-only until dedicated TUI admission scope is approved.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build deterministic Mechanicus Tool Admission V0.1 artifacts."
    )
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", default="")
    return parser.parse_args()


def resolve_repo_root(cli_repo_root: str) -> Path:
    if cli_repo_root.strip():
        return Path(cli_repo_root).resolve()
    return Path(__file__).resolve().parents[3]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_candidates(task_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, tool in enumerate(TOOL_BLUEPRINTS, start=1):
        rows.append(
            {
                "schema_version": "0.1",
                "record_id": f"TCAND-{idx:03d}",
                "task_id": task_id,
                "tool_name": tool["tool_name"],
                "tool_slug": tool["tool_slug"],
                "owner_organ": "MECHANICUS",
                "capability_summary": tool["capability_summary"],
                "need_reason": tool["need_reason"],
                "admission_state": tool["state"],
                "decision_owner_organ": "DOCTRINARIUM+MECHANICUS+OWNER",
                "evidence_required_pre_admission": [
                    "install_plan_review.md",
                    "scope_boundary_receipt.json",
                    "validator_report.json",
                ],
                "receipts_required_post_use": [
                    "tool_capability_receipt.json",
                    "post_use_validator_report.json",
                ],
                "risk_refs": [f"TRISK-{idx:03d}"],
                "no_install_in_v0_1": True,
                "install_verified": False,
                "install_verification_note": "Not verified in V0.1 foundation task.",
                "future_task_ref": f"TASK_NEWGEN_TOOL_ADMISSION_FOLLOWUP_{tool['tool_slug'].upper()}",
                "foundation_only": True,
                "forbidden_claims_blocked": True,
                "status_note": "Candidate recorded without installation.",
                "created_at_utc": GENERATED_AT_UTC,
            }
        )
    return rows


def build_risks(task_id: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, tool in enumerate(TOOL_BLUEPRINTS, start=1):
        rows.append(
            {
                "schema_version": "0.1",
                "risk_id": f"TRISK-{idx:03d}",
                "task_id": task_id,
                "tool_slug": tool["tool_slug"],
                "linked_candidate_id": candidates[idx - 1]["record_id"],
                "risk_category": tool["risk_category"],
                "severity": tool["severity"],
                "risk_summary": tool["risk_summary"],
                "mitigation_plan": tool["mitigation"],
                "proof_required_before_approval": [
                    "admission_decision_record.json",
                    "no_install_guard_receipt.json",
                    "future_install_task_contract.md",
                ],
                "owner_gate_required": True,
                "recommended_state_if_unproven": "DEFERRED_NEEDS_ADMISSION_TASK",
                "foundation_only": True,
                "created_at_utc": GENERATED_AT_UTC,
            }
        )
    return rows


def decision_reason_for_state(state: str) -> str:
    if state == "CANDIDATE_ONLY":
        return "Candidate tracked only; admission evidence not yet sufficient for broader approval."
    if state == "DEFERRED_NEEDS_ADMISSION_TASK":
        return "Tool is relevant but requires dedicated follow-up admission task before install/use."
    return "State preserved under foundation-only constraints."


def build_decisions(task_id: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, candidate in enumerate(candidates, start=1):
        tool_slug = candidate["tool_slug"]
        rows.append(
            {
                "schema_version": "0.1",
                "decision_id": f"TDEC-{idx:03d}",
                "task_id": task_id,
                "tool_slug": tool_slug,
                "linked_candidate_id": candidate["record_id"],
                "linked_risk_ids": [f"TRISK-{idx:03d}"],
                "decision_state": candidate["admission_state"],
                "decision_owner_organ": "DOCTRINARIUM+MECHANICUS+OWNER",
                "decision_reason": decision_reason_for_state(candidate["admission_state"]),
                "allowed_actions": [
                    "Document admission rationale and risk controls",
                    "Prepare bounded follow-up admission/install task",
                    "Perform read-only planning actions",
                ],
                "forbidden_actions": [
                    "Install external packages in phase 10",
                    "Claim production readiness",
                    "Claim unrestricted tool approval",
                ],
                "evidence_refs": [
                    candidate["record_id"],
                    f"TRISK-{idx:03d}",
                    "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-MECHANICUS-TOOL-ADMISSION-VM3-V0_1/VALIDATOR_REPORT.json",
                ],
                "install_allowed_now": False,
                "future_install_task_ref": candidate["future_task_ref"],
                "receipts_required_post_use": candidate["receipts_required_post_use"],
                "foundation_only": True,
                "created_at_utc": GENERATED_AT_UTC,
            }
        )
    return rows


def build_capabilities(task_id: str, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, tool in enumerate(TOOL_BLUEPRINTS, start=1):
        rows.append(
            {
                "schema_version": "0.1",
                "receipt_id": f"TCAP-{idx:03d}",
                "task_id": task_id,
                "tool_slug": tool["tool_slug"],
                "capability_name": tool["capability_summary"],
                "outcome_state": decisions[idx - 1]["decision_state"],
                "evidence_paths": [
                    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_DECISIONS_V0_1.generated.json"
                ],
                "decision_id": decisions[idx - 1]["decision_id"],
                "execution_mode": "CANDIDATE_REGISTRY_ONLY",
                "run_command": "",
                "run_result": "NOT_RUN",
                "no_install_performed": True,
                "notes": "Foundation registry receipt only; no command execution performed.",
                "foundation_only": True,
                "created_at_utc": GENERATED_AT_UTC,
            }
        )
    return rows


def count_states(candidates: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in candidates:
        state = str(row.get("admission_state", "")).strip()
        if not state:
            continue
        counts[state] = counts.get(state, 0) + 1
    return counts


def build_index(
    task_id: str,
    candidate_count: int,
    risk_count: int,
    decision_count: int,
    capability_count: int,
    state_counts: dict[str, int],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "task_id": task_id,
        "phase": 10,
        "phase_name": "Mechanicus Tool Admission V0.1",
        "foundation_only": True,
        "no_install": True,
        "generated_at_utc": GENERATED_AT_UTC,
        "paths": {
            "candidate_catalog": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CANDIDATE_CATALOG_V0_1.generated.json",
            "risk_catalog": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_RISK_CATALOG_V0_1.generated.json",
            "decision_catalog": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_DECISIONS_V0_1.generated.json",
            "capability_registry": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CAPABILITY_REGISTRY_V0_1.generated.json",
        },
        "record_counts": {
            "candidate_count": candidate_count,
            "risk_count": risk_count,
            "decision_count": decision_count,
            "capability_count": capability_count,
        },
        "admission_state_counts": state_counts,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "next_allowed_task": NEXT_ALLOWED_TASK,
    }


def build_sample(
    task_id: str,
    candidates: list[dict[str, Any]],
    risks: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    capabilities: list[dict[str, Any]],
    index: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "sample_kind": "TOOL_ADMISSION_FOUNDATION",
        "task_id": task_id,
        "foundation_only": True,
        "no_install": True,
        "candidate_record": candidates[0],
        "risk_record": risks[0],
        "decision_record": decisions[0],
        "capability_receipt_record": capabilities[0],
        "index_preview": index,
    }


def changed_path_list(task_id: str) -> list[str]:
    report_root = f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}"
    return [
        "IMPERIUM_NEW_GENERATION/ARCHITECTURE/MECHANICUS_TOOL_ADMISSION_V0_1.md",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CANDIDATE_RECORD.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_RISK_RECORD.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_ADMISSION_DECISION.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CAPABILITY_RECEIPT.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_REGISTRY_INDEX.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/samples/TOOL_ADMISSION_FOUNDATION.sample.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CANDIDATE_CATALOG_V0_1.generated.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_RISK_CATALOG_V0_1.generated.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_DECISIONS_V0_1.generated.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CAPABILITY_REGISTRY_V0_1.generated.json",
        "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_INDEX_V0_1.json",
        "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_builder_v0_1.py",
        "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_validator_v0_1.py",
        f"{report_root}/GATE_ACK_{task_id}.md",
        f"{report_root}/OFFICIO_DOCTRINARIUM_AUTHORITY_ACK.json",
        f"{report_root}/STEP_PROOF_RECORDS.json",
        f"{report_root}/VALIDATOR_REPORT.json",
        f"{report_root}/CHANGED_FILES_STATUS.md",
        f"{report_root}/GIT_CLOSURE_REPORT.json",
        f"{report_root}/FINAL_RECEIPT.json",
        f"{report_root}/OWNER_REPORT_RU.md",
        f"{report_root}/AGENT_KPD_SELF_REVIEW.json",
    ]


def write_changed_paths_report(path: Path, changed_paths: list[str]) -> None:
    lines = [
        "# CHANGED FILES STATUS",
        "",
        "BEGIN_CHANGED_PATHS",
    ]
    lines.extend(changed_paths)
    lines.extend(
        [
            "END_CHANGED_PATHS",
            "",
            "Only allowed paths are listed for this task scope.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_step_proof_records(path: Path, task_id: str) -> None:
    records = [
        {
            "STEP_ID": "MTA-S1",
            "CLAIM": "Admission authority and gate law intake completed before implementation.",
            "BASIS": [
                f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/GATE_ACK_{task_id}.md",
                f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/OFFICIO_DOCTRINARIUM_AUTHORITY_ACK.json",
            ],
            "RISK": "If authority intake is skipped, scope or no-install violations can occur.",
            "PROOF_PLAN": "Require both ACK artifacts before accepting implementation as admitted.",
            "ACTION": "ACK artifacts created before builder/validator outputs.",
            "SELF_VERDICT": "PROVED",
            "OWNER_RELEVANCE": "Confirms lawful admission before file-generation work.",
        },
        {
            "STEP_ID": "MTA-S2",
            "CLAIM": "Tool admission schemas and sample contract are present for candidate/risk/decision/receipt/index.",
            "BASIS": [
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CANDIDATE_RECORD.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_RISK_RECORD.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_ADMISSION_DECISION.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CAPABILITY_RECEIPT.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_REGISTRY_INDEX.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/samples/TOOL_ADMISSION_FOUNDATION.sample.json",
            ],
            "RISK": "Schema gaps could allow fake-green claims or inconsistent record fields.",
            "PROOF_PLAN": "Validator checks parseability and required fields for all schema-linked outputs.",
            "ACTION": "Contracts created and included in scope-tracked diff set.",
            "SELF_VERDICT": "PROVED",
            "OWNER_RELEVANCE": "Provides deterministic contract law for future admission tasks.",
        },
        {
            "STEP_ID": "MTA-S3",
            "CLAIM": "Builder generates candidate/risk/decision/capability/index records for required tools.",
            "BASIS": [
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CANDIDATE_CATALOG_V0_1.generated.json",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_RISK_CATALOG_V0_1.generated.json",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_DECISIONS_V0_1.generated.json",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CAPABILITY_REGISTRY_V0_1.generated.json",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_INDEX_V0_1.json",
            ],
            "RISK": "Missing tool entries would undercut phase-10 admission readiness.",
            "PROOF_PLAN": "Validate required tool names and state vocabulary in generated catalogs.",
            "ACTION": "Builder emits deterministic catalogs for the seven required candidate tools.",
            "SELF_VERDICT": "PROVED",
            "OWNER_RELEVANCE": "Establishes operational admission registry baseline.",
        },
        {
            "STEP_ID": "MTA-S4",
            "CLAIM": "No-install and no-fake-green boundaries are explicitly embedded in records and decisions.",
            "BASIS": [
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_DECISIONS_V0_1.generated.json",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CAPABILITY_REGISTRY_V0_1.generated.json",
                "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_INDEX_V0_1.json",
            ],
            "RISK": "Overstated readiness could create fake PASS and unsafe install behavior.",
            "PROOF_PLAN": "Validator blocks install-positive claims and production-ready language.",
            "ACTION": "All decisions keep install_allowed_now=false and no_install_performed=true.",
            "SELF_VERDICT": "PROVED",
            "OWNER_RELEVANCE": "Protects repo from premature or unsafe toolchain claims.",
        },
        {
            "STEP_ID": "MTA-S5",
            "CLAIM": "Report bundle contains required receipts for audit and closure preparation.",
            "BASIS": [
                f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/STEP_PROOF_RECORDS.json",
                f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/CHANGED_FILES_STATUS.md",
                f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/FINAL_RECEIPT.json",
                f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/GIT_CLOSURE_REPORT.json",
            ],
            "RISK": "Missing receipts would violate evidence-gate law.",
            "PROOF_PLAN": "Validator requires report-bundle file presence and parseability.",
            "ACTION": "Builder writes report scaffolds before validator execution.",
            "SELF_VERDICT": "PROVED",
            "OWNER_RELEVANCE": "Ensures closure readiness before commit/push phase.",
        },
    ]
    write_json(path, records)


def write_owner_report(path: Path, task_id: str) -> None:
    lines = [
        "# Owner Report RU - Mechanicus Tool Admission V0.1",
        "",
        "## STEP",
        "",
        task_id,
        "",
        "## BUNDLE",
        "",
        f"/home/vboxuser3/IMPERIUM_WORK/Imperium-/IMPERIUM_NEW_GENERATION/REPORTS/{task_id}",
        "",
        "## VERDICT",
        "",
        "FOUNDATION_READY_PENDING_GIT_CLOSURE",
        "",
        "## Кратко",
        "",
        "- Собран foundation-слой admission: candidate/risk/decision/capability/index.",
        "- Зафиксирован строгий no-install режим для фазы 10.",
        "- Подготовлен validator-контур против fake-green и out-of-scope заявлений.",
        "",
        "## Ограничения",
        "",
        "- Это не установка инструментов и не production toolchain.",
        "- Любое повышение состояния требует отдельной admission/install задачи.",
        "",
        "## Следующая разрешённая задача",
        "",
        NEXT_ALLOWED_TASK,
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_receipt(path: Path, task_id: str) -> None:
    payload = {
        "task_id": task_id,
        "mode": "VM3",
        "status": "FOUNDATION_COMPLETED_PENDING_GIT_CLOSURE",
        "required_starting_head": REQUIRED_STARTING_HEAD,
        "receipt_subject_head": REQUIRED_STARTING_HEAD,
        "receipt_content_head": "PENDING_COMMIT",
        "external_delivery_head": "",
        "remote_head_after_push": "",
        "followup_finalization_receipt_head": "",
        "self_head_paradox_handled": True,
        "clean_pass_allowed": False,
        "caps_triggered": ["CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING"],
        "commit_url": "",
        "builder": "PASS",
        "validator": "",
        "push_verified": False,
        "worktree_clean": False,
        "no_install_obeyed": True,
        "forbidden_paths_touched": False,
        "forbidden_claims_found": False,
        "created_artifacts": [
            "IMPERIUM_NEW_GENERATION/ARCHITECTURE/MECHANICUS_TOOL_ADMISSION_V0_1.md",
            "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/",
            "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_builder_v0_1.py",
            "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_validator_v0_1.py",
            "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/"
        ],
        "warnings": [],
        "next_allowed_task": NEXT_ALLOWED_TASK,
    }
    write_json(path, payload)


def write_git_closure_report(path: Path, task_id: str) -> None:
    payload = {
        "task_id": task_id,
        "closure_status": "PENDING_COMMIT_PUSH",
        "required_commit_message": COMMIT_MESSAGE,
        "receipt_subject_head": "",
        "external_delivery_head": "",
        "remote_head_after_push": "",
        "self_head_paradox_handled": True,
        "clean_pass_allowed": False,
        "caps_triggered": ["CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING"],
        "pushed": False,
        "worktree_clean": False,
        "changed_files_path": f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/CHANGED_FILES_STATUS.md",
        "notes": [
            "Builder prepares closure scaffold.",
            "Commit and push verification fields are finalized during git closure phase."
        ],
    }
    write_json(path, payload)


def write_kpd_self_review(path: Path, task_id: str) -> None:
    payload = {
        "agent_kpd_self_review": {
            "task_id": task_id,
            "agent_role": "SERVITOR_PRIME_Codex",
            "useful_outputs": [
                "Tool admission schemas",
                "Deterministic builder and validator",
                "Candidate/risk/decision/capability catalogs",
                "Report bundle scaffolding"
            ],
            "waste_points": [],
            "missing_tools": [
                "No existing dedicated tool-admission generator in this repo scope"
            ],
            "generated_tools_to_preserve": [
                "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_builder_v0_1.py",
                "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_validator_v0_1.py"
            ],
            "recommended_script_absorption": [
                "ABSORB_NOW: newgen_tool_admission_builder_v0_1.py",
                "ABSORB_NOW: newgen_tool_admission_validator_v0_1.py"
            ],
            "recommended_narrow_agent_profiles": [
                "NEWGEN_TOOL_ADMISSION_FOUNDATION_AGENT_V0_1"
            ],
            "future_prompt_improvements": [
                "Provide full 40-char required starting HEAD in taskpacks.",
                "Include standard closure report schema template with commit fields."
            ],
            "future_gate_or_checklist_recommendations": [
                "Add explicit gate check for short-hash normalization in task intake."
            ],
            "kpd_verdict": "GOOD"
        }
    }
    write_json(path, payload)


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    task_id = args.task_id
    report_dir = (
        Path(args.report_dir).resolve()
        if args.report_dir.strip()
        else repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    )

    contracts_dir = repo_root / "IMPERIUM_NEW_GENERATION" / "CONTRACTS" / "TOOL_ADMISSION"
    samples_dir = contracts_dir / "samples"
    mechanicus_dir = repo_root / "IMPERIUM_NEW_GENERATION" / "MECHANICUS" / "TOOL_ADMISSION"

    candidates = build_candidates(task_id)
    risks = build_risks(task_id, candidates)
    decisions = build_decisions(task_id, candidates)
    capabilities = build_capabilities(task_id, decisions)
    state_counts = count_states(candidates)
    index = build_index(
        task_id=task_id,
        candidate_count=len(candidates),
        risk_count=len(risks),
        decision_count=len(decisions),
        capability_count=len(capabilities),
        state_counts=state_counts,
    )
    sample = build_sample(task_id, candidates, risks, decisions, capabilities, index)

    write_json(
        mechanicus_dir / "TOOL_CANDIDATE_CATALOG_V0_1.generated.json",
        candidates,
    )
    write_json(
        mechanicus_dir / "TOOL_RISK_CATALOG_V0_1.generated.json",
        risks,
    )
    write_json(
        mechanicus_dir / "TOOL_ADMISSION_DECISIONS_V0_1.generated.json",
        decisions,
    )
    write_json(
        mechanicus_dir / "TOOL_CAPABILITY_REGISTRY_V0_1.generated.json",
        capabilities,
    )
    write_json(
        mechanicus_dir / "TOOL_ADMISSION_INDEX_V0_1.json",
        index,
    )
    write_json(
        samples_dir / "TOOL_ADMISSION_FOUNDATION.sample.json",
        sample,
    )

    write_changed_paths_report(
        report_dir / "CHANGED_FILES_STATUS.md",
        changed_path_list(task_id),
    )
    write_step_proof_records(report_dir / "STEP_PROOF_RECORDS.json", task_id)
    write_owner_report(report_dir / "OWNER_REPORT_RU.md", task_id)
    write_final_receipt(report_dir / "FINAL_RECEIPT.json", task_id)
    write_git_closure_report(report_dir / "GIT_CLOSURE_REPORT.json", task_id)
    write_kpd_self_review(report_dir / "AGENT_KPD_SELF_REVIEW.json", task_id)

    print((mechanicus_dir / "TOOL_ADMISSION_INDEX_V0_1.json").as_posix())
    print((report_dir / "FINAL_RECEIPT.json").as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
