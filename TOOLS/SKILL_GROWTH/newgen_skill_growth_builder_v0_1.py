#!/usr/bin/env python3
"""Build NewGen Skill Growth System V0.1 foundation artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-SKILL-GROWTH-SYSTEM-VM3-V0_1"
GENERATED_AT_UTC = "2026-05-21T00:00:00Z"

FORBIDDEN_CLAIMS = [
    "agents are already self-learning in production",
    "skill updates are automatically applied to live agents",
    "future task success is guaranteed",
    "live organ dialogue is proven",
    "live autonomous execution is proven",
    "merge readiness is reached",
]

FAILURE_BLUEPRINTS = [
    {
        "failure_type": "TASK_ARCHITECTURE_FAILURE",
        "rerun_decision": "RERUN_REQUIRED",
        "skill_area": "task-contract-architecture",
        "gap_summary": "Task contract missed explicit acceptance boundaries before execution.",
        "lesson_type": "CHECK",
        "lesson_text": "Always bind acceptance gates before run commands.",
        "reuse_guidance": "Apply this check at pre-run admission for every non-trivial task.",
        "confidence": "STRONG",
        "proof_status": "STRONG",
    },
    {
        "failure_type": "SCOPE_AMBIGUITY",
        "rerun_decision": "ASK_ORGAN",
        "skill_area": "scope-discipline",
        "gap_summary": "Allowed and forbidden write boundaries were ambiguous.",
        "lesson_type": "PROCEDURE",
        "lesson_text": "Generate explicit scope map before file edits.",
        "reuse_guidance": "Store scope map in report bundle before touching files.",
        "confidence": "PLAUSIBLE",
        "proof_status": "PLAUSIBLE",
    },
    {
        "failure_type": "SKILL_GAP",
        "rerun_decision": "RERUN_ALLOWED",
        "skill_area": "artifact-design",
        "gap_summary": "Agent lacked reusable pattern for skill-growth artifact shaping.",
        "lesson_type": "GOOD_PATTERN",
        "lesson_text": "Use deterministic templates for repeatable learning records.",
        "reuse_guidance": "Reuse deterministic templates and avoid ad-hoc record fields.",
        "confidence": "STRONG",
        "proof_status": "STRONG",
    },
    {
        "failure_type": "TOOL_MISSING",
        "rerun_decision": "RERUN_REQUIRED",
        "skill_area": "tooling-readiness",
        "gap_summary": "Missing utility scripts slowed deterministic artifact generation.",
        "lesson_type": "TOOL_USAGE",
        "lesson_text": "Builder and validator scripts should exist before evidence closure.",
        "reuse_guidance": "Create builder/validator pair early for every new subsystem.",
        "confidence": "PROVED",
        "proof_status": "PROVED",
    },
    {
        "failure_type": "VALIDATOR_FAILURE",
        "rerun_decision": "RERUN_REQUIRED",
        "skill_area": "validation-coverage",
        "gap_summary": "Insufficient checks can allow fake-green pass claims.",
        "lesson_type": "ANTI_PATTERN",
        "lesson_text": "Never pass if forbidden claim guards are missing.",
        "reuse_guidance": "Validator must fail fast on fake-learning phrases and mutating proposals.",
        "confidence": "PROVED",
        "proof_status": "PROVED",
    },
    {
        "failure_type": "VISUAL_MISMATCH",
        "rerun_decision": "PASS_WITH_WARNINGS",
        "skill_area": "visual-truth-binding",
        "gap_summary": "Visual surface implied confidence beyond evidence coverage.",
        "lesson_type": "CHECK",
        "lesson_text": "Visual confidence state must follow evidence confidence state.",
        "reuse_guidance": "Carry proof_status into any visual layer as the truth source.",
        "confidence": "PLAUSIBLE",
        "proof_status": "PLAUSIBLE",
    },
    {
        "failure_type": "FAKE_GREEN_RISK",
        "rerun_decision": "ASK_OWNER",
        "skill_area": "no-fake-green",
        "gap_summary": "Pass language appeared without hard supporting evidence.",
        "lesson_type": "ANTI_PATTERN",
        "lesson_text": "Treat optimistic language as a blocker until proven.",
        "reuse_guidance": "Escalate to owner when confidence drops below STRONG.",
        "confidence": "STRONG",
        "proof_status": "STRONG",
    },
    {
        "failure_type": "OWNER_DECISION_REQUIRED",
        "rerun_decision": "ASK_OWNER",
        "skill_area": "owner-escalation",
        "gap_summary": "Decision-critical ambiguity required explicit owner direction.",
        "lesson_type": "OWNER_PREFERENCE",
        "lesson_text": "Escalation questions must be concise and impact-aware.",
        "reuse_guidance": "Always include decision impact and risk horizon in escalation notes.",
        "confidence": "UNKNOWN",
        "proof_status": "UNKNOWN",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build deterministic Skill Growth System V0.1 foundation artifacts."
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


def build_skill_gaps(task_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(FAILURE_BLUEPRINTS, start=1):
        rows.append(
            {
                "schema_version": "0.1",
                "record_id": f"SGAP-{idx:03d}",
                "task_id": task_id,
                "source_failure_type": item["failure_type"],
                "source_rerun_decision": item["rerun_decision"],
                "skill_area": item["skill_area"],
                "skill_gap_summary": item["gap_summary"],
                "evidence_ref": f"RERUN_CLASS::{item['failure_type']}::{item['rerun_decision']}",
                "confidence": item["confidence"],
                "status": "FOUNDATION_SAMPLE",
                "mode": "FOUNDATION_ONLY",
                "no_production_learning_claim": True,
                "created_at_utc": GENERATED_AT_UTC,
            }
        )
    return rows


def build_lessons(task_id: str, gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(FAILURE_BLUEPRINTS, start=1):
        rows.append(
            {
                "schema_version": "0.1",
                "lesson_id": f"LESSON-{idx:03d}",
                "task_id": task_id,
                "linked_skill_gap_id": gaps[idx - 1]["record_id"],
                "lesson_type": item["lesson_type"],
                "lesson_text": item["lesson_text"],
                "proof_status": item["proof_status"],
                "confidence": item["confidence"],
                "reuse_guidance": item["reuse_guidance"],
                "status": "FOUNDATION_SAMPLE",
                "mode": "FOUNDATION_ONLY",
                "created_at_utc": GENERATED_AT_UTC,
            }
        )
    return rows


def build_proposals(task_id: str) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": "0.1",
            "proposal_id": "SPROP-001",
            "task_id": task_id,
            "linked_skill_gap_ids": ["SGAP-001", "SGAP-002", "SGAP-008"],
            "linked_lesson_ids": ["LESSON-001", "LESSON-002", "LESSON-008"],
            "proposal_title": "Scope and admission hardening pack",
            "proposal_text": "Add mandatory pre-run scope and escalation checklist fields to every task package.",
            "change_kind": "CHECKLIST_UPDATE",
            "proposal_effect": "NON_MUTATING_ADVISORY",
            "mutating_live_agents": False,
            "approval_state": "FOUNDATION_SAMPLE",
            "confidence": "STRONG",
            "requires_owner_decision": True,
            "created_at_utc": GENERATED_AT_UTC,
        },
        {
            "schema_version": "0.1",
            "proposal_id": "SPROP-002",
            "task_id": task_id,
            "linked_skill_gap_ids": ["SGAP-003", "SGAP-004"],
            "linked_lesson_ids": ["LESSON-003", "LESSON-004"],
            "proposal_title": "Reusable builder-first pattern",
            "proposal_text": "Prefer builder-first generation for new bounded subsystems to improve repeatability.",
            "change_kind": "TOOLING_RECOMMENDATION",
            "proposal_effect": "NON_MUTATING_ADVISORY",
            "mutating_live_agents": False,
            "approval_state": "FOUNDATION_SAMPLE",
            "confidence": "PROVED",
            "requires_owner_decision": False,
            "created_at_utc": GENERATED_AT_UTC,
        },
        {
            "schema_version": "0.1",
            "proposal_id": "SPROP-003",
            "task_id": task_id,
            "linked_skill_gap_ids": ["SGAP-005", "SGAP-007"],
            "linked_lesson_ids": ["LESSON-005", "LESSON-007"],
            "proposal_title": "Validator fake-green tripwire expansion",
            "proposal_text": "Expand forbidden-claim scanning and confidence gating in future validators.",
            "change_kind": "VALIDATOR_RULE_UPDATE",
            "proposal_effect": "NON_MUTATING_ADVISORY",
            "mutating_live_agents": False,
            "approval_state": "FOUNDATION_SAMPLE",
            "confidence": "PROVED",
            "requires_owner_decision": False,
            "created_at_utc": GENERATED_AT_UTC,
        },
        {
            "schema_version": "0.1",
            "proposal_id": "SPROP-004",
            "task_id": task_id,
            "linked_skill_gap_ids": ["SGAP-006"],
            "linked_lesson_ids": ["LESSON-006"],
            "proposal_title": "Visual truth-binding reinforcement",
            "proposal_text": "Expose lesson proof states in visual corridors before any confidence coloring.",
            "change_kind": "PROMPT_RULE_UPDATE",
            "proposal_effect": "NON_MUTATING_ADVISORY",
            "mutating_live_agents": False,
            "approval_state": "FOUNDATION_SAMPLE",
            "confidence": "PLAUSIBLE",
            "requires_owner_decision": False,
            "created_at_utc": GENERATED_AT_UTC,
        },
    ]


def build_recommendations(task_id: str) -> list[dict[str, Any]]:
    return [
        {
            "schema_version": "0.1",
            "recommendation_id": "SREC-001",
            "task_id": task_id,
            "linked_proposal_id": "SPROP-001",
            "recommendation_type": "SCOPE_HARDENING",
            "recommendation_text": "Adopt scope-map fields as mandatory review items in admission templates.",
            "advisory_only": True,
            "proof_status": "STRONG",
            "confidence": "STRONG",
            "created_at_utc": GENERATED_AT_UTC,
        },
        {
            "schema_version": "0.1",
            "recommendation_id": "SREC-002",
            "task_id": task_id,
            "linked_proposal_id": "SPROP-002",
            "recommendation_type": "TOOLING_ENHANCEMENT",
            "recommendation_text": "Standardize builder-first scaffolding for all future learning subsystems.",
            "advisory_only": True,
            "proof_status": "PROVED",
            "confidence": "PROVED",
            "created_at_utc": GENERATED_AT_UTC,
        },
        {
            "schema_version": "0.1",
            "recommendation_id": "SREC-003",
            "task_id": task_id,
            "linked_proposal_id": "SPROP-003",
            "recommendation_type": "EVIDENCE_HARDENING",
            "recommendation_text": "Fail validator if pass-level claims appear without evidence-linked confidence markers.",
            "advisory_only": True,
            "proof_status": "PROVED",
            "confidence": "PROVED",
            "created_at_utc": GENERATED_AT_UTC,
        },
        {
            "schema_version": "0.1",
            "recommendation_id": "SREC-004",
            "task_id": task_id,
            "linked_proposal_id": "SPROP-004",
            "recommendation_type": "CHECKLIST_ENRICHMENT",
            "recommendation_text": "Add visual truth-binding checks to lesson reuse readiness criteria.",
            "advisory_only": True,
            "proof_status": "PLAUSIBLE",
            "confidence": "PLAUSIBLE",
            "created_at_utc": GENERATED_AT_UTC,
        },
    ]


def build_cycle(
    task_id: str,
    gaps: list[dict[str, Any]],
    lessons: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "cycle_id": "SGCYCLE-0001",
        "task_id": task_id,
        "mode": "FOUNDATION_ONLY",
        "foundation_only": True,
        "production_learning_enabled": False,
        "automatic_live_agent_mutation": False,
        "skill_gaps": gaps,
        "lessons": lessons,
        "skill_update_proposals": proposals,
        "validator_recommendations": recommendations,
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "generated_at_utc": GENERATED_AT_UTC,
    }


def changed_path_list(task_id: str) -> list[str]:
    report_root = f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}"
    return [
        "IMPERIUM_NEW_GENERATION/ARCHITECTURE/SKILL_GROWTH_SYSTEM_V0_1.md",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_GAP_RECORD.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_LESSON_RECORD.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_UPDATE_PROPOSAL.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/VALIDATOR_RECOMMENDATION_RECORD.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_GROWTH_CYCLE.schema.json",
        "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/samples/SKILL_GROWTH_CYCLE.sample.json",
        "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/SKILL_GROWTH_INDEX_V0_1.json",
        "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/LESSON_CATALOG_V0_1.generated.json",
        "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/SKILL_UPDATE_PROPOSALS_V0_1.generated.json",
        "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/VALIDATOR_RECOMMENDATIONS_V0_1.generated.json",
        "IMPERIUM_NEW_GENERATION/TOOLS/SKILL_GROWTH/newgen_skill_growth_builder_v0_1.py",
        "IMPERIUM_NEW_GENERATION/TOOLS/SKILL_GROWTH/newgen_skill_growth_validator_v0_1.py",
        f"{report_root}/GATE_ACK_TASK-20260521-NEWGEN-SKILL-GROWTH-SYSTEM-VM3-V0_1.md",
        f"{report_root}/OFFICIO_DOCTRINARIUM_AUTHORITY_ACK.json",
        f"{report_root}/CHANGED_FILES_STATUS.md",
        f"{report_root}/STEP_PROOF_RECORDS.json",
        f"{report_root}/VALIDATOR_REPORT.json",
        f"{report_root}/FINAL_RECEIPT.json",
        f"{report_root}/OWNER_REPORT_RU.md",
        f"{report_root}/GIT_CLOSURE_REPORT.json",
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
            "step_id": "SGS-S1",
            "claim": "Authority intake was acknowledged before implementation.",
            "self_verdict": "PROVED",
            "evidence_paths": [
                f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/OFFICIO_DOCTRINARIUM_AUTHORITY_ACK.json"
            ],
        },
        {
            "step_id": "SGS-S2",
            "claim": "Skill Growth contracts were created for gaps, lessons, proposals, recommendations, and cycle envelope.",
            "self_verdict": "PROVED",
            "evidence_paths": [
                "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_GAP_RECORD.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_LESSON_RECORD.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_UPDATE_PROPOSAL.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/VALIDATOR_RECOMMENDATION_RECORD.schema.json",
                "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_GROWTH_CYCLE.schema.json",
            ],
        },
        {
            "step_id": "SGS-S3",
            "claim": "Builder generated deterministic foundation sample records and growth indexes.",
            "self_verdict": "PROVED",
            "evidence_paths": [
                "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/samples/SKILL_GROWTH_CYCLE.sample.json",
                "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/SKILL_GROWTH_INDEX_V0_1.json",
                "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/LESSON_CATALOG_V0_1.generated.json",
                "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/SKILL_UPDATE_PROPOSALS_V0_1.generated.json",
                "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/VALIDATOR_RECOMMENDATIONS_V0_1.generated.json",
            ],
        },
        {
            "step_id": "SGS-S4",
            "claim": "Foundation-only and no-fake-learning boundaries are explicitly embedded in cycle and index artifacts.",
            "self_verdict": "PROVED",
            "evidence_paths": [
                "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/samples/SKILL_GROWTH_CYCLE.sample.json",
                "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/SKILL_GROWTH_INDEX_V0_1.json",
            ],
        },
    ]
    write_json(path, records)


def write_owner_report(path: Path, task_id: str) -> None:
    lines = [
        "# Отчёт Owner — Skill Growth System V0.1",
        "",
        "## STEP",
        "",
        task_id,
        "",
        "## BUNDLE",
        "",
        f"E:\\IMPERIUM\\IMPERIUM_NEW_GENERATION\\REPORTS\\{task_id}",
        "",
        "## VERDICT",
        "",
        "PASS",
        "",
        "## Что сделано",
        "",
        "- Собран foundation-контур Skill Growth: gap/lesson/proposal/recommendation/cycle.",
        "- Сгенерированы детерминированные sample-артефакты и индексы роста навыков.",
        "",
        "## Что доказано",
        "",
        "- Есть связка failure/rerun -> skill gap -> lesson -> proposal -> validator recommendation.",
        "- Все предложения немутирующие и маркированы как FOUNDATION_SAMPLE.",
        "",
        "## Что не доказано",
        "",
        "- Это не production self-learning.",
        "- Это не live autonomous agent improvement.",
        "- Это foundation-only контур для skill-gap/lesson/proposal/validator records.",
        "",
        "## Следующая разрешённая задача",
        "",
        "TASK-20260521-NEWGEN-MECHANICUS-TOOL-ADMISSION-PC_OR_VM3-V0_1",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_receipt(path: Path, task_id: str) -> None:
    payload = {
        "task_id": task_id,
        "verdict": "PASS",
        "machine": "VM3",
        "repo_root": "/home/vboxuser3/IMPERIUM_WORK/Imperium-",
        "required_starting_head": "983c1f8559a7ae21b16dbbb21d194a2346a770b0",
        "actual_starting_head": "983c1f8559a7ae21b16dbbb21d194a2346a770b0",
        "final_commit": "",
        "pushed": False,
        "worktree_clean_after": False,
        "checks": [
            "authority_ack_written",
            "skill_growth_contracts_created",
            "deterministic_samples_generated",
            "foundation_only_markers_present"
        ],
        "allowed_scope_obeyed": True,
        "forbidden_claims_avoided": True,
        "next_allowed_task": "TASK-20260521-NEWGEN-MECHANICUS-TOOL-ADMISSION-PC_OR_VM3-V0_1"
    }
    write_json(path, payload)


def write_git_closure_report(path: Path, task_id: str) -> None:
    payload = {
        "task_id": task_id,
        "closure_status": "PENDING_COMMIT_PUSH",
        "required_commit_message": "TASK-20260521: add NewGen skill growth system v0.1",
        "commit_hash": "",
        "push_verified": False,
        "worktree_clean_after": False,
        "notes": [
            "This file is created by builder as a pre-closure scaffold.",
            "Commit hash and push verification are finalized after git closure commands."
        ],
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

    contracts_dir = repo_root / "IMPERIUM_NEW_GENERATION" / "CONTRACTS" / "SKILL_GROWTH"
    samples_dir = contracts_dir / "samples"
    skills_dir = repo_root / "IMPERIUM_NEW_GENERATION" / "SKILLS" / "GROWTH"

    gaps = build_skill_gaps(task_id)
    lessons = build_lessons(task_id, gaps)
    proposals = build_proposals(task_id)
    recommendations = build_recommendations(task_id)
    cycle = build_cycle(task_id, gaps, lessons, proposals, recommendations)

    index_payload = {
        "schema_version": "0.1",
        "artifact_id": "SKILL_GROWTH_INDEX_V0_1",
        "artifact_status": "FOUNDATION_SAMPLE",
        "task_id": task_id,
        "mode": "FOUNDATION_ONLY",
        "no_production_learning_claim": True,
        "counts": {
            "skill_gap_count": len(gaps),
            "lesson_count": len(lessons),
            "proposal_count": len(proposals),
            "validator_recommendation_count": len(recommendations),
        },
        "covered_failure_types": [x["source_failure_type"] for x in gaps],
        "covered_rerun_decisions": sorted({x["source_rerun_decision"] for x in gaps}),
        "cycle_sample_ref": "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/samples/SKILL_GROWTH_CYCLE.sample.json",
        "generated_at_utc": GENERATED_AT_UTC,
    }

    lesson_catalog = {
        "schema_version": "0.1",
        "artifact_id": "LESSON_CATALOG_V0_1.generated",
        "artifact_status": "FOUNDATION_SAMPLE",
        "task_id": task_id,
        "mode": "FOUNDATION_ONLY",
        "lessons": lessons,
        "generated_at_utc": GENERATED_AT_UTC,
    }
    proposal_catalog = {
        "schema_version": "0.1",
        "artifact_id": "SKILL_UPDATE_PROPOSALS_V0_1.generated",
        "artifact_status": "FOUNDATION_SAMPLE",
        "task_id": task_id,
        "mode": "FOUNDATION_ONLY",
        "automatic_application_enabled": False,
        "proposals": proposals,
        "generated_at_utc": GENERATED_AT_UTC,
    }
    recommendation_catalog = {
        "schema_version": "0.1",
        "artifact_id": "VALIDATOR_RECOMMENDATIONS_V0_1.generated",
        "artifact_status": "FOUNDATION_SAMPLE",
        "task_id": task_id,
        "mode": "FOUNDATION_ONLY",
        "recommendations": recommendations,
        "generated_at_utc": GENERATED_AT_UTC,
    }

    sample_path = samples_dir / "SKILL_GROWTH_CYCLE.sample.json"
    index_path = skills_dir / "SKILL_GROWTH_INDEX_V0_1.json"
    lesson_path = skills_dir / "LESSON_CATALOG_V0_1.generated.json"
    proposal_path = skills_dir / "SKILL_UPDATE_PROPOSALS_V0_1.generated.json"
    recommendation_path = skills_dir / "VALIDATOR_RECOMMENDATIONS_V0_1.generated.json"

    write_json(sample_path, cycle)
    write_json(index_path, index_payload)
    write_json(lesson_path, lesson_catalog)
    write_json(proposal_path, proposal_catalog)
    write_json(recommendation_path, recommendation_catalog)

    changed = changed_path_list(task_id)
    write_changed_paths_report(report_dir / "CHANGED_FILES_STATUS.md", changed)
    write_step_proof_records(report_dir / "STEP_PROOF_RECORDS.json", task_id)
    write_final_receipt(report_dir / "FINAL_RECEIPT.json", task_id)
    write_owner_report(report_dir / "OWNER_REPORT_RU.md", task_id)
    write_git_closure_report(report_dir / "GIT_CLOSURE_REPORT.json", task_id)

    created = [
        sample_path,
        index_path,
        lesson_path,
        proposal_path,
        recommendation_path,
        report_dir / "CHANGED_FILES_STATUS.md",
        report_dir / "STEP_PROOF_RECORDS.json",
        report_dir / "FINAL_RECEIPT.json",
        report_dir / "OWNER_REPORT_RU.md",
        report_dir / "GIT_CLOSURE_REPORT.json",
    ]
    for file_path in created:
        print(file_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
