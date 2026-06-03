#!/usr/bin/env python3
"""Validate NewGen Skill Growth System V0.1 foundation artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-SKILL-GROWTH-SYSTEM-VM3-V0_1"
FAILURE_TYPES = {
    "TASK_ARCHITECTURE_FAILURE",
    "SCOPE_AMBIGUITY",
    "SKILL_GAP",
    "TOOL_MISSING",
    "VALIDATOR_FAILURE",
    "VISUAL_MISMATCH",
    "FAKE_GREEN_RISK",
    "OWNER_DECISION_REQUIRED",
    "FOUNDATION_LIMITATION",
}
RERUN_DECISIONS = {
    "RERUN_ALLOWED",
    "RERUN_REQUIRED",
    "ASK_OWNER",
    "ASK_ORGAN",
    "BLOCKED",
    "PASS_WITH_WARNINGS",
    "PASS_STRICT",
}
FORBIDDEN_CLAIMS = {
    "agents are already self-learning in production",
    "skill updates are automatically applied to live agents",
    "future task success is guaranteed",
    "live organ dialogue is proven",
    "live autonomous execution is proven",
    "merge readiness is reached",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Skill Growth System V0.1 outputs.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--out", default="")
    return parser.parse_args()


def resolve_repo_root(cli_repo_root: str) -> Path:
    if cli_repo_root.strip():
        return Path(cli_repo_root).resolve()
    return Path(__file__).resolve().parents[3]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def required_paths(repo_root: Path, task_id: str) -> dict[str, Path]:
    report_dir = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    return {
        "architecture_doc": repo_root
        / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/SKILL_GROWTH_SYSTEM_V0_1.md",
        "schema_gap": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_GAP_RECORD.schema.json",
        "schema_lesson": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_LESSON_RECORD.schema.json",
        "schema_proposal": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_UPDATE_PROPOSAL.schema.json",
        "schema_recommendation": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/VALIDATOR_RECOMMENDATION_RECORD.schema.json",
        "schema_cycle": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/SKILL_GROWTH_CYCLE.schema.json",
        "sample_cycle": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SKILL_GROWTH/samples/SKILL_GROWTH_CYCLE.sample.json",
        "index": repo_root
        / "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/SKILL_GROWTH_INDEX_V0_1.json",
        "lessons_generated": repo_root
        / "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/LESSON_CATALOG_V0_1.generated.json",
        "proposals_generated": repo_root
        / "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/SKILL_UPDATE_PROPOSALS_V0_1.generated.json",
        "recommendations_generated": repo_root
        / "IMPERIUM_NEW_GENERATION/SKILLS/GROWTH/VALIDATOR_RECOMMENDATIONS_V0_1.generated.json",
        "builder": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/SKILL_GROWTH/newgen_skill_growth_builder_v0_1.py",
        "step_proof": report_dir / "STEP_PROOF_RECORDS.json",
        "final_receipt": report_dir / "FINAL_RECEIPT.json",
        "owner_report": report_dir / "OWNER_REPORT_RU.md",
        "closure_report": report_dir / "GIT_CLOSURE_REPORT.json",
        "changed_files": report_dir / "CHANGED_FILES_STATUS.md",
        "validator_report": report_dir / "VALIDATOR_REPORT.json",
    }


def check_required_files(paths: dict[str, Path]) -> list[str]:
    missing: list[str] = []
    for key, path in paths.items():
        if key == "validator_report":
            continue
        if not path.exists():
            missing.append(f"{key}: {path.as_posix()}")
    return missing


def parse_changed_paths(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    in_block = False
    result: list[str] = []
    for raw in lines:
        line = raw.strip()
        if line == "BEGIN_CHANGED_PATHS":
            in_block = True
            continue
        if line == "END_CHANGED_PATHS":
            in_block = False
            continue
        if in_block and line:
            result.append(line)
    return result


def run_builder(builder_path: Path, repo_root: Path, task_id: str, report_dir: Path) -> tuple[bool, str]:
    command = [
        sys.executable,
        str(builder_path),
        "--repo-root",
        str(repo_root),
        "--task-id",
        task_id,
        "--report-dir",
        str(report_dir),
    ]
    run = subprocess.run(command, capture_output=True, text=True, check=False)
    if run.returncode != 0:
        return False, f"returncode={run.returncode}; stderr={run.stderr.strip()}; stdout={run.stdout.strip()}"
    return True, "builder run succeeded"


def validate_cycle(cycle: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []

    if cycle.get("mode") != "FOUNDATION_ONLY":
        blockers.append("cycle mode must be FOUNDATION_ONLY")
    if cycle.get("foundation_only") is not True:
        blockers.append("cycle foundation_only must be true")
    if cycle.get("production_learning_enabled") is not False:
        blockers.append("cycle production_learning_enabled must be false")
    if cycle.get("automatic_live_agent_mutation") is not False:
        blockers.append("cycle automatic_live_agent_mutation must be false")

    forbidden_claims = cycle.get("forbidden_claims")
    if not isinstance(forbidden_claims, list):
        blockers.append("cycle forbidden_claims must be list")
    else:
        claim_set = {str(x).strip().lower() for x in forbidden_claims}
        missing_forbidden = sorted(FORBIDDEN_CLAIMS - claim_set)
        if missing_forbidden:
            warnings.append("cycle forbidden_claims missing entries: " + ", ".join(missing_forbidden))

    gaps = cycle.get("skill_gaps")
    if not isinstance(gaps, list) or not gaps:
        blockers.append("cycle skill_gaps must be non-empty list")
    else:
        for idx, gap in enumerate(gaps, start=1):
            if not isinstance(gap, dict):
                blockers.append(f"skill_gaps[{idx}] must be object")
                continue
            failure = str(gap.get("source_failure_type", "")).strip()
            rerun = str(gap.get("source_rerun_decision", "")).strip()
            if failure not in FAILURE_TYPES:
                blockers.append(f"skill_gaps[{idx}] invalid source_failure_type: {failure}")
            if rerun not in RERUN_DECISIONS:
                blockers.append(f"skill_gaps[{idx}] invalid source_rerun_decision: {rerun}")

    lessons = cycle.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        blockers.append("cycle lessons must be non-empty list")
    else:
        for idx, lesson in enumerate(lessons, start=1):
            if not isinstance(lesson, dict):
                blockers.append(f"lessons[{idx}] must be object")
                continue
            if not str(lesson.get("proof_status", "")).strip():
                blockers.append(f"lessons[{idx}] missing proof_status")
            if not str(lesson.get("confidence", "")).strip():
                blockers.append(f"lessons[{idx}] missing confidence")

    proposals = cycle.get("skill_update_proposals")
    if not isinstance(proposals, list) or not proposals:
        blockers.append("cycle skill_update_proposals must be non-empty list")
    else:
        for idx, proposal in enumerate(proposals, start=1):
            if not isinstance(proposal, dict):
                blockers.append(f"skill_update_proposals[{idx}] must be object")
                continue
            if proposal.get("mutating_live_agents") is not False:
                blockers.append(f"skill_update_proposals[{idx}] mutating_live_agents must be false")
            if proposal.get("proposal_effect") != "NON_MUTATING_ADVISORY":
                blockers.append(
                    f"skill_update_proposals[{idx}] proposal_effect must be NON_MUTATING_ADVISORY"
                )

    recommendations = cycle.get("validator_recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        blockers.append("cycle validator_recommendations must be non-empty list")
    else:
        for idx, recommendation in enumerate(recommendations, start=1):
            if not isinstance(recommendation, dict):
                blockers.append(f"validator_recommendations[{idx}] must be object")
                continue
            proof_status = str(recommendation.get("proof_status", ""))
            advisory_only = recommendation.get("advisory_only")
            if proof_status != "PROVED" and advisory_only is not True:
                blockers.append(
                    f"validator_recommendations[{idx}] must stay advisory unless proof_status is PROVED"
                )

    return blockers, warnings


def contains_cyrillic(text: str) -> bool:
    return re.search(r"[А-Яа-яЁё]", text) is not None


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    task_id = args.task_id
    paths = required_paths(repo_root, task_id)
    report_dir = paths["validator_report"].parent
    out_path = Path(args.out).resolve() if args.out.strip() else paths["validator_report"]

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    builder_ok, builder_details = run_builder(paths["builder"], repo_root, task_id, report_dir)
    checks.append(
        {
            "check_id": "builder_runs",
            "status": "PASS" if builder_ok else "BLOCK",
            "details": builder_details,
        }
    )
    if not builder_ok:
        blockers.append("builder execution failed")

    missing_required = check_required_files(paths)
    checks.append(
        {
            "check_id": "required_files_exist",
            "status": "PASS" if not missing_required else "BLOCK",
            "details": "all required files exist" if not missing_required else "; ".join(missing_required),
        }
    )
    blockers.extend(missing_required)

    parse_targets = [
        "schema_gap",
        "schema_lesson",
        "schema_proposal",
        "schema_recommendation",
        "schema_cycle",
        "sample_cycle",
        "index",
        "lessons_generated",
        "proposals_generated",
        "recommendations_generated",
        "step_proof",
        "final_receipt",
        "closure_report",
        "officio_ack",
    ]
    parse_errors: list[str] = []
    for key in parse_targets:
        if key == "officio_ack":
            path = report_dir / "OFFICIO_DOCTRINARIUM_AUTHORITY_ACK.json"
        else:
            path = paths[key]
        if not path.exists():
            continue
        try:
            read_json(path)
        except Exception as exc:
            parse_errors.append(f"{path.as_posix()}: {exc}")
    checks.append(
        {
            "check_id": "json_parseability",
            "status": "PASS" if not parse_errors else "BLOCK",
            "details": "json artifacts parse correctly" if not parse_errors else "; ".join(parse_errors),
        }
    )
    blockers.extend(parse_errors)

    deterministic_targets = [
        paths["sample_cycle"],
        paths["index"],
        paths["lessons_generated"],
        paths["proposals_generated"],
        paths["recommendations_generated"],
    ]
    deterministic_mismatch: list[str] = []
    if not blockers:
        before = {path.as_posix(): sha256_file(path) for path in deterministic_targets}
        run_builder(paths["builder"], repo_root, task_id, report_dir)
        after = {path.as_posix(): sha256_file(path) for path in deterministic_targets}
        for file_path, checksum_before in before.items():
            if checksum_before != after[file_path]:
                deterministic_mismatch.append(file_path)
    checks.append(
        {
            "check_id": "deterministic_builder_outputs",
            "status": "PASS" if not deterministic_mismatch else "BLOCK",
            "details": "deterministic outputs confirmed"
            if not deterministic_mismatch
            else "; ".join(deterministic_mismatch),
        }
    )
    blockers.extend([f"deterministic mismatch: {x}" for x in deterministic_mismatch])

    cycle_blockers: list[str] = []
    cycle_warnings: list[str] = []
    if not blockers:
        cycle = read_json(paths["sample_cycle"])
        if isinstance(cycle, dict):
            cycle_blockers, cycle_warnings = validate_cycle(cycle)
            blockers.extend(cycle_blockers)
            warnings.extend(cycle_warnings)
        else:
            blockers.append("sample cycle must be JSON object")
    checks.append(
        {
            "check_id": "skill_growth_cycle_rules",
            "status": "PASS" if not cycle_blockers else "BLOCK",
            "details": "cycle rule checks passed" if not cycle_blockers else "; ".join(cycle_blockers),
        }
    )

    owner_report_ok = False
    if paths["owner_report"].exists():
        owner_report_ok = contains_cyrillic(paths["owner_report"].read_text(encoding="utf-8"))
    checks.append(
        {
            "check_id": "owner_report_ru_present",
            "status": "PASS" if owner_report_ok else "BLOCK",
            "details": "owner report contains Russian text"
            if owner_report_ok
            else "OWNER_REPORT_RU.md is missing or contains no Cyrillic content",
        }
    )
    if not owner_report_ok:
        blockers.append("owner report RU check failed")

    changed_paths = parse_changed_paths(paths["changed_files"])
    forbidden_hits = [
        x
        for x in changed_paths
        if x.startswith("ORGANS/")
        or x.startswith("SANCTUM/")
        or x.startswith("IMPERIUM_TEST_VERSION/")
        or x.startswith("IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/")
        or x.startswith("IMPERIUM_NEW_GENERATION/VISUAL_BRAIN/")
    ]
    checks.append(
        {
            "check_id": "allowed_scope_only_reported",
            "status": "PASS" if not forbidden_hits else "BLOCK",
            "details": "changed files list stays in allowed scope"
            if not forbidden_hits
            else "; ".join(sorted(set(forbidden_hits))),
        }
    )
    blockers.extend([f"forbidden changed path: {x}" for x in sorted(set(forbidden_hits))])

    final_receipt_ok = False
    if paths["final_receipt"].exists():
        payload = read_json(paths["final_receipt"])
        final_receipt_ok = isinstance(payload, dict) and payload.get("task_id") == task_id
    checks.append(
        {
            "check_id": "final_receipt_present",
            "status": "PASS" if final_receipt_ok else "BLOCK",
            "details": "final receipt exists for task" if final_receipt_ok else "FINAL_RECEIPT.json missing or mismatched",
        }
    )
    if not final_receipt_ok:
        blockers.append("final receipt check failed")

    verdict = "BLOCKED" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    report = {
        "schema_version": "0.1",
        "task_id": task_id,
        "validator": "newgen_skill_growth_validator_v0_1.py",
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": sorted(set(warnings)),
        "blockers": sorted(set(blockers)),
        "builder_command": (
            f"{sys.executable} IMPERIUM_NEW_GENERATION/TOOLS/SKILL_GROWTH/"
            "newgen_skill_growth_builder_v0_1.py"
        ),
        "no_fake_learning_note": (
            "PASS validates foundation-only contract integrity. "
            "It is not proof of production self-learning or live autonomous improvement."
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path.as_posix())
    print(f"verdict={verdict}")
    return 1 if verdict == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
