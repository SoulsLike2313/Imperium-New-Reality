#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-UI-COMMAND-DECK-SKIN-V2-0001"
VALIDATOR_ID = "mechanicus_imperium_app_ui_command_deck_skin_v2_validator.v0_1"

MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
STYLES = Path("SUPPORT/APP_TAURI/src/styles.css")
CONTRACT = Path("SUPPORT/APP_TAURI/contracts/IMPERIUM_APP_UI_COMMAND_DECK_SKIN_V2_CONTRACT_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_ui_command_deck_skin_v2_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_COMMAND_DECK_SKIN_V2_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_COMMAND_DECK_SKIN_V2_REPORT_V0_1.md")

MAIN_REQUIRED = [
    'import "./styles.css";',
    "IMPERIUM_APP_PLATFORM",
    "IMPERIUM_APP_UI_CABIN_FRAME",
    "CABIN_FRAME_UX_PROOF",
    "UX_PROOF_MARKER",
    "Patch Forge",
    "Mechanicus",
    "Aquarium",
    "Copy log",
    "Clear log",
    "Save log",
    "Open logs",
    "Run registered"
]

STYLE_REQUIRED = [
    "IMPERIUM_APP_UI_COMMAND_DECK_SKIN_V2",
    "COMMAND_DECK_SKIN_V2",
    "beveled metal",
    "gothic ornament",
    "energy rail",
    "trash-polka",
    "grid-template-rows: 128px minmax(0, 1fr)",
    "commandRailFlow",
    "sigilBreath",
    "clip-path",
    ".cabin-layout",
    ".main-deck",
    ".aquarium",
    "UI renders truth; receipts prove truth",
    "overflow: hidden"
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

    add(checks, "main_js_exists_and_preserves_operational_rooms", main_path.is_file(), {
        "path": MAIN_JS.as_posix(),
        "bytes": main_path.stat().st_size if main_path.is_file() else 0
    })
    if not main_path.is_file():
        errors.append("main.js missing")

    missing_main = [m for m in MAIN_REQUIRED if m not in main_text]
    add(checks, "main_js_keeps_rooms_and_ux_actions", not missing_main, {"missing": missing_main})
    if missing_main:
        errors.append("main.js lost required rooms/actions")

    add(checks, "styles_css_exists", style_path.is_file(), {
        "path": STYLES.as_posix(),
        "bytes": style_path.stat().st_size if style_path.is_file() else 0
    })
    if not style_path.is_file():
        errors.append("styles.css missing")

    missing_style = [m for m in STYLE_REQUIRED if m not in style_text]
    add(checks, "styles_css_contains_command_deck_skin_v2_markers", not missing_style, {"missing": missing_style})
    if missing_style:
        errors.append("styles.css missing command deck v2 markers")

    css_substantive = len(style_text) >= 18000
    add(checks, "styles_css_is_substantive_target_skin", css_substantive, {"bytes": len(style_text)})
    if not css_substantive:
        errors.append("styles.css too small for command deck skin v2")

    cabin_fit = (
        "html," in style_text and
        "#app" in style_text and
        "height: 100%" in style_text and
        ".cabin-layout" in style_text and
        "grid-template-areas" in style_text and
        "minmax(0, 1fr)" in style_text
    )
    add(checks, "css_preserves_viewport_fit_cabin_layout", cabin_fit, {})
    if not cabin_fit:
        errors.append("CSS does not preserve viewport-fit cabin layout")

    motion_identity = all(x in style_text for x in ["@keyframes commandRailFlow", "@keyframes proofPulse", "@keyframes sigilBreath", "prefers-reduced-motion"])
    add(checks, "css_adds_motion_with_reduced_motion_guard", motion_identity, {})
    if not motion_identity:
        errors.append("CSS motion or reduced-motion guard missing")

    contract, contract_err = load_json(contract_path) if contract_path.is_file() else ({}, "missing")
    contract_ok = (
        contract_err is None and
        isinstance(contract, dict) and
        contract.get("contract_id") == "IMPERIUM_APP_UI_COMMAND_DECK_SKIN_V2_CONTRACT_V0_1" and
        "final target concept reached" in contract.get("not_claimed", [])
    )
    add(checks, "command_deck_skin_contract_exists_and_preserves_not_claimed", contract_ok, {
        "path": CONTRACT.as_posix(),
        "error": contract_err,
        "contract_id": contract.get("contract_id") if isinstance(contract, dict) else None,
        "not_claimed": contract.get("not_claimed") if isinstance(contract, dict) else None
    })
    if not contract_ok:
        errors.append("command deck skin contract missing or invalid")

    verdict = "PASS_IMPERIUM_APP_UI_COMMAND_DECK_SKIN_V2_READY" if not errors else "FAIL_IMPERIUM_APP_UI_COMMAND_DECK_SKIN_V2"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.imperium_app_ui_command_deck_skin_v2_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Applies a stronger command-deck skin over the working cabin layout while preserving UX actions and truth boundaries."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.imperium_app_ui_command_deck_skin_v2.v0_1",
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

    (repo / REPORT).write_text(f"""# IMPERIUM APP UI COMMAND DECK SKIN V2 REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The cabin frame became functional, but Owner said it still was not the target form.

This patch applies a stronger command-deck skin while preserving the existing operational rooms and UX proof actions.

## Boundary

This is still not final AAA and not final target concept reached. It is an iteration toward the accepted form.

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
