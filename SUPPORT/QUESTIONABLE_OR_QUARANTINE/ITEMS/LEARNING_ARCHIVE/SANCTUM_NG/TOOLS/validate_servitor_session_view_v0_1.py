#!/usr/bin/env python3
"""Validate Servitor Session View foundation artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-SERVITOR-SESSION-VIEW-VM2-V0_1"
ALLOWED_STATUSES = {
    "PASS_STRICT",
    "PASS_WITH_WARN",
    "PARTIAL_ACCEPTED",
    "PARTIAL_BLOCKED",
    "FOUNDATION_ONLY",
    "UNKNOWN",
    "MISSING",
    "STALE",
    "NOT_READY",
    "BLOCKED",
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
    default_state = (
        default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/servitor_session_view_state.generated.json"
    )
    default_schema = (
        default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/servitor_session_view_state.schema.json"
    )
    default_timeline_schema = (
        default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/servitor_session_timeline_event.schema.json"
    )
    default_status_rules = (
        default_repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/SERVITOR_SESSIONS/SERVITOR_SESSION_STATUS_RULES_V0_1.json"
    )
    default_report_dir = (
        default_repo_root / "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260523-NEWGEN-SANCTUM-SERVITOR-SESSION-VIEW-VM2-V0_1"
    )
    default_output = default_report_dir / "VALIDATOR_REPORT.json"

    parser = argparse.ArgumentParser(description="Validate Servitor Session View artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--state", type=Path, default=default_state)
    parser.add_argument("--schema", type=Path, default=default_schema)
    parser.add_argument("--timeline-schema", type=Path, default=default_timeline_schema)
    parser.add_argument("--status-rules", type=Path, default=default_status_rules)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    state_path = args.state.resolve()
    schema_path = args.schema.resolve()
    timeline_schema_path = args.timeline_schema.resolve()
    status_rules_path = args.status_rules.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()
    task_id = str(args.task_id)

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    required_files = [
        state_path,
        schema_path,
        timeline_schema_path,
        status_rules_path,
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/build_servitor_session_view_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/validate_servitor_session_view_v0_1.py",
        repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/SERVITOR_SESSIONS/SERVITOR_SESSION_VIEW_V0_1.md",
        repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/SERVITOR_SESSIONS/SERVITOR_SESSION_VIEW_REGISTRY_V0_1.json",
        repo_root / "IMPERIUM_NEW_GENERATION/TRUTH/SERVITOR_SESSIONS/SERVITOR_SESSION_STATUS_RULES_V0_1.json",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/index.html",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/app.js",
        repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP/styles.css",
    ]
    add_check(
        checks,
        warnings,
        blockers,
        "required_files_exist",
        all(path.exists() for path in required_files),
        "all core session-view files exist",
        "one or more core session-view files are missing",
    )

    state_obj, state_err = load_json(state_path)
    schema_obj, schema_err = load_json(schema_path)
    timeline_schema_obj, timeline_schema_err = load_json(timeline_schema_path)
    status_rules_obj, status_rules_err = load_json(status_rules_path)

    add_check(
        checks,
        warnings,
        blockers,
        "state_parse",
        state_obj is not None,
        "state parses as JSON object",
        f"state parse failed ({state_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "state_schema_parse",
        schema_obj is not None,
        "state schema parses as JSON object",
        f"state schema parse failed ({schema_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "timeline_schema_parse",
        timeline_schema_obj is not None,
        "timeline schema parses as JSON object",
        f"timeline schema parse failed ({timeline_schema_err})",
    )
    add_check(
        checks,
        warnings,
        blockers,
        "status_rules_parse",
        status_rules_obj is not None,
        "status rules parse as JSON object",
        f"status rules parse failed ({status_rules_err})",
    )

    allowed_from_rules: set[str] = set(ALLOWED_STATUSES)
    if status_rules_obj is not None:
        statuses = status_rules_obj.get("allowed_statuses", [])
        if isinstance(statuses, list):
            allowed_from_rules = {str(item) for item in statuses if str(item).strip()}
        add_check(
            checks,
            warnings,
            blockers,
            "status_rules_include_required_baseline",
            ALLOWED_STATUSES.issubset(allowed_from_rules),
            "status rules include baseline required statuses",
            "status rules are missing one or more baseline statuses",
        )

    if state_obj is not None:
        required_keys = {
            "schema_id",
            "task_id",
            "mode",
            "generated_at_utc",
            "session",
            "truth_flags",
            "source_reports",
            "acceptance_semantics",
            "action_layer",
            "organ_dialogue",
            "evidence_summary",
            "timeline",
            "warnings",
            "limitations",
            "forbidden_claims",
            "next_required_step",
        }
        add_check(
            checks,
            warnings,
            blockers,
            "state_minimum_shape",
            required_keys.issubset(state_obj.keys()),
            "state contains required top-level keys",
            "state is missing required top-level keys",
        )

        add_check(
            checks,
            warnings,
            blockers,
            "schema_id_match",
            str(state_obj.get("schema_id", "")) == "SERVITOR_SESSION_VIEW_STATE_V0_1",
            "schema_id matches SERVITOR_SESSION_VIEW_STATE_V0_1",
            "schema_id mismatch",
        )

        truth_flags = state_obj.get("truth_flags", {})
        flags_ok = (
            isinstance(truth_flags, dict)
            and truth_flags.get("read_only") is True
            and truth_flags.get("foundation_only") is True
            and truth_flags.get("live_autonomous_execution") is False
            and truth_flags.get("production_ready") is False
        )
        add_check(
            checks,
            warnings,
            blockers,
            "forbidden_live_claims_absent",
            flags_ok,
            "truth_flags enforce read-only/foundation/no-live/no-production",
            "truth_flags violate no-live/no-production boundary",
        )

        timeline = state_obj.get("timeline", {})
        events = timeline.get("events", []) if isinstance(timeline, dict) else []
        if not isinstance(events, list):
            events = []
        add_check(
            checks,
            warnings,
            blockers,
            "timeline_non_empty",
            len(events) > 0,
            "timeline has events",
            "timeline is empty",
        )

        run_events = 0
        rerun_events = 0
        bad_status_events: list[str] = []
        strict_without_evidence: list[str] = []
        for event in events:
            if not isinstance(event, dict):
                continue
            status = str(event.get("status", "UNKNOWN"))
            if status not in allowed_from_rules:
                bad_status_events.append(str(event.get("event_id", "UNKNOWN")))
            if str(event.get("run_kind", "RUN")) == "RERUN":
                rerun_events += 1
            else:
                run_events += 1
            refs = event.get("evidence_refs", [])
            if status == "PASS_STRICT":
                if not isinstance(refs, list) or not any(str(item).strip() for item in refs):
                    strict_without_evidence.append(str(event.get("event_id", "UNKNOWN")))

        add_check(
            checks,
            warnings,
            blockers,
            "timeline_contains_run_events",
            run_events > 0,
            f"timeline contains RUN events ({run_events})",
            "timeline has zero RUN events",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "timeline_contains_rerun_events",
            rerun_events > 0,
            f"timeline contains RERUN events ({rerun_events})",
            "timeline has zero RERUN events",
            fail_level="WARN",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "timeline_statuses_allowed",
            not bad_status_events,
            "all timeline event statuses are allowed",
            f"timeline has disallowed statuses in events: {bad_status_events}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "no_fake_green_timeline",
            not strict_without_evidence,
            "all PASS_STRICT timeline events include evidence refs",
            f"PASS_STRICT without evidence refs: {strict_without_evidence}",
        )

        source_reports = state_obj.get("source_reports", {})
        required_sources = {
            "action_layer_hardening",
            "current_truth_root_report_index",
            "evidence_map_unified",
            "partial_acceptance_map",
            "action_rollback_contract",
            "negative_test_mutation_check",
            "organ_dialogue_demo",
        }
        sources_ok = isinstance(source_reports, dict) and required_sources.issubset(source_reports.keys())
        add_check(
            checks,
            warnings,
            blockers,
            "source_reports_coverage",
            sources_ok,
            "all required source report categories are present",
            "source report categories are incomplete",
        )

        source_bad_status: list[str] = []
        source_missing_declared_present: list[str] = []
        if isinstance(source_reports, dict):
            for key, value in source_reports.items():
                if not isinstance(value, dict):
                    continue
                status = str(value.get("status", "UNKNOWN"))
                if status not in allowed_from_rules:
                    source_bad_status.append(key)
                exists = bool(value.get("exists", False))
                report_dir_rel = str(value.get("report_dir", ""))
                if exists and report_dir_rel:
                    report_dir_path = repo_root / report_dir_rel
                    if not report_dir_path.exists():
                        source_missing_declared_present.append(key)

        add_check(
            checks,
            warnings,
            blockers,
            "source_report_statuses_allowed",
            not source_bad_status,
            "all source report statuses are allowed",
            f"source reports have disallowed statuses: {source_bad_status}",
        )
        add_check(
            checks,
            warnings,
            blockers,
            "source_report_paths_exist_when_declared",
            not source_missing_declared_present,
            "source report dirs exist when exists=true",
            f"declared report dirs missing: {source_missing_declared_present}",
            fail_level="WARN",
        )

        acceptance = state_obj.get("acceptance_semantics", {})
        acceptance_statuses = acceptance.get("statuses", []) if isinstance(acceptance, dict) else []
        if not isinstance(acceptance_statuses, list):
            acceptance_statuses = []
        missing_acceptance = sorted(ALLOWED_STATUSES - {str(item) for item in acceptance_statuses})
        add_check(
            checks,
            warnings,
            blockers,
            "acceptance_semantics_status_coverage",
            not missing_acceptance,
            "acceptance semantics include required status vocabulary",
            f"acceptance semantics missing statuses: {missing_acceptance}",
        )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_version": "0.1",
        "task_id": task_id,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "state_path": state_path.relative_to(repo_root).as_posix() if state_path.exists() else str(state_path),
        "state_schema_path": schema_path.relative_to(repo_root).as_posix() if schema_path.exists() else str(schema_path),
        "timeline_schema_path": (
            timeline_schema_path.relative_to(repo_root).as_posix() if timeline_schema_path.exists() else str(timeline_schema_path)
        ),
        "status_rules_path": status_rules_path.relative_to(repo_root).as_posix() if status_rules_path.exists() else str(status_rules_path),
        "report_dir": report_dir.relative_to(repo_root).as_posix() if report_dir.exists() else str(report_dir),
        "no_fake_green_note": "PASS_STRICT is only accepted with explicit evidence references in timeline events.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"validator_verdict={verdict}")
    print(f"validator_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
