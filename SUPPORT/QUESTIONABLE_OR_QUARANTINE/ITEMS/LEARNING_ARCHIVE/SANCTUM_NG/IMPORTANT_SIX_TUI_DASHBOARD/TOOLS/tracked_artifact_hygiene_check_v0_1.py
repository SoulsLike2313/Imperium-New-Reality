"""Tracked artifact hygiene checker for NewGen dashboard/report roots."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fnmatch
import json
from pathlib import Path
import subprocess
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def git_ls_files(repo_root: Path) -> list[str]:
    output = subprocess.check_output(
        ["git", "ls-files"],
        cwd=str(repo_root),
        text=True,
        encoding="utf-8",
    )
    return [line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()]


def scan_hygiene(
    repo_root: Path,
    scan_roots: list[str],
    forbidden_patterns: list[str],
    quarantine_root: str,
) -> dict[str, Any]:
    tracked_paths = git_ls_files(repo_root)

    forbidden_existing: list[dict[str, str]] = []
    forbidden_pending_deletions: list[dict[str, str]] = []
    for path in tracked_paths:
        if not any(path.startswith(root) for root in scan_roots):
            continue
        matched = next(
            (pattern for pattern in forbidden_patterns if fnmatch.fnmatch(path, pattern)),
            None,
        )
        if not matched:
            continue
        if (repo_root / path).exists():
            forbidden_existing.append({"path": path, "matched_pattern": matched})
        else:
            forbidden_pending_deletions.append({"path": path, "matched_pattern": matched})

    q_root_path = repo_root / quarantine_root
    quarantine_files: list[str] = []
    if q_root_path.exists():
        for item in q_root_path.rglob("*"):
            if item.is_file():
                quarantine_files.append(item.relative_to(repo_root).as_posix())

    verdict = "PASS" if not forbidden_existing else "WARN"
    return {
        "schema_id": "newgen_tracked_artifact_hygiene_report_v0_1",
        "generated_at_utc": utc_now(),
        "scan_scope": {
            "tracked_only": True,
            "roots": scan_roots,
            "forbidden_runtime_patterns": forbidden_patterns,
            "quarantine_root": f"{quarantine_root}/",
        },
        "verdict": verdict,
        "forbidden_existing_tracked_matches": forbidden_existing,
        "forbidden_existing_tracked_count": len(forbidden_existing),
        "forbidden_pending_deletion_count": len(forbidden_pending_deletions),
        "forbidden_pending_deletions": forbidden_pending_deletions,
        "quarantine_file_count": len(quarantine_files),
        "quarantine_file_sample": quarantine_files[:60],
        "notes": [
            "Pending deletions are expected before commit because removed runtime junk is still in git index until staged.",
            "PASS requires zero existing files matching forbidden runtime patterns under canonical roots.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--policy-json", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--scan-root",
        action="append",
        required=True,
        help="Root (repo-relative) to scan; repeat for multiple roots.",
    )
    parser.add_argument(
        "--quarantine-root",
        required=True,
        help="Repo-relative quarantine root.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    policy = load_json(args.policy_json.resolve())
    forbidden_patterns = policy.get("delete_runtime_junk_patterns", [])
    if not isinstance(forbidden_patterns, list):
        raise ValueError("delete_runtime_junk_patterns must be a list.")

    report = scan_hygiene(
        repo_root=repo_root,
        scan_roots=[root.replace("\\", "/") for root in args.scan_root],
        forbidden_patterns=[str(pattern) for pattern in forbidden_patterns],
        quarantine_root=args.quarantine_root.replace("\\", "/").rstrip("/"),
    )
    report["task_id"] = args.task_id

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output_path), "verdict": report["verdict"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
