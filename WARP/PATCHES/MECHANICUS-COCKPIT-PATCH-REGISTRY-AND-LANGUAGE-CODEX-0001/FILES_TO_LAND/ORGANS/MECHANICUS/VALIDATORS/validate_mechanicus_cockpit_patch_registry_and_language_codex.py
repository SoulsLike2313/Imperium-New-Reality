#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "MECHANICUS-COCKPIT-PATCH-REGISTRY-AND-LANGUAGE-CODEX-0001"
VALIDATOR_ID = "mechanicus_cockpit_patch_registry_and_language_codex_validator.v0_1"

MAIN_RS = Path("SUPPORT/APP_TAURI/src-tauri/src/main.rs")
MAIN_JS = Path("SUPPORT/APP_TAURI/src/main.js")
STYLES = Path("SUPPORT/APP_TAURI/src/styles.css")
CODEX = Path("ORGANS/MECHANICUS/CODEX/MECHANICUS_LANGUAGE_POWER_CODEX_V0_1.md")
SCHEMA = Path("ORGANS/MECHANICUS/SCHEMAS/MECHANICUS_LANGUAGE_POWER_SCHEMA_V0_1.json")
MATRIX = Path("ORGANS/MECHANICUS/MATRICES/MECHANICUS_LANGUAGE_POWER_MATRIX_V0_1.json")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/mechanicus_cockpit_patch_registry_and_language_codex_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_COCKPIT_PATCH_REGISTRY_AND_LANGUAGE_CODEX_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_COCKPIT_PATCH_REGISTRY_AND_LANGUAGE_CODEX_REPORT_V0_1.md")

REQUIRED_LANGS = ["Python", "Rust", "Go", "C++", "TypeScript", "PowerShell"]
REQUIRED_COMMANDS = ["list_patch_packs", "register_patch_pack", "run_registered_patch_pack", "get_mechanicus_language_codex"]
REQUIRED_JS_MARKERS = ["Patch Pack Registry", "register_patch_pack", "run_registered_patch_pack", "Mechanicus Language Codex"]

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

    main_rs = repo / MAIN_RS
    rs_text = main_rs.read_text(encoding="utf-8") if main_rs.is_file() else ""
    add(checks, "tauri_rust_main_exists", main_rs.is_file(), {"path": MAIN_RS.as_posix(), "bytes": main_rs.stat().st_size if main_rs.is_file() else 0})
    if not main_rs.is_file(): errors.append("Tauri Rust main.rs missing")
    missing_cmds = [cmd for cmd in REQUIRED_COMMANDS if cmd not in rs_text]
    add(checks, "tauri_rust_contains_patch_registry_commands", not missing_cmds, {"missing": missing_cmds})
    if missing_cmds: errors.append("Tauri Rust main missing patch registry/language commands")
    safety_ok = "safe_patch_id" in rs_text and "git push" in rs_text and "patch pack is not registered" in rs_text
    add(checks, "tauri_rust_contains_basic_cockpit_safety_gates", safety_ok, {})
    if not safety_ok: errors.append("Tauri Rust missing cockpit safety gates")

    main_js = repo / MAIN_JS
    js_text = main_js.read_text(encoding="utf-8") if main_js.is_file() else ""
    add(checks, "tauri_frontend_main_exists", main_js.is_file(), {"path": MAIN_JS.as_posix(), "bytes": main_js.stat().st_size if main_js.is_file() else 0})
    if not main_js.is_file(): errors.append("Tauri frontend main.js missing")
    missing_js = [m for m in REQUIRED_JS_MARKERS if m not in js_text]
    add(checks, "tauri_frontend_contains_working_cockpit_markers", not missing_js, {"missing": missing_js})
    if missing_js: errors.append("Tauri frontend missing cockpit markers")

    styles = repo / STYLES
    styles_ok = styles.is_file() and "IMPERIUM_TAURI_COCKPIT_PATCH_REGISTRY_STYLE" in styles.read_text(encoding="utf-8")
    add(checks, "tauri_frontend_style_exists", styles_ok, {"path": STYLES.as_posix(), "bytes": styles.stat().st_size if styles.is_file() else 0})
    if not styles_ok: errors.append("Tauri frontend cockpit style missing")

    codex_path = repo / CODEX
    codex_text = codex_path.read_text(encoding="utf-8") if codex_path.is_file() else ""
    codex_ok = codex_path.is_file() and "Python binds" in codex_text and "Rust judges" in codex_text
    add(checks, "mechanicus_language_codex_exists", codex_ok, {"path": CODEX.as_posix()})
    if not codex_ok: errors.append("Mechanicus language codex missing or incomplete")

    schema, s_err = load_json(repo / SCHEMA) if (repo / SCHEMA).is_file() else ({}, "missing")
    add(checks, "mechanicus_language_schema_exists_and_parses", s_err is None, {"path": SCHEMA.as_posix(), "error": s_err})
    if s_err: errors.append("Mechanicus language schema missing or invalid")

    matrix, m_err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "mechanicus_language_matrix_exists_and_parses", m_err is None, {"path": MATRIX.as_posix(), "error": m_err})
    if m_err: errors.append("Mechanicus language matrix missing or invalid")
    langs = [x.get("language") for x in matrix.get("languages", [])] if isinstance(matrix, dict) else []
    missing_langs = [x for x in REQUIRED_LANGS if x not in langs]
    add(checks, "language_matrix_contains_required_language_powers", not missing_langs, {"missing": missing_langs, "actual": langs})
    if missing_langs: errors.append("Language matrix missing required languages")

    proof_ok = True
    proof_details = []
    for lang in matrix.get("languages", []) if isinstance(matrix, dict) else []:
        pc = lang.get("proof_commands", [])
        ok = isinstance(pc, list) and len(pc) > 0
        proof_ok = proof_ok and ok
        proof_details.append({"language": lang.get("language"), "proof_commands": len(pc) if isinstance(pc, list) else 0})
    add(checks, "each_language_has_proof_commands", proof_ok and len(proof_details) >= 6, {"languages": proof_details})
    if not proof_ok: errors.append("One or more language powers lack proof commands")

    verdict = "PASS_MECHANICUS_COCKPIT_PATCH_REGISTRY_AND_LANGUAGE_CODEX_READY" if not errors else "FAIL_MECHANICUS_COCKPIT_PATCH_REGISTRY_AND_LANGUAGE_CODEX"
    generated = utc()
    summary = {
        "summary_id": "mechanicus.cockpit_patch_registry_and_language_codex_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Adds operational Tauri cockpit patch pack registry/run commands and Mechanicus language power codex."
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.cockpit_patch_registry_and_language_codex.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "codex": CODEX.as_posix(),
        "schema": SCHEMA.as_posix(),
        "matrix": MATRIX.as_posix(),
        "tauri_main_rs": MAIN_RS.as_posix(),
        "tauri_main_js": MAIN_JS.as_posix()
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# MECHANICUS COCKPIT PATCH REGISTRY AND LANGUAGE CODEX REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

This validator checks that the Tauri cockpit now contains operational patch-pack registry/run commands and that Mechanicus owns a language power codex for language selection and proof.

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
