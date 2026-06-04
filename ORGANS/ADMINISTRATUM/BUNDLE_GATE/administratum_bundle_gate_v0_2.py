#!/usr/bin/env python3
"""Administratum task report bundle schema gate v0.2."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
import zipfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from administratum_bundle_gate_v0_1 import (  # noqa: E402
    ADJACENT_MANIFEST,
    COMPOSITION_RECEIPT,
    MATRIX_CLASSES as V01_MATRIX_CLASSES,
    MISSING_REQUEST,
    adjacent_matches,
    ensure_under,
    find_repo_root,
    glob_matches,
    to_posix,
    write_json,
)


TASK_ID_DEFAULT = "TASK-NEWGEN-PC-ADMINISTRATUM-BUNDLE-GATE-SCHEMA-VALIDATION-ANTI-FAKE-GREEN-REPLAY-PC-V0_1"
ACTIVE_ROOT_DEFAULT = "E:/IMPERIUM_NEW_GENERATION_NEW_REALITY"
ANCIENT_ROOT_DEFAULT = "E:/IMPERIUM"
MATRIX_VERSION = "0.2"

COMPOSITION_PASS = "BUNDLE_COMPOSITION_PASS"
COMPOSITION_BLOCK = "BUNDLE_COMPOSITION_BLOCK"
SCHEMA_PASS = "BUNDLE_SCHEMA_PASS"
SCHEMA_WARN = "BUNDLE_SCHEMA_WARN"
SCHEMA_BLOCK = "BUNDLE_SCHEMA_BLOCK"

V02_GATE_RECEIPT = "administratum_bundle_gate_v0_2_receipt.json"
SCHEMA_VALIDATION_RECEIPT = "schema_validation_receipt.json"
DIGEST_RECEIPT = "missing_items_and_invalid_fields_digest.json"

FORBIDDEN_AUTHORITY_CLAIMS = {
    "SEMANTIC_TRUTH_PASS",
    "CUSTODES_ADMISSION_PASS",
    "INQUISITION_CLEAN_PASS",
    "NO_FAKE_GREEN_FULL_PASS",
}

CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
REPORT_TEXT_EXTENSIONS = {".md", ".txt"}
SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")
SHA_SELF_REFERENCE_SKIP = {
    V02_GATE_RECEIPT,
    SCHEMA_VALIDATION_RECEIPT,
    DIGEST_RECEIPT,
    MISSING_REQUEST,
    COMPOSITION_RECEIPT,
    "bundle_packager_receipt.json",
}

SCHEMA_BY_CLASS = {
    "task_identity_and_report_metadata": "task_identity_and_report_metadata.schema.json",
    "commit_chain_identifiers": "commit_chain_identifiers.schema.json",
    "git_closure_and_remote_closure_proof": "git_closure_and_remote_closure_proof.schema.json",
    "worktree_clean_or_explicit_cap_receipt": "worktree_clean_or_explicit_cap_receipt.schema.json",
    "scope_lock_no_ancient_mutation_receipt": "scope_lock_no_ancient_mutation_receipt.schema.json",
    "claim_ledger": "claim_ledger.schema.json",
    "capability_split_receipt": "capability_split_receipt.schema.json",
    "red_team_verdict": "red_team_verdict.schema.json",
    "final_owner_summary_boundary": "final_owner_summary_boundary.schema.json",
    "bundle_manifest_and_file_inventory": "bundle_file_inventory.schema.json",
    "adjacent_receipts_manifest": "adjacent_receipts_manifest.schema.json",
    "administratum_composition_receipt": "administratum_bundle_gate_receipt.schema.json",
}

TEXT_SCHEMA_CLASSES = {"sha256_sums", "final_owner_summary_boundary"}
GENERATED_FIXTURE_FILES = {
    "task_report_bundle.zip",
    V02_GATE_RECEIPT,
    SCHEMA_VALIDATION_RECEIPT,
    DIGEST_RECEIPT,
    MISSING_REQUEST,
    "bundle_packager_receipt.json",
    "SELF_REFERENCE_LIMIT.md",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def norm_path_text(value: str) -> str:
    return value.replace("\\", "/").rstrip("/")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def schema_dir() -> Path:
    return Path(__file__).resolve().parent / "SCHEMAS"


def v02_matrix_classes() -> tuple[Any, ...]:
    classes: list[Any] = []
    for item in V01_MATRIX_CLASSES:
        patterns = item.patterns
        if item.class_id == "commit_chain_identifiers":
            patterns = tuple(dict.fromkeys((*patterns, "commit_chain_receipt.json")))
        elif item.class_id == "git_closure_and_remote_closure_proof":
            patterns = tuple(dict.fromkeys((*patterns, "remote_head_proof_receipt.json")))
        elif item.class_id == "worktree_clean_or_explicit_cap_receipt":
            patterns = tuple(dict.fromkeys((*patterns, "remote_head_proof_receipt.json")))
        elif item.class_id == "administratum_composition_receipt":
            patterns = tuple(dict.fromkeys((*patterns, V02_GATE_RECEIPT)))
        classes.append(replace(item, patterns=patterns))
    return tuple(classes)


MATRIX_CLASSES = v02_matrix_classes()


def load_json_file(path: Path) -> tuple[Any | None, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except json.JSONDecodeError as exc:
        return None, f"{exc.msg} at line {exc.lineno} column {exc.colno}"


def load_adjacent_manifest(report_dir: Path) -> tuple[dict[str, Any], str]:
    path = report_dir / ADJACENT_MANIFEST
    if not path.is_file():
        return {"adjacent_files": []}, "missing adjacent receipts manifest"
    payload, error = load_json_file(path)
    if error:
        return {"adjacent_files": []}, error
    if not isinstance(payload, dict):
        return {"adjacent_files": []}, "manifest root is not an object"
    payload.setdefault("adjacent_files", [])
    return payload, ""


def class_matches(report_dir: Path, item: Any, manifest: dict[str, Any], receipt_path: Path | None) -> tuple[list[str], list[str]]:
    actual = glob_matches(report_dir, item.patterns)
    if item.directory_name_task_id and report_dir.name.startswith("TASK-"):
        actual.append(f"{report_dir.name}/")
    if item.produced_by_gate and receipt_path is not None and receipt_path.parent.resolve() == report_dir.resolve():
        actual.append(receipt_path.name)
    adjacent = adjacent_matches(report_dir, manifest, item.class_id) if item.adjacent_allowed else []
    return sorted(set(actual)), sorted(set(adjacent))


def evidence_files(report_dir: Path, rel_paths: list[str]) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    for rel_path in rel_paths:
        if rel_path.endswith("/"):
            continue
        normalized = rel_path.replace("\\", "/")
        if normalized in seen:
            continue
        seen.add(normalized)
        candidate = report_dir / rel_path
        if candidate.is_file():
            files.append(candidate)
    return files


def load_schema_for_class(class_id: str) -> tuple[dict[str, Any] | None, str]:
    schema_name = SCHEMA_BY_CLASS.get(class_id)
    if not schema_name:
        return None, ""
    path = schema_dir() / schema_name
    if not path.is_file():
        return None, f"schema file missing: {to_posix(path)}"
    payload, error = load_json_file(path)
    if error:
        return None, f"schema file malformed: {to_posix(path)}: {error}"
    if not isinstance(payload, dict):
        return None, f"schema file root is not an object: {to_posix(path)}"
    return payload, to_posix(path)


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
    if "anyOf" in schema:
        branch_errors = [validate_schema(instance, branch, path) for branch in schema["anyOf"]]
        if not any(not branch for branch in branch_errors):
            errors.append(f"{path}: does not satisfy any accepted field set")
    expected_type = schema.get("type")
    if isinstance(expected_type, list):
        if not any(type_matches(instance, item) for item in expected_type):
            errors.append(f"{path}: expected one of {expected_type}")
            return errors
    elif isinstance(expected_type, str) and not type_matches(instance, expected_type):
        errors.append(f"{path}: expected {expected_type}")
        return errors
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
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, subschema in properties.items():
                if key in instance and isinstance(subschema, dict):
                    errors.extend(validate_schema(instance[key], subschema, f"{path}.{key}"))
        if schema.get("additionalProperties") is False:
            allowed = set(properties)
            for key in instance:
                if key not in allowed:
                    errors.append(f"{path}.{key}: additional property not allowed")
    return errors


def add_issue(issues: list[dict[str, Any]], *, class_id: str, rel_path: str, field: str, message: str, severity: str = "BLOCK") -> None:
    issues.append(
        {
            "class_id": class_id,
            "path": rel_path,
            "field": field,
            "message": message,
            "severity": severity,
        }
    )


def validate_task_id(payload: Any, *, expected_task_id: str, class_id: str, rel_path: str, issues: list[dict[str, Any]]) -> None:
    if not isinstance(payload, dict):
        return
    task_id = payload.get("task_id")
    if task_id is None:
        add_issue(issues, class_id=class_id, rel_path=rel_path, field="task_id", message="required task_id is missing")
    elif not isinstance(task_id, str) or not task_id:
        add_issue(issues, class_id=class_id, rel_path=rel_path, field="task_id", message="task_id must be a non-empty string")
    elif task_id != expected_task_id:
        add_issue(
            issues,
            class_id=class_id,
            rel_path=rel_path,
            field="task_id",
            message=f"task_id {task_id!r} does not match expected {expected_task_id!r}",
        )


def validate_active_root(
    payload: Any,
    *,
    active_root: str,
    ancient_root: str,
    class_id: str,
    rel_path: str,
    issues: list[dict[str, Any]],
) -> None:
    if not isinstance(payload, dict):
        return
    active_value = payload.get("active_root") or payload.get("active_root_resolved")
    if active_value is None:
        return
    if not isinstance(active_value, str) or not active_value:
        add_issue(issues, class_id=class_id, rel_path=rel_path, field="active_root", message="active_root must be a non-empty string")
        return
    normalized = norm_path_text(active_value).lower()
    expected = norm_path_text(active_root).lower()
    ancient = norm_path_text(ancient_root).lower()
    if normalized != expected:
        add_issue(
            issues,
            class_id=class_id,
            rel_path=rel_path,
            field="active_root",
            message=f"active_root {active_value!r} does not match {active_root!r}",
        )
    if normalized == ancient or normalized.startswith(ancient + "/"):
        add_issue(
            issues,
            class_id=class_id,
            rel_path=rel_path,
            field="active_root",
            message="Ancient Empire path is not allowed as active root",
        )


def validate_no_ancient_core(
    payload: Any,
    *,
    active_root: str,
    class_id: str,
    rel_path: str,
    issues: list[dict[str, Any]],
) -> None:
    if class_id != "scope_lock_no_ancient_mutation_receipt" or not isinstance(payload, dict):
        return
    if "active_root" not in payload:
        add_issue(issues, class_id=class_id, rel_path=rel_path, field="active_root", message="no-Ancient receipt must record active_root")
    core_fields = {"ancient_empire_mutated", "mutation_detected", "write_attempted"}
    if not any(field in payload for field in core_fields):
        add_issue(
            issues,
            class_id=class_id,
            rel_path=rel_path,
            field="ancient_mutation_core",
            message="no-Ancient receipt must include ancient_empire_mutated, mutation_detected, or write_attempted",
        )
    if payload.get("ancient_empire_mutated") is True or payload.get("mutation_detected") is True or payload.get("write_attempted") is True:
        add_issue(
            issues,
            class_id=class_id,
            rel_path=rel_path,
            field="ancient_mutation_core",
            message="no-Ancient receipt cannot pass when mutation/write is true",
        )
    if payload.get("active_root") and norm_path_text(str(payload["active_root"])).lower() != norm_path_text(active_root).lower():
        add_issue(
            issues,
            class_id=class_id,
            rel_path=rel_path,
            field="active_root",
            message="no-Ancient receipt active_root does not match New Reality root",
        )


def iter_json_strings(value: Any, field_path: str = "$") -> list[tuple[str, str]]:
    strings: list[tuple[str, str]] = []
    if isinstance(value, str):
        strings.append((field_path, value))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            strings.extend(iter_json_strings(item, f"{field_path}[{index}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            strings.extend(iter_json_strings(item, f"{field_path}.{key}"))
    return strings


def validate_authority_boundary(payload: Any, *, class_id: str, rel_path: str, issues: list[dict[str, Any]]) -> None:
    if not isinstance(payload, dict):
        return
    for field_path, value in iter_json_strings(payload):
        if field_path.rsplit(".", 1)[-1] in {"verdict", "claim", "gate", "admission_verdict"} and value in FORBIDDEN_AUTHORITY_CLAIMS:
            add_issue(
                issues,
                class_id=class_id,
                rel_path=rel_path,
                field=field_path,
                message=f"Administratum V0.2 may not claim {value}",
            )


def validate_bundle_sha(report_dir: Path, payload: Any, *, class_id: str, rel_path: str, issues: list[dict[str, Any]]) -> None:
    if not isinstance(payload, dict):
        return
    if rel_path in SHA_SELF_REFERENCE_SKIP:
        return
    bundle_sha = payload.get("bundle_sha256")
    if not bundle_sha:
        return
    if not isinstance(bundle_sha, str) or not SHA256_RE.match(bundle_sha):
        add_issue(issues, class_id=class_id, rel_path=rel_path, field="bundle_sha256", message="bundle_sha256 must be a 64-character hex string")
        return
    bundle_path = payload.get("bundle_path")
    candidate = report_dir / "task_report_bundle.zip"
    if isinstance(bundle_path, str) and bundle_path:
        bundle_candidate = Path(bundle_path)
        if not bundle_candidate.is_absolute():
            candidate = report_dir / bundle_candidate
        else:
            candidate = bundle_candidate
    if candidate.is_file():
        actual = sha256_file(candidate)
        if actual.lower() != bundle_sha.lower():
            add_issue(
                issues,
                class_id=class_id,
                rel_path=rel_path,
                field="bundle_sha256",
                message=f"bundle_sha256 is stale or mismatched; actual {actual}",
            )


def validate_adjacent_manifest_payload(report_dir: Path, payload: Any, *, class_id: str, rel_path: str, issues: list[dict[str, Any]]) -> None:
    if class_id != "adjacent_receipts_manifest" or not isinstance(payload, dict):
        return
    entries = payload.get("adjacent_files", [])
    if not isinstance(entries, list):
        add_issue(issues, class_id=class_id, rel_path=rel_path, field="adjacent_files", message="adjacent_files must be an array")
        return
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            add_issue(issues, class_id=class_id, rel_path=rel_path, field=f"adjacent_files[{index}]", message="adjacent entry must be an object")
            continue
        entry_path = entry.get("path")
        if not isinstance(entry_path, str) or not entry_path:
            add_issue(issues, class_id=class_id, rel_path=rel_path, field=f"adjacent_files[{index}].path", message="adjacent entry path missing")
            continue
        if not (report_dir / entry_path).is_file() and entry.get("status") == "ADJACENT_SELF_REFERENCE_LIMIT":
            continue
        if not (report_dir / entry_path).is_file():
            add_issue(
                issues,
                class_id=class_id,
                rel_path=rel_path,
                field=f"adjacent_files[{index}].path",
                message=f"adjacent file does not exist: {entry_path}",
            )


def validate_sha256sums(report_dir: Path, path: Path, *, class_id: str, issues: list[dict[str, Any]]) -> None:
    rel_path = path.relative_to(report_dir).as_posix()
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        add_issue(issues, class_id=class_id, rel_path=rel_path, field="sha256sums", message="sha256sums file is empty")
        return
    for index, line in enumerate(lines, start=1):
        parts = line.split(None, 1)
        if len(parts) != 2 or not SHA256_RE.match(parts[0]):
            add_issue(issues, class_id=class_id, rel_path=rel_path, field=f"line_{index}", message="sha256 line must be '<64 hex>  <path>'")
            continue
        listed_path = parts[1].strip()
        if listed_path in SHA_SELF_REFERENCE_SKIP:
            continue
        candidate = report_dir / listed_path
        if candidate.is_file():
            actual = sha256_file(candidate)
            if actual.lower() != parts[0].lower():
                add_issue(
                    issues,
                    class_id=class_id,
                    rel_path=rel_path,
                    field=f"line_{index}",
                    message=f"sha256 mismatch for {listed_path}; actual {actual}",
                )


def has_officio_localization_exception(report_dir: Path) -> bool:
    for name in ("OFFICIO_LOCALIZATION_REFERENCE.json", "OFFICIO_LOCALIZATION_REFERENCE.md", "OWNER_RESPONSE_BOUNDARY.md"):
        path = report_dir / name
        if not path.is_file():
            continue
        if path.suffix.lower() == ".json":
            payload, error = load_json_file(path)
            if not error and isinstance(payload, dict):
                return True
        else:
            return True
    return False


def validate_owner_language_boundary(report_dir: Path, issues: list[dict[str, Any]]) -> None:
    has_exception = has_officio_localization_exception(report_dir)
    for path in sorted(report_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in REPORT_TEXT_EXTENSIONS:
            continue
        rel_path = path.relative_to(report_dir).as_posix()
        if rel_path in {"SELF_REFERENCE_LIMIT.md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if CYRILLIC_RE.search(text) and not has_exception:
            add_issue(
                issues,
                class_id="final_owner_summary_boundary",
                rel_path=rel_path,
                field="owner_facing_language_boundary",
                message="Cyrillic owner-facing text found in machine bundle without Officio localization exception",
            )


def validate_report(
    report_dir: Path,
    *,
    task_id: str,
    active_root: str,
    ancient_root: str,
    receipt_path: Path | None,
) -> dict[str, Any]:
    repo_root = find_repo_root(report_dir)
    report_dir = ensure_under(repo_root, report_dir)
    manifest, manifest_error = load_adjacent_manifest(report_dir)
    class_results: list[dict[str, Any]] = []
    missing_required: list[str] = []
    invalid_fields: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    schemas_checked: list[str] = []
    files_checked: list[str] = []

    for item in MATRIX_CLASSES:
        actual, adjacent = class_matches(report_dir, item, manifest, receipt_path)
        present = bool(actual or adjacent)
        if item.required and not present:
            missing_required.append(item.class_id)
        row_files = evidence_files(report_dir, actual + adjacent)
        produced_by_this_gate = (
            item.produced_by_gate
            and receipt_path is not None
            and receipt_path.parent.resolve() == report_dir.resolve()
        )
        row = {
            "class_id": item.class_id,
            "required": item.required,
            "present": present,
            "actual_matches": actual,
            "adjacent_matches": adjacent,
            "description": item.description,
        }
        class_results.append(row)
        if not present:
            continue
        schema, schema_path = load_schema_for_class(item.class_id)
        if schema_path:
            schemas_checked.append(schema_path)
        elif item.required and item.class_id not in TEXT_SCHEMA_CLASSES:
            warnings.append(
                {
                    "class_id": item.class_id,
                    "path": "",
                    "message": f"no schema registered for required class {item.class_id}",
                    "severity": "WARN",
                }
            )
        schema_capable = False
        for file_path in row_files:
            rel_path = file_path.relative_to(report_dir).as_posix()
            files_checked.append(rel_path)
            if item.class_id == "sha256_sums":
                validate_sha256sums(report_dir, file_path, class_id=item.class_id, issues=invalid_fields)
                schema_capable = True
                continue
            if file_path.suffix.lower() != ".json":
                continue
            schema_capable = True
            payload, error = load_json_file(file_path)
            if error:
                add_issue(invalid_fields, class_id=item.class_id, rel_path=rel_path, field="$", message=f"malformed JSON: {error}")
                continue
            if schema:
                for schema_error in validate_schema(payload, schema):
                    add_issue(invalid_fields, class_id=item.class_id, rel_path=rel_path, field="$", message=schema_error)
            validate_task_id(payload, expected_task_id=task_id, class_id=item.class_id, rel_path=rel_path, issues=invalid_fields)
            validate_active_root(
                payload,
                active_root=active_root,
                ancient_root=ancient_root,
                class_id=item.class_id,
                rel_path=rel_path,
                issues=invalid_fields,
            )
            validate_no_ancient_core(payload, active_root=active_root, class_id=item.class_id, rel_path=rel_path, issues=invalid_fields)
            validate_authority_boundary(payload, class_id=item.class_id, rel_path=rel_path, issues=invalid_fields)
            validate_bundle_sha(report_dir, payload, class_id=item.class_id, rel_path=rel_path, issues=invalid_fields)
            validate_adjacent_manifest_payload(report_dir, payload, class_id=item.class_id, rel_path=rel_path, issues=invalid_fields)
        if item.required and schema and not schema_capable and item.class_id not in TEXT_SCHEMA_CLASSES and not produced_by_this_gate:
            warnings.append(
                {
                    "class_id": item.class_id,
                    "path": "",
                    "message": "required class is present only through non-JSON evidence or directory name; schema coverage is limited",
                    "severity": "WARN",
                }
            )

    if manifest_error:
        add_issue(
            invalid_fields,
            class_id="adjacent_receipts_manifest",
            rel_path=ADJACENT_MANIFEST,
            field="$",
            message=manifest_error,
        )
    if (report_dir / "bundle_file_inventory.json").is_file() and not (report_dir / ADJACENT_MANIFEST).is_file():
        add_issue(
            invalid_fields,
            class_id="adjacent_receipts_manifest",
            rel_path=ADJACENT_MANIFEST,
            field="$",
            message="bundle inventory exists but adjacent receipts manifest is missing",
        )
    validate_owner_language_boundary(report_dir, invalid_fields)

    composition_gate = COMPOSITION_BLOCK if missing_required else COMPOSITION_PASS
    schema_gate = SCHEMA_BLOCK if invalid_fields else (SCHEMA_WARN if warnings else SCHEMA_PASS)
    verdict = SCHEMA_BLOCK if composition_gate == COMPOSITION_BLOCK or schema_gate == SCHEMA_BLOCK else SCHEMA_PASS

    return {
        "task_id": task_id,
        "verdict": verdict,
        "composition_gate": composition_gate,
        "schema_gate": schema_gate,
        "authority_boundary": "composition_schema_only",
        "matrix_version": MATRIX_VERSION,
        "checked_path": to_posix(report_dir),
        "active_root_expected": active_root,
        "ancient_root_forbidden": ancient_root,
        "missing_items": missing_required,
        "invalid_fields": invalid_fields,
        "warnings": warnings,
        "created_utc": utc_now(),
        "required_class_count": sum(1 for item in MATRIX_CLASSES if item.required),
        "present_required_class_count": sum(1 for row in class_results if row["required"] and row["present"]),
        "class_results": class_results,
        "schemas_checked": sorted(set(schemas_checked)),
        "files_checked": sorted(set(files_checked)),
        "claims_allowed": sorted([COMPOSITION_PASS, COMPOSITION_BLOCK, SCHEMA_PASS, SCHEMA_BLOCK, "BUNDLE_PACKAGING_PASS"]),
        "claims_forbidden": sorted(FORBIDDEN_AUTHORITY_CLAIMS),
        "notes": "Administratum V0.2 checks bundle composition and minimal schema/field contracts only; no semantic truth admission is claimed.",
    }


def build_schema_validation_receipt(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": result["task_id"],
        "schema_validation_verdict": result["schema_gate"],
        "schemas_checked": result["schemas_checked"],
        "files_checked": result["files_checked"],
        "errors": result["invalid_fields"],
        "warnings": result["warnings"],
        "created_utc": utc_now(),
    }


def build_digest(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": result["task_id"],
        "digest_verdict": result["verdict"],
        "checked_path": result["checked_path"],
        "missing_required_files": result["missing_items"],
        "invalid_required_fields": result["invalid_fields"],
        "warning_fields": result["warnings"],
        "owner_action_required": bool(result["missing_items"] or result["invalid_fields"]),
        "created_utc": utc_now(),
    }


def build_missing_request(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": SCHEMA_BLOCK,
        "task_id": result["task_id"],
        "matrix_version": MATRIX_VERSION,
        "checked_path": result["checked_path"],
        "missing_required_items": result["missing_items"],
        "invalid_fields": result["invalid_fields"],
        "required_action": "Add missing report bundle classes or repair invalid required fields, then replay Administratum V0.2.",
        "timestamp_utc": utc_now(),
    }


def write_gate_outputs(
    result: dict[str, Any],
    *,
    receipt_path: Path,
    schema_receipt_path: Path,
    digest_path: Path,
    missing_request_path: Path,
    bundle_created: bool = False,
    bundle_path: Path | None = None,
    bundle_sha256: str = "",
) -> dict[str, Any]:
    receipt = dict(result)
    receipt["bundle_created"] = bundle_created
    if bundle_path is not None:
        receipt["bundle_path"] = to_posix(bundle_path)
    if bundle_sha256:
        receipt["bundle_sha256"] = bundle_sha256
    write_json(receipt_path, receipt)
    write_json(schema_receipt_path, build_schema_validation_receipt(receipt))
    write_json(digest_path, build_digest(receipt))
    if receipt["verdict"] == SCHEMA_BLOCK:
        write_json(missing_request_path, build_missing_request(receipt))
    return receipt


def base_fixture_payload(task_id: str) -> dict[str, dict[str, Any] | str]:
    return {
        "TASK_FOCUS_PACKET.json": {
            "task_id": task_id,
            "step_name": "Administratum V0.2 complete fixture",
            "active_root": ACTIVE_ROOT_DEFAULT,
            "machine_artifact_language": "English",
        },
        "commit_chain_receipt.json": {
            "task_id": task_id,
            "verdict": "PASS_WITH_SELF_REFERENCE_LIMIT",
            "branch": "fixture",
            "head_commit": "0" * 40,
            "commit_ids": ["0" * 40],
        },
        "git_closure_receipt.json": {
            "task_id": task_id,
            "verdict": "PASS_WITH_SELF_REFERENCE_LIMIT",
            "branch": "fixture",
            "worktree_clean": True,
            "origin_master_equals_head": True,
        },
        "remote_closure_receipt.json": {
            "task_id": task_id,
            "verdict": "PASS_WITH_SELF_REFERENCE_LIMIT",
            "origin_master_equals_head": True,
            "remote": "fixture",
        },
        "no_ancient_mutation_receipt.json": {
            "task_id": task_id,
            "verdict": "PASS_WITH_SCOPE_LOCK",
            "active_root": ACTIVE_ROOT_DEFAULT,
            "ancient_empire_mutated": False,
            "write_attempted": False,
            "forbidden_write_roots": [ANCIENT_ROOT_DEFAULT],
        },
        "CLAIM_LEDGER.json": {
            "task_id": task_id,
            "claims": [
                {
                    "claim": "Administratum V0.2 fixture is structurally complete.",
                    "evidence": "fixture files",
                    "verdict": "PASS",
                }
            ],
        },
        "CAPABILITY_SPLIT_RECEIPT.json": {
            "task_id": task_id,
            "verdict": "PASS",
            "authority_boundary": "composition_schema_only",
            "owned_claims": [COMPOSITION_PASS, SCHEMA_PASS],
        },
        "RED_TEAM_VERDICT.json": {
            "task_id": task_id,
            "verdict": "PASS_WITH_SCOPE_LIMIT",
            "review_scope": "fixture structural/schema replay",
            "residual_risk": ["No semantic truth admission is claimed."],
        },
        "OFFICIO_LOCALIZATION_REFERENCE.json": {
            "task_id": task_id,
            "owner_facing_language_boundary": "Owner-facing Russian is runtime-only through Officio; machine artifacts stay English.",
            "machine_artifact_language": "English",
        },
        "bundle_file_inventory.json": {
            "task_id": task_id,
            "inventory_type": "task_report_bundle_file_inventory",
            "included_file_count": 0,
            "included_files": [],
            "adjacent_self_reference_files": [],
        },
        ADJACENT_MANIFEST: {
            "manifest_type": "adjacent_receipts_manifest",
            "task_id": task_id,
            "matrix_version": MATRIX_VERSION,
            "adjacent_files": [
                {
                    "path": V02_GATE_RECEIPT,
                    "class_ids": ["administratum_composition_receipt"],
                    "status": "ADJACENT_SELF_REFERENCE_LIMIT",
                },
                {
                    "path": "bundle_file_inventory.json",
                    "class_ids": ["bundle_manifest_and_file_inventory"],
                    "status": "ADJACENT_SELF_REFERENCE_LIMIT",
                },
                {
                    "path": "sha256sums.txt",
                    "class_ids": ["sha256_sums"],
                    "status": "ADJACENT_SELF_REFERENCE_LIMIT",
                },
            ],
        },
        "sha256sums.txt": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  empty.txt\n",
    }


def write_fixture_file(path: Path, value: dict[str, Any] | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        write_json(path, value)


def write_base_fixture(path: Path, task_id: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for rel_path in GENERATED_FIXTURE_FILES:
        (path / rel_path).unlink(missing_ok=True)
    (path / "empty.txt").write_text("", encoding="utf-8")
    for rel_path, payload in base_fixture_payload(task_id).items():
        write_fixture_file(path / rel_path, payload)


def write_fixture_suite(fixtures_root: Path) -> dict[str, Any]:
    repo_root = find_repo_root(fixtures_root)
    fixtures_root = ensure_under(repo_root, fixtures_root)
    fixtures_root.mkdir(parents=True, exist_ok=True)

    fixture_names = [
        "v0_2_complete_report_fixture",
        "v0_2_missing_required_receipt_file",
        "v0_2_malformed_required_json",
        "v0_2_missing_task_id",
        "v0_2_wrong_task_id",
        "v0_2_wrong_active_root",
        "v0_2_missing_adjacent_manifest",
        "v0_2_stale_bundle_sha",
        "v0_2_missing_commit_chain",
        "v0_2_forged_no_ancient_missing_core",
        "v0_2_owner_russian_file_without_exception",
    ]
    for name in fixture_names:
        write_base_fixture(fixtures_root / name, f"FIXTURE-{name.upper().replace('-', '_')}")

    (fixtures_root / "v0_2_missing_required_receipt_file" / "CLAIM_LEDGER.json").unlink(missing_ok=True)
    (fixtures_root / "v0_2_malformed_required_json" / "CLAIM_LEDGER.json").write_text("{\n", encoding="utf-8")

    missing_task_id = fixtures_root / "v0_2_missing_task_id" / "CLAIM_LEDGER.json"
    payload, _ = load_json_file(missing_task_id)
    if isinstance(payload, dict):
        payload.pop("task_id", None)
        write_json(missing_task_id, payload)

    wrong_task_id = fixtures_root / "v0_2_wrong_task_id" / "TASK_FOCUS_PACKET.json"
    payload, _ = load_json_file(wrong_task_id)
    if isinstance(payload, dict):
        payload["task_id"] = "FORGED-WRONG-TASK-ID"
        write_json(wrong_task_id, payload)

    wrong_root = fixtures_root / "v0_2_wrong_active_root" / "TASK_FOCUS_PACKET.json"
    payload, _ = load_json_file(wrong_root)
    if isinstance(payload, dict):
        payload["active_root"] = ANCIENT_ROOT_DEFAULT
        write_json(wrong_root, payload)

    (fixtures_root / "v0_2_missing_adjacent_manifest" / ADJACENT_MANIFEST).unlink(missing_ok=True)

    stale = fixtures_root / "v0_2_stale_bundle_sha"
    with zipfile.ZipFile(stale / "task_report_bundle.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("fixture.txt", "fixture")
    payload, _ = load_json_file(stale / "bundle_file_inventory.json")
    if isinstance(payload, dict):
        payload["bundle_path"] = "task_report_bundle.zip"
        payload["bundle_sha256"] = "0" * 64
        write_json(stale / "bundle_file_inventory.json", payload)
    (stale / "sha256sums.txt").write_text(("0" * 64) + "  task_report_bundle.zip\n", encoding="utf-8")

    missing_commit = fixtures_root / "v0_2_missing_commit_chain"
    for name in ("commit_chain_receipt.json", "git_closure_receipt.json", "remote_closure_receipt.json"):
        (missing_commit / name).unlink(missing_ok=True)

    forged = fixtures_root / "v0_2_forged_no_ancient_missing_core" / "no_ancient_mutation_receipt.json"
    write_json(forged, {"task_id": "FIXTURE-V0_2_FORGED_NO_ANCIENT_MISSING_CORE", "verdict": "PASS"})

    russian = fixtures_root / "v0_2_owner_russian_file_without_exception"
    (russian / "OFFICIO_LOCALIZATION_REFERENCE.json").unlink(missing_ok=True)
    (russian / "OWNER_SUMMARY_RU.md").write_text("Итог владельцу: всё хорошо.\n", encoding="utf-8")

    return {
        "task_id": TASK_ID_DEFAULT,
        "fixture_suite_written": True,
        "fixtures_root": to_posix(fixtures_root),
        "fixtures": fixture_names,
        "created_utc": utc_now(),
    }


def run_fixture_suite(fixtures_root: Path, *, result_out: Path | None = None) -> dict[str, Any]:
    repo_root = find_repo_root(fixtures_root)
    fixtures_root = ensure_under(repo_root, fixtures_root)
    rows: list[dict[str, Any]] = []
    blocked_fake_green_cases: list[str] = []
    positive_passed = False
    for report_dir in sorted(path for path in fixtures_root.iterdir() if path.is_dir() and path.name.startswith("v0_2_")):
        expected = SCHEMA_PASS if report_dir.name == "v0_2_complete_report_fixture" else SCHEMA_BLOCK
        task_id = f"FIXTURE-{report_dir.name.upper().replace('-', '_')}"
        result = validate_report(
            report_dir,
            task_id=task_id,
            active_root=ACTIVE_ROOT_DEFAULT,
            ancient_root=ANCIENT_ROOT_DEFAULT,
            receipt_path=report_dir / V02_GATE_RECEIPT,
        )
        write_gate_outputs(
            result,
            receipt_path=report_dir / V02_GATE_RECEIPT,
            schema_receipt_path=report_dir / SCHEMA_VALIDATION_RECEIPT,
            digest_path=report_dir / DIGEST_RECEIPT,
            missing_request_path=report_dir / MISSING_REQUEST,
        )
        passed_expectation = result["verdict"] == expected
        if expected == SCHEMA_PASS:
            positive_passed = passed_expectation
        elif result["verdict"] == SCHEMA_BLOCK:
            blocked_fake_green_cases.append(report_dir.name)
        rows.append(
            {
                "fixture": report_dir.name,
                "expected_verdict": expected,
                "actual_verdict": result["verdict"],
                "expectation_met": passed_expectation,
                "missing_items": result["missing_items"],
                "invalid_field_count": len(result["invalid_fields"]),
                "invalid_fields": result["invalid_fields"][:8],
            }
        )
    verdict = "PASS" if rows and all(row["expectation_met"] for row in rows) else "FAIL"
    receipt = {
        "task_id": TASK_ID_DEFAULT,
        "fixture_verdict": verdict,
        "positive_fixture_passed": positive_passed,
        "negative_fixtures": [row for row in rows if row["fixture"] != "v0_2_complete_report_fixture"],
        "blocked_fake_green_cases": blocked_fake_green_cases,
        "fixture_rows": rows,
        "created_utc": utc_now(),
    }
    if result_out is not None:
        write_json(ensure_under(repo_root, result_out), receipt)
    return receipt


def prioritized_replay_dirs(reports_root: Path) -> list[Path]:
    priority_names = [
        "TASK-NEWGEN-PC-ADMINISTRATUM-TASK-REPORT-BUNDLE-GATE-MATRIX-AND-PACKAGER-PC-V0_1",
        "TASK-NEWGEN-PC-NEW-REALITY-SELF-FIX-CLEAN-DEV-ENV-SERVITOR-CONTROL-MECHANICUS-SKILL-ARSENAL-AND-REPO-STERILIZATION-PC-V0_1",
        "TASK-NEWGEN-PC-NEW-REALITY-FINAL-REMOTE-CLOSURE-RECEIPT-AND-NATIVE-REPLAY-PC-V0_1",
        "TASK-NEWGEN-PC-NEW-REALITY-REMOTE-TREE-BUNDLE-CLOSURE-VALIDATOR-PC-V0_1",
    ]
    selected: list[Path] = []
    for name in priority_names:
        path = reports_root / name
        if path.is_dir():
            selected.append(path)
    latest = sorted((path for path in reports_root.iterdir() if path.is_dir()), key=lambda item: item.stat().st_mtime, reverse=True)
    for path in latest:
        if path not in selected:
            selected.append(path)
        if len(selected) >= 4:
            break
    return selected[: max(3, min(4, len(selected)))]


def run_real_report_replay(reports_root: Path, *, result_out: Path | None = None) -> dict[str, Any]:
    repo_root = find_repo_root(reports_root)
    reports_root = ensure_under(repo_root, reports_root)
    selected = prioritized_replay_dirs(reports_root)
    rows: list[dict[str, Any]] = []
    for report_dir in selected:
        result = validate_report(
            report_dir,
            task_id=report_dir.name,
            active_root=ACTIVE_ROOT_DEFAULT,
            ancient_root=ANCIENT_ROOT_DEFAULT,
            receipt_path=report_dir / V02_GATE_RECEIPT,
        )
        if result["verdict"] == SCHEMA_PASS and result["warnings"]:
            replay_verdict = "WARN"
        elif result["verdict"] == SCHEMA_PASS:
            replay_verdict = "PASS"
        else:
            replay_verdict = "BLOCK"
        rows.append(
            {
                "report_folder": to_posix(report_dir),
                "task_id": report_dir.name,
                "verdict": replay_verdict,
                "gate_verdict": result["verdict"],
                "composition_gate": result["composition_gate"],
                "schema_gate": result["schema_gate"],
                "missing_items": result["missing_items"],
                "invalid_fields": result["invalid_fields"][:20],
                "warnings": result["warnings"][:20],
                "migration_required": result["verdict"] == SCHEMA_BLOCK,
            }
        )
    pass_count = sum(1 for row in rows if row["verdict"] == "PASS")
    warn_count = sum(1 for row in rows if row["verdict"] == "WARN")
    block_count = sum(1 for row in rows if row["verdict"] == "BLOCK")
    receipt = {
        "task_id": TASK_ID_DEFAULT,
        "replay_verdict": "PASS_WITH_MIGRATION_BLOCKS" if rows else "BLOCK_NO_REPORTS",
        "reports_replayed": rows,
        "pass_count": pass_count,
        "warn_count": warn_count,
        "block_count": block_count,
        "selection_note": "Prioritized Administratum V0.1 and New Reality closure reports, then latest REPORTS folders.",
        "created_utc": utc_now(),
    }
    if result_out is not None:
        write_json(ensure_under(repo_root, result_out), receipt)
    return receipt


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Administratum bundle schema gate v0.2.")
    parser.add_argument("--report-dir", default="", help="Task report directory to check.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT, help="Expected task ID for receipts.")
    parser.add_argument("--active-root", default=ACTIVE_ROOT_DEFAULT, help="Expected active root.")
    parser.add_argument("--ancient-root", default=ANCIENT_ROOT_DEFAULT, help="Forbidden Ancient root.")
    parser.add_argument("--receipt-out", default="", help=f"Gate receipt path. Defaults to report-dir/{V02_GATE_RECEIPT}.")
    parser.add_argument("--schema-receipt-out", default="", help=f"Schema receipt path. Defaults to report-dir/{SCHEMA_VALIDATION_RECEIPT}.")
    parser.add_argument("--digest-out", default="", help=f"Digest path. Defaults to report-dir/{DIGEST_RECEIPT}.")
    parser.add_argument("--missing-out", default="", help=f"Missing request path. Defaults to report-dir/{MISSING_REQUEST}.")
    parser.add_argument("--bundle-created", action="store_true", help="Mark receipt as bundle-created.")
    parser.add_argument("--bundle-path", default="", help="Bundle path to record.")
    parser.add_argument("--bundle-sha256", default="", help="Bundle SHA256 to record.")
    parser.add_argument("--allow-block-exit-zero", action="store_true", help="Return 0 even when the gate blocks.")
    parser.add_argument("--write-fixture-suite", default="", help="Create/update V0.2 positive and negative fixture suite under this root.")
    parser.add_argument("--run-fixtures", default="", help="Run V0.2 fixture suite under this root.")
    parser.add_argument("--fixture-result-out", default="", help="Optional anti-fake-green fixture receipt path.")
    parser.add_argument("--replay-reports-root", default="", help="Replay V0.2 against report folders under this root.")
    parser.add_argument("--replay-result-out", default="", help="Optional real report replay receipt path.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.write_fixture_suite:
        result = write_fixture_suite(Path(args.write_fixture_suite))
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    if args.run_fixtures:
        receipt = run_fixture_suite(
            Path(args.run_fixtures),
            result_out=Path(args.fixture_result_out) if args.fixture_result_out else None,
        )
        print(json.dumps(receipt, ensure_ascii=True, indent=2))
        return 0 if receipt["fixture_verdict"] == "PASS" else 2
    if args.replay_reports_root:
        receipt = run_real_report_replay(
            Path(args.replay_reports_root),
            result_out=Path(args.replay_result_out) if args.replay_result_out else None,
        )
        print(json.dumps(receipt, ensure_ascii=True, indent=2))
        return 0 if receipt["reports_replayed"] else 2
    if not args.report_dir:
        raise SystemExit("--report-dir is required unless fixture/replay mode is used")

    report_dir = Path(args.report_dir)
    repo_root = find_repo_root(report_dir)
    report_dir = ensure_under(repo_root, report_dir)
    receipt_path = ensure_under(repo_root, Path(args.receipt_out) if args.receipt_out else report_dir / V02_GATE_RECEIPT)
    schema_receipt_path = ensure_under(
        repo_root,
        Path(args.schema_receipt_out) if args.schema_receipt_out else report_dir / SCHEMA_VALIDATION_RECEIPT,
    )
    digest_path = ensure_under(repo_root, Path(args.digest_out) if args.digest_out else report_dir / DIGEST_RECEIPT)
    missing_path = ensure_under(repo_root, Path(args.missing_out) if args.missing_out else report_dir / MISSING_REQUEST)
    bundle_path = ensure_under(repo_root, Path(args.bundle_path)) if args.bundle_path else None
    result = validate_report(
        report_dir,
        task_id=args.task_id,
        active_root=args.active_root,
        ancient_root=args.ancient_root,
        receipt_path=receipt_path,
    )
    receipt = write_gate_outputs(
        result,
        receipt_path=receipt_path,
        schema_receipt_path=schema_receipt_path,
        digest_path=digest_path,
        missing_request_path=missing_path,
        bundle_created=args.bundle_created,
        bundle_path=bundle_path,
        bundle_sha256=args.bundle_sha256,
    )
    print(json.dumps(receipt, ensure_ascii=True, indent=2))
    if receipt["verdict"] == SCHEMA_BLOCK and not args.allow_block_exit_zero:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
