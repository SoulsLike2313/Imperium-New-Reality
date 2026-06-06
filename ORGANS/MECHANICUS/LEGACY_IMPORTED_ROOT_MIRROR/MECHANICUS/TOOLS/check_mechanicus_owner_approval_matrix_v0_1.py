from __future__ import annotations

import argparse
import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-ARSENAL-OWNER-APPROVAL-MATRIX-PC-V0_1"
REPORT_ROOT_DEFAULT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-ARSENAL-OWNER-APPROVAL-MATRIX-PC-V0_1"
)
CHECKER_VERSION = "0.2.0"
RECIPE_JSON_DEFAULT = "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/RECIPES/tool_validation_recipes_v0_1.json"

RECOMMENDATION_ENUM = {
    "install",
    "defer",
    "keep_candidate",
    "sandbox",
    "canon_later",
    "reject",
    "quarantine",
}
OWNER_DECISION_ENUM = {"approve", "reject", "hold", "pending"}

APPROVED_INSTALL_WAVE_001_IDS = {
    "UTILITIES_7_ZIP",
    "MARKDOWNLINT_CLI",
    "CHECK_JSONSCHEMA_CLI",
    "YAMLLINT_CLI",
}

MATRIX_COLUMNS = [
    "capability_id",
    "category",
    "current_status",
    "what_is_it_ru",
    "why_needed_ru",
    "agent_usage_ru",
    "plus_ru",
    "minus_risk_ru",
    "install_needed",
    "platform_profile_pc_windows",
    "platform_profile_ubuntu_vm3",
    "platform_profile_cross_platform",
    "platform_profile_unknown_notes",
    "install_command_candidate",
    "detect_command",
    "validation_command",
    "stress_test_candidate",
    "receipt_required",
    "recommendation",
    "owner_decision",
    "approved_for_install_wave_001",
    "notes_for_owner_ru",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check owner approval matrix artifact bundle.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-root", default=REPORT_ROOT_DEFAULT)
    parser.add_argument("--recipe-json", default=RECIPE_JSON_DEFAULT)
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Allow writing report file (disabled by default for read-only safety).",
    )
    parser.add_argument(
        "--report-output",
        default="",
        help="Explicit output path for report JSON. Implies write mode.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_mode",
        help="List IDs approved for install wave 001 and exit.",
    )
    parser.add_argument("--show-config", action="store_true", help="Show resolved config and exit.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {CHECKER_VERSION}")
    return parser.parse_args()


def resolve_repo_root(path_hint: Path) -> Path:
    try:
        top = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=path_hint, text=True).strip()
        if top:
            return Path(top)
    except Exception:
        pass
    return path_hint


def resolve_output_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()


def required_report_files() -> list[str]:
    return [
        "OWNER_APPROVAL_MATRIX.md",
        "OWNER_APPROVAL_MATRIX.csv",
        "owner_approval_matrix_v0_1.json",
        "recommended_install_waves_v0_1.json",
        "defer_queue_v0_1.json",
        "reject_or_quarantine_queue_v0_1.json",
        "owner_decision_template_v0_1.csv",
        "owner_decision_template_v0_1.json",
        "truth_check_start.json",
         "GATE_ACK.json",
         "preflight_git_state.json",
         "matrix_build_receipt.json",
         "ghost_evolve_sidecar.json",
         "FINAL_REPORT.md",
         "closure_receipt.json",
     ]


def validate_matrix_rows(rows: list[Any]) -> tuple[list[str], list[str], set[str]]:
    violations: list[str] = []
    warnings: list[str] = []
    present_ids: set[str] = set()

    for index, raw in enumerate(rows):
        row_id = f"row#{index + 1}"
        if not isinstance(raw, dict):
            violations.append(f"{row_id}: not an object")
            continue

        capability_id = str(raw.get("capability_id", "")).strip()
        if capability_id:
            present_ids.add(capability_id)
        else:
            violations.append(f"{row_id}: capability_id missing")

        for column in MATRIX_COLUMNS:
            if column not in raw:
                violations.append(f"{row_id}: missing column `{column}`")

        recommendation = str(raw.get("recommendation", "")).strip()
        owner_decision = str(raw.get("owner_decision", "")).strip()
        install_needed = raw.get("install_needed")
        approved_wave = raw.get("approved_for_install_wave_001")

        if recommendation not in RECOMMENDATION_ENUM:
            violations.append(f"{row_id}: invalid recommendation `{recommendation}`")
        if owner_decision not in OWNER_DECISION_ENUM:
            violations.append(f"{row_id}: invalid owner_decision `{owner_decision}`")
        if not isinstance(install_needed, bool):
            violations.append(f"{row_id}: install_needed must be boolean")
        if not isinstance(approved_wave, bool):
            violations.append(f"{row_id}: approved_for_install_wave_001 must be boolean")

        if bool(install_needed) and not str(raw.get("install_command_candidate", "")).strip():
            warnings.append(f"{row_id}: install_needed=true but install_command_candidate is empty")
        if not str(raw.get("detect_command", "")).strip():
            warnings.append(f"{row_id}: detect_command is empty")
        if not str(raw.get("validation_command", "")).strip():
            warnings.append(f"{row_id}: validation_command is empty")
        if not str(raw.get("receipt_required", "")).strip():
            warnings.append(f"{row_id}: receipt_required is empty")

    return (violations, warnings, present_ids)


def load_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader, [])


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    report_root = (repo_root / args.report_root).resolve()
    recipe_json_path = Path(args.recipe_json)
    if not recipe_json_path.is_absolute():
        recipe_json_path = (repo_root / recipe_json_path).resolve()
    default_output_path = report_root / "matrix_check_report.json"

    if args.list_mode:
        print(json.dumps({"approved_install_wave_001_ids": sorted(APPROVED_INSTALL_WAVE_001_IDS)}, ensure_ascii=False, indent=2))
        return 0

    if args.show_config:
        print(
            json.dumps(
                {
                    "checker": "check_mechanicus_owner_approval_matrix_v0_1.py",
                    "version": CHECKER_VERSION,
                    "task_id": args.task_id,
                    "repo_root": repo_root.as_posix(),
                    "report_root": report_root.as_posix(),
                    "recipe_json": recipe_json_path.as_posix(),
                    "default_report_output": default_output_path.as_posix(),
                    "write_by_default": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    violations: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    missing_files: list[str] = []
    for filename in required_report_files():
        if not (report_root / filename).is_file():
            missing_files.append(filename)
    if missing_files:
        violations.append("missing_required_files:" + ",".join(missing_files))

    matrix_csv_path = report_root / "OWNER_APPROVAL_MATRIX.csv"
    if matrix_csv_path.is_file():
        csv_header = load_csv_header(matrix_csv_path)
        missing_columns = [column for column in MATRIX_COLUMNS if column not in csv_header]
        if missing_columns:
            violations.append("csv_missing_columns:" + ",".join(missing_columns))
    else:
        violations.append("matrix_csv_missing")

    matrix_json_path = report_root / "owner_approval_matrix_v0_1.json"
    present_ids: set[str] = set()
    row_count = 0
    if matrix_json_path.is_file():
        matrix_payload = load_json(matrix_json_path)
        rows = matrix_payload.get("rows", [])
        if not isinstance(rows, list):
            violations.append("matrix_json_rows_not_list")
            rows = []
        row_count = len(rows)
        row_violations, row_warnings, present_ids = validate_matrix_rows(rows)
        violations.extend(row_violations)
        warnings.extend(row_warnings)
    else:
        violations.append("matrix_json_missing")

    for capability_id in sorted(APPROVED_INSTALL_WAVE_001_IDS):
        if capability_id not in present_ids:
            info.append(f"approved_wave_001_capability_not_present:{capability_id}")
            continue
        if matrix_json_path.is_file():
            rows = load_json(matrix_json_path).get("rows", [])
            match = [row for row in rows if isinstance(row, dict) and str(row.get("capability_id", "")).strip() == capability_id]
            for row in match:
                if not bool(row.get("approved_for_install_wave_001", False)):
                    violations.append(f"approved_wave_001_flag_missing:{capability_id}")

    build_receipt_path = report_root / "matrix_build_receipt.json"
    if build_receipt_path.is_file():
        build_receipt = load_json(build_receipt_path)
        install_actions = build_receipt.get("install_actions_performed")
        if install_actions is not False:
            violations.append("install_actions_performed_must_be_false")
    else:
        violations.append("matrix_build_receipt_missing")

    if recipe_json_path.is_file():
        recipe_payload = load_json(recipe_json_path)
        recipes = recipe_payload.get("recipes", [])
        if not isinstance(recipes, list):
            violations.append("recipes_payload_invalid")
            recipes = []
        if len(recipes) < row_count:
            warnings.append(f"recipes_count_lower_than_matrix_rows:{len(recipes)}<{row_count}")
        for index, recipe in enumerate(recipes):
            if not isinstance(recipe, dict):
                violations.append(f"recipe#{index + 1}: not an object")
                continue
            for key in [
                "capability_id",
                "tool_name",
                "category",
                "platform",
                "detect",
                "install",
                "validate",
                "stress",
                "receipt",
                "rollback_or_cleanup_notes",
            ]:
                if key not in recipe:
                    violations.append(f"recipe#{index + 1}: missing key `{key}`")
    else:
        violations.append(f"recipe_json_missing:{recipe_json_path.relative_to(repo_root).as_posix()}")

    verdict = "PASS"
    if violations:
        verdict = "FAIL"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"

    report_payload = {
        "task_id": args.task_id,
        "checker": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_mechanicus_owner_approval_matrix_v0_1.py",
        "checked_at_utc": utc_now(),
        "verdict": verdict,
        "summary": {
            "row_count": row_count,
            "violations_count": len(violations),
            "warnings_count": len(warnings),
            "info_count": len(info),
        },
        "violations": violations,
        "warnings": warnings,
        "info": info,
    }
    written_report_path = ""
    if args.report_output:
        report_output_path = resolve_output_path(repo_root, args.report_output)
        write_json(report_output_path, report_payload)
        written_report_path = report_output_path.as_posix()
    elif args.write_report:
        write_json(default_output_path, report_payload)
        written_report_path = default_output_path.as_posix()

    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": verdict,
                "write_mode": bool(written_report_path),
                "written_report_path": written_report_path,
                "violations_count": len(violations),
                "warnings_count": len(warnings),
            },
            ensure_ascii=False,
        )
    )
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
