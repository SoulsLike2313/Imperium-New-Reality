#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260521-NEWGEN-ARCHITECTURE-SKILL-SPINE-PC-V0_1"

FORBIDDEN_PREFIXES = (
    "ORGANS/",
    "SANCTUM/",
    "IMPERIUM_TEST_VERSION/",
    "IMPERIUM_NEW_GENERATION/RUNS/",
    ".git/",
)


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
    parser = argparse.ArgumentParser(
        description="Validate required architecture and skill spine deliverables."
    )
    parser.add_argument("--repo-root", required=True, help="Absolute repository root path")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT, help="Task identifier")
    parser.add_argument("--output", default=None, help="Optional output JSON path")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_json_file(path: Path) -> tuple[bool, str]:
    try:
        json.loads(read_text(path))
    except Exception as exc:  # pragma: no cover
        return False, f"json parse failed: {exc}"
    return True, "ok"


def parse_porcelain_path(line: str) -> str | None:
    if len(line) < 4:
        return None
    raw = line[3:].strip()
    if not raw:
        return None
    if " -> " in raw:
        raw = raw.split(" -> ", 1)[1]
    return raw.replace("\\", "/")


def run_git_status_paths(repo_root: Path) -> list[str]:
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
        parsed = parse_porcelain_path(line)
        if parsed:
            paths.append(parsed)
    return paths


def parse_changed_paths_from_report(report_path: Path) -> list[str]:
    if not report_path.exists():
        return []

    lines = read_text(report_path).splitlines()
    changed: list[str] = []
    capture = False
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


def forbidden_hits(paths: list[str]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        normalized = path.lstrip("./")
        for prefix in FORBIDDEN_PREFIXES:
            if normalized.startswith(prefix):
                hits.append(normalized)
                break
    return sorted(set(hits))


def required_files(repo_root: Path, task_id: str) -> dict[str, Path]:
    base = Path("IMPERIUM_NEW_GENERATION")
    report_rel = base / "REPORTS" / task_id
    return {
        "architecture_map": repo_root / base / "ARCHITECTURE/NEWGEN_ARCHITECTURE_MAP_V0_1.md",
        "inventory_json": repo_root / base / "ARCHITECTURE/CURRENT_TREE_INVENTORY_V0_1.json",
        "mapping_doc": repo_root / base / "ARCHITECTURE/CURRENT_TO_TARGET_MAPPING_V0_1.md",
        "baseline_notes": repo_root / base / "ARCHITECTURE/FRONTEND_BACKEND_FULLSTACK_BASELINE_NOTES_V0_1.md",
        "super_skepticism": repo_root / base / "AUTHORITY_DRAFTS/SUPER_SKEPTICISM_MODE_V0_1.md",
        "proof_schema": repo_root / base / "CONTRACTS/AGENT_STEP_PROOF_RECORD.schema.json",
        "skill_schema": repo_root / base / "CONTRACTS/SKILL_PASSPORT.schema.json",
        "skill_template": repo_root / base / "SKILLS/SKILL_PASSPORT_TEMPLATE_V0_1.json",
        "skill_frontend": repo_root / base / "SKILLS/FRONTEND_SKILL_SPINE_V0_1.md",
        "skill_backend": repo_root / base / "SKILLS/BACKEND_SKILL_SPINE_V0_1.md",
        "skill_visual": repo_root / base / "SKILLS/VISUAL_FOUNDRY_SKILL_SPINE_V0_1.md",
        "skill_agent_general": repo_root / base / "SKILLS/AGENT_GENERAL_SKILL_SPINE_V0_1.md",
        "validator_script": repo_root / base / "TOOLS/VALIDATORS/newgen_architecture_validator_v0_1.py",
        "proof_records": repo_root / report_rel / "STEP_PROOF_RECORDS.jsonl",
        "changed_files_status": repo_root / report_rel / "CHANGED_FILES_STATUS.md",
        "owner_report_ru": repo_root / report_rel / "OWNER_REPORT_RU.md",
        "final_receipt": repo_root / report_rel / "FINAL_RECEIPT.json",
    }


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

    files = required_files(repo_root, task_id)
    checks: list[CheckResult] = []
    missing: list[str] = []

    for key, path in files.items():
        if not path.exists():
            missing.append(f"{key}: {path.as_posix()}")
    checks.append(
        CheckResult(
            check_id="required_file_presence",
            status="PASS" if not missing else "FAIL",
            details="all required files exist" if not missing else "; ".join(missing),
        )
    )

    officio_ack = (
        report_root
        / f"OFFICIO_ROLE_ACK_TASK-20260521-NEWGEN-ARCHITECTURE-SKILL-SPINE-PC-V0_1.json"
    )
    missing_warn = (
        report_root
        / f"MISSING_AUTHORITY_WARN_TASK-20260521-NEWGEN-ARCHITECTURE-SKILL-SPINE-PC-V0_1.json"
    )
    officio_ok = officio_ack.exists() or missing_warn.exists()
    checks.append(
        CheckResult(
            check_id="officio_gate_file_present",
            status="PASS" if officio_ok else "FAIL",
            details=(
                "OFFICIO_ROLE_ACK present"
                if officio_ack.exists()
                else "MISSING_AUTHORITY_WARN present"
                if missing_warn.exists()
                else "neither OFFICIO_ROLE_ACK nor MISSING_AUTHORITY_WARN exists"
            ),
        )
    )

    json_targets = [
        files["inventory_json"],
        files["proof_schema"],
        files["skill_schema"],
        files["skill_template"],
        files["final_receipt"],
        officio_ack if officio_ack.exists() else missing_warn,
    ]

    parse_failures: list[str] = []
    for path in json_targets:
        if not path.exists():
            parse_failures.append(f"missing: {path.as_posix()}")
            continue
        ok, msg = parse_json_file(path)
        if not ok:
            parse_failures.append(f"{path.as_posix()}: {msg}")
    checks.append(
        CheckResult(
            check_id="json_parseability",
            status="PASS" if not parse_failures else "FAIL",
            details="all JSON parse OK" if not parse_failures else "; ".join(parse_failures),
        )
    )

    changed_report_paths = parse_changed_paths_from_report(files["changed_files_status"])
    report_forbidden = forbidden_hits(changed_report_paths)
    checks.append(
        CheckResult(
            check_id="forbidden_paths_not_listed_in_changed_report",
            status="PASS" if not report_forbidden else "FAIL",
            details=(
                "no forbidden paths in CHANGED_FILES_STATUS"
                if not report_forbidden
                else "; ".join(report_forbidden)
            ),
        )
    )

    git_status_paths = run_git_status_paths(repo_root)
    diff_forbidden = forbidden_hits(git_status_paths)
    checks.append(
        CheckResult(
            check_id="forbidden_paths_not_in_git_status",
            status="PASS" if not diff_forbidden else "FAIL",
            details=(
                "no forbidden paths in git status"
                if not diff_forbidden
                else "; ".join(diff_forbidden)
            ),
        )
    )

    status = "PASS"
    if any(c.status == "FAIL" for c in checks):
        status = "FAIL"
    elif any(c.status == "WARN" for c in checks):
        status = "WARN"

    report: dict[str, Any] = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "repo_root": repo_root.as_posix(),
        "validator": "newgen_architecture_validator_v0_1.py",
        "status": status,
        "checks": [c.to_dict() for c in checks],
        "missing_files": missing,
        "json_parse_failures": parse_failures,
        "forbidden_paths_from_changed_report": report_forbidden,
        "forbidden_paths_from_git_status": diff_forbidden,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(output_path)
    print(f"status={status}")

    return 0 if status in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
