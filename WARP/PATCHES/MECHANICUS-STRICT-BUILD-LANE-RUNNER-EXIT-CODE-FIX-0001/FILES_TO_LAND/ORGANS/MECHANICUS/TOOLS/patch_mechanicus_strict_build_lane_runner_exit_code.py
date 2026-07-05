#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

TOOL_ID = "mechanicus_strict_build_lane_runner_exit_code_patcher.v0_1"

RUNNER = Path("ORGANS/MECHANICUS/TOOLS/run_mechanicus_strict_build_lane.py")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXIT_CODE_PATCH_REPORT_V0_1.json")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    path = repo / RUNNER
    errors = []
    warnings = []
    replacements = []

    if not path.is_file():
        errors.append(f"runner missing: {RUNNER.as_posix()}")
        write_json(repo / REPORT, {"tool_id": TOOL_ID, "verdict": "FAIL", "errors": errors, "warnings": warnings})
        print(json.dumps({"tool_id": TOOL_ID, "verdict": "FAIL", "errors": errors}, ensure_ascii=True, indent=2))
        return 1

    text = path.read_text(encoding="utf-8", errors="replace")
    original = text

    if "mechanicus_strict_build_lane_foundation_runner.v0_2_exit_code_consistent" not in text:
        text = text.replace(
            'TOOL_ID = "mechanicus_strict_build_lane_foundation_runner.v0_1"',
            'TOOL_ID = "mechanicus_strict_build_lane_foundation_runner.v0_2_exit_code_consistent"\nLEGACY_VALIDATOR_MARKER = "mechanicus_strict_build_lane_foundation_runner.v0_1"'
        )
        replacements.append("tool_id_v0_2_with_legacy_marker")

    if "def configure_stdout()" not in text:
        anchor = "def utc() -> str:"
        config_fn = '''def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

'''
        if anchor in text:
            text = text.replace(anchor, config_fn + anchor, 1)
            replacements.append("configure_stdout_function_inserted")
        else:
            errors.append("could not insert configure_stdout")

    main_anchor = "def main() -> int:\n"
    if main_anchor in text and "def main() -> int:\n    configure_stdout()\n" not in text:
        text = text.replace(main_anchor, main_anchor + "    configure_stdout()\n", 1)
        replacements.append("configure_stdout_call_inserted")

    old_prints = [
        'print(json.dumps(report, ensure_ascii=False, indent=2))',
        'print(json.dumps(report, ensure_ascii=False, indent=2, default=str))'
    ]
    summary_block = '''summary = {
        "tool_id": TOOL_ID,
        "verdict": report.get("verdict"),
        "target_count": report.get("target_count"),
        "blocking_failure_count": report.get("blocking_failure_count"),
        "foundation_debt_count": report.get("foundation_debt_count"),
        "expected_exit_code": 0 if report.get("verdict") == "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION" and int(report.get("blocking_failure_count", 1)) == 0 else 1,
        "report": str(args.out)
    }
    print(json.dumps(summary, ensure_ascii=True, indent=2))'''
    replaced_print = False
    for old in old_prints:
        if old in text:
            text = text.replace(old, summary_block, 1)
            replacements.append("full_report_stdout_replaced_with_ascii_summary")
            replaced_print = True
            break
    if not replaced_print and "ensure_ascii=True" not in text:
        warnings.append("full report print pattern not found; stdout may already be patched or has different shape")

    old_return = 'return 0 if report["blocking_failure_count"] == 0 else 1'
    new_return = 'return 0 if report.get("verdict") == "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION" and int(report.get("blocking_failure_count", 1)) == 0 else 1'
    if old_return in text:
        text = text.replace(old_return, new_return, 1)
        replacements.append("exit_code_contract_return_replaced")
    elif new_return not in text:
        errors.append("runner return contract pattern not found")

    required_markers = [
        "mechanicus_strict_build_lane_foundation_runner.v0_2_exit_code_consistent",
        "LEGACY_VALIDATOR_MARKER",
        "configure_stdout()",
        "ensure_ascii=True",
        'report.get("verdict") == "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION"'
    ]
    missing_markers = [m for m in required_markers if m not in text]
    if missing_markers:
        errors.append("runner missing required markers after patch: " + ", ".join(missing_markers))

    changed = text != original
    if not errors and changed:
        path.write_text(text, encoding="utf-8")
    elif not errors and not changed:
        warnings.append("runner already appeared patched; no file rewrite needed")

    verdict = "PASS_MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXIT_CODE_PATCH_APPLIED" if not errors else "FAIL_MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXIT_CODE_PATCH"
    report = {
        "tool_id": TOOL_ID,
        "generated_at_utc": utc(),
        "verdict": verdict,
        "runner": RUNNER.as_posix(),
        "changed": changed,
        "replacements": replacements,
        "errors": errors,
        "warnings": warnings
    }
    write_json(repo / REPORT, report)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
