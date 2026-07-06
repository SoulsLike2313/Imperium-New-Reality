#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess, time, os
from pathlib import Path

PATCH_ID = "IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001-FIX-0001"
TASK_ID = PATCH_ID
VALIDATOR_ID = "imperium_app_astronomicon_mechanicus_registration_picker_fix.validator.v0_1"
CONTROL_CHARS = [chr(i) for i in range(0, 32) if chr(i) not in "\r\n\t"]
REQUIRED = [
    "SUPPORT/APP_TAURI/src/main.js",
    "SUPPORT/APP_TAURI/src/styles.css",
    "SUPPORT/APP_TAURI/src-tauri/src/main.rs",
]

def copy_tree(src_root: Path, dst_root: Path):
    for src in src_root.rglob("*"):
        if src.is_file():
            dst = dst_root / src.relative_to(src_root)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

def has_control_chars(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for idx, ch in enumerate(text):
        if ch in CONTROL_CHARS:
            hits.append({"line": text.count("\n", 0, idx) + 1, "ord": ord(ch)})
    return hits

def resolve_npm():
    return shutil.which("npm.cmd") or shutil.which("npm") or "npm"

def run_capture(cmd, cwd: Path, timeout=180):
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
        return {"cmd": cmd, "ok": p.returncode == 0, "exit_code": p.returncode, "stdout_tail": p.stdout[-2000:], "stderr_tail": p.stderr[-2000:]}
    except FileNotFoundError as e:
        return {"cmd": cmd, "ok": False, "missing_tool": True, "error": str(e)}
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd, "ok": False, "timeout": True, "error": str(e)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--host-build-check", action="store_true")
    ap.add_argument("--verbose-json", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    patch_dir = repo / "WARP" / "PATCHES" / PATCH_ID
    files_to_land = patch_dir / "FILES_TO_LAND"
    errors, warnings, checks = [], [], []

    if not files_to_land.is_dir():
        errors.append(f"FILES_TO_LAND missing: {files_to_land}")
    elif args.apply:
        copy_tree(files_to_land, repo)

    for rel in REQUIRED:
        p = repo / rel
        ok = p.is_file()
        checks.append({"name": f"exists::{rel}", "status": "PASS" if ok else "FAIL"})
        if not ok:
            errors.append(f"missing required file: {rel}")
            continue
        hits = has_control_chars(p)
        checks.append({"name": f"no_control_chars::{rel}", "status": "PASS" if not hits else "FAIL", "hits": hits[:3]})
        if hits: errors.append(f"control chars in {rel}: {hits[:3]}")

    js = (repo / "SUPPORT/APP_TAURI/src/main.js").read_text(encoding="utf-8", errors="replace")
    css = (repo / "SUPPORT/APP_TAURI/src/styles.css").read_text(encoding="utf-8", errors="replace")
    rs = (repo / "SUPPORT/APP_TAURI/src-tauri/src/main.rs").read_text(encoding="utf-8", errors="replace")
    markers = {
        "dark_picker_marker": "ASTRONOMICON_PATCH_PICKER_DARK_LIST_V0_1" in js and "ASTRONOMICON_PATCH_PICKER_DARK_LIST_V0_1" in css,
        "no_native_patch_select": 'id="patch-select"' not in js,
        "patch_search_present": 'id="patch-search"' in js,
        "patch_buttons_present": 'data-patch-id' in js,
        "current_app_pack_prioritized": "APP_REGISTRATION_PATCH_ID" in js,
        "next_trial_labeled_not_warp_pack": "not a WARP pack yet" in js,
        "backend_modified_sort": "modified_unix" in rs and "path_modified_unix" in rs,
    }
    for name, ok in markers.items():
        checks.append({"name": name, "status": "PASS" if ok else "FAIL"})
        if not ok: errors.append(f"marker failed: {name}")

    node_check = run_capture(["node", "--check", str(repo / "SUPPORT/APP_TAURI/src/main.js")], repo, timeout=60)
    checks.append({"name": "node_check_main_js", "status": "PASS" if node_check.get("ok") else "FAIL", "details": node_check})
    if not node_check.get("ok"):
        errors.append("node --check failed for main.js")

    npm_build = {"status": "SKIPPED", "reason": "--host-build-check not requested"}
    if args.host_build_check:
        app_dir = repo / "SUPPORT/APP_TAURI"
        npm_build = run_capture([resolve_npm(), "run", "build"], app_dir, timeout=240)
        checks.append({"name": "npm_run_build", "status": "PASS" if npm_build.get("ok") else "FAIL", "details": npm_build})
        if not npm_build.get("ok"):
            errors.append("npm run build failed")

    verdict = "PASS_IMPERIUM_APP_ASTRONOMICON_MECHANICUS_REGISTRATION_PICKER_FIX_READY" if not errors else "FAIL_IMPERIUM_APP_ASTRONOMICON_MECHANICUS_REGISTRATION_PICKER_FIX"
    receipt_rel = "SUPPORT/APP_TAURI/receipts/astronomicon_mechanicus_registration_picker_fix_receipt.json"
    summary_rel = "SUPPORT/APP_TAURI/receipts/astronomicon_mechanicus_registration_picker_fix_summary.json"
    receipt = {
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ui_picker_status": "PASS_DARK_SEARCHABLE_LIST" if not errors else "FAIL",
        "native_select_removed": markers.get("no_native_patch_select", False),
        "patch_sorting_status": "MODIFIED_TIME_DESC_WITH_CURRENT_PROOF_PRIORITY" if markers.get("backend_modified_sort", False) else "NOT_PROVEN",
        "next_trial_visible_as_candidate": markers.get("next_trial_labeled_not_warp_pack", False),
        "npm_build": npm_build,
        "receipt": receipt_rel,
        "summary": summary_rel,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
    summary = {k: receipt[k] for k in ["task_id", "validator_id", "verdict", "generated_at_utc", "ui_picker_status", "native_select_removed", "patch_sorting_status", "next_trial_visible_as_candidate", "errors", "warnings"]}
    (repo / "SUPPORT/APP_TAURI/receipts").mkdir(parents=True, exist_ok=True)
    (repo / receipt_rel).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / summary_rel).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.verbose_json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print(f"TASK: {TASK_ID}")
        print(f"VERDICT: {verdict}")
        print(f"PICKER: {receipt['ui_picker_status']} | SELECT_REMOVED: {receipt['native_select_removed']} | SORT: {receipt['patch_sorting_status']}")
        print(f"NEXT_TRIAL: visible_as_candidate={receipt['next_trial_visible_as_candidate']}")
        print(f"RECEIPT: {receipt_rel}")
        if errors: print("ERRORS: " + " | ".join(errors[:3]))
        if warnings: print("WARNINGS: " + " | ".join(warnings[:3]))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
