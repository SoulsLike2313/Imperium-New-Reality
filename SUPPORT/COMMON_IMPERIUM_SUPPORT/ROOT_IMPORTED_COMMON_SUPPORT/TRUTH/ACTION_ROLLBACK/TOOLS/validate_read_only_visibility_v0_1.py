#!/usr/bin/env python3
"""Validate read-only visibility integration for SSH matrix and action rollback layer."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-MECHANICUS-SSH-MATRIX-AND-ACTION-ROLLBACK-CONTRACT-VM2-V0_1"
CURRENT_TRUTH_REL = "IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json"
SANCTUM_STATE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / "IMPERIUM_NEW_GENERATION/REPORTS" / TASK_ID_DEFAULT

    parser = argparse.ArgumentParser(description="Validate read-only visibility integration.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", type=Path, default=default_report_dir / "READ_ONLY_VISIBILITY_VALIDATOR_REPORT.json")
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

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    current_truth_path = repo_root / CURRENT_TRUTH_REL
    sanctum_state_path = repo_root / SANCTUM_STATE_REL

    current_truth, current_truth_err = load_json(current_truth_path)
    sanctum_state, sanctum_state_err = load_json(sanctum_state_path)

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

    if current_truth is not None:
        ssh_ref = current_truth.get("mechanicus_ssh_connection_registry")
        rollback_ref = current_truth.get("action_rollback_contract_layer")

        add_check(
            checks,
            warnings,
            blockers,
            "current_truth_ssh_ref_exists",
            isinstance(ssh_ref, dict),
            "current truth has mechanicus ssh registry reference",
            "current truth missing mechanicus_ssh_connection_registry section",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "current_truth_rollback_ref_exists",
            isinstance(rollback_ref, dict),
            "current truth has action rollback layer reference",
            "current truth missing action_rollback_contract_layer section",
        )

        if isinstance(ssh_ref, dict):
            status_ok = ssh_ref.get("status") == "FOUNDATION_ONLY"
            add_check(
                checks,
                warnings,
                blockers,
                "ssh_ref_foundation_status",
                status_ok,
                "ssh registry status is FOUNDATION_ONLY",
                "ssh registry status is not FOUNDATION_ONLY",
            )

            path = str(ssh_ref.get("ssh_matrix_path", ""))
            add_check(
                checks,
                warnings,
                blockers,
                "ssh_ref_path_exists",
                bool(path) and (repo_root / path).exists(),
                "ssh matrix path exists",
                "ssh matrix path missing or does not exist",
            )

            add_check(
                checks,
                warnings,
                blockers,
                "ssh_private_key_rule",
                ssh_ref.get("private_key_material_allowed_in_repo") is False,
                "ssh reference explicitly disallows private key material",
                "ssh reference does not enforce private_key_material_allowed_in_repo=false",
            )

        if isinstance(rollback_ref, dict):
            status_ok = rollback_ref.get("status") == "FOUNDATION_ONLY"
            add_check(
                checks,
                warnings,
                blockers,
                "rollback_ref_foundation_status",
                status_ok,
                "rollback layer status is FOUNDATION_ONLY",
                "rollback layer status is not FOUNDATION_ONLY",
            )

            policy_path = str(rollback_ref.get("policy_path", ""))
            add_check(
                checks,
                warnings,
                blockers,
                "rollback_policy_path_exists",
                bool(policy_path) and (repo_root / policy_path).exists(),
                "rollback policy path exists",
                "rollback policy path missing or does not exist",
            )

    if sanctum_state is not None:
        truth_index = sanctum_state.get("current_truth_index", {})
        safety_layers = sanctum_state.get("foundation_safety_layers", {})

        add_check(
            checks,
            warnings,
            blockers,
            "sanctum_truth_index_exists",
            isinstance(truth_index, dict),
            "sanctum current_truth_index exists",
            "sanctum current_truth_index section missing",
        )

        if isinstance(truth_index, dict):
            ssh_path = str(truth_index.get("mechanicus_ssh_connection_registry_path", ""))
            rollback_path = str(truth_index.get("action_rollback_policy_path", ""))
            add_check(
                checks,
                warnings,
                blockers,
                "sanctum_truth_index_ssh_path",
                bool(ssh_path) and (repo_root / ssh_path).exists(),
                "sanctum truth index references ssh matrix",
                "sanctum truth index missing ssh matrix reference",
            )
            add_check(
                checks,
                warnings,
                blockers,
                "sanctum_truth_index_rollback_path",
                bool(rollback_path) and (repo_root / rollback_path).exists(),
                "sanctum truth index references rollback policy",
                "sanctum truth index missing rollback policy reference",
            )

        add_check(
            checks,
            warnings,
            blockers,
            "sanctum_foundation_safety_layers_exists",
            isinstance(safety_layers, dict),
            "sanctum foundation_safety_layers section exists",
            "sanctum missing foundation_safety_layers section",
        )

        if isinstance(safety_layers, dict):
            safety_status = str(safety_layers.get("status", ""))
            add_check(
                checks,
                warnings,
                blockers,
                "sanctum_foundation_safety_layers_status",
                safety_status == "FOUNDATION_ONLY",
                "sanctum safety layer status is FOUNDATION_ONLY",
                "sanctum safety layer status is not FOUNDATION_ONLY",
            )

    forbidden_live_claim_patterns = [
        "LIVE_BACKEND_READY",
        "AUTONOMOUS_EXECUTION_READY",
        "PRODUCTION_READY",
        "ROLLBACK_TESTED_ON_DESTRUCTIVE_MUTATIONS",
    ]

    focused_objects: list[dict[str, Any]] = []
    if current_truth is not None:
        ssh_ref = current_truth.get("mechanicus_ssh_connection_registry")
        rollback_ref = current_truth.get("action_rollback_contract_layer")
        if isinstance(ssh_ref, dict):
            focused_objects.append(ssh_ref)
        if isinstance(rollback_ref, dict):
            focused_objects.append(rollback_ref)
    if sanctum_state is not None:
        truth_index = sanctum_state.get("current_truth_index")
        safety_layers = sanctum_state.get("foundation_safety_layers")
        if isinstance(truth_index, dict):
            focused_objects.append(truth_index)
        if isinstance(safety_layers, dict):
            focused_objects.append(safety_layers)

    combined_text = json.dumps(focused_objects, ensure_ascii=False)

    found_forbidden = [pattern for pattern in forbidden_live_claim_patterns if pattern in combined_text]
    add_check(
        checks,
        warnings,
        blockers,
        "no_fake_live_claims_in_visibility_refs",
        not found_forbidden,
        "visibility references do not claim live/autonomous/destructive-tested readiness",
        f"forbidden live claim patterns found: {found_forbidden}",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "READ_ONLY_VISIBILITY_VALIDATOR_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validated_paths": {
            "current_truth": CURRENT_TRUTH_REL,
            "sanctum_state": SANCTUM_STATE_REL,
        },
        "no_fake_green_note": "PASS means read-only visibility references exist without fake live readiness claims.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"read_only_visibility_verdict={verdict}")
    print(f"read_only_visibility_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
