#!/usr/bin/env python3
"""Validate Negative Test / Mutation Check foundation artifacts (V0.1)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import py_compile
import re
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-PQG-NEGATIVE-TEST-MUTATION-CHECK-VM2-V0_1"
TRUTH_ROOT_REL = "IMPERIUM_NEW_GENERATION/TRUTH"
NEGATIVE_ROOT_REL = f"{TRUTH_ROOT_REL}/NEGATIVE_TESTS"
REPORT_DIR_REL = f"IMPERIUM_NEW_GENERATION/REPORTS/{TASK_ID_DEFAULT}"

REQUIRED_CASE_IDS = {
    "FAKE_GREEN_WITHOUT_EVIDENCE",
    "UNKNOWN_PROMOTED_TO_PASS",
    "STALE_EVIDENCE_ACCEPTED_AS_FRESH",
    "ROLLBACK_REQUIRED_BUT_MISSING",
    "PRIVATE_KEY_MATERIAL_MARKER",
    "ACTION_OUTSIDE_ALLOWLIST",
    "PENDING_POST_COMMIT_CLOSURE_ACCEPTED",
    "PARTIAL_ACCEPTED_WITHOUT_RULE",
}

SAFE_NEGATIVE_CLASSIFICATIONS = {"BLOCK", "WARN", "REJECTED"}
FORBIDDEN_KEY_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"-----END [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"OPENSSH PRIVATE KEY"),
]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / REPORT_DIR_REL

    parser = argparse.ArgumentParser(description="Validate negative test mutation check foundation.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", type=Path, default=default_report_dir / "VALIDATOR_REPORT.json")
    parser.add_argument(
        "--negative-test-run-report",
        type=Path,
        default=default_report_dir / "NEGATIVE_TEST_RUN_REPORT.json",
    )
    return parser.parse_args()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(value, dict):
        return None, "not_json_object"
    return value, None


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


def scan_for_private_key_patterns(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_KEY_PATTERNS:
            if pattern.search(content):
                hits.append(f"{path}:{pattern.pattern}")
    return hits


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    output_path = args.output.resolve()
    run_report_path = args.negative_test_run_report.resolve()
    report_dir = output_path.parent

    negative_root = repo_root / NEGATIVE_ROOT_REL
    schemas_root = repo_root / TRUTH_ROOT_REL / "SCHEMAS"

    required_core_paths = [
        negative_root / "NEGATIVE_TEST_MUTATION_CHECK_V0_1.md",
        negative_root / "NEGATIVE_TEST_CASE_CATALOG_V0_1.json",
        negative_root / "MUTATION_CHECK_POLICY_V0_1.json",
        negative_root / "FAKE_GREEN_REJECTION_RULES_V0_1.json",
        negative_root / "NEGATIVE_TEST_RESULT_MATRIX_V0_1.json",
        negative_root / "SAMPLES/NEGATIVE_TEST_SYNTHETIC_MUTANTS_V0_1.json",
        schemas_root / "NEGATIVE_TEST_CASE_V0_1.schema.json",
        schemas_root / "NEGATIVE_TEST_RESULT_MATRIX_V0_1.schema.json",
        repo_root / TRUTH_ROOT_REL / "CURRENT_TRUTH_ROOT_V0_1.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
        repo_root / TRUTH_ROOT_REL / "TOOLS/build_negative_test_mutation_check_v0_1.py",
        repo_root / TRUTH_ROOT_REL / "TOOLS/validate_negative_test_mutation_check_v0_1.py",
    ]

    required_report_paths = [
        report_dir / "GATE_ACK.md",
        report_dir / "FINAL_OWNER_REPORT_RU.md",
        report_dir / "FINAL_RECEIPT.json",
        report_dir / "POST_COMMIT_CLOSURE_RECEIPT.json",
        report_dir / "STEP_PROOF_RECORDS.jsonl",
        report_dir / "CONTEXT_SOURCE_REPORT.md",
        report_dir / "CONTEXT_SOURCE_REPORT.json",
        report_dir / "CONTEXT_WINDOW_USAGE_NOTE.md",
        report_dir / "KPD_SLICE.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.json",
        report_dir / "OFFICIO_ROLE_ACK_OR_WARN.json",
        report_dir / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        report_dir / "SUPER_SKEPTICISM_ACK.json",
    ]

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    add_check(
        checks,
        warnings,
        blockers,
        "core_artifacts_exist",
        all(path.exists() for path in required_core_paths),
        "all core negative-test/mutation-check artifacts exist",
        "one or more core artifacts are missing",
    )

    for tool_path in [
        repo_root / TRUTH_ROOT_REL / "TOOLS/build_negative_test_mutation_check_v0_1.py",
        repo_root / TRUTH_ROOT_REL / "TOOLS/validate_negative_test_mutation_check_v0_1.py",
    ]:
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

    catalog, catalog_err = load_json(negative_root / "NEGATIVE_TEST_CASE_CATALOG_V0_1.json")
    policy, policy_err = load_json(negative_root / "MUTATION_CHECK_POLICY_V0_1.json")
    rules, rules_err = load_json(negative_root / "FAKE_GREEN_REJECTION_RULES_V0_1.json")
    matrix, matrix_err = load_json(negative_root / "NEGATIVE_TEST_RESULT_MATRIX_V0_1.json")
    samples, samples_err = load_json(negative_root / "SAMPLES/NEGATIVE_TEST_SYNTHETIC_MUTANTS_V0_1.json")
    current_truth, current_truth_err = load_json(repo_root / TRUTH_ROOT_REL / "CURRENT_TRUTH_ROOT_V0_1.json")
    sanctum_state, sanctum_state_err = load_json(
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"
    )

    add_check(checks, warnings, blockers, "catalog_parse", catalog is not None, "catalog parses", f"catalog parse failed ({catalog_err})")
    add_check(checks, warnings, blockers, "policy_parse", policy is not None, "policy parses", f"policy parse failed ({policy_err})")
    add_check(checks, warnings, blockers, "rules_parse", rules is not None, "rules parse", f"rules parse failed ({rules_err})")
    add_check(checks, warnings, blockers, "matrix_parse", matrix is not None, "result matrix parses", f"matrix parse failed ({matrix_err})")
    add_check(checks, warnings, blockers, "samples_parse", samples is not None, "samples parse", f"samples parse failed ({samples_err})")
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

    case_map: dict[str, dict[str, Any]] = {}
    if catalog is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "catalog_schema_id",
            catalog.get("schema_id") == "NEGATIVE_TEST_CASE_CATALOG_V0_1",
            "catalog schema_id is correct",
            "catalog schema_id mismatch",
        )
        catalog_cases = catalog.get("cases", [])
        if isinstance(catalog_cases, list):
            for item in catalog_cases:
                if isinstance(item, dict):
                    case_map[str(item.get("case_id"))] = item
        missing_cases = sorted(REQUIRED_CASE_IDS - set(case_map.keys()))
        add_check(
            checks,
            warnings,
            blockers,
            "required_cases_present",
            not missing_cases,
            "all required negative test case IDs are present",
            f"missing case ids: {missing_cases}",
        )

    matrix_rows: list[dict[str, Any]] = []
    if matrix is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "matrix_schema_id",
            matrix.get("schema_id") == "NEGATIVE_TEST_RESULT_MATRIX_V0_1",
            "matrix schema_id is correct",
            "matrix schema_id mismatch",
        )
        rows = matrix.get("result_rows", [])
        if isinstance(rows, list):
            matrix_rows = [row for row in rows if isinstance(row, dict)]

        row_case_ids = {str(row.get("case_id")) for row in matrix_rows}
        missing_matrix_cases = sorted(REQUIRED_CASE_IDS - row_case_ids)
        add_check(
            checks,
            warnings,
            blockers,
            "matrix_covers_required_cases",
            not missing_matrix_cases,
            "result matrix covers required case IDs",
            f"matrix missing case ids: {missing_matrix_cases}",
        )

        bad_pass_rows = [
            str(row.get("case_id"))
            for row in matrix_rows
            if str(row.get("actual_classification")) == "PASS_STRICT"
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "no_bad_case_pass_strict",
            not bad_pass_rows,
            "no known-bad sample classified PASS_STRICT",
            f"bad cases classified PASS_STRICT: {bad_pass_rows}",
        )

        safe_class_violations = [
            f"{row.get('case_id')}:{row.get('actual_classification')}"
            for row in matrix_rows
            if str(row.get("actual_classification")) not in SAFE_NEGATIVE_CLASSIFICATIONS
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "known_bad_classifications_safe",
            not safe_class_violations,
            "all known-bad cases classified as BLOCK/WARN/REJECTED",
            f"unsafe classifications: {safe_class_violations}",
        )

        fake_green_accepted = [
            str(row.get("case_id"))
            for row in matrix_rows
            if bool(row.get("fake_green_accepted"))
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "no_fake_green_accepted",
            not fake_green_accepted,
            "no fake-green sample accepted",
            f"fake-green accepted cases: {fake_green_accepted}",
        )

        mismatch_rows = [
            str(row.get("case_id"))
            for row in matrix_rows
            if str(row.get("expected_classification")) != str(row.get("actual_classification"))
        ]
        add_check(
            checks,
            warnings,
            blockers,
            "expected_vs_actual_match",
            not mismatch_rows,
            "actual classifications match expected classifications",
            f"classification mismatches: {mismatch_rows}",
        )

    if policy is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "policy_schema_id",
            policy.get("schema_id") == "MUTATION_CHECK_POLICY_V0_1",
            "policy schema_id is correct",
            "policy schema_id mismatch",
        )
        forbidden_list = policy.get("forbidden_classifications_for_known_bad", [])
        forbidden = {str(item) for item in forbidden_list} if isinstance(forbidden_list, list) else set()
        add_check(
            checks,
            warnings,
            blockers,
            "policy_forbids_pass_strict",
            "PASS_STRICT" in forbidden,
            "policy forbids PASS_STRICT for known-bad samples",
            "policy does not forbid PASS_STRICT",
        )

    if rules is not None:
        rules_list = rules.get("rules", [])
        has_fake_green_rule = False
        if isinstance(rules_list, list):
            has_fake_green_rule = any(
                isinstance(rule, dict) and str(rule.get("rule_id")) == "NO_EVIDENCE_NO_STRICT_PASS"
                for rule in rules_list
            )
        add_check(
            checks,
            warnings,
            blockers,
            "fake_green_rule_present",
            has_fake_green_rule,
            "fake-green rejection rule is present",
            "fake-green rejection rule is missing",
        )

    synthetic_case_marker_ok = False
    if samples is not None:
        sample_cases = samples.get("cases", [])
        if isinstance(sample_cases, list):
            for case in sample_cases:
                if not isinstance(case, dict):
                    continue
                if str(case.get("case_id")) != "PRIVATE_KEY_MATERIAL_MARKER":
                    continue
                payload = case.get("synthetic_payload", {})
                if not isinstance(payload, dict):
                    continue
                synthetic_case_marker_ok = (
                    str(payload.get("marker_type")) == "PRIVATE_KEY_MATERIAL_MARKER"
                    and str(payload.get("marker_value")) == "SYNTHETIC_PRIVATE_KEY_MARKER_ONLY"
                    and bool(payload.get("contains_real_key_material")) is False
                )
        add_check(
            checks,
            warnings,
            blockers,
            "private_key_marker_is_synthetic_only",
            synthetic_case_marker_ok,
            "private key marker case is synthetic-only",
            "private key marker case is missing or not synthetic-only",
        )

    private_key_pattern_hits = scan_for_private_key_patterns(
        [
            negative_root / "NEGATIVE_TEST_CASE_CATALOG_V0_1.json",
            negative_root / "MUTATION_CHECK_POLICY_V0_1.json",
            negative_root / "FAKE_GREEN_REJECTION_RULES_V0_1.json",
            negative_root / "NEGATIVE_TEST_RESULT_MATRIX_V0_1.json",
            negative_root / "SAMPLES/NEGATIVE_TEST_SYNTHETIC_MUTANTS_V0_1.json",
        ]
    )
    add_check(
        checks,
        warnings,
        blockers,
        "no_real_private_key_pattern_found",
        not private_key_pattern_hits,
        "no real private-key material patterns found in negative-test artifacts",
        f"private-key pattern hits: {private_key_pattern_hits}",
    )

    if current_truth is not None:
        layer = current_truth.get("negative_test_mutation_check_layer", {})
        layer_ok = isinstance(layer, dict) and str(layer.get("status")) == "FOUNDATION_ONLY"
        add_check(
            checks,
            warnings,
            blockers,
            "current_truth_has_negative_test_layer_ref",
            layer_ok,
            "current truth root has negative-test foundation reference",
            "current truth root missing negative-test foundation reference",
        )

    if sanctum_state is not None:
        truth_index = sanctum_state.get("current_truth_index", {})
        index_ok = isinstance(truth_index, dict) and truth_index.get("negative_test_layer_status") == "FOUNDATION_ONLY"
        add_check(
            checks,
            warnings,
            blockers,
            "sanctum_state_has_negative_test_layer_ref",
            index_ok,
            "sanctum state has read-only negative-test layer reference",
            "sanctum state missing negative-test layer reference",
        )

    report_file_status = {
        path.name: ("PRESENT" if path.exists() else "MISSING")
        for path in required_report_paths
    }

    run_report = {
        "schema_id": "NEGATIVE_TEST_RUN_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "status": "PASS" if not blockers else "BLOCK",
        "required_case_count": len(REQUIRED_CASE_IDS),
        "result_row_count": len(matrix_rows),
        "safe_negative_classifications": sorted(SAFE_NEGATIVE_CLASSIFICATIONS),
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "report_bundle_file_status": report_file_status,
    }
    write_json(run_report_path, run_report)

    aggregate = {
        "schema_id": "TASK_VALIDATOR_AGGREGATE_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": "PASS" if not blockers else "BLOCK",
        "checks_total": len(checks),
        "warnings_total": len(warnings),
        "blockers_total": len(blockers),
        "checkpoints": {
            "negative_test_run_report": {
                "verdict": run_report["status"],
                "report_path": str(run_report_path.relative_to(repo_root)),
            },
            "required_report_bundle_presence": {
                "verdict": "PASS" if all(path.exists() for path in required_report_paths) else "WARN",
                "missing_files": [path.name for path in required_report_paths if not path.exists()],
            },
        },
        "warnings": warnings,
        "blockers": blockers,
    }
    write_json(output_path, aggregate)

    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
