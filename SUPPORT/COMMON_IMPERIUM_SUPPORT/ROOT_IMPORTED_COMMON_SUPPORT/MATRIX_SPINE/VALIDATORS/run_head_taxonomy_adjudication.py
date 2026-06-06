#!/usr/bin/env python3
"""Head taxonomy and combined review adjudication checker for Matrix Spine."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-NEWGEN-MATRIX-SPINE-HEAD-TAXONOMY-AND-COMBINED-REVIEW-ADJUDICATION-VM3-V0_1"
DEFAULT_REPORT_SUBDIR = (
    "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/"
    "TASK-NEWGEN-MATRIX-SPINE-HEAD-TAXONOMY-AND-COMBINED-REVIEW-ADJUDICATION-VM3-V0_1"
)
FIXTURE_DIR = Path("IMPERIUM_NEW_GENERATION/MATRIX_SPINE/FIXTURES/HEAD_TAXONOMY_ADJUDICATION")

BLOCKING_CAPS = {
    "CAP_HEAD_TAXONOMY_MANIFEST_MISSING",
    "CAP_COMBINED_REVIEW_ADJUDICATION_MISSING",
    "CAP_REVIEW_TARGET_NOT_SINGLE",
    "CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH",
    "CAP_DECLARED_TARGET_UNFETCHABLE",
    "CAP_REVIEWERS_USED_DIFFERENT_HEAD_TAXONOMY",
    "CAP_ARTIFACT_BUNDLE_HEAD_MISSING",
    "CAP_WARP_CLAIMED_WITHOUT_UNLOCK",
}

HEAD_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_single_head_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    if any(sep in text for sep in [",", "\n", "\t", ";"]):
        return False
    if " " in text:
        return False
    return True


def is_hex_head(value: Any) -> bool:
    return is_single_head_value(value) and bool(HEAD_PATTERN.fullmatch(str(value).strip().lower()))


def unique_ordered(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def load_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - defensive
        return None, str(exc)


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


def normalize_replay_commands(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    commands: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            commands.append(item.strip())
    return commands


def evaluate_payload(
    payload: dict[str, Any],
    *,
    repo_root: Path,
    execute_commands: bool,
) -> tuple[list[str], list[str], list[str], list[dict[str, Any]], bool]:
    caps: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    taxonomy = payload.get("head_taxonomy_manifest")
    review_manifest = payload.get("review_target_manifest")
    combined = payload.get("combined_review_adjudication_receipt")

    taxonomy_path = payload.get("head_taxonomy_manifest_path")
    if not isinstance(taxonomy, dict):
        caps.append("CAP_HEAD_TAXONOMY_MANIFEST_MISSING")
        notes.append("head_taxonomy_manifest is missing or not an object")
    else:
        artifact_head = taxonomy.get("artifact_bundle_head")
        if not is_nonempty_string(artifact_head):
            caps.append("CAP_ARTIFACT_BUNDLE_HEAD_MISSING")
            notes.append("artifact_bundle_head is empty")
        elif not is_hex_head(artifact_head):
            caps.append("CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH")
            notes.append("artifact_bundle_head is not a full 40-char hash")

        taxonomy_review_target = taxonomy.get("review_target_head")
        if not is_single_head_value(taxonomy_review_target):
            caps.append("CAP_REVIEW_TARGET_NOT_SINGLE")
            notes.append("head taxonomy review_target_head is missing or non-single")
        elif not is_hex_head(taxonomy_review_target):
            caps.append("CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH")
            notes.append("head taxonomy review_target_head is not a full 40-char hash")

        fallback_head = taxonomy.get("fallback_review_head")
        if is_nonempty_string(fallback_head):
            if not is_hex_head(fallback_head):
                caps.append("CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH")
                notes.append("fallback_review_head is not a full 40-char hash")
            if not is_nonempty_string(taxonomy.get("fallback_warning")):
                caps.append("CAP_REVIEW_TARGET_NOT_SINGLE")
                notes.append("fallback_review_head is present without explicit warning")

        warp_runtime_claimed = payload.get("warp_runtime_claimed") is True or taxonomy.get("warp_runtime_claimed") is True
        warp_unlocked = payload.get("warp_unlocked") is True or taxonomy.get("warp_unlocked") is True
        if warp_runtime_claimed and not warp_unlocked:
            caps.append("CAP_WARP_CLAIMED_WITHOUT_UNLOCK")
            notes.append("warp runtime is claimed while warp is locked")

    if not isinstance(review_manifest, dict):
        notes.append("review_target_manifest is missing or not an object")
    else:
        review_head = review_manifest.get("review_target_head")
        if not is_single_head_value(review_head):
            caps.append("CAP_REVIEW_TARGET_NOT_SINGLE")
            notes.append("review_target_manifest.review_target_head is missing or non-single")
        elif not is_hex_head(review_head):
            caps.append("CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH")
            notes.append("review_target_manifest.review_target_head is not a full 40-char hash")

        review_manifest_taxonomy_path = review_manifest.get("head_taxonomy_manifest_path")
        if is_nonempty_string(taxonomy_path) and is_nonempty_string(review_manifest_taxonomy_path):
            if str(review_manifest_taxonomy_path) != str(taxonomy_path):
                caps.append("CAP_REVIEWERS_USED_DIFFERENT_HEAD_TAXONOMY")
                notes.append("review_target_manifest points to different taxonomy path")

        reviewer_paths = review_manifest.get("reviewer_head_taxonomy_paths")
        if isinstance(reviewer_paths, dict):
            inquisitor_path = reviewer_paths.get("inquisitor")
            speculum_path = reviewer_paths.get("speculum")
            if is_nonempty_string(inquisitor_path) and is_nonempty_string(speculum_path):
                if inquisitor_path != speculum_path:
                    caps.append("CAP_REVIEWERS_USED_DIFFERENT_HEAD_TAXONOMY")
                    notes.append("inquisitor and speculum taxonomy paths diverge")

    reviewer_taxonomy_paths = payload.get("reviewer_head_taxonomy_paths")
    if isinstance(reviewer_taxonomy_paths, dict):
        inquisitor = reviewer_taxonomy_paths.get("inquisitor")
        speculum = reviewer_taxonomy_paths.get("speculum")
        if is_nonempty_string(inquisitor) and is_nonempty_string(speculum) and inquisitor != speculum:
            caps.append("CAP_REVIEWERS_USED_DIFFERENT_HEAD_TAXONOMY")
            notes.append("reviewer_head_taxonomy_paths diverge")

    declared_head = payload.get("declared_target_head")
    if not is_nonempty_string(declared_head):
        if isinstance(review_manifest, dict) and is_nonempty_string(review_manifest.get("review_target_head")):
            declared_head = review_manifest.get("review_target_head")
        elif isinstance(taxonomy, dict):
            declared_head = taxonomy.get("review_target_head")

    if is_nonempty_string(declared_head):
        if not is_hex_head(declared_head):
            caps.append("CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH")
            notes.append("declared_target_head is not a full 40-char hash")
        fetchable_heads = payload.get("fetchable_heads")
        if isinstance(fetchable_heads, list) and all(isinstance(item, str) for item in fetchable_heads):
            if declared_head not in fetchable_heads:
                caps.append("CAP_DECLARED_TARGET_UNFETCHABLE")
                notes.append("declared target head is not in fetchable_heads set")

    taxonomy_review_target_head = taxonomy.get("review_target_head") if isinstance(taxonomy, dict) else None
    manifest_review_target_head = review_manifest.get("review_target_head") if isinstance(review_manifest, dict) else None
    if is_nonempty_string(taxonomy_review_target_head) and is_nonempty_string(manifest_review_target_head):
        if taxonomy_review_target_head != manifest_review_target_head:
            caps.append("CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH")
            notes.append("taxonomy and review manifest review_target_head mismatch")

    if not isinstance(combined, dict):
        caps.append("CAP_COMBINED_REVIEW_ADJUDICATION_MISSING")
        notes.append("combined_review_adjudication_receipt is missing or not an object")
    else:
        combined_review_head = combined.get("review_target_head")
        if not is_single_head_value(combined_review_head):
            caps.append("CAP_REVIEW_TARGET_NOT_SINGLE")
            notes.append("combined review receipt review_target_head is missing or non-single")
        elif not is_hex_head(combined_review_head):
            caps.append("CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH")
            notes.append("combined review receipt review_target_head is not a full 40-char hash")

        if is_nonempty_string(manifest_review_target_head) and is_nonempty_string(combined_review_head):
            if manifest_review_target_head != combined_review_head:
                caps.append("CAP_REVIEW_TARGET_TYPO_OR_HASH_MISMATCH")
                notes.append("combined review receipt uses different review target head")

        if combined.get("final_merged_verdict") == "PENDING":
            warnings.append("combined review merged verdict is still PENDING")

    replay_commands: list[str] = []
    if isinstance(review_manifest, dict):
        independent_replay = review_manifest.get("independent_replay")
        if isinstance(independent_replay, dict):
            replay_commands = normalize_replay_commands(independent_replay.get("commands"))
    if not replay_commands and isinstance(taxonomy, dict):
        replay_commands = normalize_replay_commands(taxonomy.get("replay_commands"))

    if not replay_commands and is_hex_head(declared_head):
        replay_commands = [f"git cat-file -e {declared_head}^{{commit}}"]

    command_results: list[dict[str, Any]] = []
    replay_passed = False
    if execute_commands and replay_commands:
        command_results, replay_passed = run_commands(repo_root, replay_commands)
        if not replay_passed:
            caps.append("CAP_DECLARED_TARGET_UNFETCHABLE")
            notes.append("at least one replay command failed")
    elif replay_commands:
        replay_passed = True

    return unique_ordered(caps), unique_ordered(warnings), notes, command_results, replay_passed


def evaluate_fixture(repo_root: Path, fixture: dict[str, Any]) -> dict[str, Any]:
    fixture_id = str(fixture.get("fixture_id", "UNKNOWN"))
    title = str(fixture.get("title", fixture_id))
    mode = str(fixture.get("mode", "inline_payload"))
    expected_caps = fixture.get("expected_caps")
    if not isinstance(expected_caps, list):
        expected_caps = []
    expected_caps = [item for item in expected_caps if isinstance(item, str)]
    expect_no_caps = fixture.get("expect_no_caps") is True

    payload = fixture.get("payload") if isinstance(fixture.get("payload"), dict) else {}
    if mode == "missing_head_taxonomy_manifest":
        payload = dict(payload)
        payload["head_taxonomy_manifest"] = None
    elif mode == "missing_combined_review_adjudication":
        payload = dict(payload)
        payload["combined_review_adjudication_receipt"] = None

    caps, warnings, notes, _, _ = evaluate_payload(payload, repo_root=repo_root, execute_commands=False)

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
        "caps_triggered": caps,
        "warnings": warnings,
        "detected": detected,
        "notes": notes,
    }


def build_fixture_report(task_id: str, fixture_results: list[dict[str, Any]]) -> str:
    has_failure_fixture = any(item.get("expected_caps") for item in fixture_results)
    has_pass_fixture = any(item.get("expect_no_caps") is True for item in fixture_results)
    has_detected_failure = any(item.get("expected_caps") and item.get("detected") is True for item in fixture_results)
    has_detected_pass = any(item.get("expect_no_caps") is True and item.get("detected") is True for item in fixture_results)

    lines = [
        f"# Taxonomy Fixture Report — {task_id}",
        "",
        f"Timestamp (UTC): {utc_now()}",
        "",
        "## Summary",
        f"- Fixtures checked: {len(fixture_results)}",
        f"- Contains failure fixtures: {'true' if has_failure_fixture else 'false'}",
        f"- Contains pass fixtures: {'true' if has_pass_fixture else 'false'}",
        f"- Failure fixture detected by checker: {'true' if has_detected_failure else 'false'}",
        f"- Pass fixture detected by checker: {'true' if has_detected_pass else 'false'}",
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
        warnings = item.get("warnings", [])
        lines.append(f"  - caps_triggered: {', '.join(caps) if caps else 'none'}")
        lines.append(f"  - warnings: {', '.join(warnings) if warnings else 'none'}")
        expected = item.get("expected_caps", [])
        lines.append(f"  - expected_caps: {', '.join(expected) if expected else 'none'}")
        notes = item.get("notes", [])
        if notes:
            lines.append(f"  - notes: {' | '.join(str(note) for note in notes)}")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run head taxonomy and combined review adjudication checks.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--report-dir", default="")
    parser.add_argument("--head-taxonomy-path", default="")
    parser.add_argument("--review-target-path", default="")
    parser.add_argument("--combined-review-path", default="")
    parser.add_argument("--skip-fixtures", action="store_true")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else script_path.parents[3]
    report_dir = Path(args.report_dir).resolve() if args.report_dir else (repo_root / DEFAULT_REPORT_SUBDIR)
    report_dir.mkdir(parents=True, exist_ok=True)

    taxonomy_path = Path(args.head_taxonomy_path).resolve() if args.head_taxonomy_path else (report_dir / "HEAD_TAXONOMY_MANIFEST.json")
    review_target_path = Path(args.review_target_path).resolve() if args.review_target_path else (report_dir / "REVIEW_TARGET_MANIFEST.json")
    combined_review_path = Path(args.combined_review_path).resolve() if args.combined_review_path else (report_dir / "COMBINED_REVIEW_ADJUDICATION_RECEIPT.json")

    taxonomy_data: Any | None = None
    review_target_data: Any | None = None
    combined_review_data: Any | None = None
    loading_notes: list[str] = []

    if taxonomy_path.exists():
        taxonomy_data, err = load_json(taxonomy_path)
        if err is not None:
            loading_notes.append(f"taxonomy parse error: {err}")
            taxonomy_data = None
    else:
        loading_notes.append("HEAD_TAXONOMY_MANIFEST.json does not exist at requested path")

    if review_target_path.exists():
        review_target_data, err = load_json(review_target_path)
        if err is not None:
            loading_notes.append(f"review target parse error: {err}")
            review_target_data = None
    else:
        loading_notes.append("REVIEW_TARGET_MANIFEST.json does not exist at requested path")

    if combined_review_path.exists():
        combined_review_data, err = load_json(combined_review_path)
        if err is not None:
            loading_notes.append(f"combined review parse error: {err}")
            combined_review_data = None
    else:
        loading_notes.append("COMBINED_REVIEW_ADJUDICATION_RECEIPT.json does not exist at requested path")

    payload: dict[str, Any] = {
        "head_taxonomy_manifest": taxonomy_data,
        "review_target_manifest": review_target_data,
        "combined_review_adjudication_receipt": combined_review_data,
        "head_taxonomy_manifest_path": str(taxonomy_path),
        "declared_target_head": review_target_data.get("review_target_head") if isinstance(review_target_data, dict) else None,
        "fetchable_heads": taxonomy_data.get("known_fetchable_heads") if isinstance(taxonomy_data, dict) else None,
        "warp_runtime_claimed": taxonomy_data.get("warp_runtime_claimed") if isinstance(taxonomy_data, dict) else False,
        "warp_unlocked": taxonomy_data.get("warp_unlocked") if isinstance(taxonomy_data, dict) else False,
    }

    caps, warnings, notes, command_results, replay_passed = evaluate_payload(
        payload,
        repo_root=repo_root,
        execute_commands=True,
    )
    notes = loading_notes + notes

    fixture_results: list[dict[str, Any]] = []
    fixture_report_path = report_dir / "taxonomy_fixture_report.md"
    if not args.skip_fixtures:
        fixture_root = repo_root / FIXTURE_DIR
        fixture_files = sorted(fixture_root.glob("*.json"))
        for fixture_file in fixture_files:
            fixture_payload, error = load_json(fixture_file)
            if error is not None or not isinstance(fixture_payload, dict):
                fixture_results.append(
                    {
                        "fixture_id": fixture_file.stem,
                        "title": fixture_file.name,
                        "mode": "parse_error",
                        "expected_caps": [],
                        "expect_no_caps": False,
                        "caps_triggered": [],
                        "warnings": [],
                        "detected": False,
                        "notes": [f"parse error: {error}"],
                    }
                )
                continue
            fixture_results.append(evaluate_fixture(repo_root, fixture_payload))

        fixture_report_path.write_text(
            build_fixture_report(args.task_id, fixture_results),
            encoding="utf-8",
        )
    else:
        fixture_report_path.write_text(
            "# Taxonomy Fixture Report\n\n- Fixture run skipped by --skip-fixtures.\n",
            encoding="utf-8",
        )

    has_detected_failure = any(item.get("expected_caps") and item.get("detected") is True for item in fixture_results)
    has_detected_pass = any(item.get("expect_no_caps") is True and item.get("detected") is True for item in fixture_results)
    if fixture_results and not has_detected_failure:
        warnings.append("checker did not prove a failure fixture detection")
    if fixture_results and not has_detected_pass:
        warnings.append("checker did not prove a pass fixture detection")

    blocking_caps_present = [cap for cap in caps if cap in BLOCKING_CAPS]
    clean_pass_allowed = not blocking_caps_present and not warnings

    if any(cap in caps for cap in {"CAP_HEAD_TAXONOMY_MANIFEST_MISSING", "CAP_COMBINED_REVIEW_ADJUDICATION_MISSING"}):
        verdict = "BLOCK"
    elif blocking_caps_present:
        verdict = "PASS_WITH_WARNINGS"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    receipt = {
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "head_taxonomy_manifest_path": str(taxonomy_path),
        "review_target_manifest_path": str(review_target_path),
        "combined_review_adjudication_receipt_path": str(combined_review_path),
        "replay_commands_executed": command_results,
        "replay_passed": replay_passed,
        "caps_triggered": caps,
        "blocking_caps_present": blocking_caps_present,
        "warnings": unique_ordered(warnings),
        "clean_pass_allowed": clean_pass_allowed,
        "verdict": verdict,
        "notes": notes,
        "taxonomy_fixture_report_path": str(fixture_report_path),
        "fixtures_all_detected": all(item.get("detected") is True for item in fixture_results) if fixture_results else None,
        "failure_fixture_proved": has_detected_failure if fixture_results else None,
        "pass_fixture_proved": has_detected_pass if fixture_results else None,
    }

    receipt_path = report_dir / "head_taxonomy_adjudication_receipt.json"
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    print(f"[head-taxonomy-adjudication] report_dir={report_dir}")
    print(f"[head-taxonomy-adjudication] verdict={verdict}")
    print(f"[head-taxonomy-adjudication] clean_pass_allowed={clean_pass_allowed}")
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
