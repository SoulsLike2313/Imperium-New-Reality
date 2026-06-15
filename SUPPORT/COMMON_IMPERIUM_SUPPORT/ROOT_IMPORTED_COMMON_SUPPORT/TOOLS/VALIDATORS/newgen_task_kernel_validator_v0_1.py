#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-TASK-KERNEL-REGISTRY-PC-V0_1"
REQUIRED_STATES = [
    "DRAFT",
    "REGISTERED",
    "SCOPING_WITH_ORGANS",
    "READY_FOR_SERVITOR",
    "RUNNING",
    "FAILED_NEEDS_RERUN",
    "BLOCKED_NEEDS_OWNER",
    "PASSED_WITH_WARNINGS",
    "PASSED_STRICT",
    "QUARANTINED",
    "CLOSED",
]
REQUIRED_KERNEL_FIELDS = [
    "task_id",
    "schema_version",
    "owner_intent",
    "task_title",
    "status",
    "created_at_utc",
    "scope",
    "allowed_paths",
    "forbidden_paths",
    "required_organs",
    "organ_packet_set_ref",
    "required_skills",
    "stage_map",
    "run_policy",
    "evidence_policy",
    "owner_questions",
    "final_bundle_policy",
    "truth_status",
    "limitations",
    "live_orchestration",
]
IN_SCOPE_ORGANS = {
    "ASTRONOMICON",
    "OFFICIO_AGENTIS",
    "DOCTRINARIUM",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
}
OUT_OF_SCOPE_ORGANS = {"THRONE", "CUSTODES"}
FORBIDDEN_PREFIXES = (
    "ORGANS/",
    "SANCTUM/",
    "IMPERIUM_TEST_VERSION/",
    "THRONE/",
    "CUSTODES/",
    ".git/",
)


@dataclass
class Check:
    check_id: str
    status: str
    details: str

    def as_dict(self) -> dict[str, str]:
        return {"check_id": self.check_id, "status": self.status, "details": self.details}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate NewGen Task Kernel Registry V0.1")
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--out", default=None)
    return parser.parse_args()


def parse_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_status_paths(repo_root: Path) -> list[str]:
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
    out: list[str] = []
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
            out.append(line.replace("\\", "/"))
    return out


def required_paths(repo_root: Path, task_id: str) -> dict[str, Path]:
    report = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    return {
        "architecture_doc": repo_root / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/TASK_KERNEL_REGISTRY_V0_1.md",
        "kernel_schema": repo_root / "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_KERNEL_V0_1.schema.json",
        "registry_schema": repo_root / "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_REGISTRY_INDEX_V0_1.schema.json",
        "state_machine_doc": repo_root / "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/TASK_STATE_MACHINE_V0_1.md",
        "sample_kernel": repo_root / "IMPERIUM_NEW_GENERATION/CONTRACTS/TASK_KERNEL/EXAMPLES/SAMPLE_TASK_KERNEL_OBJECT_V0_1.json",
        "registry_index": repo_root / "IMPERIUM_NEW_GENERATION/TASKS/REGISTRY/TASK_INDEX_V0_1.json",
        "validator_script": repo_root / "IMPERIUM_NEW_GENERATION/TOOLS/VALIDATORS/newgen_task_kernel_validator_v0_1.py",
        "officio_ack": report / "OFFICIO_ROLE_ACK_TASK-20260521-NEWGEN-TASK-KERNEL-REGISTRY-PC-V0_1.json",
        "officio_warn": report / "OFFICIO_ROLE_NOT_FOUND_WARN_TASK-20260521-NEWGEN-TASK-KERNEL-REGISTRY-PC-V0_1.json",
        "step_proof": report / "STEP_PROOF_RECORDS.jsonl",
        "changed_files": report / "CHANGED_FILES_STATUS.md",
        "final_receipt": report / "FINAL_RECEIPT.json",
        "owner_report": report / "OWNER_REPORT_RU.md",
    }


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    task_id = args.task_id
    report_root = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    out_path = Path(args.out).resolve() if args.out else report_root / "VALIDATOR_REPORT.json"

    paths = required_paths(repo_root, task_id)
    checks: list[Check] = []
    failures: list[str] = []
    warnings: list[str] = []
    limitations: list[str] = [
        "No external jsonschema engine; this validator performs deterministic structure checks only."
    ]

    missing: list[str] = []
    for key, path in paths.items():
        if key == "officio_warn":
            continue
        if key == "officio_ack":
            if not path.exists() and not paths["officio_warn"].exists():
                missing.append(
                    "missing officio ack or warn: "
                    + path.as_posix()
                    + " | "
                    + paths["officio_warn"].as_posix()
                )
            continue
        if not path.exists():
            missing.append(f"missing {key}: {path.as_posix()}")
    checks.append(
        Check(
            "required_file_existence",
            "PASS" if not missing else "FAIL",
            "all required files exist" if not missing else "; ".join(missing),
        )
    )
    if missing:
        failures.extend(missing)

    parsed: dict[str, Any] = {}
    json_targets = {
        "kernel_schema": paths["kernel_schema"],
        "registry_schema": paths["registry_schema"],
        "sample_kernel": paths["sample_kernel"],
        "registry_index": paths["registry_index"],
        "final_receipt": paths["final_receipt"],
    }
    if paths["officio_ack"].exists():
        json_targets["officio_ack"] = paths["officio_ack"]
    elif paths["officio_warn"].exists():
        json_targets["officio_warn"] = paths["officio_warn"]

    json_errors: list[str] = []
    for key, path in json_targets.items():
        try:
            parsed[key] = parse_json(path)
        except Exception as exc:  # pragma: no cover
            json_errors.append(f"{key} parse error: {exc}")
    checks.append(
        Check(
            "json_parseability",
            "PASS" if not json_errors else "FAIL",
            "all json files parse" if not json_errors else "; ".join(json_errors),
        )
    )
    if json_errors:
        failures.extend(json_errors)

    sample_errors: list[str] = []
    sample = parsed.get("sample_kernel")
    if isinstance(sample, dict):
        for field in REQUIRED_KERNEL_FIELDS:
            if field not in sample:
                sample_errors.append(f"sample missing field: {field}")
        if sample.get("schema_version") != "0.1":
            sample_errors.append("sample schema_version must be 0.1")
        if sample.get("live_orchestration") is not False:
            sample_errors.append("sample live_orchestration must be false")
        if sample.get("truth_status") == "LIVE_VERIFIED":
            sample_errors.append("sample truth_status must not be LIVE_VERIFIED")
        organs = sample.get("required_organs", [])
        if not isinstance(organs, list):
            sample_errors.append("sample required_organs must be list")
        else:
            missing_organs = sorted(IN_SCOPE_ORGANS.difference(set(organs)))
            if missing_organs:
                sample_errors.append("sample missing in-scope organs: " + ", ".join(missing_organs))
            present_out = sorted(OUT_OF_SCOPE_ORGANS.intersection(set(organs)))
            if present_out:
                sample_errors.append("sample includes out-of-scope organs: " + ", ".join(present_out))
    else:
        sample_errors.append("sample kernel object missing or invalid type")

    checks.append(
        Check(
            "sample_kernel_required_fields",
            "PASS" if not sample_errors else "FAIL",
            "sample fields and non-live guards valid"
            if not sample_errors
            else "; ".join(sample_errors),
        )
    )
    if sample_errors:
        failures.extend(sample_errors)

    state_errors: list[str] = []
    state_doc = paths["state_machine_doc"].read_text(encoding="utf-8")
    for state in REQUIRED_STATES:
        if state not in state_doc:
            state_errors.append(f"missing state in doc: {state}")
    checks.append(
        Check(
            "required_states_documented",
            "PASS" if not state_errors else "FAIL",
            "all required states present" if not state_errors else "; ".join(state_errors),
        )
    )
    if state_errors:
        failures.extend(state_errors)

    live_claim_errors: list[str] = []
    architecture_doc = paths["architecture_doc"].read_text(encoding="utf-8")
    if "does not claim live orchestration" not in architecture_doc.lower():
        warnings.append("architecture doc should explicitly mention non-live orchestration status")
    if sample and isinstance(sample, dict):
        limits = sample.get("limitations", [])
        if isinstance(limits, list):
            limits_join = " ".join(str(x).upper() for x in limits)
            if "NOT_LIVE" not in limits_join and "EXAMPLE_ONLY" not in limits_join:
                warnings.append("sample limitations should include NOT_LIVE or EXAMPLE_ONLY")
        else:
            live_claim_errors.append("sample limitations must be list")
    checks.append(
        Check(
            "no_live_orchestration_claim_guard",
            "PASS" if not live_claim_errors else "FAIL",
            "live claim guard satisfied" if not live_claim_errors else "; ".join(live_claim_errors),
        )
    )
    if live_claim_errors:
        failures.extend(live_claim_errors)

    changed_report_paths = parse_changed_paths_report(paths["changed_files"])
    report_forbidden = forbidden_hits(changed_report_paths)
    checks.append(
        Check(
            "forbidden_paths_not_in_changed_report",
            "PASS" if not report_forbidden else "FAIL",
            "no forbidden paths in report" if not report_forbidden else "; ".join(report_forbidden),
        )
    )
    if report_forbidden:
        failures.extend([f"forbidden path in changed report: {x}" for x in report_forbidden])

    git_status_paths = parse_status_paths(repo_root)
    status_forbidden = forbidden_hits(git_status_paths)
    checks.append(
        Check(
            "forbidden_paths_not_in_git_status",
            "PASS" if not status_forbidden else "FAIL",
            "no forbidden paths in git status" if not status_forbidden else "; ".join(status_forbidden),
        )
    )
    if status_forbidden:
        failures.extend([f"forbidden path in git status: {x}" for x in status_forbidden])

    status = "PASS_STRICT"
    if failures:
        status = "BLOCKED"
    elif warnings:
        status = "PASS_WITH_WARNINGS"

    report = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "validator": "newgen_task_kernel_validator_v0_1.py",
        "status": status,
        "failures": failures,
        "warnings": warnings,
        "limitations": limitations,
        "checks": [c.as_dict() for c in checks],
        "checked_paths": {k: v.as_posix() for k, v in paths.items() if k != "officio_warn"},
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(out_path)
    print(f"status={status}")

    return 0 if status in {"PASS_STRICT", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

