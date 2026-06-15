#!/usr/bin/env python3
"""Validate Owner Question Gate foundation artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-OWNER-QUESTION-GATE-VM2-V0_1"

REQUIRED_STATUSES = {
    "OPEN",
    "ANSWERED",
    "DEFERRED",
    "CANCELLED",
    "STALE",
    "FOUNDATION_SAMPLE",
}
REQUIRED_DERIVED_STATUSES = {
    "BLOCKING_OWNER_DECISION_REQUIRED",
    "WARN_OWNER_REVIEW_RECOMMENDED",
}
REQUIRED_BLOCKING_LEVELS = {"BLOCKING", "NON_BLOCKING", "WARN_ONLY"}
REQUIRED_DECISION_TYPES = {
    "CLARIFICATION",
    "APPROVAL",
    "REJECTION",
    "SCOPE_DECISION",
    "RISK_ACCEPTANCE",
    "TOOL_DECISION",
    "MERGE_DECISION",
}
REQUIRED_SAMPLE_QUESTION_IDS = {
    "OWNER_Q-FOUNDATION-001",
    "OWNER_Q-FOUNDATION-002",
    "OWNER_Q-FOUNDATION-003",
    "OWNER_Q-FOUNDATION-004",
    "OWNER_Q-FOUNDATION-005",
    "OWNER_Q-FOUNDATION-006",
}


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
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
    pass_details: str,
    fail_details: str,
    fail_level: str = "BLOCK",
) -> None:
    if ok:
        checks.append({"check_id": check_id, "status": "PASS", "details": pass_details})
        return

    checks.append({"check_id": check_id, "status": fail_level, "details": fail_details})
    if fail_level == "WARN":
        warnings.append(f"{check_id}:{fail_details}")
    else:
        blockers.append(f"{check_id}:{fail_details}")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = (
        default_repo_root
        / "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260523-NEWGEN-SANCTUM-OWNER-QUESTION-GATE-VM2-V0_1"
    )
    parser = argparse.ArgumentParser(description="Validate Owner Question Gate artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "VALIDATOR_REPORT.json")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    return parser.parse_args()


def count_where(items: list[dict[str, Any]], key: str, value: str) -> int:
    return sum(1 for item in items if str(item.get(key, "")) == value)


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()
    task_id = str(args.task_id)

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    registry_path = repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_REGISTRY_V0_1.json"
    status_rules_path = repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_STATUS_RULES_V0_1.json"
    priority_rules_path = repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_PRIORITY_RULES_V0_1.json"
    sample_set_path = repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_SAMPLE_SET_V0_1.json"
    gate_doc_path = repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/OWNER_QUESTIONS/OWNER_QUESTION_GATE_V0_1.md"

    question_schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/owner_question.schema.json"
    event_schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/owner_question_event.schema.json"
    state_schema_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/owner_question_gate_state.schema.json"
    state_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/owner_question_gate_state.generated.json"

    builder_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/build_owner_question_gate_v0_1.py"
    validator_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/validate_owner_question_gate_v0_1.py"

    index_html_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html"
    app_js_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js"
    styles_path = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/styles.css"

    required_core_files = [
        gate_doc_path,
        registry_path,
        status_rules_path,
        priority_rules_path,
        sample_set_path,
        question_schema_path,
        event_schema_path,
        state_schema_path,
        state_path,
        builder_path,
        validator_path,
        index_html_path,
        app_js_path,
        styles_path,
    ]
    add_check(
        checks,
        warnings,
        blockers,
        "required_core_files_exist",
        all(path.exists() for path in required_core_files),
        "all owner question gate core files exist",
        "one or more owner question gate core files are missing",
    )

    required_report_files = [
        report_dir / "FINAL_OWNER_REPORT_RU.md",
        report_dir / "FINAL_RECEIPT.json",
        report_dir / "SMOKE_REPORT.json",
        report_dir / "CONTEXT_SOURCE_REPORT.md",
        report_dir / "CONTEXT_SOURCE_REPORT.json",
        report_dir / "CONTEXT_WINDOW_USAGE_NOTE.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.md",
        report_dir / "NEXT_TASK_IMPROVEMENT_REPORT.json",
        report_dir / "KPD_SLICE.md",
        report_dir / "STEP_PROOF_RECORDS.jsonl",
        report_dir / "OFFICIO_ROLE_ACK_OR_WARN.json",
        report_dir / "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
        report_dir / "SUPER_SKEPTICISM_ACK.json",
        report_dir / "POST_COMMIT_CLOSURE_RECEIPT.json",
    ]
    add_check(
        checks,
        warnings,
        blockers,
        "required_report_bundle_files_exist",
        all(path.exists() for path in required_report_files),
        "required report bundle files exist",
        "one or more required report bundle files are missing",
    )

    registry_obj, registry_err = load_json(registry_path)
    status_rules_obj, status_rules_err = load_json(status_rules_path)
    priority_rules_obj, priority_rules_err = load_json(priority_rules_path)
    sample_set_obj, sample_set_err = load_json(sample_set_path)
    state_obj, state_err = load_json(state_path)
    question_schema_obj, question_schema_err = load_json(question_schema_path)
    event_schema_obj, event_schema_err = load_json(event_schema_path)
    state_schema_obj, state_schema_err = load_json(state_schema_path)

    add_check(checks, warnings, blockers, "registry_parse", registry_obj is not None, "registry parses", f"registry parse failed ({registry_err})")
    add_check(checks, warnings, blockers, "status_rules_parse", status_rules_obj is not None, "status rules parse", f"status rules parse failed ({status_rules_err})")
    add_check(checks, warnings, blockers, "priority_rules_parse", priority_rules_obj is not None, "priority rules parse", f"priority rules parse failed ({priority_rules_err})")
    add_check(checks, warnings, blockers, "sample_set_parse", sample_set_obj is not None, "sample set parses", f"sample set parse failed ({sample_set_err})")
    add_check(checks, warnings, blockers, "state_parse", state_obj is not None, "state parses", f"state parse failed ({state_err})")
    add_check(checks, warnings, blockers, "question_schema_parse", question_schema_obj is not None, "question schema parses", f"question schema parse failed ({question_schema_err})")
    add_check(checks, warnings, blockers, "event_schema_parse", event_schema_obj is not None, "event schema parses", f"event schema parse failed ({event_schema_err})")
    add_check(checks, warnings, blockers, "state_schema_parse", state_schema_obj is not None, "state schema parses", f"state schema parse failed ({state_schema_err})")

    if status_rules_obj is not None:
        statuses = set(str(x) for x in status_rules_obj.get("allowed_statuses", []) if str(x).strip())
        derived = set(str(x) for x in status_rules_obj.get("derived_gate_statuses", []) if str(x).strip())
        sources = set(str(x) for x in status_rules_obj.get("allowed_sources", []) if str(x).strip())
        decision_types = set(str(x) for x in status_rules_obj.get("allowed_decision_types", []) if str(x).strip())

        add_check(
            checks,
            warnings,
            blockers,
            "status_rules_required_statuses",
            REQUIRED_STATUSES.issubset(statuses),
            "status rules include required statuses",
            "status rules missing required statuses",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "status_rules_required_derived_statuses",
            REQUIRED_DERIVED_STATUSES.issubset(derived),
            "status rules include required derived statuses",
            "status rules missing required derived statuses",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "status_rules_source_set",
            {"SERVITOR", "ORGAN", "SANCTUM", "TRUTH_GATE", "OWNER"}.issubset(sources),
            "status rules include required source set",
            "status rules missing required source enum values",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "status_rules_decision_types",
            REQUIRED_DECISION_TYPES.issubset(decision_types),
            "status rules include required decision types",
            "status rules missing required decision types",
        )

    if priority_rules_obj is not None:
        blocking_levels = set(str(x) for x in priority_rules_obj.get("blocking_levels", []) if str(x).strip())
        add_check(
            checks,
            warnings,
            blockers,
            "priority_rules_blocking_levels",
            REQUIRED_BLOCKING_LEVELS.issubset(blocking_levels),
            "priority rules include required blocking levels",
            "priority rules missing required blocking levels",
        )

    if sample_set_obj is not None:
        questions_raw = sample_set_obj.get("questions", [])
        questions = [q for q in questions_raw if isinstance(q, dict)] if isinstance(questions_raw, list) else []

        add_check(
            checks,
            warnings,
            blockers,
            "sample_min_count",
            len(questions) >= 6,
            f"sample count is {len(questions)} (>=6)",
            f"sample count is {len(questions)} (<6)",
        )

        ids = {str(q.get("question_id", "")).strip() for q in questions}
        add_check(
            checks,
            warnings,
            blockers,
            "sample_required_question_ids_present",
            REQUIRED_SAMPLE_QUESTION_IDS.issubset(ids),
            "required foundation sample question IDs are present",
            "required foundation sample question IDs are missing",
        )

        bad_records: list[str] = []
        bad_status: list[str] = []
        bad_blocking: list[str] = []
        bad_decision_type: list[str] = []
        for question in questions:
            qid = str(question.get("question_id", "UNKNOWN"))
            required_fields = {
                "question_id",
                "task_id",
                "source",
                "source_ref",
                "question_text_ru",
                "why_needed_ru",
                "decision_type",
                "blocking_level",
                "status",
                "owner_answer_required",
                "allowed_answers",
                "evidence_refs",
                "created_at_utc",
                "updated_at_utc",
            }
            if not required_fields.issubset(question.keys()):
                bad_records.append(qid)
            if str(question.get("status", "")) not in REQUIRED_STATUSES:
                bad_status.append(qid)
            if str(question.get("blocking_level", "")) not in REQUIRED_BLOCKING_LEVELS:
                bad_blocking.append(qid)
            if str(question.get("decision_type", "")) not in REQUIRED_DECISION_TYPES:
                bad_decision_type.append(qid)

        add_check(
            checks,
            warnings,
            blockers,
            "sample_records_have_required_fields",
            not bad_records,
            "all sample records contain required fields",
            f"sample records missing required fields: {bad_records}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "sample_statuses_allowed",
            not bad_status,
            "all sample statuses are allowed",
            f"sample records with disallowed statuses: {bad_status}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "sample_blocking_levels_allowed",
            not bad_blocking,
            "all sample blocking levels are allowed",
            f"sample records with disallowed blocking levels: {bad_blocking}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "sample_decision_types_allowed",
            not bad_decision_type,
            "all sample decision types are allowed",
            f"sample records with disallowed decision types: {bad_decision_type}",
        )

        required_set_status_ok = True
        for q in questions:
            qid = str(q.get("question_id", ""))
            if qid in REQUIRED_SAMPLE_QUESTION_IDS and str(q.get("status", "")) != "FOUNDATION_SAMPLE":
                required_set_status_ok = False
                break

        add_check(
            checks,
            warnings,
            blockers,
            "required_sample_records_are_foundation_sample",
            required_set_status_ok,
            "required sample records are FOUNDATION_SAMPLE",
            "one or more required sample records are not FOUNDATION_SAMPLE",
        )

    if state_obj is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "state_schema_id",
            str(state_obj.get("schema_id", "")) == "OWNER_QUESTION_GATE_STATE_V0_1",
            "state schema_id matches",
            "state schema_id mismatch",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "state_mode",
            str(state_obj.get("mode", "")) == "FOUNDATION_READ_ONLY_OWNER_QUESTION_GATE",
            "state mode matches",
            "state mode mismatch",
        )

        flags = state_obj.get("truth_flags", {})
        flags_ok = (
            isinstance(flags, dict)
            and flags.get("read_only") is True
            and flags.get("foundation_only") is True
            and flags.get("live_owner_channel") is False
            and flags.get("owner_answer_write_path") is False
            and flags.get("production_ready") is False
        )
        add_check(
            checks,
            warnings,
            blockers,
            "state_truth_flags_no_live_claim",
            flags_ok,
            "state truth flags enforce read-only foundation no-live boundary",
            "state truth flags violate no-live/no-write boundary",
        )

        questions_raw = state_obj.get("questions", [])
        questions = [q for q in questions_raw if isinstance(q, dict)] if isinstance(questions_raw, list) else []
        summary = state_obj.get("summary", {}) if isinstance(state_obj.get("summary", {}), dict) else {}

        add_check(
            checks,
            warnings,
            blockers,
            "state_question_count_minimum",
            len(questions) >= 6,
            f"state has {len(questions)} questions",
            f"state has only {len(questions)} questions",
        )

        expected_total = len(questions)
        expected_open = count_where(questions, "status", "OPEN")
        expected_deferred = count_where(questions, "status", "DEFERRED")
        expected_answered = count_where(questions, "status", "ANSWERED")
        expected_stale = count_where(questions, "status", "STALE")
        expected_foundation = count_where(questions, "status", "FOUNDATION_SAMPLE")
        expected_blocking = count_where(questions, "blocking_level", "BLOCKING")
        expected_warn_only = count_where(questions, "blocking_level", "WARN_ONLY")
        expected_owner_required = sum(1 for q in questions if bool(q.get("owner_answer_required")))

        summary_ok = (
            int(summary.get("total_questions", -1)) == expected_total
            and int(summary.get("open_count", -1)) == expected_open
            and int(summary.get("deferred_count", -1)) == expected_deferred
            and int(summary.get("answered_count", -1)) == expected_answered
            and int(summary.get("stale_count", -1)) == expected_stale
            and int(summary.get("foundation_sample_count", -1)) == expected_foundation
            and int(summary.get("blocking_count", -1)) == expected_blocking
            and int(summary.get("warn_only_count", -1)) == expected_warn_only
            and int(summary.get("owner_answer_required_count", -1)) == expected_owner_required
        )
        add_check(
            checks,
            warnings,
            blockers,
            "state_summary_counts_consistent",
            summary_ok,
            "state summary counts are consistent with question records",
            "state summary counts do not match question records",
        )

        derived_status = str(summary.get("derived_gate_status", ""))
        add_check(
            checks,
            warnings,
            blockers,
            "state_summary_derived_gate_status_allowed",
            derived_status in {
                "BLOCKING_OWNER_DECISION_REQUIRED",
                "WARN_OWNER_REVIEW_RECOMMENDED",
                "FOUNDATION_SAMPLE_ONLY",
            },
            "derived gate status is allowed",
            "derived gate status is not allowed",
        )

        boundary = str(state_obj.get("boundary_note", ""))
        add_check(
            checks,
            warnings,
            blockers,
            "state_boundary_note",
            "FOUNDATION_ONLY" in boundary and "NOT LIVE OWNER CHANNEL" in boundary,
            "boundary note contains foundation/no-live markers",
            "boundary note missing foundation/no-live markers",
        )

        forbidden_claims = state_obj.get("forbidden_claims", [])
        forbidden_ok = isinstance(forbidden_claims, list) and "LIVE_OWNER_ANSWER_CHANNEL_ACTIVE" in [str(v) for v in forbidden_claims]
        add_check(
            checks,
            warnings,
            blockers,
            "forbidden_live_claim_declared",
            forbidden_ok,
            "forbidden live claim is explicitly declared",
            "forbidden live claim declaration is missing",
        )

    index_html = index_html_path.read_text(encoding="utf-8") if index_html_path.exists() else ""
    app_js = app_js_path.read_text(encoding="utf-8") if app_js_path.exists() else ""
    styles = styles_path.read_text(encoding="utf-8") if styles_path.exists() else ""

    add_check(
        checks,
        warnings,
        blockers,
        "ui_owner_question_section_present",
        "owner-question-gate" in index_html,
        "index.html contains owner question gate section",
        "index.html is missing owner question gate section",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "ui_owner_question_renderer_present",
        "renderOwnerQuestionGate" in app_js,
        "app.js contains owner question renderer",
        "app.js is missing owner question renderer",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "ui_owner_question_styles_present",
        ".owner-question-gate" in styles,
        "styles.css contains owner question gate styles",
        "styles.css is missing owner question gate styles",
    )

    verdict = "PASS" if not blockers else "BLOCK"

    output_payload = {
        "schema_id": "OWNER_QUESTION_GATE_VALIDATOR_REPORT_V0_1",
        "task_id": task_id,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validated_paths": {
            "registry": registry_path.relative_to(repo_root).as_posix(),
            "status_rules": status_rules_path.relative_to(repo_root).as_posix(),
            "priority_rules": priority_rules_path.relative_to(repo_root).as_posix(),
            "sample_set": sample_set_path.relative_to(repo_root).as_posix(),
            "state": state_path.relative_to(repo_root).as_posix(),
            "report_dir": report_dir.relative_to(repo_root).as_posix(),
        },
        "no_fake_live_claim_note": "Validator enforces foundation-only read-only boundary with explicit NO LIVE OWNER CHANNEL markers.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"validator_verdict={verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
