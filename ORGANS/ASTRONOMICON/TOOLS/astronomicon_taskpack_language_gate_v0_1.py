#!/usr/bin/env python3
"""Check language/encoding gate for an already registered taskpack ZIP."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys

    sys.path.append(str(Path(__file__).resolve().parent))

from astronomicon_task_entry_lib_v0_1 import (  # noqa: E402
    build_context,
    find_zip_member,
    read_json,
    utc_now,
    validate_manifest_language_policy,
    validate_taskpack_language_root_files,
    write_json,
)


def normalize_path(path_value: str | Path) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (Path.cwd() / path).resolve()


def run_gate(repo_root: str | Path, task_id: str) -> dict[str, Any]:
    ctx = build_context(repo_root)
    registered_path = ctx["registered_root"] / task_id
    zip_path = registered_path / "TASKPACK.zip"

    if not registered_path.exists():
        return {
            "task_id": task_id,
            "timestamp_utc": utc_now(),
            "verdict": "BLOCK",
            "caps_triggered": ["CAP_REGISTERED_TASK_NOT_RESOLVABLE"],
            "warnings": [f"Registered task path missing: {registered_path}"],
            "language_gate_passed": False,
        }
    if not zip_path.exists():
        return {
            "task_id": task_id,
            "timestamp_utc": utc_now(),
            "verdict": "BLOCK",
            "caps_triggered": ["CAP_TASKPACK_ADMISSION_MISSING"],
            "warnings": [f"Taskpack ZIP missing: {zip_path}"],
            "language_gate_passed": False,
        }

    caps: list[str] = []
    warnings: list[str] = []
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        names = zip_file.namelist()
        manifest_name = find_zip_member(names, ["MANIFEST.json"])
        if manifest_name is None:
            return {
                "task_id": task_id,
                "timestamp_utc": utc_now(),
                "verdict": "BLOCK",
                "caps_triggered": ["CAP_TASKPACK_ADMISSION_MISSING"],
                "warnings": ["MANIFEST.json missing in ZIP."],
                "language_gate_passed": False,
            }
        manifest = json.loads(zip_file.read(manifest_name).decode("utf-8"))
        policy_issues, policy_caps = validate_manifest_language_policy(manifest)
        root_issues, root_caps = validate_taskpack_language_root_files(zip_file, names)
        warnings.extend(policy_issues)
        warnings.extend(root_issues)
        caps.extend(policy_caps)
        caps.extend(root_caps)

    verdict = "PASS" if not caps else "BLOCK"
    return {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "registered_task_path": str(registered_path).replace("\\", "/"),
        "taskpack_zip_path": str(zip_path).replace("\\", "/"),
        "language_gate_passed": verdict == "PASS",
        "caps_triggered": sorted(set(caps)),
        "warnings": warnings,
        "verdict": verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Astronomicon taskpack language gate check.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--task-id", required=True, help="Registered task ID.")
    parser.add_argument("--receipt-path", default="", help="Optional path to write JSON receipt.")
    args = parser.parse_args()

    receipt = run_gate(args.repo_root, args.task_id)
    if args.receipt_path:
        write_json(normalize_path(args.receipt_path), receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 1 if receipt.get("verdict") == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
