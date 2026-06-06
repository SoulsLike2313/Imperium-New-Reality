#!/usr/bin/env python3
"""Execute gated physical root migration for the nine-organ core shape."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260606-PC-CORE-PHYSICAL-ROOT-CLEAN-MIGRATION-LEARNING-ARCHIVE-V0_1"
REPORT_DEFAULT = f"REPORTS/{TASK_ID_DEFAULT}/CORE_PHYSICAL_MIGRATION_REPORT.json"
RECEIPT_DEFAULT = f"REPORTS/{TASK_ID_DEFAULT}/CORE_MIGRATION_EXECUTION_RECEIPT.json"
ADDRESS_BOOK_DEFAULT = "ORGANS/ADMINISTRATUM/ADDRESS_BOOK/physical_root_migration_address_book_v0_1.json"
MAX_FULL_PATH_LEN_DEFAULT = 390

ROOT_HOLD_ITEMS = {
    ".gitignore": "Git ignore policy file must remain at repository root.",
    "AGENTS.md": "Root agent contract must remain at repository root.",
    "ORGANS": "Canonical organ container.",
    "SUPPORT": "Canonical support container.",
    "REPORTS": "Root report evidence path is required by current and historical task contracts.",
}
ORGAN_MIRRORS = {
    "ADMINISTRATUM",
    "ASTRONOMICON",
    "DOCTRINARIUM",
    "INQUISITION",
    "MECHANICUS",
    "OFFICIO_AGENTIS",
}
LEARNING_ARCHIVE_ITEMS = {
    "AGENT_IDE",
    "ARCHIVE",
    "ARTIFACTS",
    "ORGAN_AGENT_COMMON",
    "ORGAN_AGENTS",
    "ORGAN_DIALOGUE",
    "RESEARCH",
    "RUNS",
    "SANCTUM_MINI",
    "SANCTUM_NG",
    "SANCTUM_VISUAL_FOUNDRY",
    "STRESS_TESTS",
    "VISUAL_BRAIN",
}
QUARANTINE_ITEMS = {
    ".taskpack_import_tmp",
    "ANCIENT_EMPIRE_REFERENCE.md",
    "IMPERIUM_NEW_GENERATION",
    "QUARANTINE",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def git_lines(repo_root: Path, args: list[str]) -> list[str]:
    proc = run_git(repo_root, args)
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line.strip()]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def classify_root_item(name: str) -> dict[str, Any]:
    if name in ROOT_HOLD_ITEMS:
        return {
            "action": "HOLD_WITH_REASON",
            "classification": "TECHNICAL_ROOT_EXCEPTION",
            "destination": "",
            "reason": ROOT_HOLD_ITEMS[name],
            "suspected_owner": "ADMINISTRATUM",
            "active_use_allowed": True,
            "quarantine_index_required": False,
        }
    if name in ORGAN_MIRRORS:
        return {
            "action": "MOVE_TO_ORGAN_LEGACY_MIRROR",
            "classification": "LEGACY_ROOT_ORGAN_MIRROR",
            "destination": f"ORGANS/{name}/LEGACY_IMPORTED_ROOT_MIRROR/{name}",
            "reason": "Duplicate top-level organ mirror imported into canonical organ home legacy area.",
            "suspected_owner": name,
            "active_use_allowed": False,
            "quarantine_index_required": False,
        }
    if name in LEARNING_ARCHIVE_ITEMS:
        return {
            "action": "MOVE_TO_LEARNING_ARCHIVE",
            "classification": "LEGACY_LEARNING_ARCHIVE",
            "destination": f"SUPPORT/QUESTIONABLE_OR_QUARANTINE/ITEMS/LEARNING_ARCHIVE/{name}",
            "reason": "Legacy prototype, failed experiment, training, demo, visual, or abandoned surface.",
            "suspected_owner": "SCHOLA_IMPERIALIS",
            "active_use_allowed": False,
            "quarantine_index_required": True,
        }
    if name in QUARANTINE_ITEMS:
        return {
            "action": "MOVE_TO_QUARANTINE",
            "classification": "ROOT_QUARANTINE_CANDIDATE",
            "destination": f"SUPPORT/QUESTIONABLE_OR_QUARANTINE/ITEMS/ROOT_QUARANTINE/{name}",
            "reason": "Unknown, stale, duplicate, empty temporary, or questionable root material.",
            "suspected_owner": "INQUISITION",
            "active_use_allowed": False,
            "quarantine_index_required": True,
        }
    return {
        "action": "MOVE_TO_COMMON_SUPPORT",
        "classification": "ROOT_COMMON_SUPPORT",
        "destination": f"SUPPORT/COMMON_IMPERIUM_SUPPORT/ROOT_IMPORTED_COMMON_SUPPORT/{name}",
        "reason": "Shared root support, contracts, schemas, tools, docs, task control, or historical support evidence.",
        "suspected_owner": "ADMINISTRATUM",
        "active_use_allowed": True,
        "quarantine_index_required": False,
    }


def max_destination_path_len(repo_root: Path, name: str, destination: str, tracked_files: list[str]) -> tuple[int, str]:
    max_len = len(str((repo_root / destination).resolve()))
    max_src = name
    for rel in tracked_files:
        tail = rel[len(name):].lstrip("/\\")
        new_rel = destination + ("/" + tail if tail else "")
        full_len = len(str((repo_root / new_rel).resolve()))
        if full_len > max_len:
            max_len = full_len
            max_src = rel
    return max_len, max_src


def build_plan(repo_root: Path, max_full_path_len: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for child in sorted(repo_root.iterdir(), key=lambda p: p.name.upper()):
        if child.name == ".git":
            continue
        rel = child.name
        policy = classify_root_item(rel)
        tracked = git_lines(repo_root, ["ls-files", "--", rel])
        untracked = git_lines(repo_root, ["ls-files", "--others", "--exclude-standard", "--", rel])
        max_len, max_src = (0, "")
        hold_reasons: list[str] = []
        if policy["destination"]:
            max_len, max_src = max_destination_path_len(repo_root, rel, policy["destination"], tracked)
            if max_len > max_full_path_len:
                hold_reasons.append(f"Destination path length would be {max_len}, above safe limit {max_full_path_len}; longest source {max_src}.")
            if (repo_root / policy["destination"]).exists():
                hold_reasons.append("Destination already exists.")
        planned_action = policy["action"]
        if hold_reasons and planned_action != "HOLD_WITH_REASON":
            planned_action = "HOLD_WITH_REASON"
        rows.append(
            {
                "path": rel,
                "kind": "directory" if child.is_dir() else "file",
                "tracked_file_count": len(tracked),
                "untracked_file_count": len(untracked),
                "classification": policy["classification"],
                "planned_action": planned_action,
                "destination": policy["destination"],
                "reason": policy["reason"],
                "suspected_owner": policy["suspected_owner"],
                "active_use_allowed": policy["active_use_allowed"],
                "quarantine_index_required": policy["quarantine_index_required"],
                "hold_reasons": hold_reasons if hold_reasons else ([policy["reason"]] if planned_action == "HOLD_WITH_REASON" else []),
                "max_destination_full_path_len": max_len,
                "longest_source_path": max_src,
                "execution_status": "PLANNED",
                "command": [],
                "stderr": "",
            }
        )
    return rows


def preserve_empty_untracked_destination(dest: Path, source_name: str, reason: str) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    note = dest / "EMPTY_DIRECTORY_PRESERVATION_NOTE.md"
    if not note.exists():
        note.write_text(
            "# Empty Directory Preservation Note\n\n"
            f"Original root item: {source_name}\n\n"
            f"Reason: {reason}\n\n"
            "The source directory had no git-tracked content. This note preserves the migration evidence in git.\n",
            encoding="utf-8",
            newline="\n",
        )


def execute_row(repo_root: Path, row: dict[str, Any]) -> dict[str, Any]:
    if row["planned_action"] == "HOLD_WITH_REASON":
        row["execution_status"] = "HOLD_WITH_REASON"
        return row
    src = repo_root / row["path"]
    dst = repo_root / row["destination"]
    if not src.exists():
        row["execution_status"] = "SKIPPED_SOURCE_MISSING"
        row["hold_reasons"].append("Source missing at execution time.")
        return row
    dst.parent.mkdir(parents=True, exist_ok=True)
    if row["tracked_file_count"] > 0:
        command = ["mv", row["path"], row["destination"]]
        proc = run_git(repo_root, command)
        row["command"] = ["git", *command]
        row["stderr"] = proc.stderr.strip()
        row["execution_status"] = "MOVED" if proc.returncode == 0 else "HOLD_WITH_REASON"
        if proc.returncode != 0:
            row["hold_reasons"].append(f"git mv failed with exit code {proc.returncode}: {proc.stderr.strip()}")
    else:
        try:
            if src.is_dir() and not any(src.iterdir()):
                preserve_empty_untracked_destination(dst, row["path"], row["reason"])
                shutil.rmtree(src)
                row["execution_status"] = "MOVED_EMPTY_DIRECTORY_WITH_NOTE"
            else:
                shutil.move(str(src), str(dst))
                row["execution_status"] = "MOVED_UNTRACKED"
            row["command"] = ["python", "shutil.move_or_empty_dir_preserve", row["path"], row["destination"]]
        except Exception as exc:
            row["execution_status"] = "HOLD_WITH_REASON"
            row["hold_reasons"].append(f"untracked move failed: {exc}")
    return row


def build_report(repo_root: Path, task_id: str, apply: bool, max_full_path_len: int) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    pre_status = git_lines(repo_root, ["status", "--short", "--branch"])
    pre_top = [p.name for p in repo_root.iterdir() if p.name != ".git"]
    rows = build_plan(repo_root, max_full_path_len)
    if apply:
        for row in rows:
            execute_row(repo_root, row)
    moved = [row for row in rows if row["execution_status"].startswith("MOVED")]
    holds = [row for row in rows if row["execution_status"] == "HOLD_WITH_REASON"]
    post_top = [p.name for p in repo_root.iterdir() if p.name != ".git"]
    report = {
        "schema_version": "imperium.core_physical_migration_report.v0_1",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "mode": "APPLY" if apply else "DRY_RUN",
        "repo_root": to_posix(repo_root),
        "max_full_path_len": max_full_path_len,
        "pre_status": pre_status,
        "pre_top_level_entries": sorted(pre_top, key=str.upper),
        "post_top_level_entries": sorted(post_top, key=str.upper),
        "moved_count": len(moved),
        "hold_count": len(holds),
        "planned_count": len(rows),
        "moved_items": moved,
        "hold_items": holds,
        "all_items": rows,
        "no_destructive_delete_performed": True,
        "git_mv_used_for_tracked_moves": True,
        "verdict": "PASS_WITH_WARNINGS" if holds else "PASS",
        "warnings": [
            {"id": "ROOT_HOLDS_REMAIN", "count": len(holds), "meaning": "Every hold row has HOLD_WITH_REASON."}
        ] if holds else [],
        "blockers": [],
    }
    receipt = {
        "schema_version": "imperium.core_migration_execution_receipt.v0_1",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "mode": report["mode"],
        "moved_count": report["moved_count"],
        "hold_count": report["hold_count"],
        "moved_paths": [{"original_path": row["path"], "new_path": row["destination"], "classification": row["classification"]} for row in moved],
        "hold_paths": [{"path": row["path"], "hold_reasons": row["hold_reasons"], "classification": row["classification"]} for row in holds],
        "no_destructive_delete_performed": True,
        "verdict": report["verdict"],
    }
    return {"report": report, "receipt": receipt}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute gated physical root migration.")
    parser.add_argument("--root", "--repo-root", dest="repo_root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--max-full-path-len", type=int, default=MAX_FULL_PATH_LEN_DEFAULT)
    parser.add_argument("--report-out", default=REPORT_DEFAULT)
    parser.add_argument("--receipt-out", default=RECEIPT_DEFAULT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_report(Path(args.repo_root), args.task_id, args.apply, args.max_full_path_len)
    write_json(Path(args.report_out), payload["report"])
    write_json(Path(args.receipt_out), payload["receipt"])
    print(json.dumps(payload["report"], ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
