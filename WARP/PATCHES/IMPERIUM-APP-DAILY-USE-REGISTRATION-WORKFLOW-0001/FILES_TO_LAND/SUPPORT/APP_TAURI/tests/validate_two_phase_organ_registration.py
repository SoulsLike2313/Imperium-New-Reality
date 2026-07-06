#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess, time
from pathlib import Path

PATCH_ID = "IMPERIUM-APP-DAILY-USE-REGISTRATION-WORKFLOW-0001"
CANDIDATE_ID = "IMPERIUM-APP-DAILY-USE-UI-REFIT-CANDIDATE-0001"
VALIDATOR_ID = "imperium_app_two_phase_organ_registration.validator.v0_1"
CONTROL_CHARS = [chr(i) for i in range(0, 32) if chr(i) not in "\r\n\t"]
REQUIRED = [
    "SUPPORT/APP_TAURI/src/main.js",
    "SUPPORT/APP_TAURI/src/styles.css",
    "SUPPORT/APP_TAURI/src-tauri/src/main.rs",
    "SUPPORT/APP_TAURI/contracts/IMPERIUM_APP_TWO_PHASE_ORGAN_REGISTRATION_CONTRACT_V0_1.json",
    f"ORGANS/ASTRONOMICON/TASK_CANDIDATES/{CANDIDATE_ID}.json",
    f"WARP/PATCHES/{CANDIDATE_ID}/INTENT.json",
    f"WARP/PATCHES/{CANDIDATE_ID}/PATCH_PACK.md",
]

def copy_tree(src_root: Path, dst_root: Path):
    for src in src_root.rglob("*"):
        if src.is_file():
            dst = dst_root / src.relative_to(src_root)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

def control_hits(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for idx, ch in enumerate(text):
        if ch in CONTROL_CHARS:
            hits.append({"line": text.count("\n", 0, idx) + 1, "ord": ord(ch)})
    return hits

def which_cmd(name: str):
    return shutil.which(name + ".cmd") or shutil.which(name + ".exe") or shutil.which(name) or name

def run_capture(cmd, cwd: Path, timeout=240):
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
        return {"cmd": cmd, "ok": p.returncode == 0, "exit_code": p.returncode, "stdout_tail": p.stdout[-1200:], "stderr_tail": p.stderr[-1200:]}
    except FileNotFoundError as e:
        return {"cmd": cmd, "ok": False, "missing_tool": True, "error": str(e)}
    except subprocess.TimeoutExpired as e:
        return {"cmd": cmd, "ok": False, "timeout": True, "error": str(e)}

def read(path: Path):
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""

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
        hits = control_hits(p)
        checks.append({"name": f"no_control_chars::{rel}", "status": "PASS" if not hits else "FAIL", "hits": hits[:3]})
        if hits:
            errors.append(f"control chars in {rel}: {hits[:3]}")

    js = read(repo / "SUPPORT/APP_TAURI/src/main.js")
    css = read(repo / "SUPPORT/APP_TAURI/src/styles.css")
    rs = read(repo / "SUPPORT/APP_TAURI/src-tauri/src/main.rs")
    markers = {
        "two_phase_marker_js": "IMPERIUM_APP_TWO_PHASE_ORGAN_REGISTRATION_V0_1" in js,
        "two_phase_marker_css": "IMPERIUM_APP_TWO_PHASE_ORGAN_REGISTRATION_V0_1" in css,
        "candidate_priority": CANDIDATE_ID in js,
        "candidate_preferred_on_refresh": "DAILY_UI_REFIT_CANDIDATE_PATCH_ID) || patchPacks.find" in js,
        "normalize_phase_fields": "workflow_phase:" in js and "launch_allowed:" in js,
        "candidate_phase_backend": "CANDIDATE_INTAKE_PACK" in rs and "POLISHED_EXECUTION_PACK" in rs,
        "candidate_run_block": "candidate intake pack is analysis-only" in rs,
        "astronomicon_candidate_verdict": "REGISTERABLE_CANDIDATE_PACK" in rs,
        "mechanicus_candidate_verdict": "MECHANICUS_ANALYZES_CANDIDATE_REQUIRES_POLISHED_PACK" in rs,
    }
    for name, ok in markers.items():
        checks.append({"name": name, "status": "PASS" if ok else "FAIL"})
        if not ok:
            errors.append(f"marker failed: {name}")

    node_check = run_capture([which_cmd("node"), "--check", str(repo / "SUPPORT/APP_TAURI/src/main.js")], repo, timeout=60)
    checks.append({"name": "node_check_main_js", "status": "PASS" if node_check.get("ok") else "FAIL", "details": node_check})
    if not node_check.get("ok"):
        errors.append("node --check failed for main.js")

    npm_build = {"status": "SKIPPED", "reason": "--host-build-check not requested"}
    cargo_check = {"status": "SKIPPED", "reason": "--host-build-check not requested"}
    if args.host_build_check:
        app_dir = repo / "SUPPORT/APP_TAURI"
        npm_build = run_capture([which_cmd("npm"), "run", "build"], app_dir, timeout=240)
        checks.append({"name": "npm_run_build", "status": "PASS" if npm_build.get("ok") else "FAIL", "details": npm_build})
        if not npm_build.get("ok"):
            errors.append("npm run build failed")
        cargo_check = run_capture([which_cmd("cargo"), "check", "--manifest-path", str(app_dir / "src-tauri/Cargo.toml")], repo, timeout=240)
        checks.append({"name": "cargo_check_tauri", "status": "PASS" if cargo_check.get("ok") else "FAIL", "details": cargo_check})
        if not cargo_check.get("ok"):
            errors.append("cargo check failed")

    receipt_rel = "SUPPORT/APP_TAURI/receipts/two_phase_organ_registration_receipt.json"
    summary_rel = "SUPPORT/APP_TAURI/receipts/two_phase_organ_registration_summary.json"
    verdict = "PASS_IMPERIUM_APP_DAILY_USE_REGISTRATION_WORKFLOW_READY" if not errors else "FAIL_IMPERIUM_APP_DAILY_USE_REGISTRATION_WORKFLOW"
    receipt = {
        "task_id": PATCH_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "candidate_patch_id": CANDIDATE_ID,
        "two_phase_workflow_status": "PASS_BASELINE" if not errors else "FAIL",
        "candidate_pack_created": (repo / "WARP" / "PATCHES" / CANDIDATE_ID).is_dir(),
        "candidate_run_allowed": False,
        "polished_pack_required": True,
        "app_summary_mode": "COMPACT_ORGAN_PROOF_DIGEST",
        "npm_build": npm_build,
        "cargo_check": cargo_check,
        "receipt": receipt_rel,
        "summary": summary_rel,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
    summary = {k: receipt[k] for k in ["task_id", "validator_id", "verdict", "generated_at_utc", "candidate_patch_id", "two_phase_workflow_status", "candidate_pack_created", "candidate_run_allowed", "polished_pack_required", "app_summary_mode", "errors", "warnings"]}
    out_dir = repo / "SUPPORT/APP_TAURI/receipts"
    out_dir.mkdir(parents=True, exist_ok=True)
    (repo / receipt_rel).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / summary_rel).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.verbose_json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    else:
        print(f"TASK: {PATCH_ID}")
        print(f"VERDICT: {verdict}")
        print(f"WORKFLOW: {receipt['two_phase_workflow_status']} | CANDIDATE: {CANDIDATE_ID} | RUN_ALLOWED: false")
        print(f"APP: compact_proof_digest | POLISHED_REQUIRED: true")
        print(f"RECEIPT: {receipt_rel}")
        if errors:
            print("ERRORS: " + " | ".join(errors[:3]))
        if warnings:
            print("WARNINGS: " + " | ".join(warnings[:3]))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
