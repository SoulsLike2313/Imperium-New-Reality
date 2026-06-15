from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-OWNER-APPROVED-TOOLS-REGISTRY-NORMALIZATION-PC-V0_1"
REPORT_ROOT_DEFAULT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MECHANICUS-OWNER-APPROVED-TOOLS-REGISTRY-NORMALIZATION-PC-V0_1"
)
CHECKER_VERSION = "0.2.0"
ALIAS_MAP_DEFAULT = (
    "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/"
    "owner_approved_tool_aliases_v0_1.json"
)

REQUIRED_IDS = {
    "UTILITIES_7_ZIP",
    "MARKDOWNLINT_CLI",
    "CHECK_JSONSCHEMA_CLI",
    "YAMLLINT_CLI",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check owner-approved tool normalization artifacts.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--report-root", default=REPORT_ROOT_DEFAULT)
    parser.add_argument("--alias-map", default=ALIAS_MAP_DEFAULT)
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
    parser.add_argument("--list", action="store_true", dest="list_mode", help="List required owner-approved IDs.")
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


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    report_root = (repo_root / args.report_root).resolve()
    alias_map_path = Path(args.alias_map)
    if not alias_map_path.is_absolute():
        alias_map_path = (repo_root / alias_map_path).resolve()
    default_output_path = report_root / "normalization_check_report.json"

    if args.list_mode:
        print(json.dumps({"required_owner_approved_ids": sorted(REQUIRED_IDS)}, ensure_ascii=False, indent=2))
        return 0

    if args.show_config:
        print(
            json.dumps(
                {
                    "checker": "check_owner_approved_tool_normalization_v0_1.py",
                    "version": CHECKER_VERSION,
                    "task_id": args.task_id,
                    "repo_root": repo_root.as_posix(),
                    "report_root": report_root.as_posix(),
                    "alias_map": alias_map_path.as_posix(),
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

    required_report_files = [
        "owner_approved_tools_normalization_map_v0_1.json",
        "recommended_install_wave_001_owner_approved_v0_1.json",
        "normalization_receipt.json",
        "truth_check_start.json",
        "preflight_git_state.json",
        "GATE_ACK.json",
        "ghost_evolve_sidecar.json",
        "FINAL_REPORT.md",
        "closure_receipt.json",
    ]
    missing_report_files = [name for name in required_report_files if not (report_root / name).is_file()]
    if missing_report_files:
        violations.append("missing_report_files:" + ",".join(missing_report_files))

    if not alias_map_path.is_file():
        violations.append("missing_alias_map:" + str(alias_map_path.relative_to(repo_root).as_posix()))
    else:
        try:
            alias_payload = load_json(alias_map_path)
        except Exception as exc:
            violations.append(f"alias_map_parse_error:{exc}")
            alias_payload = {}
        alias_rows = alias_payload.get("aliases", [])
        if not isinstance(alias_rows, list):
            violations.append("alias_map_aliases_not_list")
        else:
            alias_ids = {
                str(row.get("owner_approved_id", "")).strip()
                for row in alias_rows
                if isinstance(row, dict)
            }
            missing_alias_ids = sorted(REQUIRED_IDS - alias_ids)
            if missing_alias_ids:
                violations.append("alias_map_missing_ids:" + ",".join(missing_alias_ids))

    map_payload: dict[str, Any] = {}
    map_rows: list[Any] = []
    map_path = report_root / "owner_approved_tools_normalization_map_v0_1.json"
    if map_path.is_file():
        try:
            map_payload = load_json(map_path)
        except Exception as exc:
            violations.append(f"normalization_map_parse_error:{exc}")
        map_rows = map_payload.get("records", [])
        if not isinstance(map_rows, list):
            violations.append("normalization_map_records_not_list")
            map_rows = []
    else:
        violations.append("missing_normalization_map")

    map_by_id: dict[str, dict[str, Any]] = {}
    for row in map_rows:
        if not isinstance(row, dict):
            violations.append("normalization_map_row_not_object")
            continue
        owner_id = str(row.get("owner_approved_id", "")).strip()
        if owner_id:
            map_by_id[owner_id] = row

    for owner_id in sorted(REQUIRED_IDS):
        row = map_by_id.get(owner_id)
        if row is None:
            violations.append(f"normalization_map_missing_id:{owner_id}")
            continue
        if not str(row.get("canonical_capability_id", "")).strip():
            violations.append(f"normalization_map_empty_canonical_id:{owner_id}")
        if bool(row.get("install_wave_001_included")) is not True:
            violations.append(f"normalization_map_wave_flag_false:{owner_id}")
        if bool(row.get("no_install_performed")) is not True:
            violations.append(f"normalization_map_no_install_flag_false:{owner_id}")
        action_taken = str(row.get("action_taken", "")).strip()
        if action_taken not in {"already_present", "alias_created", "canonical_card_created", "matrix_row_patched"}:
            warnings.append(f"normalization_map_unknown_action:{owner_id}:{action_taken}")

    wave_payload: dict[str, Any] = {}
    wave_items: list[Any] = []
    wave_path = report_root / "recommended_install_wave_001_owner_approved_v0_1.json"
    if wave_path.is_file():
        try:
            wave_payload = load_json(wave_path)
        except Exception as exc:
            violations.append(f"wave_parse_error:{exc}")
        wave_items = wave_payload.get("items", [])
        if not isinstance(wave_items, list):
            violations.append("wave_items_not_list")
            wave_items = []
    else:
        violations.append("missing_wave_file")

    wave_by_id: dict[str, dict[str, Any]] = {}
    for item in wave_items:
        if not isinstance(item, dict):
            violations.append("wave_item_not_object")
            continue
        capability_id = str(item.get("capability_id", "")).strip()
        if capability_id:
            wave_by_id[capability_id] = item

    required_wave_fields = [
        "detect_command",
        "install_command_candidate",
        "validation_command",
        "stress_test_candidate",
    ]
    for owner_id in sorted(REQUIRED_IDS):
        item = wave_by_id.get(owner_id)
        if item is None:
            violations.append(f"wave_missing_id:{owner_id}")
            continue

        if str(item.get("owner_decision", "")).strip() != "approve":
            violations.append(f"wave_owner_decision_not_approve:{owner_id}")
        if bool(item.get("approved_for_install_wave_001")) is not True:
            violations.append(f"wave_approved_flag_false:{owner_id}")
        if bool(item.get("install_allowed_in_this_task")) is not False:
            violations.append(f"wave_install_allowed_must_be_false:{owner_id}")
        if bool(item.get("install_next_task_required")) is not True:
            violations.append(f"wave_install_next_task_required_false:{owner_id}")
        if bool(item.get("receipt_required")) is not True:
            violations.append(f"wave_receipt_required_false:{owner_id}")

        for field_name in required_wave_fields:
            if not str(item.get(field_name, "")).strip():
                violations.append(f"wave_missing_recipe_field:{owner_id}:{field_name}")

    receipt_path = report_root / "normalization_receipt.json"
    if receipt_path.is_file():
        try:
            receipt_payload = load_json(receipt_path)
        except Exception as exc:
            violations.append(f"normalization_receipt_parse_error:{exc}")
            receipt_payload = {}
        if receipt_payload.get("install_actions_performed") is not False:
            violations.append("normalization_receipt_install_actions_performed_must_be_false")
        if receipt_payload.get("install_receipts_generated") is not False:
            violations.append("normalization_receipt_install_receipts_generated_must_be_false")
    else:
        violations.append("missing_normalization_receipt")

    install_receipt_like = [
        path.name
        for path in report_root.glob("*install*receipt*.json")
        if path.name not in {"normalization_receipt.json", "closure_receipt.json"}
    ]
    if install_receipt_like:
        violations.append("unexpected_install_receipt_files:" + ",".join(sorted(install_receipt_like)))

    verdict = "PASS"
    if violations:
        verdict = "FAIL"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"

    report_payload = {
        "task_id": args.task_id,
        "checker": "IMPERIUM_NEW_GENERATION/MECHANICUS/TOOLS/check_owner_approved_tool_normalization_v0_1.py",
        "checked_at_utc": utc_now(),
        "verdict": verdict,
        "summary": {
            "required_ids": sorted(REQUIRED_IDS),
            "normalization_map_rows": len(map_rows),
            "wave_item_count": len(wave_items),
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
