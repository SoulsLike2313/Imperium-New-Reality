from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-NEWGEN-ADMINISTRATUM-FILE-ATLAS-PASSPORT-INDEX-VM3-V0_1"
HERE = Path(__file__).resolve()
ADMIN_ROOT = HERE.parents[1]
ATLAS_ROOT = ADMIN_ROOT / "FILE_ATLAS"
REPORT_ROOT = ADMIN_ROOT / "REPORTS" / TASK_ID
DEFAULT_OUTPUT = REPORT_ROOT / "file_atlas_check_receipt.json"

REQUIRED_FILES = [
    "file_passport_schema_v0_1.json",
    "file_atlas_index_v0_1.json",
    "file_passports_v0_1.jsonl",
    "organ_file_map_v0_1.json",
    "role_rule_surface_index_v0_1.json",
    "language_gate_surface_index_v0_1.json",
    "tui_surface_index_v0_1.json",
    "checker_tool_index_v0_1.json",
    "report_receipt_index_v0_1.json",
    "route_connection_surface_index_v0_1.json",
    "owner_pain_to_file_map_v0_1.json",
    "gap_success_index_v0_1.json",
    "README_FILE_ATLAS_V0_1.md",
]

REQUIRED_OWNER_PAINS = {
    "OFFICIO_LANGUAGE_GATE_WEAKNESS",
    "ROUTE_MEMORY_LOSS_PC_TO_VM3",
    "PENDING_COMMIT_PUSH_RECURRENCE",
    "INQUISITION_WEAKEST_ORGAN_BLOCKER",
    "HIDDEN_PATHS_AND_REPORT_LINKS",
}

REQUIRED_ORGANS = {"MECHANICUS", "OFFICIO_AGENTIS", "ADMINISTRATUM", "INQUISITION", "ASTRONOMICON"}
REQUIRED_PASSPORT_FIELDS = {
    "path",
    "owner_organ",
    "related_block",
    "file_kind",
    "purpose_short",
    "status",
    "ide_visible",
    "drilldown_priority",
    "related_owner_pains",
    "edit_surface",
    "evidence_source",
    "warnings",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        item = json.loads(stripped)
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _record(rows: list[dict[str, Any]], check_id: str, status: str, detail: str) -> None:
    rows.append({"check_id": check_id, "status": status, "detail": detail})


def _enforce_output_path(path: Path, allow_external: bool) -> None:
    if allow_external:
        return
    resolved_report = REPORT_ROOT.resolve()
    resolved_path = path.resolve()
    if resolved_report not in resolved_path.parents and resolved_path != resolved_report:
        raise SystemExit(f"Output path must stay under {resolved_report} unless --allow-external-output is used.")


def run_checks() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for filename in REQUIRED_FILES:
        path = ATLAS_ROOT / filename
        if path.exists():
            _record(checks, f"required_file.{filename}", "PASS", "exists")
        else:
            _record(checks, f"required_file.{filename}", "FAIL", "missing")

    if any(c["status"] == "FAIL" for c in checks):
        fail_count = sum(1 for c in checks if c["status"] == "FAIL")
        return {
            "task_id": TASK_ID,
            "checker": "administratum_file_atlas_checker_v0_1.py",
            "status": "FAIL",
            "fail_count": fail_count,
            "warn_count": 0,
            "checks": checks,
        }

    atlas_index = _read_json(ATLAS_ROOT / "file_atlas_index_v0_1.json")
    passports = _read_jsonl(ATLAS_ROOT / "file_passports_v0_1.jsonl")
    route_surface = _read_json(ATLAS_ROOT / "route_connection_surface_index_v0_1.json")
    owner_pain_map = _read_json(ATLAS_ROOT / "owner_pain_to_file_map_v0_1.json")
    checker_tool_index = _read_json(ATLAS_ROOT / "checker_tool_index_v0_1.json")
    tui_surface_index = _read_json(ATLAS_ROOT / "tui_surface_index_v0_1.json")
    language_surface_index = _read_json(ATLAS_ROOT / "language_gate_surface_index_v0_1.json")

    indexed_organs = set(atlas_index.get("indexed_organs", []))
    if REQUIRED_ORGANS.issubset(indexed_organs):
        _record(checks, "organs.five_scanned", "PASS", "all required organs indexed")
    else:
        _record(checks, "organs.five_scanned", "FAIL", f"missing={sorted(REQUIRED_ORGANS - indexed_organs)}")

    if passports:
        _record(checks, "passports.non_empty", "PASS", str(len(passports)))
    else:
        _record(checks, "passports.non_empty", "FAIL", "empty file_passports_v0_1.jsonl")

    missing_required_fields = 0
    for passport in passports[:200]:
        if not REQUIRED_PASSPORT_FIELDS.issubset(set(passport.keys())):
            missing_required_fields += 1
    if missing_required_fields == 0:
        _record(checks, "passports.required_fields", "PASS", "required fields present in sampled passports")
    else:
        _record(checks, "passports.required_fields", "FAIL", f"sampled missing fields in {missing_required_fields} rows")

    pain_ids = {p.get("pain_id") for p in owner_pain_map.get("pains", []) if isinstance(p, dict)}
    if REQUIRED_OWNER_PAINS.issubset(pain_ids):
        _record(checks, "owner_pains.required_ids", "PASS", "all required pain IDs present")
    else:
        _record(checks, "owner_pains.required_ids", "FAIL", f"missing={sorted(REQUIRED_OWNER_PAINS - pain_ids)}")

    alias_ok = bool(route_surface.get("alias_detected")) and any(
        "imperium-vm3" in str(path).lower() or "pc_to_vm3" in str(path).lower()
        for path in route_surface.get("alias_evidence_paths", [])
    )
    if alias_ok:
        _record(checks, "route.alias_imperium_vm3", "PASS", "alias evidence present")
    else:
        _record(checks, "route.alias_imperium_vm3", "FAIL", "required alias evidence missing")

    if checker_tool_index.get("total_tool_files", 0) > 0:
        _record(checks, "tools.index_present", "PASS", str(checker_tool_index.get("total_tool_files")))
    else:
        _record(checks, "tools.index_present", "FAIL", "tool index empty")

    if tui_surface_index.get("tui_file_count", 0) > 0:
        _record(checks, "tui.index_present", "PASS", str(tui_surface_index.get("tui_file_count")))
    else:
        _record(checks, "tui.index_present", "FAIL", "tui index empty")

    if language_surface_index.get("future_hardening_task"):
        _record(checks, "language.future_task_declared", "PASS", language_surface_index["future_hardening_task"])
    else:
        _record(checks, "language.future_task_declared", "FAIL", "future hardening task missing")

    unknown_count = int(atlas_index.get("unknown_file_kind_count", 0))
    if unknown_count > 0:
        _record(checks, "quality.unknown_file_kind", "WARN", f"unknown_file_kind_count={unknown_count}")
    else:
        _record(checks, "quality.unknown_file_kind", "PASS", "no unknown file kinds")

    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")
    status = "PASS" if fail_count == 0 else "FAIL"
    return {
        "task_id": TASK_ID,
        "checker": "administratum_file_atlas_checker_v0_1.py",
        "status": status,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Administratum File Atlas outputs.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--allow-external-output", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    _enforce_output_path(output_path, allow_external=args.allow_external_output)
    report = run_checks()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
