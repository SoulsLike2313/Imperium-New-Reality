#!/usr/bin/env python3
"""Validate NewGen Task State + Evidence Binder V0.1 outputs."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-TASK-STATE-EVIDENCE-BINDER-PC-V0_1"
FORBIDDEN_PREFIXES = ("ORGANS/", "SANCTUM/", "IMPERIUM_TEST_VERSION/", ".git/")
FORBIDDEN_CLAIMS = [
    "production orchestration is ready",
    "live autonomous execution is proven",
    "live organ dialogue is proven",
    "production autonomous execution is ready",
]


@dataclass
class CheckResult:
    check_id: str
    status: str
    details: str

    def as_dict(self) -> dict[str, str]:
        return {"check_id": self.check_id, "status": self.status, "details": self.details}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Task State + Evidence Binder V0.1 outputs.")
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--out", default="")
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_changed_paths_report(path: Path) -> list[str]:
    if not path.exists():
        return []
    changed: list[str] = []
    capture = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line == "BEGIN_CHANGED_PATHS":
            capture = True
            continue
        if line == "END_CHANGED_PATHS":
            capture = False
            continue
        if capture and line:
            changed.append(line.replace("\\", "/"))
    return changed


def parse_git_status_paths(repo_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    result: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            result.append(path.replace("\\", "/"))
    return result


def forbidden_hits(paths: list[str]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        for prefix in FORBIDDEN_PREFIXES:
            if path.startswith(prefix):
                hits.append(path)
                break
    return sorted(set(hits))


def required_paths(repo_root: Path, task_id: str) -> dict[str, Path]:
    report = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    return {
        "architecture_doc": repo_root
        / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/TASK_STATE_EVIDENCE_BINDER_V0_1.md",
        "transition_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_EXECUTION_BINDINGS/TASK_STATE_TRANSITION_PROPOSAL_V0_1.schema.json",
        "evidence_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_EXECUTION_BINDINGS/EVIDENCE_REPLAY_INDEX_V0_1.schema.json",
        "transition_example": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_EXECUTION_BINDINGS/EXAMPLES/SAMPLE_TASK_STATE_TRANSITION_PROPOSAL_V0_1.json",
        "evidence_example": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_EXECUTION_BINDINGS/EXAMPLES/SAMPLE_EVIDENCE_REPLAY_INDEX_V0_1.json",
        "builder": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/TASK_EXECUTION_BINDINGS/newgen_task_state_evidence_binder_v0_1.py",
        "officio_ack": report / "OFFICIO_ROLE_ACK_OR_WARN.json",
        "doctr_ack": report / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        "skeptic_ack": report / "SUPER_SKEPTICISM_ACK.json",
        "gate_ack": report / "GATE_ACK.md",
        "proof_records": report / "STEP_PROOF_RECORDS.jsonl",
        "changed_files": report / "CHANGED_FILES_STATUS.md",
        "transition_generated": report / "TASK_STATE_TRANSITION_PROPOSAL.generated.json",
        "evidence_generated": report / "EVIDENCE_REPLAY_INDEX.generated.json",
        "final_receipt": report / "FINAL_RECEIPT.json",
        "owner_report": report / "OWNER_REPORT_RU.md",
        "validator_report": report / "VALIDATOR_REPORT.json",
    }


def validate_transition_payload(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    required = [
        "schema_version",
        "task_id",
        "source_records",
        "current_task_state",
        "proposed_task_state",
        "transition_reason",
        "failure_classification",
        "rerun_decision",
        "owner_escalation_required",
        "organ_escalation_required",
        "fake_green_risk",
        "evidence_index_ref",
        "confidence",
        "foundation_limitations",
        "created_at_utc",
    ]
    for key in required:
        if key not in data:
            errors.append(f"transition missing required field: {key}")

    fake_green = bool(data.get("fake_green_risk", False))
    if fake_green:
        errors.append("transition fake_green_risk=true")

    limitations = data.get("foundation_limitations")
    if not isinstance(limitations, list) or not limitations:
        errors.append("transition foundation_limitations must be non-empty list")
    else:
        limit_set = {str(x) for x in limitations}
        if "FOUNDATION_ONLY" not in limit_set:
            warns.append("transition foundation_limitations missing FOUNDATION_ONLY marker")
        if "NOT_PRODUCTION_EXECUTOR" not in limit_set:
            warns.append("transition foundation_limitations missing NOT_PRODUCTION_EXECUTOR marker")

    source_records = data.get("source_records")
    if not isinstance(source_records, list) or not source_records:
        errors.append("transition source_records must be non-empty list")
    else:
        allowed_statuses = {"READ", "MISSING", "READ_ERROR"}
        for idx, rec in enumerate(source_records, start=1):
            if not isinstance(rec, dict):
                errors.append(f"transition source_records[{idx}] must be object")
                continue
            status = str(rec.get("status", ""))
            if status not in allowed_statuses:
                errors.append(f"transition source_records[{idx}] invalid status: {status}")
    return errors, warns


def validate_evidence_payload(
    evidence: dict[str, Any],
    transition: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    required = [
        "schema_version",
        "task_id",
        "session_id",
        "run_ids",
        "rerun_decision_ids",
        "organ_packet_refs",
        "task_kernel_ref",
        "evidence_items",
        "replay_order",
        "missing_evidence",
        "truth_claims_allowed",
        "truth_claims_forbidden",
        "created_at_utc",
    ]
    for key in required:
        if key not in evidence:
            errors.append(f"evidence index missing required field: {key}")

    missing = evidence.get("missing_evidence")
    if not isinstance(missing, list):
        errors.append("evidence missing_evidence must be list")

    source_records = transition.get("source_records")
    if isinstance(source_records, list):
        has_missing_source = any(
            isinstance(x, dict) and str(x.get("status")) in {"MISSING", "READ_ERROR"} for x in source_records
        )
        if has_missing_source and isinstance(missing, list) and not missing:
            errors.append("evidence missing_evidence must be explicit when source records are missing/read_error")
        if (not has_missing_source) and isinstance(missing, list) and missing:
            warns.append("evidence missing_evidence present though all source records are READ")

    forbidden_claims = evidence.get("truth_claims_forbidden")
    if not isinstance(forbidden_claims, list) or not forbidden_claims:
        errors.append("evidence truth_claims_forbidden must be non-empty list")
    else:
        lowered = " | ".join(str(x).lower() for x in forbidden_claims)
        if "production orchestration is ready" not in lowered:
            warns.append("truth_claims_forbidden does not explicitly include production orchestration warning")

    allowed_claims = evidence.get("truth_claims_allowed")
    if isinstance(allowed_claims, list):
        allowed_lower = " | ".join(str(x).lower() for x in allowed_claims)
        for claim in FORBIDDEN_CLAIMS:
            if claim in allowed_lower:
                errors.append(f"truth_claims_allowed contains forbidden claim: {claim}")
    return errors, warns


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    task_id = args.task_id
    paths = required_paths(repo_root, task_id)
    out_path = Path(args.out).resolve() if args.out else paths["validator_report"]

    checks: list[CheckResult] = []
    warnings: list[str] = []
    blockers: list[str] = []

    missing_core = [f"{k}: {v.as_posix()}" for k, v in paths.items() if k != "validator_report" and not v.exists()]
    checks.append(
        CheckResult(
            "required_file_exists",
            "PASS" if not missing_core else "BLOCK",
            "all required files exist" if not missing_core else "; ".join(missing_core),
        )
    )
    if missing_core:
        blockers.extend(missing_core)

    parse_targets = [
        paths["transition_schema"],
        paths["evidence_schema"],
        paths["transition_example"],
        paths["evidence_example"],
        paths["officio_ack"],
        paths["doctr_ack"],
        paths["skeptic_ack"],
    ]
    parse_errors: list[str] = []
    for target in parse_targets:
        if not target.exists():
            continue
        try:
            read_json(target)
        except Exception as exc:  # pragma: no cover
            parse_errors.append(f"{target.as_posix()}: {exc}")
    checks.append(
        CheckResult(
            "json_and_schema_parse",
            "PASS" if not parse_errors else "BLOCK",
            "json/schema parse checks passed" if not parse_errors else "; ".join(parse_errors),
        )
    )
    if parse_errors:
        blockers.extend(parse_errors)

    builder_cmd = [
        sys.executable,
        str(paths["builder"]),
        "--repo-root",
        str(repo_root),
        "--task-id",
        task_id,
        "--out-dir",
        str(paths["transition_generated"].parent),
    ]
    run = subprocess.run(builder_cmd, text=True, capture_output=True, check=False)
    builder_ok = run.returncode == 0
    checks.append(
        CheckResult(
            "builder_run",
            "PASS" if builder_ok else "BLOCK",
            "builder generated outputs"
            if builder_ok
            else f"returncode={run.returncode}; stderr={run.stderr.strip()}",
        )
    )
    if not builder_ok:
        blockers.append("builder failed: " + (run.stderr.strip() or run.stdout.strip() or "unknown error"))

    generated_missing = [
        p.as_posix() for p in [paths["transition_generated"], paths["evidence_generated"]] if not p.exists()
    ]
    checks.append(
        CheckResult(
            "generated_outputs_exist",
            "PASS" if not generated_missing else "BLOCK",
            "generated outputs exist" if not generated_missing else "; ".join(generated_missing),
        )
    )
    if generated_missing:
        blockers.extend([f"missing generated file: {x}" for x in generated_missing])

    transition: dict[str, Any] = {}
    evidence_index: dict[str, Any] = {}
    if not blockers:
        transition_raw = read_json(paths["transition_generated"])
        evidence_raw = read_json(paths["evidence_generated"])
        if not isinstance(transition_raw, dict) or not isinstance(evidence_raw, dict):
            blockers.append("generated outputs must be JSON objects")
        else:
            transition = transition_raw
            evidence_index = evidence_raw
            transition_errors, transition_warns = validate_transition_payload(transition)
            evidence_errors, evidence_warns = validate_evidence_payload(evidence_index, transition)
            blockers.extend(transition_errors + evidence_errors)
            warnings.extend(transition_warns + evidence_warns)

    checks.append(
        CheckResult(
            "generated_shapes_and_no_fake_green",
            "PASS" if not blockers else "BLOCK",
            "generated payload checks passed" if not blockers else "see blockers",
        )
    )

    fake_claim_hits: list[str] = []
    if transition:
        transition_reason = str(transition.get("transition_reason", "")).lower()
        for claim in FORBIDDEN_CLAIMS:
            if claim in transition_reason:
                fake_claim_hits.append(f"transition_reason contains forbidden claim: {claim}")
    checks.append(
        CheckResult(
            "no_fake_green_claims",
            "PASS" if not fake_claim_hits else "BLOCK",
            "no fake-green claims found" if not fake_claim_hits else "; ".join(fake_claim_hits),
        )
    )
    if fake_claim_hits:
        blockers.extend(fake_claim_hits)

    changed_report_paths = parse_changed_paths_report(paths["changed_files"])
    report_forbidden = forbidden_hits(changed_report_paths)
    checks.append(
        CheckResult(
            "forbidden_paths_not_in_changed_report",
            "PASS" if not report_forbidden else "BLOCK",
            "no forbidden paths in changed files report"
            if not report_forbidden
            else "; ".join(report_forbidden),
        )
    )
    if report_forbidden:
        blockers.extend([f"forbidden path in changed report: {x}" for x in report_forbidden])

    status_forbidden = forbidden_hits(parse_git_status_paths(repo_root))
    checks.append(
        CheckResult(
            "forbidden_paths_not_in_git_status",
            "PASS" if not status_forbidden else "BLOCK",
            "no forbidden paths in git status" if not status_forbidden else "; ".join(status_forbidden),
        )
    )
    if status_forbidden:
        blockers.extend([f"forbidden path in git status: {x}" for x in status_forbidden])

    verdict = "BLOCKED" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    report = {
        "schema_version": "0.1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": [c.as_dict() for c in checks],
        "warnings": sorted(set(warnings)),
        "blockers": sorted(set(blockers)),
        "builder_command": " ".join(builder_cmd),
        "no_fake_green_note": (
            "PASS/WARN verifies bounded foundation integrity only. "
            "This is not proof of production autonomous execution."
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path.as_posix())
    print(f"verdict={verdict}")
    return 1 if verdict == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
