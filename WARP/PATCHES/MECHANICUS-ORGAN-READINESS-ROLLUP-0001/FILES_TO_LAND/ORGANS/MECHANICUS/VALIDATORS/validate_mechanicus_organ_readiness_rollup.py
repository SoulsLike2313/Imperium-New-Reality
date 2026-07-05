#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "MECHANICUS-ORGAN-READINESS-ROLLUP-0001"
VALIDATOR_ID = "mechanicus_organ_readiness_rollup_validator.v0_1"

LAW = Path("ORGANS/MECHANICUS/LAWS/MECHANICUS_ORGAN_READINESS_ROLLUP_LAW_V0_1.json")
MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_ORGAN_READINESS_ROLLUP_MATRIX_V0_1.json")
CUSTODES_MATRIX = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_MECHANICUS_READINESS_ROLLUP_PROSECUTOR_MATRIX_V0_1.json")
THRONE_MATRIX = Path("ORGANS/THRONE/MATRICES/THRONE_MECHANICUS_READINESS_ROLLUP_CROWN_GATE_MATRIX_V0_1.json")
BUILDER = Path("ORGANS/MECHANICUS/TOOLS/build_mechanicus_organ_readiness_rollup.py")
ROLLUP_JSON = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_V0_1.json")
ROLLUP_MD = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_V0_1.md")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_ORGAN_READINESS_ROLLUP_VALIDATION_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_organ_readiness_rollup_receipt.json")

REQUIRED_ROLLUP_SECTIONS = [
    "repo_context",
    "organ_identity",
    "proven_baseline_capabilities",
    "assembly_gate_map",
    "forbidden_claims",
    "current_blockers",
    "next_patch_queue",
    "deferred_future_capabilities",
    "local_model_membrane_hook",
    "no_fake_green_guard"
]


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as exc:
        return None, str(exc)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None) -> None:
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})


def text_has_all(data: Any, needles: List[str]) -> bool:
    text = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data
    return all(n in text for n in needles)


def run_builder(repo: Path) -> Dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(repo / BUILDER), "--repo-root", str(repo)],
        cwd=str(repo),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=240
    )
    return {
        "exit_code": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-3000:],
        "rollup_json_exists": (repo / ROLLUP_JSON).is_file(),
        "rollup_md_exists": (repo / ROLLUP_MD).is_file()
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    required_static = [
        ("rollup_law", LAW, ["DEFERRED_AFTER_CORE_V1", "Readiness rollup is a measured truth index", "overclaim_is_blocking_failure"]),
        ("rollup_matrix", MATRIX, ["local_model_membrane_deferral", "rollup_claims_mechanicus_assembled", "minimum_pass_score"]),
        ("custodes_prosecutor_matrix", CUSTODES_MATRIX, ["overclaim_attack", "llm_magic_attack", "PROSECUTOR_TARGET_DECLARED_NOT_FULL_AUDIT"]),
        ("throne_crown_gate_matrix", THRONE_MATRIX, ["CROWN_GATE_TARGET_DECLARED_NOT_CLOSED", "LOCAL_MODEL_REQUIRED_FOR_CORE_V1"]),
    ]
    for name, path, needles in required_static:
        full = repo / path
        data, err = load_json(full) if full.is_file() else ({}, "missing")
        ok = err is None and text_has_all(data, needles)
        add(checks, f"{name}_exists_and_declares_required_boundaries", ok, {"path": path.as_posix(), "error": err})
        if not ok:
            errors.append(f"{name} missing or incomplete")

    builder_ok = (repo / BUILDER).is_file()
    add(checks, "rollup_builder_exists", builder_ok, {"path": BUILDER.as_posix()})
    if not builder_ok:
        errors.append("rollup builder missing")

    rollup: Dict[str, Any] = {}
    if not errors:
        run = run_builder(repo)
        add(checks, "rollup_builder_runs_and_writes_outputs", run["exit_code"] == 0 and run["rollup_json_exists"] and run["rollup_md_exists"], run)
        if run["exit_code"] != 0 or not run["rollup_json_exists"] or not run["rollup_md_exists"]:
            errors.append("rollup builder failed or outputs missing")
        else:
            loaded, load_err = load_json(repo / ROLLUP_JSON)
            rollup = loaded if isinstance(loaded, dict) else {}
            add(checks, "rollup_json_parse", load_err is None and isinstance(loaded, dict), {"error": load_err})
            if load_err is not None or not isinstance(loaded, dict):
                errors.append("rollup JSON cannot be parsed")

    if rollup:
        missing_sections = [s for s in REQUIRED_ROLLUP_SECTIONS if s not in rollup]
        add(checks, "rollup_contains_required_sections", not missing_sections, {"missing_sections": missing_sections})
        if missing_sections:
            errors.append("rollup missing required sections")

        verdict_ok = rollup.get("verdict") == "PASS_ROLLUP_CREATED_MECHANICUS_NOT_ASSEMBLED" and rollup.get("status") == "MEASURED_NOT_ASSEMBLED"
        add(checks, "rollup_verdict_is_not_assembled", verdict_ok, {"verdict": rollup.get("verdict"), "status": rollup.get("status")})
        if not verdict_ok:
            errors.append("rollup verdict/status does not preserve not-assembled truth")

        assembled_claim_ok = rollup.get("mechanicus_assembled") is False and rollup.get("organ_assembled_claim_allowed") is False
        add(checks, "rollup_blocks_mechanicus_assembled_claim", assembled_claim_ok, {
            "mechanicus_assembled": rollup.get("mechanicus_assembled"),
            "organ_assembled_claim_allowed": rollup.get("organ_assembled_claim_allowed")
        })
        if not assembled_claim_ok:
            errors.append("rollup allows/claims Mechanicus assembled")

        gates = rollup.get("assembly_gate_map", [])
        gate_ok = isinstance(gates, list) and len(gates) >= 8 and all(g.get("may_raise_assembled_claim") is False for g in gates if isinstance(g, dict))
        add(checks, "assembly_gate_map_present_and_non_closing", gate_ok, {"gate_count": len(gates) if isinstance(gates, list) else None})
        if not gate_ok:
            errors.append("assembly gate map missing or closing incorrectly")

        caps = rollup.get("proven_baseline_capabilities", [])
        add(checks, "baseline_capabilities_visible", isinstance(caps, list) and len(caps) >= 5, {"count": len(caps) if isinstance(caps, list) else None})
        if not isinstance(caps, list) or len(caps) < 5:
            errors.append("too few baseline capabilities visible")

        guard = rollup.get("no_fake_green_guard", {})
        guard_ok = all(guard.get(k) is True for k in [
            "build_proof_is_not_code_purity",
            "tool_inventory_is_not_tool_admission_v2",
            "planner_is_not_execution_authority",
            "rollup_is_not_crown_verdict",
            "local_model_is_not_inner_authority"
        ])
        add(checks, "no_fake_green_guard_complete", guard_ok, guard)
        if not guard_ok:
            errors.append("no fake-green guard incomplete")

        membrane = rollup.get("local_model_membrane_hook", {})
        membrane_ok = (
            membrane.get("status") == "DEFERRED_AFTER_CORE_V1" and
            membrane.get("near_term_dependency") is False and
            membrane.get("core_v1_dependency") is False
        )
        add(checks, "local_model_membrane_marked_deferred_not_dependency", membrane_ok, membrane)
        if not membrane_ok:
            errors.append("local model membrane is not correctly deferred")

        blockers = rollup.get("current_blockers", [])
        if blockers:
            warnings.append(f"Mechanicus assembly blockers visible: {len(blockers)}")
        else:
            errors.append("no blockers visible; likely fake-green")

    verdict = "PASS_MECHANICUS_ORGAN_READINESS_ROLLUP_READY" if not errors else "FAIL_MECHANICUS_ORGAN_READINESS_ROLLUP"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.organ_readiness_rollup_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "rollup_json": ROLLUP_JSON.as_posix(),
        "rollup_md": ROLLUP_MD.as_posix(),
        "meaning": "Mechanicus now has a script-generated readiness rollup. This is visibility, not organ assembly closure."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.organ_readiness_rollup.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "law": LAW.as_posix(),
        "matrix": MATRIX.as_posix(),
        "custodes_matrix": CUSTODES_MATRIX.as_posix(),
        "throne_matrix": THRONE_MATRIX.as_posix(),
        "rollup_json": ROLLUP_JSON.as_posix(),
        "rollup_md": ROLLUP_MD.as_posix(),
        "no_fake_green_statement": "PASS here means rollup exists and preserves NOT_ASSEMBLED truth; it does not mean Mechanicus organ closure."
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"

    (repo / REPORT).parent.mkdir(parents=True, exist_ok=True)
    (repo / REPORT).write_text(f"""# MECHANICUS ORGAN READINESS ROLLUP VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

This validator proves the readiness rollup exists, is script-generated, contains required sections, and does not falsely claim Mechanicus assembly closure.

It does not prove Mechanicus is assembled.

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Runtime outputs

- `{ROLLUP_JSON.as_posix()}`
- `{ROLLUP_MD.as_posix()}`
- `{SUMMARY.as_posix()}`
- `{RECEIPT.as_posix()}`
""", encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "rollup_json": ROLLUP_JSON.as_posix(),
        "rollup_md": ROLLUP_MD.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
