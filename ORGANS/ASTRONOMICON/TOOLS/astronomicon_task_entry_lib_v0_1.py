#!/usr/bin/env python3
"""Shared Stage2 Astronomicon intake/resolver helpers."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any

REQUIRED_ORGANS = [
    "DOCTRINARIUM",
    "OFFICIO_AGENTIS",
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]

DEFAULT_STAGE2_CAPS = [
    "CAP_STAGE1_WITH_WARNINGS_ONLY",
    "CAP_NO_IDE_VISUAL_RELEASE_YET",
    "CAP_NO_WARP_RUNTIME",
]

MANIFEST_ENTRY_NAMES = ["MANIFEST.json"]
TASK_SPEC_ENTRY_NAMES = ["TASK_SPEC.md", "01_TASK_SPEC.md", "02_TASK_SPEC.json"]
ACCEPTANCE_ENTRY_NAMES = ["ACCEPTANCE_GATES.md", "03_ACCEPTANCE_GATES.json"]
OUTPUT_ENTRY_NAMES = ["OUTPUT_REQUIREMENTS.md", "06_EVIDENCE_REQUIREMENTS.md", "07_EXPECTED_OUTPUTS.md"]
ADMISSION_VERDICTS = {"ADMISSION_PASS", "ADMISSION_PASS_WITH_WARNINGS", "ADMISSION_BLOCK"}

TASKPACK_LANGUAGE_ROOT_ENTRY_NAMES = [
    "000_START_TASK_READ_ORDER.md",
    "MANIFEST.json",
    "TASK_SPEC.md",
    "ACCEPTANCE_GATES.md",
    "OUTPUT_REQUIREMENTS.md",
    "TASK_ROUTE_MANIFEST_TEMPLATE.json",
    "TASK_START_ACK_TEMPLATE.json",
]

LANGUAGE_POLICY_REQUIRED_FIELDS = [
    "taskpack_internal_files",
    "canonical_repo_artifacts",
    "owner_facing_russian_runtime_output",
    "cyrillic_in_taskpack",
    "localization_exception",
]

TASKPACK_CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")
TASKPACK_REPLACEMENT_RE = re.compile(r"\ufffd")
TASKPACK_MOJIBAKE_PATTERNS = [
    ("MOJIBAKE_UTF8_LATIN1_C3", re.compile(r"\u00c3[\u0080-\u00bf]")),
    ("MOJIBAKE_UTF8_LATIN1_C2", re.compile(r"\u00c2[\u0080-\u00bf]")),
    ("MOJIBAKE_CP1252_QUOTES", re.compile(r"\u00e2\u0080[\u0098-\u009f]")),
    ("MOJIBAKE_D0_D1_SEQUENCE", re.compile(r"[\u00d0\u00d1][\u0080-\u00bf]")),
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def is_within(base: Path, candidate: Path) -> bool:
    base_resolved = base.resolve()
    candidate_resolved = candidate.resolve()
    try:
        candidate_resolved.relative_to(base_resolved)
        return True
    except ValueError:
        return False


def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def normalize_path(path: str | Path) -> Path:
    p = Path(path).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (Path.cwd() / p).resolve()


def build_context(repo_root: str | Path) -> dict[str, Path]:
    repo = normalize_path(repo_root)
    astro = repo / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON"
    corridor = astro / "TASK_ENTRY_CORRIDOR"
    return {
        "repo_root": repo,
        "astronomicon_root": astro,
        "task_inbox_root": astro / "TASK_INBOX",
        "registered_root": astro / "TASK_INBOX/REGISTERED",
        "task_registry_dir": astro / "TASK_REGISTRY",
        "task_registry": astro / "TASK_REGISTRY/task_registry.json",
        "legacy_stage1_registry": astro / "TASK_REGISTRY/TASK_ID_REGISTRY_STAGE1.json",
        "current_expected": astro / "TASK_REGISTRY/current_expected_task.json",
        "task_route_manifest_template": corridor / "TASK_ROUTE_MANIFEST_TEMPLATE.json",
        "task_start_ack_template": corridor / "TASK_START_ACK_TEMPLATE.json",
        "taskpack_admission_contract": corridor / "TASKPACK_ADMISSION_CONTRACT.json",
        "taskpack_intake_contract": corridor / "TASKPACK_INTAKE_CONTRACT.json",
    }


def required_organ_read_first_map() -> dict[str, str]:
    return {
        organ: f"IMPERIUM_NEW_GENERATION/ORGANS/{organ}/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md"
        for organ in REQUIRED_ORGANS
    }


def required_read_order() -> list[str]:
    read_order = [
        "AGENTS.md",
        "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md",
    ]
    read_order.extend(required_organ_read_first_map().values())
    return read_order


def load_or_init_registry(registry_path: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    if not registry_path.exists():
        return {"schema_version": "0.1", "tasks": []}, warnings
    try:
        data = read_json(registry_path)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Registry JSON decode error: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Registry root must be a JSON object.")
    tasks = data.get("tasks")
    if tasks is None:
        warnings.append("Registry missing 'tasks'; initialized to empty list.")
        data["tasks"] = []
    elif not isinstance(tasks, list):
        raise ValueError("Registry 'tasks' must be a list.")
    return data, warnings


def load_stage1_entries(stage1_registry_path: Path) -> list[dict[str, Any]]:
    if not stage1_registry_path.exists():
        return []
    try:
        data = read_json(stage1_registry_path)
    except Exception:
        return []
    entries = data.get("entries")
    if isinstance(entries, list):
        return [row for row in entries if isinstance(row, dict)]
    return []


def find_zip_member(names: list[str], candidates: list[str]) -> str | None:
    normalized = {name.replace("\\", "/"): name for name in names}
    for candidate in candidates:
        candidate_norm = candidate.replace("\\", "/")
        if candidate_norm in normalized:
            return normalized[candidate_norm]
        suffix = "/" + candidate_norm
        matches = [original for norm, original in normalized.items() if norm.endswith(suffix)]
        if len(matches) == 1:
            return matches[0]
    return None


def has_utf8_bom(raw: bytes) -> bool:
    return raw.startswith(b"\xef\xbb\xbf")


def validate_manifest_language_policy(manifest: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    caps: list[str] = []
    language_policy = manifest.get("language_and_encoding_policy")
    if not isinstance(language_policy, dict):
        issues.append("MANIFEST.language_and_encoding_policy is missing or not an object.")
        caps.append("CAP_ASTRONOMICON_ADMISSION_LANGUAGE_GATE_MISSING")
        caps.append("CAP_OWNER_LANGUAGE_NOT_ROUTED_THROUGH_OFFICIO")
        return issues, caps

    missing_fields = [field for field in LANGUAGE_POLICY_REQUIRED_FIELDS if field not in language_policy]
    if missing_fields:
        issues.append(
            "MANIFEST.language_and_encoding_policy missing required fields: " + ", ".join(missing_fields)
        )
        caps.append("CAP_ASTRONOMICON_ADMISSION_LANGUAGE_GATE_MISSING")

    owner_runtime = str(language_policy.get("owner_facing_russian_runtime_output", "")).upper()
    if "OFFICIO" not in owner_runtime:
        issues.append(
            "MANIFEST owner-facing Russian runtime policy is not routed through Officio authority."
        )
        caps.append("CAP_OWNER_LANGUAGE_NOT_ROUTED_THROUGH_OFFICIO")

    taskpack_policy = str(language_policy.get("taskpack_internal_files", "")).upper()
    canonical_policy = str(language_policy.get("canonical_repo_artifacts", "")).upper()
    if "ENGLISH" not in taskpack_policy or "UTF8" not in taskpack_policy:
        issues.append("MANIFEST taskpack_internal_files policy is not explicit ENGLISH + UTF8.")
        caps.append("CAP_NON_ENGLISH_TASKPACK_INTERNAL_TEXT")
    if "ENGLISH" not in canonical_policy or "UTF8" not in canonical_policy:
        issues.append("MANIFEST canonical_repo_artifacts policy is not explicit ENGLISH + UTF8.")
        caps.append("CAP_OWNER_LANGUAGE_NOT_ROUTED_THROUGH_OFFICIO")

    return issues, caps


def validate_taskpack_language_root_files(
    zip_file: zipfile.ZipFile,
    zip_names: list[str],
) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    caps: list[str] = []
    for candidate in TASKPACK_LANGUAGE_ROOT_ENTRY_NAMES:
        member = find_zip_member(zip_names, [candidate])
        if member is None:
            continue
        raw = zip_file.read(member)
        if has_utf8_bom(raw):
            issues.append(f"UTF-8 BOM detected in root taskpack file: {candidate}")
            caps.append("CAP_UTF8_BOM_NOT_DETECTED")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            issues.append(f"UTF-8 decode error in root taskpack file {candidate}: {exc}")
            caps.append("CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED")
            continue
        if TASKPACK_REPLACEMENT_RE.search(text):
            issues.append(f"Replacement character detected in root taskpack file: {candidate}")
            caps.append("CAP_REPLACEMENT_CHARACTER_NOT_DETECTED")
        if TASKPACK_CYRILLIC_RE.search(text):
            issues.append(f"Cyrillic detected in root taskpack file: {candidate}")
            caps.append("CAP_NON_ENGLISH_TASKPACK_INTERNAL_TEXT")
        for signature_id, pattern in TASKPACK_MOJIBAKE_PATTERNS:
            if pattern.search(text):
                issues.append(f"Mojibake signature {signature_id} detected in root taskpack file: {candidate}")
                caps.append("CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED")
                break
    return issues, caps


def detect_unsafe_members(infos: list[zipfile.ZipInfo], extract_root: Path) -> list[str]:
    unsafe: list[str] = []
    base = extract_root.resolve()
    for info in infos:
        raw = info.filename.replace("\\", "/")
        if raw.startswith("/") or raw.startswith("../") or "/../" in raw:
            unsafe.append(info.filename)
            continue
        target = (extract_root / raw).resolve()
        if not is_within(base, target):
            unsafe.append(info.filename)
    return unsafe


def validate_route_template(route_template_data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required_organs = route_template_data.get("required_organs", [])
    if not isinstance(required_organs, list):
        issues.append("Route template required_organs is not a list.")
    else:
        missing = [org for org in REQUIRED_ORGANS if org not in required_organs]
        if missing:
            issues.append("Route template missing required organs: " + ", ".join(missing))
    read_order = route_template_data.get("read_order", [])
    if not isinstance(read_order, list):
        issues.append("Route template read_order is not a list.")
    return issues


def normalize_slashes(path_value: str | Path) -> str:
    return str(path_value).replace("\\", "/")


def contains_root_taskpack_inbox_marker(path_value: str | Path) -> bool:
    normalized = normalize_slashes(path_value).lower()
    return (
        normalized.startswith("_taskpack_inbox/")
        or normalized.startswith("./_taskpack_inbox/")
        or "/_taskpack_inbox/" in normalized
    )


def validate_registered_paths(
    ctx: dict[str, Path],
    *,
    registered_task_path: Path,
    taskpack_zip_path: Path,
    extracted_path: Path,
    route_manifest_path: Path,
) -> list[str]:
    issues: list[str] = []
    if not is_within(ctx["registered_root"], registered_task_path):
        issues.append("registered_task_path escapes TASK_INBOX/REGISTERED root.")
    if not is_within(registered_task_path, taskpack_zip_path):
        issues.append("taskpack_zip_path is outside registered task path.")
    if not is_within(registered_task_path, extracted_path):
        issues.append("extracted_path is outside registered task path.")
    if not is_within(registered_task_path, route_manifest_path):
        issues.append("route_manifest_path is outside registered task path.")
    return issues


def load_admission_receipt(
    receipt_path: Path,
    expected_task_id: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    issues: list[str] = []
    if not receipt_path.exists():
        issues.append(f"Admission receipt missing: {receipt_path}")
        return None, issues
    try:
        payload = read_json(receipt_path)
    except Exception as exc:
        issues.append(f"Admission receipt JSON invalid: {exc}")
        return None, issues
    if not isinstance(payload, dict):
        issues.append("Admission receipt root is not a JSON object.")
        return None, issues

    receipt_task_id = str(payload.get("task_id", "")).strip()
    if not receipt_task_id:
        issues.append("Admission receipt missing task_id.")
    elif receipt_task_id != expected_task_id:
        issues.append(
            f"Admission receipt task_id mismatch: expected '{expected_task_id}', got '{receipt_task_id}'."
        )

    verdict = str(payload.get("admission_verdict", "")).strip()
    if verdict not in ADMISSION_VERDICTS:
        issues.append(f"Admission receipt has unknown admission_verdict: '{verdict}'.")

    return payload, issues


def read_extracted_manifest_task_id(extracted_path: Path) -> tuple[str | None, list[str]]:
    warnings: list[str] = []
    if not extracted_path.exists():
        return None, warnings
    manifests = sorted(path for path in extracted_path.rglob("MANIFEST.json") if path.is_file())
    if not manifests:
        warnings.append("No MANIFEST.json found under extracted taskpack path.")
        return None, warnings

    for manifest_path in manifests:
        try:
            payload = read_json(manifest_path)
        except Exception as exc:
            warnings.append(f"Cannot parse extracted manifest '{manifest_path}': {exc}")
            continue
        task_id = str(payload.get("task_id", "")).strip()
        if task_id:
            if len(manifests) > 1:
                warnings.append(
                    f"Multiple MANIFEST.json files detected under extracted path; "
                    f"using '{manifest_path}'."
                )
            return task_id, warnings

    warnings.append("Extracted MANIFEST.json files found, but none contain task_id.")
    return None, warnings


def build_route_manifest(
    task_id: str,
    source_zip_path: Path,
    registered_zip_path: Path,
    extracted_path: Path,
    manifest: dict[str, Any],
    route_template: dict[str, Any],
) -> dict[str, Any]:
    route = dict(route_template)
    route["task_id"] = task_id
    route["taskpack_zip_path"] = str(registered_zip_path).replace("\\", "/")
    route["source_zip_path"] = str(source_zip_path).replace("\\", "/")
    route["extracted_taskpack_path"] = str(extracted_path).replace("\\", "/")
    route["required_organs"] = REQUIRED_ORGANS
    route["read_order"] = required_read_order()
    route["entry_ack_required"] = True
    route["resolver_receipt_required"] = True
    route["caps_to_carry"] = list(DEFAULT_STAGE2_CAPS)
    route["taskpack_id"] = manifest.get("taskpack_id", "")
    route["expected_start_head"] = manifest.get("expected_start_head", "")
    route["target_contour"] = manifest.get("target_contour", "")
    return route


def build_start_ack_template(task_id: str, repo_root: Path) -> dict[str, Any]:
    organs: dict[str, Any] = {}
    missing: list[str] = []
    for organ, rel in required_organ_read_first_map().items():
        full = repo_root / rel
        found = full.exists()
        if not found:
            missing.append(organ)
        organs[organ] = {
            "read_first_path": rel,
            "found": found,
            "status": "ACTIVE_FOR_STAGE1" if found else "MISSING_READ_FIRST",
        }
    caps: list[str] = []
    if missing:
        caps.append("CAP_ORGAN_READ_FIRST_ACK_MISSING")
    verdict = "PASS_WITH_WARNINGS" if not missing else "BLOCK"
    return {
        "task_id": task_id,
        "resolved": not missing,
        "route_manifest_found": True,
        "all_required_organs_reachable": not missing,
        "organs": organs,
        "caps_triggered": caps,
        "verdict": verdict,
    }


def block_admission_result(
    source_zip_path: Path,
    caps: list[str],
    warnings: list[str],
    detail: str,
) -> dict[str, Any]:
    return {
        "timestamp_utc": utc_now(),
        "source_zip_path": str(source_zip_path).replace("\\", "/"),
        "admission_verdict": "ADMISSION_BLOCK",
        "language_gate_passed": False,
        "manifest_found": False,
        "task_id_found": False,
        "task_spec_found": False,
        "acceptance_gates_found": False,
        "output_requirements_found": False,
        "duplicate_task_id": False,
        "safe_extraction_path": False,
        "registered_task_path": "",
        "extracted_path": "",
        "route_manifest_path": "",
        "current_expected_task_updated": False,
        "caps_triggered": caps,
        "warnings": warnings + [detail],
    }


def register_taskpack(
    repo_root: str | Path,
    source_zip_path: str | Path,
    actor: str = "astronomicon_taskpack_intake_v0_1.py",
) -> dict[str, Any]:
    ctx = build_context(repo_root)
    source_zip = normalize_path(source_zip_path)
    warnings: list[str] = []
    caps: list[str] = []
    detail_warnings: list[str] = []

    if not source_zip.exists():
        caps.append("CAP_TASKPACK_ADMISSION_MISSING")
        return block_admission_result(source_zip, caps, warnings, "ZIP does not exist.")
    if not source_zip.is_file():
        caps.append("CAP_TASKPACK_ADMISSION_MISSING")
        return block_admission_result(source_zip, caps, warnings, "ZIP path is not a file.")

    route_template_path = ctx["task_route_manifest_template"]
    start_ack_template_path = ctx["task_start_ack_template"]
    if not route_template_path.exists():
        caps.append("CAP_ROUTE_MANIFEST_TEMPLATE_MISSING")
        return block_admission_result(source_zip, caps, warnings, "Route manifest template is missing.")
    if not start_ack_template_path.exists():
        caps.append("CAP_TASK_START_ACK_TEMPLATE_MISSING")
        return block_admission_result(source_zip, caps, warnings, "Task start ACK template is missing.")

    try:
        route_template_data = read_json(route_template_path)
    except Exception as exc:
        caps.append("CAP_ROUTE_MANIFEST_TEMPLATE_INVALID")
        return block_admission_result(source_zip, caps, warnings, f"Invalid route template JSON: {exc}")

    route_issues = validate_route_template(route_template_data)
    if route_issues:
        caps.append("CAP_ROUTE_DOES_NOT_INCLUDE_8_ORGANS")
        return block_admission_result(source_zip, caps, warnings, "; ".join(route_issues))

    zip_sha256 = compute_sha256(source_zip)
    try:
        zip_file = zipfile.ZipFile(source_zip, "r")
    except (zipfile.BadZipFile, OSError) as exc:
        caps.append("CAP_TASKPACK_ADMISSION_MISSING")
        return block_admission_result(source_zip, caps, warnings, f"Unreadable ZIP: {exc}")

    with zip_file:
        zip_names = zip_file.namelist()
        manifest_name = find_zip_member(zip_names, MANIFEST_ENTRY_NAMES)
        task_spec_name = find_zip_member(zip_names, TASK_SPEC_ENTRY_NAMES)
        acceptance_name = find_zip_member(zip_names, ACCEPTANCE_ENTRY_NAMES)
        output_name = find_zip_member(zip_names, OUTPUT_ENTRY_NAMES)

        manifest_found = manifest_name is not None
        task_spec_found = task_spec_name is not None
        acceptance_found = acceptance_name is not None
        output_found = output_name is not None

        if not manifest_found:
            caps.append("CAP_TASKPACK_ADMISSION_MISSING")
            return {
                "timestamp_utc": utc_now(),
                "source_zip_path": str(source_zip).replace("\\", "/"),
                "zip_sha256": zip_sha256,
                "admission_verdict": "ADMISSION_BLOCK",
                "manifest_found": False,
                "task_id_found": False,
                "task_spec_found": task_spec_found,
                "acceptance_gates_found": acceptance_found,
                "output_requirements_found": output_found,
                "duplicate_task_id": False,
                "safe_extraction_path": False,
                "registered_task_path": "",
                "extracted_path": "",
                "route_manifest_path": "",
                "current_expected_task_updated": False,
                "caps_triggered": caps,
                "warnings": ["Required file missing: MANIFEST.json"],
            }

        try:
            manifest = json.loads(zip_file.read(manifest_name).decode("utf-8"))
        except Exception as exc:
            caps.append("CAP_TASKPACK_ADMISSION_MISSING")
            return block_admission_result(source_zip, caps, warnings, f"Cannot parse MANIFEST.json: {exc}")

        language_policy_issues, language_policy_caps = validate_manifest_language_policy(manifest)
        root_language_issues, root_language_caps = validate_taskpack_language_root_files(zip_file, zip_names)
        if language_policy_issues or root_language_issues:
            caps.extend(language_policy_caps)
            caps.extend(root_language_caps)
            warnings.extend(language_policy_issues)
            warnings.extend(root_language_issues)
            return {
                "timestamp_utc": utc_now(),
                "source_zip_path": str(source_zip).replace("\\", "/"),
                "zip_sha256": zip_sha256,
                "task_id": str(manifest.get("task_id", "")).strip(),
                "admission_verdict": "ADMISSION_BLOCK",
                "manifest_found": True,
                "task_id_found": bool(str(manifest.get("task_id", "")).strip()),
                "task_spec_found": task_spec_found,
                "acceptance_gates_found": acceptance_found,
                "output_requirements_found": output_found,
                "duplicate_task_id": False,
                "safe_extraction_path": False,
                "registered_task_path": "",
                "extracted_path": "",
                "route_manifest_path": "",
                "current_expected_task_updated": False,
                "language_gate_passed": False,
                "caps_triggered": sorted(set(caps)),
                "warnings": warnings,
            }

        task_id = str(manifest.get("task_id", "")).strip()
        task_id_found = bool(task_id)
        if not task_id_found:
            caps.append("CAP_TASKPACK_ADMISSION_MISSING")
            return {
                "timestamp_utc": utc_now(),
                "source_zip_path": str(source_zip).replace("\\", "/"),
                "zip_sha256": zip_sha256,
                "admission_verdict": "ADMISSION_BLOCK",
                "manifest_found": True,
                "task_id_found": False,
                "task_spec_found": task_spec_found,
                "acceptance_gates_found": acceptance_found,
                "output_requirements_found": output_found,
                "duplicate_task_id": False,
                "safe_extraction_path": False,
                "registered_task_path": "",
                "extracted_path": "",
                "route_manifest_path": "",
                "current_expected_task_updated": False,
                "caps_triggered": caps,
                "warnings": ["MANIFEST.json exists but task_id is missing."],
            }

        manifest_organs = manifest.get("organs", [])
        if not isinstance(manifest_organs, list):
            caps.append("CAP_ROUTE_DOES_NOT_INCLUDE_8_ORGANS")
            return block_admission_result(
                source_zip,
                caps,
                warnings,
                "MANIFEST.organs is missing or not a list.",
            )
        missing_manifest_organs = [organ for organ in REQUIRED_ORGANS if organ not in manifest_organs]
        if missing_manifest_organs:
            caps.append("CAP_ROUTE_DOES_NOT_INCLUDE_8_ORGANS")
            return block_admission_result(
                source_zip,
                caps,
                warnings,
                "MANIFEST.organs missing required organs: " + ", ".join(missing_manifest_organs),
            )

        if not task_spec_found:
            caps.append("CAP_TASKPACK_ADMISSION_MISSING")
            detail_warnings.append("Missing TASK_SPEC equivalent.")
        if not acceptance_found:
            caps.append("CAP_TASKPACK_ADMISSION_MISSING")
            detail_warnings.append("Missing ACCEPTANCE_GATES equivalent.")
        if not output_found:
            caps.append("CAP_TASKPACK_ADMISSION_MISSING")
            detail_warnings.append("Missing OUTPUT_REQUIREMENTS equivalent.")
        if detail_warnings:
            return {
                "timestamp_utc": utc_now(),
                "source_zip_path": str(source_zip).replace("\\", "/"),
                "zip_sha256": zip_sha256,
                "task_id": task_id,
                "admission_verdict": "ADMISSION_BLOCK",
                "manifest_found": True,
                "task_id_found": True,
                "task_spec_found": task_spec_found,
                "acceptance_gates_found": acceptance_found,
                "output_requirements_found": output_found,
                "duplicate_task_id": False,
                "safe_extraction_path": False,
                "registered_task_path": "",
                "extracted_path": "",
                "route_manifest_path": "",
                "current_expected_task_updated": False,
                "caps_triggered": caps,
                "warnings": detail_warnings,
            }

        try:
            registry_data, registry_warnings = load_or_init_registry(ctx["task_registry"])
            warnings.extend(registry_warnings)
        except ValueError as exc:
            caps.append("CAP_TASK_REGISTRY_CORRUPTION")
            return block_admission_result(source_zip, caps, warnings, str(exc))

        stage1_entries = load_stage1_entries(ctx["legacy_stage1_registry"])
        all_task_ids = [
            str(row.get("task_id", "")).strip() for row in registry_data.get("tasks", []) if isinstance(row, dict)
        ]
        all_task_ids.extend(str(row.get("task_id", "")).strip() for row in stage1_entries)
        duplicate = task_id in {task for task in all_task_ids if task}
        if duplicate:
            caps.append("CAP_DUPLICATE_TASK_ID_NOT_DETECTED")
            return {
                "timestamp_utc": utc_now(),
                "source_zip_path": str(source_zip).replace("\\", "/"),
                "zip_sha256": zip_sha256,
                "task_id": task_id,
                "admission_verdict": "ADMISSION_BLOCK",
                "manifest_found": True,
                "task_id_found": True,
                "task_spec_found": True,
                "acceptance_gates_found": True,
                "output_requirements_found": True,
                "duplicate_task_id": True,
                "safe_extraction_path": False,
                "registered_task_path": "",
                "extracted_path": "",
                "route_manifest_path": "",
                "current_expected_task_updated": False,
                "caps_triggered": caps,
                "warnings": ["Duplicate task_id detected in registry."],
            }

        registered_root = ctx["registered_root"]
        registered_task_path = registered_root / task_id
        safe_extraction_path = is_within(registered_root, registered_task_path)
        if not safe_extraction_path:
            caps.append("CAP_UNSAFE_EXTRACTION_PATH_NOT_BLOCKED")
            return block_admission_result(source_zip, caps, warnings, "Registered task path escaped REGISTERED root.")

        extract_path = registered_task_path / "EXTRACTED"
        unsafe_members = detect_unsafe_members(zip_file.infolist(), extract_path)
        if unsafe_members:
            caps.append("CAP_UNSAFE_EXTRACTION_PATH_NOT_BLOCKED")
            return {
                "timestamp_utc": utc_now(),
                "source_zip_path": str(source_zip).replace("\\", "/"),
                "zip_sha256": zip_sha256,
                "task_id": task_id,
                "admission_verdict": "ADMISSION_BLOCK",
                "manifest_found": True,
                "task_id_found": True,
                "task_spec_found": True,
                "acceptance_gates_found": True,
                "output_requirements_found": True,
                "duplicate_task_id": False,
                "safe_extraction_path": False,
                "registered_task_path": str(registered_task_path).replace("\\", "/"),
                "extracted_path": str(extract_path).replace("\\", "/"),
                "route_manifest_path": "",
                "current_expected_task_updated": False,
                "caps_triggered": caps,
                "warnings": ["Unsafe ZIP members detected: " + ", ".join(unsafe_members)],
            }

        if registered_task_path.exists():
            caps.append("CAP_DUPLICATE_TASK_ID_NOT_DETECTED")
            return {
                "timestamp_utc": utc_now(),
                "source_zip_path": str(source_zip).replace("\\", "/"),
                "zip_sha256": zip_sha256,
                "task_id": task_id,
                "admission_verdict": "ADMISSION_BLOCK",
                "manifest_found": True,
                "task_id_found": True,
                "task_spec_found": True,
                "acceptance_gates_found": True,
                "output_requirements_found": True,
                "duplicate_task_id": True,
                "safe_extraction_path": True,
                "registered_task_path": str(registered_task_path).replace("\\", "/"),
                "extracted_path": str(extract_path).replace("\\", "/"),
                "route_manifest_path": "",
                "current_expected_task_updated": False,
                "caps_triggered": caps,
                "warnings": ["Registered task directory already exists."],
            }

        registered_task_path.mkdir(parents=True, exist_ok=False)
        registered_zip_path = registered_task_path / "TASKPACK.zip"
        shutil.copy2(source_zip, registered_zip_path)
        extract_path.mkdir(parents=True, exist_ok=True)
        zip_file.extractall(extract_path)

    route_manifest = build_route_manifest(
        task_id=task_id,
        source_zip_path=source_zip,
        registered_zip_path=registered_zip_path,
        extracted_path=extract_path,
        manifest=manifest,
        route_template=route_template_data,
    )
    route_manifest_path = registered_task_path / "TASK_ROUTE_MANIFEST.json"
    write_json(route_manifest_path, route_manifest)

    start_ack = build_start_ack_template(task_id=task_id, repo_root=ctx["repo_root"])
    start_ack_path = registered_task_path / "TASK_START_ACK_TEMPLATE.json"
    write_json(start_ack_path, start_ack)
    if not start_ack["all_required_organs_reachable"]:
        caps.append("CAP_ORGAN_READ_FIRST_ACK_MISSING")

    for task in registry_data["tasks"]:
        if isinstance(task, dict) and task.get("current_expected") is True:
            task["current_expected"] = False
            if str(task.get("status", "")).upper() == "NEXT_EXPECTED":
                task["status"] = "REGISTERED"

    receipt_rel = str((registered_task_path / "TASKPACK_ADMISSION_RECEIPT.json").relative_to(ctx["repo_root"])).replace(
        "\\", "/"
    )
    route_rel = str(route_manifest_path.relative_to(ctx["repo_root"])).replace("\\", "/")
    entry = {
        "task_id": task_id,
        "status": "NEXT_EXPECTED",
        "registered_at_utc": utc_now(),
        "source_zip_sha256": zip_sha256,
        "source_zip_path": str(source_zip).replace("\\", "/"),
        "registered_path": str(registered_task_path.relative_to(ctx["repo_root"])).replace("\\", "/"),
        "taskpack_zip_path": str(registered_zip_path.relative_to(ctx["repo_root"])).replace("\\", "/"),
        "extracted_path": str(extract_path.relative_to(ctx["repo_root"])).replace("\\", "/"),
        "route_manifest_path": route_rel,
        "admission_receipt_path": receipt_rel,
        "current_expected": True,
        "owner_launch_phrase": str(manifest.get("owner_launch_phrase", "start task")),
        "expected_start_head": str(manifest.get("expected_start_head", "")),
        "target_contour": str(manifest.get("target_contour", "")),
        "notes": "Registered via Stage2 Astronomicon intake corridor.",
    }
    registry_data["tasks"].append(entry)
    write_json(ctx["task_registry"], registry_data)

    current_expected = {
        "task_id": task_id,
        "status": "NEXT_EXPECTED_TASK",
        "registered_path": entry["registered_path"],
        "route_manifest_path": route_rel,
        "owner_instruction_ru": f"Send to Servitor: TASK_ID: {task_id} and start task",
        "updated_at_utc": utc_now(),
        "updated_by": actor,
    }
    write_json(ctx["current_expected"], current_expected)

    admission_verdict = "ADMISSION_PASS_WITH_WARNINGS" if warnings or caps else "ADMISSION_PASS"
    if caps:
        admission_verdict = "ADMISSION_PASS_WITH_WARNINGS"
    receipt = {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "source_zip_path": str(source_zip).replace("\\", "/"),
        "zip_sha256": zip_sha256,
        "admission_verdict": admission_verdict,
        "language_gate_passed": True,
        "manifest_found": True,
        "task_id_found": True,
        "task_spec_found": True,
        "acceptance_gates_found": True,
        "output_requirements_found": True,
        "duplicate_task_id": False,
        "safe_extraction_path": True,
        "registered_task_path": str(registered_task_path).replace("\\", "/"),
        "extracted_path": str(extract_path).replace("\\", "/"),
        "route_manifest_path": str(route_manifest_path).replace("\\", "/"),
        "current_expected_task_updated": True,
        "caps_triggered": sorted(set(caps + DEFAULT_STAGE2_CAPS)),
        "warnings": warnings,
    }
    write_json(registered_task_path / "TASKPACK_ADMISSION_RECEIPT.json", receipt)
    return receipt


def _load_current_expected(current_expected_path: Path) -> tuple[str | None, list[str]]:
    warnings: list[str] = []
    if not current_expected_path.exists():
        return None, warnings
    try:
        payload = read_json(current_expected_path)
    except Exception as exc:
        warnings.append(f"Cannot parse current_expected_task.json: {exc}")
        return None, warnings
    task_id = str(payload.get("task_id", "")).strip()
    return (task_id or None), warnings


def resolve_task_id(
    repo_root: str | Path,
    task_id: str | None = None,
    actor: str = "astronomicon_task_id_resolver_v0_1.py",
    write_receipt: bool = True,
    receipt_output_path: str | Path | None = None,
) -> dict[str, Any]:
    ctx = build_context(repo_root)
    caps: list[str] = []
    warnings: list[str] = []
    started_at = utc_now()

    try:
        registry_data, registry_warnings = load_or_init_registry(ctx["task_registry"])
        warnings.extend(registry_warnings)
    except ValueError as exc:
        caps.append("CAP_TASK_REGISTRY_CORRUPTION")
        return {
            "timestamp_utc": started_at,
            "resolver_verdict": "BLOCK",
            "caps_triggered": caps,
            "warnings": [str(exc)],
        }

    if not ctx["task_registry"].exists():
        caps.append("CAP_TASK_REGISTRY_MISSING")
        return {
            "timestamp_utc": started_at,
            "resolver_verdict": "BLOCK",
            "caps_triggered": caps,
            "warnings": ["task_registry.json is missing."],
        }

    explicit_task_id = task_id.strip() if isinstance(task_id, str) else None
    resolved_from_current_expected = False
    resolved_task_id = explicit_task_id
    if not resolved_task_id:
        resolved_from_current_expected = True
        resolved_task_id, current_warnings = _load_current_expected(ctx["current_expected"])
        warnings.extend(current_warnings)
        if not resolved_task_id:
            caps.append("CAP_START_TASK_WITHOUT_TASK_ID")
            caps.append("CAP_CURRENT_EXPECTED_TASK_MISSING")
            caps.append("CAP_CURRENT_EXPECTED_TASK_NOT_RESOLVABLE")
            return {
                "timestamp_utc": started_at,
                "resolver_verdict": "BLOCK",
                "caps_triggered": caps,
                "warnings": warnings + ["No task_id provided and no current expected task found."],
            }

    tasks = [row for row in registry_data.get("tasks", []) if isinstance(row, dict)]
    matches = [row for row in tasks if str(row.get("task_id", "")).strip() == resolved_task_id]
    if len(matches) > 1:
        caps.append("CAP_DUPLICATE_TASK_ID_NOT_DETECTED")
        return {
            "timestamp_utc": started_at,
            "task_id": resolved_task_id,
            "resolver_verdict": "BLOCK",
            "caps_triggered": caps,
            "warnings": warnings + [f"Duplicate task_id entries found: {resolved_task_id}"],
        }

    route_manifest_path: Path | None = None
    registered_task_path: Path | None = None
    taskpack_zip_path: Path | None = None
    extracted_path: Path | None = None
    source = "stage2_registry"

    payload: dict[str, Any]
    registered_path_raw = ""
    taskpack_zip_raw = ""
    extracted_path_raw = ""
    route_manifest_raw = ""
    admission_receipt_raw = ""

    if len(matches) == 1:
        payload = matches[0]
        registered_path_raw = str(payload.get("registered_path", "")).strip()
        taskpack_zip_raw = str(payload.get("taskpack_zip_path", "")).strip()
        extracted_path_raw = str(payload.get("extracted_path", "")).strip()
        route_manifest_raw = str(payload.get("route_manifest_path", "")).strip()
        admission_receipt_raw = str(payload.get("admission_receipt_path", "")).strip()
        registered_task_path = normalize_path(ctx["repo_root"] / registered_path_raw)
        taskpack_zip_path = normalize_path(ctx["repo_root"] / taskpack_zip_raw)
        extracted_path = normalize_path(ctx["repo_root"] / extracted_path_raw)
        route_manifest_path = normalize_path(ctx["repo_root"] / route_manifest_raw)
    else:
        source = "stage1_registry_fallback"
        legacy_entries = load_stage1_entries(ctx["legacy_stage1_registry"])
        legacy_matches = [row for row in legacy_entries if str(row.get("task_id", "")).strip() == resolved_task_id]
        if len(legacy_matches) > 1:
            caps.append("CAP_DUPLICATE_TASK_ID_NOT_DETECTED")
            return {
                "timestamp_utc": started_at,
                "task_id": resolved_task_id,
                "resolver_verdict": "BLOCK",
                "caps_triggered": caps,
                "warnings": warnings + [f"Duplicate task_id in stage1 registry: {resolved_task_id}"],
            }
        if not legacy_matches:
            if resolved_from_current_expected:
                caps.append("CAP_CURRENT_EXPECTED_TASK_NOT_RESOLVABLE")
            else:
                caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
            caps.append("CAP_TASK_ID_RESOLVER_MISSING")
            return {
                "timestamp_utc": started_at,
                "task_id": resolved_task_id,
                "resolver_verdict": "BLOCK",
                "caps_triggered": caps,
                "warnings": warnings + ["Task ID not found in stage2 or stage1 registry."],
            }
        payload = legacy_matches[0]
        taskpack_zip_raw = str(payload.get("taskpack_path", "")).strip()
        extracted_rel = str(payload.get("extracted_reference", "")).strip()
        extracted_path_raw = extracted_rel
        registered_path_raw = str(Path(extracted_rel).parent).strip()
        route_manifest_raw = str(ctx["task_route_manifest_template"].relative_to(ctx["repo_root"])).replace("\\", "/")
        admission_receipt_raw = ""
        taskpack_zip_path = normalize_path(taskpack_zip_raw)
        extracted_path = normalize_path(ctx["repo_root"] / extracted_rel)
        registered_task_path = extracted_path.parent
        route_manifest_path = ctx["task_route_manifest_template"]
        warnings.append("Using stage1 resolver fallback entry.")

    assert registered_task_path is not None
    assert taskpack_zip_path is not None
    assert extracted_path is not None
    assert route_manifest_path is not None

    if contains_root_taskpack_inbox_marker(registered_path_raw) or contains_root_taskpack_inbox_marker(extracted_path_raw):
        caps.append("CAP_ROOT_TASKPACK_INBOX_CANON_MISUSE")
        warnings.append("Registry path points to root _TASKPACK_INBOX staging instead of canonical REGISTERED path.")

    path_issues = validate_registered_paths(
        ctx,
        registered_task_path=registered_task_path,
        taskpack_zip_path=taskpack_zip_path,
        extracted_path=extracted_path,
        route_manifest_path=route_manifest_path,
    )
    if path_issues:
        caps.append("CAP_UNSAFE_EXTRACTION_PATH_NOT_BLOCKED")
        caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
        warnings.extend(path_issues)

    if not taskpack_zip_path.exists():
        caps.append("CAP_TASKPACK_ADMISSION_MISSING")
        caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
        warnings.append(f"Taskpack ZIP missing: {taskpack_zip_path}")
    if not extracted_path.exists():
        caps.append("CAP_REGISTERED_ARTIFACT_MISSING")
        caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
        warnings.append(f"Extracted taskpack missing: {extracted_path}")
    else:
        extracted_manifest_task_id, extracted_manifest_warnings = read_extracted_manifest_task_id(extracted_path)
        warnings.extend(extracted_manifest_warnings)
        if extracted_manifest_task_id and extracted_manifest_task_id != resolved_task_id:
            caps.append("CAP_EXTRACTED_MANIFEST_TASK_ID_MISMATCH")
            caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
            warnings.append(
                f"Extracted manifest task_id mismatch: expected '{resolved_task_id}', got '{extracted_manifest_task_id}'."
            )
    if not route_manifest_path.exists():
        caps.append("CAP_ROUTE_MANIFEST_MISSING")
        caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
        warnings.append(f"Route manifest missing: {route_manifest_path}")

    if admission_receipt_raw:
        admission_receipt_path = normalize_path(ctx["repo_root"] / admission_receipt_raw)
    else:
        admission_receipt_path = registered_task_path / "TASKPACK_ADMISSION_RECEIPT.json"
    if not is_within(registered_task_path, admission_receipt_path):
        caps.append("CAP_UNSAFE_EXTRACTION_PATH_NOT_BLOCKED")
        caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
        warnings.append("Admission receipt path is outside registered task path.")
    else:
        _, admission_receipt_issues = load_admission_receipt(admission_receipt_path, resolved_task_id)
        if admission_receipt_issues:
            caps.append("CAP_MALFORMED_ADMISSION_RECEIPT")
            caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
            warnings.extend(admission_receipt_issues)

    route_manifest: dict[str, Any] = {}
    if route_manifest_path.exists():
        try:
            route_manifest = read_json(route_manifest_path)
        except Exception as exc:
            caps.append("CAP_ROUTE_MANIFEST_MISSING")
            caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
            warnings.append(f"Route manifest JSON invalid: {exc}")
        else:
            missing_organs = [
                organ for organ in REQUIRED_ORGANS if organ not in route_manifest.get("required_organs", [])
            ]
            if missing_organs:
                caps.append("CAP_ROUTE_DOES_NOT_INCLUDE_8_ORGANS")
                caps.append("CAP_REGISTERED_TASK_NOT_RESOLVABLE")
                warnings.append("Missing organs in route manifest: " + ", ".join(missing_organs))

    start_ack = build_start_ack_template(resolved_task_id, ctx["repo_root"])
    if not start_ack["all_required_organs_reachable"]:
        caps.append("CAP_ORGAN_READ_FIRST_ACK_MISSING")

    if resolved_from_current_expected and "CAP_REGISTERED_TASK_NOT_RESOLVABLE" in caps:
        caps.append("CAP_CURRENT_EXPECTED_TASK_NOT_RESOLVABLE")

    verdict = "PASS_WITH_WARNINGS" if not caps else "BLOCK"
    receipt = {
        "timestamp_utc": started_at,
        "resolved_by": actor,
        "resolver_source": source,
        "resolved_from_current_expected": resolved_from_current_expected,
        "start_task_request_without_task_id": resolved_from_current_expected,
        "task_id": resolved_task_id,
        "registered_task_path": str(registered_task_path).replace("\\", "/"),
        "taskpack_zip_path": str(taskpack_zip_path).replace("\\", "/"),
        "extracted_path": str(extracted_path).replace("\\", "/"),
        "route_manifest_path": str(route_manifest_path).replace("\\", "/"),
        "admission_receipt_path": str(admission_receipt_path).replace("\\", "/"),
        "current_expected_task_path": str(ctx["current_expected"]).replace("\\", "/"),
        "current_expected_task_found": ctx["current_expected"].exists(),
        "task_start_ack": start_ack,
        "caps_triggered": sorted(set(caps + DEFAULT_STAGE2_CAPS)),
        "warnings": warnings,
        "resolver_verdict": verdict,
    }

    if write_receipt:
        if receipt_output_path is not None:
            out_path = normalize_path(receipt_output_path)
        elif registered_task_path.exists():
            out_path = registered_task_path / "TASK_ID_RESOLVER_RECEIPT.json"
        else:
            out_path = ctx["task_registry_dir"] / f"resolver_{resolved_task_id}.json"
        write_json(out_path, receipt)

        if registered_task_path.exists():
            write_json(registered_task_path / "TASK_START_ACK_TEMPLATE.json", start_ack)

    return receipt
