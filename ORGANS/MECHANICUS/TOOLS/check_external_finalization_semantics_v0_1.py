#!/usr/bin/env python3
"""Check external finalization semantics fixtures for paradox/cap/replay consistency."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CAP_SELF_HEAD_PARADOX = "CAP_SELF_HEAD_PARADOX"
CAP_AMBIGUOUS_FINAL_HEAD = "CAP_AMBIGUOUS_FINAL_HEAD"
CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING = "CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING"
CAP_CAP_CLOSED_WITHOUT_EVIDENCE = "CAP_CAP_CLOSED_WITHOUT_EVIDENCE"
CAP_REPLAY_STATE_AMBIGUOUS = "CAP_REPLAY_STATE_AMBIGUOUS"
CAP_STALE_REPLAY_USED_AS_CURRENT = "CAP_STALE_REPLAY_USED_AS_CURRENT"
CAP_FINALIZATION_SEMANTICS_CONTRADICTORY = "CAP_FINALIZATION_SEMANTICS_CONTRADICTORY"
CAP_WARP_CLAIMED_WITHOUT_UNLOCK = "CAP_WARP_CLAIMED_WITHOUT_UNLOCK"

BLOCKING_CAPS = {
    CAP_AMBIGUOUS_FINAL_HEAD,
    CAP_CAP_CLOSED_WITHOUT_EVIDENCE,
    CAP_STALE_REPLAY_USED_AS_CURRENT,
    CAP_FINALIZATION_SEMANTICS_CONTRADICTORY,
    CAP_WARP_CLAIMED_WITHOUT_UNLOCK,
}

CURRENT_TARGET_REPLAY_STATES = {
    "SEPARATE_REPLAY_RUNNER_FOR_TARGET",
    "INQUISITOR_REPLAY_FOR_TARGET",
    "SPECULUM_REPLAY_FOR_TARGET",
    "EXTERNAL_REPLAY_ACCEPTED",
}

REPLAY_STATES = {
    "NONE",
    "PRIOR_REPLAY_EXISTS",
    "SEPARATE_REPLAY_RUNNER_FOR_TARGET",
    "INQUISITOR_REPLAY_FOR_TARGET",
    "SPECULUM_REPLAY_FOR_TARGET",
    "EXTERNAL_REPLAY_ACCEPTED",
    "STALE_REPLAY_ONLY",
}

CLOSING_STATES = {"CLOSED_BY_REPLAY", "CLOSED_BY_EXTERNAL_REVIEW"}


@dataclass
class FixtureResult:
    fixture_id: str
    expected_verdict: str
    actual_verdict: str
    expected_caps: list[str]
    unexpected_caps: list[str]
    caps_triggered: list[str]
    checks_passed: bool
    notes: list[str]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_bool(value: Any) -> bool:
    return bool(value)


def evaluate_fixture(payload: dict[str, Any]) -> tuple[str, list[str], list[str]]:
    caps: set[str] = set()
    notes: list[str] = []

    receipt = payload.get("external_finalization_receipt", {})
    cap_states = payload.get("cap_closure_states", [])
    replay = payload.get("independent_replay_state", {})

    # Receipt checks
    required_receipt = [
        "receipt_subject_head",
        "last_verified_head_before_this_commit",
        "receipt_content_head",
        "remote_head_after_push",
        "verification_timestamp_utc",
        "verification_actor",
        "verification_method",
    ]
    for field in required_receipt:
        if not _as_text(receipt.get(field)):
            caps.add(CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING)
            notes.append(f"missing_receipt_field:{field}")

    if _as_text(receipt.get("external_delivery_head")) == "":
        caps.add(CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING)
        notes.append("external_delivery_head_missing")

    if _as_text(receipt.get("final_head")):
        caps.add(CAP_AMBIGUOUS_FINAL_HEAD)
        notes.append("legacy_final_head_present")

    if not _as_bool(receipt.get("self_head_paradox_handled")):
        caps.add(CAP_SELF_HEAD_PARADOX)
        notes.append("self_head_paradox_unhandled")

    if receipt.get("worktree_clean_after_push") is None:
        caps.add(CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING)
        notes.append("worktree_clean_after_push_missing")

    if receipt.get("origin_master_sync_after_push") is None:
        caps.add(CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING)
        notes.append("origin_master_sync_after_push_missing")

    if _as_bool(receipt.get("warp_claimed_without_unlock")):
        caps.add(CAP_WARP_CLAIMED_WITHOUT_UNLOCK)
        notes.append("warp_claimed_without_unlock")

    # Cap closure checks
    for idx, state_obj in enumerate(cap_states):
        state = _as_text(state_obj.get("state"))
        evidence = state_obj.get("evidence_for_state") or []
        closure_head = _as_text(state_obj.get("closure_head"))

        if state in CLOSING_STATES:
            if not evidence:
                caps.add(CAP_CAP_CLOSED_WITHOUT_EVIDENCE)
                notes.append(f"cap_state_{idx}_closed_without_evidence")
            if not closure_head:
                caps.add(CAP_CAP_CLOSED_WITHOUT_EVIDENCE)
                notes.append(f"cap_state_{idx}_closed_without_closure_head")

    # Replay checks
    replay_state = _as_text(replay.get("replay_state"))
    target_head = _as_text(replay.get("target_head"))
    replay_head = _as_text(replay.get("replay_head"))
    replay_receipt_path = _as_text(replay.get("replay_receipt_path"))
    is_current = _as_bool(replay.get("is_current_for_target"))

    if replay_state not in REPLAY_STATES:
        caps.add(CAP_REPLAY_STATE_AMBIGUOUS)
        notes.append("replay_state_unknown")

    if replay_state == "NONE":
        if replay_head or replay_receipt_path or is_current:
            caps.add(CAP_REPLAY_STATE_AMBIGUOUS)
            notes.append("replay_none_but_evidence_present")

    if replay_state in CURRENT_TARGET_REPLAY_STATES:
        if not replay_head or not target_head:
            caps.add(CAP_REPLAY_STATE_AMBIGUOUS)
            notes.append("current_target_state_missing_heads")
        if replay_head != target_head:
            caps.add(CAP_STALE_REPLAY_USED_AS_CURRENT)
            notes.append("current_target_state_head_mismatch")
        if not is_current:
            caps.add(CAP_STALE_REPLAY_USED_AS_CURRENT)
            notes.append("current_target_state_is_current_false")
        if not replay_receipt_path:
            caps.add(CAP_REPLAY_STATE_AMBIGUOUS)
            notes.append("current_target_state_missing_receipt_path")

    if replay_state == "STALE_REPLAY_ONLY":
        if not replay_head or not target_head:
            caps.add(CAP_REPLAY_STATE_AMBIGUOUS)
            notes.append("stale_state_missing_heads")
        if replay_head == target_head and replay_head:
            caps.add(CAP_STALE_REPLAY_USED_AS_CURRENT)
            notes.append("stale_state_but_heads_equal")
        if is_current:
            caps.add(CAP_STALE_REPLAY_USED_AS_CURRENT)
            notes.append("stale_state_marked_current")

    if replay_state == "PRIOR_REPLAY_EXISTS":
        if not replay_head:
            caps.add(CAP_REPLAY_STATE_AMBIGUOUS)
            notes.append("prior_replay_exists_missing_replay_head")

    clean_pass_allowed = _as_bool(receipt.get("clean_pass_allowed"))
    if clean_pass_allowed and caps:
        caps.add(CAP_FINALIZATION_SEMANTICS_CONTRADICTORY)
        notes.append("clean_pass_allowed_with_active_caps")

    if caps & BLOCKING_CAPS:
        verdict = "BLOCK"
    elif caps:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    return verdict, sorted(caps), notes


def evaluate_expected(payload: dict[str, Any], verdict: str, caps: list[str], notes: list[str]) -> FixtureResult:
    expected = payload.get("expected", {})
    expected_verdict = _as_text(expected.get("verdict")) or "PASS"
    must_include = [str(item) for item in expected.get("must_include_caps", [])]
    must_not_include = [str(item) for item in expected.get("must_not_include_caps", [])]

    cap_set = set(caps)
    missing = [cap for cap in must_include if cap not in cap_set]
    unexpected = [cap for cap in must_not_include if cap in cap_set]

    checks_passed = (verdict == expected_verdict) and not missing and not unexpected
    notes_out = list(notes)
    if verdict != expected_verdict:
        notes_out.append(f"expected_verdict_mismatch:{expected_verdict}->{verdict}")
    for cap in missing:
        notes_out.append(f"missing_expected_cap:{cap}")
    for cap in unexpected:
        notes_out.append(f"unexpected_cap_present:{cap}")

    return FixtureResult(
        fixture_id=_as_text(payload.get("fixture_id")) or "UNKNOWN_FIXTURE",
        expected_verdict=expected_verdict,
        actual_verdict=verdict,
        expected_caps=missing,
        unexpected_caps=unexpected,
        caps_triggered=caps,
        checks_passed=checks_passed,
        notes=notes_out,
    )


def run(fixtures_dir: Path) -> dict[str, Any]:
    fixture_paths = sorted(path for path in fixtures_dir.glob("*.json") if path.is_file())
    if not fixture_paths:
        raise RuntimeError(f"No fixture files found in {fixtures_dir}")

    results: list[FixtureResult] = []
    verdict_counts = {"PASS": 0, "PASS_WITH_WARNINGS": 0, "BLOCK": 0}

    for path in fixture_paths:
        payload = _load_json(path)
        verdict, caps, notes = evaluate_fixture(payload)
        result = evaluate_expected(payload, verdict, caps, notes)
        results.append(result)
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

    passed = sum(1 for item in results if item.checks_passed)
    failed = len(results) - passed

    return {
        "schema_id": "newgen_external_finalization_semantics_checker_report_v0_1",
        "fixtures_dir": str(fixtures_dir),
        "fixture_total": len(results),
        "fixture_checks_passed": passed,
        "fixture_checks_failed": failed,
        "verdict_counts": verdict_counts,
        "results": [
            {
                "fixture_id": item.fixture_id,
                "expected_verdict": item.expected_verdict,
                "actual_verdict": item.actual_verdict,
                "missing_expected_caps": item.expected_caps,
                "unexpected_caps": item.unexpected_caps,
                "caps_triggered": item.caps_triggered,
                "checks_passed": item.checks_passed,
                "notes": item.notes,
            }
            for item in results
        ],
        "overall_status": "PASS" if failed == 0 else "FAIL",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check external finalization semantics fixtures.")
    parser.add_argument("--fixture-dir", required=True, help="Directory containing fixture JSON files.")
    parser.add_argument("--report-json", help="Optional output path for JSON report.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run(Path(args.fixture_dir))

    if args.compact:
        out = json.dumps(report, ensure_ascii=False, separators=(",", ":"))
    else:
        out = json.dumps(report, ensure_ascii=False, indent=2)

    if args.report_json:
        path = Path(args.report_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out + "\n", encoding="utf-8")

    print(out)
    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
