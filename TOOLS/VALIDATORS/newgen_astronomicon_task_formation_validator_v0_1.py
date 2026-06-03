#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-ASTRONOMICON-TASK-FORMATION-PC-V0_1"
REQUIRED_ORGANS = {
    "ASTRONOMICON",
    "OFFICIO_AGENTIS",
    "DOCTRINARIUM",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
}
FORBIDDEN_PREFIXES = ("ORGANS/", "SANCTUM/", "IMPERIUM_TEST_VERSION/", ".git/")


@dataclass
class CheckResult:
    check_id: str
    status: str
    details: str

    def to_dict(self) -> dict[str, str]:
        return {
            "check_id": self.check_id,
            "status": self.status,
            "details": self.details,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate NewGen Astronomicon Task Formation V0.1")
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--formation-dir", default=None)
    parser.add_argument("--out", default=None)
    return parser.parse_args()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_porcelain_paths(repo_root: Path) -> list[str]:
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


def parse_changed_paths_report(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    capture = False
    changed: list[str] = []
    for raw in lines:
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


def required_paths(repo_root: Path, task_id: str) -> dict[str, Path]:
    report_root = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    return {
        "architecture_doc": repo_root
        / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/ASTRONOMICON_TASK_FORMATION_V0_1.md",
        "request_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/TASK_FORMATION_REQUEST_V0_1.schema.json",
        "record_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/TASK_FORMATION_RECORD_V0_1.schema.json",
        "stage_map_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/STAGE_MAP_PREVIEW_V0_1.schema.json",
        "sample_request": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/EXAMPLES/SAMPLE_OWNER_INTENT_REQUEST_V0_1.json",
        "sample_record": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ASTRONOMICON/EXAMPLES/SAMPLE_TASK_FORMATION_RECORD_V0_1.json",
        "task_former": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/ASTRONOMICON/newgen_astronomicon_task_former_v0_1.py",
        "validator": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/VALIDATORS/newgen_astronomicon_task_formation_validator_v0_1.py",
        "officio_ack_or_warn": report_root / "OFFICIO_ROLE_ACK_OR_WARN.json",
        "step_proof_records": report_root / "STEP_PROOF_RECORDS.jsonl",
        "owner_report": report_root / "OWNER_REPORT_RU.md",
        "changed_files_report": report_root / "CHANGED_FILES_STATUS.md",
    }


def validate_record_shape(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_fields = [
        "task_id",
        "owner_intent",
        "scope",
        "allowed_paths",
        "forbidden_paths",
        "required_organs",
        "stage_map_preview",
        "servitor_start_block",
        "limitations",
    ]
    for field in required_fields:
        if field not in record:
            errors.append(f"missing generated field: {field}")

    start_block = record.get("servitor_start_block")
    if isinstance(start_block, list):
        if not (2 <= len(start_block) <= 5):
            errors.append("servitor_start_block must contain 2-5 lines")
    else:
        errors.append("servitor_start_block must be list")

    required_organs = record.get("required_organs")
    if isinstance(required_organs, list):
        present = set(str(item) for item in required_organs)
        if present != REQUIRED_ORGANS:
            missing = sorted(REQUIRED_ORGANS.difference(present))
            extra = sorted(present.difference(REQUIRED_ORGANS))
            if missing:
                errors.append("required_organs missing: " + ", ".join(missing))
            if extra:
                errors.append("required_organs extra: " + ", ".join(extra))
    else:
        errors.append("required_organs must be list")

    limits = record.get("limitations")
    if isinstance(limits, list):
        combined = " ".join(str(item).lower() for item in limits)
        if "no live" not in combined and "foundation-only" not in combined:
            errors.append("limitations must include non-live/foundation statement")
    else:
        errors.append("limitations must be list")

    return errors


def live_claim_scan(text: str) -> list[str]:
    forbidden_claims = [
        "live multi-organ orchestration is ready",
        "production-ready orchestrator",
        "autonomous live runtime is implemented",
        "fully autonomous servitor orchestration",
    ]
    lowered = text.lower()
    return [claim for claim in forbidden_claims if claim in lowered]


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    task_id = args.task_id
    report_root = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    formation_dir = (
        Path(args.formation_dir).resolve()
        if args.formation_dir
        else report_root / "FORMATION_RUN"
    )
    out_path = (
        Path(args.out).resolve()
        if args.out
        else report_root / "VALIDATOR_REPORT.json"
    )

    paths = required_paths(repo_root, task_id)
    checks: list[CheckResult] = []
    failures: list[str] = []
    warnings: list[str] = []
    limitations = [
        "Validator performs deterministic structure checks and policy checks without external jsonschema engine."
    ]

    missing: list[str] = []
    for key, path in paths.items():
        if not path.exists():
            missing.append(f"missing {key}: {path.as_posix()}")
    checks.append(
        CheckResult(
            check_id="required_files_exist",
            status="PASS" if not missing else "FAIL",
            details="all required files found" if not missing else "; ".join(missing),
        )
    )
    if missing:
        failures.extend(missing)

    json_targets = [
        paths["request_schema"],
        paths["record_schema"],
        paths["stage_map_schema"],
        paths["sample_request"],
        paths["sample_record"],
        paths["officio_ack_or_warn"],
    ]
    parse_errors: list[str] = []
    for json_path in json_targets:
        if not json_path.exists():
            continue
        try:
            read_json(json_path)
        except Exception as exc:  # pragma: no cover
            parse_errors.append(f"{json_path.as_posix()}: {exc}")
    checks.append(
        CheckResult(
            check_id="json_parseability",
            status="PASS" if not parse_errors else "FAIL",
            details="all JSON artifacts parse" if not parse_errors else "; ".join(parse_errors),
        )
    )
    if parse_errors:
        failures.extend(parse_errors)

    formation_dir.mkdir(parents=True, exist_ok=True)
    generated_record = formation_dir / "TASK_FORMATION_RECORD_V0_1.generated.json"
    generated_report = formation_dir / "TASK_FORMATION_REPORT_V0_1.md"
    run_cmd = [
        sys.executable,
        str(paths["task_former"]),
        "--intent-file",
        str(paths["sample_request"]),
        "--out-dir",
        str(formation_dir),
    ]
    run_proc = subprocess.run(run_cmd, text=True, capture_output=True, check=False)
    run_ok = run_proc.returncode == 0
    checks.append(
        CheckResult(
            check_id="task_former_sample_run",
            status="PASS" if run_ok else "FAIL",
            details=(
                "sample formation run completed"
                if run_ok
                else f"returncode={run_proc.returncode}; stderr={run_proc.stderr.strip()}"
            ),
        )
    )
    if not run_ok:
        failures.append(
            "task former sample run failed: "
            + (run_proc.stderr.strip() or run_proc.stdout.strip() or "unknown error")
        )

    generated_missing: list[str] = []
    if not generated_record.exists():
        generated_missing.append(generated_record.as_posix())
    if not generated_report.exists():
        generated_missing.append(generated_report.as_posix())
    checks.append(
        CheckResult(
            check_id="generated_outputs_exist",
            status="PASS" if not generated_missing else "FAIL",
            details=(
                "generated record/report found"
                if not generated_missing
                else "; ".join(generated_missing)
            ),
        )
    )
    if generated_missing:
        failures.extend(["missing generated output: " + p for p in generated_missing])

    shape_errors: list[str] = []
    if generated_record.exists():
        try:
            generated_data = read_json(generated_record)
            if isinstance(generated_data, dict):
                shape_errors = validate_record_shape(generated_data)
            else:
                shape_errors = ["generated record must be JSON object"]
        except Exception as exc:  # pragma: no cover
            shape_errors = [f"generated record parse failed: {exc}"]
    checks.append(
        CheckResult(
            check_id="generated_record_required_fields",
            status="PASS" if not shape_errors else "FAIL",
            details=(
                "generated record contains required acceptance fields"
                if not shape_errors
                else "; ".join(shape_errors)
            ),
        )
    )
    if shape_errors:
        failures.extend(shape_errors)

    claim_errors: list[str] = []
    if generated_report.exists():
        report_text = generated_report.read_text(encoding="utf-8")
        hit = live_claim_scan(report_text)
        if hit:
            claim_errors.extend(hit)
        if "foundation-only" not in report_text.lower():
            warnings.append("generated markdown report should include explicit foundation-only phrase")
    checks.append(
        CheckResult(
            check_id="no_forbidden_live_claims_in_generated_report",
            status="PASS" if not claim_errors else "FAIL",
            details=(
                "no forbidden live-orchestration claims found"
                if not claim_errors
                else "; ".join(claim_errors)
            ),
        )
    )
    if claim_errors:
        failures.extend(["forbidden live claim: " + x for x in claim_errors])

    owner_claim_errors: list[str] = []
    if paths["owner_report"].exists():
        owner_text = paths["owner_report"].read_text(encoding="utf-8")
        owner_hits = live_claim_scan(owner_text)
        if owner_hits:
            owner_claim_errors.extend(owner_hits)
    else:
        warnings.append("owner report not found during validator run")
    checks.append(
        CheckResult(
            check_id="no_forbidden_live_claims_in_owner_report",
            status="PASS" if not owner_claim_errors else "FAIL",
            details=(
                "owner report has no forbidden live claims"
                if not owner_claim_errors
                else "; ".join(owner_claim_errors)
            ),
        )
    )
    if owner_claim_errors:
        failures.extend(["owner report forbidden live claim: " + x for x in owner_claim_errors])

    changed_report_paths = parse_changed_paths_report(paths["changed_files_report"])
    report_forbidden = forbidden_hits(changed_report_paths)
    checks.append(
        CheckResult(
            check_id="forbidden_paths_not_listed_in_changed_report",
            status="PASS" if not report_forbidden else "FAIL",
            details=(
                "no forbidden paths listed in changed files report"
                if not report_forbidden
                else "; ".join(report_forbidden)
            ),
        )
    )
    if report_forbidden:
        failures.extend([f"forbidden path in changed report: {item}" for item in report_forbidden])

    git_status_paths = parse_porcelain_paths(repo_root)
    status_forbidden = forbidden_hits(git_status_paths)
    checks.append(
        CheckResult(
            check_id="forbidden_paths_not_in_git_status",
            status="PASS" if not status_forbidden else "FAIL",
            details=(
                "no forbidden paths touched in git status"
                if not status_forbidden
                else "; ".join(status_forbidden)
            ),
        )
    )
    if status_forbidden:
        failures.extend([f"forbidden path in git status: {item}" for item in status_forbidden])

    status = "PASS"
    if failures:
        status = "BLOCK"
    elif warnings:
        status = "PASS_WITH_WARNINGS"

    report = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "validator": "newgen_astronomicon_task_formation_validator_v0_1.py",
        "repo_root": repo_root.as_posix(),
        "status": status,
        "checks": [check.to_dict() for check in checks],
        "failures": failures,
        "warnings": warnings,
        "limitations": limitations,
        "formation_dir": formation_dir.as_posix(),
        "generated_record_path": generated_record.as_posix(),
        "generated_report_path": generated_report.as_posix(),
        "task_former_command": " ".join(run_cmd),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out_path.as_posix())
    print(f"status={status}")
    return 0 if status in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
