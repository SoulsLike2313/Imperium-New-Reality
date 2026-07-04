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

TASK_ID = "MECHANICUS-UI-WORKSHOP-AND-NO-MONOLITH-LAW-0001"
VALIDATOR_ID = "mechanicus_ui_workshop_and_no_monolith_law_validator.v0_1"

LAW = Path("ORGANS/MECHANICUS/LAWS/MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW_V0_1.json")
ARCH_MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_NO_MONOLITH_ARCHITECTURE_MATRIX_V0_1.json")
UI_MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_UI_WORKSHOP_TARGET_PIPELINE_MATRIX_V0_1.json")
CUSTODES = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_NO_MONOLITH_PROSECUTOR_MATRIX_V0_1.json")
THRONE = Path("ORGANS/THRONE/MATRICES/THRONE_NO_MONOLITH_CROWN_GATE_MATRIX_V0_1.json")
TOOL = Path("ORGANS/MECHANICUS/TOOLS/measure_ui_monolith_surface.py")
CODEX_REVIEW = Path("ORGANS/MECHANICUS/REPORTS/CODEX_UI_OUTSOURCE_CODE_REVIEW_V0_1.md")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_ui_workshop_and_no_monolith_law_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW_REPORT_V0_1.md")
SCAN_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_UI_MONOLITH_SURFACE_SCAN_V0_1.json")

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

def text_has_all(text: str, needles: List[str]) -> bool:
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

    law, law_err = load_json(repo / LAW) if (repo / LAW).is_file() else ({}, "missing")
    law_text = json.dumps(law, ensure_ascii=False) if isinstance(law, dict) else ""
    law_ok = law_err is None and text_has_all(law_text, [
        "All UI rules, UI tools, UI fidelity gates and implementation language recommendations belong under Mechanicus",
        "Monoliths are forbidden as a normal development form, including backend monoliths",
        "Fast result is not the priority; working, maintainable, provable result is the priority",
        "Reference image overlay is not live UI proof"
    ])
    add(checks, "mechanicus_ui_workshop_and_no_monolith_law_exists", law_ok, {"path": LAW.as_posix(), "error": law_err})
    if not law_ok:
        errors.append("Mechanicus UI workshop/no-monolith law missing or incomplete")

    arch, arch_err = load_json(repo / ARCH_MATRIX) if (repo / ARCH_MATRIX).is_file() else ({}, "missing")
    dims = arch.get("dimensions", []) if isinstance(arch, dict) else []
    weights_sum = sum(int(d.get("weight", 0)) for d in dims if isinstance(d, dict))
    arch_text = json.dumps(arch, ensure_ascii=False) if isinstance(arch, dict) else ""
    arch_ok = arch_err is None and weights_sum == 100 and text_has_all(arch_text, [
        "single_file_contains_state_render_commands_data_and_events",
        "bitmap_reference_mode_claimed_as_live_ui",
        "backend_multi_domain_monolith"
    ])
    add(checks, "no_monolith_architecture_matrix_exists_and_weights_100", arch_ok, {
        "path": ARCH_MATRIX.as_posix(),
        "error": arch_err,
        "weights_sum": weights_sum
    })
    if not arch_ok:
        errors.append("No-monolith architecture matrix missing, weak, or weights != 100")

    ui, ui_err = load_json(repo / UI_MATRIX) if (repo / UI_MATRIX).is_file() else ({}, "missing")
    stages = [s.get("stage") for s in ui.get("pipeline", [])] if isinstance(ui, dict) else []
    required_stages = ["target_contract", "design_tokens", "component_inventory", "ornament_assets", "reference_fidelity_review", "live_runtime_proof", "owner_acceptance"]
    ui_ok = ui_err is None and all(s in stages for s in required_stages)
    add(checks, "ui_workshop_pipeline_matrix_exists_and_declares_required_stages", ui_ok, {
        "path": UI_MATRIX.as_posix(),
        "error": ui_err,
        "missing_stages": [s for s in required_stages if s not in stages]
    })
    if not ui_ok:
        errors.append("UI workshop pipeline matrix missing required stages")

    custodes, custodes_err = load_json(repo / CUSTODES) if (repo / CUSTODES).is_file() else ({}, "missing")
    custodes_text = json.dumps(custodes, ensure_ascii=False) if isinstance(custodes, dict) else ""
    custodes_ok = custodes_err is None and text_has_all(custodes_text, [
        "prosecutor_not_helper",
        "unregistered_monolith_growth",
        "bitmap_reference_fidelity_fake_green"
    ])
    add(checks, "custodes_no_monolith_prosecutor_matrix_exists", custodes_ok, {"path": CUSTODES.as_posix(), "error": custodes_err})
    if not custodes_ok:
        errors.append("Custodes no-monolith prosecutor matrix missing or weak")

    throne, throne_err = load_json(repo / THRONE) if (repo / THRONE).is_file() else ({}, "missing")
    throne_text = json.dumps(throne, ensure_ascii=False) if isinstance(throne, dict) else ""
    throne_ok = throne_err is None and text_has_all(throne_text, [
        "No local monolith may become accepted global architecture by accident",
        "No visual candidate may become canonical if it hides live DOM under a reference bitmap",
        "No backend monolith may be justified by speed alone"
    ])
    add(checks, "throne_no_monolith_crown_gate_matrix_exists", throne_ok, {"path": THRONE.as_posix(), "error": throne_err})
    if not throne_ok:
        errors.append("Throne no-monolith crown gate matrix missing or weak")

    tool_exists = (repo / TOOL).is_file()
    add(checks, "mechanicus_ui_monolith_surface_scanner_exists", tool_exists, {"path": TOOL.as_posix()})
    if not tool_exists:
        errors.append("Mechanicus UI monolith surface scanner missing")

    scan_ok = False
    scan_data = {}
    if tool_exists:
        p = subprocess.run(
            [sys.executable, str(repo / TOOL), "--repo-root", str(repo), "--out", SCAN_REPORT.as_posix()],
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120
        )
        try:
            scan_data = json.loads((repo / SCAN_REPORT).read_text(encoding="utf-8"))
        except Exception:
            scan_data = {"stdout": p.stdout[-2000:], "stderr": p.stderr[-2000:]}
        scan_ok = p.returncode == 0 and (repo / SCAN_REPORT).is_file()
    add(checks, "monolith_surface_scanner_runs_and_writes_transitional_debt_report", scan_ok, {
        "scan_report": SCAN_REPORT.as_posix(),
        "monolith_debt_count": len(scan_data.get("monolith_debt", [])) if isinstance(scan_data, dict) else None,
        "reference_bitmap_risk_count": len(scan_data.get("reference_bitmap_risks", [])) if isinstance(scan_data, dict) else None
    })
    if not scan_ok:
        errors.append("Mechanicus monolith scanner did not run")

    review_exists = (repo / CODEX_REVIEW).is_file()
    review_text = (repo / CODEX_REVIEW).read_text(encoding="utf-8", errors="replace") if review_exists else ""
    review_ok = review_exists and text_has_all(review_text, [
        "The UI is still a monolith",
        "reference bitmap mode",
        "Do not continue stacking CSS on the monolith"
    ])
    add(checks, "codex_outsource_code_review_report_exists", review_ok, {"path": CODEX_REVIEW.as_posix()})
    if not review_ok:
        errors.append("Codex outsource code review report missing or incomplete")

    # Transitional debt is allowed here. Warn visibly if current scan detects monoliths.
    if isinstance(scan_data, dict) and scan_data.get("monolith_debt"):
        warnings.append("Current APP_TAURI surface has monolith debt; this patch records it as transitional debt and does not fail legacy files.")
    if isinstance(scan_data, dict) and scan_data.get("reference_bitmap_risks"):
        warnings.append("Reference bitmap/invisible hit-zone risk detected in scanned files; allowed only as NON_CANON_REFERENCE_AID, never as live UI proof.")

    verdict = "PASS_MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW_READY" if not errors else "FAIL_MECHANICUS_UI_WORKSHOP_AND_NO_MONOLITH_LAW"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.ui_workshop_and_no_monolith_law_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "scan_report": SCAN_REPORT.as_posix(),
        "meaning": "Places UI rules/tools under Mechanicus and establishes no-monolith law with transitional debt reporting."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.ui_workshop_and_no_monolith_law.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "law": LAW.as_posix(),
        "architecture_matrix": ARCH_MATRIX.as_posix(),
        "ui_workshop_matrix": UI_MATRIX.as_posix(),
        "custodes_matrix": CUSTODES.as_posix(),
        "throne_matrix": THRONE.as_posix(),
        "scanner": TOOL.as_posix(),
        "scan_report": SCAN_REPORT.as_posix(),
        "codex_review": CODEX_REVIEW.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS UI WORKSHOP AND NO MONOLITH LAW REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Mechanicus now owns the UI workshop law/tool surface. Monoliths are forbidden as normal development form, including backend monoliths.

Existing APP_TAURI monoliths are recorded as transitional debt. Future work must reduce this debt or explicitly register a temporary waiver.

## Core law

```text
Fast result is not the priority.
Working, maintainable, provable result is the priority.
A monolith is forbidden unless explicitly registered as transitional debt.
Reference image overlay is not live UI proof.
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
        "scan_report": SCAN_REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
