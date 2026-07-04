#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-COCKPIT-MERGE-HOTFIX-0001"
VALIDATOR_ID = "mechanicus_imperium_app_cockpit_merge_hotfix_validator.v0_1"

MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
STYLES = Path("SUPPORT/APP_TAURI/src/styles.css")
PACKAGE = Path("SUPPORT/APP_TAURI/package.json")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_cockpit_merge_hotfix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_REPORT_V0_1.md")

REQUIRED_MAIN_MARKERS = [
    "IMPERIUM_TAURI_SHELL",
    "IMPERIUM_APP_PLATFORM",
    "ORGAN_HUB_ROOM",
    "PATCH_FORGE_ROOM",
    "MECHANICUS_ROOM",
    "PATCH_REGISTRY",
    "LANGUAGE_POWER_CODEX",
    "AQUARIUM",
    "APP_COCKPIT_MERGED_INTO_PLATFORM",
    "callAnyCommand",
    "refreshPatchPacks",
    "registerPatchPack",
    "runRegisteredPatchPack",
    "loadLanguagePowers",
    "recordRuntimeFpsProof",
    "record_runtime_fps_proof"
]

REQUIRED_STYLE_MARKERS = [
    "IMPERIUM_APP_PLATFORM",
    "APP_COCKPIT_MERGED_INTO_PLATFORM",
    ".room-nav",
    ".room-panel",
    ".organ-grid",
    ".aquarium"
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

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
    styles_path = repo / STYLES
    package_path = repo / PACKAGE

    main_text = main_path.read_text(encoding="utf-8") if main_path.is_file() else ""
    styles_text = styles_path.read_text(encoding="utf-8") if styles_path.is_file() else ""

    add(checks, "tauri_main_js_exists", main_path.is_file(), {
        "path": MAIN_JS.as_posix(),
        "bytes": main_path.stat().st_size if main_path.is_file() else 0
    })
    if not main_path.is_file():
        errors.append("SUPPORT/APP_TAURI/src/main.js missing")

    missing_main = [m for m in REQUIRED_MAIN_MARKERS if m not in main_text]
    add(checks, "main_js_contains_existing_app_room_markers_and_cockpit_powers", not missing_main, {
        "missing": missing_main
    })
    if missing_main:
        errors.append("main.js missing app merge markers")

    platform_not_replaced = "Imperium App Platform" in main_text and "Operational Cockpit" not in main_text
    add(checks, "main_js_restores_platform_as_primary_app_not_operational_cockpit_title", platform_not_replaced, {
        "has_platform_title": "Imperium App Platform" in main_text,
        "has_operational_cockpit_title": "Operational Cockpit" in main_text
    })
    if not platform_not_replaced:
        errors.append("main.js still appears to replace the app with Operational Cockpit")

    patch_room_ok = "Patch Forge" in main_text and "Patch Pack Registry" in main_text and "Run registered" in main_text
    add(checks, "patch_registry_is_room_inside_app", patch_room_ok, {})
    if not patch_room_ok:
        errors.append("Patch registry not represented as in-app room")

    mechanicus_room_ok = "Mechanicus" in main_text and "Language Power Codex" in main_text and "Python binds" in main_text
    add(checks, "mechanicus_language_codex_is_room_inside_app", mechanicus_room_ok, {})
    if not mechanicus_room_ok:
        errors.append("Mechanicus language codex not represented as in-app room")

    fps_ok = "FPS_LOCK_TARGET" in main_text and "RUNTIME_FPS_PROOF" in main_text and "recordRuntimeFpsProof" in main_text
    add(checks, "runtime_fps_proof_marker_preserved", fps_ok, {})
    if not fps_ok:
        errors.append("runtime FPS proof markers not preserved")

    add(checks, "tauri_styles_css_exists", styles_path.is_file(), {
        "path": STYLES.as_posix(),
        "bytes": styles_path.stat().st_size if styles_path.is_file() else 0
    })
    if not styles_path.is_file():
        errors.append("SUPPORT/APP_TAURI/src/styles.css missing")

    missing_styles = [m for m in REQUIRED_STYLE_MARKERS if m not in styles_text]
    add(checks, "styles_css_contains_platform_room_layout_markers", not missing_styles, {
        "missing": missing_styles
    })
    if missing_styles:
        errors.append("styles.css missing room layout markers")

    add(checks, "tauri_package_json_exists", package_path.is_file(), {
        "path": PACKAGE.as_posix(),
        "bytes": package_path.stat().st_size if package_path.is_file() else 0
    })
    if not package_path.is_file():
        errors.append("SUPPORT/APP_TAURI/package.json missing")

    verdict = "PASS_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX_READY" if not errors else "FAIL_IMPERIUM_APP_COCKPIT_MERGE_HOTFIX"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.imperium_app_cockpit_merge_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Restores the existing Imperium App Platform and embeds cockpit powers as rooms rather than replacing the app."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.imperium_app_cockpit_merge_hotfix.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "main_js": MAIN_JS.as_posix(),
        "styles": STYLES.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# IMPERIUM APP COCKPIT MERGE HOTFIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The previous cockpit patch made Patch Registry and Language Codex feel like a separate replacement app.

This hotfix restores the existing Imperium App Platform shape and embeds operational powers as rooms:

- Organ Hub;
- Patch Forge / Patch Pack Registry;
- Mechanicus / Language Power Codex;
- Aquarium;
- future Eyes/Seed Core rooms.

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
