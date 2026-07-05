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

TASK_ID = "MECHANICUS-STRICT-LANGUAGE-LANE-FOUNDATION-0001"
VALIDATOR_ID = "mechanicus_strict_language_lane_foundation_validator.v0_1"

REGISTRY = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_STRICT_LANGUAGE_LANE_REGISTRY_V0_1.json")
MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_STRICT_LANGUAGE_LANE_FOUNDATION_MATRIX_V0_1.json")
CUSTODES = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_STRICT_LANGUAGE_LANE_PROSECUTOR_MATRIX_V0_1.json")
THRONE = Path("ORGANS/THRONE/MATRICES/THRONE_STRICT_LANGUAGE_LANE_CROWN_GATE_MATRIX_V0_1.json")
TOOL = Path("ORGANS/MECHANICUS/TOOLS/generate_strict_language_lane_readout.py")

SURFACE_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_SURFACE_V2_REPORT_V0_1.json")
TOOLCHAIN_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")
DISPATCH_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_VALIDATION_BASELINE_V0_1.json")
LANE_READOUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_strict_language_lane_foundation_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_FOUNDATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_FOUNDATION_REPORT_V0_1.md")

REQUIRED_LANES = {"python", "powershell", "rust", "node_frontend", "css_ui", "json_evidence", "markdown_docs", "toml_config", "go_future", "cpp_future"}

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

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    registry, registry_err = load_json(repo / REGISTRY) if (repo / REGISTRY).is_file() else ({}, "missing")
    lane_ids = {x.get("lane_id") for x in registry.get("lanes", []) if isinstance(x, dict)} if isinstance(registry, dict) else set()
    registry_text = json.dumps(registry, ensure_ascii=False) if isinstance(registry, dict) else ""
    registry_ok = registry_err is None and REQUIRED_LANES.issubset(lane_ids) and has_all(registry_text, [
        "Languages must not be validated in one common bucket",
        "A missing toolchain is capability debt",
        "A baseline lane pass is not 100% code cleanliness"
    ])
    add(checks, "strict_language_lane_registry_exists_and_covers_required_lanes", registry_ok, {
        "path": REGISTRY.as_posix(),
        "error": registry_err,
        "missing_lanes": sorted(REQUIRED_LANES - lane_ids)
    })
    if not registry_ok:
        errors.append("strict language lane registry missing or incomplete")

    matrix, matrix_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    dims = matrix.get("dimensions", []) if isinstance(matrix, dict) else []
    weight_sum = sum(int(d.get("weight", 0)) for d in dims if isinstance(d, dict))
    matrix_text = json.dumps(matrix, ensure_ascii=False) if isinstance(matrix, dict) else ""
    matrix_ok = matrix_err is None and weight_sum == 100 and has_all(matrix_text, [
        "single_common_language_bucket",
        "baseline_claimed_as_100_clean",
        "source_evidence_not_split"
    ])
    add(checks, "strict_language_lane_foundation_matrix_exists_and_weights_100", matrix_ok, {
        "path": MATRIX.as_posix(),
        "error": matrix_err,
        "weight_sum": weight_sum
    })
    if not matrix_ok:
        errors.append("strict language lane foundation matrix missing or weak")

    for name, path, needles in [
        ("custodes_strict_language_lane_matrix", CUSTODES, ["prosecutor_not_helper", "common_bucket_validation", "baseline_as_100_clean"]),
        ("throne_strict_language_lane_matrix", THRONE, ["No common language bucket", "No 100% clean claim", "No missing toolchain"]),
    ]:
        data, err = load_json(repo / path) if (repo / path).is_file() else ({}, "missing")
        ok = err is None and has_all(json.dumps(data, ensure_ascii=False), needles)
        add(checks, f"{name}_exists_and_blocks_fake_lane_readiness", ok, {"path": path.as_posix(), "error": err})
        if not ok:
            errors.append(f"{name} missing or incomplete")

    tool_ok = (repo / TOOL).is_file()
    add(checks, "strict_language_lane_readout_tool_exists", tool_ok, {"path": TOOL.as_posix()})
    if not tool_ok:
        errors.append("strict language lane readout tool missing")

    for name, path in [
        ("surface_v2_report_available", SURFACE_REPORT),
        ("toolchain_report_available", TOOLCHAIN_REPORT),
        ("dispatch_report_available", DISPATCH_REPORT),
    ]:
        ok = (repo / path).is_file()
        add(checks, name, ok, {"path": path.as_posix()})
        if not ok:
            errors.append(f"{name} missing; run previous Mechanicus language surface/toolchain patch first")

    readout_data = {}
    if not errors:
        p = subprocess.run(
            [sys.executable, str(repo / TOOL), "--repo-root", str(repo), "--out", LANE_READOUT.as_posix()],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180
        )
        readout_ok = p.returncode == 0 and (repo / LANE_READOUT).is_file()
        add(checks, "strict_language_lane_readout_tool_runs_and_writes_report", readout_ok, {
            "exit_code": p.returncode,
            "stdout_tail": p.stdout[-3000:],
            "stderr_tail": p.stderr[-3000:],
            "path": LANE_READOUT.as_posix()
        })
        if not readout_ok:
            errors.append("strict language lane readout did not run/write report")
        else:
            readout_data, readout_err = load_json(repo / LANE_READOUT)
            states = readout_data.get("state_counts", {}) if isinstance(readout_data, dict) else {}
            readout_text = json.dumps(readout_data, ensure_ascii=False) if isinstance(readout_data, dict) else ""
            no_fake_ok = readout_err is None and readout_data.get("lane_count", 0) >= len(REQUIRED_LANES) and "100% clean" in readout_text and readout_data.get("verdict") != "PASS_100_CLEAN"
            add(checks, "strict_language_lane_readout_covers_lanes_and_does_not_claim_100_clean", no_fake_ok, {
                "error": readout_err,
                "lane_count": readout_data.get("lane_count") if isinstance(readout_data, dict) else None,
                "state_counts": states,
                "verdict": readout_data.get("verdict") if isinstance(readout_data, dict) else None
            })
            if not no_fake_ok:
                errors.append("strict language lane readout incomplete or risks fake 100% clean claim")

    if isinstance(readout_data, dict):
        states = readout_data.get("state_counts", {})
        if states.get("LANE_MEASURED_WITH_DEBT") or states.get("LANE_TOOLCHAIN_MISSING") or states.get("LANE_FOUNDATION_ONLY"):
            warnings.append("Strict language lanes contain measured debt/foundation-only lanes; expected at this stage.")
        for lane in readout_data.get("lanes", []) or []:
            if lane.get("state") in {"LANE_TOOLCHAIN_MISSING", "LANE_MEASURED_WITH_DEBT"}:
                warnings.append(f"Lane debt: {lane.get('lane_id')} => {lane.get('state')}")

    verdict = "PASS_MECHANICUS_STRICT_LANGUAGE_LANE_FOUNDATION_READY" if not errors else "FAIL_MECHANICUS_STRICT_LANGUAGE_LANE_FOUNDATION"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.strict_language_lane_foundation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "lane_readout": LANE_READOUT.as_posix(),
        "state_counts": readout_data.get("state_counts", {}) if isinstance(readout_data, dict) else {},
        "meaning": "Establishes strict per-language lanes and readout. This is lane foundation, not full code cleanliness."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.strict_language_lane_foundation.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "registry": REGISTRY.as_posix(),
        "foundation_matrix": MATRIX.as_posix(),
        "lane_readout": LANE_READOUT.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    state_md = "\n".join(f"- `{k}`: `{v}`" for k, v in (readout_data.get("state_counts", {}) if isinstance(readout_data, dict) else {}).items()) or "- none"

    (repo / REPORT).write_text(f"""# MECHANICUS STRICT LANGUAGE LANE FOUNDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Mechanicus now has strict per-language lane foundation.

No more one-bucket language validation. Python, PowerShell, Rust, Node frontend, CSS UI, JSON evidence, Markdown docs, TOML config, Go future and C++ future are separate lanes.

## Lane state counts

{state_md}

## Boundary

```text
This is not 100% code cleanliness.
This is lane foundation and measured debt.
```

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}
""", encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "lane_readout": LANE_READOUT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
