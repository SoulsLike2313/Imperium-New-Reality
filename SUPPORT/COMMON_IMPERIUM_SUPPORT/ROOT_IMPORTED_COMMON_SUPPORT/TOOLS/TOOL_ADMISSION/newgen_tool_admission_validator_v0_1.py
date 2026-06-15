#!/usr/bin/env python3
"""Validate NewGen Mechanicus Tool Admission V0.1 foundation artifacts."""
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


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-MECHANICUS-TOOL-ADMISSION-VM3-V0_1"

ADMISSION_STATES = {
    "CANDIDATE_ONLY",
    "AVAILABLE_ON_HOST_UNVERIFIED_FOR_IMPERIUM",
    "AVAILABLE_ON_HOST_VERIFIED_BASIC",
    "DEFERRED_NEEDS_OWNER",
    "DEFERRED_NEEDS_ADMISSION_TASK",
    "BLOCKED_BY_RISK",
    "APPROVED_FOR_FUTURE_INSTALL_TASK",
    "APPROVED_FOR_READ_ONLY_USE",
    "INSTALLED_AND_REGISTERED",
}

REQUIRED_TOOL_NAMES = {
    "Playwright",
    "Vitest",
    "ESLint",
    "Storybook",
    "Nx",
    "Turborepo",
}

FORBIDDEN_CLAIMS = {
    "production toolchain is ready",
    "playwright/vitest/storybook/nx are installed by this task",
    "external tools are approved for unrestricted use",
    "future ui/ux evidence is guaranteed",
    "mechanicus has production package management",
    "live autonomous agents are proven",
}

ALLOWED_PREFIXES = (
    "IMPERIUM_NEW_GENERATION/ARCHITECTURE/",
    "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/",
    "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/",
    "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/",
    "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260521-NEWGEN-MECHANICUS-TOOL-ADMISSION-VM3-V0_1/",
)

FORBIDDEN_PREFIXES = (
    "ORGANS/",
    "SANCTUM/",
    "IMPERIUM_TEST_VERSION/",
    "THRONE/",
    "CUSTODES/",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Tool Admission V0.1 outputs.")
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
        / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/MECHANICUS_TOOL_ADMISSION_V0_1.md",
        "schema_candidate": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CANDIDATE_RECORD.schema.json",
        "schema_risk": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_RISK_RECORD.schema.json",
        "schema_decision": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_ADMISSION_DECISION.schema.json",
        "schema_capability": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_CAPABILITY_RECEIPT.schema.json",
        "schema_index": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/TOOL_REGISTRY_INDEX.schema.json",
        "sample": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TOOL_ADMISSION/samples/TOOL_ADMISSION_FOUNDATION.sample.json",
        "candidate_catalog": repo_root
        / "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CANDIDATE_CATALOG_V0_1.generated.json",
        "risk_catalog": repo_root
        / "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_RISK_CATALOG_V0_1.generated.json",
        "decisions_catalog": repo_root
        / "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_DECISIONS_V0_1.generated.json",
        "capability_catalog": repo_root
        / "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_CAPABILITY_REGISTRY_V0_1.generated.json",
        "index": repo_root
        / "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOL_ADMISSION/TOOL_ADMISSION_INDEX_V0_1.json",
        "builder": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_builder_v0_1.py",
        "validator": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/newgen_tool_admission_validator_v0_1.py",
        "gate_ack": report_dir / f"GATE_ACK_{task_id}.md",
        "officio_ack": report_dir / "OFFICIO_DOCTRINARIUM_AUTHORITY_ACK.json",
        "step_proof": report_dir / "STEP_PROOF_RECORDS.json",
        "validator_report": report_dir / "VALIDATOR_REPORT.json",
        "changed_files": report_dir / "CHANGED_FILES_STATUS.md",
        "closure_report": report_dir / "GIT_CLOSURE_REPORT.json",
        "final_receipt": report_dir / "FINAL_RECEIPT.json",
        "owner_report": report_dir / "OWNER_REPORT_RU.md",
        "kpd_review": report_dir / "AGENT_KPD_SELF_REVIEW.json",
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
    result: list[str] = []
    in_block = False
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


def contains_cyrillic(text: str) -> bool:
    return re.search(r"[А-Яа-яЁё]", text) is not None


def normalize_text(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False).lower()


def validate_candidates(candidates: Any) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not isinstance(candidates, list) or not candidates:
        return ["candidate catalog must be a non-empty list"], warnings

    present_names = {str(row.get("tool_name", "")).strip() for row in candidates if isinstance(row, dict)}
    for required_name in sorted(REQUIRED_TOOL_NAMES):
        if required_name not in present_names:
            blockers.append(f"missing required candidate tool: {required_name}")

    rich_present = any(
        isinstance(row, dict)
        and ("rich" in str(row.get("tool_name", "")).lower() or "textual" in str(row.get("tool_name", "")).lower())
        for row in candidates
    )
    if not rich_present:
        blockers.append("missing Rich/Textual CLI candidate")

    for idx, row in enumerate(candidates, start=1):
        if not isinstance(row, dict):
            blockers.append(f"candidate[{idx}] must be object")
            continue
        state = str(row.get("admission_state", "")).strip()
        if state not in ADMISSION_STATES:
            blockers.append(f"candidate[{idx}] invalid admission_state: {state}")
        if row.get("no_install_in_v0_1") is not True:
            blockers.append(f"candidate[{idx}] no_install_in_v0_1 must be true")
        if row.get("install_verified") is True:
            blockers.append(f"candidate[{idx}] install_verified must remain false in V0.1")
        if row.get("foundation_only") is not True:
            blockers.append(f"candidate[{idx}] foundation_only must be true")
        evidence = row.get("evidence_required_pre_admission")
        receipts = row.get("receipts_required_post_use")
        risks = row.get("risk_refs")
        if not isinstance(evidence, list) or not evidence:
            blockers.append(f"candidate[{idx}] evidence_required_pre_admission must be non-empty list")
        if not isinstance(receipts, list) or not receipts:
            blockers.append(f"candidate[{idx}] receipts_required_post_use must be non-empty list")
        if not isinstance(risks, list) or not risks:
            blockers.append(f"candidate[{idx}] risk_refs must be non-empty list")
        if state == "INSTALLED_AND_REGISTERED":
            blockers.append(f"candidate[{idx}] installed state is forbidden in foundation-only task")
        if state not in {"CANDIDATE_ONLY", "DEFERRED_NEEDS_ADMISSION_TASK"}:
            warnings.append(f"candidate[{idx}] uses non-default foundation state: {state}")
    return blockers, warnings


def validate_decisions(decisions: Any) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not isinstance(decisions, list) or not decisions:
        return ["decision catalog must be a non-empty list"], warnings

    for idx, row in enumerate(decisions, start=1):
        if not isinstance(row, dict):
            blockers.append(f"decision[{idx}] must be object")
            continue
        state = str(row.get("decision_state", "")).strip()
        if state not in ADMISSION_STATES:
            blockers.append(f"decision[{idx}] invalid decision_state: {state}")
        if row.get("install_allowed_now") is not False:
            blockers.append(f"decision[{idx}] install_allowed_now must be false in V0.1")
        if row.get("foundation_only") is not True:
            blockers.append(f"decision[{idx}] foundation_only must be true")
        evidence = row.get("evidence_refs")
        forbidden = row.get("forbidden_actions")
        if not isinstance(evidence, list) or not evidence:
            blockers.append(f"decision[{idx}] evidence_refs must be non-empty list")
        if not isinstance(forbidden, list) or not forbidden:
            blockers.append(f"decision[{idx}] forbidden_actions must be non-empty list")
        if state == "INSTALLED_AND_REGISTERED":
            blockers.append(f"decision[{idx}] installed decision is forbidden in foundation-only task")
        for action in forbidden if isinstance(forbidden, list) else []:
            if "install" in str(action).lower():
                break
        else:
            warnings.append(f"decision[{idx}] forbidden_actions does not explicitly mention install")
    return blockers, warnings


def validate_capabilities(capabilities: Any) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not isinstance(capabilities, list) or not capabilities:
        return ["capability registry must be a non-empty list"], warnings

    for idx, row in enumerate(capabilities, start=1):
        if not isinstance(row, dict):
            blockers.append(f"capability[{idx}] must be object")
            continue
        state = str(row.get("outcome_state", "")).strip()
        if state not in ADMISSION_STATES:
            blockers.append(f"capability[{idx}] invalid outcome_state: {state}")
        if row.get("no_install_performed") is not True:
            blockers.append(f"capability[{idx}] no_install_performed must be true")
        run_result = str(row.get("run_result", "")).strip()
        if run_result not in {"NOT_RUN", "WARN"}:
            warnings.append(f"capability[{idx}] run_result is uncommon for foundation task: {run_result}")
        if row.get("foundation_only") is not True:
            blockers.append(f"capability[{idx}] foundation_only must be true")
        evidence = row.get("evidence_paths")
        if not isinstance(evidence, list) or not evidence:
            blockers.append(f"capability[{idx}] evidence_paths must be non-empty list")
    return blockers, warnings


def validate_index(index_obj: Any) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []
    if not isinstance(index_obj, dict):
        return ["index file must be JSON object"], warnings
    if index_obj.get("phase") != 10:
        blockers.append("index phase must be 10")
    if index_obj.get("foundation_only") is not True:
        blockers.append("index foundation_only must be true")
    if index_obj.get("no_install") is not True:
        blockers.append("index no_install must be true")
    counts = index_obj.get("record_counts")
    if not isinstance(counts, dict):
        blockers.append("index record_counts must be object")
    else:
        for key in ("candidate_count", "risk_count", "decision_count", "capability_count"):
            value = counts.get(key)
            if not isinstance(value, int) or value <= 0:
                blockers.append(f"index record_counts.{key} must be positive integer")
    state_counts = index_obj.get("admission_state_counts")
    if not isinstance(state_counts, dict) or not state_counts:
        blockers.append("index admission_state_counts must be non-empty object")
    forbidden_claims = index_obj.get("forbidden_claims")
    if not isinstance(forbidden_claims, list) or not forbidden_claims:
        blockers.append("index forbidden_claims must be non-empty list")
    return blockers, warnings


def scan_forbidden_claims(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in FORBIDDEN_CLAIMS:
            if phrase in content:
                hits.append(f"{path.as_posix()} -> {phrase}")
    return hits


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
        "schema_candidate",
        "schema_risk",
        "schema_decision",
        "schema_capability",
        "schema_index",
        "sample",
        "candidate_catalog",
        "risk_catalog",
        "decisions_catalog",
        "capability_catalog",
        "index",
        "officio_ack",
        "step_proof",
        "closure_report",
        "final_receipt",
        "kpd_review",
    ]
    parse_errors: list[str] = []
    for key in parse_targets:
        path = paths[key]
        if not path.exists():
            continue
        try:
            read_json(path)
        except Exception as exc:  # noqa: BLE001
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
        paths["sample"],
        paths["candidate_catalog"],
        paths["risk_catalog"],
        paths["decisions_catalog"],
        paths["capability_catalog"],
        paths["index"],
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

    candidate_blockers: list[str] = []
    decision_blockers: list[str] = []
    capability_blockers: list[str] = []
    index_blockers: list[str] = []
    if not blockers:
        candidate_blockers, candidate_warnings = validate_candidates(read_json(paths["candidate_catalog"]))
        decision_blockers, decision_warnings = validate_decisions(read_json(paths["decisions_catalog"]))
        capability_blockers, capability_warnings = validate_capabilities(read_json(paths["capability_catalog"]))
        index_blockers, index_warnings = validate_index(read_json(paths["index"]))
        warnings.extend(candidate_warnings + decision_warnings + capability_warnings + index_warnings)
        blockers.extend(candidate_blockers + decision_blockers + capability_blockers + index_blockers)
    checks.append(
        {
            "check_id": "record_integrity_rules",
            "status": "PASS"
            if not (candidate_blockers or decision_blockers or capability_blockers or index_blockers)
            else "BLOCK",
            "details": "record integrity checks passed"
            if not (candidate_blockers or decision_blockers or capability_blockers or index_blockers)
            else "; ".join(candidate_blockers + decision_blockers + capability_blockers + index_blockers),
        }
    )

    forbidden_hits = scan_forbidden_claims(
        [
            paths["architecture_doc"],
            paths["sample"],
            paths["candidate_catalog"],
            paths["decisions_catalog"],
            paths["capability_catalog"],
            paths["owner_report"],
            paths["final_receipt"],
        ]
    )
    checks.append(
        {
            "check_id": "forbidden_claim_guard",
            "status": "PASS" if not forbidden_hits else "BLOCK",
            "details": "no forbidden claims found" if not forbidden_hits else "; ".join(forbidden_hits),
        }
    )
    blockers.extend([f"forbidden claim: {x}" for x in forbidden_hits])

    changed_paths = parse_changed_paths(paths["changed_files"])
    scope_hits: list[str] = []
    for changed in changed_paths:
        if not changed.startswith(ALLOWED_PREFIXES):
            scope_hits.append(f"outside_allowed:{changed}")
        if changed.startswith(FORBIDDEN_PREFIXES):
            scope_hits.append(f"forbidden_prefix:{changed}")
    checks.append(
        {
            "check_id": "scope_boundary_report",
            "status": "PASS" if not scope_hits else "BLOCK",
            "details": "changed files remain in allowed scope" if not scope_hits else "; ".join(scope_hits),
        }
    )
    blockers.extend(scope_hits)

    owner_report_ok = False
    if paths["owner_report"].exists():
        owner_report_ok = contains_cyrillic(paths["owner_report"].read_text(encoding="utf-8"))
    checks.append(
        {
            "check_id": "owner_report_ru_present",
            "status": "PASS" if owner_report_ok else "BLOCK",
            "details": "owner report contains Russian text"
            if owner_report_ok
            else "OWNER_REPORT_RU.md missing Cyrillic content",
        }
    )
    if not owner_report_ok:
        blockers.append("owner report RU check failed")

    step_proof_ok = False
    if paths["step_proof"].exists():
        proof_payload = read_json(paths["step_proof"])
        if isinstance(proof_payload, list) and proof_payload:
            required_keys = {
                "CLAIM",
                "BASIS",
                "RISK",
                "PROOF_PLAN",
                "ACTION",
                "SELF_VERDICT",
                "OWNER_RELEVANCE",
            }
            step_proof_ok = all(isinstance(x, dict) and required_keys.issubset(x.keys()) for x in proof_payload)
    checks.append(
        {
            "check_id": "super_skepticism_step_records",
            "status": "PASS" if step_proof_ok else "BLOCK",
            "details": "step proof records contain required skepticism keys"
            if step_proof_ok
            else "STEP_PROOF_RECORDS.json missing required skepticism fields",
        }
    )
    if not step_proof_ok:
        blockers.append("step proof skepticism fields check failed")

    verdict = "BLOCKED" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    report = {
        "schema_version": "0.1",
        "task_id": task_id,
        "validator": "newgen_tool_admission_validator_v0_1.py",
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": sorted(set(warnings)),
        "blockers": sorted(set(blockers)),
        "builder_command": (
            f"{sys.executable} IMPERIUM_NEW_GENERATION/TOOLS/TOOL_ADMISSION/"
            "newgen_tool_admission_builder_v0_1.py"
        ),
        "no_install_note": (
            "PASS/PASS_WITH_WARNINGS validates foundation-only admission artifacts. "
            "It is not proof of installed external toolchain readiness."
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path.as_posix())
    print(f"verdict={verdict}")
    return 1 if verdict == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
