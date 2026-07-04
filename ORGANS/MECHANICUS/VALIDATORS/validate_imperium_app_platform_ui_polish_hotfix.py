#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-PLATFORM-UI-POLISH-HOTFIX-0001"
VALIDATOR_ID = "mechanicus_imperium_app_platform_ui_polish_hotfix_validator.v0_1"

MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
STYLES = Path("SUPPORT/APP_TAURI/src/styles.css")

RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_platform_ui_polish_hotfix_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_PLATFORM_UI_POLISH_HOTFIX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_PLATFORM_UI_POLISH_HOTFIX_REPORT_V0_1.md")

REQUIRED_STYLE_MARKERS = [
    "IMPERIUM_APP_PLATFORM_UI_POLISH_HOTFIX_V0_1",
    "Victorian Gothic",
    "Cyberpunk Glow",
    ".app-shell",
    ".hero",
    ".room-nav",
    ".room-panel",
    ".organ-grid",
    ".aquarium",
    "backdrop-filter",
    "::-webkit-scrollbar"
]

REQUIRED_MAIN_MARKERS = [
    "IMPERIUM_APP_PLATFORM",
    "ORGAN_HUB_ROOM",
    "PATCH_FORGE_ROOM",
    "MECHANICUS_ROOM",
    "AQUARIUM",
    "APP_COCKPIT_MERGED_INTO_PLATFORM"
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def ensure_css_import(main_path: Path) -> Dict[str, Any]:
    text = main_path.read_text(encoding="utf-8")
    before = text

    if 'import "./styles.css";' not in text and "import './styles.css';" not in text:
        lines = text.splitlines()
        insert_at = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("import "):
                insert_at = i + 1
        lines.insert(insert_at, 'import "./styles.css";')
        text = "\n".join(lines) + "\n"

    main_path.write_text(text, encoding="utf-8")
    return {
        "changed": before != text,
        "has_double_quote_import": 'import "./styles.css";' in text,
        "has_single_quote_import": "import './styles.css';" in text,
        "bytes": main_path.stat().st_size
    }

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

    add(checks, "main_js_exists", main_path.is_file(), {
        "path": MAIN_JS.as_posix(),
        "bytes": main_path.stat().st_size if main_path.is_file() else 0
    })
    if not main_path.is_file():
        errors.append("main.js missing")

    import_result = {}
    if not errors:
        import_result = ensure_css_import(main_path)
    import_ok = import_result.get("has_double_quote_import") or import_result.get("has_single_quote_import")
    add(checks, "main_js_imports_styles_css", bool(import_ok), import_result)
    if not import_ok:
        errors.append("main.js does not import styles.css")

    main_text = main_path.read_text(encoding="utf-8") if main_path.is_file() else ""
    missing_main = [m for m in REQUIRED_MAIN_MARKERS if m not in main_text]
    add(checks, "main_js_preserves_app_platform_room_markers", not missing_main, {"missing": missing_main})
    if missing_main:
        errors.append("main.js lost required app platform markers")

    add(checks, "styles_css_exists", styles_path.is_file(), {
        "path": STYLES.as_posix(),
        "bytes": styles_path.stat().st_size if styles_path.is_file() else 0
    })
    if not styles_path.is_file():
        errors.append("styles.css missing")

    styles_text = styles_path.read_text(encoding="utf-8") if styles_path.is_file() else ""
    missing_styles = [m for m in REQUIRED_STYLE_MARKERS if m not in styles_text]
    add(checks, "styles_css_contains_polish_markers", not missing_styles, {"missing": missing_styles})
    if missing_styles:
        errors.append("styles.css missing UI polish markers")

    ugly_unstyled_risk_reduced = "body {" in styles_text and "background:" in styles_text and ".hero" in styles_text and ".room-nav" in styles_text
    add(checks, "unstyled_html_risk_reduced_by_imported_layout_css", ugly_unstyled_risk_reduced, {})
    if not ugly_unstyled_risk_reduced:
        errors.append("layout CSS does not appear sufficient to reduce unstyled HTML state")

    truth_boundary = "UI only; truth remains in receipts" in styles_text
    add(checks, "ui_polish_does_not_claim_truth_authority", truth_boundary, {})
    if not truth_boundary:
        errors.append("UI polish truth boundary marker missing")

    verdict = "PASS_IMPERIUM_APP_PLATFORM_UI_POLISH_HOTFIX_READY" if not errors else "FAIL_IMPERIUM_APP_PLATFORM_UI_POLISH_HOTFIX"
    generated = utc()

    summary = {
        "summary_id": "mechanicus.imperium_app_platform_ui_polish_hotfix_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Applies a usable gothic/cyberpunk room-based UI skin to the existing Imperium App Platform and ensures Vite imports styles.css."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.imperium_app_platform_ui_polish_hotfix.v0_1",
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
    (repo / REPORT).write_text(f"""# IMPERIUM APP PLATFORM UI POLISH HOTFIX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The app was structurally correct, but appeared as unstyled HTML because the frontend did not import `styles.css`.

This patch:

- ensures `SUPPORT/APP_TAURI/src/main.js` imports `./styles.css`;
- applies a usable Victorian Gothic + cyberpunk glow room layout;
- preserves the existing Imperium App Platform shape;
- does not claim final AAA visual work.

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
