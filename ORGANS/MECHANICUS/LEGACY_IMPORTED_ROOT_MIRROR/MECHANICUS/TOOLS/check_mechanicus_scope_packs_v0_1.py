from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import jsonschema
except Exception:  # pragma: no cover - optional runtime dependency
    jsonschema = None


TASK_ID_DEFAULT = "TASK-NEWGEN-MECHANICUS-CAPABILITY-SCOPE-EXPORT-PC-V0_1"
REQUIRED_SCOPE_FILES: dict[str, str] = {
    "code_quality_task": "scope_code_quality_task_v0_1.json",
    "json_schema_validation_task": "scope_json_schema_validation_task_v0_1.json",
    "mechanicus_tool_validation_task": "scope_mechanicus_tool_validation_task_v0_1.json",
    "controlled_tool_provision_task": "scope_controlled_tool_provision_task_v0_1.json",
    "repo_hygiene_task": "scope_repo_hygiene_task_v0_1.json",
    "taskpack_generation_task": "scope_taskpack_generation_task_v0_1.json",
    "visual_readiness_task": "scope_visual_readiness_task_v0_1.json",
}
REQUIRED_PACK_FIELDS: tuple[str, ...] = (
    "scope_id",
    "version",
    "generated_at_utc",
    "source_registry",
    "purpose",
    "target_task_types",
    "canon_allowed",
    "sandbox_allowed",
    "candidate_context_only",
    "owner_decision_required",
    "forbidden",
    "required_receipts",
    "required_gates",
    "warnings",
    "examples_of_use",
    "future_promotion_candidates",
    "forbidden_actions",
    "last_generated_from_commit",
)
SCOPE_BUCKETS: tuple[str, ...] = (
    "canon_allowed",
    "sandbox_allowed",
    "candidate_context_only",
    "owner_decision_required",
    "forbidden",
)
RESERVED_CATEGORIES = {"LOCAL_LLM", "CLOUD_LLM_ADAPTERS"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_repo_root(path_hint: Path) -> Path:
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path_hint,
            text=True,
        ).strip()
        if root:
            return Path(root)
    except Exception:
        pass
    return path_hint


def expected_status_for_bucket(bucket: str) -> str | None:
    mapping = {
        "canon_allowed": "CANON",
        "sandbox_allowed": "SANDBOX",
        "candidate_context_only": "CANDIDATE",
    }
    return mapping.get(bucket)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Mechanicus scope packs for structure, policy guards, and fake-CANON drift.")
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--registry",
        default="IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/REGISTRY/arsenal_registry_v0_1.json",
    )
    parser.add_argument(
        "--scope-root",
        default="IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/SCOPE_PACKS/V0_1",
    )
    parser.add_argument(
        "--schema-path",
        default="scope_pack_schema_v0_1.json",
        help="File name in scope-root or absolute path.",
    )
    parser.add_argument(
        "--report-output",
        required=True,
        help="Report output path (absolute or repo-relative).",
    )
    args = parser.parse_args()

    repo_root = resolve_repo_root(Path(args.repo_root).resolve())
    registry_path = (repo_root / args.registry).resolve()
    scope_root = (repo_root / args.scope_root).resolve()

    schema_path = Path(args.schema_path)
    if not schema_path.is_absolute():
        schema_path = scope_root / schema_path

    report_output = Path(args.report_output)
    if not report_output.is_absolute():
        report_output = (repo_root / report_output).resolve()

    registry = read_json(registry_path)
    cards = registry.get("cards", [])
    if not isinstance(cards, list):
        raise RuntimeError("Registry cards must be a list.")

    cards_by_id: dict[str, dict[str, Any]] = {}
    for card in cards:
        if not isinstance(card, dict):
            continue
        capability_id = str(card.get("capability_id", "")).strip()
        if capability_id:
            cards_by_id[capability_id] = card

    schema_payload: dict[str, Any] | None = None
    if schema_path.exists():
        data = read_json(schema_path)
        if isinstance(data, dict):
            schema_payload = data

    errors: list[str] = []
    warnings: list[str] = []
    fake_canon_rows: list[dict[str, str]] = []
    unknown_capability_rows: list[dict[str, str]] = []
    bucket_status_mismatch_rows: list[dict[str, str]] = []
    non_reserved_owner_decision_rows: list[dict[str, str]] = []
    overlap_rows: list[dict[str, str]] = []
    scope_summaries: list[dict[str, Any]] = []

    loaded_packs: dict[str, dict[str, Any]] = {}

    for scope_id, filename in REQUIRED_SCOPE_FILES.items():
        path = scope_root / filename
        if not path.exists():
            errors.append(f"missing_scope_pack:{filename}")
            continue

        payload = read_json(path)
        if not isinstance(payload, dict):
            errors.append(f"invalid_json_object:{filename}")
            continue
        loaded_packs[scope_id] = payload

        for field in REQUIRED_PACK_FIELDS:
            if field not in payload:
                errors.append(f"missing_field:{filename}:{field}")

        # Lightweight schema/type checks independent from jsonschema package.
        for field in SCOPE_BUCKETS:
            value = payload.get(field, [])
            if not isinstance(value, list):
                errors.append(f"bucket_not_list:{filename}:{field}")

        if schema_payload and jsonschema is not None:
            try:
                jsonschema.validate(payload, schema_payload)
            except Exception as exc:
                errors.append(f"schema_validation_failed:{filename}:{exc}")
        elif schema_payload is None:
            warnings.append("schema_file_missing_or_unreadable")
        elif jsonschema is None:
            warnings.append("jsonschema_package_unavailable_schema_validation_skipped")

        # Bucket overlap checks.
        bucket_sets: dict[str, set[str]] = {}
        for field in SCOPE_BUCKETS:
            raw = payload.get(field, [])
            typed = {str(item).strip() for item in raw if str(item).strip()}
            bucket_sets[field] = typed
        all_fields = list(SCOPE_BUCKETS)
        for i, left in enumerate(all_fields):
            for right in all_fields[i + 1 :]:
                overlap = sorted(bucket_sets[left] & bucket_sets[right])
                if overlap:
                    overlap_rows.append(
                        {
                            "scope_id": scope_id,
                            "left": left,
                            "right": right,
                            "overlap_count": str(len(overlap)),
                        }
                    )

        # Capability-to-status checks.
        for bucket_name in SCOPE_BUCKETS:
            expected_status = expected_status_for_bucket(bucket_name)
            for capability_id in bucket_sets[bucket_name]:
                card = cards_by_id.get(capability_id)
                if card is None:
                    unknown_capability_rows.append({"scope_id": scope_id, "capability_id": capability_id})
                    continue

                status = str(card.get("status", "")).strip()
                category = str(card.get("category", "")).strip()
                if bucket_name == "canon_allowed" and status != "CANON":
                    fake_canon_rows.append(
                        {
                            "scope_id": scope_id,
                            "capability_id": capability_id,
                            "registry_status": status,
                        }
                    )
                if expected_status and status != expected_status:
                    bucket_status_mismatch_rows.append(
                        {
                            "scope_id": scope_id,
                            "bucket": bucket_name,
                            "capability_id": capability_id,
                            "registry_status": status,
                            "expected_status": expected_status,
                        }
                    )
                if bucket_name == "owner_decision_required" and category not in RESERVED_CATEGORIES:
                    non_reserved_owner_decision_rows.append(
                        {
                            "scope_id": scope_id,
                            "capability_id": capability_id,
                            "category": category,
                        }
                    )

        forbidden_actions = payload.get("forbidden_actions", [])
        if not isinstance(forbidden_actions, list) or not forbidden_actions:
            errors.append(f"missing_forbidden_actions:{filename}")

        scope_summaries.append(
            {
                "scope_id": scope_id,
                "path": path.relative_to(repo_root).as_posix(),
                "canon_allowed_count": len(bucket_sets["canon_allowed"]),
                "sandbox_allowed_count": len(bucket_sets["sandbox_allowed"]),
                "candidate_context_only_count": len(bucket_sets["candidate_context_only"]),
                "owner_decision_required_count": len(bucket_sets["owner_decision_required"]),
                "forbidden_count": len(bucket_sets["forbidden"]),
            }
        )

    if unknown_capability_rows:
        errors.append(f"unknown_capabilities={len(unknown_capability_rows)}")
    if overlap_rows:
        errors.append(f"bucket_overlap_rows={len(overlap_rows)}")
    if bucket_status_mismatch_rows:
        errors.append(f"bucket_status_mismatch_rows={len(bucket_status_mismatch_rows)}")
    if fake_canon_rows:
        errors.append(f"fake_canon_rows={len(fake_canon_rows)}")

    if non_reserved_owner_decision_rows:
        warnings.append(f"owner_decision_non_reserved_rows={len(non_reserved_owner_decision_rows)}")

    # Acceptance-specific guard checks.
    controlled = loaded_packs.get("controlled_tool_provision_task", {})
    controlled_forbidden_actions = [str(x).lower() for x in controlled.get("forbidden_actions", [])]
    if not any("silent install" in item for item in controlled_forbidden_actions):
        errors.append("controlled_provision_missing_silent_install_forbid")

    visual = loaded_packs.get("visual_readiness_task", {})
    visual_forbidden_actions = [str(x).lower() for x in visual.get("forbidden_actions", [])]
    required_visual_phrases = [
        "react/vite project creation",
        "playwright browser install",
        "visual prototype comparison",
        "llm/cloud activation",
    ]
    for phrase in required_visual_phrases:
        if not any(phrase in item for item in visual_forbidden_actions):
            errors.append(f"visual_readiness_missing_forbid:{phrase}")

    code_quality = loaded_packs.get("code_quality_task", {})
    combined_code_quality_ids = {
        str(x).strip()
        for bucket_name in SCOPE_BUCKETS
        for x in code_quality.get(bucket_name, [])
        if str(x).strip()
    }
    required_code_quality_caps = {
        "CODE_QUALITY_JSONSCHEMA",
        "CODE_QUALITY_RUFF",
        "CODE_QUALITY_MYPY",
        "CODE_QUALITY_PRE_COMMIT",
        "CODE_QUALITY_PYTEST",
        "CODE_QUALITY_PY_COMPILE",
    }
    missing_code_quality_caps = sorted(required_code_quality_caps - combined_code_quality_ids)
    if missing_code_quality_caps:
        errors.append("code_quality_missing_required_caps=" + ",".join(missing_code_quality_caps))

    fake_canon_count = len(fake_canon_rows)
    verdict = "PASS" if not errors else "FAIL"
    report = {
        "task_id": args.task_id,
        "generated_at_utc": utc_now(),
        "checker": "check_mechanicus_scope_packs_v0_1.py",
        "verdict": verdict,
        "notes": errors if errors else ["all checks passed"],
        "warnings": warnings,
        "summary": {
            "required_scope_pack_count": len(REQUIRED_SCOPE_FILES),
            "existing_scope_pack_count": len(loaded_packs),
            "scope_pack_summary": scope_summaries,
            "fake_canon_count": fake_canon_count,
            "unknown_capability_count": len(unknown_capability_rows),
            "status_mismatch_count": len(bucket_status_mismatch_rows),
            "overlap_count": len(overlap_rows),
            "owner_decision_non_reserved_count": len(non_reserved_owner_decision_rows),
        },
        "raw_dump_status": "COMPACT_ONLY",
        "fake_canon_rows": fake_canon_rows[:100],
        "unknown_capability_rows": unknown_capability_rows[:100],
        "bucket_status_mismatch_rows": bucket_status_mismatch_rows[:100],
        "bucket_overlap_rows": overlap_rows[:100],
        "non_reserved_owner_decision_rows": non_reserved_owner_decision_rows[:100],
        "missing_code_quality_capabilities": missing_code_quality_caps,
    }

    write_json(report_output, report)
    print(
        json.dumps(
            {
                "task_id": args.task_id,
                "verdict": verdict,
                "errors": len(errors),
                "fake_canon_count": fake_canon_count,
            },
            ensure_ascii=False,
        )
    )
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
