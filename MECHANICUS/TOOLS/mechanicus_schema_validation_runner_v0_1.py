from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import jsonschema  # type: ignore[import-untyped]
except Exception:
    jsonschema = None


DEFAULT_TASK_ID = "TASK-NEWGEN-MECHANICUS-VALIDATION-BATCH-002-PC-V0_1"
DEFAULT_SCOPE_SCHEMA = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCOPE_PACKS/V0_1/scope_pack_schema_v0_1.json"
)
DEFAULT_OFFICIO_ROLE_PACK = (
    "IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/ROLE_PACKS/OFFICIO_PC_SERVITOR_ROLE_PACK_V0_1.json"
)


@dataclass(frozen=True)
class ValidationTarget:
    path: Path
    schema_path: Path | None
    reason: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative_or_abs(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except Exception:
        return path.as_posix()


def is_json_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".json"


def collect_scope_targets(repo_root: Path, scope_schema_path: Path) -> list[ValidationTarget]:
    targets: list[ValidationTarget] = []
    scope_root = scope_schema_path.parent
    for file_path in sorted(scope_root.glob("scope_*_task_v0_1.json")):
        targets.append(
            ValidationTarget(
                path=file_path,
                schema_path=scope_schema_path if scope_schema_path.exists() else None,
                reason="scope_pack_schema",
            )
        )
    return targets


def collect_report_targets(report_root: Path) -> list[ValidationTarget]:
    targets: list[ValidationTarget] = []
    for file_path in sorted(report_root.glob("*.json")):
        targets.append(ValidationTarget(path=file_path, schema_path=None, reason="report_json_parse_only"))
    return targets


def collect_taskpack_targets(taskpack_dir: Path) -> list[ValidationTarget]:
    targets: list[ValidationTarget] = []
    for file_path in sorted(taskpack_dir.glob("*.json")):
        targets.append(ValidationTarget(path=file_path, schema_path=None, reason="taskpack_json_parse_only"))
    return targets


def dedupe_targets(targets: list[ValidationTarget]) -> list[ValidationTarget]:
    by_path: dict[Path, ValidationTarget] = {}
    for target in targets:
        existing = by_path.get(target.path)
        if existing is None:
            by_path[target.path] = target
            continue
        if existing.schema_path is None and target.schema_path is not None:
            by_path[target.path] = target
    return sorted(by_path.values(), key=lambda t: t.path.as_posix())


def validate_targets(targets: list[ValidationTarget], repo_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    parse_fail_count = 0
    schema_fail_count = 0
    no_schema_count = 0
    schema_checked_count = 0

    for target in targets:
        path = target.path
        if not path.exists():
            errors.append(f"missing_target:{path}")
            rows.append(
                {
                    "artifact_path": str(path),
                    "exists": False,
                    "json_parse_status": "MISSING",
                    "schema_status": "NOT_APPLICABLE",
                    "reason": target.reason,
                }
            )
            continue

        try:
            payload = load_json(path)
            parse_status = "PASS"
        except Exception as exc:
            parse_status = "FAIL"
            parse_fail_count += 1
            errors.append(f"json_parse_failed:{path}:{exc}")
            rows.append(
                {
                    "artifact_path": path.relative_to(repo_root).as_posix(),
                    "exists": True,
                    "json_parse_status": parse_status,
                    "schema_status": "SKIPPED_PARSE_FAIL",
                    "reason": target.reason,
                    "error": str(exc),
                }
            )
            continue

        schema_status = "NO_SCHEMA_AVAILABLE"
        schema_error = ""
        if target.schema_path is not None:
            if not target.schema_path.exists():
                schema_status = "NO_SCHEMA_AVAILABLE"
                no_schema_count += 1
            elif jsonschema is None:
                schema_status = "SCHEMA_CHECK_SKIPPED_JSONSCHEMA_MISSING"
                warnings.append(f"jsonschema_unavailable:{path.name}")
            else:
                try:
                    schema_payload = load_json(target.schema_path)
                    jsonschema.validate(payload, schema_payload)
                    schema_status = "PASS"
                    schema_checked_count += 1
                except Exception as exc:
                    schema_status = "FAIL"
                    schema_fail_count += 1
                    schema_error = str(exc)
                    errors.append(f"schema_validation_failed:{path}:{exc}")
        else:
            no_schema_count += 1

        rows.append(
            {
                "artifact_path": relative_or_abs(path, repo_root),
                "exists": True,
                "json_parse_status": parse_status,
                "schema_status": schema_status,
                "schema_path": (
                    relative_or_abs(target.schema_path, repo_root)
                    if target.schema_path is not None and target.schema_path.exists()
                    else None
                ),
                "reason": target.reason,
                "schema_error": schema_error,
            }
        )

    verdict = "PASS"
    if errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "WARN"

    return {
        "generated_at_utc": utc_now(),
        "checker": "mechanicus_schema_validation_runner_v0_1.py",
        "targets_total": len(targets),
        "summary": {
            "parse_fail_count": parse_fail_count,
            "schema_fail_count": schema_fail_count,
            "schema_checked_count": schema_checked_count,
            "no_schema_count": no_schema_count,
        },
        "artifacts": rows,
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "raw_dump_status": "COMPACT_ONLY",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run JSON parse + schema checks with honest NO_SCHEMA reporting.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-root", required=True)
    parser.add_argument("--taskpack-dir", help="Optional unpacked taskpack directory.")
    parser.add_argument("--scope-schema-path", default=DEFAULT_SCOPE_SCHEMA)
    parser.add_argument("--officio-role-pack", default=DEFAULT_OFFICIO_ROLE_PACK)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    report_root = Path(args.report_root)
    if not report_root.is_absolute():
        report_root = (repo_root / report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    scope_schema_path = Path(args.scope_schema_path)
    if not scope_schema_path.is_absolute():
        scope_schema_path = (repo_root / scope_schema_path).resolve()

    role_pack_path = Path(args.officio_role_pack)
    if not role_pack_path.is_absolute():
        role_pack_path = (repo_root / role_pack_path).resolve()

    targets: list[ValidationTarget] = []
    targets.extend(collect_scope_targets(repo_root=repo_root, scope_schema_path=scope_schema_path))
    targets.extend(collect_report_targets(report_root=report_root))
    if role_pack_path.exists() and is_json_file(role_pack_path):
        targets.append(
            ValidationTarget(
                path=role_pack_path,
                schema_path=None,
                reason="officio_role_pack_parse_only",
            )
        )
    if args.taskpack_dir:
        taskpack_dir = Path(args.taskpack_dir)
        if not taskpack_dir.is_absolute():
            taskpack_dir = taskpack_dir.resolve()
        if taskpack_dir.exists():
            targets.extend(collect_taskpack_targets(taskpack_dir))

    deduped_targets = dedupe_targets(targets)
    report = validate_targets(deduped_targets, repo_root=repo_root)
    report["task_id"] = args.task_id

    output = Path(args.output)
    if not output.is_absolute():
        output = (repo_root / output).resolve()
    write_json(output, report)
    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": report["verdict"],
                "targets_total": report["targets_total"],
                "schema_fail_count": report["summary"]["schema_fail_count"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["verdict"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
