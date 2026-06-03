#!/usr/bin/env python3
"""Validate Unified Evidence Map foundation artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import py_compile
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-PQG-EVIDENCE-MAP-UNIFIED-VM3-V0_1"
TRUTH_ROOT_REL = "IMPERIUM_NEW_GENERATION/TRUTH"
REPORT_DIR_REL = f"IMPERIUM_NEW_GENERATION/REPORTS/{TASK_ID_DEFAULT}"

CANONICAL_STATUSES = {
    "PASS",
    "PASS_STRICT",
    "PASS_WITH_WARN",
    "WARN",
    "BLOCK",
    "PARTIAL",
    "UNKNOWN",
    "MISSING",
    "FOUNDATION_ONLY",
    "PENDING_POST_COMMIT",
    "STALE",
}

ALLOWED_FRESHNESS = {
    "CURRENT",
    "STALE",
    "UNKNOWN",
    "MISSING",
    "FOUNDATION_ONLY",
    "PARTIAL",
}

ALLOWED_PROOF_LEVELS = {
    "STRONG",
    "PARTIAL",
    "FOUNDATION",
    "WEAK",
    "UNKNOWN",
    "MISSING",
}

NOT_PROVEN_ALLOWED = {
    "WARN",
    "UNKNOWN",
    "MISSING",
    "PARTIAL",
    "FOUNDATION_ONLY",
    "STALE",
    "PENDING_POST_COMMIT",
}


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / REPORT_DIR_REL

    parser = argparse.ArgumentParser(description="Validate NewGen Unified Evidence Map foundation artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", type=Path, default=default_report_dir / "VALIDATOR_REPORT.json")
    return parser.parse_args()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(payload, dict):
        return None, "not_json_object"
    return payload, None


def add_check(
    checks: list[dict[str, str]],
    warnings: list[str],
    blockers: list[str],
    check_id: str,
    ok: bool,
    ok_details: str,
    fail_details: str,
    fail_level: str = "BLOCK",
) -> None:
    if ok:
        checks.append({"check_id": check_id, "status": "PASS", "details": ok_details})
        return

    checks.append({"check_id": check_id, "status": fail_level, "details": fail_details})
    if fail_level == "WARN":
        warnings.append(f"{check_id}:{fail_details}")
    else:
        blockers.append(f"{check_id}:{fail_details}")


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    output_path = args.output.resolve()
    report_dir = output_path.parent

    unified_map_path = repo_root / TRUTH_ROOT_REL / "EVIDENCE_MAP_UNIFIED_V0_1.json"
    freshness_path = repo_root / TRUTH_ROOT_REL / "EVIDENCE_FRESHNESS_INDEX_V0_1.json"
    normalization_path = repo_root / TRUTH_ROOT_REL / "REPORT_STATUS_NORMALIZATION_TABLE_V0_1.json"
    not_proven_path = repo_root / TRUTH_ROOT_REL / "NOT_PROVEN_REGISTER_V0_1.json"
    current_truth_path = repo_root / TRUTH_ROOT_REL / "CURRENT_TRUTH_ROOT_V0_1.json"
    sanctum_state_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"

    schema_paths = [
        repo_root / TRUTH_ROOT_REL / "SCHEMAS/evidence_map_unified_v0_1.schema.json",
        repo_root / TRUTH_ROOT_REL / "SCHEMAS/evidence_freshness_index_v0_1.schema.json",
        repo_root / TRUTH_ROOT_REL / "SCHEMAS/report_status_normalization_table_v0_1.schema.json",
        repo_root / TRUTH_ROOT_REL / "SCHEMAS/not_proven_register_v0_1.schema.json",
    ]

    tool_paths = [
        repo_root / TRUTH_ROOT_REL / "TOOLS/evidence_map_unified_builder.py",
        repo_root / TRUTH_ROOT_REL / "TOOLS/evidence_map_unified_validator.py",
    ]

    required_report_paths = [
        report_dir / "GATE_ACK.md",
        report_dir / "EVIDENCE_MAP_UNIFIED_BUILD_REPORT.json",
        report_dir / "VALIDATOR_REPORT.json",
        report_dir / "STEP_PROOF_RECORDS.jsonl",
        report_dir / "OFFICIO_LIVE_COMMUNICATION_ACK.json",
        report_dir / "OFFICIO_LIVE_COMMUNICATION_NOTE.md",
        report_dir / "CONTEXT_WINDOW_USAGE_NOTE.md",
        report_dir / "CONTEXT_SOURCE_MIX_REPORT.md",
        report_dir / "CONTEXT_SOURCE_MIX_REPORT.json",
        report_dir / "KPD_SLICE.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.json",
        report_dir / "FINAL_OWNER_REPORT_RU.md",
        report_dir / "FINAL_RECEIPT.json",
        report_dir / "POST_COMMIT_CLOSURE_RECEIPT.json",
    ]

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    core_paths = [
        unified_map_path,
        freshness_path,
        normalization_path,
        not_proven_path,
        current_truth_path,
        sanctum_state_path,
    ]

    add_check(
        checks,
        warnings,
        blockers,
        "core_unified_artifacts_exist",
        all(path.exists() for path in core_paths),
        "all unified core artifacts exist",
        "one or more unified core artifacts are missing",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "schema_files_exist",
        all(path.exists() for path in schema_paths),
        "all required schema files exist",
        "one or more schema files are missing",
    )

    for tool_path in tool_paths:
        try:
            py_compile.compile(str(tool_path), doraise=True)
            add_check(
                checks,
                warnings,
                blockers,
                f"py_compile_{tool_path.name}",
                True,
                f"{tool_path.name} compiles",
                "",
            )
        except py_compile.PyCompileError as exc:
            add_check(
                checks,
                warnings,
                blockers,
                f"py_compile_{tool_path.name}",
                False,
                "",
                str(exc),
            )

    unified_map, unified_err = load_json(unified_map_path)
    freshness_index, freshness_err = load_json(freshness_path)
    normalization_table, normalization_err = load_json(normalization_path)
    not_proven, not_proven_err = load_json(not_proven_path)
    current_truth, current_truth_err = load_json(current_truth_path)
    sanctum_state, sanctum_state_err = load_json(sanctum_state_path)

    add_check(
        checks,
        warnings,
        blockers,
        "unified_map_parse",
        unified_map is not None,
        "unified evidence map parses",
        f"unified evidence map parse failed ({unified_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "freshness_index_parse",
        freshness_index is not None,
        "evidence freshness index parses",
        f"freshness index parse failed ({freshness_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "normalization_table_parse",
        normalization_table is not None,
        "status normalization table parses",
        f"status normalization table parse failed ({normalization_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "not_proven_parse",
        not_proven is not None,
        "not-proven register parses",
        f"not-proven register parse failed ({not_proven_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "current_truth_parse",
        current_truth is not None,
        "current truth root parses",
        f"current truth parse failed ({current_truth_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "sanctum_state_parse",
        sanctum_state is not None,
        "sanctum state parses",
        f"sanctum state parse failed ({sanctum_state_err})",
    )

    unified_records: list[dict[str, Any]] = []
    if unified_map is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "unified_map_schema_id",
            unified_map.get("schema_id") == "EVIDENCE_MAP_UNIFIED_V0_1",
            "unified map schema_id is correct",
            "unified map schema_id mismatch",
        )

        raw_records = unified_map.get("records", [])
        if isinstance(raw_records, list):
            unified_records = [item for item in raw_records if isinstance(item, dict)]

        add_check(
            checks,
            warnings,
            blockers,
            "unified_records_non_empty",
            len(unified_records) > 0,
            "unified map contains records",
            "unified map has no records",
        )

        invalid_status = [
            str(item.get("status"))
            for item in unified_records
            if str(item.get("status")) not in CANONICAL_STATUSES
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "unified_status_values",
            not invalid_status,
            "all unified statuses are canonical",
            f"invalid unified statuses found: {invalid_status[:10]}",
        )

        invalid_freshness = [
            str(item.get("freshness"))
            for item in unified_records
            if str(item.get("freshness")) not in ALLOWED_FRESHNESS
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "unified_freshness_values",
            not invalid_freshness,
            "all unified freshness values are allowed",
            f"invalid unified freshness values found: {invalid_freshness[:10]}",
        )

        invalid_proof = [
            str(item.get("proof_level"))
            for item in unified_records
            if str(item.get("proof_level")) not in ALLOWED_PROOF_LEVELS
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "unified_proof_levels",
            not invalid_proof,
            "all unified proof levels are allowed",
            f"invalid unified proof levels found: {invalid_proof[:10]}",
        )

        inconsistent_missing = [
            str(item.get("evidence_id"))
            for item in unified_records
            if str(item.get("status")) == "MISSING" and str(item.get("freshness")) != "MISSING"
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "missing_status_implies_missing_freshness",
            not inconsistent_missing,
            "missing status consistently maps to missing freshness",
            f"status/freshness mismatch for missing records: {inconsistent_missing[:10]}",
        )

        fake_green_candidates = [
            str(item.get("evidence_id"))
            for item in unified_records
            if str(item.get("status")) in {"PASS", "PASS_STRICT"} and len(item.get("linked_reports", [])) == 0
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "pass_records_have_linked_reports",
            not fake_green_candidates,
            "PASS/PASS_STRICT records include linked reports",
            f"PASS records without linked reports: {fake_green_candidates[:10]}",
            fail_level="WARN",
        )

    if freshness_index is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "freshness_index_schema_id",
            freshness_index.get("schema_id") == "EVIDENCE_FRESHNESS_INDEX_V0_1",
            "freshness index schema_id is correct",
            "freshness index schema_id mismatch",
        )

        entries = freshness_index.get("entries", [])
        if not isinstance(entries, list):
            entries = []

        entry_ids = {str(item.get("evidence_id")) for item in entries if isinstance(item, dict)}
        record_ids = {str(item.get("evidence_id")) for item in unified_records}

        add_check(
            checks,
            warnings,
            blockers,
            "freshness_index_covers_unified_records",
            record_ids.issubset(entry_ids),
            "freshness index covers all unified records",
            "freshness index missing evidence ids from unified map",
        )

    if normalization_table is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "normalization_schema_id",
            normalization_table.get("schema_id") == "REPORT_STATUS_NORMALIZATION_TABLE_V0_1",
            "normalization table schema_id is correct",
            "normalization table schema_id mismatch",
        )

        mappings = normalization_table.get("mappings", [])
        if not isinstance(mappings, list):
            mappings = []

        raw_values = {str(item.get("raw_status")) for item in mappings if isinstance(item, dict)}
        required_raw = {
            "PASS",
            "PASS_STRICT",
            "WARN",
            "BLOCK",
            "PARTIAL",
            "UNKNOWN",
            "MISSING",
            "FOUNDATION_ONLY",
            "PENDING_POST_COMMIT",
            "STALE",
        }
        add_check(
            checks,
            warnings,
            blockers,
            "normalization_required_raw_statuses",
            required_raw.issubset(raw_values),
            "normalization table covers required status variants",
            "normalization table is missing one or more required raw status variants",
        )

    if not_proven is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "not_proven_schema_id",
            not_proven.get("schema_id") == "NOT_PROVEN_REGISTER_V0_1",
            "not-proven register schema_id is correct",
            "not-proven register schema_id mismatch",
        )

        entries = not_proven.get("entries", [])
        if not isinstance(entries, list):
            entries = []

        invalid = [
            str(item.get("current_status"))
            for item in entries
            if isinstance(item, dict) and str(item.get("current_status")) not in NOT_PROVEN_ALLOWED
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "not_proven_status_values",
            not invalid,
            "not-proven statuses are allowed",
            f"invalid not-proven statuses found: {invalid[:10]}",
        )

    if current_truth is not None:
        expected_paths = {
            "evidence_map_unified_path": "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_MAP_UNIFIED_V0_1.json",
            "evidence_freshness_index_path": "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_FRESHNESS_INDEX_V0_1.json",
            "report_status_normalization_table_path": "IMPERIUM_NEW_GENERATION/TRUTH/REPORT_STATUS_NORMALIZATION_TABLE_V0_1.json",
            "not_proven_register_path": "IMPERIUM_NEW_GENERATION/TRUTH/NOT_PROVEN_REGISTER_V0_1.json",
        }

        path_ok = True
        path_failures: list[str] = []
        for key, expected in expected_paths.items():
            value = str(current_truth.get(key, "")).strip()
            if value != expected:
                path_ok = False
                path_failures.append(f"{key}={value}")
            elif not (repo_root / expected).exists():
                path_ok = False
                path_failures.append(f"{key}_target_missing={expected}")

        add_check(
            checks,
            warnings,
            blockers,
            "current_truth_references_unified_artifacts",
            path_ok,
            "current truth root references unified artifacts",
            f"current truth unified references invalid: {path_failures}",
        )

    if sanctum_state is not None:
        truth_index = sanctum_state.get("current_truth_index", {})
        has_truth_index = isinstance(truth_index, dict)
        add_check(
            checks,
            warnings,
            blockers,
            "sanctum_has_current_truth_index",
            has_truth_index,
            "sanctum state includes current truth index",
            "sanctum state missing current truth index",
        )

        if has_truth_index:
            required_truth_keys = {
                "current_truth_root_path",
                "report_status_index_path",
                "evidence_source_map_path",
                "evidence_map_unified_path",
                "evidence_freshness_index_path",
                "status",
                "last_sync_utc",
            }
            key_ok = required_truth_keys.issubset(truth_index.keys())
            add_check(
                checks,
                warnings,
                blockers,
                "sanctum_truth_index_unified_keys",
                key_ok,
                "sanctum truth index includes unified evidence/freshness keys",
                "sanctum truth index missing unified evidence/freshness keys",
            )

    add_check(
        checks,
        warnings,
        blockers,
        "report_bundle_files_exist",
        all(path.exists() for path in required_report_paths),
        "all required report bundle files exist",
        "one or more required report bundle files are missing",
    )

    verdict = "PASS" if not blockers else "BLOCK"
    if verdict == "PASS" and warnings:
        verdict = "WARN"

    report = {
        "schema_id": "EVIDENCE_MAP_UNIFIED_VALIDATOR_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validated_paths": {
            "unified_map": unified_map_path.relative_to(repo_root).as_posix(),
            "freshness_index": freshness_path.relative_to(repo_root).as_posix(),
            "normalization_table": normalization_path.relative_to(repo_root).as_posix(),
            "not_proven_register": not_proven_path.relative_to(repo_root).as_posix(),
            "current_truth_root": current_truth_path.relative_to(repo_root).as_posix(),
            "sanctum_state": sanctum_state_path.relative_to(repo_root).as_posix(),
            "report_dir": report_dir.relative_to(repo_root).as_posix(),
        },
        "no_fake_green_note": "Validation keeps unresolved evidence explicitly non-green and rejects hidden missing paths.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"validator_verdict={verdict}")
    print(f"validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
