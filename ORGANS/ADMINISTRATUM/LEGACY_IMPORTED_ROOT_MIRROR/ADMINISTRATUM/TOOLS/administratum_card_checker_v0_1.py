from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TASK_ID = "TASK-NEWGEN-ADMINISTRATUM-REGISTRATION-CARDS-CURRENT-TRUTH-PC-V0_1"
HERE = Path(__file__).resolve()
ADMIN_ROOT = HERE.parents[1]
REPORT_ROOT = ADMIN_ROOT / "REPORTS" / TASK_ID
DEFAULT_OUTPUT = REPORT_ROOT / "receipts" / "schema_validation_receipt.json"

try:
    from jsonschema import validate as jsonschema_validate
except Exception:  # pragma: no cover - fallback is intentional
    jsonschema_validate = None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _enforce_output_path(path: Path, allow_external: bool) -> None:
    if allow_external:
        return
    resolved_report = REPORT_ROOT.resolve()
    resolved_path = path.resolve()
    if resolved_report not in resolved_path.parents and resolved_path != resolved_report:
        raise SystemExit(f"Output path must stay under {resolved_report} unless --allow-external-output is used.")


def _record(results: list[dict[str, Any]], check_id: str, status: str, detail: str) -> None:
    results.append({"check_id": check_id, "status": status, "detail": detail})


def _validate_instance(
    *,
    schema: dict[str, Any],
    instance: Any,
    label: str,
    results: list[dict[str, Any]],
) -> None:
    if jsonschema_validate is None:
        _record(results, f"schema.{label}", "WARN", "jsonschema package unavailable; validation skipped")
        return
    try:
        jsonschema_validate(instance=instance, schema=schema)
        _record(results, f"schema.{label}", "PASS", "instance validates")
    except Exception as exc:
        _record(results, f"schema.{label}", "FAIL", f"validation failed: {exc}")


def run_checks() -> dict[str, Any]:
    results: list[dict[str, Any]] = []

    paths = {
        "organ_schema": ADMIN_ROOT / "REGISTRATION_CARDS" / "schemas" / "organ_card_schema_v0_1.json",
        "block_schema": ADMIN_ROOT / "REGISTRATION_CARDS" / "schemas" / "block_card_schema_v0_1.json",
        "task_schema": ADMIN_ROOT / "REGISTRATION_CARDS" / "schemas" / "task_session_card_schema_v0_1.json",
        "warp_schema": ADMIN_ROOT / "REGISTRATION_CARDS" / "schemas" / "warp_session_card_schema_v0_1.json",
        "artifact_schema": ADMIN_ROOT / "REGISTRATION_CARDS" / "schemas" / "artifact_card_schema_v0_1.json",
        "cli_schema": ADMIN_ROOT / "REGISTRATION_CARDS" / "schemas" / "cli_worker_report_card_schema_v0_1.json",
        "mechanicus_card": ADMIN_ROOT / "REGISTRATION_CARDS" / "organs" / "mechanicus_organ_card_v0_1.json",
        "officio_card": ADMIN_ROOT / "REGISTRATION_CARDS" / "organs" / "officio_agentis_organ_card_v0_1.json",
        "artifact_index": ADMIN_ROOT / "REGISTRATION_CARDS" / "artifacts" / "accepted_artifacts_index_v0_1.json",
        "block_registry": ADMIN_ROOT / "BLOCKS" / "block_registry_seed_v0_1.json",
    }

    loaded: dict[str, Any] = {}
    for key, path in paths.items():
        if not path.exists():
            _record(results, f"file.{key}", "FAIL", f"missing: {path.as_posix()}")
            continue
        try:
            loaded[key] = _read_json(path)
            _record(results, f"file.{key}", "PASS", f"loaded: {path.as_posix()}")
        except Exception as exc:
            _record(results, f"file.{key}", "FAIL", f"invalid json: {exc}")

    if "organ_schema" in loaded:
        for label in ("mechanicus_card", "officio_card"):
            if label in loaded:
                _validate_instance(
                    schema=loaded["organ_schema"],
                    instance=loaded[label],
                    label=label,
                    results=results,
                )

    if "artifact_schema" in loaded and "artifact_index" in loaded:
        artifacts = loaded["artifact_index"].get("artifacts", [])
        if isinstance(artifacts, list):
            for idx, item in enumerate(artifacts):
                _validate_instance(
                    schema=loaded["artifact_schema"],
                    instance=item,
                    label=f"artifact_index[{idx}]",
                    results=results,
                )
        else:
            _record(results, "schema.artifact_index", "FAIL", "artifacts field must be an array")

    if "block_schema" in loaded and "block_registry" in loaded:
        blocks = loaded["block_registry"].get("blocks", [])
        if isinstance(blocks, list):
            for idx, item in enumerate(blocks):
                _validate_instance(
                    schema=loaded["block_schema"],
                    instance=item,
                    label=f"block_registry[{idx}]",
                    results=results,
                )
        else:
            _record(results, "schema.block_registry", "FAIL", "blocks field must be an array")

    sample_task = {
        "schema_id": "task_session_card_v0_1",
        "session_id": "seed.task.session.001",
        "task_id": TASK_ID,
        "starting_head": "892ae8a6f5452c55211da4748bed3b1d9d3f9326",
        "ending_head": None,
        "task_status": "PLANNED",
        "registration_owner_organ": "ADMINISTRATUM",
        "notes": ["seed sample only"]
    }
    sample_warp = {
        "schema_id": "warp_session_card_v0_1",
        "seed_status": "FUTURE_COMPATIBLE_SEED",
        "session_id": "seed.warp.session.001",
        "task_id": "FUTURE_TASK_ID",
        "starting_head": "HEAD_PLACEHOLDER",
        "workspace_path": "RUNS/WARP/SESSION_001",
        "organ_packets": [],
        "receipts": [],
        "diffs": [],
        "artifacts": [],
        "final_verdict": "FUTURE",
        "absorption_status": "NOT_STARTED"
    }
    sample_cli = {
        "schema_id": "cli_worker_report_card_v0_1",
        "seed_status": "FUTURE_COMPATIBLE_SEED",
        "report_id": "seed.cli.report.001",
        "inspected_organ": "ADMINISTRATUM",
        "inspected_block": "ADMINISTRATUM_CAPABILITY_BLOCK",
        "findings": ["seed schema only"],
        "severity": "INFO",
        "proposed_improvement": "Future worker runtime will populate this field.",
        "evidence": [],
        "approval_status": "FUTURE"
    }

    if "task_schema" in loaded:
        _validate_instance(schema=loaded["task_schema"], instance=sample_task, label="task_session_seed", results=results)
    if "warp_schema" in loaded:
        _validate_instance(schema=loaded["warp_schema"], instance=sample_warp, label="warp_session_seed", results=results)
    if "cli_schema" in loaded:
        _validate_instance(schema=loaded["cli_schema"], instance=sample_cli, label="cli_worker_seed", results=results)

    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    warn_count = sum(1 for r in results if r["status"] == "WARN")
    status = "PASS" if fail_count == 0 and warn_count == 0 else ("WARN" if fail_count == 0 else "FAIL")
    return {
        "task_id": TASK_ID,
        "checker": "administratum_card_checker_v0_1.py",
        "status": status,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "results": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Administratum card files and schema seeds.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--allow-external-output", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    _enforce_output_path(output_path, allow_external=args.allow_external_output)
    report = run_checks()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["fail_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
