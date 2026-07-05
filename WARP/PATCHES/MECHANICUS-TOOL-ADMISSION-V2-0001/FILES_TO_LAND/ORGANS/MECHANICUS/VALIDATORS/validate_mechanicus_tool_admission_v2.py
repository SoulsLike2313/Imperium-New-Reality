#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path
from datetime import datetime, timezone

TASK_ID = "MECHANICUS-TOOL-ADMISSION-V2-0001"
VALIDATOR_ID = "mechanicus_tool_admission_v2_validator.v0_1"
REQUIRED_STATIC = [
    "ORGANS/MECHANICUS/LAWS/MECHANICUS_TOOL_ADMISSION_V2_LAW_V0_1.json",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_ADMISSION_V2_SCHEMA_V0_1.json",
    "ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_ADMISSION_V2_RISK_MATRIX_V0_1.json",
    "ORGANS/MECHANICUS/TOOLS/build_mechanicus_tool_admission_v2.py",
    "ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_TOOL_ADMISSION_V2_PROSECUTOR_MATRIX_V0_1.json",
    "ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_TOOL_ADMISSION_V2_CROWN_GATE_MATRIX_V0_1.json",
    "ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_INVENTORY_V0_1.json",
    "ORGANS/MECHANICUS/REGISTRY/command_policy.json",
]
REPORT_JSON = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_REPORT_V0_1.json")
SUMMARY_JSON = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_SUMMARY_V0_1.json")
RECEIPT_JSON = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_tool_admission_v2_receipt.json")
VALIDATION_MD = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_VALIDATION_REPORT_V0_1.md")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def import_builder(path: Path):
    spec = importlib.util.spec_from_file_location("build_mechanicus_tool_admission_v2", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(repo_root: Path, apply: bool) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []

    def check(name: str, ok: bool, details=None, blocking=True):
        checks.append({"name": name, "status": "PASS" if ok else ("FAIL" if blocking else "WARN"), "details": details or {}})
        if not ok:
            (errors if blocking else warnings).append(name)

    for rel in REQUIRED_STATIC:
        check(f"exists::{rel}", (repo_root / rel).exists(), {"path": rel})

    # Validate static JSON shape.
    for rel in [p for p in REQUIRED_STATIC if p.endswith('.json')]:
        try:
            load_json(repo_root / rel)
            check(f"json_parse::{rel}", True)
        except Exception as e:
            check(f"json_parse::{rel}", False, {"error": str(e)})

    policy_path = repo_root / "ORGANS/MECHANICUS/REGISTRY/command_policy.json"
    if policy_path.exists():
        policy = load_json(policy_path)
        check("command_policy_forbids_arbitrary_shell", policy.get("arbitrary_shell_execution_allowed") is False, {"value": policy.get("arbitrary_shell_execution_allowed")})
        check("command_policy_has_dry_run_allowlist", isinstance(policy.get("allowlisted_tool_ids_for_dry_run"), list) and len(policy.get("allowlisted_tool_ids_for_dry_run")) > 0, {"count": len(policy.get("allowlisted_tool_ids_for_dry_run") or [])})

    builder_path = repo_root / "ORGANS/MECHANICUS/TOOLS/build_mechanicus_tool_admission_v2.py"
    if builder_path.exists():
        try:
            builder = import_builder(builder_path)
            build_result = builder.build(repo_root, apply=apply)
            check("builder_runs", build_result.get("verdict") == "PASS_MECHANICUS_TOOL_ADMISSION_V2_READY", build_result)
        except Exception as e:
            build_result = {}
            check("builder_runs", False, {"error": str(e)})
    else:
        build_result = {}

    if apply:
        for rel in [REPORT_JSON, SUMMARY_JSON, RECEIPT_JSON]:
            check(f"generated::{rel.as_posix()}", (repo_root / rel).exists(), {"path": rel.as_posix()})

        if (repo_root / REPORT_JSON).exists():
            report = load_json(repo_root / REPORT_JSON)
            required_report_fields = [
                "task_id", "validator_id", "verdict", "source_inventory_path", "source_tool_count",
                "admission_counts_by_v2_status", "execution_mode_counts", "risk_class_counts",
                "real_execution_enabled_count", "admission_records", "errors", "warnings"
            ]
            missing = [f for f in required_report_fields if f not in report]
            check("report_has_required_fields", not missing, {"missing": missing})
            check("report_verdict_pass", report.get("verdict") == "PASS_MECHANICUS_TOOL_ADMISSION_V2_READY", {"verdict": report.get("verdict")})
            check("source_tool_count_positive", int(report.get("source_tool_count") or 0) > 0, {"source_tool_count": report.get("source_tool_count")})
            check("real_execution_enabled_count_zero", int(report.get("real_execution_enabled_count") or 0) == 0, {"real_execution_enabled_count": report.get("real_execution_enabled_count")})
            records = report.get("admission_records") or []
            required_record_fields = load_json(repo_root / "ORGANS/MECHANICUS/MATRICES/MECHANICUS_TOOL_ADMISSION_V2_SCHEMA_V0_1.json").get("required_fields") or []
            missing_record_fields = []
            for idx, rec in enumerate(records[:50]):
                for field in required_record_fields:
                    if field not in rec:
                        missing_record_fields.append({"index": idx, "tool_id": rec.get("tool_id"), "missing": field})
            check("sample_records_have_v2_passport_fields", not missing_record_fields, {"missing_sample": missing_record_fields[:10]})
            check("no_admitted_owner_approved_execution_records", not any(r.get("v2_admission_status") == "ADMITTED_OWNER_APPROVED_EXECUTION" for r in records), {})

        if (repo_root / SUMMARY_JSON).exists():
            summary = load_json(repo_root / SUMMARY_JSON)
            check("summary_verdict_pass", summary.get("verdict") == "PASS_MECHANICUS_TOOL_ADMISSION_V2_READY", {"verdict": summary.get("verdict")})
            check("summary_local_model_deferred", summary.get("local_model_membrane_status") == "DEFERRED_AFTER_CORE_V1", {"local_model_membrane_status": summary.get("local_model_membrane_status")})

    verdict = "PASS_MECHANICUS_TOOL_ADMISSION_V2_READY" if not errors else "FAIL_MECHANICUS_TOOL_ADMISSION_V2"
    result = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": utc_now(),
        "receipt": RECEIPT_JSON.as_posix(),
        "summary": SUMMARY_JSON.as_posix(),
        "report_json": REPORT_JSON.as_posix(),
        "report_md": "ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_ADMISSION_V2_REPORT_V0_1.md",
        "errors": errors,
        "warnings": warnings,
        "checks": checks
    }

    if apply:
        md = [
            "# MECHANICUS TOOL ADMISSION V2 VALIDATION REPORT V0.1",
            "",
            f"Task: `{TASK_ID}`",
            f"Verdict: `{verdict}`",
            f"Generated: `{result['generated_at_utc']}`",
            "",
            "## Checks",
            ""
        ]
        for c in checks:
            md.append(f"- `{c['status']}` {c['name']}")
        md.extend(["", "## Errors", ""])
        md.extend([f"- {e}" for e in errors] or ["- None"])
        md.extend(["", "## Warnings", ""])
        md.extend([f"- {w}" for w in warnings] or ["- None"])
        (repo_root / VALIDATION_MD).parent.mkdir(parents=True, exist_ok=True)
        (repo_root / VALIDATION_MD).write_text("\n".join(md) + "\n", encoding="utf-8")

    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    result = validate(Path(args.repo_root).resolve(), args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"].startswith("PASS_") else 1

if __name__ == "__main__":
    raise SystemExit(main())
