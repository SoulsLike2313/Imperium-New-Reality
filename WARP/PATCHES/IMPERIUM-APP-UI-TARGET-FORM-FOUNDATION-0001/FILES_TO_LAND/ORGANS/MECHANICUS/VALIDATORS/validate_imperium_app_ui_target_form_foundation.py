#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-UI-TARGET-FORM-FOUNDATION-0001"
VALIDATOR_ID = "mechanicus_imperium_app_ui_target_form_foundation_validator.v0_1"

MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
STYLES = Path("SUPPORT/APP_TAURI/src/styles.css")
CONTRACT = Path("SUPPORT/APP_TAURI/contracts/IMPERIUM_APP_UI_TARGET_FORM_CONTRACT_V0_1.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_ui_target_form_foundation_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_TARGET_FORM_FOUNDATION_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_TARGET_FORM_FOUNDATION_REPORT_V0_1.md")

MAIN_MARKERS = [
    'import "./styles.css";',
    "IMPERIUM_APP_UI_TARGET_FORM",
    "UI_TARGET_FORM_FOUNDATION",
    "ORGAN_HUB_ROOM",
    "PATCH_FORGE_ROOM",
    "MECHANICUS_ROOM",
    "PATCH_REGISTRY",
    "LANGUAGE_POWER_CODEX",
    "AQUARIUM",
    "UX_PROOF_MARKER",
    "refreshPatchPacks",
    "registerPatchPack",
    "runRegisteredPatchPack",
    "loadLanguagePowers",
    "saveAquariumLog",
    "openLogs",
    "recordRuntimeFpsProof",
    "record_runtime_fps_proof"
]

STYLE_MARKERS = [
    "IMPERIUM_APP_UI_TARGET_FORM_FOUNDATION_V0_1",
    "Victorian Gothic",
    "Cyberpunk Glow",
    "Trash Polka",
    "--gold",
    "--crimson",
    "--cyan",
    "--violet",
    ".imperial-crest",
    ".organ-sigil",
    ".room-button.active",
    ".aquarium",
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

    add(checks, "main_js_exists", main_path.is_file(), {
        "path": MAIN_JS.as_posix(),
        "bytes": main_path.stat().st_size if main_path.is_file() else 0
    })
    if not main_path.is_file():
        errors.append("main.js missing")

    missing_main = [m for m in MAIN_MARKERS if m not in main_text]
    add(checks, "main_js_contains_ui_target_rooms_and_ux_actions", not missing_main, {"missing": missing_main})
    if missing_main:
        errors.append("main.js missing required UI target markers/actions")

    room_names = ["Organ Hub", "Patch Forge", "Mechanicus", "Astronomicon", "Throne", "Eyes Room", "Seed Core"]
    missing_rooms = [r for r in room_names if r not in main_text]
    add(checks, "main_js_contains_all_required_rooms", not missing_rooms, {"missing": missing_rooms})
    if missing_rooms:
        errors.append("main.js missing required room labels")

    ux_buttons = ["Copy log", "Clear log", "Save log", "Open logs", "Refresh", "Register", "Run registered", "Load language powers"]
    missing_buttons = [b for b in ux_buttons if b not in main_text]
    add(checks, "main_js_contains_required_ux_controls", not missing_buttons, {"missing": missing_buttons})
    if missing_buttons:
        errors.append("main.js missing required UX controls")

    anti_fake_green = "No fake execution claimed" in main_text or "no fake execution claimed" in main_text
    add(checks, "patch_runner_ui_has_no_fake_execution_boundary", anti_fake_green, {})
    if not anti_fake_green:
        errors.append("patch runner UI missing no-fake-execution boundary")

    add(checks, "styles_css_exists", style_path.is_file(), {
        "path": STYLES.as_posix(),
        "bytes": style_path.stat().st_size if style_path.is_file() else 0
    })
    if not style_path.is_file():
        errors.append("styles.css missing")

    missing_styles = [m for m in STYLE_MARKERS if m not in style_text]
    add(checks, "styles_css_contains_target_aesthetic_and_motion_markers", not missing_styles, {"missing": missing_styles})
    if missing_styles:
        errors.append("styles.css missing required target aesthetic markers")

    css_size_ok = len(style_text) >= 12000
    add(checks, "styles_css_is_substantive_not_minimal_skin", css_size_ok, {"bytes": len(style_text)})
    if not css_size_ok:
        errors.append("styles.css too small for target form foundation")

    contract, contract_err = load_json(contract_path) if contract_path.is_file() else ({}, "missing")
    contract_ok = (
        contract_err is None and
        isinstance(contract, dict) and
        contract.get("contract_id") == "IMPERIUM_APP_UI_TARGET_FORM_CONTRACT_V0_1" and
        "final AAA polish" in contract.get("not_claimed", [])
    )
    add(checks, "ui_target_form_contract_exists_and_preserves_not_claimed", contract_ok, {
        "path": CONTRACT.as_posix(),
        "error": contract_err,
        "contract_id": contract.get("contract_id") if isinstance(contract, dict) else None,
        "not_claimed": contract.get("not_claimed") if isinstance(contract, dict) else None
    })
    if not contract_ok:
        errors.append("UI target form contract missing or invalid")

    truth_law_text = json.dumps(contract.get("truth_law", []), ensure_ascii=False) if isinstance(contract, dict) else ""
    truth_ok = "UI renders truth" in truth_law_text and "receipts prove truth" in truth_law_text
    add(checks, "contract_declares_ui_truth_boundary", truth_ok, {"truth_law": contract.get("truth_law") if isinstance(contract, dict) else None})
    if not truth_ok:
        errors.append("UI target contract missing truth boundary")

    verdict = "PASS_IMPERIUM_APP_UI_TARGET_FORM_FOUNDATION_READY" if not errors else "FAIL_IMPERIUM_APP_UI_TARGET_FORM_FOUNDATION"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.imperium_app_ui_target_form_foundation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Moves the existing Imperium Tauri app toward the accepted gothic/metallic/cyberpunk/trash-polka target form and adds UX proof controls."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.imperium_app_ui_target_form_foundation.v0_1",
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
    (repo / REPORT).write_text(f"""# IMPERIUM APP UI TARGET FORM FOUNDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

Owner accepted the high-level target concept: Victorian Gothic, dark metallic material, cyberpunk glow, restrained Trash Polka energy, usable room-based MetaOS cockpit.

This patch moves the existing Tauri app toward that target form.

## UX proof

The UI now exposes proof-bearing controls:

- room navigation;
- Patch Forge refresh/register/run registered;
- Mechanicus language powers;
- Aquarium copy/clear/save/open logs;
- UX action markers in the Aquarium.

## Boundary

This is a target-form foundation, not final AAA polish. UI renders truth; receipts prove truth.

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
