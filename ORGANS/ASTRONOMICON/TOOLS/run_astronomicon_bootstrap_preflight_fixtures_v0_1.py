#!/usr/bin/env python3
"""Run bootstrap preflight/repair fixtures for Astronomicon Stage3.1 hardening."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys

    sys.path.append(str(Path(__file__).resolve().parent))

from astronomicon_bootstrap_preflight_v0_1 import (  # noqa: E402
    DEFAULT_ROUTE_TEMPLATE_REL,
    DEFAULT_START_ACK_TEMPLATE_REL,
    DEFAULT_TASK_ID,
    REQUIRED_ORGANS,
    normalize_repo_root,
    run_preflight,
    to_posix,
    utc_now,
    write_json,
)
from astronomicon_bootstrap_repair_v0_1 import (  # noqa: E402
    default_route_template,
    default_start_ack_template,
    run_repair,
)


def write_json_no_bom(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_json_utf8_bom(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))


def corridor_paths(repo_root: Path) -> tuple[Path, Path]:
    return (
        (repo_root / DEFAULT_ROUTE_TEMPLATE_REL).resolve(),
        (repo_root / DEFAULT_START_ACK_TEMPLATE_REL).resolve(),
    )


def seed_valid_pair(repo_root: Path) -> tuple[Path, Path]:
    route_path, start_path = corridor_paths(repo_root)
    write_json_no_bom(route_path, default_route_template())
    write_json_no_bom(start_path, default_start_ack_template())
    return route_path, start_path


def as_fixture_case(
    *,
    case_id: str,
    case_type: str,
    expected_verdict: str,
    expected_caps: list[str],
    actual_verdict: str,
    actual_caps: list[str],
    evidence_path: str,
    details: dict[str, Any],
) -> dict[str, Any]:
    expected_caps_set = set(expected_caps)
    actual_caps_set = set(actual_caps)
    pass_flag = actual_verdict == expected_verdict and expected_caps_set.issubset(actual_caps_set)
    return {
        "case_id": case_id,
        "case_type": case_type,
        "expected_verdict": expected_verdict,
        "expected_caps": expected_caps,
        "actual_verdict": actual_verdict,
        "actual_caps": sorted(actual_caps_set),
        "evidence_path": evidence_path,
        "pass": pass_flag,
        "details": details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap preflight fixture runner.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument(
        "--report-root",
        default=(
            "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/"
            "TASK-NEWGEN-STAGE3-ASTRONOMICON-BOOTSTRAP-HARDENING-UTF8-PREFLIGHT-PC-V0_1"
        ),
        help="Where to write fixture report artifacts.",
    )
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID, help="Task ID for fixture metadata.")
    args = parser.parse_args()

    repo_root = normalize_repo_root(args.repo_root)
    report_root = (repo_root / args.report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)
    sandbox_root = (report_root / "_bootstrap_preflight_fixture_sandbox_v0_1").resolve()
    if sandbox_root.exists():
        shutil.rmtree(sandbox_root)
    sandbox_root.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    evidence_path = to_posix((report_root / "bootstrap_fixture_results.json").resolve())

    # Case 1: missing route template -> BLOCK
    seed_valid_pair(sandbox_root)
    route_path, start_path = corridor_paths(sandbox_root)
    route_path.unlink()
    receipt = run_preflight(repo_root=sandbox_root, task_id=args.task_id)
    results.append(
        as_fixture_case(
            case_id="CASE-01",
            case_type="MISSING_ROUTE_TEMPLATE",
            expected_verdict="BLOCK",
            expected_caps=["CAP_ASTRONOMICON_ROUTE_TEMPLATE_MISSING"],
            actual_verdict=str(receipt.get("verdict", "")),
            actual_caps=list(receipt.get("caps_triggered", [])),
            evidence_path=evidence_path,
            details={"preflight_receipt": receipt},
        )
    )

    # Case 2: missing start ack template -> BLOCK
    seed_valid_pair(sandbox_root)
    _, start_path = corridor_paths(sandbox_root)
    start_path.unlink()
    receipt = run_preflight(repo_root=sandbox_root, task_id=args.task_id)
    results.append(
        as_fixture_case(
            case_id="CASE-02",
            case_type="MISSING_START_ACK_TEMPLATE",
            expected_verdict="BLOCK",
            expected_caps=["CAP_ASTRONOMICON_START_ACK_TEMPLATE_MISSING"],
            actual_verdict=str(receipt.get("verdict", "")),
            actual_caps=list(receipt.get("caps_triggered", [])),
            evidence_path=evidence_path,
            details={"preflight_receipt": receipt},
        )
    )

    # Case 3: route template has UTF-8 BOM -> BLOCK with explicit BOM cap
    seed_valid_pair(sandbox_root)
    route_path, _ = corridor_paths(sandbox_root)
    write_json_utf8_bom(route_path, default_route_template())
    receipt = run_preflight(repo_root=sandbox_root, task_id=args.task_id)
    results.append(
        as_fixture_case(
            case_id="CASE-03",
            case_type="UTF8_BOM",
            expected_verdict="BLOCK",
            expected_caps=["CAP_ASTRONOMICON_TEMPLATE_UTF8_BOM_PRESENT"],
            actual_verdict=str(receipt.get("verdict", "")),
            actual_caps=list(receipt.get("caps_triggered", [])),
            evidence_path=evidence_path,
            details={"preflight_receipt": receipt},
        )
    )

    # Case 4: invalid JSON -> BLOCK
    seed_valid_pair(sandbox_root)
    route_path, _ = corridor_paths(sandbox_root)
    route_path.write_text("{broken-json\n", encoding="utf-8")
    receipt = run_preflight(repo_root=sandbox_root, task_id=args.task_id)
    results.append(
        as_fixture_case(
            case_id="CASE-04",
            case_type="INVALID_JSON",
            expected_verdict="BLOCK",
            expected_caps=["CAP_ASTRONOMICON_ROUTE_TEMPLATE_JSON_INVALID"],
            actual_verdict=str(receipt.get("verdict", "")),
            actual_caps=list(receipt.get("caps_triggered", [])),
            evidence_path=evidence_path,
            details={"preflight_receipt": receipt},
        )
    )

    # Case 5: route missing one organ -> BLOCK
    seed_valid_pair(sandbox_root)
    route_path, _ = corridor_paths(sandbox_root)
    route_payload = default_route_template()
    route_payload["required_organs"] = REQUIRED_ORGANS[:-1]
    write_json_no_bom(route_path, route_payload)
    receipt = run_preflight(repo_root=sandbox_root, task_id=args.task_id)
    results.append(
        as_fixture_case(
            case_id="CASE-05",
            case_type="MISSING_ORGAN",
            expected_verdict="BLOCK",
            expected_caps=["CAP_ASTRONOMICON_ROUTE_TEMPLATE_MISSING_REQUIRED_ORGANS"],
            actual_verdict=str(receipt.get("verdict", "")),
            actual_caps=list(receipt.get("caps_triggered", [])),
            evidence_path=evidence_path,
            details={"preflight_receipt": receipt},
        )
    )

    # Case 6: valid pair -> PASS or PASS_WITH_WARNINGS
    seed_valid_pair(sandbox_root)
    receipt = run_preflight(repo_root=sandbox_root, task_id=args.task_id)
    valid_case = as_fixture_case(
        case_id="CASE-06",
        case_type="VALID_PAIR",
        expected_verdict="PASS",
        expected_caps=[],
        actual_verdict=str(receipt.get("verdict", "")),
        actual_caps=list(receipt.get("caps_triggered", [])),
        evidence_path=evidence_path,
        details={"preflight_receipt": receipt},
    )
    if valid_case["actual_verdict"] == "PASS_WITH_WARNINGS" and not valid_case["actual_caps"]:
        valid_case["pass"] = True
    results.append(valid_case)

    # Case 7: repair missing files -> creates no-BOM templates
    seed_valid_pair(sandbox_root)
    route_path, start_path = corridor_paths(sandbox_root)
    route_path.unlink()
    start_path.unlink()
    repair_receipt = run_repair(repo_root=sandbox_root, force=False, task_id=args.task_id)
    route_exists_after = route_path.exists()
    start_exists_after = start_path.exists()
    post_preflight = run_preflight(repo_root=sandbox_root, task_id=args.task_id)
    case7_caps = list(post_preflight.get("caps_triggered", []))
    case7_verdict = str(post_preflight.get("verdict", ""))
    case7 = as_fixture_case(
        case_id="CASE-07",
        case_type="REPAIR_MISSING",
        expected_verdict="PASS",
        expected_caps=[],
        actual_verdict=case7_verdict,
        actual_caps=case7_caps,
        evidence_path=evidence_path,
        details={
            "repair_receipt": repair_receipt,
            "route_exists_after": route_exists_after,
            "start_exists_after": start_exists_after,
            "post_preflight": post_preflight,
        },
    )
    if case7["actual_verdict"] == "PASS_WITH_WARNINGS" and not case7["actual_caps"]:
        case7["pass"] = True
    results.append(case7)

    # Case 8: repair BOM file with force -> rewrite no-BOM with before hash
    seed_valid_pair(sandbox_root)
    route_path, _ = corridor_paths(sandbox_root)
    write_json_utf8_bom(route_path, default_route_template())
    repair_receipt = run_repair(repo_root=sandbox_root, force=True, task_id=args.task_id)
    post_preflight = run_preflight(repo_root=sandbox_root, task_id=args.task_id)
    rewrite_actions = [
        action
        for action in repair_receipt.get("actions", [])
        if action.get("operation") == "REWRITTEN_FORCE_UTF8_NO_BOM"
    ]
    has_before_hash = any(action.get("before_sha256") for action in rewrite_actions)
    has_after_hash = any(action.get("after_sha256") for action in rewrite_actions)
    case8 = as_fixture_case(
        case_id="CASE-08",
        case_type="REPAIR_BOM",
        expected_verdict="PASS",
        expected_caps=[],
        actual_verdict=str(post_preflight.get("verdict", "")),
        actual_caps=list(post_preflight.get("caps_triggered", [])),
        evidence_path=evidence_path,
        details={
            "repair_receipt": repair_receipt,
            "post_preflight": post_preflight,
            "force_rewrite_actions_count": len(rewrite_actions),
            "before_hash_recorded": has_before_hash,
            "after_hash_recorded": has_after_hash,
        },
    )
    if case8["actual_verdict"] == "PASS_WITH_WARNINGS" and not case8["actual_caps"]:
        case8["pass"] = True
    if not has_before_hash or not has_after_hash:
        case8["pass"] = False
    results.append(case8)

    passed = len([row for row in results if row.get("pass")])
    failed = len(results) - passed
    fixture_results = {
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "repo_root": to_posix(repo_root),
        "sandbox_root": to_posix(sandbox_root),
        "total_cases": len(results),
        "passed_cases": passed,
        "failed_cases": failed,
        "cases": results,
    }
    write_json(report_root / "bootstrap_fixture_results.json", fixture_results)

    lines = [
        "# Bootstrap Fixture Report",
        "",
        f"Task ID: `{args.task_id}`",
        f"Timestamp (UTC): `{fixture_results['timestamp_utc']}`",
        f"Sandbox: `{fixture_results['sandbox_root']}`",
        "",
        f"- Total cases: `{fixture_results['total_cases']}`",
        f"- Passed: `{fixture_results['passed_cases']}`",
        f"- Failed: `{fixture_results['failed_cases']}`",
        "",
        "## Case Results",
    ]
    for row in results:
        status = "PASS" if row.get("pass") else "FAIL"
        lines.append(f"- `{row['case_id']}` `{row['case_type']}` -> `{status}`")
        lines.append(f"  expected: `{row['expected_verdict']}` {row['expected_caps']}")
        lines.append(f"  actual: `{row['actual_verdict']}` {row['actual_caps']}")
    (report_root / "bootstrap_fixture_report.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    print(json.dumps(fixture_results, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
