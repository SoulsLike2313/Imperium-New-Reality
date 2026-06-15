#!/usr/bin/env python3
"""Compute 5-scale efficiency delta receipt for Matrix Spine runtime corridor task."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-RECEIPT-HEAD-CONSISTENCY-AND-INDEPENDENT-REPLAY-GATE-VM3-V0_1"
BASE_HEAD_DEFAULT = "c10f2b1c46d19e6a7614e25c4eff57b46b8baef5"
IMPLEMENTATION_TRUTH_HEAD_DEFAULT = "3aa07798217fff0f594214d203e1783307a03a5e"
SYNTHETIC_OVERALL_DELTA_CAP = 13

BASELINE = {
    "mechanicus": 64,
    "inquisition": 41,
    "officio": 44,
    "administratum": 46,
    "overall": 69,
}

SEVERE_RED_TEAM_CAPS = {
    "CAP_UNTYPED_RUNTIME_CLAIM",
    "CAP_SYNTHETIC_CLAIMED_AS_REAL",
    "CAP_WARP_CLAIMED_WITHOUT_UNLOCK",
    "CAP_NO_FINAL_CLOSURE_VERIFIER",
    "CAP_NO_NEXT_PIPELINE_HANDOFF",
    "CAP_RUNTIME_OUTPUT_UNCLASSIFIED",
    "CAP_RUNTIME_EXCLUDED_OUTPUT_WITHOUT_HASH",
    "CAP_HEADS_MIXED_OR_AMBIGUOUS",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - defensive
        return None, str(exc)


def clamp(value: int) -> int:
    return max(0, min(100, value))


def collect_cap_codes(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return []

    caps: set[str] = set()
    for key in ["cap_codes_detected", "caps_triggered", "known_caps_or_warnings", "downgrade_rules_applied"]:
        value = payload.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.startswith("CAP_"):
                    caps.add(item)
    return sorted(caps)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute efficiency delta receipt.")
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

    validator_summary_path = output_dir / "matrix_validator_run" / "matrix_spine_validation_summary.json"
    corridor_receipt_path = output_dir / "synthetic_corridor_receipt.json"
    red_team_path = output_dir / "hard_red_team_verdict.json"
    final_closure_path = output_dir / "final_closure_verifier_receipt.json"

    summary, summary_error = load_json(validator_summary_path)
    corridor, corridor_error = load_json(corridor_receipt_path)

    if summary_error is not None or not isinstance(summary, dict):
        print(f"[efficiency-delta] unable to read validator summary: {summary_error}", file=sys.stderr)
        return 1
    if corridor_error is not None or not isinstance(corridor, dict):
        print(f"[efficiency-delta] unable to read corridor receipt: {corridor_error}", file=sys.stderr)
        return 1

    red_team, red_team_error = load_json(red_team_path)
    final_closure, final_closure_error = load_json(final_closure_path)

    issue_counts = summary.get("issue_counts", {})
    fail_count = int(issue_counts.get("FAIL", 0)) if isinstance(issue_counts, dict) else 0
    warn_count = int(issue_counts.get("WARN", 0)) if isinstance(issue_counts, dict) else 0

    negative_results = summary.get("negative_fixture_results", [])
    negative_count = len(negative_results) if isinstance(negative_results, list) else 0
    negative_detected = 0
    if isinstance(negative_results, list):
        negative_detected = sum(1 for item in negative_results if isinstance(item, dict) and item.get("detected") is True)

    corridor_steps = corridor.get("steps", [])
    passed_steps = 0
    if isinstance(corridor_steps, list):
        passed_steps = sum(1 for item in corridor_steps if isinstance(item, dict) and item.get("status") == "PASS")

    summary_caps = collect_cap_codes(summary)
    red_team_caps = collect_cap_codes(red_team)
    closure_caps = collect_cap_codes(final_closure)
    combined_caps: set[str] = set(summary_caps) | set(red_team_caps) | set(closure_caps)

    red_team_missing = red_team_error is not None or not isinstance(red_team, dict)
    if red_team_missing:
        combined_caps.add("CAP_REDTEAM_CAPS_NOT_APPLIED_TO_SCORE")

    severe_cap_penalty = sum(1 for cap in combined_caps if cap in SEVERE_RED_TEAM_CAPS)
    if red_team_missing:
        severe_cap_penalty += 1

    mechanicus_after = clamp(
        BASELINE["mechanicus"]
        + 8
        + min(12, negative_detected)
        - (3 * fail_count)
        - warn_count
        - (2 * severe_cap_penalty)
    )
    inquisition_after = clamp(
        BASELINE["inquisition"]
        + min(15, negative_detected)
        + (6 if fail_count == 0 else 0)
        - (3 * severe_cap_penalty)
    )
    officio_after = clamp(
        BASELINE["officio"]
        + (8 if passed_steps >= 1 else 0)
        + (3 if negative_detected >= 12 else 0)
        - (2 * severe_cap_penalty)
    )
    administratum_after = clamp(
        BASELINE["administratum"]
        + (10 if passed_steps >= 5 else 0)
        + (4 if corridor.get("overall") == "PASS" else 0)
        - (2 * severe_cap_penalty)
    )

    overall_after_raw = clamp(
        BASELINE["overall"]
        + min(20, (2 * passed_steps) + (negative_detected // 2))
        - (4 * fail_count)
        - (2 * warn_count)
        - (6 * severe_cap_penalty)
    )

    replay_status = "NONE"
    if isinstance(final_closure, dict):
        replay_status_value = final_closure.get("independent_replay_status")
        if isinstance(replay_status_value, str) and replay_status_value.strip():
            replay_status = replay_status_value

    corridor_type = corridor.get("corridor_type")
    synthetic_mode = corridor_type != "real_runtime_corridor"

    synthetic_score_cap_applied: int | None = None
    if synthetic_mode:
        max_overall_after = BASELINE["overall"] + SYNTHETIC_OVERALL_DELTA_CAP
        if overall_after_raw > max_overall_after:
            overall_after = max_overall_after
            synthetic_score_cap_applied = SYNTHETIC_OVERALL_DELTA_CAP
        else:
            overall_after = overall_after_raw
    else:
        overall_after = overall_after_raw

    independent_replay_cap_applied: str | None = None
    if replay_status == "NONE":
        combined_caps.add("CAP_NO_INDEPENDENT_REPLAY")
        independent_replay_cap_applied = "CAP_NO_INDEPENDENT_REPLAY"

    after = {
        "mechanicus": mechanicus_after,
        "inquisition": inquisition_after,
        "officio": officio_after,
        "administratum": administratum_after,
        "overall": overall_after,
    }

    delta = {key: after[key] - BASELINE[key] for key in BASELINE}
    positive_delta = all(value > 0 for value in delta.values())
    if not positive_delta:
        combined_caps.add("CAP_NO_EFFICIENCY_DELTA")

    final_closure_verdict = ""
    if isinstance(final_closure, dict):
        verdict_value = final_closure.get("verdict")
        if isinstance(verdict_value, str):
            final_closure_verdict = verdict_value
    if replay_status == "NONE" and final_closure_verdict == "PASS":
        combined_caps.add("CAP_NO_INDEPENDENT_REPLAY")

    if any(cap in combined_caps for cap in {"CAP_WARP_CLAIMED_WITHOUT_UNLOCK", "CAP_SYNTHETIC_CLAIMED_AS_REAL"}):
        verdict = "BLOCK"
    elif "CAP_NO_EFFICIENCY_DELTA" in combined_caps:
        verdict = "WARN"
    elif "CAP_NO_INDEPENDENT_REPLAY" in combined_caps or synthetic_mode:
        verdict = "PASS_WITH_WARNINGS"
    elif positive_delta:
        verdict = "PASS"
    else:
        verdict = "WARN"

    base_head = BASE_HEAD_DEFAULT
    closure_bundle_head = ""
    if isinstance(final_closure, dict):
        if isinstance(final_closure.get("base_head"), str) and final_closure.get("base_head", "").strip():
            base_head = str(final_closure["base_head"])
        closure_bundle_value = final_closure.get("closure_bundle_head")
        if isinstance(closure_bundle_value, str):
            closure_bundle_head = closure_bundle_value

    receipt = {
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "base_head": base_head,
        "implementation_truth_head": IMPLEMENTATION_TRUTH_HEAD_DEFAULT,
        "closure_bundle_head": closure_bundle_head,
        "independent_replay_status": replay_status,
        "scales": {
            "mechanicus": {
                "before": BASELINE["mechanicus"],
                "after": mechanicus_after,
                "delta": delta["mechanicus"],
                "evidence": [str(validator_summary_path)],
            },
            "inquisition": {
                "before": BASELINE["inquisition"],
                "after": inquisition_after,
                "delta": delta["inquisition"],
                "evidence": [str(validator_summary_path)],
            },
            "officio": {
                "before": BASELINE["officio"],
                "after": officio_after,
                "delta": delta["officio"],
                "evidence": [str(corridor_receipt_path)],
            },
            "administratum": {
                "before": BASELINE["administratum"],
                "after": administratum_after,
                "delta": delta["administratum"],
                "evidence": [str(corridor_receipt_path)],
            },
            "overall": {
                "before": BASELINE["overall"],
                "after": overall_after,
                "delta": delta["overall"],
                "evidence": [str(validator_summary_path), str(corridor_receipt_path)],
            },
        },
        "baseline": BASELINE,
        "after": after,
        "delta": delta,
        "red_team_caps_consumed": sorted(combined_caps),
        "synthetic_score_cap_applied": synthetic_score_cap_applied,
        "independent_replay_cap_applied": independent_replay_cap_applied,
        "caps_triggered": sorted(combined_caps),
        "final_verdict": verdict,
        "verdict": verdict,
        "evidence": [
            {
                "path": str(validator_summary_path),
                "negative_fixture_total": negative_count,
                "negative_fixture_detected": negative_detected,
                "fail_count": fail_count,
                "warn_count": warn_count,
            },
            {
                "path": str(corridor_receipt_path),
                "passed_steps": passed_steps,
                "overall": corridor.get("overall"),
                "corridor_type": corridor_type,
            },
            {
                "path": str(red_team_path),
                "read_ok": not red_team_missing,
                "caps_detected": red_team_caps,
                "error": red_team_error if red_team_missing else "",
            },
            {
                "path": str(final_closure_path),
                "read_ok": final_closure_error is None and isinstance(final_closure, dict),
                "caps_detected": closure_caps,
                "error": final_closure_error if final_closure_error is not None else "",
            },
        ],
        "notes": [
            "Five-scale score is deterministic and stdlib-only.",
            "Synthetic corridor overall delta is capped at +13 until real runtime proof.",
            "Clean PASS is blocked when independent replay status is NONE.",
            "Red-team caps are consumed before verdict emission.",
        ],
    }

    output_path = output_dir / "efficiency_delta_receipt.json"
    output_path.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    print(f"[efficiency-delta] output={output_path}")
    print(
        "[efficiency-delta] "
        + f"overall_before={BASELINE['overall']} "
        + f"overall_after={overall_after} "
        + f"delta={delta['overall']} "
        + f"verdict={verdict}"
    )
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    sys.exit(main())
