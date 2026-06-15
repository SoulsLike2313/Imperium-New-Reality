#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-ORGAN-PACKET-CONTRACT-PC-V0_1"
REQUIRED_ORGANS = [
    "ASTRONOMICON",
    "OFFICIO_AGENTIS",
    "DOCTRINARIUM",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]
OUT_OF_SCOPE_ORGANS = {"THRONE", "CUSTODES"}
STATUS_ENUM = {
    "READY",
    "READY_WITH_WARNINGS",
    "BLOCKED",
    "MISSING_AUTHORITY",
    "NOT_APPLICABLE",
    "EXAMPLE_ONLY",
}
LIVE_STATUS_ENUM = {"LIVE", "STUB", "EXAMPLE_ONLY", "NOT_IMPLEMENTED"}
CONFIDENCE_ENUM = {"PROVED", "STRONG", "PLAUSIBLE", "UNKNOWN", "FAILED", "FAKE_GREEN_RISK"}
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
    parser = argparse.ArgumentParser(description="Validate NewGen Organ Packet Contract V0.1")
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", default=None)
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
    for p in paths:
        for prefix in FORBIDDEN_PREFIXES:
            if p.startswith(prefix):
                hits.append(p)
                break
    return sorted(set(hits))


def parse_changed_paths_report(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    capture = False
    out: list[str] = []
    for raw in lines:
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
        "protocol_md": repo_root / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/ORGAN_PACKET_PROTOCOL_V0_1.md",
        "schema_packet": repo_root / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/ORGAN_PACKET_V0_1.schema.json",
        "schema_packet_set": repo_root / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/ORGAN_PACKET_SET_V0_1.schema.json",
        "catalog_md": repo_root / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/ORGAN_PACKET_RESPONSE_CATALOG_V0_1.md",
        "example_set": repo_root / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_PACKETS/EXAMPLES/SAMPLE_TASK_8_ORGAN_PACKET_SET_V0_1.json",
        "validator_py": repo_root / "IMPERIUM_NEW_GENERATION/TOOLS/VALIDATORS/newgen_organ_packet_contract_validator_v0_1.py",
        "officio_ack": report / "OFFICIO_ROLE_ACK_TASK-20260521-NEWGEN-ORGAN-PACKET-CONTRACT-PC-V0_1.json",
        "gate_ack": report / "GATE_ACK_TASK-20260521-NEWGEN-ORGAN-PACKET-CONTRACT-PC-V0_1.md",
        "step_proof": report / "STEP_PROOF_RECORDS.jsonl",
        "changed_files": report / "CHANGED_FILES_STATUS.md",
        "final_receipt": report / "FINAL_RECEIPT.json",
        "owner_report": report / "OWNER_REPORT_RU.md",
    }


def validate_packet_shape(packet: dict[str, Any], expected_task_id: str) -> list[str]:
    errors: list[str] = []
    required_keys = [
        "schema_version",
        "packet_id",
        "task_id",
        "organ_id",
        "packet_status",
        "live_status",
        "scope_advice",
        "required_inputs",
        "allowed_actions",
        "forbidden_actions",
        "required_checks",
        "evidence_required",
        "risks",
        "questions_for_owner",
        "questions_for_other_organs",
        "skill_requirements",
        "tool_requirements",
        "stop_conditions",
        "confidence",
        "proof",
    ]
    for key in required_keys:
        if key not in packet:
            errors.append(f"missing key: {key}")
    if errors:
        return errors

    if packet["schema_version"] != "0.1":
        errors.append("schema_version must be 0.1")
    if packet["task_id"] != expected_task_id:
        errors.append("task_id mismatch inside packet")
    if packet["organ_id"] not in REQUIRED_ORGANS:
        errors.append(f"organ_id out of scope: {packet['organ_id']}")
    if packet["packet_status"] not in STATUS_ENUM:
        errors.append(f"invalid packet_status: {packet['packet_status']}")
    if packet["live_status"] not in LIVE_STATUS_ENUM:
        errors.append(f"invalid live_status: {packet['live_status']}")
    if packet["confidence"] not in CONFIDENCE_ENUM:
        errors.append(f"invalid confidence: {packet['confidence']}")

    if packet["live_status"] == "LIVE":
        errors.append("LIVE status is not allowed for this contract-only task")

    proof = packet.get("proof")
    if not isinstance(proof, dict):
        errors.append("proof must be an object")
    else:
        for key in ("basis_paths", "basis_commands", "limitations"):
            if key not in proof or not isinstance(proof[key], list):
                errors.append(f"proof.{key} must be a list")

    list_fields = [
        "scope_advice",
        "required_inputs",
        "allowed_actions",
        "forbidden_actions",
        "required_checks",
        "evidence_required",
        "risks",
        "questions_for_owner",
        "questions_for_other_organs",
        "skill_requirements",
        "tool_requirements",
        "stop_conditions",
    ]
    for field in list_fields:
        if not isinstance(packet[field], list):
            errors.append(f"{field} must be a list")

    return errors


def validate_packet_set(example: dict[str, Any], task_id: str) -> list[str]:
    errors: list[str] = []
    required_top = [
        "schema_version",
        "set_id",
        "task_id",
        "set_live_status",
        "non_live_disclaimer",
        "organs_expected",
        "packets",
    ]
    for key in required_top:
        if key not in example:
            errors.append(f"missing top-level key: {key}")
    if errors:
        return errors

    if example["schema_version"] != "0.1":
        errors.append("top-level schema_version must be 0.1")
    if example["task_id"] != task_id:
        errors.append("top-level task_id mismatch")
    if example["set_live_status"] not in LIVE_STATUS_ENUM:
        errors.append("invalid set_live_status")
    if example["set_live_status"] == "LIVE":
        errors.append("set_live_status LIVE is not allowed for this task")

    disclaimer = str(example.get("non_live_disclaimer", "")).lower()
    if "not evidence" not in disclaimer and "example" not in disclaimer:
        errors.append("non_live_disclaimer must clearly state non-live status")

    organs_expected = example.get("organs_expected")
    packets = example.get("packets")
    if not isinstance(organs_expected, list):
        errors.append("organs_expected must be a list")
        organs_expected = []
    if not isinstance(packets, list):
        errors.append("packets must be a list")
        packets = []

    expected_sorted = sorted(REQUIRED_ORGANS)
    if sorted(organs_expected) != expected_sorted:
        errors.append("organs_expected must contain exactly the 8 in-scope organs")

    if len(packets) != 8:
        errors.append("packets must contain exactly 8 entries")

    packet_organs: list[str] = []
    for idx, packet in enumerate(packets):
        if not isinstance(packet, dict):
            errors.append(f"packet[{idx}] must be object")
            continue
        p_errors = validate_packet_shape(packet, task_id)
        for e in p_errors:
            errors.append(f"packet[{idx}] {e}")
        organ_id = str(packet.get("organ_id", ""))
        if organ_id:
            packet_organs.append(organ_id)
            if organ_id in OUT_OF_SCOPE_ORGANS:
                errors.append(f"packet[{idx}] out-of-scope organ present: {organ_id}")

    if sorted(packet_organs) != expected_sorted:
        errors.append("packet organ_id set must match exact 8 in-scope organs")
    if len(set(packet_organs)) != len(packet_organs):
        errors.append("duplicate organ_id detected in packets")

    return errors


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    task_id = args.task_id
    report_root = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    output_path = (
        Path(args.output).resolve()
        if args.output
        else report_root / "VALIDATOR_REPORT.json"
    )

    files = required_paths(repo_root, task_id)
    checks: list[CheckResult] = []

    missing = [f"{k}: {v.as_posix()}" for k, v in files.items() if not v.exists()]
    checks.append(
        CheckResult(
            "required_files_present",
            "PASS" if not missing else "FAIL",
            "all required files exist" if not missing else "; ".join(missing),
        )
    )

    json_targets = [
        files["schema_packet"],
        files["schema_packet_set"],
        files["example_set"],
        files["officio_ack"],
        files["final_receipt"],
    ]
    json_failures: list[str] = []
    parsed_example: dict[str, Any] | None = None
    for p in json_targets:
        if not p.exists():
            json_failures.append(f"missing: {p.as_posix()}")
            continue
        try:
            data = read_json(p)
            if p == files["example_set"] and isinstance(data, dict):
                parsed_example = data
        except Exception as exc:  # pragma: no cover
            json_failures.append(f"{p.as_posix()}: {exc}")
    checks.append(
        CheckResult(
            "json_parseability",
            "PASS" if not json_failures else "FAIL",
            "all JSON parse OK" if not json_failures else "; ".join(json_failures),
        )
    )

    packet_errors: list[str] = []
    if parsed_example is None:
        packet_errors.append("example packet set could not be parsed")
    else:
        packet_errors = validate_packet_set(parsed_example, task_id)
    checks.append(
        CheckResult(
            "example_packet_set_validation",
            "PASS" if not packet_errors else "FAIL",
            "packet set satisfies v0.1 constraints"
            if not packet_errors
            else "; ".join(packet_errors),
        )
    )

    changed_report_paths = parse_changed_paths_report(files["changed_files"])
    report_forbidden = forbidden_hits(changed_report_paths)
    checks.append(
        CheckResult(
            "forbidden_paths_not_in_changed_files_report",
            "PASS" if not report_forbidden else "FAIL",
            "no forbidden paths listed" if not report_forbidden else "; ".join(report_forbidden),
        )
    )

    status_paths = parse_porcelain_paths(repo_root)
    status_forbidden = forbidden_hits(status_paths)
    checks.append(
        CheckResult(
            "forbidden_paths_not_in_git_status",
            "PASS" if not status_forbidden else "FAIL",
            "no forbidden paths touched in git status"
            if not status_forbidden
            else "; ".join(status_forbidden),
        )
    )

    status = "PASS"
    if any(c.status == "FAIL" for c in checks):
        status = "FAIL"
    elif any(c.status == "WARN" for c in checks):
        status = "WARN"

    report = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "validator": "newgen_organ_packet_contract_validator_v0_1.py",
        "repo_root": repo_root.as_posix(),
        "status": status,
        "checks": [c.as_dict() for c in checks],
        "missing_files": missing,
        "json_failures": json_failures,
        "packet_validation_errors": packet_errors,
        "forbidden_paths_from_changed_files_report": report_forbidden,
        "forbidden_paths_from_git_status": status_forbidden,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(output_path)
    print(f"status={status}")

    return 0 if status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

