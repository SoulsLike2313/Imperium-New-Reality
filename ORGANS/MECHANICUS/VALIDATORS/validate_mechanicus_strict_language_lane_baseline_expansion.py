#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "MECHANICUS-STRICT-LANGUAGE-LANE-BASELINE-EXPANSION-0001"
VALIDATOR_ID = "mechanicus_strict_language_lane_baseline_expansion_validator.v0_1"

MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_STRICT_LANGUAGE_LANE_BASELINE_EXPANSION_MATRIX_V0_1.json")
CUSTODES = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_STRICT_LANGUAGE_LANE_BASELINE_EXPANSION_PROSECUTOR_MATRIX_V0_1.json")
THRONE = Path("ORGANS/THRONE/MATRICES/THRONE_STRICT_LANGUAGE_LANE_BASELINE_EXPANSION_CROWN_GATE_MATRIX_V0_1.json")
DISPATCH_TOOL = Path("ORGANS/MECHANICUS/TOOLS/run_language_validation_dispatch.py")
READOUT_TOOL = Path("ORGANS/MECHANICUS/TOOLS/generate_strict_language_lane_readout.py")
DISPATCH_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_VALIDATION_BASELINE_V0_1.json")
LANE_READOUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_language_lane_baseline_expansion_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_BASELINE_EXPANSION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_BASELINE_EXPANSION_REPORT_V0_1.md")
ACTIVE_LANES = {"python", "powershell", "rust", "node_frontend", "css_ui", "json_evidence", "markdown_docs", "toml_config"}

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def has_all(text: str, needles: List[str]) -> bool:
    return all(n in text for n in needles)

def run_py(repo: Path, tool: Path, out: Path, timeout: int = 240):
    p = subprocess.run([sys.executable, str(repo / tool), "--repo-root", str(repo), "--out", out.as_posix()],
        cwd=str(repo), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return {"exit_code": p.returncode, "stdout_tail": p.stdout[-5000:], "stderr_tail": p.stderr[-3000:], "out_exists": (repo / out).is_file()}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    for name, path, needles in [
        ("baseline_expansion_matrix", MATRIX, ["Baseline expansion is not strict cleanliness", "expanded_lanes", "JSON evidence parse debt"]),
        ("custodes_baseline_expansion_matrix", CUSTODES, ["prosecutor_not_helper", "strict_build_claimed_from_baseline", "json_evidence_debt_hidden"]),
        ("throne_baseline_expansion_matrix", THRONE, ["No lane may become strict-clean", "claim npm build pass without npm build"]),
    ]:
        data, err = load_json(repo / path) if (repo / path).is_file() else ({}, "missing")
        ok = err is None and has_all(json.dumps(data, ensure_ascii=False), needles)
        add(checks, f"{name}_exists_and_declares_boundaries", ok, {"path": path.as_posix(), "error": err})
        if not ok:
            errors.append(f"{name} missing or incomplete")

    dispatch_installed = (repo / DISPATCH_TOOL).is_file() and "mechanicus_language_validator_dispatch_baseline.v0_2_lane_expanded" in (repo / DISPATCH_TOOL).read_text(encoding="utf-8", errors="replace")
    add(checks, "lane_expanded_dispatch_tool_installed", dispatch_installed, {"path": DISPATCH_TOOL.as_posix()})
    if not dispatch_installed:
        errors.append("lane-expanded dispatch tool not installed")
    readout_installed = (repo / READOUT_TOOL).is_file() and "mechanicus_strict_language_lane_readout.v0_2_lane_expanded" in (repo / READOUT_TOOL).read_text(encoding="utf-8", errors="replace")
    add(checks, "lane_expanded_readout_tool_installed", readout_installed, {"path": READOUT_TOOL.as_posix()})
    if not readout_installed:
        errors.append("lane-expanded readout tool not installed")

    dispatch_data = {}
    readout_data = {}
    if not errors:
        r = run_py(repo, DISPATCH_TOOL, DISPATCH_REPORT, timeout=240)
        add(checks, "lane_expanded_dispatch_runs_and_writes_report", r["exit_code"] == 0 and r["out_exists"], r)
        if r["exit_code"] != 0 or not r["out_exists"]:
            errors.append("lane-expanded dispatch did not run/write report")
        else:
            dispatch_data, dispatch_err = load_json(repo / DISPATCH_REPORT)
            lane_ids = {c.get("lane_id") for c in dispatch_data.get("checks", []) if isinstance(c, dict)} if isinstance(dispatch_data, dict) else set()
            coverage_ok = ACTIVE_LANES.issubset(lane_ids) and dispatch_data.get("verdict") != "PASS_100_CLEAN"
            add(checks, "dispatch_report_covers_active_lanes_and_does_not_claim_100_clean", coverage_ok, {"error": dispatch_err, "lane_ids": sorted(lane_ids), "missing": sorted(ACTIVE_LANES - lane_ids), "verdict": dispatch_data.get("verdict") if isinstance(dispatch_data, dict) else None})
            if not coverage_ok:
                errors.append("dispatch report does not cover active lanes or risks fake 100 clean claim")
    if not errors:
        r = run_py(repo, READOUT_TOOL, LANE_READOUT, timeout=180)
        add(checks, "lane_expanded_readout_runs_and_writes_report", r["exit_code"] == 0 and r["out_exists"], r)
        if r["exit_code"] != 0 or not r["out_exists"]:
            errors.append("lane-expanded readout did not run/write report")
        else:
            readout_data, readout_err = load_json(repo / LANE_READOUT)
            lanes = {l.get("lane_id"): l for l in readout_data.get("lanes", []) if isinstance(l, dict)} if isinstance(readout_data, dict) else {}
            foundation_only = [lane_id for lane_id, lane in lanes.items() if lane.get("state") == "LANE_FOUNDATION_ONLY" and lane_id in ACTIVE_LANES]
            readout_ok = readout_err is None and not foundation_only and readout_data.get("verdict") != "PASS_100_CLEAN"
            add(checks, "active_lanes_no_longer_foundation_only_and_no_100_clean_claim", readout_ok, {"error": readout_err, "foundation_only_active_lanes": foundation_only, "state_counts": readout_data.get("state_counts") if isinstance(readout_data, dict) else None, "verdict": readout_data.get("verdict") if isinstance(readout_data, dict) else None})
            if not readout_ok:
                errors.append("some active lanes remain foundation-only or readout risks fake 100 clean")

    if isinstance(dispatch_data, dict) and dispatch_data.get("validation_debt"):
        warnings.append("Expanded baseline contains validation debt; expected until strict lane validators are implemented.")
        for d in dispatch_data.get("validation_debt", [])[:8]:
            warnings.append(f"Validation debt: {d.get('lane_id')} / {d.get('language')} visible_errors={d.get('error_count_visible')}")
    if isinstance(readout_data, dict):
        for lane in readout_data.get("lanes", []) or []:
            if lane.get("state") in {"LANE_MEASURED_WITH_DEBT", "LANE_TOOLCHAIN_MISSING", "LANE_FUTURE_CAPABILITY"}:
                warnings.append(f"Lane state: {lane.get('lane_id')} => {lane.get('state')}")

    verdict = "PASS_MECHANICUS_STRICT_LANGUAGE_LANE_BASELINE_EXPANSION_READY" if not errors else "FAIL_MECHANICUS_STRICT_LANGUAGE_LANE_BASELINE_EXPANSION"
    generated = utc()
    summary = {"summary_id": "mechanicus.strict_language_lane_baseline_expansion_summary.v0_1", "task_id": TASK_ID, "validator_id": VALIDATOR_ID, "verdict": verdict, "generated_at_utc": generated, "checks": checks, "errors": errors, "warnings": warnings, "dispatch_report": DISPATCH_REPORT.as_posix(), "lane_readout": LANE_READOUT.as_posix(), "state_counts": readout_data.get("state_counts", {}) if isinstance(readout_data, dict) else {}, "meaning": "Expands baseline validation so active strict language lanes have lane-specific baseline evidence instead of remaining foundation-only."}
    receipt = {"receipt_id": "receipt.mechanicus.strict_language_lane_baseline_expansion.v0_1", "task_id": TASK_ID, "validator_id": VALIDATOR_ID, "verdict": verdict, "generated_at_utc": generated, "checks": checks, "errors": errors, "warnings": warnings, "dispatch_report": DISPATCH_REPORT.as_posix(), "lane_readout": LANE_READOUT.as_posix()}
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    state_md = "\n".join(f"- `{k}`: `{v}`" for k, v in (readout_data.get("state_counts", {}) if isinstance(readout_data, dict) else {}).items()) or "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS STRICT LANGUAGE LANE BASELINE EXPANSION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Active lanes now have lane-specific baseline evidence.

This should reduce `LANE_FOUNDATION_ONLY` for PowerShell, Rust, Node frontend and CSS UI without pretending that strict build/lint/type/security lanes are complete.

## Lane state counts

{state_md}

## Boundary

```text
Baseline expansion is not strict cleanliness.
cargo check and npm build are still separate strict build lanes.
```

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}
""", encoding="utf-8")
    print(json.dumps({"task_id": TASK_ID, "validator_id": VALIDATOR_ID, "verdict": verdict, "receipt": RECEIPT.as_posix(), "summary": SUMMARY.as_posix(), "dispatch_report": DISPATCH_REPORT.as_posix(), "lane_readout": LANE_READOUT.as_posix(), "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
