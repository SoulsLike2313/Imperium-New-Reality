#!/usr/bin/env python3
"""Independent replay runner for REVIEW_TARGET_MANIFEST alignment."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-INDEPENDENT-REPLAY-AND-HEAD-CHAIN-RECONCILIATION-VM3-V0_1"
DEFAULT_REPORT_SUBDIR = (
    "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MATRIX-SPINE-INDEPENDENT-REPLAY-AND-HEAD-CHAIN-RECONCILIATION-VM3-V0_1"
)
FIXTURE_DIR = Path("IMPERIUM_NEW_GENERATION/MATRIX_SPINE/FIXTURES/REVIEW_TARGET_ALIGNMENT")

BLOCKING_CAPS = {
    "CAP_REVIEW_TARGET_CONFLICT",
    "CAP_REVIEW_TARGET_MANIFEST_MISSING",
    "CAP_IMPLEMENTATION_TRUTH_UNRESOLVED",
    "CAP_NO_INDEPENDENT_REPLAY",
    "CAP_HEAD_CHAIN_INCOMPLETE",
    "CAP_REVIEWERS_CAN_DIVERGE",
    "CAP_WARP_CLAIMED_WITHOUT_UNLOCK",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - defensive
        return None, str(exc)


def unique_caps(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def evaluate_manifest_payload(data: Any) -> tuple[list[str], list[str], list[str]]:
    caps: list[str] = []
    notes: list[str] = []
    replay_commands: list[str] = []

    if not isinstance(data, dict):
        return (
            ["CAP_REVIEW_TARGET_MANIFEST_MISSING", "CAP_HEAD_CHAIN_INCOMPLETE"],
            ["manifest root is not an object"],
            replay_commands,
        )

    if not is_nonempty_string(data.get("review_target_head")):
        caps.append("CAP_HEAD_CHAIN_INCOMPLETE")
        notes.append("review_target_head is missing or empty")

    if not is_nonempty_string(data.get("accepted_continuity_head")):
        caps.append("CAP_HEAD_CHAIN_INCOMPLETE")
        notes.append("accepted_continuity_head is missing or empty")

    head_chain = data.get("head_chain")
    if not isinstance(head_chain, dict):
        caps.append("CAP_HEAD_CHAIN_INCOMPLETE")
        notes.append("head_chain object is missing")
    else:
        required_head_chain_keys = [
            "base_head",
            "previous_closure_head",
            "accepted_continuity_head",
            "proof_receipt_head",
            "closure_bundle_head",
            "remote_head_after_push",
        ]
        missing_keys = [key for key in required_head_chain_keys if not is_nonempty_string(head_chain.get(key))]
        if missing_keys:
            caps.append("CAP_HEAD_CHAIN_INCOMPLETE")
            notes.append(f"head_chain missing keys: {', '.join(missing_keys)}")

    reviewer_targets = data.get("reviewer_targets")
    if not isinstance(reviewer_targets, dict):
        caps.append("CAP_REVIEW_TARGET_MANIFEST_MISSING")
        notes.append("reviewer_targets object is missing")
    else:
        inquisitor = reviewer_targets.get("inquisitor")
        speculum = reviewer_targets.get("speculum")
        inquisitor_head = inquisitor.get("target_head") if isinstance(inquisitor, dict) else None
        speculum_head = speculum.get("target_head") if isinstance(speculum, dict) else None
        target_head = data.get("review_target_head")

        if not is_nonempty_string(inquisitor_head) or not is_nonempty_string(speculum_head):
            caps.append("CAP_REVIEW_TARGET_MANIFEST_MISSING")
            notes.append("reviewer target head is missing for inquisitor or speculum")
        else:
            if inquisitor_head != speculum_head:
                caps.extend(["CAP_REVIEW_TARGET_CONFLICT", "CAP_REVIEWERS_CAN_DIVERGE"])
                notes.append("inquisitor and speculum target heads diverge")
            if is_nonempty_string(target_head) and (inquisitor_head != target_head or speculum_head != target_head):
                caps.extend(["CAP_REVIEW_TARGET_CONFLICT", "CAP_REVIEWERS_CAN_DIVERGE"])
                notes.append("review_target_head does not match reviewer target heads")

    implementation_status = data.get("implementation_truth_status")
    implementation_head = data.get("implementation_truth_head")
    if implementation_status != "RESOLVED":
        caps.append("CAP_IMPLEMENTATION_TRUTH_UNRESOLVED")
        notes.append("implementation_truth_status is not RESOLVED")
    elif not is_nonempty_string(implementation_head):
        caps.append("CAP_IMPLEMENTATION_TRUTH_UNRESOLVED")
        notes.append("implementation_truth_head is empty while status is RESOLVED")

    independent_replay = data.get("independent_replay")
    if isinstance(independent_replay, dict):
        commands = independent_replay.get("commands")
        if isinstance(commands, list):
            replay_commands = [item for item in commands if isinstance(item, str) and item.strip()]
    if not replay_commands:
        caps.append("CAP_NO_INDEPENDENT_REPLAY")
        notes.append("independent replay command list is empty")

    warp_runtime_claimed = data.get("warp_runtime_claimed") is True
    warp_unlocked = data.get("warp_unlocked") is True
    if warp_runtime_claimed and not warp_unlocked:
        caps.append("CAP_WARP_CLAIMED_WITHOUT_UNLOCK")
        notes.append("warp runtime is claimed while warp is still locked")

    return unique_caps(caps), notes, replay_commands


def evaluate_fixture(repo_root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    fixture_id = str(payload.get("fixture_id", "UNKNOWN_FIXTURE"))
    title = str(payload.get("title", fixture_id))
    mode = str(payload.get("mode", "inline_manifest"))
    expected_caps = payload.get("expected_caps")
    if not isinstance(expected_caps, list):
        expected_caps = []
    expected_caps = [item for item in expected_caps if isinstance(item, str)]
    expect_no_caps = payload.get("expect_no_caps") is True

    caps: list[str] = []
    notes: list[str] = []

    if mode == "inline_manifest":
        manifest_payload = payload.get("manifest")
        caps, notes, _ = evaluate_manifest_payload(manifest_payload)
    elif mode == "missing_manifest_path":
        rel_path = payload.get("manifest_path")
        manifest_path = repo_root / str(rel_path) if isinstance(rel_path, str) else None
        if manifest_path is None or manifest_path.exists():
            notes.append("fixture expected missing manifest path but file exists or path is invalid")
        else:
            caps.append("CAP_REVIEW_TARGET_MANIFEST_MISSING")
            notes.append("missing manifest path correctly detected")
    else:
        notes.append(f"unsupported fixture mode: {mode}")

    detected = True
    if expect_no_caps and caps:
        detected = False
    if expected_caps and any(cap not in caps for cap in expected_caps):
        detected = False

    return {
        "fixture_id": fixture_id,
        "title": title,
        "mode": mode,
        "expected_caps": expected_caps,
        "expect_no_caps": expect_no_caps,
        "caps_triggered": unique_caps(caps),
        "detected": detected,
        "notes": notes,
    }


def run_commands(repo_root: Path, commands: list[str]) -> tuple[list[dict[str, Any]], bool]:
    results: list[dict[str, Any]] = []
    all_ok = True
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            shell=True,
            text=True,
            capture_output=True,
        )
        if completed.returncode != 0:
            all_ok = False
        results.append(
            {
                "command": command,
                "returncode": completed.returncode,
                "stdout_excerpt": completed.stdout.strip()[-1200:],
                "stderr_excerpt": completed.stderr.strip()[-1200:],
            }
        )
    return results, all_ok


def build_fixture_report(
    *,
    task_id: str,
    timestamp: str,
    fixture_results: list[dict[str, Any]],
) -> str:
    lines = [
        f"# Reviewer Alignment Fixture Report — {task_id}",
        "",
        f"Timestamp (UTC): {timestamp}",
        "",
        "## Summary",
        f"- Fixtures checked: {len(fixture_results)}",
        f"- All expected detections: {'true' if all(item.get('detected') is True for item in fixture_results) else 'false'}",
        "",
        "## Results",
    ]
    for item in fixture_results:
        lines.append(
            "- "
            + f"{item['fixture_id']} {item['title']}: "
            + ("detected" if item.get("detected") else "NOT detected")
        )
        caps = item.get("caps_triggered", [])
        lines.append(f"  - caps_triggered: {', '.join(caps) if caps else 'none'}")
        expected = item.get("expected_caps", [])
        lines.append(f"  - expected_caps: {', '.join(expected) if expected else 'none'}")
        notes = item.get("notes", [])
        if notes:
            lines.append(f"  - notes: {' | '.join(str(note) for note in notes)}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run independent replay and reviewer-alignment checks.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--report-dir", default="")
    parser.add_argument("--manifest-path", default="")
    parser.add_argument("--skip-fixtures", action="store_true")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else script_path.parents[3]
    report_dir = Path(args.report_dir).resolve() if args.report_dir else (repo_root / DEFAULT_REPORT_SUBDIR)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = Path(args.manifest_path).resolve() if args.manifest_path else (report_dir / "REVIEW_TARGET_MANIFEST.json")
    caps: list[str] = []
    manifest_notes: list[str] = []
    replay_commands: list[str] = []

    manifest_loaded = False
    if not manifest_path.exists():
        caps.extend(["CAP_REVIEW_TARGET_MANIFEST_MISSING", "CAP_HEAD_CHAIN_INCOMPLETE", "CAP_NO_INDEPENDENT_REPLAY"])
        manifest_notes.append("REVIEW_TARGET_MANIFEST.json does not exist at requested path")
    else:
        manifest_data, manifest_error = load_json(manifest_path)
        if manifest_error is not None:
            caps.extend(["CAP_REVIEW_TARGET_MANIFEST_MISSING", "CAP_HEAD_CHAIN_INCOMPLETE"])
            manifest_notes.append(f"manifest parse error: {manifest_error}")
        else:
            manifest_loaded = True
            manifest_caps, notes, commands = evaluate_manifest_payload(manifest_data)
            caps.extend(manifest_caps)
            manifest_notes.extend(notes)
            replay_commands = commands

    command_results: list[dict[str, Any]] = []
    replay_passed = False
    if replay_commands:
        command_results, replay_passed = run_commands(repo_root, replay_commands)
        if not replay_passed:
            caps.append("CAP_NO_INDEPENDENT_REPLAY")
    else:
        replay_passed = False
        caps.append("CAP_NO_INDEPENDENT_REPLAY")

    fixture_results: list[dict[str, Any]] = []
    fixture_report_path = report_dir / "reviewer_alignment_fixture_report.md"
    if not args.skip_fixtures:
        fixture_root = repo_root / FIXTURE_DIR
        fixture_files = sorted(fixture_root.glob("*.json"))
        for fixture_file in fixture_files:
            payload, error = load_json(fixture_file)
            if error is not None or not isinstance(payload, dict):
                fixture_results.append(
                    {
                        "fixture_id": fixture_file.stem,
                        "title": fixture_file.name,
                        "mode": "parse_error",
                        "expected_caps": [],
                        "expect_no_caps": False,
                        "caps_triggered": [],
                        "detected": False,
                        "notes": [f"parse error: {error}"],
                    }
                )
                continue
            fixture_results.append(evaluate_fixture(repo_root, payload))

        fixture_report = build_fixture_report(
            task_id=args.task_id,
            timestamp=utc_now(),
            fixture_results=fixture_results,
        )
        fixture_report_path.write_text(fixture_report, encoding="utf-8")
    else:
        fixture_report_path.write_text(
            "# Reviewer Alignment Fixture Report\n\n- Fixture run skipped by --skip-fixtures.\n",
            encoding="utf-8",
        )

    if not all(item.get("detected") is True for item in fixture_results):
        caps.append("CAP_REVIEWERS_CAN_DIVERGE")

    caps = unique_caps(caps)
    blocking_caps_present = [cap for cap in caps if cap in BLOCKING_CAPS]
    clean_pass_allowed = replay_passed and not blocking_caps_present

    if "CAP_REVIEW_TARGET_MANIFEST_MISSING" in caps:
        verdict = "BLOCK"
    elif clean_pass_allowed:
        verdict = "PASS"
    else:
        verdict = "PASS_WITH_WARNINGS"

    receipt = {
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "manifest_path": str(manifest_path),
        "manifest_loaded": manifest_loaded,
        "replay_runner": "SEPARATE_REPLAY_RUNNER",
        "replay_commands": replay_commands,
        "replay_commands_executed": command_results,
        "replay_passed": replay_passed,
        "caps_triggered": caps,
        "blocking_caps_present": blocking_caps_present,
        "clean_pass_allowed": clean_pass_allowed,
        "verdict": verdict,
        "manifest_notes": manifest_notes,
        "reviewer_alignment_fixture_report_path": str(fixture_report_path),
        "fixtures_all_detected": all(item.get("detected") is True for item in fixture_results) if fixture_results else None,
    }

    receipt_path = report_dir / "independent_replay_receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    print(f"[review-target-alignment] report_dir={report_dir}")
    print(f"[review-target-alignment] verdict={verdict}")
    print(f"[review-target-alignment] clean_pass_allowed={clean_pass_allowed}")
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
