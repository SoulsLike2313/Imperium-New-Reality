#!/usr/bin/env python3
"""Build foundation-only read-only Servitor Session View state from existing NewGen artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-SERVITOR-SESSION-VIEW-VM2-V0_1"
REQUIRED_STARTING_HEAD_DEFAULT = "4a4c6cc842ef1658041aeea286230b7425908834"
MODE = "FOUNDATION_READ_ONLY_SERVITOR_SESSION_VIEW"
SESSION_ID = "SERVITOR-SESSION-VIEW-VM2-V0_1"
NEXT_REQUIRED_STEP = "TASK-20260523-NEWGEN-SANCTUM-OWNER-QUESTION-GATE-VM2-OR-VM3-V0_1"

CURRENT_TRUTH_REL = "IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json"
REPORT_STATUS_INDEX_REL = "IMPERIUM_NEW_GENERATION/TRUTH/REPORT_STATUS_INDEX_V0_1.json"
EVIDENCE_MAP_UNIFIED_REL = "IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_MAP_UNIFIED_V0_1.json"
PARTIAL_ACCEPTANCE_MAP_REL = "IMPERIUM_NEW_GENERATION/TRUTH/PARTIAL_ACCEPTANCE_MAP_V0_1.json"
SERVITOR_STATUS_RULES_REL = "IMPERIUM_NEW_GENERATION/TRUTH/SERVITOR_SESSIONS/SERVITOR_SESSION_STATUS_RULES_V0_1.json"
TIMELINE_EVENT_SCHEMA_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/servitor_session_timeline_event.schema.json"

ALLOWED_STATUSES = [
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
]

SOURCE_REPORT_TOKENS: dict[str, str] = {
    "action_layer_hardening": "SANCTUM-ACTION-LAYER-HARDENING",
    "current_truth_root_report_index": "CURRENT-TRUTH-ROOT-REPORT-INDEX",
    "evidence_map_unified": "PQG-EVIDENCE-MAP-UNIFIED",
    "partial_acceptance_map": "PQG-PARTIAL-ACCEPTANCE-MAP",
    "action_rollback_contract": "ACTION-ROLLBACK-CONTRACT",
    "negative_test_mutation_check": "NEGATIVE-TEST-MUTATION-CHECK",
    "organ_dialogue_demo": "SANCTUM-ORGAN-DIALOGUE-DEMO",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def run_git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "UNKNOWN"
    return proc.stdout.strip()


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def parse_utc(raw: str | None) -> dt.datetime | None:
    if not raw or not isinstance(raw, str):
        return None
    value = raw.strip()
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def fmt_utc(value: dt.datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def map_status(raw_status: Any) -> str:
    value = str(raw_status or "").strip().upper()
    if value in ALLOWED_STATUSES:
        return value
    if value in {"PASS", "PROVED", "OK"}:
        return "PASS_STRICT"
    if value in {"WARN", "WARNING", "READY_WITH_WARNINGS", "STRONG"}:
        return "PASS_WITH_WARN"
    if value in {"PARTIAL"}:
        return "PARTIAL_ACCEPTED"
    if value in {"PARTIAL_BLOCK", "PARTIAL_BLOCKED"}:
        return "PARTIAL_BLOCKED"
    if value in {"FOUNDATION", "FOUNDATION_READY", "FOUNDATION_ONLY"}:
        return "FOUNDATION_ONLY"
    if value in {"MISSING", "MISSING_PREREQUISITE"}:
        return "MISSING"
    if value in {"NOT_READY"}:
        return "NOT_READY"
    if value in {"STALE"}:
        return "STALE"
    if value in {"BLOCK", "BLOCKED", "ERROR", "REJECTED", "NOT_ALLOWED", "BLOCKED_NEEDS_OWNER"}:
        return "BLOCKED"
    return "UNKNOWN"


def report_generated_at(report_dir: Path, final_receipt: dict[str, Any] | None, validator: dict[str, Any] | None) -> str:
    for payload in [final_receipt, validator]:
        if not isinstance(payload, dict):
            continue
        for key in ["generated_at_utc", "timestamp_utc", "created_at_utc"]:
            parsed = parse_utc(str(payload.get(key, "")))
            if parsed:
                return fmt_utc(parsed)
    return fmt_utc(dt.datetime.fromtimestamp(report_dir.stat().st_mtime, tz=dt.timezone.utc))


def find_latest_report_dir(repo_root: Path, token: str) -> Path | None:
    reports_root = repo_root / "IMPERIUM_NEW_GENERATION/REPORTS"
    if not reports_root.exists():
        return None
    candidates = [path for path in reports_root.glob("TASK-*") if path.is_dir() and token in path.name]
    if not candidates:
        return None
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0]


def report_status_from_payloads(final_receipt: dict[str, Any] | None, validator: dict[str, Any] | None) -> str:
    if isinstance(final_receipt, dict):
        for key in ["status", "verdict", "overall_status"]:
            value = final_receipt.get(key)
            if value:
                return map_status(value)
    if isinstance(validator, dict):
        for key in ["verdict", "status"]:
            value = validator.get(key)
            if value:
                return map_status(value)
    return "UNKNOWN"


def report_evidence_refs(repo_root: Path, report_dir: Path) -> list[str]:
    refs: list[str] = []
    for name in ["FINAL_RECEIPT.json", "VALIDATOR_REPORT.json", "STEP_PROOF_RECORDS.jsonl"]:
        path = report_dir / name
        if path.exists():
            refs.append(relpath(path, repo_root))
    return refs


def load_source_reports(repo_root: Path, warnings: list[str]) -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for key, token in SOURCE_REPORT_TOKENS.items():
        report_dir = find_latest_report_dir(repo_root, token)
        if report_dir is None:
            warnings.append(f"MISSING_EXPECTED_CONTEXT:{key}:{token}")
            sources[key] = {
                "report_dir": f"IMPERIUM_NEW_GENERATION/REPORTS/<TASK-*{token}*>",
                "exists": False,
                "status": "MISSING",
                "generated_at_utc": "UNKNOWN",
                "evidence_refs": [],
                "notes": ["MISSING_EXPECTED_CONTEXT"],
            }
            continue

        final_receipt = load_json(report_dir / "FINAL_RECEIPT.json")
        validator = load_json(report_dir / "VALIDATOR_REPORT.json")
        status = report_status_from_payloads(final_receipt, validator)
        evidence_refs = report_evidence_refs(repo_root, report_dir)
        notes: list[str] = []

        if status == "PASS_STRICT" and not evidence_refs:
            status = "PASS_WITH_WARN"
            notes.append("PASS_WITHOUT_EVIDENCE_DOWNGRADED")
            warnings.append(f"{key}:PASS_WITHOUT_EVIDENCE_DOWNGRADED")

        generated_at = report_generated_at(report_dir, final_receipt, validator)
        sources[key] = {
            "report_dir": relpath(report_dir, repo_root),
            "exists": True,
            "status": status,
            "generated_at_utc": generated_at,
            "evidence_refs": evidence_refs,
            "notes": notes,
        }
    return sources


def step_timestamp(step: dict[str, Any], fallback: dt.datetime, offset: int) -> str:
    for key in ["timestamp_utc", "generated_at_utc", "ts_utc", "time_utc", "created_at_utc"]:
        parsed = parse_utc(str(step.get(key, "")))
        if parsed:
            return fmt_utc(parsed)
    return fmt_utc(fallback + dt.timedelta(seconds=offset))


def is_rerun_step(step_name: str) -> bool:
    upper = step_name.upper()
    rerun_markers = ["RERUN", "RETRY", "RECHECK", "POST_CLOSURE", "REFRESH", "REPAIR"]
    return any(marker in upper for marker in rerun_markers)


def normalize_evidence_field(step: dict[str, Any], source_path: str) -> list[str]:
    out: list[str] = []
    for key in ["evidence", "basis"]:
        value = step.get(key)
        if isinstance(value, list):
            out.extend(str(item) for item in value if str(item).strip())
        elif isinstance(value, str) and value.strip():
            out.append(value.strip())
    if not out:
        out.append(source_path)
    return out


def timeline_from_step_proofs(
    repo_root: Path,
    source_reports: dict[str, dict[str, Any]],
    session_id: str,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    index = 1
    for source_key, info in source_reports.items():
        if not info.get("exists"):
            continue
        report_dir = repo_root / str(info["report_dir"])
        step_path = report_dir / "STEP_PROOF_RECORDS.jsonl"
        rows = load_jsonl(step_path)
        if not rows:
            continue

        fallback = parse_utc(str(info.get("generated_at_utc", ""))) or dt.datetime.now(dt.timezone.utc)
        rerun_counter = 0
        for row_idx, row in enumerate(rows):
            step_name = str(row.get("step", f"STEP_{row_idx + 1}")).strip() or f"STEP_{row_idx + 1}"
            raw_status = row.get("status") or row.get("self_verdict") or "UNKNOWN"
            status = map_status(raw_status)
            timestamp = step_timestamp(row, fallback, row_idx)
            run_kind = "RERUN" if is_rerun_step(step_name) else "RUN"
            run_id = f"{source_key}-run-001"
            rerun_id = ""
            if run_kind == "RERUN":
                rerun_counter += 1
                rerun_id = f"{source_key}-rerun-{rerun_counter:03d}"
            source_path = relpath(step_path, repo_root)
            evidence_refs = normalize_evidence_field(row, source_path)
            summary = f"{source_key}:{step_name}"

            events.append(
                {
                    "event_id": f"EVT-{index:04d}",
                    "timestamp_utc": timestamp,
                    "event_type": "STEP_PROOF",
                    "status": status,
                    "task_id": str(row.get("task_id", source_key)),
                    "session_id": session_id,
                    "run_id": run_id,
                    "rerun_id": rerun_id,
                    "run_kind": run_kind,
                    "summary": summary,
                    "source_path": source_path,
                    "evidence_refs": evidence_refs,
                    "notes": [f"source_report={source_key}"],
                }
            )
            index += 1
    return events


def timeline_from_action_logs(repo_root: Path, source_reports: dict[str, dict[str, Any]], session_id: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    source = source_reports.get("action_layer_hardening", {})
    if not source.get("exists"):
        return events
    report_dir = repo_root / str(source["report_dir"])
    results_dir = report_dir / "ACTION_LOGS" / "RESULTS"
    if not results_dir.exists():
        return events

    items: list[tuple[dt.datetime, dict[str, Any], Path]] = []
    for path in sorted(results_dir.glob("*.json")):
        payload = load_json(path)
        if payload is None:
            continue
        parsed = parse_utc(str(payload.get("started_at_utc", ""))) or parse_utc(str(payload.get("finished_at_utc", "")))
        if parsed is None:
            parsed = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc)
        items.append((parsed, payload, path))

    if not items:
        return events

    grouped: dict[str, list[tuple[dt.datetime, dict[str, Any], Path]]] = {}
    for parsed, payload, path in items:
        key = fmt_utc(parsed)
        grouped.setdefault(key, []).append((parsed, payload, path))

    sorted_keys = sorted(grouped.keys())
    index = 1
    for run_idx, time_key in enumerate(sorted_keys, start=1):
        bucket = grouped[time_key]
        run_kind = "RUN" if run_idx == 1 else "RERUN"
        rerun_id = "" if run_kind == "RUN" else f"action-rerun-{run_idx - 1:03d}"
        for _, payload, path in sorted(bucket, key=lambda item: str(item[1].get("action_id", ""))):
            status = map_status(payload.get("status", "UNKNOWN"))
            action_id = str(payload.get("action_id", "UNKNOWN_ACTION"))
            result_state = str((payload.get("state_model") or {}).get("result_state", "UNKNOWN"))
            summary = f"{action_id} -> {status} ({result_state})"
            evidence_refs = [str(item) for item in payload.get("evidence_refs", []) if str(item).strip()]
            if not evidence_refs:
                evidence_refs = [relpath(path, repo_root)]

            events.append(
                {
                    "event_id": f"ACT-{index:04d}",
                    "timestamp_utc": time_key,
                    "event_type": "ACTION_RESULT",
                    "status": status,
                    "task_id": str(payload.get("task_id", "")),
                    "session_id": session_id,
                    "run_id": f"action-run-{run_idx:03d}",
                    "rerun_id": rerun_id,
                    "run_kind": run_kind,
                    "summary": summary,
                    "source_path": relpath(path, repo_root),
                    "evidence_refs": evidence_refs,
                    "notes": [f"action_status={payload.get('action_status', 'UNKNOWN')}"],
                }
            )
            index += 1
    return events


def build_organ_dialogue(
    repo_root: Path,
    source_reports: dict[str, dict[str, Any]],
    warnings: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fallback = {
        "task_id": "UNKNOWN",
        "thread_id": "UNKNOWN",
        "request_count": 0,
        "response_count": 0,
        "warnings_count": 0,
        "last_event": "NOT_READY",
        "last_event_at_utc": "UNKNOWN",
        "foundation_only": True,
        "live_autonomy": False,
        "response_verdict_counts": {},
        "references": [],
    }

    source = source_reports.get("organ_dialogue_demo", {})
    if not source.get("exists"):
        warnings.append("MISSING_EXPECTED_CONTEXT:organ_dialogue_demo")
        return fallback, []

    report_dir = repo_root / str(source["report_dir"])
    run_report_path = report_dir / "ORGAN_DIALOGUE_DEMO_RUN_REPORT.json"
    run_report = load_json(run_report_path)
    if run_report is None:
        warnings.append("MISSING_EXPECTED_CONTEXT:ORGAN_DIALOGUE_DEMO_RUN_REPORT")
        return fallback, []

    paths = run_report.get("paths", {})
    if not isinstance(paths, dict):
        paths = {}
    thread_rel = str(paths.get("thread", "")).strip()
    events_rel = str(paths.get("events", "")).strip()
    thread_payload = load_json(repo_root / thread_rel) if thread_rel else None

    response_verdict_counts: Counter[str] = Counter()
    summary: dict[str, Any] = {}
    if isinstance(thread_payload, dict):
        for response in thread_payload.get("responses", []):
            if isinstance(response, dict):
                response_verdict_counts[str(response.get("verdict", "UNKNOWN"))] += 1
        summary = thread_payload.get("summary", {}) if isinstance(thread_payload.get("summary"), dict) else {}

    organ_dialogue = {
        "task_id": str(run_report.get("task_id", "UNKNOWN")),
        "thread_id": str(run_report.get("thread_id", "UNKNOWN")),
        "request_count": int(run_report.get("request_count", 0)),
        "response_count": int(run_report.get("response_count", 0)),
        "warnings_count": int(run_report.get("warnings_count", 0)),
        "last_event": str(summary.get("last_event", "NOT_READY")),
        "last_event_at_utc": str(summary.get("last_event_at_utc", "UNKNOWN")),
        "foundation_only": True,
        "live_autonomy": False,
        "response_verdict_counts": dict(response_verdict_counts),
        "references": [
            relpath(run_report_path, repo_root),
            thread_rel,
            events_rel,
        ],
    }

    timeline_events: list[dict[str, Any]] = []
    if events_rel and (repo_root / events_rel).exists():
        rows = load_jsonl(repo_root / events_rel)
        for idx, row in enumerate(rows, start=1):
            event_type = str(row.get("event_type", "ORGAN_DIALOGUE_EVENT"))
            note = str(row.get("note", ""))
            verdict = "FOUNDATION_ONLY"
            if "Verdict=" in note:
                verdict = map_status(note.split("Verdict=", 1)[1].strip())
            elif event_type == "THREAD_SUMMARY_UPDATED":
                verdict = "PARTIAL_ACCEPTED"

            timeline_events.append(
                {
                    "event_id": f"OD-{idx:04d}",
                    "timestamp_utc": str(row.get("timestamp_utc", organ_dialogue["last_event_at_utc"])),
                    "event_type": "ORGAN_DIALOGUE_EVENT",
                    "status": verdict,
                    "task_id": organ_dialogue["task_id"],
                    "session_id": SESSION_ID,
                    "run_id": "organ-dialogue-run-001",
                    "rerun_id": "",
                    "run_kind": "RUN",
                    "summary": f"{event_type}:{row.get('actor', 'UNKNOWN')}",
                    "source_path": events_rel,
                    "evidence_refs": [str(row.get("payload_ref", events_rel))],
                    "notes": [note] if note else [],
                }
            )

    return organ_dialogue, timeline_events


def build_evidence_summary(
    current_truth: dict[str, Any] | None,
    report_status_index: dict[str, Any] | None,
    evidence_map_unified: dict[str, Any] | None,
) -> dict[str, Any]:
    report_entries = report_status_index.get("entries", []) if isinstance(report_status_index, dict) else []
    evidence_records = evidence_map_unified.get("records", []) if isinstance(evidence_map_unified, dict) else []

    critical_refs: list[str] = []
    if isinstance(current_truth, dict):
        action_layer = current_truth.get("action_layer_status", {})
        if isinstance(action_layer, dict):
            refs = action_layer.get("evidence_refs", [])
            if isinstance(refs, list):
                critical_refs.extend(str(item) for item in refs if str(item).strip())

    if not critical_refs:
        critical_refs = [
            CURRENT_TRUTH_REL,
            REPORT_STATUS_INDEX_REL,
            EVIDENCE_MAP_UNIFIED_REL,
        ]

    return {
        "evidence_map_unified_path": EVIDENCE_MAP_UNIFIED_REL,
        "evidence_record_count": len(evidence_records),
        "report_status_index_path": REPORT_STATUS_INDEX_REL,
        "report_entry_count": len(report_entries),
        "critical_refs": critical_refs[:24],
    }


def build_action_layer_snapshot(
    current_truth: dict[str, Any] | None,
    action_events: list[dict[str, Any]],
) -> dict[str, Any]:
    action_layer = current_truth.get("action_layer_status", {}) if isinstance(current_truth, dict) else {}
    if not isinstance(action_layer, dict):
        action_layer = {}

    component_status = action_layer.get("components", {})
    if not isinstance(component_status, dict):
        component_status = {}

    mapped_components = {key: map_status(value) for key, value in component_status.items()}
    overall_status = map_status(action_layer.get("overall_status", "FOUNDATION_ONLY"))

    status_counts: Counter[str] = Counter()
    result_counts: Counter[str] = Counter()
    for event in action_events:
        status_counts[str(event.get("status", "UNKNOWN"))] += 1
        summary = str(event.get("summary", ""))
        if "(" in summary and summary.endswith(")"):
            result_state = summary.split("(", 1)[1][:-1]
            result_counts[result_state] += 1

    evidence_refs = action_layer.get("evidence_refs", [])
    if not isinstance(evidence_refs, list):
        evidence_refs = []

    known_limitations = action_layer.get("known_limitations", [])
    if not isinstance(known_limitations, list):
        known_limitations = []

    return {
        "overall_status": overall_status,
        "component_status": mapped_components,
        "action_log_status_counts": dict(status_counts),
        "action_log_result_state_counts": dict(result_counts),
        "known_limitations": [str(item) for item in known_limitations],
        "evidence_refs": [str(item) for item in evidence_refs if str(item).strip()],
    }


def build_acceptance_semantics(partial_acceptance_map: dict[str, Any] | None, warnings: list[str]) -> dict[str, Any]:
    statuses: list[str] = []
    invariants: list[str] = []
    if isinstance(partial_acceptance_map, dict):
        raw_statuses = partial_acceptance_map.get("statuses", [])
        if isinstance(raw_statuses, list):
            for item in raw_statuses:
                if isinstance(item, dict):
                    value = str(item.get("status", "")).strip()
                    if value:
                        statuses.append(value)
        raw_invariants = partial_acceptance_map.get("no_fake_green_invariants", [])
        if isinstance(raw_invariants, list):
            invariants = [str(item) for item in raw_invariants if str(item).strip()]

    if not statuses:
        statuses = ALLOWED_STATUSES[:]
        warnings.append("PARTIAL_ACCEPTANCE_STATUS_SOURCE_MISSING")
    if not invariants:
        invariants = [
            "NO_EVIDENCE_NO_STRICT_PASS",
            "UNKNOWN_CANNOT_CONTINUE_AS_GREEN",
        ]
        warnings.append("PARTIAL_ACCEPTANCE_INVARIANTS_SOURCE_MISSING")

    return {
        "status_rules_path": SERVITOR_STATUS_RULES_REL,
        "statuses": statuses,
        "invariants": invariants,
    }


def sort_timeline(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(event: dict[str, Any]) -> tuple[dt.datetime, str]:
        parsed = parse_utc(str(event.get("timestamp_utc", ""))) or dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
        return parsed, str(event.get("event_id", ""))

    return sorted(events, key=key)


def timeline_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: Counter[str] = Counter()
    run_events = 0
    rerun_events = 0
    for event in events:
        status_counts[str(event.get("status", "UNKNOWN"))] += 1
        kind = str(event.get("run_kind", "RUN"))
        if kind == "RERUN":
            rerun_events += 1
        else:
            run_events += 1
    return {
        "total_events": len(events),
        "run_events": run_events,
        "rerun_events": rerun_events,
        "status_counts": dict(status_counts),
    }


def build_state(repo_root: Path, task_id: str, required_starting_head: str) -> dict[str, Any]:
    warnings: list[str] = []
    source_reports = load_source_reports(repo_root, warnings)

    current_truth = load_json(repo_root / CURRENT_TRUTH_REL)
    report_status_index = load_json(repo_root / REPORT_STATUS_INDEX_REL)
    evidence_map_unified = load_json(repo_root / EVIDENCE_MAP_UNIFIED_REL)
    partial_acceptance_map = load_json(repo_root / PARTIAL_ACCEPTANCE_MAP_REL)

    if current_truth is None:
        warnings.append("MISSING_EXPECTED_CONTEXT:CURRENT_TRUTH_ROOT_V0_1.json")
    if report_status_index is None:
        warnings.append("MISSING_EXPECTED_CONTEXT:REPORT_STATUS_INDEX_V0_1.json")
    if evidence_map_unified is None:
        warnings.append("MISSING_EXPECTED_CONTEXT:EVIDENCE_MAP_UNIFIED_V0_1.json")
    if partial_acceptance_map is None:
        warnings.append("MISSING_EXPECTED_CONTEXT:PARTIAL_ACCEPTANCE_MAP_V0_1.json")

    step_events = timeline_from_step_proofs(repo_root, source_reports, SESSION_ID)
    action_events = timeline_from_action_logs(repo_root, source_reports, SESSION_ID)
    organ_dialogue, organ_events = build_organ_dialogue(repo_root, source_reports, warnings)

    timeline_events = sort_timeline(step_events + action_events + organ_events)
    timeline = {
        "events": timeline_events,
        "summary": timeline_summary(timeline_events),
    }

    git_head = run_git(repo_root, "rev-parse", "HEAD")
    git_branch = run_git(repo_root, "branch", "--show-current")
    git_status = run_git(repo_root, "status", "--short")

    state = {
        "schema_id": "SERVITOR_SESSION_VIEW_STATE_V0_1",
        "task_id": task_id,
        "mode": MODE,
        "generated_at_utc": utc_now(),
        "session": {
            "session_id": SESSION_ID,
            "view_task_id": task_id,
            "required_starting_head": required_starting_head,
            "current_head": git_head,
            "branch": git_branch,
            "worktree_dirty": bool(git_status),
            "runbook": "Build from existing NewGen artifacts only. No live autonomy.",
        },
        "session_status": "FOUNDATION_ONLY",
        "truth_flags": {
            "read_only": True,
            "foundation_only": True,
            "live_autonomous_execution": False,
            "production_ready": False,
        },
        "source_reports": source_reports,
        "acceptance_semantics": build_acceptance_semantics(partial_acceptance_map, warnings),
        "action_layer": build_action_layer_snapshot(current_truth, action_events),
        "organ_dialogue": organ_dialogue,
        "evidence_summary": build_evidence_summary(current_truth, report_status_index, evidence_map_unified),
        "timeline": timeline,
        "warnings": sorted(set(warnings)),
        "limitations": [
            "Foundation-only read model from existing receipts and reports.",
            "No live autonomous execution, no production readiness claim.",
            "Timeline reflects artifact history and rerun markers, not runtime orchestration.",
            "Statuses are normalized to strict no-fake-green semantics.",
        ],
        "forbidden_claims": [
            "LIVE_AUTONOMOUS_EXECUTION",
            "PRODUCTION_READY",
            "LIVE_ORGAN_INTELLIGENCE",
            "UNBOUNDED_AGENT_CONTROL",
        ],
        "next_required_step": NEXT_REQUIRED_STEP,
        "references": {
            "current_truth_root_path": CURRENT_TRUTH_REL,
            "report_status_index_path": REPORT_STATUS_INDEX_REL,
            "evidence_map_unified_path": EVIDENCE_MAP_UNIFIED_REL,
            "partial_acceptance_map_path": PARTIAL_ACCEPTANCE_MAP_REL,
            "status_rules_path": SERVITOR_STATUS_RULES_REL,
            "timeline_event_schema_path": TIMELINE_EVENT_SCHEMA_REL,
        },
    }
    return state


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_output = (
        default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/servitor_session_view_state.generated.json"
    )

    parser = argparse.ArgumentParser(description="Build Servitor Session View state.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--required-starting-head", default=REQUIRED_STARTING_HEAD_DEFAULT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    output = args.output.resolve()

    state = build_state(repo_root, str(args.task_id), str(args.required_starting_head))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"state_written={relpath(output, repo_root)}")
    print(f"timeline_events={len(state.get('timeline', {}).get('events', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
