#!/usr/bin/env python3
"""Run Stage2 Astronomicon admission/resolver fixtures in isolated sandbox."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

from astronomicon_task_entry_lib_v0_1 import REQUIRED_ORGANS, register_taskpack, resolve_task_id, utc_now, write_json


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


def build_manifest(task_id: str, taskpack_id: str) -> dict[str, Any]:
    return {
        "taskpack_id": taskpack_id,
        "task_id": task_id,
        "target_contour": "PC",
        "expected_start_head": "fixture-head",
        "owner_launch_phrase": "start task",
        "organs": REQUIRED_ORGANS,
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
) -> None:
    root = f"FIXTURE_{task_id}"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if include_manifest:
            manifest = build_manifest(task_id if include_task_id else "", f"TASKPACK_{task_id}")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-root", required=True)
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report_root = Path(args.report_root).resolve()
    sandbox_root = report_root / "_fixture_sandbox"
    fixture_zip_root = report_root / "fixture_zips"
    fixture_zip_root.mkdir(parents=True, exist_ok=True)

    prepare_sandbox(repo_root, sandbox_root)

    admission_results: list[dict[str, Any]] = []
    resolver_results: list[dict[str, Any]] = []

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

    zip_no_spec = fixture_zip_root / "no_spec.zip"
    write_zip(zip_no_spec, task_id="TASK-FIXTURE-NO-SPEC", include_task_spec=False)
    admission_results.append(admission_case("missing_task_spec", sandbox_root, zip_no_spec))

    zip_unsafe = fixture_zip_root / "unsafe.zip"
    write_zip(zip_unsafe, task_id="TASK-FIXTURE-UNSAFE", include_unsafe_member=True)
    admission_results.append(admission_case("unsafe_extraction_path", sandbox_root, zip_unsafe))

    positive_task_id = "TASK-FIXTURE-STAGE2-POSITIVE"
    zip_positive = fixture_zip_root / "positive.zip"
    write_zip(zip_positive, task_id=positive_task_id)
    positive_admission = admission_case("positive_valid_registration", sandbox_root, zip_positive)
    admission_results.append(positive_admission)

    zip_dup = fixture_zip_root / "duplicate.zip"
    write_zip(zip_dup, task_id=positive_task_id)
    admission_results.append(admission_case("duplicate_task_id", sandbox_root, zip_dup))

    route_template = (
        sandbox_root
        / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ROUTE_MANIFEST_TEMPLATE.json"
    )
    route_template_backup = route_template.with_suffix(".json.bak")
    shutil.copy2(route_template, route_template_backup)
    route_template.unlink()
    zip_missing_route = fixture_zip_root / "missing_route_template.zip"
    write_zip(zip_missing_route, task_id="TASK-FIXTURE-MISSING-ROUTE")
    admission_results.append(admission_case("missing_route_template", sandbox_root, zip_missing_route))
    shutil.move(str(route_template_backup), str(route_template))

    resolver_results.append(resolver_case("positive_resolve", sandbox_root, positive_task_id))
    resolver_results.append(resolver_case("missing_task", sandbox_root, "TASK-NOT-FOUND"))

    registry_path = sandbox_root / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_REGISTRY/task_registry.json"
    registry_backup = registry_path.with_suffix(".json.bak")
    shutil.copy2(registry_path, registry_backup)
    registry_path.write_text("{broken", encoding="utf-8")
    resolver_results.append(resolver_case("registry_corruption", sandbox_root, positive_task_id))
    shutil.move(str(registry_backup), str(registry_path))

    positive_registered = (
        sandbox_root
        / "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED"
        / positive_task_id
    )
    extracted = positive_registered / "EXTRACTED"
    extracted_backup = positive_registered / "_EXTRACTED_BACKUP"
    if extracted.exists():
        shutil.copytree(extracted, extracted_backup)
        shutil.rmtree(extracted)
    resolver_results.append(resolver_case("registered_artifact_missing", sandbox_root, positive_task_id))
    if extracted_backup.exists():
        shutil.move(str(extracted_backup), str(extracted))

    organ_path = (
        sandbox_root
        / "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md"
    )
    organ_backup = organ_path.with_suffix(".md.bak")
    shutil.copy2(organ_path, organ_backup)
    organ_path.unlink()
    resolver_results.append(resolver_case("organ_read_first_missing", sandbox_root, positive_task_id))
    shutil.move(str(organ_backup), str(organ_path))

    summary = {
        "timestamp_utc": utc_now(),
        "sandbox_root": str(sandbox_root).replace("\\", "/"),
        "admission_case_count": len(admission_results),
        "resolver_case_count": len(resolver_results),
        "admission_results": admission_results,
        "resolver_results": resolver_results,
    }
    write_json(report_root / "stage2_fixture_summary.json", summary)
    write_json(report_root / "taskpack_admission_fixture_results.json", admission_results)
    write_json(report_root / "task_id_resolver_fixture_results.json", resolver_results)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
