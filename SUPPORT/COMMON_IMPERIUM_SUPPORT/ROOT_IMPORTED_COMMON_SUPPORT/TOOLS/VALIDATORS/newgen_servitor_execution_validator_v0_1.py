#!/usr/bin/env python3
"""Validate NewGen Servitor run/rerun loop V0.1 foundation outputs."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-SERVITOR-RUN-RERUN-LOOP-PC-V0_1"
ALLOWED_SOURCE_TYPES = {
    "LIVE_AGENT_RESPONSE",
    "STATIC_FILE",
    "SAMPLE_PACKET",
    "FOUNDATION_STUB",
    "MISSING_IMPLEMENTATION_WARN",
}
FORBIDDEN_CLAIMS = [
    "production autonomous execution is ready",
    "live autonomous servitor execution is proven",
    "live 8-organ dialogue is proven",
    "fully production-ready orchestration",
]
FORBIDDEN_PREFIXES = ("ORGANS/", "SANCTUM/", "IMPERIUM_TEST_VERSION/", ".git/")


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
    parser = argparse.ArgumentParser(description="Validate Servitor run/rerun loop V0.1 outputs.")
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--out", default="")
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def contains_forbidden_claim(text: str) -> list[str]:
    lowered = text.lower()
    return [claim for claim in FORBIDDEN_CLAIMS if claim in lowered]


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
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            paths.append(path.replace("\\", "/"))
    return paths


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
        / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/SERVITOR_RUN_RERUN_LOOP_V0_1.md",
        "session_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SERVITOR_EXECUTION/SERVITOR_EXECUTION_SESSION_V0_1.schema.json",
        "run_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SERVITOR_EXECUTION/SERVITOR_RUN_RECORD_V0_1.schema.json",
        "rerun_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SERVITOR_EXECUTION/RERUN_DECISION_RECORD_V0_1.schema.json",
        "session_example": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/SERVITOR_EXECUTION/EXAMPLES/SAMPLE_SERVITOR_EXECUTION_SESSION_V0_1.json",
        "builder": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/SERVITOR_EXECUTION/newgen_servitor_execution_session_builder_v0_1.py",
        "validator": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/VALIDATORS/newgen_servitor_execution_validator_v0_1.py",
        "officio_ack": report / "OFFICIO_ROLE_ACK_OR_WARN.json",
        "doctr_ack": report / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        "proof_records": report / "STEP_PROOF_RECORDS.jsonl",
        "owner_report": report / "OWNER_REPORT_RU.md",
        "changed_files": report / "CHANGED_FILES_STATUS.md",
        "session_generated": report / "SERVITOR_EXECUTION_SESSION.generated.json",
        "run_generated": report / "RUN_RECORD_001.generated.json",
        "rerun_generated": report / "RERUN_DECISION_RECORD.generated.json",
        "final_receipt": report / "FINAL_RECEIPT.json",
        "validator_report": report / "VALIDATOR_REPORT.json",
    }


def validate_generated_shapes(
    session: dict[str, Any],
    run_record: dict[str, Any],
    rerun: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []

    session_required = [
        "schema_version",
        "session_id",
        "task_id",
        "status",
        "truth_level",
        "inputs",
        "organ_scope_summary",
        "run_plan",
        "no_fake_green_boundary",
    ]
    for key in session_required:
        if key not in session:
            errors.append(f"session missing required field: {key}")

    run_required = [
        "schema_version",
        "run_id",
        "session_id",
        "task_id",
        "run_index",
        "status",
        "checks",
        "failure_classification",
        "evidence",
    ]
    for key in run_required:
        if key not in run_record:
            errors.append(f"run record missing required field: {key}")

    rerun_required = [
        "schema_version",
        "decision_id",
        "session_id",
        "task_id",
        "decision",
        "reason",
        "next_action",
    ]
    for key in rerun_required:
        if key not in rerun:
            errors.append(f"rerun decision missing required field: {key}")

    no_fake = session.get("no_fake_green_boundary")
    if not isinstance(no_fake, dict):
        errors.append("session no_fake_green_boundary must be an object")
    else:
        may_not_claim = no_fake.get("may_not_claim")
        if not isinstance(may_not_claim, list) or not may_not_claim:
            errors.append("session no_fake_green_boundary.may_not_claim must be non-empty list")

    scope_summary = session.get("organ_scope_summary")
    if isinstance(scope_summary, dict):
        count = scope_summary.get("organ_count")
        if count is None:
            warns.append("session organ_scope_summary.organ_count is null")
        elif not isinstance(count, int):
            errors.append("session organ_scope_summary.organ_count must be integer or null")
    else:
        errors.append("session organ_scope_summary must be object")

    return errors, warns


def validate_scope_source_consistency(repo_root: Path, session: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []

    inputs = session.get("inputs")
    if not isinstance(inputs, list):
        errors.append("session inputs must be list")
        return errors, warns

    scope_path_text = None
    for item in inputs:
        if isinstance(item, dict) and str(item.get("kind")) == "organ_scope_merge_record":
            scope_path_text = str(item.get("path", "")).strip()
            break

    if not scope_path_text:
        errors.append("session inputs missing organ_scope_merge_record entry")
        return errors, warns

    scope_path = (repo_root / scope_path_text).resolve()
    if not scope_path.exists():
        warns.append("scope merge record path from session input does not exist")
        return errors, warns

    try:
        merge = read_json(scope_path)
        if not isinstance(merge, dict):
            errors.append("scope merge record is not JSON object")
            return errors, warns
    except Exception as exc:  # pragma: no cover
        errors.append(f"scope merge record parse error: {exc}")
        return errors, warns

    sources = merge.get("packet_sources")
    if not isinstance(sources, list):
        errors.append("scope merge record packet_sources must be list")
        return errors, warns

    organ_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            errors.append("scope merge record packet_sources contains non-object item")
            continue
        organ = str(source.get("organ_id", ""))
        source_type = str(source.get("source_type", ""))
        if organ:
            organ_ids.add(organ)
        if source_type not in ALLOWED_SOURCE_TYPES:
            errors.append(f"scope merge record has invalid source_type: {source_type}")
        if source_type == "LIVE_AGENT_RESPONSE":
            warns.append("LIVE_AGENT_RESPONSE detected; ensure explicit live receipts exist before production claims.")

    if len(organ_ids) != 8:
        warns.append(f"scope merge record organ coverage is {len(organ_ids)} instead of 8")

    return errors, sorted(set(warns))


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    task_id = args.task_id
    paths = required_paths(repo_root, task_id)
    out_path = Path(args.out).resolve() if args.out else paths["validator_report"]

    checks: list[CheckResult] = []
    warnings: list[str] = []
    blockers: list[str] = []

    missing = [f"{k}: {v.as_posix()}" for k, v in paths.items() if k != "validator_report" and not v.exists()]
    checks.append(
        CheckResult(
            "required_file_exists",
            "PASS" if not missing else "BLOCK",
            "all required files exist" if not missing else "; ".join(missing),
        )
    )
    if missing:
        blockers.extend(missing)

    json_targets = [
        paths["session_schema"],
        paths["run_schema"],
        paths["rerun_schema"],
        paths["session_example"],
        paths["officio_ack"],
        paths["doctr_ack"],
    ]
    parse_errors: list[str] = []
    for target in json_targets:
        if not target.exists():
            continue
        try:
            read_json(target)
        except Exception as exc:  # pragma: no cover
            parse_errors.append(f"{target.as_posix()}: {exc}")
    checks.append(
        CheckResult(
            "json_parseability",
            "PASS" if not parse_errors else "BLOCK",
            "json parse checks passed" if not parse_errors else "; ".join(parse_errors),
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
        str(paths["session_generated"].parent),
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

    gen_missing = [
        p.as_posix()
        for p in [paths["session_generated"], paths["run_generated"], paths["rerun_generated"]]
        if not p.exists()
    ]
    checks.append(
        CheckResult(
            "generated_outputs_exist",
            "PASS" if not gen_missing else "BLOCK",
            "generated files exist" if not gen_missing else "; ".join(gen_missing),
        )
    )
    if gen_missing:
        blockers.extend(["missing generated file: " + x for x in gen_missing])

    session_data: dict[str, Any] = {}
    run_data: dict[str, Any] = {}
    rerun_data: dict[str, Any] = {}
    if not blockers:
        session_data = read_json(paths["session_generated"])
        run_data = read_json(paths["run_generated"])
        rerun_data = read_json(paths["rerun_generated"])

        if not isinstance(session_data, dict) or not isinstance(run_data, dict) or not isinstance(rerun_data, dict):
            blockers.append("generated artifacts must be JSON objects")
        else:
            shape_errors, shape_warns = validate_generated_shapes(session_data, run_data, rerun_data)
            if shape_errors:
                blockers.extend(shape_errors)
            warnings.extend(shape_warns)

            scope_errors, scope_warns = validate_scope_source_consistency(repo_root, session_data)
            if scope_errors:
                blockers.extend(scope_errors)
            warnings.extend(scope_warns)

    checks.append(
        CheckResult(
            "generated_shape_and_loop_fields",
            "PASS" if not blockers else "BLOCK",
            "generated records have required run/rerun loop fields"
            if not blockers
            else "see blockers",
        )
    )

    fake_claim_hits: list[str] = []
    claim_targets = [paths["architecture_doc"], paths["owner_report"], paths["session_generated"], paths["run_generated"], paths["rerun_generated"]]
    for target in claim_targets:
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8", errors="ignore")
        for hit in contains_forbidden_claim(text):
            fake_claim_hits.append(f"{target.as_posix()}: {hit}")
    checks.append(
        CheckResult(
            "no_fake_green_claims",
            "PASS" if not fake_claim_hits else "BLOCK",
            "no forbidden fake-green claims detected"
            if not fake_claim_hits
            else "; ".join(fake_claim_hits),
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
            "no forbidden paths in git status"
            if not status_forbidden
            else "; ".join(status_forbidden),
        )
    )
    if status_forbidden:
        blockers.extend([f"forbidden path in git status: {x}" for x in status_forbidden])

    verdict = "BLOCK" if blockers else ("WARN" if warnings else "PASS")

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
            "PASS/WARN validates foundation artifact integrity only. "
            "It does not prove production autonomous Servitor execution."
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_path.as_posix())
    print(f"verdict={verdict}")
    return 1 if verdict == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
