#!/usr/bin/env python3
"""Administratum post-work bundle checker v0.2."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2"
ACTIVE_ROOT = "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY"
PASS_VERDICT = "POST_WORK_BUNDLE_SCHEMA_PASS"
BLOCK_VERDICT = "POST_WORK_BUNDLE_SCHEMA_BLOCK"
REPAIR_VERDICT = "POST_WORK_REPAIR_REQUEST_EMITTED"
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
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/POST_WORK_BUNDLE_CONTRACT_V0_2.md",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/POST_WORK_REPAIR_LOOP_CONTRACT_V0_2.md",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/TEMPLATES/POST_WORK_REPAIR_REQUEST_TEMPLATE.json",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_bundle_manifest.schema.json",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_bundle_index_card.schema.json",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_receipt_index.schema.json",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_file_delta_index.schema.json",
    "ORGANS/_POST_WORK_RING/SCHEMAS/post_work_organ_receipt.schema.json",
    "ORGANS/_POST_WORK_RING/SCHEMAS/post_work_repair_request.schema.json",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/administratum_post_work_bundle_checker_v0_2.py",
    "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/administratum_post_work_closure_updater_v0_2.py",
    "ORGANS/_POST_WORK_RING/POST_WORK_ORGAN_RING_CONTRACT_V0_2.md",
]
REQUIRED_REPORT_FILES = [
    "OFFICIO_ROLE_ENTRY_RECEIPT.json",
    "SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json",
    "MECHANICUS_TOOL_DELTA_RECEIPT.json",
    "INQUISITION_CONTRADICTION_SCAN_RECEIPT.json",
    "CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json",
    "ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json",
    "POST_WORK_BUNDLE_INDEX_CARD.json",
    "POST_WORK_BUNDLE_MANIFEST.json",
    "POST_WORK_RECEIPT_INDEX.json",
    "POST_WORK_FILE_DELTA_INDEX.json",
    "POST_WORK_ORGAN_RING_RECEIPT.json",
    "GIT_CLOSURE_RECEIPT.json",
    "REMOTE_CLOSURE_RECEIPT.json",
    "NEXT_TASK_ROUTE.json",
]
SCHEMA_TARGETS = {
    "POST_WORK_BUNDLE_MANIFEST.json": "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_bundle_manifest.schema.json",
    "POST_WORK_BUNDLE_INDEX_CARD.json": "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_bundle_index_card.schema.json",
    "POST_WORK_RECEIPT_INDEX.json": "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_receipt_index.schema.json",
    "POST_WORK_FILE_DELTA_INDEX.json": "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/SCHEMAS/post_work_file_delta_index.schema.json",
    "POST_WORK_ORGAN_RING_RECEIPT.json": "ORGANS/_POST_WORK_RING/SCHEMAS/post_work_organ_receipt.schema.json",
}
REQUIRED_RECEIPTS = {
    "OFFICIO_ROLE_ENTRY_RECEIPT.json": "OFFICIO_AGENTIS",
    "SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json": "SCHOLA_IMPERIALIS",
    "MECHANICUS_TOOL_DELTA_RECEIPT.json": "MECHANICUS",
    "INQUISITION_CONTRADICTION_SCAN_RECEIPT.json": "INQUISITION",
    "CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json": "CUSTODES",
}
HEAVY_SUFFIXES = {".zip", ".7z", ".rar", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".avi"}
CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")
FINAL_PASS_VALUES = {"PASS", "FINAL_PASS", "POST_WORK_BUNDLE_FINAL_PASS", "POST_WORK_BUNDLE_SCHEMA_PASS_FINAL"}


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def add_issue(issues: list[dict[str, Any]], check_id: str, message: str, path: str = "", severity: str = "BLOCK") -> None:
    issues.append({"check_id": check_id, "severity": severity, "path": path, "message": message})


def type_matches(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return (isinstance(instance, int) or isinstance(instance, float)) and not isinstance(instance, bool)
    if expected == "null":
        return instance is None
    return True


def validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if isinstance(expected, list):
        if not any(type_matches(instance, item) for item in expected):
            return [f"{path}: expected one of {expected}"]
    elif isinstance(expected, str) and not type_matches(instance, expected):
        return [f"{path}: expected {expected}"]
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")
    if isinstance(instance, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(instance) < min_length:
            errors.append(f"{path}: string shorter than {min_length}")
    if isinstance(instance, list):
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(instance) < min_items:
            errors.append(f"{path}: array shorter than {min_items}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(validate_schema(item, item_schema, f"{path}[{index}]"))
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key}: required field missing")
        props = schema.get("properties", {})
        if isinstance(props, dict):
            for key, subschema in props.items():
                if key in instance and isinstance(subschema, dict):
                    errors.extend(validate_schema(instance[key], subschema, f"{path}.{key}"))
        if schema.get("additionalProperties") is False:
            allowed = set(props)
            for key in instance:
                if key not in allowed:
                    errors.append(f"{path}.{key}: additional property not allowed")
    return errors


def load_schema(repo_root: Path, rel_path: str, issues: list[dict[str, Any]]) -> dict[str, Any] | None:
    path = repo_root / rel_path
    payload, error = read_json_no_bom(path) if path.exists() else (None, "schema file missing")
    if error:
        add_issue(issues, "schema_load", error, rel_path)
        return None
    if not isinstance(payload, dict):
        add_issue(issues, "schema_load", "schema root is not object", rel_path)
        return None
    return payload


def validate_core_files(repo_root: Path, issues: list[dict[str, Any]]) -> None:
    for rel_path in CORE_FILES:
        path = repo_root / rel_path
        if not path.exists():
            add_issue(issues, "core_file", "missing core V0.2 file", rel_path)
            continue
        if path.suffix.lower() == ".json":
            _, error = read_json_no_bom(path)
        else:
            _, error = read_text_no_bom(path)
        if error:
            add_issue(issues, "core_file", error, rel_path)


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
            add_issue(issues, "registered_taskpack", f"{key} missing", value)
    route_payload, route_error = read_json_no_bom(Path(paths["route_manifest"])) if Path(paths["route_manifest"]).exists() else (None, "")
    if route_error:
        add_issue(issues, "registered_route_manifest", route_error, paths["route_manifest"])
    if isinstance(route_payload, dict) and route_payload.get("task_id") != task_id:
        add_issue(issues, "registered_route_manifest", "route manifest task_id mismatch", paths["route_manifest"])
    return paths


def validate_report_files(report_dir: Path, task_id: str, out_path: Path | None, issues: list[dict[str, Any]]) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    out_name = out_path.name if out_path else ""
    for name in REQUIRED_REPORT_FILES:
        path = report_dir / name
        if not path.is_file():
            if name == "ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json" and out_name == name:
                add_issue(issues, "required_report_file", "checker report is generated by this run", name, "WARN")
                continue
            add_issue(issues, "required_report_file", "missing required report file", name)
            continue
    summary = report_dir / "FINAL_OWNER_SUMMARY_RU.md"
    if summary.is_file():
        text, error = read_text_no_bom(summary)
        if error:
            add_issue(issues, "owner_summary", error, summary.name)
        elif not CYRILLIC_RE.search(text):
            add_issue(issues, "owner_summary", "owner summary must be Russian text after Officio role entry", summary.name)
    else:
        add_issue(issues, "owner_summary", "missing FINAL_OWNER_SUMMARY_RU.md", summary.name)
    for path in sorted(report_dir.glob("*.json")):
        payload, error = read_json_no_bom(path)
        if error:
            add_issue(issues, "report_json", error, path.name)
            continue
        loaded[path.name] = payload
        if isinstance(payload, dict) and payload.get("task_id") not in (None, task_id):
            add_issue(issues, "report_task_id", f"task_id mismatch: {payload.get('task_id')!r}", path.name)
    return loaded


def validate_schema_targets(repo_root: Path, report_dir: Path, loaded: dict[str, Any], issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for report_name, schema_rel in SCHEMA_TARGETS.items():
        payload = loaded.get(report_name)
        schema = load_schema(repo_root, schema_rel, issues)
        if payload is None or schema is None:
            continue
        errors = validate_schema(payload, schema)
        checks.append({"file": report_name, "schema": schema_rel, "error_count": len(errors), "errors": errors})
        for error in errors:
            add_issue(issues, "schema_validation", error, report_name)
    return checks


def existing_rel(repo_root: Path, report_dir: Path, value: str) -> bool:
    path = Path(value)
    if path.is_absolute():
        return path.exists()
    return (repo_root / value).exists() or (report_dir / value).exists()


def validate_index_paths(repo_root: Path, report_dir: Path, loaded: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    index = loaded.get("POST_WORK_BUNDLE_INDEX_CARD.json")
    if not isinstance(index, dict):
        return
    for key in ("primary_report_path", "bundle_manifest_path", "receipt_index_path", "file_delta_index_path", "organ_ring_receipt_path"):
        value = index.get(key)
        if not isinstance(value, str) or not value:
            add_issue(issues, "bundle_index_path", f"{key} missing", "POST_WORK_BUNDLE_INDEX_CARD.json")
        elif not existing_rel(repo_root, report_dir, value):
            add_issue(issues, "bundle_index_path", f"{key} target not found: {value}", "POST_WORK_BUNDLE_INDEX_CARD.json")
    if index.get("github_safe") is not True:
        add_issue(issues, "bundle_index", "github_safe must be true", "POST_WORK_BUNDLE_INDEX_CARD.json")


def validate_receipt_index(repo_root: Path, report_dir: Path, loaded: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    receipt_index = loaded.get("POST_WORK_RECEIPT_INDEX.json")
    if not isinstance(receipt_index, dict):
        return
    indexed = {}
    for item in receipt_index.get("receipts", []):
        if isinstance(item, dict) and isinstance(item.get("receipt_id"), str):
            indexed[item["receipt_id"]] = item
            path = item.get("path")
            if isinstance(path, str) and path and not existing_rel(repo_root, report_dir, path):
                add_issue(issues, "receipt_index_path", f"receipt path target not found: {path}", "POST_WORK_RECEIPT_INDEX.json")
    for name, owner in REQUIRED_RECEIPTS.items():
        receipt_id = name.removesuffix(".json")
        if not any(isinstance(item, dict) and item.get("path", "").endswith(name) for item in receipt_index.get("receipts", [])):
            add_issue(issues, "receipt_index", f"missing {owner} receipt index entry for {name}", "POST_WORK_RECEIPT_INDEX.json")


def validate_organ_ring(loaded: dict[str, Any], task_id: str, issues: list[dict[str, Any]]) -> list[str]:
    ring = loaded.get("POST_WORK_ORGAN_RING_RECEIPT.json")
    blocked_organs: list[str] = []
    if not isinstance(ring, dict):
        add_issue(issues, "organ_ring", "POST_WORK_ORGAN_RING_RECEIPT.json missing or malformed", "POST_WORK_ORGAN_RING_RECEIPT.json")
        return blocked_organs
    rows = ring.get("organ_receipts")
    if not isinstance(rows, list):
        add_issue(issues, "organ_ring", "organ_receipts must be array", "POST_WORK_ORGAN_RING_RECEIPT.json")
        return blocked_organs
    by_organ = {str(row.get("organ_id", "")): row for row in rows if isinstance(row, dict)}
    for organ in REQUIRED_ORGANS:
        row = by_organ.get(organ)
        if row is None:
            add_issue(issues, "organ_ring", f"missing required organ receipt: {organ}", "POST_WORK_ORGAN_RING_RECEIPT.json")
            continue
        if row.get("task_id") != task_id:
            add_issue(issues, "organ_ring", f"{organ} task_id mismatch", "POST_WORK_ORGAN_RING_RECEIPT.json")
        status = row.get("status")
        if status == "BLOCK":
            blocked_organs.append(organ)
            add_issue(issues, "organ_block", f"required organ reports BLOCK: {organ}", "POST_WORK_ORGAN_RING_RECEIPT.json")
        if status == "NOT_YET_IMPLEMENTED" and (not row.get("limitation_reason") or not row.get("next_task_route")):
            add_issue(issues, "organ_ring", f"{organ} NOT_YET_IMPLEMENTED requires limitation_reason and next_task_route", "POST_WORK_ORGAN_RING_RECEIPT.json")
    return blocked_organs


def validate_specific_receipts(loaded: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    for name, owner in REQUIRED_RECEIPTS.items():
        if not isinstance(loaded.get(name), dict):
            add_issue(issues, "required_receipt", f"{owner} receipt missing or malformed", name)
    schola = loaded.get("SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json")
    if isinstance(schola, dict) and schola.get("enhanced_ghost_evolve_mode") not in ("ULTIMATE_ORGAN_TEACHING", "ULTIMATE_ORGAN_TEACHING_V0_2"):
        add_issue(issues, "schola_receipt", "Schola receipt must preserve ULTIMATE_ORGAN_TEACHING", "SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json")
    custodes = loaded.get("CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json")
    if isinstance(custodes, dict) and custodes.get("full_custodes_authority_claimed") is True:
        add_issue(issues, "custodes_receipt", "full Custodes authority claim is forbidden", "CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json")
    inq = loaded.get("INQUISITION_CONTRADICTION_SCAN_RECEIPT.json")
    if isinstance(inq, dict):
        verdict = str(inq.get("status") or inq.get("fake_green_scan") or "")
        if verdict == "PASS" and inq.get("warnings"):
            add_issue(issues, "inquisition_receipt", "PASS_WITH_WARNINGS must not be summarized as PASS", "INQUISITION_CONTRADICTION_SCAN_RECEIPT.json")


def validate_remote_proof(loaded: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    remote = loaded.get("REMOTE_CLOSURE_RECEIPT.json")
    if not isinstance(remote, dict):
        return
    for field in ("pre_commit_head", "expected_commit_message", "post_push_head", "origin_master_head", "local_equals_origin", "no_write_after_remote_proof", "self_reference_boundary"):
        if field not in remote:
            add_issue(issues, "remote_proof", f"missing remote proof field: {field}", "REMOTE_CLOSURE_RECEIPT.json")
    index = loaded.get("POST_WORK_BUNDLE_INDEX_CARD.json")
    index_verdict = index.get("verdict") if isinstance(index, dict) else ""
    if index_verdict in FINAL_PASS_VALUES and remote.get("local_equals_origin") is not True:
        add_issue(issues, "fake_final_pass", "final PASS requires local_equals_origin=true", "POST_WORK_BUNDLE_INDEX_CARD.json")


def validate_heavy_artifacts(report_dir: Path, loaded: dict[str, Any], issues: list[dict[str, Any]]) -> None:
    indexed = set()
    index = loaded.get("POST_WORK_BUNDLE_INDEX_CARD.json")
    delta = loaded.get("POST_WORK_FILE_DELTA_INDEX.json")
    for source in (index, delta):
        if isinstance(source, dict):
            for item in source.get("local_heavy_artifacts", []):
                if isinstance(item, dict) and isinstance(item.get("path"), str):
                    indexed.add(item["path"].replace("\\", "/"))
    for path in sorted(report_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(report_dir).as_posix()
        if path.suffix.lower() in HEAVY_SUFFIXES or path.stat().st_size > 1024 * 1024:
            if rel not in indexed and to_posix(path) not in indexed:
                add_issue(issues, "heavy_artifact_policy", f"unindexed heavy artifact in report dir: {rel}", rel)


def build_repair_request(task_id: str, issues: list[dict[str, Any]]) -> dict[str, Any]:
    repairs = []
    for index, issue in enumerate([item for item in issues if item["severity"] == "BLOCK"], start=1):
        repairs.append(
            {
                "issue_id": f"REPAIR-{index:03d}-{issue['check_id']}",
                "path": issue.get("path") or "REPORT_DIR",
                "repair_action": issue["message"],
            }
        )
    return {
        "schema_version": "post_work.repair_request.v0_2",
        "task_id": task_id,
        "repair_request_id": f"REPAIR-{task_id}-001",
        "created_at_utc": utc_now(),
        "blocked_verdict": BLOCK_VERDICT,
        "owner_organ": "ADMINISTRATUM",
        "trigger_issue": "Post-work bundle V0.2 checker found blocking defects.",
        "requested_repairs": repairs or [{"issue_id": "REPAIR-001-UNKNOWN", "path": "REPORT_DIR", "repair_action": "Replay checker and inspect block report."}],
        "status": "OPEN",
    }


def build_report(repo_root: Path, task_id: str, report_dir: Path, out_path: Path | None = None, fixture_mode: bool = False) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    if to_posix(repo_root) != ACTIVE_ROOT:
        add_issue(issues, "root", f"active root mismatch: {to_posix(repo_root)}")
    validate_core_files(repo_root, issues)
    if fixture_mode:
        registered = {"fixture_mode": "SKIPPED_REGISTERED_TASKPACK_CHECK"}
    else:
        registered = validate_registered_task(repo_root, task_id, issues)
    loaded = validate_report_files(report_dir, task_id, out_path, issues)
    schema_checks = validate_schema_targets(repo_root, report_dir, loaded, issues)
    validate_index_paths(repo_root, report_dir, loaded, issues)
    validate_receipt_index(repo_root, report_dir, loaded, issues)
    blocked_organs = validate_organ_ring(loaded, task_id, issues)
    validate_specific_receipts(loaded, issues)
    validate_remote_proof(loaded, issues)
    validate_heavy_artifacts(report_dir, loaded, issues)
    block_count = sum(1 for issue in issues if issue["severity"] == "BLOCK")
    warning_count = sum(1 for issue in issues if issue["severity"] == "WARN")
    return {
        "schema_version": "administratum.post_work_bundle_checker_report.v0_2",
        "task_id": task_id,
        "created_at_utc": utc_now(),
        "repo_root": to_posix(repo_root),
        "report_dir": to_posix(report_dir),
        "registered_taskpack": registered,
        "required_organs": REQUIRED_ORGANS,
        "schema_checks": schema_checks,
        "blocked_organs": blocked_organs,
        "issue_count": len(issues),
        "block_count": block_count,
        "warning_count": warning_count,
        "issues": issues,
        "repair_request_required": block_count > 0,
        "authority_boundary": "POST_WORK_BUNDLE_SCHEMA_ONLY",
        "verdict": PASS_VERDICT if block_count == 0 else BLOCK_VERDICT,
    }


def base_fixture(task_id: str) -> dict[str, Any]:
    report = "ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/FIXTURES"
    rows = [
        {
            "organ_id": organ,
            "task_id": task_id,
            "status": "IMPLEMENTED_WITH_WARNINGS" if organ in {"ASTRONOMICON", "CUSTODES"} else "IMPLEMENTED",
            "owned_checks": [f"{organ} fixture check"],
            "evidence_paths": [f"{report}/{organ}.json"],
            "learned_rules": [f"{organ} fixture learned rule"],
        }
        for organ in REQUIRED_ORGANS
    ]
    receipt_index = [
        ("OFFICIO_ROLE_ENTRY", "OFFICIO_AGENTIS", "OFFICIO_ROLE_ENTRY_RECEIPT.json", "PASS"),
        ("SCHOLA_ENHANCED_GHOST_EVOLVE", "SCHOLA_IMPERIALIS", "SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json", "PASS"),
        ("MECHANICUS_TOOL_DELTA", "MECHANICUS", "MECHANICUS_TOOL_DELTA_RECEIPT.json", "PASS"),
        ("INQUISITION_CONTRADICTION_SCAN", "INQUISITION", "INQUISITION_CONTRADICTION_SCAN_RECEIPT.json", "PASS_WITH_WARNINGS"),
        ("CUSTODES_ORGAN_MATRIX_AUDIT", "CUSTODES", "CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json", "PASS_WITH_WARNINGS"),
        ("POST_WORK_ORGAN_RING", "CUSTODES", "POST_WORK_ORGAN_RING_RECEIPT.json", "PASS"),
        ("GIT_CLOSURE", "ADMINISTRATUM", "GIT_CLOSURE_RECEIPT.json", "PENDING_REMOTE_PROOF"),
        ("REMOTE_CLOSURE", "ADMINISTRATUM", "REMOTE_CLOSURE_RECEIPT.json", "PENDING_REMOTE_PROOF"),
    ]
    return {
        "FINAL_OWNER_SUMMARY_RU.md": "Russian owner summary placeholder: \u0418\u0442\u043e\u0433 \u0434\u043b\u044f \u0432\u043b\u0430\u0434\u0435\u043b\u044c\u0446\u0430.\n",
        "OFFICIO_ROLE_ENTRY_RECEIPT.json": {"schema_version": "fixture.officio.v0_2", "task_id": task_id, "role_id": "SERVITOR", "ack_verdict": "PASS"},
        "SCHOLA_ENHANCED_GHOST_EVOLVE_RECEIPT.json": {"schema_version": "fixture.schola.v0_2", "task_id": task_id, "enhanced_ghost_evolve_mode": "ULTIMATE_ORGAN_TEACHING", "status": "PASS"},
        "MECHANICUS_TOOL_DELTA_RECEIPT.json": {"schema_version": "fixture.mechanicus.v0_2", "task_id": task_id, "tools_added": [], "status": "PASS"},
        "INQUISITION_CONTRADICTION_SCAN_RECEIPT.json": {"schema_version": "fixture.inquisition.v0_2", "task_id": task_id, "fake_green_scan": "PASS_WITH_WARNINGS", "warnings": ["fixture caps preserved"], "status": "PASS_WITH_WARNINGS"},
        "CUSTODES_ORGAN_MATRIX_AUDIT_RECEIPT.json": {"schema_version": "fixture.custodes.v0_2", "task_id": task_id, "missing_required_organs": [], "full_custodes_authority_claimed": False, "status": "PASS_WITH_WARNINGS"},
        "ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json": {"schema_version": "fixture.checker.placeholder.v0_2", "task_id": task_id, "verdict": "PLACEHOLDER_REPLACED_BY_CHECKER"},
        "POST_WORK_BUNDLE_MANIFEST.json": {
            "schema_version": "post_work.bundle_manifest.v0_2",
            "task_id": task_id,
            "bundle_id": f"BUNDLE-{task_id}",
            "active_root": ACTIVE_ROOT,
            "registered_taskpack": "ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/TASKPACK.zip",
            "route_manifest": "ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-20260605-PC-POST-WORK-BUNDLE-ADMISSION-RING-V0_2/TASK_ROUTE_MANIFEST.json",
            "entry_head": "0" * 40,
            "file_delta_index": "POST_WORK_FILE_DELTA_INDEX.json",
            "receipt_index": "POST_WORK_RECEIPT_INDEX.json",
            "organ_ring_receipt": "POST_WORK_ORGAN_RING_RECEIPT.json",
            "github_safe_index": True,
            "heavy_artifact_policy": "Fixture heavy artifacts must be indexed.",
            "local_heavy_artifacts": [],
            "remote_proof": {
                "pre_commit_head": "0" * 40,
                "expected_commit_message": "fixture",
                "post_push_head": "SELF_REFERENCE_BOUNDARY",
                "origin_master_head": "SELF_REFERENCE_BOUNDARY",
                "local_equals_origin": "PENDING_POST_PUSH_NO_WRITE_PROOF",
                "no_write_after_remote_proof": "PENDING_POST_PUSH_NO_WRITE_PROOF",
            },
        },
        "POST_WORK_BUNDLE_INDEX_CARD.json": {
            "schema_version": "post_work.bundle_index_card.v0_2",
            "task_id": task_id,
            "bundle_id": f"BUNDLE-{task_id}",
            "primary_report_path": "FINAL_OWNER_SUMMARY_RU.md",
            "bundle_manifest_path": "POST_WORK_BUNDLE_MANIFEST.json",
            "receipt_index_path": "POST_WORK_RECEIPT_INDEX.json",
            "file_delta_index_path": "POST_WORK_FILE_DELTA_INDEX.json",
            "organ_ring_receipt_path": "POST_WORK_ORGAN_RING_RECEIPT.json",
            "github_safe": True,
            "verdict": "POST_WORK_BUNDLE_SCHEMA_PASS_PENDING_REMOTE_PROOF",
            "local_heavy_artifacts": [],
        },
        "POST_WORK_RECEIPT_INDEX.json": {
            "schema_version": "post_work.receipt_index.v0_2",
            "task_id": task_id,
            "receipts": [
                {"receipt_id": receipt_id, "owner_organ": owner, "path": path, "status": status}
                for receipt_id, owner, path, status in receipt_index
            ],
        },
        "POST_WORK_FILE_DELTA_INDEX.json": {
            "schema_version": "post_work.file_delta_index.v0_2",
            "task_id": task_id,
            "entry_head": "0" * 40,
            "files": [{"path": "fixture", "change_type": "fixture", "owner_organ": "ADMINISTRATUM", "purpose": "fixture"}],
            "github_safe_artifacts_only": True,
            "local_heavy_artifacts": [],
        },
        "POST_WORK_ORGAN_RING_RECEIPT.json": {
            "schema_version": "post_work.organ_ring_receipt.v0_2",
            "task_id": task_id,
            "organ_receipts": rows,
            "ring_verdict": "NINE_ORGAN_RING_REPRESENTED_WITH_WARNINGS",
        },
        "GIT_CLOSURE_RECEIPT.json": {"schema_version": "fixture.git.v0_2", "task_id": task_id, "pre_commit_head": "0" * 40, "status": "PENDING_REMOTE_PROOF"},
        "REMOTE_CLOSURE_RECEIPT.json": {
            "schema_version": "fixture.remote.v0_2",
            "task_id": task_id,
            "pre_commit_head": "0" * 40,
            "expected_commit_message": "fixture",
            "post_push_head": "SELF_REFERENCE_BOUNDARY",
            "origin_master_head": "SELF_REFERENCE_BOUNDARY",
            "local_equals_origin": "PENDING_POST_PUSH_NO_WRITE_PROOF",
            "no_write_after_remote_proof": "PENDING_POST_PUSH_NO_WRITE_PROOF",
            "self_reference_boundary": "fixture",
        },
        "NEXT_TASK_ROUTE.json": {"schema_version": "fixture.next.v0_2", "task_id": task_id, "status": "READY"},
    }


def write_fixture_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8", newline="\n")
    else:
        write_json(path, payload)


def write_fixture_suite(root: Path) -> dict[str, Any]:
    fixtures = [
        "valid_bundle",
        "missing_organ_receipt",
        "malformed_receipt",
        "required_organ_block",
        "required_organ_block_repaired",
        "remote_closure_missing",
        "heavy_artifact_without_index",
    ]
    for name in fixtures:
        task_id = f"FIXTURE-{name.upper().replace('-', '_')}"
        path = root / name
        path.mkdir(parents=True, exist_ok=True)
        for existing in path.iterdir():
            if existing.is_file():
                existing.unlink()
        payloads = base_fixture(task_id)
        if name == "missing_organ_receipt":
            ring = copy.deepcopy(payloads["POST_WORK_ORGAN_RING_RECEIPT.json"])
            ring["organ_receipts"] = ring["organ_receipts"][:-1]
            payloads["POST_WORK_ORGAN_RING_RECEIPT.json"] = ring
        elif name == "malformed_receipt":
            payloads["POST_WORK_RECEIPT_INDEX.json"] = {
                "schema_version": "post_work.receipt_index.v0_2",
                "task_id": task_id,
                "receipts": "schema-invalid-not-array",
            }
        elif name == "required_organ_block":
            ring = copy.deepcopy(payloads["POST_WORK_ORGAN_RING_RECEIPT.json"])
            ring["organ_receipts"][2]["status"] = "BLOCK"
            ring["organ_receipts"][2]["owned_checks"].append("Fixture forced block")
            payloads["POST_WORK_ORGAN_RING_RECEIPT.json"] = ring
        elif name == "remote_closure_missing":
            payloads.pop("REMOTE_CLOSURE_RECEIPT.json", None)
        elif name == "heavy_artifact_without_index":
            payloads["local_bundle.zip"] = "fixture zip placeholder\n"
        for rel, payload in payloads.items():
            write_fixture_file(path / rel, payload)
    return {"task_id": TASK_ID_DEFAULT, "fixtures_root": to_posix(root), "fixtures": fixtures, "created_at_utc": utc_now()}


def run_fixture_suite(repo_root: Path, root: Path, result_out: Path | None = None) -> dict[str, Any]:
    expectations = {
        "valid_bundle": PASS_VERDICT,
        "missing_organ_receipt": BLOCK_VERDICT,
        "malformed_receipt": BLOCK_VERDICT,
        "required_organ_block": BLOCK_VERDICT,
        "required_organ_block_repaired": PASS_VERDICT,
        "remote_closure_missing": BLOCK_VERDICT,
        "heavy_artifact_without_index": BLOCK_VERDICT,
    }
    rows = []
    for name, expected in expectations.items():
        report_dir = root / name
        task_id = f"FIXTURE-{name.upper().replace('-', '_')}"
        repair_out = report_dir / "POST_WORK_REPAIR_REQUEST.json"
        result = build_report(
            repo_root,
            task_id,
            report_dir,
            report_dir / "ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json",
            fixture_mode=True,
        )
        if result["block_count"]:
            write_json(repair_out, build_repair_request(task_id, result["issues"]))
            result["repair_request_path"] = to_posix(repair_out)
        write_json(report_dir / "ADMINISTRATUM_POST_WORK_BUNDLE_CHECKER_REPORT.json", result)
        rows.append(
            {
                "fixture": name,
                "expected": expected,
                "actual": result["verdict"],
                "expectation_met": result["verdict"] == expected,
                "block_count": result["block_count"],
                "repair_request_created": repair_out.exists(),
            }
        )
    receipt = {
        "schema_version": "administratum.post_work_fixture_suite_receipt.v0_2",
        "task_id": TASK_ID_DEFAULT,
        "created_at_utc": utc_now(),
        "fixture_verdict": "PASS" if all(row["expectation_met"] for row in rows) else "FAIL",
        "repair_loop_proof": {
            "block_fixture": "required_organ_block",
            "pass_fixture": "required_organ_block_repaired",
            "block_created_repair_request": next(row["repair_request_created"] for row in rows if row["fixture"] == "required_organ_block"),
        },
        "fixture_rows": rows,
    }
    if result_out is not None:
        write_json(result_out, receipt)
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Administratum post-work bundle V0.2.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", default="")
    parser.add_argument("--out", default="")
    parser.add_argument("--repair-out", default="")
    parser.add_argument("--allow-block-exit-zero", action="store_true")
    parser.add_argument("--write-fixtures", default="")
    parser.add_argument("--run-fixtures", default="")
    parser.add_argument("--fixture-result-out", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)
    if to_posix(repo_root) != ACTIVE_ROOT:
        raise SystemExit(f"active root mismatch: {to_posix(repo_root)}")
    if args.write_fixtures:
        root = ensure_under(repo_root, repo_root / args.write_fixtures)
        receipt = write_fixture_suite(root)
        print(json.dumps(receipt, ensure_ascii=True, indent=2))
        return 0
    if args.run_fixtures:
        root = ensure_under(repo_root, repo_root / args.run_fixtures)
        out = ensure_under(repo_root, repo_root / args.fixture_result_out) if args.fixture_result_out else None
        receipt = run_fixture_suite(repo_root, root, out)
        print(json.dumps(receipt, ensure_ascii=True, indent=2))
        return 0 if receipt["fixture_verdict"] == "PASS" else 2
    if not args.report_dir:
        raise SystemExit("--report-dir is required unless fixture mode is used")
    report_dir = ensure_under(repo_root, repo_root / args.report_dir)
    out_path = ensure_under(repo_root, repo_root / args.out) if args.out else None
    repair_path = ensure_under(repo_root, repo_root / args.repair_out) if args.repair_out else None
    result = build_report(repo_root, args.task_id, report_dir, out_path)
    if result["block_count"] and repair_path is not None:
        write_json(repair_path, build_repair_request(args.task_id, result["issues"]))
        result["repair_request_path"] = to_posix(repair_path)
        result["repair_request_verdict"] = REPAIR_VERDICT
    if out_path is not None:
        write_json(out_path, result)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if result["block_count"] and not args.allow_block_exit_zero:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
