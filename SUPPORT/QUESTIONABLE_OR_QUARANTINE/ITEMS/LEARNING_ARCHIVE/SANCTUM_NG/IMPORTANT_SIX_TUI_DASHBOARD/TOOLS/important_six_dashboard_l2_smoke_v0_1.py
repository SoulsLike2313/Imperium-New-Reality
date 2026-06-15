#!/usr/bin/env python3
"""API smoke for Important Six dashboard L2 action surface.

Default mode is strictly read-only and does not call mutating POST routes.
Mutation smoke is opt-in via --allow-mutation-smoke.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID = "TASK-NEWGEN-VERIFICATION-SPINE-CONVERGENCE-PC-V0_1"

PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
FAIL = "FAIL"
BLOCKED = "BLOCKED"
CANONICAL = {PASS, PASS_WITH_WARNINGS, FAIL, BLOCKED}

REQUIRED_ACTIONS = [
    "ADMIN_FULL_NEWGEN_FILE_AUDIT",
    "ADMIN_BUILD_CONTINUITY_PACK",
    "ADMIN_EVIDENCE_REPORT_MAP",
    "TRANSFER_SEND_TASKPACK_VM2_DRY_RUN",
    "TRANSFER_SEND_TASKPACK_VM3_DRY_RUN",
    "TRANSFER_FETCH_REPORT_VM2_DRY_RUN",
    "TRANSFER_FETCH_REPORT_VM3_DRY_RUN",
    "MECHANICUS_CHECK_REQUIRED_TOOLS",
    "MECHANICUS_CHECK_SCRIPTS_VALIDATORS",
    "INQUISITION_REPO_HYGIENE_AUDIT",
    "INQUISITION_FAKE_GREEN_RISK_SCAN",
    "ASTRONOMICON_REGISTER_TASK_DRAFT",
    "DIFF_COMPARE_HEADS",
    "OWNER_RECORD_DIFF_DECISION",
    "OWNER_QUESTIONS_LIST",
    "OWNER_RECORD_NOTE_OR_DECISION",
]

REQUIRED_GROUPS = {
    "Administratum",
    "Transfer Zone",
    "Mechanicus",
    "Inquisition",
    "Astronomicon",
    "Diff / Approval",
    "Owner Intent / Questions",
}

REGISTRY_REQUIRED_FIELDS = {
    "action_id",
    "owner_organ",
    "label_ru",
    "description",
    "safety_class",
    "writes_allowed",
    "output_root",
    "handler",
    "dry_run_supported",
    "receipt_required",
    "dashboard_button_group",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_verdict(value: str | None) -> str:
    upper = str(value or "").strip().upper()
    if upper in {PASS, "OK"}:
        return PASS
    if upper in {PASS_WITH_WARNINGS, "WARN", "WARNING", "PARTIAL"}:
        return PASS_WITH_WARNINGS
    if upper in {FAIL, "FAILED", "ERROR"}:
        return FAIL
    if upper in {BLOCKED, "BLOCK"}:
        return BLOCKED
    return BLOCKED


def merge_verdict(current: str, incoming: str) -> str:
    order = {PASS: 0, PASS_WITH_WARNINGS: 1, FAIL: 2, BLOCKED: 3}
    return incoming if order[incoming] > order[current] else current


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[4]
    default_report_root = (
        repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "REPORTS"
        / "TASK-NEWGEN-VERIFICATION-SPINE-CONVERGENCE-PC-V0_1"
    )
    parser = argparse.ArgumentParser(description="Run Important Six dashboard L2 API smoke.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8766")
    parser.add_argument("--timeout-sec", type=float, default=70.0)
    parser.add_argument("--report-root", type=Path, default=default_report_root)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--allow-mutation-smoke",
        action="store_true",
        help="Opt-in: run mutating POST routes and action runs.",
    )
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_json(url: str, timeout_sec: float) -> dict[str, Any] | list[Any]:
    with urllib.request.urlopen(url, timeout=timeout_sec) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def post_json(url: str, payload: dict[str, Any], timeout_sec: float) -> tuple[int, dict[str, Any] | list[Any]]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            raw = response.read().decode("utf-8")
            return int(response.status), json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload_json = json.loads(raw)
        except json.JSONDecodeError:
            payload_json = {"raw_error": raw}
        return int(exc.code), payload_json


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[4]
    base_url = args.base_url.rstrip("/")
    report_root = args.report_root.resolve()
    report_root.mkdir(parents=True, exist_ok=True)

    output_path = args.output.resolve() if args.output else report_root / "read_only_smoke_report.json"
    registry_validation_path = report_root / "action_registry_validation_report.json"
    sample_receipts_index_path = report_root / "sample_action_receipts_index.json"
    json_parse_report_path = report_root / "json_parse_validation_report.json"

    steps: list[dict[str, Any]] = []
    blocked_steps: list[str] = []
    failed_steps: list[str] = []
    warning_steps: list[str] = []
    verdict = PASS

    def add_step(name: str, status: str, details: Any) -> None:
        nonlocal verdict
        normalized = normalize_verdict(status)
        steps.append({"step": name, "status": normalized, "details": details})
        verdict = merge_verdict(verdict, normalized)
        if normalized == BLOCKED:
            blocked_steps.append(name)
        elif normalized == FAIL:
            failed_steps.append(name)
        elif normalized == PASS_WITH_WARNINGS:
            warning_steps.append(name)

    # Base endpoint checks (read-only).
    for endpoint in ("/api/status", "/api/actions", "/api/action-history", "/api/owner-questions", "/api/diff/status"):
        url = f"{base_url}{endpoint}"
        try:
            payload = fetch_json(url, args.timeout_sec)
            add_step(f"get_{endpoint}", PASS, {"url": url, "json_type": type(payload).__name__})
            if endpoint == "/api/actions" and isinstance(payload, dict):
                groups = payload.get("groups", {})
                group_names = set(groups.keys()) if isinstance(groups, dict) else set()
                missing_groups = sorted(REQUIRED_GROUPS - group_names)
                add_step(
                    "required_groups_check",
                    PASS if not missing_groups else FAIL,
                    {"found": sorted(group_names), "missing": missing_groups},
                )
        except Exception as exc:  # noqa: BLE001
            add_step(f"get_{endpoint}", BLOCKED, {"url": url, "error": str(exc)})

    # Registry fields and required actions from /api/actions.
    registry_actions: list[dict[str, Any]] = []
    try:
        api_actions = fetch_json(f"{base_url}/api/actions", args.timeout_sec)
        if isinstance(api_actions, dict) and isinstance(api_actions.get("groups"), dict):
            for group, items in api_actions["groups"].items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    if isinstance(item, dict):
                        entry = dict(item)
                        entry["dashboard_button_group"] = entry.get("dashboard_button_group", group)
                        registry_actions.append(entry)
        add_step("collect_registry_actions", PASS, {"count": len(registry_actions)})
    except Exception as exc:  # noqa: BLE001
        add_step("collect_registry_actions", BLOCKED, str(exc))

    found_action_ids = {str(entry.get("action_id")) for entry in registry_actions}
    missing_actions = [action_id for action_id in REQUIRED_ACTIONS if action_id not in found_action_ids]
    add_step(
        "required_actions_check",
        PASS if not missing_actions else FAIL,
        {"found_count": len(found_action_ids), "missing_actions": missing_actions},
    )

    registry_checks: list[dict[str, Any]] = []
    registry_has_fail = False
    for entry in registry_actions:
        action_id = str(entry.get("action_id", "UNKNOWN"))
        missing_fields = sorted(REGISTRY_REQUIRED_FIELDS - set(entry.keys()))
        status = PASS if not missing_fields else FAIL
        if status == FAIL:
            registry_has_fail = True
        registry_checks.append({"action_id": action_id, "status": status, "missing_fields": missing_fields})

    read_only_actions = sorted(
        str(entry.get("action_id"))
        for entry in registry_actions
        if entry.get("writes_allowed") is False
    )
    write_actions = sorted(
        str(entry.get("action_id"))
        for entry in registry_actions
        if entry.get("writes_allowed") is True
    )

    registry_validation_payload = {
        "schema_id": "important_six_action_registry_validation_report_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": FAIL if registry_has_fail else PASS,
        "read_only_actions": read_only_actions,
        "write_actions": write_actions,
        "checks": registry_checks,
    }
    write_json(registry_validation_path, registry_validation_payload)

    receipt_paths: list[str] = []
    payloads_by_action = {
        "OWNER_RECORD_DIFF_DECISION": {"decision": "NEEDS_REWORK", "note_ru": "Smoke mutation mode."},
        "OWNER_RECORD_NOTE_OR_DECISION": {
            "organ": "OFFICIO_AGENTIS",
            "severity": "MEDIUM",
            "question": "Mutation smoke note",
            "required_decision": "OWNER_REVIEW",
            "note_ru": "Smoke mutation mode.",
        },
    }

    # Mutation mode is explicit; default mode is read-only and skips POST calls.
    if args.allow_mutation_smoke:
        add_step(
            "mutation_mode_enabled",
            PASS_WITH_WARNINGS,
            {"note": "Mutating routes enabled explicitly by --allow-mutation-smoke."},
        )
        for action_id in REQUIRED_ACTIONS:
            payload = payloads_by_action.get(action_id, {})
            url = f"{base_url}/api/actions/{action_id}/run"
            try:
                status_code, result = post_json(url, payload, args.timeout_sec)
                result_status = BLOCKED
                if isinstance(result, dict):
                    result_status = normalize_verdict(str(result.get("status", BLOCKED)))
                    receipt_path = result.get("receipt_path")
                    if isinstance(receipt_path, str):
                        receipt_paths.append(receipt_path)

                if status_code >= 500:
                    add_step(f"run_{action_id}", FAIL, {"http_status": status_code, "result": result})
                elif status_code >= 400:
                    add_step(f"run_{action_id}", BLOCKED, {"http_status": status_code, "result": result})
                else:
                    add_step(f"run_{action_id}", result_status, {"http_status": status_code, "result": result})
            except Exception as exc:  # noqa: BLE001
                add_step(f"run_{action_id}", BLOCKED, {"error": str(exc)})

            try:
                last_payload = fetch_json(f"{base_url}/api/actions/{action_id}/last-result", args.timeout_sec)
                ok = isinstance(last_payload, dict) and last_payload.get("action_id") == action_id
                add_step(f"last_{action_id}", PASS if ok else FAIL, last_payload)
            except Exception as exc:  # noqa: BLE001
                add_step(f"last_{action_id}", BLOCKED, {"error": str(exc)})

        try:
            decision_url = f"{base_url}/api/owner-intent/decision"
            status_code, result = post_json(
                decision_url,
                {"decision": "APPROVE", "note_ru": "Smoke mutation mode."},
                args.timeout_sec,
            )
            if status_code >= 500:
                add_step("direct_owner_intent_decision_endpoint", FAIL, {"http_status": status_code, "result": result})
            elif status_code >= 400:
                add_step("direct_owner_intent_decision_endpoint", BLOCKED, {"http_status": status_code, "result": result})
            else:
                status = PASS
                if isinstance(result, dict):
                    status = normalize_verdict(str(result.get("status", PASS)))
                add_step("direct_owner_intent_decision_endpoint", status, {"http_status": status_code, "result": result})
        except Exception as exc:  # noqa: BLE001
            add_step("direct_owner_intent_decision_endpoint", BLOCKED, {"error": str(exc)})
    else:
        add_step(
            "mutation_mode_skipped_default",
            PASS,
            {
                "note": "Default smoke is read-only; all POST action-run and owner decision endpoints were skipped.",
                "skipped_actions": REQUIRED_ACTIONS,
                "skipped_direct_endpoints": ["/api/owner-intent/decision"],
            },
        )

    receipt_records: list[dict[str, Any]] = []
    for rel_path in sorted(set(receipt_paths)):
        abs_path = repo_root / rel_path
        receipt_records.append({"receipt_path": rel_path, "exists": abs_path.exists()})
    sample_receipts_index = {
        "schema_id": "important_six_sample_action_receipts_index_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "mutation_mode": bool(args.allow_mutation_smoke),
        "receipts": receipt_records,
    }
    write_json(sample_receipts_index_path, sample_receipts_index)

    smoke_report = {
        "schema_id": "important_six_dashboard_l2_action_api_smoke_report_v0_2",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "base_url": base_url,
        "mode": "MUTATION_OPT_IN" if args.allow_mutation_smoke else "READ_ONLY_DEFAULT",
        "verdict": verdict,
        "blocked_steps": blocked_steps,
        "failed_steps": failed_steps,
        "warning_steps": warning_steps,
        "steps": steps,
    }
    write_json(output_path, smoke_report)

    parse_checks: list[dict[str, Any]] = []
    for path in (output_path, registry_validation_path, sample_receipts_index_path):
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            parse_checks.append({"path": str(path), "status": PASS, "json_type": type(parsed).__name__})
        except Exception as exc:  # noqa: BLE001
            parse_checks.append({"path": str(path), "status": FAIL, "error": str(exc)})

    parse_verdict = PASS if all(item["status"] == PASS for item in parse_checks) else FAIL
    parse_report = {
        "schema_id": "important_six_dashboard_l2_json_parse_validation_report_v0_2",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": parse_verdict,
        "checks": parse_checks,
    }
    write_json(json_parse_report_path, parse_report)

    if parse_verdict != PASS:
        return 1
    return 0 if verdict in {PASS, PASS_WITH_WARNINGS} else 1


if __name__ == "__main__":
    raise SystemExit(main())

