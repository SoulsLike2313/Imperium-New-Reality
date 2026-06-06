from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_excerpt(value: str, limit: int = 400) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...<truncated>"


def make_receipt_id(task_id: str, capability_id: str, check_name: str) -> str:
    safe_task = task_id.lower().replace(" ", "-")
    safe_cap = capability_id.lower().replace(" ", "-")
    safe_check = check_name.lower().replace(" ", "-")
    return f"{safe_task}:{safe_cap}:{safe_check}"


def build_validation_receipt(
    *,
    task_id: str,
    capability_id: str,
    validator: str,
    check_name: str,
    command_or_check: str,
    exit_code: int | None,
    stdout_text: str,
    stderr_text: str,
    side_effects: list[str],
    network_used: bool,
    files_created_or_modified: list[str],
    validation_verdict: str,
    promotion_recommendation: str,
    evidence_paths: list[str],
    warnings: list[str] | None = None,
    violations: list[str] | None = None,
) -> dict[str, Any]:
    status = "PASS"
    verdict_upper = validation_verdict.upper()
    if verdict_upper in {"FAIL", "BLOCKED"}:
        status = verdict_upper
    elif verdict_upper in {"PASS_WITH_WARNINGS", "MISSING"}:
        status = "PASS_WITH_WARNINGS"

    summary = (
        f"{capability_id}: {validation_verdict} via {check_name}. "
        f"promotion_recommendation={promotion_recommendation}"
    )
    return {
        "receipt_id": make_receipt_id(task_id, capability_id, check_name),
        "task_id": task_id,
        "capability_id": capability_id,
        "validator": validator,
        "checked_at_utc": utc_now(),
        "status": status,
        "summary": summary,
        "check_name": check_name,
        "command_or_check": command_or_check,
        "exit_code": exit_code,
        "stdout_excerpt": short_excerpt(stdout_text),
        "stderr_excerpt": short_excerpt(stderr_text),
        "side_effects": side_effects,
        "network_used": network_used,
        "files_created_or_modified": files_created_or_modified,
        "validation_verdict": validation_verdict,
        "promotion_recommendation": promotion_recommendation,
        "warnings": warnings or [],
        "violations": violations or [],
        "evidence_paths": evidence_paths,
    }


def write_receipt(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a Mechanicus validation receipt JSON payload.",
    )
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--capability-id", required=True)
    parser.add_argument("--validator", required=True)
    parser.add_argument("--check-name", required=True)
    parser.add_argument("--command-or-check", required=True)
    parser.add_argument("--exit-code", type=int, default=0)
    parser.add_argument("--stdout", default="")
    parser.add_argument("--stderr", default="")
    parser.add_argument("--side-effects-json", default="[]")
    parser.add_argument("--files-json", default="[]")
    parser.add_argument("--network-used", action="store_true")
    parser.add_argument("--validation-verdict", required=True)
    parser.add_argument("--promotion-recommendation", required=True)
    parser.add_argument("--evidence-paths-json", default="[]")
    parser.add_argument("--warnings-json", default="[]")
    parser.add_argument("--violations-json", default="[]")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    side_effects = json.loads(args.side_effects_json)
    files_touched = json.loads(args.files_json)
    evidence_paths = json.loads(args.evidence_paths_json)
    warnings = json.loads(args.warnings_json)
    violations = json.loads(args.violations_json)

    payload = build_validation_receipt(
        task_id=args.task_id,
        capability_id=args.capability_id,
        validator=args.validator,
        check_name=args.check_name,
        command_or_check=args.command_or_check,
        exit_code=args.exit_code,
        stdout_text=args.stdout,
        stderr_text=args.stderr,
        side_effects=side_effects,
        network_used=bool(args.network_used),
        files_created_or_modified=files_touched,
        validation_verdict=args.validation_verdict,
        promotion_recommendation=args.promotion_recommendation,
        evidence_paths=evidence_paths,
        warnings=warnings,
        violations=violations,
    )
    write_receipt(Path(args.output), payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
