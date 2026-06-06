#!/usr/bin/env python3
"""Build a New Reality evidence index for a task report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


for candidate in Path(__file__).resolve().parents:
    if all((candidate / marker).is_file() for marker in ("EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md")):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        break

from ORGAN_AGENT_COMMON.root_resolution import resolve_new_reality_root, resolve_output_path  # noqa: E402


REMOTE_BRANCH = "master"
REQUIRED_RECEIPTS = [
    "preflight_truth_receipt.json",
    "repo_inventory.json",
    "classification_decision_ledger.json",
    "active_core_manifest.json",
    "active_reports_manifest.json",
    "candidate_review_manifest.json",
    "do_not_touch_manifest.json",
    "quarantine_manifest.json",
    "moved_files_receipt.json",
    "restore_instructions.md",
    "servitor_control_chain_receipt.json",
    "mechanicus_candidate_registry_summary.json",
    "remote_tree_bundle_closure_receipt.json",
    "no_ancient_mutation_receipt.json",
    "validation_run_receipt.json",
    "RED_TEAM_VERDICT.json",
    "CLAIM_LEDGER.json",
    "CAPABILITY_SPLIT_RECEIPT.json",
    "IMPERIUM_QUESTION_PASS.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "status": "PASS" if completed.returncode == 0 else "FAIL",
    }


def run_git(repo_root: Path, *args: str) -> dict[str, Any]:
    return run_command(["git", *args], repo_root)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_remote_head(stdout: str) -> str:
    wanted_ref = f"refs/heads/{REMOTE_BRANCH}"
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == wanted_ref:
            return parts[0]
    return ""


def build_index(repo_root: Path, task_id: str, report_dir: Path, bundle_name: str, out_name: str) -> dict[str, Any]:
    local_head = run_git(repo_root, "rev-parse", "HEAD")
    remote_probe = run_git(repo_root, "ls-remote", "origin", f"refs/heads/{REMOTE_BRANCH}")
    status = run_git(repo_root, "status", "--porcelain=v1")
    bundle_path = report_dir / bundle_name
    bundle_sha = sha256_file(bundle_path) if bundle_path.exists() else ""
    required = {
        name: {
            "path": to_posix(report_dir / name),
            "present": (report_dir / name).exists(),
        }
        for name in REQUIRED_RECEIPTS
    }
    missing = [name for name, item in required.items() if not item["present"]]
    payload = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "active_root": to_posix(repo_root),
        "final_head": local_head.get("stdout", ""),
        "remote_head": parse_remote_head(remote_probe.get("stdout", "")),
        "bundle_path": to_posix(bundle_path),
        "bundle_sha256": bundle_sha,
        "required_receipts": required,
        "missing_required_receipts": missing,
        "self_reference_limit": "Final exact commit proof requires a no-write post-push verification after the receipt commit.",
        "reviewer_gaps": [
            "Browser UI visibility is not claimed.",
            "Ancient Empire was not read because New Reality scope lock forbids parent-context access."
        ],
        "next_gate": "Run final closure proof and post-push remote HEAD equality verification.",
        "commands": {
            "local_head": local_head,
            "remote_probe": remote_probe,
            "status": status
        },
        "verdict": "PASS_WITH_WARNINGS" if bundle_sha and not missing else "BLOCK"
    }
    write_json(report_dir / out_name, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a New Reality task evidence index.")
    parser.add_argument("--repo-root", default="", help="Explicit New Reality root.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--bundle-name", default="task_report_bundle.zip")
    parser.add_argument("--out-name", default="evidence_index.json")
    args = parser.parse_args()

    repo_root = resolve_new_reality_root(args.repo_root or None, start=Path(__file__)).active_root
    report_dir = resolve_output_path(args.report_dir, repo_root)
    payload = build_index(repo_root, args.task_id, report_dir, args.bundle_name, args.out_name)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if not str(payload.get("verdict", "")).startswith("BLOCK") else 1


if __name__ == "__main__":
    raise SystemExit(main())

