#!/usr/bin/env python3
"""Consume a task context pack in a bounded, replayable way."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from typing import Any


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def detect_organ(path: str) -> str | None:
    m = re.search(r"ORGANS/([A-Z_]+)/", path)
    return m.group(1) if m else None


def classify_role(path: str) -> str:
    if path == "AGENTS.md":
        return "router"
    if path.endswith("MATRIX_SPINE_INDEX.md"):
        return "matrix_spine"
    if path.endswith("/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md"):
        return "task_participation_read_first"
    if path.endswith("/BLOCK/CONTEXT_DIGEST_V0_1.md"):
        return "organ_context_digest"
    if path.endswith("/BLOCK/READ_FIRST_COMPACT.md"):
        return "organ_compact_read_first"
    if path.endswith("/BLOCK/PASSPORT/ORGAN_BLOCK_PASSPORT_V0_1.json"):
        return "organ_block_passport"
    return "mandatory_context_item"


def consume_path(repo_root: pathlib.Path, rel_path: str) -> dict[str, Any]:
    abs_path = (repo_root / rel_path).resolve()
    role = classify_role(rel_path)
    organ = detect_organ(rel_path)

    if not abs_path.exists():
        return {
            "path": rel_path,
            "exists": False,
            "read": False,
            "sha256": None,
            "byte_count": 0,
            "char_count": 0,
            "organ": organ,
            "role": role,
            "note": "missing",
        }

    if abs_path.is_dir():
        return {
            "path": rel_path,
            "exists": True,
            "read": False,
            "sha256": None,
            "byte_count": 0,
            "char_count": 0,
            "organ": organ,
            "role": role,
            "note": "directory_skipped",
        }

    data = abs_path.read_bytes()
    try:
        char_count = len(data.decode("utf-8"))
    except UnicodeDecodeError:
        char_count = len(data.decode("utf-8", errors="replace"))

    return {
        "path": rel_path,
        "exists": True,
        "read": True,
        "sha256": sha256_bytes(data),
        "byte_count": len(data),
        "char_count": char_count,
        "organ": organ,
        "role": role,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Consume task context pack")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--context-pack", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--task-id", default="")
    parser.add_argument("--actor", default="consume_task_context_pack_v0_1.py")
    args = parser.parse_args()

    repo_root = pathlib.Path(args.repo_root).resolve()
    context_pack_path = pathlib.Path(args.context_pack).resolve()
    out_dir = pathlib.Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    context_pack = load_json(context_pack_path)
    task_id = args.task_id or str(context_pack.get("task_id", "UNKNOWN_TASK"))
    mandatory = list(context_pack.get("mandatory_context", []))

    consumed_items = [consume_path(repo_root, path) for path in mandatory]

    read_count = sum(1 for item in consumed_items if item["read"])
    missing_count = sum(1 for item in consumed_items if not item["exists"])
    total_bytes = sum(int(item["byte_count"]) for item in consumed_items)
    total_chars = sum(int(item["char_count"]) for item in consumed_items)

    missing_paths = [item["path"] for item in consumed_items if not item["exists"]]

    critical_missing = []
    for rel in missing_paths:
        if rel == "AGENTS.md":
            critical_missing.append(rel)
        elif rel.endswith("MATRIX_SPINE_INDEX.md"):
            critical_missing.append(rel)
        elif rel.endswith("/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md"):
            critical_missing.append(rel)

    if critical_missing:
        verdict = "BLOCK"
    elif missing_count > 0:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    receipt = {
        "task_id": task_id,
        "context_pack_path": str(context_pack_path),
        "generated_at_utc": utc_now(),
        "consumer_tool": args.actor,
        "consumed_items": consumed_items,
        "summary": {
            "mandatory_count": len(mandatory),
            "read_count": read_count,
            "missing_count": missing_count,
            "total_bytes": total_bytes,
            "total_chars": total_chars,
            "broad_read_detected": False,
            "critical_missing_count": len(critical_missing),
            "critical_missing": critical_missing,
        },
        "verdict": verdict,
    }

    out_path = out_dir / "context_pack_consumption_receipt.json"
    out_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if critical_missing:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
