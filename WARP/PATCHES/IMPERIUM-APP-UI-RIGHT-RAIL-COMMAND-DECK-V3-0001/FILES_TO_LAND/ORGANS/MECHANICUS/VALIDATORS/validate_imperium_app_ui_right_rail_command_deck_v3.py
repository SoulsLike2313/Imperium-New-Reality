#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-UI-RIGHT-RAIL-COMMAND-DECK-V3-0001"
VALIDATOR_ID = "mechanicus_imperium_app_ui_right_rail_command_deck_v3_validator.v0_1"

MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
STYLES = Path("SUPPORT/APP_TAURI/src/styles.css")
CONTRACT = Path("SUPPORT/APP_TAURI/contracts/IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3_CONTRACT_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_ui_right_rail_command_deck_v3_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3_REPORT_V0_1.md")

MAIN_REQUIRED = [
    'import "./styles.css";',
    "IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3",
    "COMMAND_RAIL",
    "COMMAND_DECK_V3",
    "renderCommandRail",
    "status-tile-row",
    "rail-section",
    "Patch Forge",
    "Mechanicus",
    "Aquarium",
    "Copy log",
    "Clear log",
    "Save log",
    "Open logs",
    "Run registered",
    "No fake execution claimed"
]

STYLE_REQUIRED = [
    "IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3",
    "COMMAND_DECK_V3",
    "right proof/status rail",
    "grid-template-columns: 270px minmax(0, 1fr) 280px",
    'grid-template-areas:',
    '"nav deck rail"',
    '"nav aquarium rail"',
    ".command-rail",
    ".rail-section",
    ".status-tile-row",
    ".organ-grade",
    "commandRailFlow",
    "sigilBreath",
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

    add(checks, "main_js_exists", main_path.is_file(), {
        "path": MAIN_JS.as_posix(),
        "bytes": main_path.stat().st_size if main_path.is_file() else 0
    })
    if not main_path.is_file():
        errors.append("main.js missing")

    missing_main = [m for m in MAIN_REQUIRED if m not in main_text]
    add(checks, "main_js_contains_right_rail_and_preserves_ux_actions", not missing_main, {"missing": missing_main})
    if missing_main:
        errors.append("main.js missing right rail or UX action markers")

    add(checks, "styles_css_exists", style_path.is_file(), {
        "path": STYLES.as_posix(),
        "bytes": style_path.stat().st_size if style_path.is_file() else 0
    })
    if not style_path.is_file():
        errors.append("styles.css missing")

    missing_style = [m for m in STYLE_REQUIRED if m not in style_text]
    add(checks, "styles_css_contains_right_rail_command_deck_v3_markers", not missing_style, {"missing": missing_style})
    if missing_style:
        errors.append("styles.css missing command deck v3 markers")

    css_substantive = len(style_text) >= 22000
    add(checks, "styles_css_is_substantive_v3_skin", css_substantive, {"bytes": len(style_text)})
    if not css_substantive:
        errors.append("styles.css too small for command deck v3")

    viewport_fit = all(x in style_text for x in ["html,", "#app", "height: 100%", "overflow: hidden", "minmax(0, 1fr)", ".main-deck", ".aquarium"])
    add(checks, "css_preserves_viewport_fit_with_internal_zones", viewport_fit, {})
    if not viewport_fit:
        errors.append("CSS does not preserve viewport-fit internal zones")

    contract, contract_err = load_json(contract_path) if contract_path.is_file() else ({}, "missing")
    contract_ok = (
        contract_err is None and
        isinstance(contract, dict) and
        contract.get("contract_id") == "IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3_CONTRACT_V0_1" and
        "final target UI reached" in contract.get("not_claimed", [])
    )
    add(checks, "right_rail_command_deck_contract_exists_and_preserves_not_claimed", contract_ok, {
        "path": CONTRACT.as_posix(),
        "error": contract_err,
        "contract_id": contract.get("contract_id") if isinstance(contract, dict) else None,
        "not_claimed": contract.get("not_claimed") if isinstance(contract, dict) else None
    })
    if not contract_ok:
        errors.append("right rail command deck contract missing or invalid")

    verdict = "PASS_IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3_READY" if not errors else "FAIL_IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.imperium_app_ui_right_rail_command_deck_v3_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Adds a right command rail and stronger command-deck layout while preserving Patch Forge, Mechanicus, Aquarium and UX proof actions."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.imperium_app_ui_right_rail_command_deck_v3.v0_1",
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

    (repo / REPORT).write_text(f"""# IMPERIUM APP UI RIGHT RAIL COMMAND DECK V3 REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The prior command deck is functional and cleaner, but still not target. This patch adds a right proof/status command rail and strengthens the cockpit hierarchy.

## Boundary

This still does not claim final target UI. UI renders truth; receipts prove truth.

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
