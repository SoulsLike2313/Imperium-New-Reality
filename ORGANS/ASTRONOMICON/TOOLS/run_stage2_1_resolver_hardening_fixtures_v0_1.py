#!/usr/bin/env python3
"""Run Stage2.1 resolver-hardening fixtures in isolated sandbox."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

from astronomicon_task_entry_lib_v0_1 import (
    REQUIRED_ORGANS,
    register_taskpack,
    resolve_task_id,
    utc_now,
    write_json,
)


def copy_rel(repo_root: Path, sandbox_root: Path, rel: str) -> None:
    src = repo_root / rel
    dst = sandbox_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dst)


def prepare_sandbox(repo_root: Path, sandbox_root: Path) -> None:
    if sandbox_root.exists():
        shutil.rmtree(sandbox_root)
    sandbox_root.mkdir(parents=True, exist_ok=True)

    copy_rel(repo_root, sandbox_root, "AGENTS.md")
    copy_rel(repo_root, sandbox_root, "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md")
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ENTRY_CORRIDOR_CONTRACT.json",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ENTRY_CORRIDOR_CONTRACT.md",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASKPACK_INTAKE_CONTRACT.json",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASKPACK_INTAKE_CONTRACT.md",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASKPACK_ADMISSION_CONTRACT.json",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ID_RESOLVER_CONTRACT.json",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ROUTE_MANIFEST_TEMPLATE.json",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_START_ACK_TEMPLATE.json",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/TASK_INBOX_README.md",
    )
    copy_rel(
        repo_root,
        sandbox_root,
        "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/TASK_ID_REGISTRY_STAGE1.json",
    )

    for organ in REQUIRED_ORGANS:
        rel = f"IMPERIUM_NEW_GENERATION/ORGANS/{organ}/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md"
        copy_rel(repo_root, sandbox_root, rel)


def build_manifest(task_id: str, taskpack_id: str, organs: list[str]) -> dict[str, Any]:
    return {
        "taskpack_id": taskpack_id,
        "task_id": task_id,
        "target_contour": "PC",
        "expected_start_head": "fixture-head",
        "owner_launch_phrase": "start task",
        "organs": organs,
    }


def write_zip(
    zip_path: Path,
    *,
    task_id: str,
    include_manifest: bool = True,
    include_task_id: bool = True,
    include_task_spec: bool = True,
    include_acceptance: bool = True,
    include_output: bool = True,
    include_unsafe_member: bool = False,
    manifest_organs: list[str] | None = None,
) -> None:
    root = f"FIXTURE_{task_id}"
    manifest_organs = manifest_organs if manifest_organs is not None else list(REQUIRED_ORGANS)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if include_manifest:
            manifest = build_manifest(task_id if include_task_id else "", f"TASKPACK_{task_id}", manifest_organs)
            zf.writestr(f"{root}/MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        if include_task_spec:
            zf.writestr(f"{root}/TASK_SPEC.md", f"# Task Spec for {task_id}\n")
        if include_acceptance:
            zf.writestr(f"{root}/ACCEPTANCE_GATES.md", "# Acceptance\n")
        if include_output:
            zf.writestr(f"{root}/OUTPUT_REQUIREMENTS.md", "# Output\n")
        zf.writestr(f"{root}/000_START_TASK_READ_ORDER.md", "# start task\n")
        if include_unsafe_member:
            zf.writestr("../escape.txt", "unsafe")


def admission_case(name: str, repo_root: Path, zip_path: Path) -> dict[str, Any]:
    receipt = register_taskpack(repo_root=repo_root, source_zip_path=zip_path)
    return {
        "case": name,
        "timestamp_utc": utc_now(),
        "admission_verdict": receipt.get("admission_verdict"),
        "task_id": receipt.get("task_id", ""),
        "caps_triggered": receipt.get("caps_triggered", []),
        "warnings": receipt.get("warnings", []),
        "raw_receipt": receipt,
    }


def resolver_case(name: str, repo_root: Path, task_id: str | None) -> dict[str, Any]:
    receipt = resolve_task_id(repo_root=repo_root, task_id=task_id, write_receipt=False)
    return {
        "case": name,
        "timestamp_utc": utc_now(),
        "resolver_verdict": receipt.get("resolver_verdict"),
        "task_id": receipt.get("task_id", task_id or ""),
        "caps_triggered": receipt.get("caps_triggered", []),
        "warnings": receipt.get("warnings", []),
        "raw_receipt": receipt,
    }


def load_registry(registry_path: Path) -> dict[str, Any]:
    return json.loads(registry_path.read_text(encoding="utf-8"))


def save_registry(registry_path: Path, data: dict[str, Any]) -> None:
    registry_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def first_task_entry(registry_data: dict[str, Any], task_id: str) -> dict[str, Any]:
    tasks = registry_data.get("tasks", [])
    for row in tasks:
        if isinstance(row, dict) and str(row.get("task_id", "")).strip() == task_id:
            return row
    raise RuntimeError(f"Task not found in sandbox registry: {task_id}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-root", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report_root = Path(args.report_root).resolve()
    sandbox_root = report_root / "_fixture_sandbox_stage2_1"
    fixture_zip_root = report_root / "fixture_zips_stage2_1"
    fixture_zip_root.mkdir(parents=True, exist_ok=True)

    prepare_sandbox(repo_root, sandbox_root)

    admission_results: list[dict[str, Any]] = []
    resolver_results: list[dict[str, Any]] = []

    # Admission negatives
    missing_zip = fixture_zip_root / "missing.zip"
    admission_results.append(admission_case("missing_zip", sandbox_root, missing_zip))

    bad_zip = fixture_zip_root / "bad_zip.zip"
    bad_zip.write_text("not a zip", encoding="utf-8")
    admission_results.append(admission_case("bad_zip", sandbox_root, bad_zip))

    zip_no_manifest = fixture_zip_root / "no_manifest.zip"
    write_zip(zip_no_manifest, task_id="TASK-FIXTURE-NO-MANIFEST", include_manifest=False)
    admission_results.append(admission_case("missing_manifest", sandbox_root, zip_no_manifest))

    zip_no_task_id = fixture_zip_root / "no_task_id.zip"
    write_zip(zip_no_task_id, task_id="TASK-FIXTURE-NO-TASKID", include_task_id=False)
    admission_results.append(admission_case("missing_task_id", sandbox_root, zip_no_task_id))

    zip_manifest_missing_organs = fixture_zip_root / "manifest_missing_organs.zip"
    write_zip(
        zip_manifest_missing_organs,
        task_id="TASK-FIXTURE-MANIFEST-MISSING-ORGANS",
        manifest_organs=REQUIRED_ORGANS[:-1],
    )
    admission_results.append(admission_case("manifest_organs_missing_required", sandbox_root, zip_manifest_missing_organs))

    zip_unsafe = fixture_zip_root / "unsafe.zip"
    write_zip(zip_unsafe, task_id="TASK-FIXTURE-UNSAFE", include_unsafe_member=True)
    admission_results.append(admission_case("unsafe_extraction_path", sandbox_root, zip_unsafe))

    positive_task_id = "TASK-FIXTURE-STAGE2-1-POSITIVE"
    zip_positive = fixture_zip_root / "positive.zip"
    write_zip(zip_positive, task_id=positive_task_id)
    positive_admission = admission_case("positive_valid_registration", sandbox_root, zip_positive)
    admission_results.append(positive_admission)

    zip_dup = fixture_zip_root / "duplicate.zip"
    write_zip(zip_dup, task_id=positive_task_id)
    admission_results.append(admission_case("duplicate_task_id", sandbox_root, zip_dup))

    # Positive resolver proof
    resolver_results.append(resolver_case("positive_resolve_registered_task", sandbox_root, positive_task_id))
    resolver_results.append(resolver_case("positive_resolve_current_expected", sandbox_root, None))

    registry_path = sandbox_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json"
    current_expected_path = (
        sandbox_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/current_expected_task.json"
    )
    registry_data = load_registry(registry_path)
    task_entry = first_task_entry(registry_data, positive_task_id)
    registered_path = sandbox_root / str(task_entry["registered_path"]).replace("/", "\\")
    route_manifest_path = sandbox_root / str(task_entry["route_manifest_path"]).replace("/", "\\")
    extracted_path = sandbox_root / str(task_entry["extracted_path"]).replace("/", "\\")
    admission_receipt_path = sandbox_root / str(task_entry["admission_receipt_path"]).replace("/", "\\")

    # Resolver negatives required by taskpack
    extracted_backup = registered_path / "_EXTRACTED_BACKUP"
    if extracted_path.exists():
        shutil.copytree(extracted_path, extracted_backup)
        shutil.rmtree(extracted_path)
    resolver_results.append(resolver_case("registered_artifact_missing", sandbox_root, positive_task_id))
    if extracted_backup.exists():
        shutil.move(str(extracted_backup), str(extracted_path))

    current_expected_backup = current_expected_path.with_suffix(".json.bak")
    shutil.copy2(current_expected_path, current_expected_backup)
    current_expected_payload = json.loads(current_expected_path.read_text(encoding="utf-8"))
    current_expected_payload["task_id"] = "TASK-NOT-REGISTERED"
    current_expected_path.write_text(json.dumps(current_expected_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    resolver_results.append(resolver_case("current_expected_points_to_missing_task", sandbox_root, None))
    shutil.move(str(current_expected_backup), str(current_expected_path))

    route_backup = route_manifest_path.with_suffix(".json.bak")
    shutil.copy2(route_manifest_path, route_backup)
    route_manifest_path.unlink()
    resolver_results.append(resolver_case("route_manifest_missing", sandbox_root, positive_task_id))
    shutil.move(str(route_backup), str(route_manifest_path))

    route_backup = route_manifest_path.with_suffix(".json.bak")
    shutil.copy2(route_manifest_path, route_backup)
    route_payload = json.loads(route_manifest_path.read_text(encoding="utf-8"))
    route_payload["required_organs"] = REQUIRED_ORGANS[:-1]
    route_manifest_path.write_text(json.dumps(route_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    resolver_results.append(resolver_case("route_manifest_missing_required_organs", sandbox_root, positive_task_id))
    shutil.move(str(route_backup), str(route_manifest_path))

    receipt_backup = admission_receipt_path.with_suffix(".json.bak")
    shutil.copy2(admission_receipt_path, receipt_backup)
    admission_receipt_path.write_text("{bad-json", encoding="utf-8")
    resolver_results.append(resolver_case("malformed_admission_receipt", sandbox_root, positive_task_id))
    shutil.move(str(receipt_backup), str(admission_receipt_path))

    registry_backup = registry_path.with_suffix(".json.bak")
    shutil.copy2(registry_path, registry_backup)
    registry_mut = load_registry(registry_path)
    first_task_entry(registry_mut, positive_task_id)["registered_path"] = "../ESCAPE/TASK"
    save_registry(registry_path, registry_mut)
    resolver_results.append(resolver_case("unsafe_registered_path", sandbox_root, positive_task_id))
    shutil.move(str(registry_backup), str(registry_path))

    extracted_manifest = next((p for p in extracted_path.rglob("MANIFEST.json") if p.is_file()), None)
    if extracted_manifest is not None:
        manifest_backup = extracted_manifest.with_suffix(".json.bak")
        shutil.copy2(extracted_manifest, manifest_backup)
        manifest_payload = json.loads(extracted_manifest.read_text(encoding="utf-8"))
        manifest_payload["task_id"] = "TASK-MISMATCHED-MANIFEST"
        extracted_manifest.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        resolver_results.append(resolver_case("extracted_manifest_task_id_mismatch", sandbox_root, positive_task_id))
        shutil.move(str(manifest_backup), str(extracted_manifest))

    current_expected_backup = current_expected_path.with_suffix(".json.bak")
    shutil.copy2(current_expected_path, current_expected_backup)
    current_expected_path.unlink()
    resolver_results.append(resolver_case("start_task_without_task_id", sandbox_root, None))
    shutil.move(str(current_expected_backup), str(current_expected_path))

    registry_backup = registry_path.with_suffix(".json.bak")
    shutil.copy2(registry_path, registry_backup)
    registry_mut = load_registry(registry_path)
    task_row = first_task_entry(registry_mut, positive_task_id)
    task_row["registered_path"] = "_TASKPACK_INBOX/REGISTERED/LEGACY_ROOT_TASK"
    task_row["extracted_path"] = "_TASKPACK_INBOX/REGISTERED/LEGACY_ROOT_TASK/EXTRACTED"
    task_row["taskpack_zip_path"] = "_TASKPACK_INBOX/REGISTERED/LEGACY_ROOT_TASK/TASKPACK.zip"
    task_row["route_manifest_path"] = "_TASKPACK_INBOX/REGISTERED/LEGACY_ROOT_TASK/TASK_ROUTE_MANIFEST.json"
    task_row["admission_receipt_path"] = "_TASKPACK_INBOX/REGISTERED/LEGACY_ROOT_TASK/TASKPACK_ADMISSION_RECEIPT.json"
    save_registry(registry_path, registry_mut)
    resolver_results.append(resolver_case("root_taskpack_inbox_used_as_canon", sandbox_root, positive_task_id))
    shutil.move(str(registry_backup), str(registry_path))

    registry_backup = registry_path.with_suffix(".json.bak")
    shutil.copy2(registry_path, registry_backup)
    registry_path.write_text("{broken", encoding="utf-8")
    resolver_results.append(resolver_case("registry_corruption", sandbox_root, positive_task_id))
    shutil.move(str(registry_backup), str(registry_path))

    resolver_results.append(resolver_case("missing_task_id", sandbox_root, "TASK-NOT-FOUND"))

    negative_admission = [row for row in admission_results if row["admission_verdict"] == "ADMISSION_BLOCK"]
    negative_resolver = [row for row in resolver_results if row["resolver_verdict"] == "BLOCK"]
    summary = {
        "timestamp_utc": utc_now(),
        "sandbox_root": str(sandbox_root).replace("\\", "/"),
        "admission_case_count": len(admission_results),
        "resolver_case_count": len(resolver_results),
        "negative_admission_case_count": len(negative_admission),
        "negative_resolver_case_count": len(negative_resolver),
        "combined_negative_case_count": len(negative_admission) + len(negative_resolver),
        "admission_results": admission_results,
        "resolver_results": resolver_results,
    }
    write_json(report_root / "stage2_1_fixture_summary.json", summary)
    write_json(report_root / "taskpack_admission_fixture_results_stage2_1.json", admission_results)
    write_json(report_root / "task_id_resolver_fixture_results_stage2_1.json", resolver_results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
