from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1"
MAX_SAMPLES_PER_RULE = 10
SCAN_ROOTS = ("IMPERIUM_NEW_GENERATION",)
PRUNE_DIR_NAMES = {".git", ".venv", "node_modules", ".mypy_cache", ".ruff_cache"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.strip()


def add_finding(
    findings: dict[str, dict[str, Any]],
    rule_id: str,
    relative_path: str,
    max_samples_per_rule: int = MAX_SAMPLES_PER_RULE,
) -> None:
    row = findings.setdefault(rule_id, {"count": 0, "samples": []})
    row["count"] = int(row["count"]) + 1
    samples = row["samples"]
    if len(samples) < max_samples_per_rule:
        samples.append(relative_path)


def scan_hygiene(repo_root: Path) -> dict[str, dict[str, Any]]:
    findings: dict[str, dict[str, Any]] = {}
    for root_rel in SCAN_ROOTS:
        root_path = (repo_root / root_rel).resolve()
        if not root_path.exists():
            continue
        for path in root_path.rglob("*"):
            if any(part in PRUNE_DIR_NAMES for part in path.parts):
                continue
            if path.is_dir():
                if path.name == "__pycache__":
                    rel = path.relative_to(repo_root).as_posix()
                    add_finding(findings, "PY_CACHE_DIR", rel)
                continue

            rel = path.relative_to(repo_root).as_posix()
            lower_name = path.name.lower()
            if lower_name.endswith(".pyc"):
                add_finding(findings, "PYC_FILE", rel)
            if lower_name.endswith(".log"):
                add_finding(findings, "LOG_FILE", rel)
            if lower_name.endswith(".tmp"):
                add_finding(findings, "TMP_FILE", rel)
            if lower_name == "server_pid.txt":
                add_finding(findings, "SERVER_PID_FILE", rel)
            normalized = rel.lower()
            if "inbox/taskpacks" in normalized:
                add_finding(findings, "TASKPACK_LEFTOVER_PATH", rel)
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report-only NewGen hygiene scan (no deletion).")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = (repo_root / output).resolve()

    findings = scan_hygiene(repo_root)
    total_hits = sum(int(item["count"]) for item in findings.values())
    verdict = "PASS" if total_hits == 0 else "WARN"

    status_short = run_git(repo_root, "status", "--short")
    status_lines = [line for line in status_short.splitlines() if line.strip()]
    tracked_dirty_count = sum(1 for line in status_lines if not line.startswith("??"))
    untracked_count = sum(1 for line in status_lines if line.startswith("??"))

    report = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "checker": "newgen_repo_hygiene_check_v0_1.py",
        "mode": "report_only_no_delete",
        "scan_roots": list(SCAN_ROOTS),
        "summary": {
            "findings_rule_count": len(findings),
            "total_hits": total_hits,
            "tracked_dirty_count": tracked_dirty_count,
            "untracked_count": untracked_count,
        },
        "findings": findings,
        "warnings": (
            ["hygiene_hits_found_report_only_mode"]
            if total_hits > 0
            else []
        ),
        "errors": [],
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
        "omitted_findings_count": 0,
    }
    write_json(output, report)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": verdict,
                "total_hits": total_hits,
                "tracked_dirty_count": tracked_dirty_count,
                "untracked_count": untracked_count,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
