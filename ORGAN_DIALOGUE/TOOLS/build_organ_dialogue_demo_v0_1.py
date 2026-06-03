#!/usr/bin/env python3
"""Build deterministic file-backed Organ Dialogue foundation demo artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-ORGAN-DIALOGUE-DEMO-VM2-V0_1"
DEMO_TASK_ID = "TASK-DEMO-ORGAN-DIALOGUE-V0_1"
THREAD_ID = "THREAD-TASK-DEMO-ORGAN-DIALOGUE-V0_1"

ORGANS: list[dict[str, Any]] = [
    {
        "organ": "ASTRONOMICON",
        "source_actor": "SANCTUM_NG",
        "verdict": "FOUNDATION_READY",
        "confidence": 0.86,
        "questions": [
            "Confirm bounded thread framing and task identity continuity.",
            "List strict non-goals for this foundation demo."
        ],
    },
    {
        "organ": "OFFICIO_AGENTIS",
        "source_actor": "SANCTUM_NG",
        "verdict": "READY_WITH_WARNINGS",
        "confidence": 0.78,
        "questions": [
            "Validate Owner-facing RU live commentary boundary.",
            "Confirm technical artifact language policy."
        ],
    },
    {
        "organ": "DOCTRINARIUM",
        "source_actor": "SANCTUM_NG",
        "verdict": "FOUNDATION_ONLY",
        "confidence": 0.82,
        "questions": [
            "Check no-fake-green wording and evidence rule.",
            "Verify no live autonomy claim appears."
        ],
    },
    {
        "organ": "ADMINISTRATUM",
        "source_actor": "SANCTUM_NG",
        "verdict": "FOUNDATION_READY",
        "confidence": 0.85,
        "questions": [
            "Confirm receipt bundle completeness requirements.",
            "Confirm thread/event packet retention requirements."
        ],
    },
    {
        "organ": "MECHANICUS",
        "source_actor": "SERVITOR_EXTERNAL",
        "verdict": "READY_WITH_WARNINGS",
        "confidence": 0.77,
        "questions": [
            "Validate deterministic builder/validator/smoke wiring.",
            "Confirm script artifact preservation expectation."
        ],
    },
    {
        "organ": "INQUISITION",
        "source_actor": "SERVITOR_EXTERNAL",
        "verdict": "MISSING_PREREQUISITE",
        "confidence": 0.74,
        "questions": [
            "List stop conditions for scope drift and fake green.",
            "Confirm forbidden path enforcement expectations."
        ],
    },
    {
        "organ": "STRATEGIUM",
        "source_actor": "SERVITOR_EXTERNAL",
        "verdict": "BLOCKED_NEEDS_OWNER",
        "confidence": 0.66,
        "questions": [
            "Identify owner-choice boundary for next expansion phase.",
            "List what must remain manual in this version."
        ],
    },
    {
        "organ": "SCHOLA_IMPERIALIS",
        "source_actor": "SERVITOR_EXTERNAL",
        "verdict": "FOUNDATION_ONLY",
        "confidence": 0.79,
        "questions": [
            "Summarize teachable packet pattern for future agents.",
            "Confirm onboarding notes for deterministic dialogue packets."
        ],
    },
]

WARN_VERDICTS = {
    "READY_WITH_WARNINGS",
    "MISSING_PREREQUISITE",
    "BLOCKED_NEEDS_OWNER",
    "FOUNDATION_ONLY",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


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


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/"
        "TASK-20260523-NEWGEN-SANCTUM-ORGAN-DIALOGUE-DEMO-VM2-V0_1"
    )

    parser = argparse.ArgumentParser(description="Build Organ Dialogue foundation demo.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument(
        "--sanctum-state",
        type=Path,
        default=default_repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
    )
    return parser.parse_args()


def build_request_payload(task_id: str, idx: int, organ_cfg: dict[str, Any], timestamp: str) -> dict[str, Any]:
    organ = str(organ_cfg["organ"])
    return {
        "schema_id": "ORGAN_DIALOGUE_REQUEST_V0_1",
        "request_id": f"OD-REQ-{idx:03d}-{organ}",
        "task_id": DEMO_TASK_ID,
        "source_actor": str(organ_cfg["source_actor"]),
        "target_organ": organ,
        "purpose": f"Foundation dialogue intake for {organ} without live autonomy.",
        "question_set": [str(q) for q in organ_cfg["questions"]],
        "context_refs": [
            "IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json",
            "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
            "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260523-NEWGEN-PQG-NEGATIVE-TEST-MUTATION-CHECK-VM2-V0_1/FINAL_RECEIPT.json",
        ],
        "allowed_response_mode": "FOUNDATION_DETERMINISTIC_FILE_BACKED_ONLY",
        "claim_boundary": "foundation-only deterministic packet response; no live autonomous organ execution",
        "created_at_utc": timestamp,
        "owner_task_id": task_id,
    }


def build_response_payload(request: dict[str, Any], idx: int, organ_cfg: dict[str, Any], timestamp: str) -> dict[str, Any]:
    organ = str(organ_cfg["organ"])
    verdict = str(organ_cfg["verdict"])
    return {
        "schema_id": "ORGAN_DIALOGUE_RESPONSE_V0_1",
        "response_id": f"OD-RES-{idx:03d}-{organ}",
        "request_id": str(request["request_id"]),
        "organ_id": organ,
        "verdict": verdict,
        "scope_advice": [
            "Stay inside ORGAN_DIALOGUE and SANCTUM_NG read-only display scope.",
            "Keep claim boundary explicit: foundation-only deterministic dialogue.",
        ],
        "required_checks": [
            "GATE-U02-SCOPE-BOUNDARY",
            "GATE-U04-EVIDENCE-RECEIPT",
            "GATE-U09-NO-FAKE-GREEN",
        ],
        "forbidden_actions": [
            "Claim live autonomous organ intelligence.",
            "Write outside allowlisted NewGen paths.",
            "Mark production-ready without evidence receipts.",
        ],
        "evidence_required": [
            "request packet exists",
            "response packet exists",
            "thread and event log updated",
            "sanctum state reference updated",
        ],
        "owner_questions": [
            "Should this organ receive richer decision tables in the next bounded task?",
            "Is deterministic stub depth acceptable for current foundation checkpoint?",
        ],
        "confidence": float(organ_cfg["confidence"]),
        "foundation_only": True,
        "evidence_refs": [
            "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/REGISTRY/ORGAN_DIALOGUE_THREAD_INDEX_V0_1.json",
            "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/THREADS/TASK-DEMO-ORGAN-DIALOGUE-V0_1/ORGAN_DIALOGUE_THREAD_V0_1.generated.json",
            "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
        ],
        "generated_at_utc": timestamp,
    }


def build() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    task_id = str(args.task_id)
    report_dir = args.report_dir.resolve()
    sanctum_state_path = args.sanctum_state.resolve()

    base_dir = repo_root / "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE"
    registry_dir = base_dir / "REGISTRY"
    thread_dir = base_dir / "THREADS/TASK-DEMO-ORGAN-DIALOGUE-V0_1"
    requests_dir = thread_dir / "REQUESTS"
    responses_dir = thread_dir / "RESPONSES"
    scope_dir = thread_dir / "SCOPE_IMPACT"

    for path in [registry_dir, requests_dir, responses_dir, scope_dir, report_dir]:
        path.mkdir(parents=True, exist_ok=True)

    for path in list(requests_dir.glob("*.request.json")):
        path.unlink()
    for path in list(responses_dir.glob("*.response.json")):
        path.unlink()

    start = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)

    requests_index: list[dict[str, Any]] = []
    responses_index: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    for idx, organ_cfg in enumerate(ORGANS, start=1):
        ts_request = (start + dt.timedelta(seconds=idx)).isoformat().replace("+00:00", "Z")
        request_payload = build_request_payload(task_id, idx, organ_cfg, ts_request)
        request_path = requests_dir / f"{request_payload['request_id']}.request.json"
        write_json(request_path, request_payload)

        requests_index.append(
            {
                "request_id": request_payload["request_id"],
                "target_organ": request_payload["target_organ"],
                "request_path": relpath(request_path, repo_root),
            }
        )

        events.append(
            {
                "schema_id": "ORGAN_DIALOGUE_EVENT_V0_1",
                "event_id": f"OD-EVT-{idx:03d}-REQ",
                "thread_id": THREAD_ID,
                "timestamp_utc": ts_request,
                "event_type": "REQUEST_EMITTED",
                "actor": request_payload["source_actor"],
                "payload_ref": relpath(request_path, repo_root),
                "foundation_only": True,
                "note": "Deterministic request packet created.",
            }
        )

        ts_response = (start + dt.timedelta(seconds=100 + idx)).isoformat().replace("+00:00", "Z")
        response_payload = build_response_payload(request_payload, idx, organ_cfg, ts_response)
        response_path = responses_dir / f"{response_payload['response_id']}.response.json"
        write_json(response_path, response_payload)

        responses_index.append(
            {
                "response_id": response_payload["response_id"],
                "request_id": response_payload["request_id"],
                "organ_id": response_payload["organ_id"],
                "response_path": relpath(response_path, repo_root),
                "verdict": response_payload["verdict"],
                "foundation_only": True,
            }
        )

        events.append(
            {
                "schema_id": "ORGAN_DIALOGUE_EVENT_V0_1",
                "event_id": f"OD-EVT-{idx:03d}-RES",
                "thread_id": THREAD_ID,
                "timestamp_utc": ts_response,
                "event_type": "RESPONSE_RECORDED",
                "actor": response_payload["organ_id"],
                "payload_ref": relpath(response_path, repo_root),
                "foundation_only": True,
                "note": f"Verdict={response_payload['verdict']}",
            }
        )

    warnings_count = sum(1 for item in responses_index if str(item["verdict"]) in WARN_VERDICTS)
    last_event_ts = (start + dt.timedelta(seconds=300)).isoformat().replace("+00:00", "Z")
    last_event = "THREAD_SUMMARY_UPDATED"

    thread_payload = {
        "schema_id": "ORGAN_DIALOGUE_THREAD_V0_1",
        "thread_id": THREAD_ID,
        "demo_task_id": DEMO_TASK_ID,
        "owner_task_id": task_id,
        "foundation_only": True,
        "live_autonomy": False,
        "requests": requests_index,
        "responses": responses_index,
        "summary": {
            "request_count": len(requests_index),
            "response_count": len(responses_index),
            "warnings_count": warnings_count,
            "last_event": last_event,
            "last_event_at_utc": last_event_ts,
        },
        "limitations": [
            "Deterministic synthetic packets only.",
            "No live organ-to-organ or model-to-model autonomy.",
            "No production execution claim.",
        ],
    }
    thread_path = thread_dir / "ORGAN_DIALOGUE_THREAD_V0_1.generated.json"
    write_json(thread_path, thread_payload)

    summary_event = {
        "schema_id": "ORGAN_DIALOGUE_EVENT_V0_1",
        "event_id": "OD-EVT-999-SUMMARY",
        "thread_id": THREAD_ID,
        "timestamp_utc": last_event_ts,
        "event_type": "THREAD_SUMMARY_UPDATED",
        "actor": "SANCTUM_NG",
        "payload_ref": relpath(thread_path, repo_root),
        "foundation_only": True,
        "note": f"requests={len(requests_index)} responses={len(responses_index)} warnings={warnings_count}",
    }
    events.append(summary_event)

    events_path = thread_dir / "ORGAN_DIALOGUE_EVENTS_V0_1.generated.jsonl"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    with events_path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    scope_impact_payload = {
        "schema_id": "ORGAN_DIALOGUE_SCOPE_IMPACT_V0_1",
        "task_id": task_id,
        "demo_task_id": DEMO_TASK_ID,
        "foundation_only": True,
        "allowed_paths": [
            "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/**",
            "IMPERIUM_NEW_GENERATION/SANCTUM_NG/**",
            "IMPERIUM_NEW_GENERATION/TRUTH/**",
            f"IMPERIUM_NEW_GENERATION/REPORTS/{task_id}/**",
        ],
        "forbidden_paths": [
            "ORGANS/**",
            "SANCTUM/**",
            "IMPERIUM_TEST_VERSION/**",
            "main/root files outside allowlisted NewGen paths",
        ],
        "claims_not_proved": [
            "LIVE_AUTONOMOUS_ORGAN_INTELLIGENCE",
            "PRODUCTION_BACKEND_READY",
            "FULL_AGENT_FACTORY_AUTONOMY",
        ],
        "runtime_impact": "READ_ONLY_UI_SURFACE",
        "evidence_refs": [
            relpath(thread_path, repo_root),
            relpath(events_path, repo_root),
            "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json",
        ],
    }
    scope_impact_path = scope_dir / "ORGAN_DIALOGUE_SCOPE_IMPACT_V0_1.generated.json"
    write_json(scope_impact_path, scope_impact_payload)

    thread_index_payload = {
        "schema_id": "ORGAN_DIALOGUE_THREAD_INDEX_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "mode": "FOUNDATION_DETERMINISTIC_FILE_BACKED_ONLY",
        "threads": [
            {
                "thread_id": THREAD_ID,
                "demo_task_id": DEMO_TASK_ID,
                "thread_path": relpath(thread_path, repo_root),
                "events_path": relpath(events_path, repo_root),
                "scope_impact_path": relpath(scope_impact_path, repo_root),
                "request_count": len(requests_index),
                "response_count": len(responses_index),
                "warnings_count": warnings_count,
                "foundation_only": True,
            }
        ],
        "forbidden_claims": [
            "LIVE_ORGAN_AUTONOMY",
            "PRODUCTION_READY",
        ],
    }
    thread_index_path = registry_dir / "ORGAN_DIALOGUE_THREAD_INDEX_V0_1.json"
    write_json(thread_index_path, thread_index_payload)

    capability_matrix_payload = {
        "schema_id": "ORGAN_DIALOGUE_CAPABILITY_MATRIX_V0_1",
        "task_id": task_id,
        "generated_at_utc": utc_now(),
        "foundation_only": True,
        "capabilities": [
            {
                "organ_id": str(cfg["organ"]),
                "packet_mode": "FOUNDATION_DETERMINISTIC_FILE_BACKED_ONLY",
                "allowed_response_mode": "FOUNDATION_DETERMINISTIC_FILE_BACKED_ONLY",
                "live_autonomy": False,
                "notes": [
                    "Response is deterministic stub.",
                    "Evidence and scope boundaries remain explicit.",
                ],
            }
            for cfg in ORGANS
        ],
    }
    capability_matrix_path = registry_dir / "ORGAN_DIALOGUE_CAPABILITY_MATRIX_V0_1.json"
    write_json(capability_matrix_path, capability_matrix_payload)

    sanctum_state = load_json(sanctum_state_path)
    if sanctum_state is None:
        sanctum_state = {
            "schema_id": "SANCTUM_NG_STATE_V0_1",
            "task_id": task_id,
            "mode": "READ_ONLY_FOUNDATION",
            "generated_at_utc": utc_now(),
            "warnings": [],
            "limitations": [],
        }

    sanctum_state["task_id"] = task_id
    sanctum_state["generated_at_utc"] = utc_now()

    warnings = sanctum_state.get("warnings", [])
    if not isinstance(warnings, list):
        warnings = []
    marker_warning = "ORGAN_DIALOGUE_DEMO_FOUNDATION_ONLY"
    if marker_warning not in warnings:
        warnings.append(marker_warning)
    sanctum_state["warnings"] = warnings

    limitations = sanctum_state.get("limitations", [])
    if not isinstance(limitations, list):
        limitations = []
    marker_limit = "Organ Dialogue Demo is deterministic foundation-only; no live autonomy is claimed."
    if marker_limit not in limitations:
        limitations.append(marker_limit)
    sanctum_state["limitations"] = limitations

    sanctum_state["organ_dialogue_demo"] = {
        "task_id": DEMO_TASK_ID,
        "thread_id": THREAD_ID,
        "request_count": len(requests_index),
        "response_count": len(responses_index),
        "warnings_count": warnings_count,
        "last_event": last_event,
        "last_event_at_utc": last_event_ts,
        "foundation_only_label": "FOUNDATION_ONLY",
        "no_live_autonomy_label": "NO_LIVE_AUTONOMY",
        "thread_path": relpath(thread_path, repo_root),
        "events_path": relpath(events_path, repo_root),
    }

    write_json(sanctum_state_path, sanctum_state)

    run_report = {
        "schema_id": "ORGAN_DIALOGUE_DEMO_RUN_REPORT_V0_1",
        "task_id": task_id,
        "demo_task_id": DEMO_TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": "PASS",
        "request_count": len(requests_index),
        "response_count": len(responses_index),
        "warnings_count": warnings_count,
        "thread_id": THREAD_ID,
        "paths": {
            "thread_index": relpath(thread_index_path, repo_root),
            "capability_matrix": relpath(capability_matrix_path, repo_root),
            "thread": relpath(thread_path, repo_root),
            "events": relpath(events_path, repo_root),
            "scope_impact": relpath(scope_impact_path, repo_root),
            "sanctum_state": relpath(sanctum_state_path, repo_root),
        },
        "git": {
            "head": run_git(repo_root, "rev-parse", "HEAD"),
            "branch": run_git(repo_root, "branch", "--show-current"),
            "worktree_dirty": bool(run_git(repo_root, "status", "--short")),
        },
        "forbidden_claims": [
            "LIVE_AUTONOMOUS_ORGAN_INTELLIGENCE",
            "PRODUCTION_READY",
        ],
    }

    report_path = report_dir / "ORGAN_DIALOGUE_DEMO_RUN_REPORT.json"
    write_json(report_path, run_report)

    print(f"builder_verdict=PASS")
    print(f"run_report={relpath(report_path, repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
