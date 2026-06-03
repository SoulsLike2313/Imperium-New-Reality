#!/usr/bin/env python3
"""Validate Partial Acceptance Map V0.1 artifacts and no-fake-green rules."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import py_compile
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-PQG-PARTIAL-ACCEPTANCE-MAP-VM3-V0_1"
TRUTH_ROOT_REL = "IMPERIUM_NEW_GENERATION/TRUTH"
REPORT_DIR_REL = f"IMPERIUM_NEW_GENERATION/REPORTS/{TASK_ID_DEFAULT}"

REQUIRED_STATUSES = {
    "PASS_STRICT",
    "PASS_WITH_WARN",
    "PARTIAL_ACCEPTED",
    "PARTIAL_BLOCKED",
    "FOUNDATION_ONLY",
    "UNKNOWN",
    "MISSING",
    "STALE",
    "NOT_READY",
    "BLOCKED",
    "FAKE_GREEN_RISK",
}

REQUIRED_RULE_IDS = {
    "NO_EVIDENCE_NO_STRICT_PASS",
    "UNKNOWN_CANNOT_CONTINUE_AS_GREEN",
    "PARTIAL_REQUIRES_REASON_AND_OWNER_OR_CONTRACT_BASIS",
}

REQUIRED_SAMPLE_OUTCOMES = {
    "PASS_STRICT",
    "PASS_WITH_WARN",
    "FOUNDATION_ONLY",
    "UNKNOWN",
    "MISSING",
    "STALE",
    "PARTIAL_ACCEPTED",
    "PARTIAL_BLOCKED",
}


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / REPORT_DIR_REL

    parser = argparse.ArgumentParser(description="Validate Partial Acceptance Map V0.1 artifacts.")
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

    map_path = repo_root / TRUTH_ROOT_REL / "PARTIAL_ACCEPTANCE_MAP_V0_1.json"
    rules_path = repo_root / TRUTH_ROOT_REL / "ACCEPTANCE_DECISION_RULES_V0_1.json"
    samples_path = repo_root / TRUTH_ROOT_REL / "ACCEPTANCE_DECISION_SAMPLES_V0_1.json"
    current_truth_path = repo_root / TRUTH_ROOT_REL / "CURRENT_TRUTH_ROOT_V0_1.json"
    sanctum_state_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"

    schema_paths = [
        repo_root / TRUTH_ROOT_REL / "SCHEMAS/PARTIAL_ACCEPTANCE_MAP_V0_1.schema.json",
        repo_root / TRUTH_ROOT_REL / "SCHEMAS/ACCEPTANCE_DECISION_RULES_V0_1.schema.json",
        repo_root / TRUTH_ROOT_REL / "SCHEMAS/ACCEPTANCE_DECISION_RECORD_V0_1.schema.json",
    ]

    tool_paths = [
        repo_root / TRUTH_ROOT_REL / "TOOLS/build_partial_acceptance_map_v0_1.py",
        repo_root / TRUTH_ROOT_REL / "TOOLS/validate_partial_acceptance_map_v0_1.py",
    ]

    required_report_paths = [
        report_dir / "FINAL_OWNER_REPORT_RU.md",
        report_dir / "FINAL_RECEIPT.json",
        report_dir / "POST_COMMIT_CLOSURE_RECEIPT.json",
        report_dir / "STEP_PROOF_RECORDS.jsonl",
        report_dir / "CONTEXT_SOURCE_REPORT.md",
        report_dir / "CONTEXT_SOURCE_REPORT.json",
        report_dir / "KPD_SLICE.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.json",
    ]

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    core_files = [map_path, rules_path, samples_path, current_truth_path, sanctum_state_path] + schema_paths + tool_paths
    add_check(
        checks,
        warnings,
        blockers,
        "core_partial_acceptance_artifacts_exist",
        all(path.exists() for path in core_files),
        "all core partial acceptance artifacts exist",
        "one or more core partial acceptance artifacts are missing",
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

    partial_map, map_err = load_json(map_path)
    rules_payload, rules_err = load_json(rules_path)
    samples_payload, samples_err = load_json(samples_path)
    current_truth, current_truth_err = load_json(current_truth_path)
    sanctum_state, sanctum_state_err = load_json(sanctum_state_path)

    add_check(checks, warnings, blockers, "partial_map_parse", partial_map is not None, "partial map parses", f"partial map parse failed ({map_err})")
    add_check(checks, warnings, blockers, "rules_parse", rules_payload is not None, "rules parse", f"rules parse failed ({rules_err})")
    add_check(checks, warnings, blockers, "samples_parse", samples_payload is not None, "samples parse", f"samples parse failed ({samples_err})")
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

    if partial_map is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "partial_map_schema_id",
            partial_map.get("schema_id") == "PARTIAL_ACCEPTANCE_MAP_V0_1",
            "partial map schema_id is correct",
            "partial map schema_id mismatch",
        )

        statuses = partial_map.get("statuses", [])
        if not isinstance(statuses, list):
            statuses = []

        status_map: dict[str, dict[str, Any]] = {}
        for item in statuses:
            if isinstance(item, dict):
                status_map[str(item.get("status"))] = item

        present_statuses = set(status_map.keys())
        missing_statuses = sorted(REQUIRED_STATUSES - present_statuses)
        add_check(
            checks,
            warnings,
            blockers,
            "required_statuses_present",
            not missing_statuses,
            "all required statuses are present in partial acceptance map",
            f"missing statuses: {missing_statuses}",
        )

        no_green_statuses = ["UNKNOWN", "MISSING", "STALE", "FAKE_GREEN_RISK"]
        no_green_violations = []
        for status in no_green_statuses:
            node = status_map.get(status, {})
            if not isinstance(node, dict):
                no_green_violations.append(f"{status}:missing_record")
                continue
            if node.get("can_continue") is True:
                no_green_violations.append(f"{status}:can_continue=true")
            if node.get("production_claim_allowed") is True:
                no_green_violations.append(f"{status}:production_claim_allowed=true")

        add_check(
            checks,
            warnings,
            blockers,
            "unknown_missing_stale_fake_green_non_green",
            not no_green_violations,
            "UNKNOWN/MISSING/STALE/FAKE_GREEN_RISK remain non-green",
            f"non-green rule violations: {no_green_violations}",
        )

        strict_node = status_map.get("PASS_STRICT", {})
        strict_ok = isinstance(strict_node, dict) and strict_node.get("evidence_required") is True
        add_check(
            checks,
            warnings,
            blockers,
            "strict_pass_requires_evidence",
            strict_ok,
            "PASS_STRICT requires evidence",
            "PASS_STRICT does not require evidence",
        )

        partial_acc_node = status_map.get("PARTIAL_ACCEPTED", {})
        partial_acc_ok = (
            isinstance(partial_acc_node, dict)
            and partial_acc_node.get("owner_decision_required") is True
            and partial_acc_node.get("evidence_required") is True
        )
        add_check(
            checks,
            warnings,
            blockers,
            "partial_accepted_requires_owner_and_evidence",
            partial_acc_ok,
            "PARTIAL_ACCEPTED requires owner decision and evidence",
            "PARTIAL_ACCEPTED missing owner/evidence requirement",
        )

    if rules_payload is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "rules_schema_id",
            rules_payload.get("schema_id") == "ACCEPTANCE_DECISION_RULES_V0_1",
            "rules schema_id is correct",
            "rules schema_id mismatch",
        )

        rules = rules_payload.get("rules", [])
        if not isinstance(rules, list):
            rules = []

        rule_id_map: dict[str, dict[str, Any]] = {}
        for rule in rules:
            if isinstance(rule, dict):
                rule_id_map[str(rule.get("rule_id"))] = rule

        missing_rule_ids = sorted(REQUIRED_RULE_IDS - set(rule_id_map.keys()))
        add_check(
            checks,
            warnings,
            blockers,
            "required_rule_ids_present",
            not missing_rule_ids,
            "required rule ids are present",
            f"missing required rule ids: {missing_rule_ids}",
        )

        no_evidence_rule = rule_id_map.get("NO_EVIDENCE_NO_STRICT_PASS", {})
        no_evidence_ok = isinstance(no_evidence_rule, dict) and no_evidence_rule.get("then_outcome") != "PASS_STRICT"
        add_check(
            checks,
            warnings,
            blockers,
            "no_evidence_rule_no_strict_pass",
            no_evidence_ok,
            "NO_EVIDENCE_NO_STRICT_PASS prevents strict pass",
            "NO_EVIDENCE_NO_STRICT_PASS incorrectly allows strict pass",
        )

        partial_basis_rule = rule_id_map.get("PARTIAL_REQUIRES_REASON_AND_OWNER_OR_CONTRACT_BASIS", {})
        partial_basis_when = partial_basis_rule.get("when", {}) if isinstance(partial_basis_rule, dict) else {}
        partial_basis_ok = (
            isinstance(partial_basis_when, dict)
            and partial_basis_when.get("reason_present") is True
            and partial_basis_when.get("owner_or_contract_basis") is True
        )
        add_check(
            checks,
            warnings,
            blockers,
            "partial_basis_rule_strictness",
            partial_basis_ok,
            "partial acceptance rule requires reason and owner/contract basis",
            "partial acceptance rule is missing reason/basis requirement",
        )

    if samples_payload is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "samples_schema_id",
            samples_payload.get("schema_id") == "ACCEPTANCE_DECISION_SAMPLES_V0_1",
            "samples schema_id is correct",
            "samples schema_id mismatch",
        )

        samples = samples_payload.get("samples", [])
        if not isinstance(samples, list):
            samples = []

        sample_outcomes = {str(sample.get("expected_outcome")) for sample in samples if isinstance(sample, dict)}
        missing_sample_outcomes = sorted(REQUIRED_SAMPLE_OUTCOMES - sample_outcomes)
        add_check(
            checks,
            warnings,
            blockers,
            "required_sample_outcomes_present",
            not missing_sample_outcomes,
            "required sample outcomes are present",
            f"missing required sample outcomes: {missing_sample_outcomes}",
        )

        strict_samples = [s for s in samples if isinstance(s, dict) and s.get("expected_outcome") == "PASS_STRICT"]
        strict_samples_ok = bool(strict_samples)
        for sample in strict_samples:
            sample_input = sample.get("input", {})
            if not isinstance(sample_input, dict):
                strict_samples_ok = False
                break
            if sample_input.get("evidence_present") is not True:
                strict_samples_ok = False
                break

        add_check(
            checks,
            warnings,
            blockers,
            "strict_sample_requires_evidence",
            strict_samples_ok,
            "strict sample(s) require evidence",
            "PASS_STRICT sample missing evidence requirement",
        )

        partial_acc_samples = [s for s in samples if isinstance(s, dict) and s.get("expected_outcome") == "PARTIAL_ACCEPTED"]
        partial_acc_samples_ok = bool(partial_acc_samples)
        for sample in partial_acc_samples:
            sample_input = sample.get("input", {})
            if not isinstance(sample_input, dict):
                partial_acc_samples_ok = False
                break
            if sample_input.get("reason_present") is not True:
                partial_acc_samples_ok = False
                break
            if not (sample_input.get("owner_decision_confirmed") is True or sample_input.get("contract_basis_present") is True):
                partial_acc_samples_ok = False
                break

        add_check(
            checks,
            warnings,
            blockers,
            "partial_accepted_sample_requires_basis",
            partial_acc_samples_ok,
            "PARTIAL_ACCEPTED sample requires reason and owner/contract basis",
            "PARTIAL_ACCEPTED sample missing reason/basis requirement",
        )

    if current_truth is not None:
        truth_ref_keys = [
            "partial_acceptance_map_path",
            "acceptance_decision_rules_path",
            "acceptance_decision_samples_path",
        ]
        missing_truth_keys = [key for key in truth_ref_keys if key not in current_truth]
        add_check(
            checks,
            warnings,
            blockers,
            "current_truth_has_acceptance_refs",
            not missing_truth_keys,
            "current truth contains acceptance reference paths",
            f"current truth missing acceptance refs: {missing_truth_keys}",
        )

        layer = current_truth.get("partial_acceptance_layer", {})
        layer_ok = isinstance(layer, dict) and layer.get("status") == "FOUNDATION_ONLY"
        add_check(
            checks,
            warnings,
            blockers,
            "current_truth_acceptance_layer_foundation",
            layer_ok,
            "current truth acceptance layer is foundation-only",
            "current truth acceptance layer is missing or not foundation-only",
        )

    if sanctum_state is not None:
        index = sanctum_state.get("current_truth_index", {})
        index_ok = isinstance(index, dict)
        add_check(
            checks,
            warnings,
            blockers,
            "sanctum_current_truth_index_present",
            index_ok,
            "sanctum current truth index present",
            "sanctum current truth index missing",
        )

        if isinstance(index, dict):
            missing_sanctum_refs = [
                key
                for key in [
                    "partial_acceptance_map_path",
                    "acceptance_decision_rules_path",
                    "acceptance_decision_samples_path",
                ]
                if key not in index
            ]
            add_check(
                checks,
                warnings,
                blockers,
                "sanctum_acceptance_refs_present",
                not missing_sanctum_refs,
                "sanctum index has acceptance references",
                f"sanctum index missing acceptance refs: {missing_sanctum_refs}",
            )

    add_check(
        checks,
        warnings,
        blockers,
        "report_bundle_files_exist",
        all(path.exists() for path in required_report_paths),
        "required report bundle files exist",
        "one or more required report bundle files are missing",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "PARTIAL_ACCEPTANCE_MAP_VALIDATOR_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validated_paths": {
            "partial_acceptance_map": map_path.relative_to(repo_root).as_posix(),
            "acceptance_decision_rules": rules_path.relative_to(repo_root).as_posix(),
            "acceptance_decision_samples": samples_path.relative_to(repo_root).as_posix(),
            "current_truth_root": current_truth_path.relative_to(repo_root).as_posix(),
            "sanctum_state": sanctum_state_path.relative_to(repo_root).as_posix(),
            "report_dir": report_dir.relative_to(repo_root).as_posix(),
        },
        "no_fake_green_note": "Validator blocks strict-green interpretation for UNKNOWN/MISSING/STALE/FAKE_GREEN_RISK and enforces evidence for PASS_STRICT.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"validator_verdict={verdict}")
    print(f"validator_report={output_path.relative_to(repo_root).as_posix()}")

    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
