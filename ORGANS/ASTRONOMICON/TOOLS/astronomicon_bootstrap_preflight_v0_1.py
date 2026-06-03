#!/usr/bin/env python3
"""Astronomicon bootstrap preflight checker for route/start templates."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

DEFAULT_TASK_ID = "TASK-NEWGEN-STAGE3-ASTRONOMICON-BOOTSTRAP-HARDENING-UTF8-PREFLIGHT-PC-V0_1"

DEFAULT_ROUTE_TEMPLATE_REL = Path(
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_ROUTE_MANIFEST_TEMPLATE.json"
)
DEFAULT_START_ACK_TEMPLATE_REL = Path(
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_ENTRY_CORRIDOR/TASK_START_ACK_TEMPLATE.json"
)

REQUIRED_ORGANS = [
    "DOCTRINARIUM",
    "OFFICIO_AGENTIS",
    "ASTRONOMICON",
    "ADMINISTRATUM",
    "MECHANICUS",
    "INQUISITION",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
]

REQUIRED_READ_ORDER = [
    "AGENTS.md",
    "IMPERIUM_NEW_GENERATION/MATRIX_SPINE/INDEX/MATRIX_SPINE_INDEX.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/DOCTRINARIUM/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/OFFICIO_AGENTIS/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md",
    "IMPERIUM_NEW_GENERATION/ORGANS/SCHOLA_IMPERIALIS/TASK_PARTICIPATION/READ_FIRST_TASK_PARTICIPATION.md",
]

ROUTE_REQUIRED_FIELDS = [
    "schema_version",
    "template_id",
    "task_id",
    "taskpack_zip_path",
    "extracted_taskpack_path",
    "read_order",
    "required_organs",
    "entry_ack_required",
    "resolver_receipt_required",
]

START_ACK_REQUIRED_FIELDS = [
    "schema_version",
    "template_id",
    "task_id",
    "resolved",
    "route_manifest_found",
    "all_required_organs_reachable",
    "organs",
    "caps_triggered",
    "verdict",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_repo_root(repo_root: str | Path) -> Path:
    return Path(repo_root).expanduser().resolve()


def normalize_path(path: str | Path, repo_root: Path) -> Path:
    p = Path(path).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (repo_root / p).resolve()


def to_posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def has_utf8_bom(raw: bytes) -> bool:
    return len(raw) >= 3 and raw[0:3] == b"\xef\xbb\xbf"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json_utf8(path: Path) -> tuple[dict[str, Any] | None, list[str], bool]:
    issues: list[str] = []
    raw = path.read_bytes()
    bom_present = has_utf8_bom(raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        issues.append(f"UTF-8 decode error: {exc}")
        return None, issues, bom_present
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        issues.append(f"JSON parse error with utf-8: {exc}")
        return None, issues, bom_present
    if not isinstance(payload, dict):
        issues.append("JSON root must be object.")
        return None, issues, bom_present
    return payload, issues, bom_present


def _validate_route_payload(payload: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    issues: list[str] = []
    missing_fields = [field for field in ROUTE_REQUIRED_FIELDS if field not in payload]
    if missing_fields:
        issues.append("Missing required route fields: " + ", ".join(missing_fields))

    organs_missing: list[str] = []
    route_organs = payload.get("required_organs")
    if not isinstance(route_organs, list):
        issues.append("required_organs must be a list.")
        organs_missing = list(REQUIRED_ORGANS)
    else:
        organs_missing = [organ for organ in REQUIRED_ORGANS if organ not in route_organs]
        if organs_missing:
            issues.append("required_organs missing: " + ", ".join(organs_missing))

    read_order_missing: list[str] = []
    read_order = payload.get("read_order")
    if not isinstance(read_order, list):
        issues.append("read_order must be a list.")
        read_order_missing = list(REQUIRED_READ_ORDER)
    else:
        read_order_missing = [entry for entry in REQUIRED_READ_ORDER if entry not in read_order]
        if read_order_missing:
            issues.append("read_order missing required entries: " + ", ".join(read_order_missing))

    return issues, organs_missing, read_order_missing


def _validate_start_ack_payload(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    missing_fields = [field for field in START_ACK_REQUIRED_FIELDS if field not in payload]
    if missing_fields:
        issues.append("Missing required start-ack fields: " + ", ".join(missing_fields))

    if "organs" in payload and not isinstance(payload.get("organs"), dict):
        issues.append("start-ack field 'organs' must be an object.")
    if "caps_triggered" in payload and not isinstance(payload.get("caps_triggered"), list):
        issues.append("start-ack field 'caps_triggered' must be a list.")
    if "verdict" in payload and not isinstance(payload.get("verdict"), str):
        issues.append("start-ack field 'verdict' must be a string.")

    return issues, missing_fields


def run_preflight(
    repo_root: str | Path = ".",
    *,
    route_template_path: str | Path | None = None,
    start_ack_template_path: str | Path | None = None,
    task_id: str = DEFAULT_TASK_ID,
) -> dict[str, Any]:
    repo = normalize_repo_root(repo_root)
    route_path = normalize_path(route_template_path or DEFAULT_ROUTE_TEMPLATE_REL, repo)
    start_path = normalize_path(start_ack_template_path or DEFAULT_START_ACK_TEMPLATE_REL, repo)

    caps: list[str] = []
    warnings: list[str] = []
    route_validation_issues: list[str] = []
    start_ack_validation_issues: list[str] = []
    route_required_organs_missing: list[str] = []
    route_required_read_order_missing: list[str] = []
    start_ack_required_fields_missing: list[str] = []

    route_exists = route_path.exists()
    start_exists = start_path.exists()

    route_utf8_no_bom: bool | None = None
    start_utf8_no_bom: bool | None = None
    route_json_valid: bool | None = None
    start_json_valid: bool | None = None
    route_includes_all_8_organs: bool | None = None
    route_read_order_complete: bool | None = None
    start_ack_required_fields_present: bool | None = None

    route_payload: dict[str, Any] | None = None
    start_payload: dict[str, Any] | None = None

    if not route_exists:
        caps.append("CAP_ASTRONOMICON_ROUTE_TEMPLATE_MISSING")
    else:
        route_payload, read_issues, route_bom_present = _read_json_utf8(route_path)
        route_utf8_no_bom = not route_bom_present
        route_json_valid = len(read_issues) == 0
        if route_bom_present:
            caps.append("CAP_ASTRONOMICON_TEMPLATE_UTF8_BOM_PRESENT")
        if read_issues:
            caps.append("CAP_ASTRONOMICON_ROUTE_TEMPLATE_JSON_INVALID")
            route_validation_issues.extend(read_issues)
        else:
            extra_issues, route_required_organs_missing, route_required_read_order_missing = _validate_route_payload(
                route_payload or {}
            )
            route_validation_issues.extend(extra_issues)
            if route_required_organs_missing:
                caps.append("CAP_ASTRONOMICON_ROUTE_TEMPLATE_MISSING_REQUIRED_ORGANS")
            if route_required_read_order_missing:
                caps.append("CAP_ASTRONOMICON_ROUTE_TEMPLATE_READ_ORDER_INCOMPLETE")
            route_includes_all_8_organs = len(route_required_organs_missing) == 0
            route_read_order_complete = len(route_required_read_order_missing) == 0
            if extra_issues and "CAP_ASTRONOMICON_ROUTE_TEMPLATE_JSON_INVALID" not in caps:
                caps.append("CAP_ASTRONOMICON_ROUTE_TEMPLATE_SCHEMA_INVALID")

    if not start_exists:
        caps.append("CAP_ASTRONOMICON_START_ACK_TEMPLATE_MISSING")
    else:
        start_payload, read_issues, start_bom_present = _read_json_utf8(start_path)
        start_utf8_no_bom = not start_bom_present
        start_json_valid = len(read_issues) == 0
        if start_bom_present:
            caps.append("CAP_ASTRONOMICON_TEMPLATE_UTF8_BOM_PRESENT")
        if read_issues:
            caps.append("CAP_ASTRONOMICON_START_ACK_TEMPLATE_JSON_INVALID")
            start_ack_validation_issues.extend(read_issues)
        else:
            extra_issues, start_ack_required_fields_missing = _validate_start_ack_payload(start_payload or {})
            start_ack_validation_issues.extend(extra_issues)
            start_ack_required_fields_present = len(start_ack_required_fields_missing) == 0 and len(extra_issues) == 0
            if extra_issues:
                caps.append("CAP_ASTRONOMICON_START_ACK_TEMPLATE_SCHEMA_INVALID")

    if route_includes_all_8_organs is None and route_exists and route_json_valid:
        route_includes_all_8_organs = True
    if route_read_order_complete is None and route_exists and route_json_valid:
        route_read_order_complete = True
    if start_ack_required_fields_present is None and start_exists and start_json_valid:
        start_ack_required_fields_present = True

    unique_caps = sorted(set(caps))
    if unique_caps:
        verdict = "BLOCK"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    return {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "repo_root": to_posix(repo),
        "route_template_path": to_posix(route_path),
        "start_ack_template_path": to_posix(start_path),
        "route_template_exists": route_exists,
        "start_ack_template_exists": start_exists,
        "route_template_utf8_no_bom": route_utf8_no_bom,
        "start_ack_template_utf8_no_bom": start_utf8_no_bom,
        "route_template_json_valid": route_json_valid,
        "start_ack_template_json_valid": start_json_valid,
        "route_includes_all_8_organs": route_includes_all_8_organs,
        "route_read_order_complete": route_read_order_complete,
        "start_ack_required_fields_present": start_ack_required_fields_present,
        "route_required_organs_missing": route_required_organs_missing,
        "route_required_read_order_missing": route_required_read_order_missing,
        "start_ack_required_fields_missing": start_ack_required_fields_missing,
        "route_validation_issues": route_validation_issues,
        "start_ack_validation_issues": start_ack_validation_issues,
        "caps_triggered": unique_caps,
        "warnings": warnings,
        "verdict": verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Astronomicon bootstrap template preflight.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--route-template-path", default="", help="Override route template path.")
    parser.add_argument("--start-ack-template-path", default="", help="Override start-ack template path.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID, help="Task ID for receipt metadata.")
    parser.add_argument("--receipt-path", default="", help="If set, write receipt JSON to this path.")
    args = parser.parse_args()

    receipt = run_preflight(
        repo_root=args.repo_root,
        route_template_path=args.route_template_path or None,
        start_ack_template_path=args.start_ack_template_path or None,
        task_id=args.task_id,
    )

    if args.receipt_path:
        write_json(normalize_path(args.receipt_path, normalize_repo_root(args.repo_root)), receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 1 if receipt.get("verdict") == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
