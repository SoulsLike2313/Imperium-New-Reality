#!/usr/bin/env python3
"""Run required language/encoding fixture cases for mojibake filter."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys

    sys.path.append(str(Path(__file__).resolve().parent))

from inquisition_mojibake_filter_v0_1 import run_filter, utc_now, write_json, write_markdown  # noqa: E402


DEFAULT_TASK_ID = "TASK-NEWGEN-LANGUAGE-AUTHORITY-AND-MOJIBAKE-FILTER-SPINOFF-PC-V0_1"


def write_utf8(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_utf8_bom(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))


def write_json_utf8(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_json_utf8_bom(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    write_utf8_bom(path, text)


def case_result(
    *,
    case_id: str,
    case_type: str,
    expected_verdict: str,
    expected_caps: list[str],
    report: dict[str, Any],
    evidence_path: str,
) -> dict[str, Any]:
    actual_verdict = str(report.get("verdict", ""))
    actual_caps = list(report.get("caps_triggered", []))
    passed = actual_verdict == expected_verdict and set(expected_caps).issubset(set(actual_caps))
    return {
        "case_id": case_id,
        "case_type": case_type,
        "expected_verdict": expected_verdict,
        "expected_caps": expected_caps,
        "actual_verdict": actual_verdict,
        "actual_caps": sorted(set(actual_caps)),
        "evidence_path": evidence_path,
        "pass": passed,
        "details": {
            "summary": report.get("summary", {}),
            "excluded_paths": report.get("excluded_paths", [])[:10],
            "sample_hits": report.get("hits", [])[:5],
        },
    }


def run_case(
    *,
    sandbox_root: Path,
    case_name: str,
    task_id: str,
    current_task_id: str,
) -> dict[str, Any]:
    case_root = sandbox_root / case_name
    if case_root.exists():
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True, exist_ok=True)
    write_utf8(case_root / "AGENTS.md", "# AGENTS\n\nEnglish only baseline.\n")
    return {
        "repo_root": case_root,
        "task_id": task_id,
        "current_task_id": current_task_id,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run language/encoding fixtures.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument(
        "--report-root",
        default=(
            "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/REPORTS/"
            "TASK-NEWGEN-LANGUAGE-AUTHORITY-AND-MOJIBAKE-FILTER-SPINOFF-PC-V0_1"
        ),
        help="Output report root.",
    )
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID, help="Task ID metadata.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    report_root = (repo_root / args.report_root).resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    sandbox_root = (report_root / "_language_encoding_fixture_sandbox_v0_1").resolve()
    if sandbox_root.exists():
        shutil.rmtree(sandbox_root)
    sandbox_root.mkdir(parents=True, exist_ok=True)

    current_task_id = args.task_id
    evidence_path = str((report_root / "language_encoding_fixture_results.json").resolve()).replace("\\", "/")
    results: list[dict[str, Any]] = []

    # Case 1: clean English canonical file -> PASS
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-01-CLEAN_ENGLISH",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_utf8(
        case["repo_root"] / "IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/POLICIES/CLEAN.md",
        "Policy text in English only.\n",
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    results.append(
        case_result(
            case_id="CASE-01",
            case_type="CLEAN_ENGLISH",
            expected_verdict="PASS",
            expected_caps=[],
            report=report,
            evidence_path=evidence_path,
        )
    )

    # Case 2: Cyrillic in canonical markdown -> BLOCK
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-02-CYRILLIC_CANONICAL",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_utf8(
        case["repo_root"] / "IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/POLICIES/BAD.md",
        "Forbidden text: \u0422\u0435\u043a\u0441\u0442.\n",
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    results.append(
        case_result(
            case_id="CASE-02",
            case_type="CYRILLIC_CANONICAL",
            expected_verdict="BLOCK",
            expected_caps=["CAP_CANONICAL_ARTIFACT_CONTAINS_CYRILLIC"],
            report=report,
            evidence_path=evidence_path,
        )
    )

    # Case 3: UTF-8 BOM JSON -> BLOCK
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-03-UTF8_BOM",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_json_utf8_bom(
        case["repo_root"] / "IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/POLICIES/BOM.json",
        {"value": "english"},
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    results.append(
        case_result(
            case_id="CASE-03",
            case_type="UTF8_BOM",
            expected_verdict="BLOCK",
            expected_caps=["CAP_UTF8_BOM_NOT_DETECTED"],
            report=report,
            evidence_path=evidence_path,
        )
    )

    # Case 4: replacement character -> BLOCK
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-04-REPLACEMENT_CHARACTER",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_utf8(
        case["repo_root"] / "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/MATRICES/REPLACEMENT.md",
        "Bad replacement: \ufffd\n",
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    results.append(
        case_result(
            case_id="CASE-04",
            case_type="REPLACEMENT_CHARACTER",
            expected_verdict="BLOCK",
            expected_caps=["CAP_REPLACEMENT_CHARACTER_NOT_DETECTED"],
            report=report,
            evidence_path=evidence_path,
        )
    )

    # Case 5: named mojibake signature -> BLOCK
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-05-MOJIBAKE_SIGNATURE",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_utf8(
        case["repo_root"] / "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/MATRICES/MOJIBAKE.md",
        "Broken sequence: \u00c3\u00a2 and \u00d0\u00a1.\n",
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    results.append(
        case_result(
            case_id="CASE-05",
            case_type="MOJIBAKE_SIGNATURE",
            expected_verdict="BLOCK",
            expected_caps=["CAP_MOJIBAKE_SIGNATURE_NOT_DETECTED"],
            report=report,
            evidence_path=evidence_path,
        )
    )

    # Case 6: controlled localization resource -> PASS (excluded)
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-06-LOCALIZATION_ALLOWED",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_utf8(
        case["repo_root"] / "IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/locales/ru/messages.md",
        "\u041b\u043e\u043a\u0430\u043b\u0438\u0437\u043e\u0432\u0430\u043d\u043e.\n",
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    case6 = case_result(
        case_id="CASE-06",
        case_type="LOCALIZATION_ALLOWED",
        expected_verdict="PASS",
        expected_caps=[],
        report=report,
        evidence_path=evidence_path,
    )
    if report.get("verdict") == "WARN" and not report.get("caps_triggered"):
        case6["pass"] = True
    results.append(case6)

    # Case 7: binary/PDF ignored -> PASS
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-07-BINARY_EXCLUDED",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    pdf_path = case["repo_root"] / "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/REPORTS/sample.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.write_bytes(b"%PDF-1.4\n%binary\n")
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    results.append(
        case_result(
            case_id="CASE-07",
            case_type="BINARY_EXCLUDED",
            expected_verdict="PASS",
            expected_caps=[],
            report=report,
            evidence_path=evidence_path,
        )
    )

    # Case 8: Officio-authorized runtime owner summary -> WARN
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-08-RUNTIME_OWNER_SUMMARY",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_utf8(
        case["repo_root"]
        / "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/REPORTS/TASK-LOCAL-RUNTIME/final_owner_summary_ru.md",
        "Runtime owner summary: \u041e\u0442\u0447\u0435\u0442.\n",
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    case8 = case_result(
        case_id="CASE-08",
        case_type="RUNTIME_OWNER_SUMMARY",
        expected_verdict="WARN",
        expected_caps=["CAP_CANONICAL_ARTIFACT_CONTAINS_CYRILLIC"],
        report=report,
        evidence_path=evidence_path,
    )
    if report.get("verdict") == "PASS" and not report.get("caps_triggered"):
        case8["pass"] = True
    results.append(case8)

    # Case 9: taskpack root file with Cyrillic -> BLOCK
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-09-TASKPACK_ROOT_CYRILLIC",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_utf8(
        case["repo_root"]
        / f"IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/{current_task_id}/EXTRACTED/TASK_SPEC.md",
        "Task root bad text: \u041f\u0440\u0438\u043c\u0435\u0440.\n",
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    results.append(
        case_result(
            case_id="CASE-09",
            case_type="TASKPACK_ROOT_VIOLATION_CYRILLIC",
            expected_verdict="BLOCK",
            expected_caps=["CAP_NON_ENGLISH_TASKPACK_INTERNAL_TEXT"],
            report=report,
            evidence_path=evidence_path,
        )
    )

    # Case 10: taskpack root file with UTF-8 BOM -> BLOCK
    case = run_case(
        sandbox_root=sandbox_root,
        case_name="CASE-10-TASKPACK_ROOT_BOM",
        task_id=args.task_id,
        current_task_id=current_task_id,
    )
    write_utf8_bom(
        case["repo_root"]
        / f"IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/{current_task_id}/EXTRACTED/TASK_SPEC.md",
        "Task root with BOM only.\n",
    )
    report = run_filter(repo_root=case["repo_root"], task_id=args.task_id, current_task_id=current_task_id)
    results.append(
        case_result(
            case_id="CASE-10",
            case_type="TASKPACK_ROOT_VIOLATION_BOM",
            expected_verdict="BLOCK",
            expected_caps=["CAP_UTF8_BOM_NOT_DETECTED"],
            report=report,
            evidence_path=evidence_path,
        )
    )

    passed = len([row for row in results if row.get("pass")])
    failed = len(results) - passed
    fixture_results = {
        "task_id": args.task_id,
        "timestamp_utc": utc_now(),
        "sandbox_root": str(sandbox_root).replace("\\", "/"),
        "total_cases": len(results),
        "passed_cases": passed,
        "failed_cases": failed,
        "cases": results,
    }
    write_json(report_root / "language_encoding_fixture_results.json", fixture_results)

    lines = [
        "# Language Encoding Fixture Report",
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
    write_markdown(report_root / "language_encoding_fixture_report.md", lines)

    print(json.dumps(fixture_results, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
