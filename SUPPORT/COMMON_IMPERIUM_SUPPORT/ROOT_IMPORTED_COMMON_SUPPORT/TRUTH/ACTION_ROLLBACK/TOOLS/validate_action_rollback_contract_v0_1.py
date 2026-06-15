#!/usr/bin/env python3
"""Validate Action Rollback Contract V0.1 foundation artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-MECHANICUS-SSH-MATRIX-AND-ACTION-ROLLBACK-CONTRACT-VM2-V0_1"
ROLLBACK_ROOT_REL = "IMPERIUM_NEW_GENERATION/TRUTH/ACTION_ROLLBACK"

REQUIRED_MUTATION_CLASSES = {
    "READ_ONLY_ACTION",
    "GENERATED_STATE_REFRESH",
    "REPORT_WRITE_ACTION",
    "REGISTRY_UPDATE_ACTION",
    "TASK_STATE_MUTATION",
    "ORGAN_DIALOGUE_PACKET_WRITE",
    "SCOPE_MERGE_MUTATION",
    "DANGEROUS_ACTION",
}

REQUIRED_ROLLBACK_VERDICTS = {
    "ROLLBACK_NOT_REQUIRED",
    "ROLLBACK_BY_REBUILD",
    "ROLLBACK_BY_BACKUP_RESTORE",
    "ROLLBACK_BY_GIT_RESTORE",
    "ROLLBACK_REQUIRES_OWNER",
    "ROLLBACK_NOT_DEFINED_BLOCK",
    "DANGEROUS_ACTION_BLOCKED",
}

REQUIRED_ACTION_FIELDS = {
    "action_id",
    "mutation_class",
    "allowed_paths",
    "backup_required",
    "rollback_method",
    "rollback_evidence_required",
    "owner_approval_required",
    "failure_policy",
    "no_fake_green_rule",
    "preconditions",
    "postconditions",
}


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / "IMPERIUM_NEW_GENERATION/REPORTS" / TASK_ID_DEFAULT

    parser = argparse.ArgumentParser(description="Validate action rollback contract artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", type=Path, default=default_report_dir / "ACTION_ROLLBACK_VALIDATOR_REPORT.json")
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
    output_path = args.output.resolve()
    task_id = str(args.task_id)

    root = repo_root / ROLLBACK_ROOT_REL

    policy_path = root / "ACTION_ROLLBACK_POLICY_V0_1.json"
    classification_path = root / "ACTION_MUTATION_CLASSIFICATION_V0_1.json"
    rules_path = root / "ROLLBACK_DECISION_RULES_V0_1.json"
    sample_actions_path = root / "SAMPLES/ACTION_ROLLBACK_SAMPLE_ACTIONS_V0_1.json"

    required_paths = [
        root / "ACTION_ROLLBACK_CONTRACT_V0_1.md",
        policy_path,
        classification_path,
        rules_path,
        root / "SCHEMAS/action_rollback_policy_v0_1.schema.json",
        root / "SCHEMAS/action_mutation_classification_v0_1.schema.json",
        root / "SCHEMAS/rollback_decision_rules_v0_1.schema.json",
        root / "SCHEMAS/action_rollback_sample_actions_v0_1.schema.json",
        sample_actions_path,
        root / "TOOLS/validate_action_rollback_contract_v0_1.py",
    ]

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    add_check(
        checks,
        warnings,
        blockers,
        "rollback_core_files_exist",
        all(path.exists() for path in required_paths),
        "rollback contract core files exist",
        "one or more rollback core files are missing",
    )

    policy, policy_err = load_json(policy_path)
    classification, classification_err = load_json(classification_path)
    rules, rules_err = load_json(rules_path)
    sample_actions, sample_err = load_json(sample_actions_path)

    add_check(
        checks,
        warnings,
        blockers,
        "policy_parse",
        policy is not None,
        "policy json parses",
        f"policy parse failed ({policy_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "classification_parse",
        classification is not None,
        "classification json parses",
        f"classification parse failed ({classification_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "rules_parse",
        rules is not None,
        "decision rules json parses",
        f"decision rules parse failed ({rules_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "sample_actions_parse",
        sample_actions is not None,
        "sample actions json parses",
        f"sample actions parse failed ({sample_err})",
    )

    if classification is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "classification_schema_id",
            classification.get("schema_id") == "ACTION_MUTATION_CLASSIFICATION_V0_1",
            "classification schema id matches",
            "classification schema id mismatch",
        )

        required_list = classification.get("required_mutation_classes", [])
        required_set = {str(item) for item in required_list} if isinstance(required_list, list) else set()
        missing_from_required = sorted(REQUIRED_MUTATION_CLASSES - required_set)
        add_check(
            checks,
            warnings,
            blockers,
            "required_mutation_classes_declared",
            not missing_from_required,
            "all required mutation classes are declared",
            f"missing required mutation classes in declaration: {missing_from_required}",
        )

        class_rows = classification.get("mutation_classes", [])
        class_set = {
            str(item.get("mutation_class"))
            for item in class_rows
            if isinstance(item, dict)
        }
        missing_from_rows = sorted(REQUIRED_MUTATION_CLASSES - class_set)
        add_check(
            checks,
            warnings,
            blockers,
            "mutation_class_rows_present",
            not missing_from_rows,
            "mutation class rows cover all required classes",
            f"missing mutation class rows: {missing_from_rows}",
        )

    if policy is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "policy_schema_id",
            policy.get("schema_id") == "ACTION_ROLLBACK_POLICY_V0_1",
            "policy schema id matches",
            "policy schema id mismatch",
        )

        required_fields = policy.get("required_fields_per_action_contract", [])
        required_fields_set = {str(item) for item in required_fields} if isinstance(required_fields, list) else set()
        missing_fields = sorted(REQUIRED_ACTION_FIELDS - required_fields_set)
        add_check(
            checks,
            warnings,
            blockers,
            "required_action_fields_declared",
            not missing_fields,
            "all required action fields are declared in policy",
            f"missing required action fields in policy: {missing_fields}",
        )

        policy_classes = policy.get("required_mutation_classes", [])
        policy_class_set = {str(item) for item in policy_classes} if isinstance(policy_classes, list) else set()
        missing_policy_classes = sorted(REQUIRED_MUTATION_CLASSES - policy_class_set)
        add_check(
            checks,
            warnings,
            blockers,
            "policy_mutation_classes",
            not missing_policy_classes,
            "policy includes all required mutation classes",
            f"policy missing mutation classes: {missing_policy_classes}",
        )

        policy_verdicts = policy.get("required_rollback_verdicts", [])
        policy_verdict_set = {str(item) for item in policy_verdicts} if isinstance(policy_verdicts, list) else set()
        missing_policy_verdicts = sorted(REQUIRED_ROLLBACK_VERDICTS - policy_verdict_set)
        add_check(
            checks,
            warnings,
            blockers,
            "policy_rollback_verdicts",
            not missing_policy_verdicts,
            "policy includes all required rollback verdicts",
            f"policy missing rollback verdicts: {missing_policy_verdicts}",
        )

    rule_class_set: set[str] = set()
    if rules is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "rules_schema_id",
            rules.get("schema_id") == "ROLLBACK_DECISION_RULES_V0_1",
            "decision rules schema id matches",
            "decision rules schema id mismatch",
        )

        rules_required_verdicts = rules.get("required_rollback_verdicts", [])
        rules_verdict_set = (
            {str(item) for item in rules_required_verdicts}
            if isinstance(rules_required_verdicts, list)
            else set()
        )
        missing_rules_verdicts = sorted(REQUIRED_ROLLBACK_VERDICTS - rules_verdict_set)
        add_check(
            checks,
            warnings,
            blockers,
            "rules_required_verdicts",
            not missing_rules_verdicts,
            "decision rules declare all required rollback verdicts",
            f"decision rules missing rollback verdicts: {missing_rules_verdicts}",
        )

        rows = rules.get("rules", [])
        if isinstance(rows, list):
            rule_class_set = {
                str(item.get("mutation_class"))
                for item in rows
                if isinstance(item, dict)
            }
        missing_rule_classes = sorted(REQUIRED_MUTATION_CLASSES - rule_class_set)
        add_check(
            checks,
            warnings,
            blockers,
            "rules_cover_all_mutation_classes",
            not missing_rule_classes,
            "decision rules cover all required mutation classes",
            f"decision rules missing mutation classes: {missing_rule_classes}",
        )

    actions: list[dict[str, Any]] = []
    if sample_actions is not None:
        raw_actions = sample_actions.get("actions", [])
        if isinstance(raw_actions, list):
            actions = [item for item in raw_actions if isinstance(item, dict)]

        add_check(
            checks,
            warnings,
            blockers,
            "sample_actions_non_empty",
            len(actions) > 0,
            "sample actions are present",
            "sample actions list is empty",
        )

        missing_field_actions: list[str] = []
        unknown_class_actions: list[str] = []
        empty_no_fake_green: list[str] = []

        for action in actions:
            action_id = str(action.get("action_id", "UNKNOWN"))
            missing = sorted(field for field in REQUIRED_ACTION_FIELDS if field not in action)
            if missing:
                missing_field_actions.append(f"{action_id}:{','.join(missing)}")

            mutation_class = str(action.get("mutation_class", ""))
            if mutation_class not in REQUIRED_MUTATION_CLASSES:
                unknown_class_actions.append(action_id)

            no_fake_green_rule = str(action.get("no_fake_green_rule", "")).strip()
            if not no_fake_green_rule:
                empty_no_fake_green.append(action_id)

        add_check(
            checks,
            warnings,
            blockers,
            "sample_actions_have_required_fields",
            not missing_field_actions,
            "all sample actions include required rollback fields",
            f"sample actions missing required fields: {missing_field_actions}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "sample_actions_known_classes",
            not unknown_class_actions,
            "all sample actions use known mutation classes",
            f"sample actions with unknown mutation classes: {unknown_class_actions}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "sample_actions_no_fake_green_rules",
            not empty_no_fake_green,
            "all sample actions define no_fake_green_rule",
            f"actions missing no_fake_green_rule: {empty_no_fake_green}",
        )

        sampled_classes = {str(item.get("mutation_class")) for item in actions}
        missing_sample_classes = sorted(REQUIRED_MUTATION_CLASSES - sampled_classes)
        add_check(
            checks,
            warnings,
            blockers,
            "sample_coverage_all_classes",
            not missing_sample_classes,
            "sample actions cover all required mutation classes",
            f"sample actions missing mutation class coverage: {missing_sample_classes}",
        )

        dangerous_violations: list[str] = []
        for action in actions:
            if str(action.get("mutation_class")) != "DANGEROUS_ACTION":
                continue

            action_id = str(action.get("action_id", "UNKNOWN"))
            owner_required = action.get("owner_approval_required") is True
            owner_ref = str(action.get("owner_approval_contract_ref", "")).strip()
            approved = owner_required and bool(owner_ref)

            failure_policy = str(action.get("failure_policy", ""))
            rollback_method = str(action.get("rollback_method", ""))

            if approved:
                if rollback_method not in {"ROLLBACK_REQUIRES_OWNER", "ROLLBACK_BY_BACKUP_RESTORE"}:
                    dangerous_violations.append(
                        f"{action_id}:approved_dangerous_action_invalid_rollback_method={rollback_method}"
                    )
                continue

            if failure_policy != "DANGEROUS_ACTION_BLOCKED":
                dangerous_violations.append(
                    f"{action_id}:missing_block_failure_policy={failure_policy}"
                )
            if rollback_method != "DANGEROUS_ACTION_BLOCKED":
                dangerous_violations.append(
                    f"{action_id}:missing_block_rollback_method={rollback_method}"
                )

        add_check(
            checks,
            warnings,
            blockers,
            "dangerous_action_block_rule",
            not dangerous_violations,
            "dangerous actions are blocked unless explicit owner approval contract is present",
            f"dangerous action rule violations: {dangerous_violations}",
        )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "ACTION_ROLLBACK_VALIDATOR_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validated_paths": {
            "rollback_root": ROLLBACK_ROOT_REL,
            "policy": (policy_path.relative_to(repo_root).as_posix()),
            "classification": (classification_path.relative_to(repo_root).as_posix()),
            "decision_rules": (rules_path.relative_to(repo_root).as_posix()),
            "sample_actions": (sample_actions_path.relative_to(repo_root).as_posix()),
        },
        "no_fake_green_note": "PASS means rollback contract definitions are structurally safe; destructive mutation runtime testing is still out of scope.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"action_rollback_validator_verdict={verdict}")
    print(f"action_rollback_validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
