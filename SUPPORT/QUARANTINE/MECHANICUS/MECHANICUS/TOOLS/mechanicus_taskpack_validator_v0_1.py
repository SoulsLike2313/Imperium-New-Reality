from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1"
REQUIRED_ROOT_FILES: tuple[str, ...] = (
    "TASK.md",
    "TASK.json",
    "ACCEPTANCE_GATES.md",
    "00_START_HERE_SERVITOR.md",
)
RECOMMENDED_FILES: tuple[str, ...] = (
    "QUALITY_GATE_SCOPE.md",
    "QUALITY_GATE_SCOPE.json",
    "OFFICIO_MECHANICUS_COMBINED_GATE.md",
    "GHOST_EVOLVE_BATCH_002_CONTRACT.md",
    "FINAL_REPORT_TEMPLATE.md",
    "_MANIFEST.json",
)
REQUIRED_TEMPLATE_FILES: tuple[str, ...] = (
    "TEMPLATES/closure_receipt.template.json",
    "TEMPLATES/quality_gate_report.template.json",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(text: str) -> Any:
    return json.loads(text)


def normalize_entry(entry: str) -> str:
    return entry.replace("\\", "/").lstrip("./")


def path_exists_in_entries(entries: set[str], relative_path: str) -> bool:
    normalized = normalize_entry(relative_path)
    if normalized in entries:
        return True
    suffix = "/" + normalized
    return any(item.endswith(suffix) for item in entries)


def read_text_from_entries(zip_path: Path, normalized_entries: dict[str, zipfile.ZipInfo], relative_path: str) -> str:
    normalized_rel = normalize_entry(relative_path)
    info = normalized_entries.get(normalized_rel)
    if info is None:
        suffix = "/" + normalized_rel
        for key, value in normalized_entries.items():
            if key.endswith(suffix):
                info = value
                break
    if info is None:
        raise FileNotFoundError(relative_path)
    with zipfile.ZipFile(zip_path, "r") as archive:
        content = archive.read(info.filename)
    return content.decode("utf-8")


def validate_zip_taskpack(taskpack_zip: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    json_checks: list[dict[str, str]] = []

    with zipfile.ZipFile(taskpack_zip, "r") as archive:
        raw_entries = [normalize_entry(item.filename) for item in archive.infolist() if not item.is_dir()]
    entries_set = set(raw_entries)

    normalized_map: dict[str, zipfile.ZipInfo] = {}
    with zipfile.ZipFile(taskpack_zip, "r") as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            normalized_map[normalize_entry(info.filename)] = info

    missing_required = [name for name in REQUIRED_ROOT_FILES if not path_exists_in_entries(entries_set, name)]
    missing_templates = [name for name in REQUIRED_TEMPLATE_FILES if not path_exists_in_entries(entries_set, name)]
    missing_recommended = [name for name in RECOMMENDED_FILES if not path_exists_in_entries(entries_set, name)]

    if missing_required:
        errors.append("missing_required:" + ",".join(missing_required))
    if missing_templates:
        errors.append("missing_templates:" + ",".join(missing_templates))
    if missing_recommended:
        warnings.append("missing_recommended:" + ",".join(missing_recommended))

    json_targets = [
        "TASK.json",
        "QUALITY_GATE_SCOPE.json",
        "_MANIFEST.json",
        "TEMPLATES/closure_receipt.template.json",
        "TEMPLATES/quality_gate_report.template.json",
    ]
    for target in json_targets:
        if not path_exists_in_entries(entries_set, target):
            continue
        try:
            text = read_text_from_entries(taskpack_zip, normalized_map, target)
            parsed = load_json(text)
            json_checks.append(
                {
                    "path": target,
                    "parse_status": "PASS",
                    "payload_type": type(parsed).__name__,
                }
            )
        except Exception as exc:
            errors.append(f"json_parse_failed:{target}:{exc}")
            json_checks.append(
                {
                    "path": target,
                    "parse_status": "FAIL",
                    "payload_type": "unknown",
                }
            )

    verdict = "PASS"
    if errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARN"

    return {
        "source_kind": "zip",
        "source_path": str(taskpack_zip),
        "entries_count": len(raw_entries),
        "required_files": list(REQUIRED_ROOT_FILES),
        "required_templates": list(REQUIRED_TEMPLATE_FILES),
        "recommended_files": list(RECOMMENDED_FILES),
        "missing_required_files": missing_required,
        "missing_required_templates": missing_templates,
        "missing_recommended_files": missing_recommended,
        "json_checks": json_checks,
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }


def validate_directory_taskpack(taskpack_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    json_checks: list[dict[str, str]] = []

    missing_required = [name for name in REQUIRED_ROOT_FILES if not (taskpack_dir / name).exists()]
    missing_templates = [name for name in REQUIRED_TEMPLATE_FILES if not (taskpack_dir / name).exists()]
    missing_recommended = [name for name in RECOMMENDED_FILES if not (taskpack_dir / name).exists()]

    if missing_required:
        errors.append("missing_required:" + ",".join(missing_required))
    if missing_templates:
        errors.append("missing_templates:" + ",".join(missing_templates))
    if missing_recommended:
        warnings.append("missing_recommended:" + ",".join(missing_recommended))

    json_targets = [
        "TASK.json",
        "QUALITY_GATE_SCOPE.json",
        "_MANIFEST.json",
        "TEMPLATES/closure_receipt.template.json",
        "TEMPLATES/quality_gate_report.template.json",
    ]
    for target in json_targets:
        target_path = taskpack_dir / target
        if not target_path.exists():
            continue
        try:
            parsed = load_json(target_path.read_text(encoding="utf-8"))
            json_checks.append(
                {
                    "path": target,
                    "parse_status": "PASS",
                    "payload_type": type(parsed).__name__,
                }
            )
        except Exception as exc:
            errors.append(f"json_parse_failed:{target}:{exc}")
            json_checks.append(
                {
                    "path": target,
                    "parse_status": "FAIL",
                    "payload_type": "unknown",
                }
            )

    verdict = "PASS"
    if errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARN"

    return {
        "source_kind": "directory",
        "source_path": str(taskpack_dir),
        "entries_count": len([path for path in taskpack_dir.rglob("*") if path.is_file()]),
        "required_files": list(REQUIRED_ROOT_FILES),
        "required_templates": list(REQUIRED_TEMPLATE_FILES),
        "recommended_files": list(RECOMMENDED_FILES),
        "missing_required_files": missing_required,
        "missing_required_templates": missing_templates,
        "missing_recommended_files": missing_recommended,
        "json_checks": json_checks,
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate taskpack dossier structure for repeatable NewGen admission.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--taskpack-zip", help="Path to dossier ZIP.")
    parser.add_argument("--taskpack-dir", help="Path to unpacked dossier directory.")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.taskpack_zip and not args.taskpack_dir:
        raise SystemExit("Either --taskpack-zip or --taskpack-dir is required.")

    if args.taskpack_zip:
        source_path = Path(args.taskpack_zip).resolve()
        result = validate_zip_taskpack(source_path)
    else:
        source_path = Path(args.taskpack_dir).resolve()
        result = validate_directory_taskpack(source_path)

    result["task_id"] = args.task_id
    result["generated_at_utc"] = utc_now()
    result["checker"] = "mechanicus_taskpack_validator_v0_1.py"

    output = Path(args.output)
    if not output.is_absolute():
        output = Path.cwd() / output
    write_json(output, result)

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "source_kind": result["source_kind"],
                "verdict": result["verdict"],
                "missing_required_files": len(result["missing_required_files"]),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["verdict"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
