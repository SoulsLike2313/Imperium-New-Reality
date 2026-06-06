#!/usr/bin/env python3
"""Local file-backed allowlisted action server for Sanctum NG foundation layer."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import uuid
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

TASK_ID_DEFAULT = "TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1"
REQUIRED_STARTING_HEAD_DEFAULT = "573169b9830ecb0322202e33a3e12ca2fc5e3556"
APP_DIR_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/APP"
STATE_PATH_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"
SERVITOR_SESSION_VIEW_STATE_REL = (
    "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/servitor_session_view_state.generated.json"
)
OWNER_QUESTION_GATE_STATE_REL = (
    "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/owner_question_gate_state.generated.json"
)
TRANSFER_CONSOLE_VIEW_STATE_REL = (
    "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json"
)
TRANSFER_CONSOLE_ACTION_RUNNER_REL = (
    "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/transfer_console_action_runner_v0_1.py"
)
TRANSFER_ACTION_RUNNER_REL = (
    "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/TOOLS/transfer_action_runner_v0_1.py"
)
PHASE_REGISTRY_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_PHASE_REGISTRY_V0_1.json"
ACTION_REGISTRY_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/REGISTRY/SANCTUM_NG_ACTION_REGISTRY_V0_1.json"
VALIDATOR_PATH_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_validator.py"
REFRESH_RUNNER_PATH_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_refresh_runner.py"
STATE_SCHEMA_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/sanctum_ng_state.schema.json"

FORBIDDEN_PATHS = [
    "ORGANS/**",
    "SANCTUM/**",
    "IMPERIUM_TEST_VERSION/**",
    "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/**",
    ".git/**",
]

SUMMARY_STATE_SET = {"FOUND", "MISSING", "PARTIAL", "NOT_READY", "STALE", "ERROR"}


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


class ActionLayer:
    def __init__(
        self,
        repo_root: Path,
        task_id: str,
        required_starting_head: str,
        report_dir: Path,
        action_log_dir: Path,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.task_id = task_id
        self.required_starting_head = required_starting_head
        self.report_dir = report_dir.resolve()
        self.action_log_dir = action_log_dir.resolve()
        self.app_dir = (self.repo_root / APP_DIR_REL).resolve()
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.action_log_dir.mkdir(parents=True, exist_ok=True)

    def state_payload(self) -> dict[str, Any]:
        state = load_json(self.repo_root / STATE_PATH_REL)
        if state is None:
            return {
                "schema_id": "SANCTUM_NG_STATE_V0_1",
                "task_id": self.task_id,
                "mode": "READ_ONLY_FOUNDATION",
                "generated_at_utc": "UNKNOWN",
                "warnings": ["STATE_FILE_MISSING_OR_INVALID"],
            }
        return state

    def action_registry(self) -> dict[str, Any]:
        registry = load_json(self.repo_root / ACTION_REGISTRY_REL)
        if registry is None:
            return {
                "schema_id": "SANCTUM_NG_ACTION_REGISTRY_V0_1",
                "task_id": self.task_id,
                "mode": "ACTION_LAYER_FOUNDATION_ONLY",
                "actions": [],
                "warnings": ["ACTION_REGISTRY_MISSING_OR_INVALID"],
            }
        return registry

    def servitor_session_view_payload(self) -> dict[str, Any]:
        payload = load_json(self.repo_root / SERVITOR_SESSION_VIEW_STATE_REL)
        if payload is None:
            return {
                "schema_id": "SERVITOR_SESSION_VIEW_STATE_V0_1",
                "task_id": self.task_id,
                "mode": "FOUNDATION_READ_ONLY_SERVITOR_SESSION_VIEW",
                "status": "MISSING",
                "warnings": ["SERVITOR_SESSION_VIEW_STATE_MISSING_OR_INVALID"],
                "known_limitations": [
                    "Servitor Session View state file is missing or invalid.",
                    "No live autonomy claim is made."
                ],
            }
        return payload

    def owner_question_gate_payload(self) -> dict[str, Any]:
        payload = load_json(self.repo_root / OWNER_QUESTION_GATE_STATE_REL)
        if payload is None:
            return {
                "schema_id": "OWNER_QUESTION_GATE_STATE_V0_1",
                "task_id": self.task_id,
                "mode": "FOUNDATION_READ_ONLY_OWNER_QUESTION_GATE",
                "status": "MISSING",
                "warnings": ["OWNER_QUESTION_GATE_STATE_MISSING_OR_INVALID"],
                "truth_flags": {
                    "read_only": True,
                    "foundation_only": True,
                    "live_owner_channel": False,
                    "owner_answer_write_path": False,
                    "production_ready": False,
                },
                "known_limitations": [
                    "Owner Question Gate state file is missing or invalid.",
                    "No live owner answer channel is claimed.",
                ],
            }
        return payload

    def transfer_console_view_payload(self) -> dict[str, Any]:
        payload = load_json(self.repo_root / TRANSFER_CONSOLE_VIEW_STATE_REL)
        if payload is None:
            return {
                "schema_id": "TRANSFER_CONSOLE_VIEW_STATE_V0_1",
                "task_id": self.task_id,
                "generated_at_utc": "UNKNOWN",
                "claim_boundary": "FOUNDATION_ONLY",
                "contour_cards": [],
                "latest_requests": [],
                "latest_results": [],
                "action_ledger": [],
                "transfer_routes": [],
                "source_refs": [],
                "context_source_mix": {
                    "taskpack_percent": 0,
                    "existing_newgen_repo_percent": 0,
                    "owner_handoff_percent": 0,
                    "organ_registry_percent": 0,
                    "servitor_inference_percent": 0,
                    "external_local_private_percent": 0,
                },
                "truth_labels": [
                    "FOUNDATION_ONLY",
                    "NO_PRODUCTION_REMOTE_ORCHESTRATION",
                ],
                "warnings": ["TRANSFER_CONSOLE_VIEW_STATE_MISSING_OR_INVALID"],
                "known_limitations": [
                    "Transfer Console view state is missing or invalid.",
                    "No production remote orchestration claim is made.",
                ],
            }
        return payload

    def action_map(self) -> dict[str, dict[str, Any]]:
        registry = self.action_registry()
        actions = registry.get("actions", [])
        out: dict[str, dict[str, Any]] = {}
        if isinstance(actions, list):
            for action in actions:
                if isinstance(action, dict):
                    action_id = str(action.get("action_id", "")).strip()
                    if action_id:
                        out[action_id] = action
        return out

    def connection_state_model(self) -> dict[str, Any]:
        return {
            "connection_state": "CONNECTED",
            "connection_states": [
                "CONNECTED",
                "NOT_CONNECTED",
                "UNKNOWN",
                "ACTION_SERVER_NOT_CONNECTED",
            ],
            "action_states": [
                "ACTION_ALLOWED",
                "ACTION_DISABLED",
            ],
            "result_states": [
                "ACTION_RESULT_PASS",
                "ACTION_RESULT_WARN",
                "ACTION_RESULT_BLOCK",
                "ACTION_RESULT_PARTIAL",
            ],
        }

    def _action_availability_state(self, action_status: str) -> str:
        return "ACTION_ALLOWED" if action_status == "WIRED" else "ACTION_DISABLED"

    def _action_result_state(self, status: str) -> str:
        status_upper = status.strip().upper()
        if status_upper == "PASS":
            return "ACTION_RESULT_PASS"
        if status_upper in {"PARTIAL"}:
            return "ACTION_RESULT_PARTIAL"
        if status_upper in {"BLOCK", "NOT_ALLOWED", "ERROR"}:
            return "ACTION_RESULT_BLOCK"
        return "ACTION_RESULT_WARN"

    def _attach_state_model(self, result: dict[str, Any]) -> dict[str, Any]:
        status = str(result.get("status", "WARN"))
        action_status = str(result.get("action_status", "BLOCKED"))
        result["state_model"] = {
            "connection_state": "CONNECTED",
            "action_availability": self._action_availability_state(action_status),
            "result_state": self._action_result_state(status),
            "known_states": self.connection_state_model(),
        }
        return result

    def _load_latest_action_result(self) -> dict[str, Any] | None:
        return load_json(self.action_log_dir / "latest_action_result.json")

    def _run_command(self, cmd: list[str], timeout_seconds: int = 240) -> dict[str, Any]:
        proc = subprocess.run(
            cmd,
            cwd=self.repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
        return {
            "command": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }

    def _request_record(self, action_id: str, requester: str, dry_run: bool, input_payload: dict[str, Any]) -> tuple[str, Path]:
        request_id = f"{utc_now().replace(':', '').replace('-', '')}_{uuid.uuid4().hex[:10]}"
        request_path = self.report_dir / "ACTION_LOGS" / "REQUESTS" / f"{request_id}.json"
        request_payload = {
            "schema_id": "SANCTUM_NG_ACTION_REQUEST_V0_1",
            "task_id": self.task_id,
            "request_id": request_id,
            "action_id": action_id,
            "requested_at_utc": utc_now(),
            "requester": requester,
            "dry_run": dry_run,
            "input": input_payload,
        }
        write_json(request_path, request_payload)
        return request_id, request_path

    def _result_record_path(self, request_id: str) -> Path:
        return self.report_dir / "ACTION_LOGS" / "RESULTS" / f"{request_id}.json"

    def _run_refresh(self) -> dict[str, Any]:
        runner_path = self.repo_root / REFRESH_RUNNER_PATH_REL
        cmd = [
            "python3",
            str(runner_path),
            "--repo-root",
            str(self.repo_root),
            "--task-id",
            self.task_id,
            "--required-starting-head",
            self.required_starting_head,
            "--report-dir",
            str(self.report_dir),
        ]
        run = self._run_command(cmd)
        runner_report = load_json(self.report_dir / "SANCTUM_NG_REFRESH_RUNNER_REPORT.json") or {}
        verdict = str(runner_report.get("verdict", "UNKNOWN"))
        if run["returncode"] != 0:
            status = "BLOCK"
        elif verdict == "PASS":
            status = "PASS"
        else:
            status = "WARN"

        return {
            "status": status,
            "executed_command": cmd,
            "output_summary": f"refresh_returncode={run['returncode']} runner_verdict={verdict}",
            "payload": {
                "runner": run,
                "runner_report": runner_report,
            },
            "evidence_refs": [
                STATE_PATH_REL,
                relpath(self.report_dir / "SANCTUM_NG_REFRESH_RUNNER_REPORT.json", self.repo_root),
                relpath(self.report_dir / "VALIDATOR_REPORT.json", self.repo_root),
            ],
            "known_limitations": [
                "Runs bounded local refresh flow only.",
                "No production backend claim."
            ],
        }

    def _run_validate(self) -> dict[str, Any]:
        validator_path = self.repo_root / VALIDATOR_PATH_REL
        state_path = self.repo_root / STATE_PATH_REL
        schema_path = self.repo_root / STATE_SCHEMA_REL
        output_path = self.report_dir / "VALIDATOR_REPORT.json"

        cmd = [
            "python3",
            str(validator_path),
            "--repo-root",
            str(self.repo_root),
            "--state",
            str(state_path),
            "--schema",
            str(schema_path),
            "--report-dir",
            str(self.report_dir),
            "--output",
            str(output_path),
            "--task-id",
            self.task_id,
        ]
        run = self._run_command(cmd)
        validator_report = load_json(output_path) or {}
        verdict = str(validator_report.get("verdict", "UNKNOWN"))
        if run["returncode"] != 0:
            status = "BLOCK"
        elif verdict == "PASS":
            status = "PASS"
        else:
            status = "WARN"

        return {
            "status": status,
            "executed_command": cmd,
            "output_summary": f"validator_returncode={run['returncode']} validator_verdict={verdict}",
            "payload": {
                "validator": run,
                "validator_report": validator_report,
            },
            "evidence_refs": [relpath(output_path, self.repo_root)],
            "known_limitations": [
                "Validator covers bounded Sanctum NG foundation checks.",
                "No production readiness claim."
            ],
        }

    def _parse_kv_from_stdout(self, text: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for line in text.splitlines():
            line = line.strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip()
        return out

    def _run_transfer_console_action(self, action_id: str) -> dict[str, Any]:
        runner_path = self.repo_root / TRANSFER_CONSOLE_ACTION_RUNNER_REL
        transfer_report_dir = (
            self.repo_root
            / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS"
            / self.task_id
        )
        cmd = [
            "python3",
            str(runner_path),
            "--repo-root",
            str(self.repo_root),
            "--task-id",
            self.task_id,
            "--action-id",
            action_id,
            "--requester",
            "SANCTUM_NG_ACTION_SERVER",
            "--report-dir",
            str(transfer_report_dir),
        ]
        run = self._run_command(cmd)
        parsed = self._parse_kv_from_stdout(str(run.get("stdout", "")))
        transfer_status = parsed.get("transfer_console_action_status", "WARN")
        report_ref = parsed.get("transfer_console_action_report")
        view_ref = parsed.get("transfer_console_view_state", TRANSFER_CONSOLE_VIEW_STATE_REL)

        if run["returncode"] != 0:
            status = "BLOCK"
        elif transfer_status == "PASS":
            status = "PASS"
        elif transfer_status == "BLOCK":
            status = "BLOCK"
        else:
            status = "WARN"

        evidence_refs = [TRANSFER_CONSOLE_ACTION_RUNNER_REL, TRANSFER_CONSOLE_VIEW_STATE_REL]
        if report_ref:
            evidence_refs.append(report_ref)
        if view_ref and view_ref not in evidence_refs:
            evidence_refs.append(view_ref)

        return {
            "status": status,
            "executed_command": cmd,
            "output_summary": (
                f"transfer_action={action_id} status={transfer_status} "
                f"returncode={run['returncode']}"
            ),
            "payload": {
                "runner": run,
                "runner_report_ref": report_ref,
                "view_state_ref": view_ref,
                "transfer_action_status": transfer_status,
                "parsed_stdout": parsed,
            },
            "evidence_refs": evidence_refs,
            "known_limitations": [
                "Transfer Console actions are file-backed foundation workflows only.",
                "No production remote orchestration claim is made.",
            ],
        }

    def _run_transfer_action_runner_action(self, action_id: str) -> dict[str, Any]:
        runner_path = self.repo_root / TRANSFER_ACTION_RUNNER_REL
        transfer_report_dir = (
            self.repo_root
            / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS"
            / self.task_id
        )
        cmd = [
            "python3",
            str(runner_path),
            "--repo-root",
            str(self.repo_root),
            "--task-id",
            self.task_id,
            "--action-id",
            action_id,
            "--requester",
            "SANCTUM_NG_ACTION_SERVER",
            "--report-dir",
            str(transfer_report_dir),
        ]
        run = self._run_command(cmd)
        parsed = self._parse_kv_from_stdout(str(run.get("stdout", "")))
        runner_status = parsed.get("transfer_action_runner_status", "WARN")
        report_ref = parsed.get("transfer_action_runner_report")
        request_ref = parsed.get("transfer_action_request_ref")
        result_ref = parsed.get("transfer_action_result_ref")
        view_ref = parsed.get("transfer_console_view_state", TRANSFER_CONSOLE_VIEW_STATE_REL)

        if run["returncode"] != 0:
            status = "BLOCK"
        elif runner_status == "PASS":
            status = "PASS"
        elif runner_status == "BLOCK":
            status = "BLOCK"
        else:
            status = "WARN"

        evidence_refs = [TRANSFER_ACTION_RUNNER_REL, TRANSFER_CONSOLE_VIEW_STATE_REL]
        for ref in [report_ref, request_ref, result_ref, view_ref]:
            if ref and ref not in evidence_refs:
                evidence_refs.append(ref)

        return {
            "status": status,
            "executed_command": cmd,
            "output_summary": (
                f"transfer_action_runner={action_id} status={runner_status} "
                f"returncode={run['returncode']}"
            ),
            "payload": {
                "runner": run,
                "runner_report_ref": report_ref,
                "request_ref": request_ref,
                "result_ref": result_ref,
                "view_state_ref": view_ref,
                "transfer_action_runner_status": runner_status,
                "parsed_stdout": parsed,
            },
            "evidence_refs": evidence_refs,
            "known_limitations": [
                "Transfer Action Runner is foundation-only allowlisted workflow.",
                "No production remote orchestration claim is made.",
            ],
        }

    def _read_fixed_json(self, rel: str) -> dict[str, Any]:
        payload = load_json(self.repo_root / rel)
        if payload is None:
            return {
                "status": "WARN",
                "payload": {"path": rel, "exists": False},
                "evidence_refs": [rel],
                "output_summary": f"missing_or_invalid:{rel}",
                "known_limitations": ["File is missing or not a JSON object."],
            }
        return {
            "status": "PASS",
            "payload": {"path": rel, "exists": True, "content": payload},
            "evidence_refs": [rel],
            "output_summary": f"read_ok:{rel}",
            "known_limitations": ["Read scope is bounded to fixed path."],
        }

    def _parse_any_utc(self, payload: dict[str, Any]) -> dt.datetime | None:
        timestamp_keys = ["generated_at_utc", "timestamp_utc", "finished_at_utc", "requested_at_utc"]
        for key in timestamp_keys:
            raw = payload.get(key)
            if not isinstance(raw, str):
                continue
            value = raw.strip()
            if not value:
                continue
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            try:
                parsed = dt.datetime.fromisoformat(value)
            except ValueError:
                continue
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc)
        return None

    def _resolve_existing_report(self, primary_name: str, aliases: list[str]) -> tuple[Path | None, str]:
        candidates = [primary_name, *aliases]
        for name in candidates:
            candidate = self.report_dir / name
            if candidate.exists():
                return candidate, name
        return None, ""

    def _read_latest_report_summary(self) -> dict[str, Any]:
        expected_specs = [
            {
                "logical_id": "refresh_runner",
                "primary": "SANCTUM_NG_REFRESH_RUNNER_REPORT.json",
                "aliases": [],
            },
            {
                "logical_id": "validator",
                "primary": "VALIDATOR_REPORT.json",
                "aliases": [],
            },
            {
                "logical_id": "smoke",
                "primary": "SMOKE_REPORT.json",
                "aliases": ["ACTION_LAYER_SMOKE_REPORT.json"],
            },
            {
                "logical_id": "final_receipt",
                "primary": "FINAL_RECEIPT.json",
                "aliases": [],
            },
            {
                "logical_id": "post_commit_closure",
                "primary": "POST_COMMIT_CLOSURE_RECEIPT.json",
                "aliases": [],
            },
        ]

        evidence_refs: list[str] = [relpath(self.report_dir, self.repo_root)]
        expected_files: list[str] = []
        found_files: list[str] = []
        missing_files: list[str] = []
        partial_files: list[str] = []
        stale_files: list[str] = []
        error_files: list[str] = []
        inspected_reports: list[dict[str, Any]] = []

        for spec in expected_specs:
            primary_name = str(spec["primary"])
            aliases = [str(item) for item in spec["aliases"]]
            expected_path = self.report_dir / primary_name
            expected_rel = relpath(expected_path, self.repo_root)
            expected_files.append(expected_rel)

            resolved_path, resolved_name = self._resolve_existing_report(primary_name, aliases)
            if resolved_path is None:
                missing_files.append(expected_rel)
                inspected_reports.append(
                    {
                        "logical_id": spec["logical_id"],
                        "expected_path": expected_rel,
                        "resolved_path": "N/A",
                        "summary_state": "MISSING",
                        "reason": "file_not_found",
                        "exists": False,
                        "verdict": "UNKNOWN",
                    }
                )
                continue

            resolved_rel = relpath(resolved_path, self.repo_root)
            payload = load_json(resolved_path)
            evidence_refs.append(resolved_rel)

            if payload is None:
                error_files.append(resolved_rel)
                inspected_reports.append(
                    {
                        "logical_id": spec["logical_id"],
                        "expected_path": expected_rel,
                        "resolved_path": resolved_rel,
                        "summary_state": "ERROR",
                        "reason": "invalid_json_or_not_object",
                        "exists": True,
                        "verdict": "UNKNOWN",
                    }
                )
                continue

            file_task_id = str(payload.get("task_id", "")).strip()
            file_verdict = str(payload.get("verdict", payload.get("status", "UNKNOWN")))
            summary_state = "FOUND"
            reason = "ok"

            if file_task_id and file_task_id != self.task_id:
                summary_state = "STALE"
                reason = f"task_id_mismatch:{file_task_id}"
                stale_files.append(resolved_rel)
            elif resolved_name != primary_name:
                summary_state = "PARTIAL"
                reason = f"legacy_alias_used:{resolved_name}"
                partial_files.append(resolved_rel)
            elif not file_verdict.strip():
                summary_state = "PARTIAL"
                reason = "missing_verdict_or_status"
                partial_files.append(resolved_rel)
            else:
                parsed_time = self._parse_any_utc(payload)
                if parsed_time is None:
                    summary_state = "PARTIAL"
                    reason = "missing_or_invalid_timestamp"
                    partial_files.append(resolved_rel)
                else:
                    found_files.append(resolved_rel)

            inspected_reports.append(
                {
                    "logical_id": spec["logical_id"],
                    "expected_path": expected_rel,
                    "resolved_path": resolved_rel,
                    "summary_state": summary_state,
                    "reason": reason,
                    "exists": True,
                    "verdict": file_verdict,
                }
            )

        report_dir_items = [path for path in self.report_dir.iterdir()] if self.report_dir.exists() else []
        summary_state = "FOUND"
        reason = "all_expected_reports_found"

        if error_files:
            summary_state = "ERROR"
            reason = "invalid_or_unreadable_report_detected"
        elif stale_files:
            summary_state = "STALE"
            reason = "stale_report_detected"
        elif missing_files or partial_files:
            if not found_files and not partial_files:
                if not report_dir_items:
                    summary_state = "NOT_READY"
                    reason = "report_bundle_not_started"
                else:
                    summary_state = "MISSING"
                    reason = "expected_reports_missing"
            else:
                summary_state = "PARTIAL"
                reason = "report_bundle_incomplete_or_legacy"

        if summary_state not in SUMMARY_STATE_SET:
            summary_state = "ERROR"
            reason = "internal_summary_state_violation"

        owner_summary = (
            f"{summary_state}: found={len(found_files)} "
            f"missing={len(missing_files)} partial={len(partial_files)} "
            f"stale={len(stale_files)} error={len(error_files)}"
        )

        status_map = {
            "FOUND": "PASS",
            "MISSING": "PARTIAL",
            "PARTIAL": "PARTIAL",
            "NOT_READY": "PARTIAL",
            "STALE": "PARTIAL",
            "ERROR": "ERROR",
        }
        status = status_map.get(summary_state, "ERROR")

        return {
            "status": status,
            "payload": {
                "summary_state": summary_state,
                "reason": reason,
                "owner_summary": owner_summary,
                "report_folder_inspected": relpath(self.report_dir, self.repo_root),
                "expected_files": expected_files,
                "found_files": found_files,
                "missing_files": missing_files,
                "partial_files": partial_files,
                "stale_files": stale_files,
                "error_files": error_files,
                "reports": inspected_reports,
            },
            "evidence_refs": sorted(set(evidence_refs)),
            "output_summary": owner_summary,
            "known_limitations": [
                "Only fixed known report files are readable.",
                "Alias support is limited to historical smoke filename compatibility.",
                "Summary is read-only and does not auto-repair missing files.",
            ],
        }

    def latest_report_summary(self) -> dict[str, Any]:
        return self._read_latest_report_summary()

    def execute_action(self, action_id: str, requester: str, dry_run: bool, input_payload: dict[str, Any]) -> dict[str, Any]:
        started_at = utc_now()
        action_map = self.action_map()
        action_def = action_map.get(action_id)

        if action_def is None:
            result = {
                "schema_id": "SANCTUM_NG_ACTION_RESULT_V0_1",
                "task_id": self.task_id,
                "request_id": "NOT_CREATED",
                "action_id": action_id,
                "action_status": "BLOCKED",
                "status": "NOT_ALLOWED",
                "started_at_utc": started_at,
                "finished_at_utc": utc_now(),
                "request_record_path": "N/A",
                "result_record_path": "N/A",
                "executed_command": [],
                "output_summary": "Action ID is not allowlisted.",
                "payload": {"known_actions": sorted(action_map.keys())},
                "evidence_refs": [ACTION_REGISTRY_REL],
                "known_limitations": [
                    "Only allowlisted actions can be executed.",
                    "Arbitrary action IDs are blocked.",
                ],
            }
            return self._attach_state_model(result)

        request_id, request_path = self._request_record(action_id, requester, dry_run, input_payload)
        action_status = str(action_def.get("status", "BLOCKED"))

        base_result = {
            "schema_id": "SANCTUM_NG_ACTION_RESULT_V0_1",
            "task_id": self.task_id,
            "request_id": request_id,
            "action_id": action_id,
            "action_status": action_status,
            "started_at_utc": started_at,
            "request_record_path": relpath(request_path, self.repo_root),
            "executed_command": [],
        }

        result_path = self._result_record_path(request_id)

        if action_status != "WIRED":
            status_map = {
                "PREVIEW_ONLY": "PREVIEW_ONLY",
                "NOT_WIRED": "BLOCK",
                "BLOCKED": "BLOCK",
            }
            result = {
                **base_result,
                "status": status_map.get(action_status, "BLOCK"),
                "finished_at_utc": utc_now(),
                "result_record_path": relpath(result_path, self.repo_root),
                "output_summary": f"Action status {action_status} is not executable.",
                "payload": {
                    "action": action_def,
                    "dry_run": dry_run,
                },
                "evidence_refs": [ACTION_REGISTRY_REL],
                "known_limitations": [
                    "Only WIRED actions are executable from the server.",
                    "Non-WIRED actions are surfaced for transparency only.",
                ],
            }
            result = self._attach_state_model(result)
            write_json(result_path, result)
            return result

        if dry_run:
            result = {
                **base_result,
                "status": "PASS",
                "finished_at_utc": utc_now(),
                "result_record_path": relpath(result_path, self.repo_root),
                "output_summary": "Dry run completed; no action routine executed.",
                "payload": {"action": action_def, "dry_run": True},
                "evidence_refs": [ACTION_REGISTRY_REL],
                "known_limitations": ["Dry run does not produce runtime side effects."],
            }
            result = self._attach_state_model(result)
            write_json(result_path, result)
            return result

        dispatch = {
            "REFRESH_TRUTH_STATE": self._run_refresh,
            "VALIDATE_TRUTH_STATE": self._run_validate,
            "READ_PHASE_REGISTRY": lambda: self._read_fixed_json(PHASE_REGISTRY_REL),
            "READ_ACTION_REGISTRY": lambda: self._read_fixed_json(ACTION_REGISTRY_REL),
            "READ_LATEST_REPORT_SUMMARY": self._read_latest_report_summary,
            "CHECK_CONTOUR_STATUS": lambda: self._run_transfer_console_action("CHECK_CONTOUR_STATUS"),
            "REGISTER_TASKPACK_SEND": lambda: self._run_transfer_console_action("REGISTER_TASKPACK_SEND"),
            "REGISTER_REPORT_BUNDLE_FETCH": lambda: self._run_transfer_console_action("REGISTER_REPORT_BUNDLE_FETCH"),
            "DRY_RUN_TASKPACK_SEND": lambda: self._run_transfer_console_action("DRY_RUN_TASKPACK_SEND"),
            "DRY_RUN_REPORT_FETCH": lambda: self._run_transfer_console_action("DRY_RUN_REPORT_FETCH"),
            "REFRESH_TRANSFER_CONSOLE_VIEW": lambda: self._run_transfer_console_action("REFRESH_TRANSFER_CONSOLE_VIEW"),
            "SEND_TASKPACK_ZIP": lambda: self._run_transfer_action_runner_action("SEND_TASKPACK_ZIP"),
            "FETCH_REPORT_BUNDLE_ZIP": lambda: self._run_transfer_action_runner_action("FETCH_REPORT_BUNDLE_ZIP"),
            "REGISTER_TRANSFER_RESULT": lambda: self._run_transfer_action_runner_action("REGISTER_TRANSFER_RESULT"),
            "VALIDATE_TRANSFER_REQUEST": lambda: self._run_transfer_action_runner_action("VALIDATE_TRANSFER_REQUEST"),
            "DRY_RUN_TRANSFER": lambda: self._run_transfer_action_runner_action("DRY_RUN_TRANSFER"),
        }
        routine = dispatch.get(action_id)

        if routine is None:
            result = {
                **base_result,
                "status": "BLOCK",
                "finished_at_utc": utc_now(),
                "result_record_path": relpath(result_path, self.repo_root),
                "output_summary": "Action is allowlisted but routine is not implemented.",
                "payload": {"action": action_def},
                "evidence_refs": [ACTION_REGISTRY_REL],
                "known_limitations": ["Routine mapping is missing for this action."],
            }
            result = self._attach_state_model(result)
            write_json(result_path, result)
            return result

        try:
            payload = routine()
            status = str(payload.get("status", "WARN"))
            result = {
                **base_result,
                "status": status,
                "finished_at_utc": utc_now(),
                "result_record_path": relpath(result_path, self.repo_root),
                "executed_command": payload.get("executed_command", []),
                "output_summary": str(payload.get("output_summary", "")),
                "payload": payload.get("payload", {}),
                "evidence_refs": payload.get("evidence_refs", []),
                "known_limitations": payload.get("known_limitations", []),
            }
        except Exception as exc:  # defensive guard
            result = {
                **base_result,
                "status": "ERROR",
                "finished_at_utc": utc_now(),
                "result_record_path": relpath(result_path, self.repo_root),
                "output_summary": f"Action execution error: {exc}",
                "payload": {"error": str(exc)},
                "evidence_refs": [ACTION_REGISTRY_REL],
                "known_limitations": ["Unexpected exception while running allowlisted action."],
            }

        result = self._attach_state_model(result)
        write_json(result_path, result)
        latest_path = self.action_log_dir / "latest_action_result.json"
        write_json(latest_path, result)
        return result


class SanctumHandler(SimpleHTTPRequestHandler):
    layer: ActionLayer

    def __init__(self, *args: Any, layer: ActionLayer, **kwargs: Any) -> None:
        self.layer = layer
        super().__init__(*args, directory=str(layer.app_dir), **kwargs)

    def log_message(self, fmt: str, *args: Any) -> None:
        # Keep stdout concise for task receipts while preserving default server behavior.
        print(f"[sanctum-ng-action-server] {fmt % args}")

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self._send_json(
                {
                    "status": "OK",
                    "service": "sanctum_ng_action_server",
                    "task_id": self.layer.task_id,
                    "generated_at_utc": utc_now(),
                }
            )
            return

        if path == "/api/state":
            latest_action_result = self.layer._load_latest_action_result()
            self._send_json(
                {
                    "status": "CONNECTED",
                    "task_id": self.layer.task_id,
                    "state": self.layer.state_payload(),
                    "servitor_session_view": self.layer.servitor_session_view_payload(),
                    "owner_question_gate": self.layer.owner_question_gate_payload(),
                    "transfer_console_view": self.layer.transfer_console_view_payload(),
                    "action_layer_state_model": self.layer.connection_state_model(),
                    "latest_action_result": latest_action_result,
                    "latest_report_summary": self.layer.latest_report_summary(),
                }
            )
            return

        if path == "/api/actions":
            registry = self.layer.action_registry()
            actions = registry.get("actions", [])
            action_list: list[dict[str, Any]] = []
            if isinstance(actions, list):
                for action in actions:
                    if not isinstance(action, dict):
                        continue
                    status = str(action.get("status", "BLOCKED"))
                    action_list.append(
                        {
                            **action,
                            "availability_state": self.layer._action_availability_state(status),
                        }
                    )

            registry_status = "ACTION_ALLOWED" if any(
                str(item.get("status", "")) == "WIRED" for item in action_list
            ) else "ACTION_DISABLED"
            self._send_json(
                {
                    "status": "CONNECTED",
                    "task_id": self.layer.task_id,
                    "registry": {
                        "schema_id": registry.get("schema_id", "SANCTUM_NG_ACTION_REGISTRY_V0_1"),
                        "mode": registry.get("mode", "ACTION_LAYER_FOUNDATION_ONLY"),
                        "status": registry_status,
                    },
                    "actions": action_list,
                    "action_layer_state_model": self.layer.connection_state_model(),
                    "forbidden_paths": FORBIDDEN_PATHS,
                }
            )
            return

        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if not path.startswith("/api/actions/"):
            self._send_json(
                {
                    "error": "not_found",
                    "details": "Only /api/actions/<ACTION_ID> is supported for POST.",
                },
                status=HTTPStatus.NOT_FOUND,
            )
            return

        action_id = unquote(path.split("/api/actions/", 1)[1]).strip()
        if not action_id:
            self._send_json(
                {
                    "error": "invalid_action_id",
                    "details": "Action ID is missing in URL.",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        length_header = self.headers.get("Content-Length", "0")
        try:
            content_length = int(length_header)
        except ValueError:
            content_length = 0

        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError:
            self._send_json(
                {
                    "error": "invalid_json",
                    "details": "Request body must be valid JSON.",
                },
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        if not isinstance(body, dict):
            body = {}

        requester = str(body.get("requester", "API_CLIENT"))
        dry_run = bool(body.get("dry_run", False))
        input_payload = body.get("input", {})
        if not isinstance(input_payload, dict):
            input_payload = {}

        result = self.layer.execute_action(action_id, requester, dry_run, input_payload)

        status = str(result.get("status", "ERROR"))
        http_status = HTTPStatus.OK
        if status in {"NOT_ALLOWED", "BLOCK", "ERROR"}:
            http_status = HTTPStatus.BAD_REQUEST

        self._send_json(result, status=http_status)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM-ACTION-LAYER-HARDENING-VM3-V0_1"
    )
    default_action_log_dir = default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/action_logs"

    parser = argparse.ArgumentParser(description="Sanctum NG file-backed action layer server.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--required-starting-head", default=REQUIRED_STARTING_HEAD_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--action-log-dir", type=Path, default=default_action_log_dir)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()

    if args.host not in {"127.0.0.1", "localhost"}:
        print("error=localhost_only host must be 127.0.0.1 or localhost")
        return 1

    layer = ActionLayer(
        repo_root=repo_root,
        task_id=str(args.task_id),
        required_starting_head=str(args.required_starting_head),
        report_dir=args.report_dir.resolve(),
        action_log_dir=args.action_log_dir.resolve(),
    )

    def handler_factory(*handler_args: Any, **handler_kwargs: Any) -> SanctumHandler:
        return SanctumHandler(*handler_args, layer=layer, **handler_kwargs)

    server = ThreadingHTTPServer((args.host, int(args.port)), handler_factory)
    print(f"server_status=STARTING host={args.host} port={args.port}")
    print(f"app_dir={relpath(layer.app_dir, repo_root)}")
    print(f"action_registry={ACTION_REGISTRY_REL}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

    print("server_status=STOPPED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
