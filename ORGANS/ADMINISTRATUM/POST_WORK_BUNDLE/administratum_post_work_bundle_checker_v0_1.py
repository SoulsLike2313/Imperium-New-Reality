#!/usr/bin/env python3
"""Administratum post-work bundle checker v0.1."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_1"
ACTIVE_ROOT = "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY"
REQUIRED_ORGANS = [
    "ASTRONOMICON",
    "OFFICIO_AGENTIS",
    "ADMINISTRATUM",
    "MECHANICUS",
    "DOCTRINARIUM",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
    "CUSTODES",
]
CORE_FILES = [
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/POST_WORK_BUNDLE_CONTRACT_V0_1.md",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_bundle_manifest.schema.json",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/organ_post_work_receipt.schema.json",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/bundle_index_card.schema.json",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/administratum_post_work_bundle_checker_v0_1.py",
    "ORGANS/_POST_WORK_RING/POST_WORK_ORGAN_RING_CONTRACT_V0_1.md",
    "ORGANS/_POST_WORK_RING/REQUIRED_9_ORGANS_V0_1.json",
    "ORGANS/_POST_WORK_RING/ORGAN_POST_WORK_RECEIPT_TEMPLATE.json",
    "ORGANS/CUSTODES/ORGAN_MATRIX_AUDIT/CUSTODES_ORGAN_MATRIX_AUDIT_CONTRACT_V0_1.md",
]
REQUIRED_REPORT_FILES = [
    "OFFICIO_ROLE_ENTRY_RECEIPT.json",
    "POST_WORK_BUNDLE_INDEX_CARD.json",
    "POST_WORK_RECEIPT_INDEX.json",
    "POST_WORK_FILE_DELTA_INDEX.json",
    "POST_WORK_ORGAN_RING_RECEIPT.json",
    "ADMINISTRATUM_POST_WORK_BUNDLE_RECEIPT.json",
    "MECHANICUS_TOOL_DELTA_RECEIPT.json",
    "INQUISITION_CONTRADICTION_SCAN_RECEIPT.json",
    "SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json",
    "CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json",
    "GIT_CLOSURE_RECEIPT.json",
    "REMOTE_CLOSURE_RECEIPT.json",
    "NEXT_TASK_ROUTE.json",
]
HEAVY_SUFFIXES = {".zip", ".7z", ".rar", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".avi"}
CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True, indent=2) + "\n")


def read_text_no_bom(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return "", "UTF-8 BOM detected"
    try:
        return raw.decode("utf-8"), ""
    except UnicodeDecodeError as exc:
        return "", f"UTF-8 decode error: {exc}"


def read_json_no_bom(path: Path) -> tuple[Any | None, str]:
    text, error = read_text_no_bom(path)
    if error:
        return None, error
    try:
        return json.loads(text), ""
    except json.JSONDecodeError as exc:
        return None, f"JSON decode error: {exc.msg} at line {exc.lineno} column {exc.colno}"


def resolve_repo_root(value: str) -> Path:
    root = Path(value or ".").resolve()
    markers = ["EPOCH_MANIFEST.json", "NEW_REALITY_SCOPE_LOCK.md", "AGENTS.md"]
    if all((root / marker).is_file() for marker in markers):
        return root
    raise SystemExit(f"repo root missing New Reality markers: {to_posix(root)}")


def rel_exists(repo_root: Path, rel_path: str) -> bool:
    return (repo_root / rel_path).exists()


def add_issue(issues: list[dict[str, Any]], check_id: str, message: str, severity: str = "BLOCK") -> None:
    issues.append({"check_id": check_id, "severity": severity, "message": message})


def validate_core_files(repo_root: Path, issues: list[dict[str, Any]]) -> None:
    for rel_path in CORE_FILES:
        path = repo_root / rel_path
        if not path.exists():
            add_issue(issues, "core_file", f"missing: {rel_path}")
            continue
        if path.suffix.lower() == ".json":
            _, error = read_json_no_bom(path)
            if error:
                add_issue(issues, "core_json", f"{rel_path}: {error}")
        else:
            _, error = read_text_no_bom(path)
            if error:
                add_issue(issues, "core_text", f"{rel_path}: {error}")


def validate_registered_task(repo_root: Path, task_id: str, issues: list[dict[str, Any]]) -> dict[str, str]:
    base = repo_root / "ORGANS" / "ASTRONOMICON" / "TASK_INBOX" / "REGISTERED" / task_id
    paths = {
        "registered_task_path": to_posix(base),
        "taskpack_zip": to_posix(base / "TASKPACK.zip"),
        "route_manifest": to_posix(base / "TASK_ROUTE_MANIFEST.json"),
        "admission_receipt": to_posix(base / "TASKPACK_ADMISSION_RECEIPT.json"),
        "manifest": to_posix(base / "EXTRACTED" / "MANIFEST.json"),
    }
    for key, value in paths.items():
        if not Path(value).exists():
            add_issue(issues, "registered_taskpack", f"{key} missing: {value}")
    route_payload, route_error = read_json_no_bom(Path(paths["route_manifest"])) if Path(paths["route_manifest"]).exists() else (None, "")
    if route_error:
        add_issue(issues, "registered_route_manifest", route_error)
    if isinstance(route_payload, dict) and route_payload.get("task_id") != task_id:
        add_issue(issues, "registered_route_manifest", "route manifest task_id mismatch")
    return paths


def validate_report_json_files(report_dir: Path, task_id: str, issues: list[dict[str, Any]]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for path in sorted(report_dir.glob("*.json")):
        payload, error = read_json_no_bom(path)
        rel = path.name
        if error:
            add_issue(issues, "report_json", f"{rel}: {error}")
            continue
        loaded[rel] = payload
        if isinstance(payload, dict) and payload.get("task_id") not in (None, task_id):
            add_issue(issues, "report_task_id", f"{rel}: task_id mismatch")
    return loaded


def validate_report_files(report_dir: Path, issues: list[dict[str, Any]]) -> None:
    for name in REQUIRED_REPORT_FILES:
        if not (report_dir / name).is_file():
            add_issue(issues, "required_report_file", f"missing: {name}")
    summary = report_dir / "FINAL_OWNER_SUMMARY_RU.md"
    if not summary.is_file():
        add_issue(issues, "owner_summary", "missing FINAL_OWNER_SUMMARY_RU.md")
    else:
        text, error = read_text_no_bom(summary)
        if error:
            add_issue(issues, "owner_summary", error)
        elif not CYRILLIC_RE.search(text):
            add_issue(issues, "owner_summary", "FINAL_OWNER_SUMMARY_RU.md must be Russian owner-facing text")


def validate_organ_ring(report_dir: Path, task_id: str, issues: list[dict[str, Any]]) -> None:
    path = report_dir / "POST_WORK_ORGAN_RING_RECEIPT.json"
    payload, error = read_json_no_bom(path) if path.exists() else (None, "missing POST_WORK_ORGAN_RING_RECEIPT.json")
    if error:
        add_issue(issues, "organ_ring", error)
        return
    if not isinstance(payload, dict):
        add_issue(issues, "organ_ring", "root must be object")
        return
    rows = payload.get("organ_receipts")
    if not isinstance(rows, list):
        add_issue(issues, "organ_ring", "organ_receipts must be array")
        return
    by_organ = {str(row.get("organ_id", "")): row for row in rows if isinstance(row, dict)}
    for organ in REQUIRED_ORGANS:
        row = by_organ.get(organ)
        if row is None:
            add_issue(issues, "organ_ring", f"missing organ receipt: {organ}")
            continue
        for field in ("task_id", "status", "owned_checks", "evidence_paths", "learned_rules"):
            if field not in row:
                add_issue(issues, "organ_receipt", f"{organ}: missing {field}")
        if row.get("task_id") != task_id:
            add_issue(issues, "organ_receipt", f"{organ}: task_id mismatch")
        if row.get("status") == "NOT_YET_IMPLEMENTED":
            if not row.get("limitation_reason") or not row.get("next_task_route"):
                add_issue(issues, "organ_receipt", f"{organ}: NOT_YET_IMPLEMENTED requires limitation_reason and next_task_route")


def validate_specific_receipts(loaded: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    admin = loaded.get("ADMINISTRATUM_POST_WORK_BUNDLE_RECEIPT.json")
    if not isinstance(admin, dict):
        add_issue(issues, "administratum_receipt", "ADMINISTRATUM_POST_WORK_BUNDLE_RECEIPT.json missing or malformed")
    elif admin.get("bundle_admission_evidence") is not True:
        add_issue(issues, "administratum_receipt", "bundle_admission_evidence must be true")
    inq = loaded.get("INQUISITION_CONTRADICTION_SCAN_RECEIPT.json")
    if not isinstance(inq, dict):
        add_issue(issues, "inquisition_receipt", "INQUISITION_CONTRADICTION_SCAN_RECEIPT.json missing or malformed")
    elif inq.get("fake_green_scan") != "PASS":
        add_issue(issues, "inquisition_receipt", "fake_green_scan must be PASS")
    custodes = loaded.get("CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json")
    if not isinstance(custodes, dict):
        add_issue(issues, "custodes_receipt", "CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json missing or malformed")
    elif custodes.get("missing_required_organs"):
        add_issue(issues, "custodes_receipt", "missing_required_organs must be empty")


def validate_bundle_index(report_dir: Path, task_id: str, issues: list[dict[str, Any]]) -> None:
    path = report_dir / "POST_WORK_BUNDLE_INDEX_CARD.json"
    payload, error = read_json_no_bom(path) if path.exists() else (None, "missing POST_WORK_BUNDLE_INDEX_CARD.json")
    if error:
        add_issue(issues, "bundle_index", error)
        return
    if not isinstance(payload, dict):
        add_issue(issues, "bundle_index", "root must be object")
        return
    if payload.get("task_id") != task_id:
        add_issue(issues, "bundle_index", "task_id mismatch")
    if payload.get("github_safe") is not True:
        add_issue(issues, "bundle_index", "github_safe must be true")
    for key in ("receipt_index_path", "file_delta_index_path", "organ_ring_receipt_path"):
        rel = payload.get(key)
        if not isinstance(rel, str) or not rel:
            add_issue(issues, "bundle_index", f"{key} missing")
        elif not (Path(rel).is_absolute() or (report_dir.parent.parent / rel).exists() or (Path.cwd() / rel).exists()):
            add_issue(issues, "bundle_index", f"{key} target not found: {rel}")


def validate_heavy_artifacts(report_dir: Path, loaded: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    index = loaded.get("POST_WORK_BUNDLE_INDEX_CARD.json")
    indexed = set()
    if isinstance(index, dict):
        for item in index.get("local_heavy_artifacts", []):
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                indexed.add(item["path"].replace("\\", "/"))
    for path in sorted(report_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(report_dir).as_posix()
        if path.suffix.lower() in HEAVY_SUFFIXES or path.stat().st_size > 1024 * 1024:
            if rel not in indexed:
                add_issue(issues, "heavy_artifact_policy", f"unindexed heavy artifact in report dir: {rel}")


def build_report(repo_root: Path, task_id: str, report_dir: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    if to_posix(repo_root) != ACTIVE_ROOT:
        add_issue(issues, "root", f"active root mismatch: {to_posix(repo_root)}")
    validate_core_files(repo_root, issues)
    registered = validate_registered_task(repo_root, task_id, issues)
    validate_report_files(report_dir, issues)
    loaded = validate_report_json_files(report_dir, task_id, issues)
    validate_bundle_index(report_dir, task_id, issues)
    validate_organ_ring(report_dir, task_id, issues)
    validate_specific_receipts(loaded, issues)
    validate_heavy_artifacts(report_dir, loaded, issues)
    block_count = sum(1 for issue in issues if issue["severity"] == "BLOCK")
    return {
        "schema_version": "administratum.post_work_bundle_checker_report.v0_1",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "repo_root": to_posix(repo_root),
        "report_dir": to_posix(report_dir),
        "registered_taskpack": registered,
        "required_organs": REQUIRED_ORGANS,
        "issue_count": len(issues),
        "block_count": block_count,
        "issues": issues,
        "authority_boundary": "POST_WORK_BUNDLE_STRUCTURAL_ONLY",
        "verdict": "POST_WORK_BUNDLE_STRUCTURAL_PASS" if block_count == 0 else "POST_WORK_BUNDLE_STRUCTURAL_BLOCK",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Administratum post-work bundle V0.1.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--out", default="")
    parser.add_argument("--allow-block-exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    report_dir = (repo_root / args.report_dir).resolve() if not Path(args.report_dir).is_absolute() else Path(args.report_dir).resolve()
    if repo_root not in report_dir.parents and report_dir != repo_root:
        raise SystemExit(f"report dir escapes repo root: {to_posix(report_dir)}")
    report = build_report(repo_root, args.task_id, report_dir)
    if args.out:
        out = (repo_root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()
        if repo_root not in out.parents and out != repo_root:
            raise SystemExit(f"output escapes repo root: {to_posix(out)}")
        write_json(out, report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    if report["block_count"] and not args.allow_block_exit_zero:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
