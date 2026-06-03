#!/usr/bin/env python3
"""Validate NewGen Current Truth Root v0.1 foundation artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import py_compile
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260522-NEWGEN-CURRENT-TRUTH-ROOT-REPORT-INDEX-VM3-V0_1"
TRUTH_ROOT = "IMPERIUM_NEW_GENERATION/TRUTH"
SANCTUM_STATE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"

ALLOWED_STATUSES = {
    "PASS",
    "PASS_WITH_WARN",
    "WARN",
    "BLOCK",
    "UNKNOWN",
    "MISSING",
    "PARTIAL",
    "FOUNDATION_ONLY",
}


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / "IMPERIUM_NEW_GENERATION/REPORTS" / TASK_ID_DEFAULT

    parser = argparse.ArgumentParser(description="Validate Current Truth Root + Report Status Index + Evidence Source Map.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--output", type=Path, default=default_report_dir / "VALIDATOR_REPORT.json")
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
    task_id = str(args.task_id)
    output_path = args.output.resolve()
    report_dir = output_path.parent

    current_truth_path = repo_root / TRUTH_ROOT / "CURRENT_TRUTH_ROOT_V0_1.json"
    report_index_path = repo_root / TRUTH_ROOT / "REPORT_STATUS_INDEX_V0_1.json"
    evidence_map_path = repo_root / TRUTH_ROOT / "EVIDENCE_SOURCE_MAP_V0_1.json"
    schema_paths = [
        repo_root / TRUTH_ROOT / "SCHEMAS/current_truth_root_v0_1.schema.json",
        repo_root / TRUTH_ROOT / "SCHEMAS/report_status_index_v0_1.schema.json",
        repo_root / TRUTH_ROOT / "SCHEMAS/evidence_source_map_v0_1.schema.json",
    ]
    tool_paths = [
        repo_root / TRUTH_ROOT / "TOOLS/build_current_truth_root_v0_1.py",
        repo_root / TRUTH_ROOT / "TOOLS/validate_current_truth_root_v0_1.py",
    ]
    readme_path = repo_root / TRUTH_ROOT / "README_CURRENT_TRUTH_ROOT_V0_1.md"

    required_report_paths = [
        report_dir / "OFFICIO_ROLE_ACK_OR_WARN.json",
        report_dir / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        report_dir / "SUPER_SKEPTICISM_ACK.json",
        report_dir / "CONTEXT_WINDOW_USAGE_NOTE.md",
        report_dir / "CONTEXT_SOURCE_MIX_REPORT.md",
        report_dir / "CONTEXT_SOURCE_MIX_REPORT.json",
        report_dir / "CURRENT_TRUTH_BUILD_REPORT.json",
        report_dir / "VALIDATOR_REPORT.json",
        report_dir / "FINAL_OWNER_REPORT_RU.md",
        report_dir / "FINAL_RECEIPT.json",
        report_dir / "POST_COMMIT_CLOSURE_RECEIPT.json",
        report_dir / "STEP_PROOF_RECORDS.jsonl",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.json",
    ]

    sanctum_files = [
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/styles.css",
    ]

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    core_files = [current_truth_path, report_index_path, evidence_map_path, readme_path] + schema_paths + tool_paths
    add_check(
        checks,
        warnings,
        blockers,
        "core_truth_files_exist",
        all(path.exists() for path in core_files),
        "truth core files exist",
        "one or more truth core files are missing",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "sanctum_reference_files_exist",
        all(path.exists() for path in sanctum_files),
        "sanctum state/ui reference files exist",
        "one or more sanctum reference files are missing",
    )

    for script_path in tool_paths:
        try:
            py_compile.compile(str(script_path), doraise=True)
            add_check(
                checks,
                warnings,
                blockers,
                f"py_compile_{script_path.name}",
                True,
                f"{script_path.name} compiles",
                "",
            )
        except py_compile.PyCompileError as exc:
            add_check(
                checks,
                warnings,
                blockers,
                f"py_compile_{script_path.name}",
                False,
                "",
                str(exc),
            )

    current_truth, truth_err = load_json(current_truth_path)
    report_index, index_err = load_json(report_index_path)
    evidence_map, evidence_err = load_json(evidence_map_path)

    add_check(
        checks,
        warnings,
        blockers,
        "current_truth_json_parse",
        current_truth is not None,
        "current truth root parses",
        f"current truth root parse failed ({truth_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "report_index_json_parse",
        report_index is not None,
        "report status index parses",
        f"report status index parse failed ({index_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "evidence_map_json_parse",
        evidence_map is not None,
        "evidence source map parses",
        f"evidence source map parse failed ({evidence_err})",
    )

    if current_truth is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "current_truth_schema_id",
            current_truth.get("schema_id") == "CURRENT_TRUTH_ROOT_V0_1",
            "current truth schema_id is correct",
            "current truth schema_id mismatch",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "current_truth_mode",
            current_truth.get("newgen_mode") == "FOUNDATION_TRUTH_SPINE_V0_1",
            "newgen mode is foundation truth spine",
            "newgen mode mismatch",
        )

    if report_index is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "report_index_schema_id",
            report_index.get("schema_id") == "REPORT_STATUS_INDEX_V0_1",
            "report index schema_id is correct",
            "report index schema_id mismatch",
        )

        entries = report_index.get("entries", [])
        if not isinstance(entries, list):
            entries = []
        invalid_statuses = [str(item.get("status")) for item in entries if str(item.get("status")) not in ALLOWED_STATUSES]
        add_check(
            checks,
            warnings,
            blockers,
            "report_status_values",
            not invalid_statuses,
            "all report statuses are allowed",
            f"invalid report statuses found: {invalid_statuses}",
        )

        missing_evidence_for_pass = []
        missing_report_path_for_pass = []
        for item in entries:
            if not isinstance(item, dict):
                continue
            status = str(item.get("status"))
            if status not in {"PASS", "PASS_WITH_WARN"}:
                continue
            refs = item.get("evidence_refs")
            path = str(item.get("report_path", "")).strip()
            if not isinstance(refs, list) or not any(str(ref).strip() for ref in refs):
                missing_evidence_for_pass.append(str(item.get("task_id", "UNKNOWN")))
            if not path:
                missing_report_path_for_pass.append(str(item.get("task_id", "UNKNOWN")))

        add_check(
            checks,
            warnings,
            blockers,
            "pass_entries_have_evidence",
            not missing_evidence_for_pass,
            "all PASS/PASS_WITH_WARN entries have evidence refs",
            f"PASS/PASS_WITH_WARN entries without evidence: {missing_evidence_for_pass}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "pass_entries_have_report_path",
            not missing_report_path_for_pass,
            "all PASS/PASS_WITH_WARN entries have report paths",
            f"PASS/PASS_WITH_WARN entries without report path: {missing_report_path_for_pass}",
        )

    if evidence_map is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "evidence_map_schema_id",
            evidence_map.get("schema_id") == "EVIDENCE_SOURCE_MAP_V0_1",
            "evidence map schema_id is correct",
            "evidence map schema_id mismatch",
        )

    forbidden_claim_fail = False
    forbidden_details = ""
    if current_truth is not None:
        as_text = json.dumps(current_truth)
        bad_patterns = [
            '"production_ready": true',
            '"live_backend": true',
            '"autonomous_execution": true',
            "AUTONOMOUS_EXECUTION_READY:true",
        ]
        hit = [pattern for pattern in bad_patterns if pattern in as_text]
        if hit:
            forbidden_claim_fail = True
            forbidden_details = ", ".join(hit)

    add_check(
        checks,
        warnings,
        blockers,
        "forbidden_claims_absent",
        not forbidden_claim_fail,
        "forbidden production/autonomy claim patterns are absent",
        f"forbidden claim pattern detected: {forbidden_details}",
    )

    sanctum_state_obj, sanctum_state_err = load_json(repo_root / SANCTUM_STATE_REL)
    html_text = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html").read_text(encoding="utf-8")
    js_text = (repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js").read_text(encoding="utf-8")
    ui_updated = "truth-root-status" in html_text and "renderTruthIndex" in js_text

    state_ref_ok = True
    state_ref_details = "UI not updated, state truth reference check skipped."
    if ui_updated:
        if sanctum_state_obj is None:
            state_ref_ok = False
            state_ref_details = f"sanctum state parse failed ({sanctum_state_err})"
        else:
            truth_ref = sanctum_state_obj.get("current_truth_index")
            if not isinstance(truth_ref, dict):
                state_ref_ok = False
                state_ref_details = "current_truth_index section missing in sanctum state"
            else:
                required_keys = {"current_truth_root_path", "report_status_index_path", "evidence_source_map_path", "status"}
                if not required_keys.issubset(truth_ref.keys()):
                    state_ref_ok = False
                    state_ref_details = "current_truth_index section is missing required fields"
                else:
                    state_ref_details = "sanctum state references current truth root/report index/evidence map"

    add_check(
        checks,
        warnings,
        blockers,
        "sanctum_state_truth_reference",
        state_ref_ok,
        state_ref_details,
        state_ref_details,
    )

    add_check(
        checks,
        warnings,
        blockers,
        "task_report_bundle_files_exist",
        all(path.exists() for path in required_report_paths),
        "all required task report bundle files exist",
        "one or more required task report bundle files are missing",
        fail_level="WARN",
    )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "CURRENT_TRUTH_VALIDATOR_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validated_paths": {
            "current_truth_root": current_truth_path.relative_to(repo_root).as_posix(),
            "report_status_index": report_index_path.relative_to(repo_root).as_posix(),
            "evidence_source_map": evidence_map_path.relative_to(repo_root).as_posix(),
            "sanctum_state": SANCTUM_STATE_REL,
            "report_dir": report_dir.relative_to(repo_root).as_posix() if report_dir.exists() else str(report_dir),
        },
        "no_fake_green_note": "PASS here validates bounded foundation truth/index artifacts only.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"validator_verdict={verdict}")
    print(f"validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
