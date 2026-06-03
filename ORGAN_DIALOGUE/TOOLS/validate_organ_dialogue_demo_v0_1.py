#!/usr/bin/env python3
"""Validate Organ Dialogue demo artifacts against foundation-only acceptance checks."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-ORGAN-DIALOGUE-DEMO-VM2-V0_1"
DEMO_TASK_ID = "TASK-DEMO-ORGAN-DIALOGUE-V0_1"
THREAD_ID = "THREAD-TASK-DEMO-ORGAN-DIALOGUE-V0_1"

SCHEMA_RELS = [
    "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/SCHEMAS/ORGAN_DIALOGUE_REQUEST_V0_1.schema.json",
    "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/SCHEMAS/ORGAN_DIALOGUE_RESPONSE_V0_1.schema.json",
    "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/SCHEMAS/ORGAN_DIALOGUE_THREAD_V0_1.schema.json",
    "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/SCHEMAS/ORGAN_DIALOGUE_EVENT_V0_1.schema.json",
    "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/SCHEMAS/ORGAN_DIALOGUE_SCOPE_IMPACT_V0_1.schema.json",
]

THREAD_REL = (
    "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/THREADS/TASK-DEMO-ORGAN-DIALOGUE-V0_1/"
    "ORGAN_DIALOGUE_THREAD_V0_1.generated.json"
)
EVENTS_REL = (
    "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/THREADS/TASK-DEMO-ORGAN-DIALOGUE-V0_1/"
    "ORGAN_DIALOGUE_EVENTS_V0_1.generated.jsonl"
)
SCOPE_IMPACT_REL = (
    "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/THREADS/TASK-DEMO-ORGAN-DIALOGUE-V0_1/"
    "SCOPE_IMPACT/ORGAN_DIALOGUE_SCOPE_IMPACT_V0_1.generated.json"
)
REQUESTS_DIR_REL = "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/THREADS/TASK-DEMO-ORGAN-DIALOGUE-V0_1/REQUESTS"
RESPONSES_DIR_REL = "IMPERIUM_NEW_GENERATION/ORGAN_DIALOGUE/THREADS/TASK-DEMO-ORGAN-DIALOGUE-V0_1/RESPONSES"
SANCTUM_STATE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/sanctum_ng_state.generated.json"

REQUIRED_REPORT_FILES = [
    "FINAL_OWNER_REPORT_RU.md",
    "FINAL_RECEIPT.json",
    "POST_COMMIT_CLOSURE_RECEIPT.json",
    "ORGAN_DIALOGUE_DEMO_RUN_REPORT.json",
    "STEP_PROOF_RECORDS.jsonl",
    "CONTEXT_WINDOW_USAGE_NOTE.md",
    "CONTEXT_SOURCE_REPORT.md",
    "CONTEXT_SOURCE_REPORT.json",
    "KPD_SLICE.md",
    "NEXT_TASK_IMPROVEMENT_REPORT.md",
    "NEXT_TASK_IMPROVEMENT_REPORT.json",
    "OFFICIO_ROLE_ACK_OR_WARN.json",
    "DOCTRINARIUM_LAW_ACK_OR_WARN.json",
    "SUPER_SKEPTICISM_ACK.json",
    "GATE_ACK.md",
]

PRIVATE_KEY_MARKERS = [
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN RSA PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
    "api_key=",
    "xoxb-",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    if not isinstance(data, dict):
        return None, "not_json_object"
    return data, None


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]] | None, str | None]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return None, "missing"

    out: list[dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        text = line.strip()
        if not text:
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            return None, f"jsonl_decode_error_line_{idx}:{exc}"
        if not isinstance(value, dict):
            return None, f"jsonl_not_object_line_{idx}"
        out.append(value)
    return out, None


def add_check(
    checks: list[dict[str, str]],
    warnings: list[str],
    blockers: list[str],
    check_id: str,
    ok: bool,
    detail_ok: str,
    detail_fail: str,
    fail_level: str = "BLOCK",
) -> None:
    if ok:
        checks.append({"check_id": check_id, "status": "PASS", "details": detail_ok})
        return

    checks.append({"check_id": check_id, "status": fail_level, "details": detail_fail})
    if fail_level == "WARN":
        warnings.append(f"{check_id}:{detail_fail}")
    else:
        blockers.append(f"{check_id}:{detail_fail}")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/"
        "TASK-20260523-NEWGEN-SANCTUM-ORGAN-DIALOGUE-DEMO-VM2-V0_1"
    )

    parser = argparse.ArgumentParser(description="Validate Organ Dialogue demo artifacts.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "VALIDATOR_REPORT.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output = args.output.resolve()

    checks: list[dict[str, str]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    schema_paths = [repo_root / rel for rel in SCHEMA_RELS]
    add_check(
        checks,
        warnings,
        blockers,
        "schemas_exist",
        all(path.exists() for path in schema_paths),
        "all Organ Dialogue schemas exist",
        "one or more Organ Dialogue schemas are missing",
    )

    schema_parse_ok = True
    for path in schema_paths:
        payload, err = load_json(path)
        if payload is None:
            schema_parse_ok = False
            warnings.append(f"schema_parse_failed:{relpath(path, repo_root)}:{err}")
    add_check(
        checks,
        warnings,
        blockers,
        "schemas_parse",
        schema_parse_ok,
        "all schemas parse as JSON objects",
        "one or more schemas failed to parse",
    )

    thread_path = repo_root / THREAD_REL
    thread_obj, thread_err = load_json(thread_path)
    add_check(
        checks,
        warnings,
        blockers,
        "thread_exists",
        thread_obj is not None,
        "thread file exists and parses",
        f"thread missing or invalid ({thread_err})",
    )

    requests_dir = repo_root / REQUESTS_DIR_REL
    responses_dir = repo_root / RESPONSES_DIR_REL
    request_paths = sorted(requests_dir.glob("*.request.json"))
    response_paths = sorted(responses_dir.glob("*.response.json"))

    add_check(
        checks,
        warnings,
        blockers,
        "request_count_is_8",
        len(request_paths) == 8,
        "8 request packets found",
        f"expected 8 requests, found {len(request_paths)}",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "response_count_is_8",
        len(response_paths) == 8,
        "8 response packets found",
        f"expected 8 responses, found {len(response_paths)}",
    )

    request_ids: set[str] = set()
    request_parse_ok = True
    for path in request_paths:
        obj, err = load_json(path)
        if obj is None:
            request_parse_ok = False
            warnings.append(f"request_parse_failed:{relpath(path, repo_root)}:{err}")
            continue
        rid = str(obj.get("request_id", "")).strip()
        if rid:
            request_ids.add(rid)

    response_parse_ok = True
    broken_links: list[str] = []
    not_foundation_only: list[str] = []
    illegal_live_fields: list[str] = []
    for path in response_paths:
        obj, err = load_json(path)
        if obj is None:
            response_parse_ok = False
            warnings.append(f"response_parse_failed:{relpath(path, repo_root)}:{err}")
            continue

        request_id = str(obj.get("request_id", "")).strip()
        if request_id not in request_ids:
            broken_links.append(str(path.name))

        if obj.get("foundation_only") is not True:
            not_foundation_only.append(str(path.name))

        for key in ["live_autonomy", "autonomous_execution", "production_ready"]:
            if key in obj and obj.get(key) is True:
                illegal_live_fields.append(f"{path.name}:{key}")

    add_check(
        checks,
        warnings,
        blockers,
        "responses_link_to_valid_requests",
        response_parse_ok and not broken_links,
        "every response links to a valid request",
        f"broken response->request links: {broken_links}",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "responses_foundation_only",
        response_parse_ok and not not_foundation_only,
        "all responses include foundation_only=true",
        f"responses without foundation_only=true: {not_foundation_only}",
    )

    add_check(
        checks,
        warnings,
        blockers,
        "no_live_autonomous_claim_in_responses",
        response_parse_ok and not illegal_live_fields,
        "responses do not claim live/autonomous/production booleans",
        f"illegal live/autonomous fields in responses: {illegal_live_fields}",
    )

    scope_impact_path = repo_root / SCOPE_IMPACT_REL
    scope_obj, scope_err = load_json(scope_impact_path)
    add_check(
        checks,
        warnings,
        blockers,
        "scope_impact_exists",
        scope_obj is not None,
        "scope impact record exists and parses",
        f"scope impact missing or invalid ({scope_err})",
    )

    sanctum_state_path = repo_root / SANCTUM_STATE_REL
    sanctum_state, sanctum_err = load_json(sanctum_state_path)
    demo_ref_ok = False
    if sanctum_state is not None:
        demo = sanctum_state.get("organ_dialogue_demo")
        if isinstance(demo, dict):
            demo_ref_ok = (
                str(demo.get("task_id", "")) == DEMO_TASK_ID
                and int(demo.get("request_count", 0)) == 8
                and int(demo.get("response_count", 0)) == 8
                and str(demo.get("foundation_only_label", "")) == "FOUNDATION_ONLY"
            )
    add_check(
        checks,
        warnings,
        blockers,
        "sanctum_state_references_demo",
        demo_ref_ok,
        "Sanctum state references Organ Dialogue demo",
        f"Sanctum state missing/invalid Organ Dialogue reference ({sanctum_err})",
    )

    report_file_presence = all((report_dir / name).exists() for name in REQUIRED_REPORT_FILES)
    add_check(
        checks,
        warnings,
        blockers,
        "report_bundle_exists",
        report_file_presence,
        "required report bundle files exist",
        "required report bundle files are missing",
        fail_level="WARN",
    )

    key_scan_paths = [
        thread_path,
        repo_root / EVENTS_REL,
        scope_impact_path,
        *request_paths,
        *response_paths,
    ]
    private_key_hits: list[str] = []
    for path in key_scan_paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in PRIVATE_KEY_MARKERS:
            if marker in text:
                private_key_hits.append(f"{relpath(path, repo_root)}:{marker}")

    add_check(
        checks,
        warnings,
        blockers,
        "no_private_key_material",
        not private_key_hits,
        "no private key material detected in Organ Dialogue artifacts",
        f"private key markers found: {private_key_hits}",
    )

    no_fake_green_ok = False
    if thread_obj is not None and scope_obj is not None:
        thread_foundation = thread_obj.get("foundation_only") is True and thread_obj.get("live_autonomy") is False
        claims_not_proved = scope_obj.get("claims_not_proved", [])
        if not isinstance(claims_not_proved, list):
            claims_not_proved = []

        claims_lower = {str(item).strip().lower() for item in claims_not_proved}
        no_fake_green_ok = thread_foundation and {
            "live_autonomous_organ_intelligence",
            "production_backend_ready",
        }.issubset(claims_lower)

    add_check(
        checks,
        warnings,
        blockers,
        "no_fake_green_claim",
        no_fake_green_ok,
        "foundation-only/no-fake-green boundaries are explicit",
        "missing explicit no-fake-green boundary evidence",
    )

    events_obj, events_err = load_jsonl(repo_root / EVENTS_REL)
    add_check(
        checks,
        warnings,
        blockers,
        "events_jsonl_parse",
        events_obj is not None,
        "events JSONL parses",
        f"events JSONL missing/invalid ({events_err})",
    )

    if thread_obj is not None:
        add_check(
            checks,
            warnings,
            blockers,
            "thread_identity",
            str(thread_obj.get("thread_id", "")) == THREAD_ID and str(thread_obj.get("demo_task_id", "")) == DEMO_TASK_ID,
            "thread_id and demo_task_id are correct",
            "thread_id or demo_task_id mismatch",
        )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_id": "ORGAN_DIALOGUE_DEMO_VALIDATOR_REPORT_V0_1",
        "task_id": str(args.task_id),
        "demo_task_id": DEMO_TASK_ID,
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "checks": checks,
        "warnings": warnings,
        "blockers": blockers,
        "validated_paths": {
            "schemas": SCHEMA_RELS,
            "thread": THREAD_REL,
            "events": EVENTS_REL,
            "scope_impact": SCOPE_IMPACT_REL,
            "requests_dir": REQUESTS_DIR_REL,
            "responses_dir": RESPONSES_DIR_REL,
            "sanctum_state": SANCTUM_STATE_REL,
            "report_dir": relpath(report_dir, repo_root) if report_dir.exists() else str(report_dir),
        },
        "no_fake_green_note": "PASS/WARN proves deterministic file-backed foundation dialogue only; no live autonomy or production readiness claim.",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"validator_verdict={verdict}")
    print(f"validator_report={relpath(output, repo_root)}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
