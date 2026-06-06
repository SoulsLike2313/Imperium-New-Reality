#!/usr/bin/env python3
"""Synthetic Ghost_Evolve runtime corridor checker for VM3 taskpack proof."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-V0_1"
FIXTURE_ROOT = Path("IMPERIUM_NEW_GENERATION/MATRIX_SPINE/FIXTURES/SYNTHETIC_RUNTIME_CORRIDOR")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - defensive
        return None, str(exc)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_entry_ack(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["entry_ack root is not an object"]
    required_keys = [
        "task_id",
        "run_id",
        "repo_head",
        "contour",
        "read_files",
        "organ_packets",
        "matrix_packs",
        "scope",
        "capability_gaps",
        "verdict",
    ]
    errors: list[str] = []
    for key in required_keys:
        if key not in data:
            errors.append(f"missing required key: {key}")
    return errors


def validate_capability_split(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["capability_split root is not an object"]
    items = data.get("items")
    if not isinstance(items, list) or not items:
        return ["items must be a non-empty list"]

    errors: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{index}] is not an object")
            continue
        classification = item.get("classification")
        replay = item.get("gap_or_replay")
        if classification in {"LOCAL_SCRIPT_FIRST", "CANDIDATE_SCRIPT_FIRST"}:
            if not is_nonempty_string(replay) or "replay" not in replay.lower():
                errors.append(f"items[{index}] script-first entry missing replay command")
    return errors


def validate_red_team(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["red_team root is not an object"]
    required_keys = ["task_id", "builder_claims", "attacks", "downgrade_rules_applied", "final_verdict"]
    errors: list[str] = []
    for key in required_keys:
        if key not in data:
            errors.append(f"missing required key: {key}")
    return errors


def validate_final_receipt(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return ["final_receipt root is not an object"]

    errors: list[str] = []
    for key in [
        "base_head",
        "implementation_head",
        "proof_head",
        "closure_bundle_head",
        "final_verifier_head",
        "remote_head_after_bundle",
        "claim_ledger_path",
    ]:
        if not is_nonempty_string(data.get(key)):
            errors.append(f"{key} is missing or empty")

    if data.get("worktree_clean_after_bundle") is not True:
        errors.append("worktree_clean_after_bundle must be true")

    if data.get("origin_master_sync_after_bundle") is not True:
        errors.append("origin_master_sync_after_bundle must be true")

    verdict = data.get("verdict")
    if verdict in {"PASS", "PASS_WITH_WARNINGS"} and not is_nonempty_string(data.get("hard_red_team_verdict_path")):
        errors.append("hard_red_team_verdict_path required for PASS/PASS_WITH_WARNINGS")

    if not is_nonempty_string(data.get("implementation_commit_url")):
        errors.append("implementation_commit_url is required")
    if not is_nonempty_string(data.get("proof_commit_url")):
        errors.append("proof_commit_url is required")
    if not is_nonempty_string(data.get("closure_bundle_commit_url")):
        errors.append("closure_bundle_commit_url is required")

    replay_status = data.get("independent_replay_status")
    allowed_replay_status = {"INQUISITOR", "SPECULUM", "SEPARATE_REPLAY_RUNNER", "NONE"}
    if replay_status not in allowed_replay_status:
        errors.append("independent_replay_status must be typed")
    if replay_status == "NONE" and verdict == "PASS":
        errors.append("clean PASS forbidden when independent_replay_status is NONE")

    return errors


def step_result(step_id: str, name: str, errors: list[str], evidence: list[str]) -> dict[str, Any]:
    return {
        "id": step_id,
        "name": name,
        "status": "PASS" if not errors else "BLOCK",
        "evidence": evidence,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run synthetic runtime corridor proof.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else script_path.parents[3]

    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = (
            repo_root
            / "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS"
            / TASK_ID_DEFAULT
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    fixture_dir = repo_root / FIXTURE_ROOT
    entry_ack_path = fixture_dir / "entry_ack_fixture.json"
    capability_split_path = fixture_dir / "capability_split_fixture.json"
    red_team_path = fixture_dir / "red_team_verdict_fixture.json"
    final_receipt_path = fixture_dir / "final_receipt_fixture.json"

    steps: list[dict[str, Any]] = []

    entry_ack_data, entry_ack_error = load_json(entry_ack_path)
    s1_errors = [f"parse error: {entry_ack_error}"] if entry_ack_error else validate_entry_ack(entry_ack_data)
    steps.append(step_result("S1", "entry_ack_fixture", s1_errors, [str(entry_ack_path)]))

    matrix_output_dir = output_dir / "matrix_validator_run"
    validator_cmd = [
        sys.executable,
        str(repo_root / "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/validate_matrix_spine.py"),
        "--task-id",
        args.task_id,
        "--repo-root",
        str(repo_root),
        "--output-dir",
        str(matrix_output_dir),
    ]
    validator_run = subprocess.run(validator_cmd, capture_output=True, text=True)
    validator_summary_path = matrix_output_dir / "matrix_spine_validation_summary.json"

    s2_errors: list[str] = []
    if validator_run.returncode != 0:
        s2_errors.append("matrix validator returned non-zero status")

    summary_data, summary_error = load_json(validator_summary_path)
    if summary_error is not None or not isinstance(summary_data, dict):
        s2_errors.append(f"unable to read validator summary: {summary_error}")
    else:
        if summary_data.get("verdict") not in {"PASS", "PASS_WITH_WARNINGS"}:
            s2_errors.append("matrix validator verdict is not PASS/PASS_WITH_WARNINGS")
        negative_results = summary_data.get("negative_fixture_results")
        if isinstance(negative_results, list):
            typed_corridor_caught = any(
                isinstance(item, dict)
                and item.get("expected_issue_code") == "CAP_UNTYPED_RUNTIME_CLAIM"
                and item.get("detected") is True
                for item in negative_results
            )
            if not typed_corridor_caught:
                s2_errors.append("corridor naming negative fixture CAP_UNTYPED_RUNTIME_CLAIM not detected")
        else:
            s2_errors.append("negative_fixture_results missing in validator summary")

    steps.append(
        step_result(
            "S2",
            "matrix_validation",
            s2_errors,
            [
                str(validator_summary_path),
                str(matrix_output_dir / "matrix_spine_validation_report.md"),
            ],
        )
    )

    capability_data, capability_error = load_json(capability_split_path)
    s3_errors = [f"parse error: {capability_error}"] if capability_error else validate_capability_split(capability_data)
    steps.append(step_result("S3", "capability_split_fixture", s3_errors, [str(capability_split_path)]))

    red_team_data, red_team_error = load_json(red_team_path)
    s4_errors = [f"parse error: {red_team_error}"] if red_team_error else validate_red_team(red_team_data)
    steps.append(step_result("S4", "red_team_verdict_fixture", s4_errors, [str(red_team_path)]))

    final_receipt_data, final_receipt_error = load_json(final_receipt_path)
    s5_errors = [f"parse error: {final_receipt_error}"] if final_receipt_error else validate_final_receipt(final_receipt_data)
    steps.append(step_result("S5", "final_receipt_fixture", s5_errors, [str(final_receipt_path)]))

    overall = "PASS" if all(step["status"] == "PASS" for step in steps) else "BLOCK"

    receipt = {
        "task_id": args.task_id,
        "corridor_type": "synthetic_corridor",
        "not_real_warp": True,
        "typed_runtime_claim_allowed": ["synthetic_corridor", "real_runtime_corridor", "warp_corridor"],
        "timestamp_utc": utc_now(),
        "steps": steps,
        "overall": overall,
        "replay_command": "bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.sh",
        "matrix_validation_output_dir": str(matrix_output_dir),
        "matrix_validator_stdout": validator_run.stdout.strip(),
        "matrix_validator_stderr": validator_run.stderr.strip(),
    }

    receipt_path = output_dir / "synthetic_corridor_receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    report_lines = [
        f"# Synthetic Runtime Corridor Report — {args.task_id}",
        "",
        f"Timestamp (UTC): {receipt['timestamp_utc']}",
        "",
        "## Steps",
    ]
    for step in steps:
        report_lines.append(
            f"- {step['id']} {step['name']}: {step['status']}"
        )
        if step["errors"]:
            for error in step["errors"]:
                report_lines.append(f"  - error: {error}")
    report_lines.extend([
        "",
        "## Overall",
        f"- Verdict: {overall}",
        "- Corridor type: synthetic_corridor (training/replay only).",
        "- Synthetic only: real_runtime_corridor and warp_corridor are intentionally out of scope.",
        "",
        "## Replay",
        "- bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.sh",
        "",
    ])
    (output_dir / "synthetic_runtime_corridor_report.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(f"[synthetic-corridor] output_dir={output_dir}")
    print(f"[synthetic-corridor] overall={overall}")
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
