#!/usr/bin/env python3
"""Build Partial Acceptance Map V0.1 foundation artifacts for NewGen Truth Spine."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-PQG-PARTIAL-ACCEPTANCE-MAP-VM3-V0_1"
TRUTH_ROOT_REL = "IMPERIUM_NEW_GENERATION/TRUTH"
CURRENT_TRUTH_REL = f"{TRUTH_ROOT_REL}/CURRENT_TRUTH_ROOT_V0_1.json"
REPORT_INDEX_REL = f"{TRUTH_ROOT_REL}/REPORT_STATUS_INDEX_V0_1.json"
EVIDENCE_MAP_UNIFIED_REL = f"{TRUTH_ROOT_REL}/EVIDENCE_MAP_UNIFIED_V0_1.json"
EVIDENCE_FRESHNESS_REL = f"{TRUTH_ROOT_REL}/EVIDENCE_FRESHNESS_INDEX_V0_1.json"
NORMALIZATION_REL = f"{TRUTH_ROOT_REL}/REPORT_STATUS_NORMALIZATION_TABLE_V0_1.json"
NOT_PROVEN_REL = f"{TRUTH_ROOT_REL}/NOT_PROVEN_REGISTER_V0_1.json"

PARTIAL_ACCEPTANCE_MAP_REL = f"{TRUTH_ROOT_REL}/PARTIAL_ACCEPTANCE_MAP_V0_1.json"
ACCEPTANCE_RULES_REL = f"{TRUTH_ROOT_REL}/ACCEPTANCE_DECISION_RULES_V0_1.json"
ACCEPTANCE_SAMPLES_REL = f"{TRUTH_ROOT_REL}/ACCEPTANCE_DECISION_SAMPLES_V0_1.json"


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / "IMPERIUM_NEW_GENERATION/REPORTS" / TASK_ID_DEFAULT

    parser = argparse.ArgumentParser(description="Build Partial Acceptance Map V0.1 artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--partial-acceptance-map-output", type=Path, default=default_repo_root / PARTIAL_ACCEPTANCE_MAP_REL)
    parser.add_argument("--acceptance-rules-output", type=Path, default=default_repo_root / ACCEPTANCE_RULES_REL)
    parser.add_argument("--acceptance-samples-output", type=Path, default=default_repo_root / ACCEPTANCE_SAMPLES_REL)
    parser.add_argument("--current-truth-output", type=Path, default=default_repo_root / CURRENT_TRUTH_REL)
    parser.add_argument(
        "--build-report",
        type=Path,
        default=default_report_dir / "PARTIAL_ACCEPTANCE_BUILD_REPORT.json",
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


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def deterministic_generated_at(payloads: list[dict[str, Any] | None]) -> str:
    stamps: list[str] = []
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        stamp = payload.get("generated_at_utc")
        if isinstance(stamp, str) and stamp.strip():
            stamps.append(stamp.strip())
    if stamps:
        # ISO-8601 UTC strings sort lexicographically by time.
        return sorted(stamps)[-1]
    return utc_now()


def build_partial_acceptance_statuses() -> list[dict[str, Any]]:
    return [
        {
            "status": "PASS_STRICT",
            "meaning": "All required evidence and freshness checks passed with no unresolved boundaries.",
            "can_continue": True,
            "owner_decision_required": False,
            "rerun_required": False,
            "evidence_required": True,
            "freshness_required": True,
            "production_claim_allowed": True,
            "ui_truth_color_hint": "green",
            "sanctum_display_label": "Strict Pass",
            "next_action": "Proceed with scoped next step and preserve receipt chain.",
            "forbidden_claims": [],
        },
        {
            "status": "PASS_WITH_WARN",
            "meaning": "Core acceptance passed but warnings remain explicit and bounded.",
            "can_continue": True,
            "owner_decision_required": True,
            "rerun_required": False,
            "evidence_required": True,
            "freshness_required": True,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "amber",
            "sanctum_display_label": "Pass With Warn",
            "next_action": "Continue only with visible warnings and a bounded follow-up plan.",
            "forbidden_claims": [
                "STRICT_GREEN",
                "ZERO_RISK",
            ],
        },
        {
            "status": "PARTIAL_ACCEPTED",
            "meaning": "Partial outcome is accepted only with explicit reason and owner or contract basis.",
            "can_continue": True,
            "owner_decision_required": True,
            "rerun_required": True,
            "evidence_required": True,
            "freshness_required": True,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "amber",
            "sanctum_display_label": "Partial Accepted",
            "next_action": "Execute bounded next action and schedule rerun/closure evidence.",
            "forbidden_claims": [
                "STRICT_PASS",
                "PRODUCTION_READY",
            ],
        },
        {
            "status": "PARTIAL_BLOCKED",
            "meaning": "Partial status lacks minimum basis and is blocked from continuation as green.",
            "can_continue": False,
            "owner_decision_required": True,
            "rerun_required": True,
            "evidence_required": True,
            "freshness_required": True,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "red",
            "sanctum_display_label": "Partial Blocked",
            "next_action": "Add missing reason/basis or convert to explicit BLOCKED path.",
            "forbidden_claims": [
                "GREEN_BY_ASSUMPTION",
                "PRODUCTION_READY",
            ],
        },
        {
            "status": "FOUNDATION_ONLY",
            "meaning": "Artifact is a foundation layer and not production acceptance proof.",
            "can_continue": True,
            "owner_decision_required": True,
            "rerun_required": False,
            "evidence_required": True,
            "freshness_required": False,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "blue",
            "sanctum_display_label": "Foundation Only",
            "next_action": "Use as backend baseline and plan promotion checks before strict claims.",
            "forbidden_claims": [
                "PRODUCTION_READY",
                "LIVE_AUTONOMY_READY",
            ],
        },
        {
            "status": "UNKNOWN",
            "meaning": "Truth is unknown; no acceptance upgrade is allowed.",
            "can_continue": False,
            "owner_decision_required": True,
            "rerun_required": True,
            "evidence_required": True,
            "freshness_required": False,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "gray",
            "sanctum_display_label": "Unknown",
            "next_action": "Create diagnostics or measurement contract before execution.",
            "forbidden_claims": [
                "STRICT_PASS",
                "GREEN_CONTINUE",
            ],
        },
        {
            "status": "MISSING",
            "meaning": "Required artifacts/evidence are missing.",
            "can_continue": False,
            "owner_decision_required": True,
            "rerun_required": True,
            "evidence_required": True,
            "freshness_required": False,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "red",
            "sanctum_display_label": "Missing",
            "next_action": "Restore missing artifact and rerun validator before acceptance.",
            "forbidden_claims": [
                "PASS",
                "COMPLETED",
            ],
        },
        {
            "status": "STALE",
            "meaning": "Evidence exists but is stale for current acceptance claim.",
            "can_continue": False,
            "owner_decision_required": True,
            "rerun_required": True,
            "evidence_required": True,
            "freshness_required": True,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "orange",
            "sanctum_display_label": "Stale",
            "next_action": "Refresh evidence and re-evaluate acceptance with current receipts.",
            "forbidden_claims": [
                "CURRENT_GREEN",
                "STRICT_PASS",
            ],
        },
        {
            "status": "NOT_READY",
            "meaning": "Task slice is not ready for acceptance decision.",
            "can_continue": False,
            "owner_decision_required": True,
            "rerun_required": False,
            "evidence_required": False,
            "freshness_required": False,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "slate",
            "sanctum_display_label": "Not Ready",
            "next_action": "Complete prerequisite contracts or receipts first.",
            "forbidden_claims": [
                "PASS",
                "READY_FOR_PRODUCTION",
            ],
        },
        {
            "status": "BLOCKED",
            "meaning": "Hard blocker prevents valid acceptance progression.",
            "can_continue": False,
            "owner_decision_required": True,
            "rerun_required": False,
            "evidence_required": True,
            "freshness_required": False,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "crimson",
            "sanctum_display_label": "Blocked",
            "next_action": "Resolve blocker or terminate with explicit BLOCK receipt.",
            "forbidden_claims": [
                "PASS",
                "AUTO_CONTINUE",
            ],
        },
        {
            "status": "FAKE_GREEN_RISK",
            "meaning": "Detected mismatch where a green claim is attempted without required basis.",
            "can_continue": False,
            "owner_decision_required": True,
            "rerun_required": True,
            "evidence_required": True,
            "freshness_required": True,
            "production_claim_allowed": False,
            "ui_truth_color_hint": "red",
            "sanctum_display_label": "Fake Green Risk",
            "next_action": "Downgrade claim and attach missing evidence/freshness proof before retry.",
            "forbidden_claims": [
                "STRICT_PASS",
                "PRODUCTION_READY",
                "DONE_WITHOUT_RECEIPT",
            ],
        },
    ]


def build_acceptance_rules() -> list[dict[str, Any]]:
    return [
        {
            "rule_id": "NO_EVIDENCE_NO_STRICT_PASS",
            "priority": 10,
            "when": {
                "candidate_outcome_any_of": ["PASS_STRICT", "PASS_WITH_WARN"],
                "evidence_present": False,
            },
            "then_outcome": "FAKE_GREEN_RISK",
            "rationale": "Green-like outcomes require explicit evidence links.",
            "no_fake_green": True,
        },
        {
            "rule_id": "UNKNOWN_CANNOT_CONTINUE_AS_GREEN",
            "priority": 20,
            "when": {
                "normalized_status": "UNKNOWN",
            },
            "then_outcome": "UNKNOWN",
            "rationale": "UNKNOWN must stay non-green until direct proof exists.",
            "no_fake_green": True,
        },
        {
            "rule_id": "MISSING_IS_BLOCKING_FOR_ACCEPTANCE",
            "priority": 30,
            "when": {
                "normalized_status": "MISSING",
            },
            "then_outcome": "MISSING",
            "rationale": "Missing artifacts block acceptance progression.",
            "no_fake_green": True,
        },
        {
            "rule_id": "STALE_EVIDENCE_REQUIRES_REFRESH",
            "priority": 40,
            "when": {
                "freshness": "STALE",
            },
            "then_outcome": "STALE",
            "rationale": "Stale proof cannot represent current acceptance truth.",
            "no_fake_green": True,
        },
        {
            "rule_id": "PARTIAL_REQUIRES_REASON_AND_OWNER_OR_CONTRACT_BASIS",
            "priority": 50,
            "when": {
                "normalized_status": "PARTIAL",
                "evidence_present": True,
                "reason_present": True,
                "owner_or_contract_basis": True,
            },
            "then_outcome": "PARTIAL_ACCEPTED",
            "rationale": "Partial can proceed only with explicit reason and decision basis.",
            "no_fake_green": True,
        },
        {
            "rule_id": "PARTIAL_WITHOUT_BASIS_IS_BLOCKED",
            "priority": 60,
            "when": {
                "normalized_status": "PARTIAL",
                "reason_present": False,
                "owner_or_contract_basis": False,
            },
            "then_outcome": "PARTIAL_BLOCKED",
            "rationale": "Partial without explicit basis is blocked to avoid hidden risk.",
            "no_fake_green": True,
        },
        {
            "rule_id": "FOUNDATION_ONLY_REMAINS_FOUNDATION",
            "priority": 70,
            "when": {
                "normalized_status": "FOUNDATION_ONLY",
            },
            "then_outcome": "FOUNDATION_ONLY",
            "rationale": "Foundation status is useful but not a production claim.",
            "no_fake_green": True,
        },
        {
            "rule_id": "STRICT_PASS_REQUIRES_CURRENT_EVIDENCE",
            "priority": 80,
            "when": {
                "normalized_status_any_of": ["PASS", "PASS_STRICT"],
                "evidence_present": True,
                "freshness": "CURRENT",
                "production_claim_requested": False,
            },
            "then_outcome": "PASS_STRICT",
            "rationale": "Strict pass requires current evidence and bounded claim scope.",
            "no_fake_green": True,
        },
        {
            "rule_id": "PASS_WITH_WARN_RETAINS_WARN_BOUNDARY",
            "priority": 90,
            "when": {
                "normalized_status_any_of": ["PASS_WITH_WARN", "WARN"],
                "evidence_present": True,
            },
            "then_outcome": "PASS_WITH_WARN",
            "rationale": "Warnings must remain explicit; no silent strict upgrade.",
            "no_fake_green": True,
        },
        {
            "rule_id": "NOT_READY_FOR_UNSET_OR_PENDING",
            "priority": 100,
            "when": {
                "normalized_status_any_of": ["PENDING_POST_COMMIT", "NOT_READY"],
            },
            "then_outcome": "NOT_READY",
            "rationale": "Pending or precondition-missing states are not acceptance-ready.",
            "no_fake_green": True,
        },
        {
            "rule_id": "BLOCK_REMAINS_BLOCKED",
            "priority": 110,
            "when": {
                "normalized_status": "BLOCK",
            },
            "then_outcome": "BLOCKED",
            "rationale": "Block status must remain hard-blocked in acceptance map.",
            "no_fake_green": True,
        },
    ]


def build_acceptance_samples() -> list[dict[str, Any]]:
    return [
        {
            "sample_id": "SAMPLE_PASS_STRICT_CURRENT_EVIDENCE",
            "input": {
                "normalized_status": "PASS",
                "evidence_present": True,
                "freshness": "CURRENT",
                "reason_present": True,
                "owner_decision_confirmed": False,
                "contract_basis_present": True,
                "production_claim_requested": False,
            },
            "expected_outcome": "PASS_STRICT",
            "reason": "Current evidence and no warning boundary allow strict pass.",
            "claim_boundary": "No production/autonomy claim implied outside task contract.",
        },
        {
            "sample_id": "SAMPLE_PASS_WITH_WARN",
            "input": {
                "normalized_status": "WARN",
                "evidence_present": True,
                "freshness": "PARTIAL",
                "reason_present": True,
                "owner_decision_confirmed": True,
                "contract_basis_present": False,
                "production_claim_requested": False,
            },
            "expected_outcome": "PASS_WITH_WARN",
            "reason": "Warnings preserved with explicit bounded continuation.",
            "claim_boundary": "Strict green is forbidden while WARN boundary exists.",
        },
        {
            "sample_id": "SAMPLE_FOUNDATION_ONLY",
            "input": {
                "normalized_status": "FOUNDATION_ONLY",
                "evidence_present": True,
                "freshness": "FOUNDATION_ONLY",
                "reason_present": True,
                "owner_decision_confirmed": True,
                "contract_basis_present": True,
                "production_claim_requested": False,
            },
            "expected_outcome": "FOUNDATION_ONLY",
            "reason": "Foundation artifact remains foundation until promoted by separate scope.",
            "claim_boundary": "No production readiness claim is allowed.",
        },
        {
            "sample_id": "SAMPLE_UNKNOWN",
            "input": {
                "normalized_status": "UNKNOWN",
                "evidence_present": False,
                "freshness": "UNKNOWN",
                "reason_present": False,
                "owner_decision_confirmed": False,
                "contract_basis_present": False,
                "production_claim_requested": False,
            },
            "expected_outcome": "UNKNOWN",
            "reason": "Unknown remains unknown until direct proof exists.",
            "claim_boundary": "Cannot continue as green.",
        },
        {
            "sample_id": "SAMPLE_MISSING",
            "input": {
                "normalized_status": "MISSING",
                "evidence_present": False,
                "freshness": "MISSING",
                "reason_present": False,
                "owner_decision_confirmed": False,
                "contract_basis_present": False,
                "production_claim_requested": False,
            },
            "expected_outcome": "MISSING",
            "reason": "Missing artifacts block acceptance.",
            "claim_boundary": "No completion claim allowed.",
        },
        {
            "sample_id": "SAMPLE_STALE",
            "input": {
                "normalized_status": "PASS",
                "evidence_present": True,
                "freshness": "STALE",
                "reason_present": True,
                "owner_decision_confirmed": True,
                "contract_basis_present": True,
                "production_claim_requested": False,
            },
            "expected_outcome": "STALE",
            "reason": "Stale freshness downgrades acceptance even if historical status passed.",
            "claim_boundary": "Current strict green is forbidden.",
        },
        {
            "sample_id": "SAMPLE_PARTIAL_ACCEPTED",
            "input": {
                "normalized_status": "PARTIAL",
                "evidence_present": True,
                "freshness": "PARTIAL",
                "reason_present": True,
                "owner_decision_confirmed": True,
                "contract_basis_present": False,
                "production_claim_requested": False,
            },
            "expected_outcome": "PARTIAL_ACCEPTED",
            "reason": "Partial is accepted because reason and owner basis are explicit.",
            "claim_boundary": "Must carry rerun/closure action.",
        },
        {
            "sample_id": "SAMPLE_PARTIAL_BLOCKED",
            "input": {
                "normalized_status": "PARTIAL",
                "evidence_present": True,
                "freshness": "PARTIAL",
                "reason_present": False,
                "owner_decision_confirmed": False,
                "contract_basis_present": False,
                "production_claim_requested": False,
            },
            "expected_outcome": "PARTIAL_BLOCKED",
            "reason": "Partial without explicit basis is blocked.",
            "claim_boundary": "No green continuation allowed.",
        },
        {
            "sample_id": "SAMPLE_FAKE_GREEN_RISK",
            "input": {
                "normalized_status": "PASS",
                "evidence_present": False,
                "freshness": "UNKNOWN",
                "reason_present": False,
                "owner_decision_confirmed": False,
                "contract_basis_present": False,
                "production_claim_requested": True,
            },
            "expected_outcome": "FAKE_GREEN_RISK",
            "reason": "Green claim attempted without evidence must be flagged as fake-green risk.",
            "claim_boundary": "Requires downgrade and explicit evidence restoration.",
        },
    ]


def update_current_truth_root(
    repo_root: Path,
    task_id: str,
    generated_at: str,
    current_truth: dict[str, Any],
) -> dict[str, Any]:
    payload = dict(current_truth)

    payload["task_id"] = task_id
    payload["generated_at_utc"] = generated_at

    repo_truth = payload.get("repo_truth", {})
    if not isinstance(repo_truth, dict):
        repo_truth = {}
    repo_truth["repo_root"] = str(repo_root)
    repo_truth["head"] = run_git(repo_root, "rev-parse", "HEAD")
    repo_truth["branch"] = run_git(repo_root, "branch", "--show-current")
    repo_truth["worktree_dirty"] = bool(run_git(repo_root, "status", "--short"))
    repo_truth["head_commit_utc"] = run_git(repo_root, "show", "-s", "--format=%cI", "HEAD")
    payload["repo_truth"] = repo_truth

    payload["partial_acceptance_map_path"] = PARTIAL_ACCEPTANCE_MAP_REL
    payload["acceptance_decision_rules_path"] = ACCEPTANCE_RULES_REL
    payload["acceptance_decision_samples_path"] = ACCEPTANCE_SAMPLES_REL

    payload["partial_acceptance_layer"] = {
        "status": "FOUNDATION_ONLY",
        "partial_acceptance_map_path": PARTIAL_ACCEPTANCE_MAP_REL,
        "acceptance_decision_rules_path": ACCEPTANCE_RULES_REL,
        "acceptance_decision_samples_path": ACCEPTANCE_SAMPLES_REL,
        "known_limitations": [
            "Partial acceptance is a backend truth interpretation layer, not a production acceptance engine.",
            "UNKNOWN/MISSING/STALE boundaries remain explicit and non-green.",
            "Owner or contract basis is required for PARTIAL_ACCEPTED continuation.",
        ],
        "updated_at_utc": generated_at,
    }

    limitations = payload.get("limitations", [])
    if not isinstance(limitations, list):
        limitations = []
    limitations.append("Partial acceptance semantics are foundation-only and no fake-green upgrades are allowed.")
    payload["limitations"] = unique([str(item) for item in limitations])

    known_warnings = payload.get("known_warnings", [])
    if not isinstance(known_warnings, list):
        known_warnings = []
    payload["known_warnings"] = unique([str(item) for item in known_warnings])

    return payload


def build_payloads(repo_root: Path, task_id: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    current_truth = load_json(repo_root / CURRENT_TRUTH_REL) or {}
    report_index = load_json(repo_root / REPORT_INDEX_REL) or {}
    evidence_map = load_json(repo_root / EVIDENCE_MAP_UNIFIED_REL) or {}
    freshness = load_json(repo_root / EVIDENCE_FRESHNESS_REL) or {}
    normalization = load_json(repo_root / NORMALIZATION_REL) or {}
    not_proven = load_json(repo_root / NOT_PROVEN_REL) or {}

    generated_at = deterministic_generated_at(
        [
            current_truth,
            report_index,
            evidence_map,
            freshness,
            normalization,
            not_proven,
        ]
    )

    statuses = build_partial_acceptance_statuses()
    rules = build_acceptance_rules()
    samples = build_acceptance_samples()

    normalization_statuses = normalization.get("canonical_statuses", [])
    if not isinstance(normalization_statuses, list):
        normalization_statuses = []
    freshness_values = freshness.get("allowed_freshness_values", [])
    if not isinstance(freshness_values, list):
        freshness_values = []

    partial_acceptance_map = {
        "schema_id": "PARTIAL_ACCEPTANCE_MAP_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "source_truth_refs": [
            CURRENT_TRUTH_REL,
            REPORT_INDEX_REL,
            EVIDENCE_MAP_UNIFIED_REL,
            EVIDENCE_FRESHNESS_REL,
            NORMALIZATION_REL,
            NOT_PROVEN_REL,
        ],
        "source_snapshot": {
            "report_index_entries": len(report_index.get("entries", [])) if isinstance(report_index.get("entries"), list) else 0,
            "evidence_map_records": len(evidence_map.get("records", [])) if isinstance(evidence_map.get("records"), list) else 0,
            "freshness_entries": len(freshness.get("entries", [])) if isinstance(freshness.get("entries"), list) else 0,
            "not_proven_entries": len(not_proven.get("entries", [])) if isinstance(not_proven.get("entries"), list) else 0,
        },
        "statuses": statuses,
        "no_fake_green_invariants": [
            "NO_EVIDENCE_NO_STRICT_PASS",
            "UNKNOWN_CANNOT_CONTINUE_AS_GREEN",
            "MISSING_CANNOT_CONTINUE_AS_GREEN",
            "STALE_CANNOT_CONTINUE_AS_CURRENT_GREEN",
            "PARTIAL_REQUIRES_REASON_AND_OWNER_OR_CONTRACT_BASIS",
        ],
        "limitations": [
            "This is a foundation interpretation map and does not claim production acceptance automation.",
            "Outcomes are bounded by existing report/evidence/freshness artifacts.",
        ],
    }

    acceptance_rules = {
        "schema_id": "ACCEPTANCE_DECISION_RULES_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "input_contract": {
            "normalized_status_values": [str(item) for item in normalization_statuses],
            "freshness_values": [str(item) for item in freshness_values],
            "required_inputs": [
                "normalized_status",
                "evidence_present",
                "freshness",
                "reason_present",
                "owner_decision_confirmed",
                "contract_basis_present",
                "production_claim_requested",
            ],
        },
        "rules": rules,
        "priority_order": [str(rule["rule_id"]) for rule in rules],
        "no_fake_green_rules": [
            "NO_EVIDENCE_NO_STRICT_PASS",
            "UNKNOWN_CANNOT_CONTINUE_AS_GREEN",
            "PARTIAL_REQUIRES_REASON_AND_OWNER_OR_CONTRACT_BASIS",
        ],
        "limitations": [
            "Rules are deterministic and foundation-oriented.",
            "Rules do not override explicit BLOCKED contract outcomes.",
        ],
    }

    acceptance_samples = {
        "schema_id": "ACCEPTANCE_DECISION_SAMPLES_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "record_schema_path": "IMPERIUM_NEW_GENERATION/TRUTH/SCHEMAS/ACCEPTANCE_DECISION_RECORD_V0_1.schema.json",
        "samples": samples,
        "coverage": {
            "sample_count": len(samples),
            "covered_outcomes": unique([str(sample["expected_outcome"]) for sample in samples]),
        },
    }

    updated_current_truth = update_current_truth_root(repo_root, task_id, generated_at, current_truth)

    build_report = {
        "schema_id": "PARTIAL_ACCEPTANCE_BUILD_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": generated_at,
        "status": "PASS",
        "outputs": {
            "partial_acceptance_map": PARTIAL_ACCEPTANCE_MAP_REL,
            "acceptance_decision_rules": ACCEPTANCE_RULES_REL,
            "acceptance_decision_samples": ACCEPTANCE_SAMPLES_REL,
            "current_truth_root": CURRENT_TRUTH_REL,
        },
        "no_fake_green_note": "Builder encodes explicit non-green handling for UNKNOWN/MISSING/STALE/FAKE_GREEN_RISK.",
    }

    return partial_acceptance_map, acceptance_rules, acceptance_samples, updated_current_truth, build_report


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)

    partial_acceptance_map, acceptance_rules, acceptance_samples, updated_current_truth, build_report = build_payloads(
        repo_root,
        task_id,
    )

    write_json(args.partial_acceptance_map_output.resolve(), partial_acceptance_map)
    write_json(args.acceptance_rules_output.resolve(), acceptance_rules)
    write_json(args.acceptance_samples_output.resolve(), acceptance_samples)
    write_json(args.current_truth_output.resolve(), updated_current_truth)
    write_json(args.build_report.resolve(), build_report)

    print("build_status=PASS")
    print(f"partial_acceptance_map={args.partial_acceptance_map_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"acceptance_decision_rules={args.acceptance_rules_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"acceptance_decision_samples={args.acceptance_samples_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"current_truth_root_updated={args.current_truth_output.resolve().relative_to(repo_root).as_posix()}")
    print(f"build_report={args.build_report.resolve().relative_to(repo_root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
