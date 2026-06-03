#!/usr/bin/env python3
"""Astronomicon bootstrap template repair helper (UTF-8 no-BOM)."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys

    sys.path.append(str(Path(__file__).resolve().parent))

from astronomicon_bootstrap_preflight_v0_1 import (  # noqa: E402
    DEFAULT_TASK_ID,
    REQUIRED_ORGANS,
    default_route_template_rel,
    default_start_ack_template_rel,
    normalize_path,
    normalize_repo_root,
    required_read_order,
    run_preflight,
    to_posix,
    utc_now,
    write_json,
)

DEFAULT_CAPS_TO_CARRY = [
    "CAP_STAGE1_WITH_WARNINGS_ONLY",
    "CAP_SYNTHETIC_ONLY_UNTIL_REAL_USE_PILOT",
    "CAP_NO_IDE_VISUAL_RELEASE_YET",
    "CAP_NO_WARP_RUNTIME",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def has_utf8_bom(path: Path) -> bool:
    raw = path.read_bytes()
    return len(raw) >= 3 and raw[0:3] == b"\xef\xbb\xbf"


def load_json_allow_bom(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    issues: list[str] = []
    try:
        text = path.read_bytes().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        issues.append(f"UTF-8 decode error: {exc}")
        return None, issues
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        issues.append(f"JSON parse error: {exc}")
        return None, issues
    if not isinstance(payload, dict):
        issues.append("JSON root must be object.")
        return None, issues
    return payload, issues


def default_route_template(repo_root: Path) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "template_id": "TASK_ROUTE_MANIFEST_TEMPLATE_V0_1",
        "task_id": "",
        "taskpack_zip_path": "",
        "extracted_taskpack_path": "",
        "read_order": list(required_read_order(repo_root)),
        "required_organs": list(REQUIRED_ORGANS),
        "entry_ack_required": True,
        "resolver_receipt_required": True,
        "caps_to_carry": list(DEFAULT_CAPS_TO_CARRY),
    }


def default_start_ack_template() -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "template_id": "TASK_START_ACK_TEMPLATE_V0_1",
        "task_id": "",
        "resolved": False,
        "route_manifest_found": False,
        "all_required_organs_reachable": False,
        "organs": {},
        "caps_triggered": [],
        "verdict": "PASS_WITH_WARNINGS/WARN/BLOCK",
    }


def write_json_no_bom(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _repair_single_template(
    path: Path,
    *,
    force: bool,
    fallback_payload: dict[str, Any],
) -> dict[str, Any]:
    action: dict[str, Any] = {
        "path": to_posix(path),
        "force": force,
    }

    if not path.exists():
        write_json_no_bom(path, fallback_payload)
        action.update(
            {
                "operation": "CREATED_MISSING_TEMPLATE",
                "before_exists": False,
                "after_exists": True,
                "after_sha256": sha256_file(path),
                "after_has_utf8_bom": has_utf8_bom(path),
                "source_payload": "fallback_default",
            }
        )
        return action

    before_sha = sha256_file(path)
    before_bom = has_utf8_bom(path)
    payload, parse_issues = load_json_allow_bom(path)

    action["before_exists"] = True
    action["before_sha256"] = before_sha
    action["before_has_utf8_bom"] = before_bom
    action["before_json_parse_issues"] = parse_issues

    if not force:
        action.update(
            {
                "operation": "SKIPPED_EXISTING_NO_FORCE",
                "after_sha256": before_sha,
                "after_has_utf8_bom": before_bom,
            }
        )
        return action

    if payload is None:
        payload = fallback_payload
        action["source_payload"] = "fallback_default_due_parse_failure"
    else:
        action["source_payload"] = "existing_payload"

    write_json_no_bom(path, payload)
    after_sha = sha256_file(path)
    after_bom = has_utf8_bom(path)

    action.update(
        {
            "operation": "REWRITTEN_FORCE_UTF8_NO_BOM",
            "after_sha256": after_sha,
            "after_has_utf8_bom": after_bom,
            "content_changed": before_sha != after_sha,
        }
    )
    return action


def run_repair(
    repo_root: str | Path = ".",
    *,
    route_template_path: str | Path | None = None,
    start_ack_template_path: str | Path | None = None,
    force: bool = False,
    task_id: str = DEFAULT_TASK_ID,
) -> dict[str, Any]:
    repo = normalize_repo_root(repo_root)
    route_path = normalize_path(route_template_path or default_route_template_rel(repo), repo)
    start_path = normalize_path(start_ack_template_path or default_start_ack_template_rel(repo), repo)

    actions = [
        _repair_single_template(route_path, force=force, fallback_payload=default_route_template(repo)),
        _repair_single_template(start_path, force=force, fallback_payload=default_start_ack_template()),
    ]

    post_preflight = run_preflight(
        repo_root=repo,
        route_template_path=route_path,
        start_ack_template_path=start_path,
        task_id=task_id,
    )

    caps_closed_or_reduced: list[str] = []
    for action in actions:
        op = action.get("operation")
        before_bom = bool(action.get("before_has_utf8_bom"))
        if op == "CREATED_MISSING_TEMPLATE":
            if str(action.get("path", "")).endswith("TASK_ROUTE_MANIFEST_TEMPLATE.json"):
                caps_closed_or_reduced.append("CAP_ASTRONOMICON_ROUTE_TEMPLATE_MISSING")
            if str(action.get("path", "")).endswith("TASK_START_ACK_TEMPLATE.json"):
                caps_closed_or_reduced.append("CAP_ASTRONOMICON_START_ACK_TEMPLATE_MISSING")
        if op == "REWRITTEN_FORCE_UTF8_NO_BOM" and before_bom:
            caps_closed_or_reduced.append("CAP_ASTRONOMICON_TEMPLATE_UTF8_BOM_PRESENT")

    if post_preflight.get("verdict") == "BLOCK":
        verdict = "BLOCK"
    elif post_preflight.get("verdict") == "PASS_WITH_WARNINGS":
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    return {
        "task_id": task_id,
        "timestamp_utc": utc_now(),
        "repo_root": to_posix(repo),
        "force": force,
        "actions": actions,
        "caps_closed_or_reduced": sorted(set(caps_closed_or_reduced)),
        "post_preflight_receipt": post_preflight,
        "post_preflight_caps": post_preflight.get("caps_triggered", []),
        "verdict": verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair Astronomicon bootstrap templates (UTF-8 no-BOM).")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--route-template-path", default="", help="Override route template path.")
    parser.add_argument("--start-ack-template-path", default="", help="Override start-ack template path.")
    parser.add_argument("--force", action="store_true", help="Allow rewriting existing files.")
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID, help="Task ID for receipt metadata.")
    parser.add_argument("--receipt-path", default="", help="If set, write repair receipt JSON to this path.")
    args = parser.parse_args()

    receipt = run_repair(
        repo_root=args.repo_root,
        route_template_path=args.route_template_path or None,
        start_ack_template_path=args.start_ack_template_path or None,
        force=args.force,
        task_id=args.task_id,
    )

    if args.receipt_path:
        write_json(normalize_path(args.receipt_path, normalize_repo_root(args.repo_root)), receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 1 if receipt.get("verdict") == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
