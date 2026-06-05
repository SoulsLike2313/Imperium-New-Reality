#!/usr/bin/env python3
"""Administratum post-work closure updater v0.2."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ACTIVE_ROOT = "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True, indent=2) + "\n")


def resolve_repo_root(value: str) -> Path:
    root = Path(value or ".").resolve()
    markers = ["EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md"]
    if all((root / marker).is_file() for marker in markers):
        return root
    raise SystemExit(f"repo root missing New Reality markers: {to_posix(root)}")


def ensure_under(root: Path, path: Path) -> Path:
    resolved = path.resolve()
    if resolved == root or root in resolved.parents:
        return resolved
    raise SystemExit(f"path escapes repo root: {to_posix(resolved)}")


def git_text(repo_root: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def remote_head(repo_root: Path) -> str:
    code, out, _ = git_text(repo_root, "ls-remote", "origin", "refs/heads/master")
    if code != 0 or not out:
        return ""
    return out.split()[0]


def build_pre_commit(repo_root: Path, task_id: str, report_dir: Path, expected_commit_message: str) -> dict[str, Any]:
    _, head, _ = git_text(repo_root, "rev-parse", "HEAD")
    return {
        "schema_version": "administratum.post_work_closure_receipt.v0_2",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "mode": "PRE_COMMIT_SELF_REFERENCE",
        "repo_root": to_posix(repo_root),
        "report_dir": to_posix(report_dir),
        "pre_commit_head": head,
        "expected_commit_message": expected_commit_message,
        "post_push_head": "SELF_REFERENCE_BOUNDARY_PENDING_POST_PUSH_NO_WRITE_PROOF",
        "origin_master_head": remote_head(repo_root) or "REMOTE_HEAD_UNAVAILABLE_BEFORE_PUSH",
        "local_equals_origin": "PENDING_POST_PUSH_NO_WRITE_PROOF",
        "no_write_after_remote_proof": "PENDING_POST_PUSH_NO_WRITE_PROOF",
        "self_reference_boundary": "The final commit hash cannot be embedded into a file that is part of that same commit. Run no-write-proof after push."
    }


def build_no_write_proof(repo_root: Path, task_id: str, report_dir: Path, expected_commit_message: str) -> dict[str, Any]:
    _, head, _ = git_text(repo_root, "rev-parse", "HEAD")
    origin = remote_head(repo_root)
    _, status_short, _ = git_text(repo_root, "status", "--short", "--branch")
    _, porcelain, _ = git_text(repo_root, "status", "--porcelain=v1")
    return {
        "schema_version": "administratum.post_work_remote_no_write_proof.v0_2",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "mode": "POST_PUSH_NO_WRITE_PROOF",
        "repo_root": to_posix(repo_root),
        "report_dir": to_posix(report_dir),
        "pre_commit_head": "SEE_COMMITTED_REMOTE_CLOSURE_RECEIPT",
        "expected_commit_message": expected_commit_message,
        "post_push_head": head,
        "origin_master_head": origin,
        "local_equals_origin": bool(head and origin and head == origin),
        "no_write_after_remote_proof": True,
        "git_status_short_branch": status_short,
        "git_status_porcelain_v1": porcelain,
        "self_reference_boundary": "This proof is intentionally printed after push and not written into the committed tree."
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update or print post-work closure proof V0.2.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--expected-commit-message", default="Add post-work bundle admission ring v0.2 enforcement")
    parser.add_argument("--mode", choices=["pre-commit", "no-write-proof"], required=True)
    parser.add_argument("--out", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    if to_posix(repo_root) != ACTIVE_ROOT:
        raise SystemExit(f"active root mismatch: {to_posix(repo_root)}")
    report_dir = ensure_under(repo_root, repo_root / args.report_dir)
    if args.mode == "pre-commit":
        payload = build_pre_commit(repo_root, args.task_id, report_dir, args.expected_commit_message)
        if args.out:
            write_json(ensure_under(repo_root, repo_root / args.out), payload)
    else:
        payload = build_no_write_proof(repo_root, args.task_id, report_dir, args.expected_commit_message)
        if args.out:
            raise SystemExit("no-write-proof mode refuses --out to preserve no-write remote proof")
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 0 if payload.get("local_equals_origin") is not False else 2


if __name__ == "__main__":
    raise SystemExit(main())
