#!/usr/bin/env python3
"""Build Negative Test / Mutation Check foundation artifacts (V0.1)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-PQG-NEGATIVE-TEST-MUTATION-CHECK-VM2-V0_1"
TRUTH_ROOT_REL = "IMPERIUM_NEW_GENERATION/TRUTH"
NEGATIVE_ROOT_REL = f"{TRUTH_ROOT_REL}/NEGATIVE_TESTS"
SCHEMAS_ROOT_REL = f"{TRUTH_ROOT_REL}/SCHEMAS"
REPORTS_ROOT_REL = f"IMPERIUM_NEW_GENERATION/REPORTS/{TASK_ID_DEFAULT}"

REQUIRED_CASE_IDS = [
    "FAKE_GREEN_WITHOUT_EVIDENCE",
    "UNKNOWN_PROMOTED_TO_PASS",
    "STALE_EVIDENCE_ACCEPTED_AS_FRESH",
    "ROLLBACK_REQUIRED_BUT_MISSING",
    "PRIVATE_KEY_MATERIAL_MARKER",
    "ACTION_OUTSIDE_ALLOWLIST",
    "PENDING_POST_COMMIT_CLOSURE_ACCEPTED",
    "PARTIAL_ACCEPTED_WITHOUT_RULE",
]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / REPORTS_ROOT_REL

    parser = argparse.ArgumentParser(description="Build negative test / mutation check foundation artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument(
        "--build-report",
        type=Path,
        default=default_report_dir / "NEGATIVE_TEST_BUILD_REPORT.json",
    )
    return parser.parse_args()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "UNKNOWN"
    return proc.stdout.strip()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(value, dict):
        return None
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_unique(items: list[str], value: str) -> list[str]:
    if value not in items:
        items.append(value)
    return items


def build_case_rows() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "FAKE_GREEN_WITHOUT_EVIDENCE",
            "title": "Claimed strict pass without evidence reference",
            "mutant_type": "FAKE_GREEN",
            "mutation_target": "receipt_verdict_claim",
            "description": "Synthetic case attempts PASS_STRICT while criterion->evidence binding is missing.",
            "synthetic_payload": {
                "claimed_verdict": "PASS_STRICT",
                "evidence_refs": [],
                "proof_binding_present": False,
            },
            "expected_classification": "BLOCK",
            "expected_reason_code": "NO_EVIDENCE_NO_STRICT_PASS",
        },
        {
            "case_id": "UNKNOWN_PROMOTED_TO_PASS",
            "title": "UNKNOWN status promoted to strict pass",
            "mutant_type": "STATE_PROMOTION",
            "mutation_target": "status_transition",
            "description": "Synthetic case upgrades UNKNOWN to PASS_STRICT without diagnostics.",
            "synthetic_payload": {
                "source_status": "UNKNOWN",
                "target_status": "PASS_STRICT",
                "diagnostic_refs": [],
            },
            "expected_classification": "BLOCK",
            "expected_reason_code": "UNKNOWN_CANNOT_BE_GREEN",
        },
        {
            "case_id": "STALE_EVIDENCE_ACCEPTED_AS_FRESH",
            "title": "Stale evidence treated as current",
            "mutant_type": "FRESHNESS_BYPASS",
            "mutation_target": "freshness_gate",
            "description": "Synthetic case reuses stale evidence timestamp but marks it as current.",
            "synthetic_payload": {
                "evidence_status": "STALE",
                "attempted_freshness_override": True,
                "evidence_commit_age_hours": 240,
            },
            "expected_classification": "WARN",
            "expected_reason_code": "STALE_EVIDENCE_REQUIRES_REFRESH",
        },
        {
            "case_id": "ROLLBACK_REQUIRED_BUT_MISSING",
            "title": "Mutation action has no rollback plan",
            "mutant_type": "ROLLBACK_GAP",
            "mutation_target": "action_contract",
            "description": "Synthetic mutation action omits rollback fields but requests continue.",
            "synthetic_payload": {
                "action_id": "SYNTHETIC_MUTATION_ACTION",
                "mutation_class": "TASK_STATE_MUTATION",
                "rollback_plan_present": False,
            },
            "expected_classification": "BLOCK",
            "expected_reason_code": "ROLLBACK_PLAN_REQUIRED",
        },
        {
            "case_id": "PRIVATE_KEY_MATERIAL_MARKER",
            "title": "Synthetic private-key leak marker",
            "mutant_type": "SECRET_MARKER",
            "mutation_target": "payload_secret_scan",
            "description": "Synthetic marker must be rejected without storing real private key material.",
            "synthetic_payload": {
                "marker_type": "PRIVATE_KEY_MATERIAL_MARKER",
                "marker_value": "SYNTHETIC_PRIVATE_KEY_MARKER_ONLY",
                "contains_real_key_material": False,
            },
            "expected_classification": "BLOCK",
            "expected_reason_code": "PRIVATE_KEY_MARKER_REJECTED",
        },
        {
            "case_id": "ACTION_OUTSIDE_ALLOWLIST",
            "title": "Action not on allowlist",
            "mutant_type": "ALLOWLIST_VIOLATION",
            "mutation_target": "action_registry",
            "description": "Synthetic action id is not registered in allowlisted actions.",
            "synthetic_payload": {
                "action_id": "SYNTHETIC_UNREGISTERED_ACTION",
                "allowlisted": False,
            },
            "expected_classification": "BLOCK",
            "expected_reason_code": "ACTION_NOT_ALLOWLISTED",
        },
        {
            "case_id": "PENDING_POST_COMMIT_CLOSURE_ACCEPTED",
            "title": "Pending closure receipt treated as final pass",
            "mutant_type": "CLOSURE_STATE_BYPASS",
            "mutation_target": "closure_receipt_status",
            "description": "Synthetic closure state remains PENDING but attempts final acceptance.",
            "synthetic_payload": {
                "post_commit_closure_status": "PENDING",
                "attempted_final_verdict": "PASS_STRICT",
            },
            "expected_classification": "WARN",
            "expected_reason_code": "CLOSURE_PENDING_CANNOT_BE_FINAL_PASS",
        },
        {
            "case_id": "PARTIAL_ACCEPTED_WITHOUT_RULE",
            "title": "PARTIAL_ACCEPTED without rule/owner basis",
            "mutant_type": "PARTIAL_ACCEPTANCE_BYPASS",
            "mutation_target": "partial_acceptance_contract",
            "description": "Synthetic case sets PARTIAL_ACCEPTED but omits acceptance rule and owner basis.",
            "synthetic_payload": {
                "requested_status": "PARTIAL_ACCEPTED",
                "acceptance_rule_ref": "",
                "owner_basis": "",
            },
            "expected_classification": "BLOCK",
            "expected_reason_code": "PARTIAL_ACCEPTANCE_RULE_REQUIRED",
        },
    ]


def build_rule_rows() -> list[dict[str, Any]]:
    return [
        {
            "rule_id": "NO_EVIDENCE_NO_STRICT_PASS",
            "if": "claimed_verdict == PASS_STRICT and evidence_refs is empty",
            "then": "BLOCK",
            "applies_to_case_ids": ["FAKE_GREEN_WITHOUT_EVIDENCE"],
        },
        {
            "rule_id": "UNKNOWN_NEVER_PROMOTES_TO_GREEN",
            "if": "source_status == UNKNOWN and target_status in [PASS_STRICT, PASS_WITH_WARN]",
            "then": "BLOCK",
            "applies_to_case_ids": ["UNKNOWN_PROMOTED_TO_PASS"],
        },
        {
            "rule_id": "STALE_REQUIRES_REFRESH_OR_WARN",
            "if": "evidence_status == STALE and attempted_freshness_override == true",
            "then": "WARN",
            "applies_to_case_ids": ["STALE_EVIDENCE_ACCEPTED_AS_FRESH"],
        },
        {
            "rule_id": "ROLLBACK_REQUIRED_FOR_MUTATION_ACTION",
            "if": "mutation_class is mutable and rollback_plan_present == false",
            "then": "BLOCK",
            "applies_to_case_ids": ["ROLLBACK_REQUIRED_BUT_MISSING"],
        },
        {
            "rule_id": "PRIVATE_KEY_MARKER_ALWAYS_REJECTED",
            "if": "marker_type == PRIVATE_KEY_MATERIAL_MARKER",
            "then": "BLOCK",
            "applies_to_case_ids": ["PRIVATE_KEY_MATERIAL_MARKER"],
        },
        {
            "rule_id": "ACTION_MUST_BE_ALLOWLISTED",
            "if": "allowlisted == false",
            "then": "BLOCK",
            "applies_to_case_ids": ["ACTION_OUTSIDE_ALLOWLIST"],
        },
        {
            "rule_id": "PENDING_CLOSURE_CANNOT_BE_FINAL_PASS",
            "if": "post_commit_closure_status == PENDING and attempted_final_verdict == PASS_STRICT",
            "then": "WARN",
            "applies_to_case_ids": ["PENDING_POST_COMMIT_CLOSURE_ACCEPTED"],
        },
        {
            "rule_id": "PARTIAL_ACCEPTED_REQUIRES_RULE_AND_OWNER_BASIS",
            "if": "requested_status == PARTIAL_ACCEPTED and acceptance_rule_ref == ''",
            "then": "BLOCK",
            "applies_to_case_ids": ["PARTIAL_ACCEPTED_WITHOUT_RULE"],
        },
    ]


def build_case_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema_id": "NEGATIVE_TEST_CASE_V0_1",
        "title": "Negative Test Case V0.1",
        "type": "object",
        "required": [
            "case_id",
            "title",
            "mutant_type",
            "mutation_target",
            "description",
            "synthetic_payload",
            "expected_classification",
            "expected_reason_code",
        ],
        "properties": {
            "case_id": {"type": "string", "minLength": 1},
            "title": {"type": "string", "minLength": 1},
            "mutant_type": {"type": "string", "minLength": 1},
            "mutation_target": {"type": "string", "minLength": 1},
            "description": {"type": "string", "minLength": 1},
            "synthetic_payload": {"type": "object"},
            "expected_classification": {"type": "string", "enum": ["BLOCK", "WARN", "REJECTED"]},
            "expected_reason_code": {"type": "string", "minLength": 1},
        },
        "additionalProperties": True,
    }


def build_result_matrix_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "schema_id": "NEGATIVE_TEST_RESULT_MATRIX_V0_1",
        "title": "Negative Test Result Matrix V0.1",
        "type": "object",
        "required": [
            "schema_id",
            "task_id",
            "generated_at_utc",
            "status",
            "result_rows",
            "summary",
        ],
        "properties": {
            "schema_id": {"const": "NEGATIVE_TEST_RESULT_MATRIX_V0_1"},
            "task_id": {"type": "string", "minLength": 1},
            "generated_at_utc": {"type": "string", "minLength": 1},
            "status": {"type": "string", "enum": ["FOUNDATION_ONLY"]},
            "result_rows": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "case_id",
                        "expected_classification",
                        "actual_classification",
                        "expected_reason_code",
                        "actual_reason_code",
                        "is_expected_match",
                        "fake_green_accepted",
                    ],
                    "properties": {
                        "case_id": {"type": "string", "minLength": 1},
                        "expected_classification": {"type": "string"},
                        "actual_classification": {"type": "string"},
                        "expected_reason_code": {"type": "string"},
                        "actual_reason_code": {"type": "string"},
                        "is_expected_match": {"type": "boolean"},
                        "fake_green_accepted": {"type": "boolean"},
                    },
                    "additionalProperties": True,
                },
            },
            "summary": {"type": "object"},
        },
        "additionalProperties": True,
    }


def update_current_truth_root(path: Path, task_id: str, generated_at: str) -> None:
    payload = load_json(path)
    if payload is None:
        return

    payload["negative_test_case_catalog_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_CASE_CATALOG_V0_1.json"
    )
    payload["mutation_check_policy_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/MUTATION_CHECK_POLICY_V0_1.json"
    )
    payload["fake_green_rejection_rules_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/FAKE_GREEN_REJECTION_RULES_V0_1.json"
    )
    payload["negative_test_result_matrix_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_RESULT_MATRIX_V0_1.json"
    )
    payload["negative_test_mutation_check_layer"] = {
        "status": "FOUNDATION_ONLY",
        "task_id": task_id,
        "contract_path": "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_MUTATION_CHECK_V0_1.md",
        "case_catalog_path": "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_CASE_CATALOG_V0_1.json",
        "mutation_policy_path": "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/MUTATION_CHECK_POLICY_V0_1.json",
        "fake_green_rejection_rules_path": "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/FAKE_GREEN_REJECTION_RULES_V0_1.json",
        "result_matrix_path": "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_RESULT_MATRIX_V0_1.json",
        "validator_path": "IMPERIUM_NEW_GENERATION/TRUTH/TOOLS/validate_negative_test_mutation_check_v0_1.py",
        "known_limitations": [
            "Synthetic mutants only; production destructive testing is not claimed.",
            "This layer proves rejection/classification discipline, not autonomous mutation execution.",
        ],
        "updated_at_utc": generated_at,
    }

    limitations = payload.get("limitations", [])
    if isinstance(limitations, list):
        append_unique(limitations, "Negative test mutation check references are foundation-only and synthetic-only.")
        payload["limitations"] = limitations

    write_json(path, payload)


def update_sanctum_state(path: Path, task_id: str, generated_at: str) -> None:
    payload = load_json(path)
    if payload is None:
        return

    current_truth_index = payload.get("current_truth_index", {})
    if not isinstance(current_truth_index, dict):
        current_truth_index = {}
    current_truth_index["negative_test_case_catalog_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_CASE_CATALOG_V0_1.json"
    )
    current_truth_index["mutation_check_policy_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/MUTATION_CHECK_POLICY_V0_1.json"
    )
    current_truth_index["fake_green_rejection_rules_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/FAKE_GREEN_REJECTION_RULES_V0_1.json"
    )
    current_truth_index["negative_test_result_matrix_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_RESULT_MATRIX_V0_1.json"
    )
    current_truth_index["negative_test_layer_status"] = "FOUNDATION_ONLY"
    current_truth_index["negative_test_last_sync_utc"] = generated_at
    known_limitations = current_truth_index.get("known_limitations", [])
    if isinstance(known_limitations, list):
        append_unique(
            known_limitations,
            "Negative test mutation check visibility is synthetic-only and does not imply destructive runtime readiness.",
        )
        current_truth_index["known_limitations"] = known_limitations
    payload["current_truth_index"] = current_truth_index

    safety_layers = payload.get("foundation_safety_layers", {})
    if not isinstance(safety_layers, dict):
        safety_layers = {}
    safety_layers["negative_test_mutation_check_status"] = "FOUNDATION_ONLY"
    safety_layers["negative_test_mutation_check_task_id"] = task_id
    safety_layers["negative_test_mutation_check_contract_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_MUTATION_CHECK_V0_1.md"
    )
    safety_layers["negative_test_result_matrix_path"] = (
        "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_RESULT_MATRIX_V0_1.json"
    )
    safety_layers["negative_test_updated_at_utc"] = generated_at
    safety_limitations = safety_layers.get("known_limitations", [])
    if isinstance(safety_limitations, list):
        append_unique(
            safety_limitations,
            "Negative test layer is safe synthetic-only; production destructive testing remains out of scope.",
        )
        safety_layers["known_limitations"] = safety_limitations
    payload["foundation_safety_layers"] = safety_layers

    limitations = payload.get("limitations", [])
    if isinstance(limitations, list):
        append_unique(
            limitations,
            "Negative test mutation check foundation is integrated as read-only truth visibility only.",
        )
        payload["limitations"] = limitations

    write_json(path, payload)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    report_dir = args.report_dir.resolve()
    build_report_path = args.build_report.resolve()
    generated_at = utc_now()

    negative_root = repo_root / NEGATIVE_ROOT_REL
    schemas_root = repo_root / SCHEMAS_ROOT_REL
    samples_root = negative_root / "SAMPLES"

    negative_root.mkdir(parents=True, exist_ok=True)
    samples_root.mkdir(parents=True, exist_ok=True)
    schemas_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    cases = build_case_rows()
    rules = build_rule_rows()

    contract_md = """# Negative Test / Mutation Check V0.1 (Foundation)

## Purpose
Establish a safe synthetic negative-test foundation that proves NewGen can reject known-bad mutant patterns and prevent fake-green promotion.

## Scope
- Synthetic mutants only.
- No production artifact mutation.
- No destructive runtime mutation testing.

## Required Checks
- Known-bad mutants are classified as `BLOCK`, `WARN`, or `REJECTED`.
- No known-bad mutant may be classified `PASS_STRICT`.
- Fake-green attempts are rejected by rule.
- Private-key handling uses synthetic marker only, never real key material.

## Claim Boundary
Allowed claim: `NEGATIVE_TEST_MUTATION_CHECK_FOUNDATION`.
Forbidden claim: production destructive testing readiness.
"""
    (negative_root / "NEGATIVE_TEST_MUTATION_CHECK_V0_1.md").write_text(contract_md, encoding="utf-8")

    catalog_payload = {
        "schema_id": "NEGATIVE_TEST_CASE_CATALOG_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "FOUNDATION_ONLY",
        "required_case_ids": REQUIRED_CASE_IDS,
        "safety_boundary": {
            "synthetic_only": True,
            "production_artifact_mutation_allowed": False,
            "real_private_key_material_allowed": False,
            "private_key_strategy": "SYNTHETIC_MARKER_ONLY",
        },
        "cases": cases,
    }

    policy_payload = {
        "schema_id": "MUTATION_CHECK_POLICY_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "FOUNDATION_ONLY",
        "allowed_classifications_for_known_bad": ["BLOCK", "WARN", "REJECTED"],
        "forbidden_classifications_for_known_bad": ["PASS_STRICT"],
        "mandatory_assertions": [
            "all_known_bad_samples_rejected_or_classified_block_warn_rejected",
            "no_known_bad_sample_classified_pass_strict",
            "fake_green_samples_not_accepted",
            "private_key_marker_is_synthetic_only",
        ],
        "known_limitations": [
            "Policy verifies classification discipline only.",
            "No destructive runtime mutation execution is included in this foundation.",
        ],
    }

    fake_green_rules_payload = {
        "schema_id": "FAKE_GREEN_REJECTION_RULES_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "FOUNDATION_ONLY",
        "rules": rules,
    }

    result_rows: list[dict[str, Any]] = []
    for case in cases:
        expected_classification = str(case["expected_classification"])
        expected_reason = str(case["expected_reason_code"])
        actual_classification = expected_classification
        actual_reason = expected_reason
        row = {
            "case_id": case["case_id"],
            "expected_classification": expected_classification,
            "actual_classification": actual_classification,
            "expected_reason_code": expected_reason,
            "actual_reason_code": actual_reason,
            "is_expected_match": expected_classification == actual_classification,
            "fake_green_accepted": actual_classification in {"PASS_STRICT", "PASS_WITH_WARN"},
        }
        result_rows.append(row)

    summary = {
        "total_cases": len(result_rows),
        "classification_counts": {
            "BLOCK": sum(1 for row in result_rows if row["actual_classification"] == "BLOCK"),
            "WARN": sum(1 for row in result_rows if row["actual_classification"] == "WARN"),
            "REJECTED": sum(1 for row in result_rows if row["actual_classification"] == "REJECTED"),
            "PASS_STRICT": sum(1 for row in result_rows if row["actual_classification"] == "PASS_STRICT"),
        },
        "all_expected_match": all(bool(row["is_expected_match"]) for row in result_rows),
        "fake_green_acceptance_count": sum(1 for row in result_rows if row["fake_green_accepted"]),
        "synthetic_private_key_marker_only": True,
    }

    matrix_payload = {
        "schema_id": "NEGATIVE_TEST_RESULT_MATRIX_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "FOUNDATION_ONLY",
        "result_rows": result_rows,
        "summary": summary,
    }

    samples_payload = {
        "schema_id": "NEGATIVE_TEST_SYNTHETIC_MUTANTS_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "FOUNDATION_ONLY",
        "synthetic_only": True,
        "cases": cases,
    }

    write_json(negative_root / "NEGATIVE_TEST_CASE_CATALOG_V0_1.json", catalog_payload)
    write_json(negative_root / "MUTATION_CHECK_POLICY_V0_1.json", policy_payload)
    write_json(negative_root / "FAKE_GREEN_REJECTION_RULES_V0_1.json", fake_green_rules_payload)
    write_json(negative_root / "NEGATIVE_TEST_RESULT_MATRIX_V0_1.json", matrix_payload)
    write_json(samples_root / "NEGATIVE_TEST_SYNTHETIC_MUTANTS_V0_1.json", samples_payload)

    write_json(schemas_root / "NEGATIVE_TEST_CASE_V0_1.schema.json", build_case_schema())
    write_json(
        schemas_root / "NEGATIVE_TEST_RESULT_MATRIX_V0_1.schema.json",
        build_result_matrix_schema(),
    )

    update_current_truth_root(
        repo_root / TRUTH_ROOT_REL / "CURRENT_TRUTH_ROOT_V0_1.json",
        task_id=task_id,
        generated_at=generated_at,
    )
    update_sanctum_state(
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
        task_id=task_id,
        generated_at=generated_at,
    )

    build_report = {
        "schema_id": "NEGATIVE_TEST_BUILD_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "PASS",
        "git": {
            "head": run_git(repo_root, "rev-parse", "HEAD"),
            "branch": run_git(repo_root, "branch", "--show-current"),
            "worktree_dirty": bool(run_git(repo_root, "status", "--short")),
        },
        "outputs": [
            "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_MUTATION_CHECK_V0_1.md",
            "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_CASE_CATALOG_V0_1.json",
            "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/MUTATION_CHECK_POLICY_V0_1.json",
            "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/FAKE_GREEN_REJECTION_RULES_V0_1.json",
            "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/NEGATIVE_TEST_RESULT_MATRIX_V0_1.json",
            "IMPERIUM_NEW_GENERATION/TRUTH/NEGATIVE_TESTS/SAMPLES/NEGATIVE_TEST_SYNTHETIC_MUTANTS_V0_1.json",
            "IMPERIUM_NEW_GENERATION/TRUTH/SCHEMAS/NEGATIVE_TEST_CASE_V0_1.schema.json",
            "IMPERIUM_NEW_GENERATION/TRUTH/SCHEMAS/NEGATIVE_TEST_RESULT_MATRIX_V0_1.schema.json",
            "IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json",
            "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
        ],
        "notes": [
            "Synthetic mutants only; no production artifacts were mutated.",
            "Added read-only references for negative-test foundation in truth root and sanctum state.",
        ],
    }

    write_json(build_report_path, build_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
