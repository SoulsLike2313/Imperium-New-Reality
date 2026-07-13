"""Measured Git base-to-result diff for the Core Reference Corridor.

This module deliberately separates committed-range truth from working-tree dirt.
A clean worktree does not imply that base_head and result_head are identical.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "imperium.real_diff.v1"
PASS_VERDICT = "REAL_DIFF_REVIEW_PROVEN"
_SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")


class GitFailure(RuntimeError):
    """Raised when a required Git measurement cannot be completed."""


def _run_git(root: Path, *args: str, binary: bool = False, timeout: int = 30) -> bytes | str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        shell=False,
        capture_output=True,
        text=not binary,
        encoding=None if binary else "utf-8",
        errors=None if binary else "replace",
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace") if binary else completed.stderr
        raise GitFailure(f"git {' '.join(args)} failed: {stderr.strip()}")
    return completed.stdout


def _verify_commit(root: Path, ref: str) -> str:
    if not ref or not _SHA40.fullmatch(ref):
        raise GitFailure("base_head must be a full 40-character hexadecimal commit id")
    resolved = str(_run_git(root, "rev-parse", "--verify", f"{ref}^{{commit}}")).strip()
    if not _SHA40.fullmatch(resolved):
        raise GitFailure("resolved commit id is invalid")
    return resolved.lower()


def _status(root: Path) -> list[str]:
    raw = str(_run_git(root, "status", "--porcelain=v1", "-z"))
    return [entry for entry in raw.split("\0") if entry]


def _parse_name_status(payload: bytes) -> list[dict[str, Any]]:
    tokens = [part.decode("utf-8", errors="surrogateescape") for part in payload.split(b"\0") if part]
    files: list[dict[str, Any]] = []
    index = 0
    while index < len(tokens):
        status_token = tokens[index]
        index += 1
        code = status_token[:1] or "?"
        similarity = status_token[1:] or None
        if code in {"R", "C"}:
            if index + 1 >= len(tokens):
                raise GitFailure("truncated rename/copy name-status payload")
            old_path = tokens[index]
            path = tokens[index + 1]
            index += 2
        else:
            if index >= len(tokens):
                raise GitFailure("truncated name-status payload")
            old_path = None
            path = tokens[index]
            index += 1
        files.append(
            {
                "path": path,
                "old_path": old_path,
                "status": code,
                "similarity": int(similarity) if similarity and similarity.isdigit() else None,
                "insertions": 0,
                "deletions": 0,
                "binary": False,
            }
        )
    return files


def _parse_numstat(payload: bytes) -> dict[tuple[str | None, str], dict[str, Any]]:
    tokens = payload.split(b"\0")
    index = 0
    result: dict[tuple[str | None, str], dict[str, Any]] = {}
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token:
            continue
        text = token.decode("utf-8", errors="surrogateescape")
        parts = text.split("\t", 2)
        if len(parts) != 3:
            raise GitFailure("invalid numstat payload")
        added_raw, deleted_raw, path = parts
        old_path: str | None = None
        if path == "":
            if index + 1 >= len(tokens):
                raise GitFailure("truncated rename/copy numstat payload")
            old_path = tokens[index].decode("utf-8", errors="surrogateescape")
            path = tokens[index + 1].decode("utf-8", errors="surrogateescape")
            index += 2
        binary = added_raw == "-" or deleted_raw == "-"
        result[(old_path, path)] = {
            "insertions": 0 if binary else int(added_raw),
            "deletions": 0 if binary else int(deleted_raw),
            "binary": binary,
        }
    return result


def _empty_result(base_head: str, worktree: Path, reality: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "verdict": "NOT_PROVEN",
        "errors": [],
        "base_head_requested": base_head,
        "base_head": None,
        "result_head": None,
        "merge_base": None,
        "ahead_count": 0,
        "behind_count": 0,
        "files_changed": 0,
        "insertions": 0,
        "deletions": 0,
        "binary_files": 0,
        "renamed_files": 0,
        "files": [],
        "files_truncated": False,
        "patch_available": False,
        "patch_preview": "",
        "patch_preview_truncated": False,
        "patch_sha256": None,
        "worktree_root": str(worktree),
        "worktree_dirty_count": 0,
        "worktree_status": [],
        "reality_root": str(reality),
        "reality_head": None,
        "reality_dirty_count": 0,
        "reality_status": [],
        "committed_range_proven": False,
    }


def build_real_diff(
    worktree_root: Path | str,
    reality_root: Path | str,
    base_head: str,
    *,
    file_limit: int = 200,
    patch_preview_limit: int = 12_000,
) -> dict[str, Any]:
    """Measure committed base-to-result changes and separate dirty state.

    Failures are returned as explicit BLOCK/NOT_PROVEN verdicts; callers never
    need to infer success from an empty list or clean worktree.
    """

    worktree = Path(worktree_root).resolve()
    reality = Path(reality_root).resolve()
    result = _empty_result(base_head, worktree, reality)

    try:
        result["worktree_status"] = _status(worktree)
        result["worktree_dirty_count"] = len(result["worktree_status"])
        result["reality_status"] = _status(reality)
        result["reality_dirty_count"] = len(result["reality_status"])
        result["reality_head"] = str(_run_git(reality, "rev-parse", "HEAD")).strip().lower()

        verified_base = _verify_commit(worktree, base_head)
        result_head = str(_run_git(worktree, "rev-parse", "HEAD^{commit}")).strip().lower()
        merge_base = str(_run_git(worktree, "merge-base", verified_base, result_head)).strip().lower()
        result.update(base_head=verified_base, result_head=result_head, merge_base=merge_base)

        if merge_base != verified_base:
            result["verdict"] = "BLOCK_BASE_NOT_ANCESTOR"
            result["errors"].append("base_head is not an ancestor of result_head")
            return result

        left_right = str(_run_git(worktree, "rev-list", "--left-right", "--count", f"{verified_base}...{result_head}")).strip().split()
        if len(left_right) != 2:
            raise GitFailure("invalid ahead/behind measurement")
        result["behind_count"] = int(left_right[0])
        result["ahead_count"] = int(left_right[1])

        names_payload = _run_git(
            worktree,
            "diff",
            "--find-renames",
            "--find-copies",
            "--name-status",
            "-z",
            verified_base,
            result_head,
            "--",
            binary=True,
        )
        numstat_payload = _run_git(
            worktree,
            "diff",
            "--find-renames",
            "--find-copies",
            "--numstat",
            "-z",
            verified_base,
            result_head,
            "--",
            binary=True,
        )
        files = _parse_name_status(names_payload)
        numstats = _parse_numstat(numstat_payload)
        for item in files:
            stats = numstats.get((item["old_path"], item["path"])) or numstats.get((None, item["path"]))
            if stats:
                item.update(stats)

        result["files_changed"] = len(files)
        result["insertions"] = sum(int(item["insertions"]) for item in files)
        result["deletions"] = sum(int(item["deletions"]) for item in files)
        result["binary_files"] = sum(1 for item in files if item["binary"])
        result["renamed_files"] = sum(1 for item in files if item["status"] == "R")
        result["files_truncated"] = len(files) > file_limit
        result["files"] = files[:file_limit]

        patch = _run_git(
            worktree,
            "diff",
            "--find-renames",
            "--find-copies",
            "--no-ext-diff",
            "--no-color",
            "--unified=3",
            verified_base,
            result_head,
            "--",
            binary=True,
            timeout=60,
        )
        result["patch_available"] = bool(patch)
        result["patch_sha256"] = hashlib.sha256(patch).hexdigest()
        preview = patch[:patch_preview_limit]
        result["patch_preview"] = preview.decode("utf-8", errors="replace")
        result["patch_preview_truncated"] = len(patch) > patch_preview_limit
        result["committed_range_proven"] = True

        if result["reality_dirty_count"]:
            result["verdict"] = "BLOCK_REALITY_DIRTY"
            result["errors"].append("Reality working tree is dirty")
        else:
            result["verdict"] = PASS_VERDICT
        return result
    except (GitFailure, OSError, subprocess.SubprocessError, ValueError) as exc:
        result["verdict"] = "BLOCK_REAL_DIFF_MEASUREMENT_FAILED"
        result["errors"].append(str(exc))
        return result
