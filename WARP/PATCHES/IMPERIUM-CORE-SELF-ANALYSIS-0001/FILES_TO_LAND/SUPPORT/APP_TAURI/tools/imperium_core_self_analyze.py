#!/usr/bin/env python3
"""Imperium Core self-analysis orchestrator.

Runs the current two-organ baseline:
- Astronomicon: patch-pack inventory and registration shape visibility.
- Mechanicus: app code topology and monolith/zone visibility.

No LLM, no execution gateway, no UI mutation.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID = "IMPERIUM-CORE-SELF-ANALYSIS-0001"
VERDICT = "PASS_IMPERIUM_CORE_SELF_ANALYSIS_READY"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def run_py(repo_root: Path, script: str, extra: list[str]) -> dict[str, Any]:
    script_path = repo_root / script
    if not script_path.exists():
        return {"ok": False, "exit_code": None, "error": f"missing script: {script}", "stdout_tail": [], "stderr_tail": []}
    cmd = [sys.executable, str(script_path), "--repo-root", str(repo_root), *extra]
    try:
        proc = subprocess.run(cmd, cwd=str(repo_root), text=True, capture_output=True, timeout=120)
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "cmd": cmd,
            "stdout_tail": proc.stdout.splitlines()[-8:],
            "stderr_tail": proc.stderr.splitlines()[-8:],
            "error": None if proc.returncode == 0 else "script returned non-zero",
        }
    except Exception as exc:
        return {"ok": False, "exit_code": None, "cmd": cmd, "stdout_tail": [], "stderr_tail": [], "error": str(exc)}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing": path.as_posix()}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    astra_run = run_py(repo_root, "ORGANS/ASTRONOMICON/TOOLS/build_astronomicon_patch_pack_inventory.py", ["--compact"])
    mech_run = run_py(repo_root, "ORGANS/MECHANICUS/TOOLS/build_mechanicus_code_topology.py", ["--scope", "SUPPORT/APP_TAURI", "--compact"])
    if not astra_run["ok"]:
        errors.append(f"Astronomicon inventory failed: {astra_run.get('error')}")
    if not mech_run["ok"]:
        errors.append(f"Mechanicus topology failed: {mech_run.get('error')}")

    astra_summary_path = repo_root / "ORGANS" / "ASTRONOMICON" / "REPORTS" / "ASTRONOMICON_PATCH_PACK_INVENTORY_SUMMARY_V0_1.json"
    mech_summary_path = repo_root / "ORGANS" / "MECHANICUS" / "REPORTS" / "MECHANICUS_CODE_TOPOLOGY_SUMMARY_V0_1.json"
    astra = read_json(astra_summary_path)
    mech = read_json(mech_summary_path)
    if "missing" in astra:
        errors.append(f"missing Astronomicon summary: {astra['missing']}")
    if "missing" in mech:
        errors.append(f"missing Mechanicus summary: {mech['missing']}")

    if isinstance(astra.get("warnings"), list):
        warnings.extend(["ASTRA: " + w for w in astra.get("warnings", [])[:4]])
    if isinstance(mech.get("warnings"), list):
        warnings.extend(["MECH: " + w for w in mech.get("warnings", [])[:4]])

    verdict = VERDICT if not errors else "FAIL_IMPERIUM_CORE_SELF_ANALYSIS"
    summary = {
        "task_id": TASK_ID,
        "validator_id": "imperium_core_self_analysis.v0_1",
        "verdict": verdict,
        "generated_at_utc": utc_now(),
        "core_name": "Imperium Core",
        "mode": "terminal_first_two_organ_self_analysis",
        "astronomicon": {
            "pack_count": astra.get("pack_count"),
            "standard_pack_count": astra.get("standard_pack_count"),
            "candidate_pack_count": astra.get("candidate_pack_count"),
            "legacy_or_incomplete_count": astra.get("legacy_or_incomplete_count"),
            "dirty_nested_warp_count": astra.get("dirty_nested_warp_count"),
            "long_path_blocker_count": astra.get("long_path_blocker_count"),
            "summary_path": rel(repo_root, astra_summary_path),
        },
        "mechanicus": {
            "scope": mech.get("scope"),
            "file_count": mech.get("file_count"),
            "total_lines": mech.get("total_lines"),
            "monolith_risk_count": mech.get("monolith_risk_count"),
            "blocking_monolith_count": mech.get("blocking_monolith_count"),
            "node_boundary_count": mech.get("node_boundary_count"),
            "top_monoliths": mech.get("top_monoliths", []),
            "summary_path": rel(repo_root, mech_summary_path),
        },
        "next_recommended_patch": "IMPERIUM-CORE-APP-MONOLITH-SPLIT-PLAN-0001",
        "no_llm_dependency": True,
        "real_execution_gateway_claim": False,
        "core_v1_claim": False,
        "errors": errors,
        "warnings": warnings,
    }

    app_receipts = repo_root / "SUPPORT" / "APP_TAURI" / "receipts"
    app_receipts.mkdir(parents=True, exist_ok=True)
    summary_path = app_receipts / "imperium_core_self_analysis_summary.json"
    receipt_path = app_receipts / "imperium_core_self_analysis_receipt.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    receipt = dict(summary)
    receipt.update({
        "astronomicon_run": astra_run,
        "mechanicus_run": mech_run,
        "summary": rel(repo_root, summary_path),
    })
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.compact:
        print(f"TASK: {TASK_ID}")
        print(f"VERDICT: {verdict}")
        print(
            "ASTRA: "
            f"packs={summary['astronomicon']['pack_count']} "
            f"standard={summary['astronomicon']['standard_pack_count']} "
            f"candidate={summary['astronomicon']['candidate_pack_count']} "
            f"legacy={summary['astronomicon']['legacy_or_incomplete_count']} "
            f"dirty={summary['astronomicon']['dirty_nested_warp_count']}"
        )
        print(
            "MECH: "
            f"files={summary['mechanicus']['file_count']} "
            f"lines={summary['mechanicus']['total_lines']} "
            f"monoliths={summary['mechanicus']['monolith_risk_count']} "
            f"blockers={summary['mechanicus']['blocking_monolith_count']} "
            f"nodes={summary['mechanicus']['node_boundary_count']}"
        )
        print(f"SUMMARY: {rel(repo_root, summary_path)}")
        print(f"RECEIPT: {rel(repo_root, receipt_path)}")
        if warnings:
            print("WARNINGS: " + " | ".join(warnings[:3]))
        if errors:
            print("ERRORS: " + " | ".join(errors[:3]))
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
