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


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-8-ORGAN-SCOPING-CORRIDOR-PC-V0_1"
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
FORBIDDEN_LIVE_CLAIMS = [
    "servitor now live-talks to all organs autonomously in production",
    "live autonomous cross-organ runtime is implemented",
    "production live multi-agent runtime is ready",
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
    parser = argparse.ArgumentParser(description="Validate NewGen 8-organ scoping corridor bundle.")
    parser.add_argument("--repo-root", default="E:\\IMPERIUM")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--out", default=None)
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


def contains_forbidden_live_claim(text: str) -> list[str]:
    lowered = text.lower()
    return [claim for claim in FORBIDDEN_LIVE_CLAIMS if claim in lowered]


def required_paths(repo_root: Path, task_id: str) -> dict[str, Path]:
    report_root = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    return {
        "architecture_doc": repo_root
        / "IMPERIUM_NEW_GENERATION/ARCHITECTURE/EIGHT_ORGAN_SCOPING_CORRIDOR_V0_1.md",
        "request_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_SCOPING/ORGAN_SCOPE_REQUEST_V0_1.schema.json",
        "merge_schema": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_SCOPING/ORGAN_SCOPE_MERGE_RECORD_V0_1.schema.json",
        "example_request": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_SCOPING/EXAMPLES/SAMPLE_ORGAN_SCOPE_REQUEST_V0_1.json",
        "example_merge": repo_root
        / "IMPERIUM_NEW_GENERATION/CONTRACTS/ORGAN_SCOPING/EXAMPLES/SAMPLE_ORGAN_SCOPE_MERGE_RECORD_V0_1.json",
        "collector_tool": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/ORGAN_SCOPING/newgen_8_organ_scope_collector_v0_1.py",
        "validator_tool": repo_root
        / "IMPERIUM_NEW_GENERATION/TOOLS/VALIDATORS/newgen_8_organ_scoping_validator_v0_1.py",
        "officio_ack": report_root / "OFFICIO_ROLE_ACK_OR_WARN.json",
        "doctr_ack": report_root / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        "proof_records": report_root / "STEP_PROOF_RECORDS.jsonl",
        "scope_request_generated": report_root / "SCOPE_REQUEST.generated.json",
        "organ_packets_generated": report_root / "ORGAN_PACKETS.generated.json",
        "merge_generated": report_root / "ORGAN_SCOPE_MERGE_RECORD.generated.json",
        "changed_files": report_root / "CHANGED_FILES_STATUS.md",
        "owner_report": report_root / "OWNER_REPORT_RU.md",
    }


def validate_coverage(generated_request: dict[str, Any], generated_merge: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    req_organs = generated_request.get("required_organs")
    if not isinstance(req_organs, list):
        errors.append("generated scope request required_organs must be a list")
    else:
        req_set = {str(item) for item in req_organs}
        if req_set != REQUIRED_ORGANS:
            missing = sorted(REQUIRED_ORGANS.difference(req_set))
            extra = sorted(req_set.difference(REQUIRED_ORGANS))
            if missing:
                errors.append("generated scope request missing organs: " + ", ".join(missing))
            if extra:
                errors.append("generated scope request extra organs: " + ", ".join(extra))

    packet_sources = generated_merge.get("packet_sources")
    if not isinstance(packet_sources, list):
        errors.append("generated merge packet_sources must be list")
    else:
        source_organs = {str(item.get("organ_id", "")) for item in packet_sources if isinstance(item, dict)}
        if source_organs != REQUIRED_ORGANS:
            missing = sorted(REQUIRED_ORGANS.difference(source_organs))
            extra = sorted(source_organs.difference(REQUIRED_ORGANS))
            if missing:
                errors.append("generated merge missing packet sources for organs: " + ", ".join(missing))
            if extra:
                errors.append("generated merge has out-of-scope packet sources: " + ", ".join(extra))

        for item in packet_sources:
            if not isinstance(item, dict):
                errors.append("generated merge packet_sources contains non-object entry")
                continue
            source_type = str(item.get("source_type", ""))
            if source_type not in {
                "LIVE_AGENT_RESPONSE",
                "STATIC_FILE",
                "SAMPLE_PACKET",
                "FOUNDATION_STUB",
                "MISSING_IMPLEMENTATION_WARN",
            }:
                errors.append(f"invalid source_type in generated merge: {source_type}")

    return errors


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    task_id = args.task_id
    report_root = repo_root / "IMPERIUM_NEW_GENERATION" / "REPORTS" / task_id
    out_path = Path(args.out).resolve() if args.out else report_root / "VALIDATOR_REPORT.json"

    paths = required_paths(repo_root, task_id)
    checks: list[CheckResult] = []
    failures: list[str] = []
    warnings: list[str] = []

    missing = [f"{k}: {v.as_posix()}" for k, v in paths.items() if not v.exists()]
    checks.append(
        CheckResult(
            "required_files_exist",
            "PASS" if not missing else "FAIL",
            "all required files exist" if not missing else "; ".join(missing),
        )
    )
    if missing:
        failures.extend(missing)

    json_targets = [
        paths["request_schema"],
        paths["merge_schema"],
        paths["example_request"],
        paths["example_merge"],
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
            "PASS" if not parse_errors else "FAIL",
            "JSON parseability checks passed" if not parse_errors else "; ".join(parse_errors),
        )
    )
    if parse_errors:
        failures.extend(parse_errors)

    collector_cmd = [
        sys.executable,
        str(paths["collector_tool"]),
        "--repo-root",
        str(repo_root),
        "--task-id",
        task_id,
        "--out-dir",
        str(report_root),
    ]
    run_proc = subprocess.run(collector_cmd, text=True, capture_output=True, check=False)
    collector_ok = run_proc.returncode == 0
    checks.append(
        CheckResult(
            "collector_run",
            "PASS" if collector_ok else "FAIL",
            "collector generated outputs"
            if collector_ok
            else f"returncode={run_proc.returncode}; stderr={run_proc.stderr.strip()}",
        )
    )
    if not collector_ok:
        failures.append(
            "collector run failed: "
            + (run_proc.stderr.strip() or run_proc.stdout.strip() or "unknown error")
        )

    generated_missing = [
        p.as_posix()
        for p in [
            paths["scope_request_generated"],
            paths["organ_packets_generated"],
            paths["merge_generated"],
        ]
        if not p.exists()
    ]
    checks.append(
        CheckResult(
            "generated_outputs_exist",
            "PASS" if not generated_missing else "FAIL",
            "all generated outputs exist"
            if not generated_missing
            else "; ".join(generated_missing),
        )
    )
    if generated_missing:
        failures.extend(["missing generated output: " + x for x in generated_missing])

    coverage_errors: list[str] = []
    if paths["scope_request_generated"].exists() and paths["merge_generated"].exists():
        try:
            generated_request = read_json(paths["scope_request_generated"])
            generated_merge = read_json(paths["merge_generated"])
            if isinstance(generated_request, dict) and isinstance(generated_merge, dict):
                coverage_errors = validate_coverage(generated_request, generated_merge)
                readiness = str(generated_merge.get("readiness", ""))
                if readiness not in {"READY", "READY_WITH_WARNINGS", "BLOCKED", "FOUNDATION_ONLY"}:
                    coverage_errors.append(f"invalid readiness in generated merge: {readiness}")
            else:
                coverage_errors.append("generated outputs must be JSON objects")
        except Exception as exc:  # pragma: no cover
            coverage_errors.append(f"generated output parse failed: {exc}")
    checks.append(
        CheckResult(
            "eight_organ_coverage_and_merge_shape",
            "PASS" if not coverage_errors else "FAIL",
            "8-organ coverage checks passed" if not coverage_errors else "; ".join(coverage_errors),
        )
    )
    if coverage_errors:
        failures.extend(coverage_errors)

    live_claim_failures: list[str] = []
    for path in [paths["architecture_doc"], paths["owner_report"], paths["merge_generated"]]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        hit = contains_forbidden_live_claim(text)
        if hit:
            live_claim_failures.extend([f"{path.as_posix()}: {h}" for h in hit])
    checks.append(
        CheckResult(
            "no_forbidden_live_claims",
            "PASS" if not live_claim_failures else "FAIL",
            "no forbidden live claims detected"
            if not live_claim_failures
            else "; ".join(live_claim_failures),
        )
    )
    if live_claim_failures:
        failures.extend(live_claim_failures)

    if paths["merge_generated"].exists():
        merge_text = paths["merge_generated"].read_text(encoding="utf-8", errors="ignore").lower()
        if "live_agent_response" in merge_text:
            warnings.append(
                "generated merge includes LIVE_AGENT_RESPONSE source type; ensure this is backed by real receipts."
            )

    changed_report_paths = parse_changed_paths_report(paths["changed_files"])
    report_forbidden = forbidden_hits(changed_report_paths)
    checks.append(
        CheckResult(
            "forbidden_paths_not_in_changed_files_report",
            "PASS" if not report_forbidden else "FAIL",
            "no forbidden paths listed" if not report_forbidden else "; ".join(report_forbidden),
        )
    )
    if report_forbidden:
        failures.extend(["forbidden path in changed report: " + x for x in report_forbidden])

    git_status_forbidden = forbidden_hits(parse_git_status_paths(repo_root))
    checks.append(
        CheckResult(
            "forbidden_paths_not_in_git_status",
            "PASS" if not git_status_forbidden else "FAIL",
            "no forbidden paths touched in git status"
            if not git_status_forbidden
            else "; ".join(git_status_forbidden),
        )
    )
    if git_status_forbidden:
        failures.extend(["forbidden path in git status: " + x for x in git_status_forbidden])

    status = "PASS"
    if failures:
        status = "BLOCK"
    elif warnings:
        status = "PASS_WITH_WARNINGS"

    report = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "validator": "newgen_8_organ_scoping_validator_v0_1.py",
        "repo_root": repo_root.as_posix(),
        "status": status,
        "checks": [c.as_dict() for c in checks],
        "failures": failures,
        "warnings": warnings,
        "collector_command": " ".join(collector_cmd),
        "generated_outputs": [
            paths["scope_request_generated"].as_posix(),
            paths["organ_packets_generated"].as_posix(),
            paths["merge_generated"].as_posix(),
        ],
        "limitations": [
            "Validator performs deterministic structure checks without external jsonschema engine."
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out_path.as_posix())
    print(f"status={status}")

    return 0 if status in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
