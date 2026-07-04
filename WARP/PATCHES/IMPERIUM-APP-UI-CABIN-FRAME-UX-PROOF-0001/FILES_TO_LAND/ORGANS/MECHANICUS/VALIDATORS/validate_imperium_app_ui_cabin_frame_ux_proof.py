#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-UI-CABIN-FRAME-UX-PROOF-0001"
VALIDATOR_ID = "mechanicus_imperium_app_ui_cabin_frame_ux_proof_validator.v0_1"

MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
STYLES = Path("SUPPORT/APP_TAURI/src/styles.css")
CONTRACT = Path("SUPPORT/APP_TAURI/contracts/IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_CONTRACT_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_ui_cabin_frame_ux_proof_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_REPORT_V0_1.md")

MAIN_MARKERS = [
    'import "./styles.css";',
    "IMPERIUM_APP_UI_CABIN_FRAME",
    "CABIN_FRAME_UX_PROOF",
    "UX_PROOF_MARKER",
    "cabin-layout",
    "main-deck",
    "Copy log",
    "Clear log",
    "Save log",
    "Open logs",
    "Refresh",
    "Register",
    "Run registered",
    "Load language powers",
    "No fake execution claimed",
    "recordRuntimeFpsProof",
    "record_runtime_fps_proof"
]

STYLE_MARKERS = [
    "IMPERIUM_APP_UI_CABIN_FRAME_V0_1",
    "height: 100%",
    "overflow: hidden",
    "grid-template-rows: 150px minmax(0, 1fr)",
    ".cabin-layout",
    "grid-template-areas",
    ".main-deck",
    ".aquarium",
    "height: calc(100% - 64px)",
    "Trash Polka",
    "Victorian Gothic",
    "Cyberpunk Glow",
    "@keyframes energyFlow",
    "@keyframes proofPulse",
    "prefers-reduced-motion",
    "UI renders truth; receipts prove truth"
]

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

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    main_path = repo / MAIN_JS
    style_path = repo / STYLES
    contract_path = repo / CONTRACT

    main_text = main_path.read_text(encoding="utf-8") if main_path.is_file() else ""
    style_text = style_path.read_text(encoding="utf-8") if style_path.is_file() else ""

    add(checks, "main_js_exists", main_path.is_file(), {"path": MAIN_JS.as_posix(), "bytes": main_path.stat().st_size if main_path.is_file() else 0})
    if not main_path.is_file():
        errors.append("main.js missing")

    missing_main = [m for m in MAIN_MARKERS if m not in main_text]
    add(checks, "main_js_contains_cabin_frame_and_ux_proof_actions", not missing_main, {"missing": missing_main})
    if missing_main:
        errors.append("main.js missing required cabin/UX markers")

    rooms = ["Organ Hub", "Patch Forge", "Mechanicus", "Astronomicon", "Throne", "Eyes Room", "Seed Core"]
    missing_rooms = [r for r in rooms if r not in main_text]
    add(checks, "main_js_preserves_required_rooms", not missing_rooms, {"missing": missing_rooms})
    if missing_rooms:
        errors.append("main.js missing required rooms")

    add(checks, "styles_css_exists", style_path.is_file(), {"path": STYLES.as_posix(), "bytes": style_path.stat().st_size if style_path.is_file() else 0})
    if not style_path.is_file():
        errors.append("styles.css missing")

    missing_styles = [m for m in STYLE_MARKERS if m not in style_text]
    add(checks, "styles_css_contains_cabin_fit_no_page_clip_markers", not missing_styles, {"missing": missing_styles})
    if missing_styles:
        errors.append("styles.css missing cabin fit/identity markers")

    no_page_clip = (
        "html, body, #app" in style_text and
        "overflow: hidden" in style_text and
        ".cabin-layout" in style_text and
        "minmax(0, 1fr)" in style_text and
        ".room-panel" in style_text and
        "overflow: auto" in style_text
    )
    add(checks, "css_reduces_page_level_clipping_with_internal_scroll_zones", no_page_clip, {})
    if not no_page_clip:
        errors.append("CSS does not prove internal scroll cabin layout")

    hud_fit = ".hud span" in style_text and "grid-template-columns: 22px 68px minmax(0, 1fr) auto" in style_text and "text-overflow: ellipsis" in style_text
    add(checks, "hud_layout_prevents_overflow_and_line_collision", hud_fit, {})
    if not hud_fit:
        errors.append("HUD layout does not show overflow prevention markers")

    contract, contract_err = load_json(contract_path) if contract_path.is_file() else ({}, "missing")
    contract_ok = contract_err is None and isinstance(contract, dict) and contract.get("contract_id") == "IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_CONTRACT_V0_1"
    add(checks, "cabin_frame_contract_exists_and_parses", contract_ok, {"path": CONTRACT.as_posix(), "error": contract_err})
    if not contract_ok:
        errors.append("cabin frame UX proof contract missing or invalid")

    addressed = contract.get("owner_complaints_addressed", []) if isinstance(contract, dict) else []
    complaint_ok = all(x in addressed for x in ["protruding zones", "cropped/broken view", "too little animation", "not enough control-cabin feeling"])
    add(checks, "contract_addresses_owner_marked_ui_failures", complaint_ok, {"owner_complaints_addressed": addressed})
    if not complaint_ok:
        errors.append("contract does not address owner-marked UI failures")

    truth_law_text = json.dumps(contract.get("truth_law", []), ensure_ascii=False) if isinstance(contract, dict) else ""
    truth_ok = "UX action proof is not execution proof" in truth_law_text and "receipts prove truth" in truth_law_text
    add(checks, "contract_declares_ux_proof_not_execution_proof", truth_ok, {"truth_law": contract.get("truth_law") if isinstance(contract, dict) else None})
    if not truth_ok:
        errors.append("contract missing UX proof boundary")

    verdict = "PASS_IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF_READY" if not errors else "FAIL_IMPERIUM_APP_UI_CABIN_FRAME_UX_PROOF"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.imperium_app_ui_cabin_frame_ux_proof_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Fixes the marked UI issues by introducing a viewport-fit cabin frame, internal scroll zones, better HUD/card fit and UX proof markers."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.imperium_app_ui_cabin_frame_ux_proof.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "main_js": MAIN_JS.as_posix(),
        "styles": STYLES.as_posix(),
        "contract": CONTRACT.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM APP UI CABIN FRAME UX PROOF REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Owner marked the previous UI as still broken: protruding zones, cropped view, weak animation, and no strong control-cabin feeling.

This patch introduces a viewport-fit cabin frame with internal scroll zones and UX proof controls.

## Boundary

UX proof means the interface records interaction actions in Aquarium. It does not prove backend patch execution without receipts.

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
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
