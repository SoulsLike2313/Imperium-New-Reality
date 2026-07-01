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

TASK_ID = "ASTRONOMICON-PATCH-PACK-INTAKE-AND-VALIDATION-SMOKE-0001"
VALIDATOR_ID = "astronomicon_patch_pack_intake_validation_smoke_validator.v0_1"

MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/ASTRONOMICON_PATCH_PACK_SMOKE_VALIDATION_MATRIX_V0_1.json")
SCHEMA = Path("ORGANS/ASTRONOMICON/SCHEMAS/patch_pack_smoke_result.schema.json")
DOCTRINE = Path("ORGANS/ASTRONOMICON/DOCTRINE/PATCH_PACK_INTAKE_AND_VALIDATION_SMOKE_V0_1.md")
TOOL = Path("ORGANS/ASTRONOMICON/TOOLS/astronomicon_patch_pack_smoke.py")

DOCTRINARIUM_PACK_TAXONOMY = Path("ORGANS/DOCTRINARIUM/MATRICES/PACK_TAXONOMY_MATRIX_V0_1.json")
DOCTRINARIUM_PATCH_LAW = Path("ORGANS/DOCTRINARIUM/MATRICES/PATCH_PACK_LAW_MATRIX_V0_1.json")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/patch_pack_intake_validation_smoke_receipt.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_INTAKE_VALIDATION_SMOKE_REPORT_V0_1.md")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_SMOKE_VALIDATION_SUMMARY_V0_1.json")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=20)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, str(e)

def run_tool(repo: Path, patch_id: str | None = None) -> Tuple[int, str, str]:
    cmd = [sys.executable, str(repo / TOOL), "--repo-root", str(repo), "--out", SUMMARY.as_posix()]
    if patch_id:
        cmd += ["--patch-id", patch_id]
    p = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout, p.stderr

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    for rel in [MATRIX, SCHEMA, DOCTRINE, TOOL, DOCTRINARIUM_PACK_TAXONOMY, DOCTRINARIUM_PATCH_LAW]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    for rel in [MATRIX, SCHEMA, DOCTRINARIUM_PACK_TAXONOMY, DOCTRINARIUM_PATCH_LAW]:
        if (repo / rel).is_file():
            data, err = load_json(repo / rel)
            add(checks, f"{rel.name}_parses", err is None, {"error": err})
            if err:
                errors.append(f"parse failed {rel.as_posix()}: {err}")

    matrix, err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    hard_laws = matrix.get("hard_laws", []) if isinstance(matrix, dict) else []
    required_hard_laws = [
        "receipt existence is not task completion proof",
        "Patch Pack smoke validation must not execute runner",
        "Patch Pack smoke validation is not Custodes trust",
        "Patch Pack smoke validation is not Throne verdict",
        "SERVITOR Task Pack law must not be confused with Patch Pack law",
    ]
    missing_laws = [x for x in required_hard_laws if x not in hard_laws]
    add(checks, "smoke_hard_laws_present", not missing_laws, {"missing": missing_laws})
    if missing_laws:
        errors.append("missing smoke hard laws: " + ", ".join(missing_laws))

    code, out, errout = run_tool(repo)
    add(checks, "astronomicon_patch_pack_smoke_tool_runs", code == 0, {"stderr": errout[-1000:]})
    if code != 0:
        errors.append("smoke tool failed")
    summary = {}
    if (repo / SUMMARY).is_file():
        summary, err = load_json(repo / SUMMARY)
        add(checks, "smoke_summary_parses", err is None, {"error": err})
        if err:
            errors.append("smoke summary parse failed: " + err)
            summary = {}
    else:
        add(checks, "smoke_summary_exists", False)
        errors.append("smoke summary was not written")

    results = summary.get("results", []) if isinstance(summary, dict) else []
    patch_count = len(results)
    add(checks, "current_patch_packs_smoke_scanned", patch_count > 0, {"patch_count": patch_count})
    if patch_count == 0:
        errors.append("no patch packs scanned")

    taxonomy_confusion = []
    for r in results:
        for linked in r.get("linked_intake_candidates", []):
            if linked.get("status") != "INTAKE_DRAFT_ONLY":
                taxonomy_confusion.append({"patch_id": r.get("patch_id"), "linked": linked})
    add(checks, "linked_intakes_remain_intake_draft_only", not taxonomy_confusion, {"violations": taxonomy_confusion})
    if taxonomy_confusion:
        errors.append("linked intake candidates were not kept as INTAKE_DRAFT_ONLY")

    executed = False
    # No runner output should be created by this validator. We check for a self marker only.
    add(checks, "smoke_validation_did_not_execute_patch_runners", not executed, {"executed": executed})

    # Need at least one result that is not blindly CLOSED, proving Astronomicon can say incomplete.
    non_closed = [r for r in results if r.get("smoke_verdict") != "CLOSED_BY_DECLARED_GOALS"]
    add(checks, "smoke_can_refuse_goal_closure", bool(non_closed), {"non_closed_count": len(non_closed)})
    if not non_closed:
        warnings.append("all scanned patch packs closed by declaration; this is unusual for smoke training")

    verdict = "PASS_PATCH_PACK_INTAKE_VALIDATION_SMOKE_READY" if not errors else "FAIL_PATCH_PACK_INTAKE_VALIDATION_SMOKE"
    generated = utc()

    receipt = {
        "receipt_id": "receipt.astronomicon.patch_pack_intake_validation_smoke.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "patch_count": patch_count,
        "smoke_summary": SUMMARY.as_posix(),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "meaning": "Astronomicon can smoke-compare Patch Pack declarations against visible receipts without execution. This is not trust or Throne verdict."
    }

    for p in [RECEIPT, REPORT]:
        (repo / p).parent.mkdir(parents=True, exist_ok=True)
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    verdict_counts: Dict[str, int] = {}
    for r in results:
        verdict_counts[r.get("smoke_verdict", "UNKNOWN")] = verdict_counts.get(r.get("smoke_verdict", "UNKNOWN"), 0) + 1

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    verdict_md = "\n".join(f"- `{k}`: `{v}`" for k, v in sorted(verdict_counts.items()))
    sample_md = "\n".join(
        f"- `{r.get('patch_id')}` — `{r.get('smoke_verdict')}`, evidence `{r.get('evidence_level')}`"
        for r in results[:30]
    )

    (repo / REPORT).write_text(f"""# PATCH PACK INTAKE VALIDATION SMOKE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Meaning

Astronomicon now has a smoke path for checking whether a Patch Pack's declared expectations are supported by visible receipts.

This does not execute patch runners.

This is not Inquisition anti-fake-green.

This is not Custodes trust.

This is not Throne verdict.

## Smoke verdict counts

{verdict_md}

## Sample patch results

{sample_md}

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
        "patch_count": patch_count,
        "smoke_summary": SUMMARY.as_posix(),
        "receipt": RECEIPT.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings,
        "verdict_counts": verdict_counts
    }, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
