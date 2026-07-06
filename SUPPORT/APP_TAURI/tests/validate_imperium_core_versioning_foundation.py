#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess, time
from pathlib import Path
TASK_ID = "IMPERIUM-APP-CORE-VERSIONING-FOUNDATION-0001"
PASS = "PASS_IMPERIUM_CORE_VERSIONING_FOUNDATION_READY"
FAIL = "FAIL_IMPERIUM_CORE_VERSIONING_FOUNDATION"

def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for c in [cur, *cur.parents]:
        if (c/"SUPPORT"/"APP_TAURI").is_dir() and (c/"WARP").is_dir(): return c
    raise SystemExit("Repo root not found")

def read(path: Path) -> str: return path.read_text(encoding="utf-8", errors="ignore")
def tool(name: str) -> str: return f"{name}.cmd" if os.name == "nt" and name == "npm" else (f"{name}.exe" if os.name == "nt" and name == "cargo" else name)
def run(cmd, cwd, timeout=180):
    try:
        p = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=timeout)
        return {"ok": p.returncode == 0, "exit_code": p.returncode, "missing_tool": False, "error": "", "stdout_tail": "\n".join(p.stdout.splitlines()[-6:]), "stderr_tail": "\n".join(p.stderr.splitlines()[-6:])}
    except FileNotFoundError as e:
        return {"ok": False, "exit_code": None, "missing_tool": True, "error": str(e)}
    except subprocess.TimeoutExpired:
        return {"ok": False, "exit_code": None, "missing_tool": False, "timeout": True, "error": "timeout"}

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root", default="."); ap.add_argument("--apply", action="store_true"); ap.add_argument("--json", action="store_true")
    args=ap.parse_args(); repo=find_repo_root(Path(args.repo_root)); app=repo/"SUPPORT"/"APP_TAURI"
    errors=[]; warnings=["Core versioning foundation does not claim v1; Owner recognition required.", "Registration/launch buttons remain present but terminal remains recommended until daily UI matures."]
    paths=[
        app/"src"/"main.js", app/"src"/"styles.css", app/"src-tauri"/"src"/"main.rs", app/"src-tauri"/"tauri.conf.json", app/"package.json",
        app/"state"/"imperium_core_current_version.json", app/"state"/"imperium_core_available_version.json", app/"contracts"/"IMPERIUM_CORE_VERSIONING_FOUNDATION_CONTRACT_V0_1.json",
        app/"tools"/"set_imperium_core_available_version.py"
    ]
    for p in paths:
        if not p.is_file(): errors.append(f"missing {p.relative_to(repo).as_posix()}")
    main_js=read(app/"src"/"main.js") if (app/"src"/"main.js").is_file() else ""
    main_rs=read(app/"src-tauri"/"src"/"main.rs") if (app/"src-tauri"/"src"/"main.rs").is_file() else ""
    conf=json.loads(read(app/"src-tauri"/"tauri.conf.json")) if (app/"src-tauri"/"tauri.conf.json").is_file() else {}
    pkg=json.loads(read(app/"package.json")) if (app/"package.json").is_file() else {}
    for marker in ["Imperium Core", "IMPERIUM_CORE_VERSIONING_V0_1", "Current version", "imperium-core-update"]:
        if marker not in main_js: errors.append(f"missing UI marker {marker}")
    for marker in ["get_imperium_core_version_state", "initialize_imperium_core_update"]:
        if marker not in main_rs: errors.append(f"missing backend command {marker}")
    if "Register via Astronomicon" not in main_js: errors.append("registration button was removed; must remain present")
    if "Launch polished only" not in main_js: errors.append("launch gate button was removed; must remain present")
    if conf.get("productName") != "Imperium Core": errors.append("tauri productName is not Imperium Core")
    if conf.get("app",{}).get("windows",[{}])[0].get("title") != "Imperium Core": errors.append("window title is not Imperium Core")
    if pkg.get("name") != "imperium-core": errors.append("package name is not imperium-core")
    npm=run([tool("npm"), "run", "build"], app, timeout=180)
    cargo=run([tool("cargo"), "check"], app/"src-tauri", timeout=240)
    if not npm.get("ok"): errors.append("npm run build failed")
    if not cargo.get("ok"): errors.append("cargo check failed")
    receipt={
        "task_id":TASK_ID,"validator_id":"imperium_core_versioning_foundation_validator.v0_1","verdict": PASS if not errors else FAIL,
        "product_name":"Imperium Core","current_version":"0.1.0-alpha.0","registration_functions_preserved": "Register via Astronomicon" in main_js and "Launch polished only" in main_js,
        "version_strip_ready":"IMPERIUM_CORE_VERSIONING_V0_1" in main_js,"update_command_ready":"initialize_imperium_core_update" in main_rs,
        "core_v1_claim":False,"npm_build_ok":npm.get("ok",False),"cargo_check_ok":cargo.get("ok",False),"npm_build":npm,"cargo_check":cargo,
        "errors":errors,"warnings":warnings,"generated_at_unix":int(time.time())
    }
    summary={k: receipt[k] for k in ["task_id","verdict","product_name","current_version","registration_functions_preserved","version_strip_ready","update_command_ready","core_v1_claim","npm_build_ok","cargo_check_ok"]}
    if args.apply or not errors:
        rdir=app/"receipts"; rdir.mkdir(parents=True, exist_ok=True)
        (rdir/"imperium_core_versioning_foundation_receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
        (rdir/"imperium_core_versioning_foundation_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    if args.json: print(json.dumps(receipt, indent=2, ensure_ascii=False))
    else:
        print(f"TASK: {TASK_ID}")
        print(f"VERDICT: {receipt['verdict']}")
        print(f"CORE: name={receipt['product_name']} | version={receipt['current_version']} | v1_claim={receipt['core_v1_claim']}")
        print(f"APP: registration_kept={receipt['registration_functions_preserved']} | version_strip={receipt['version_strip_ready']} | update_command={receipt['update_command_ready']}")
        print(f"BUILD: npm={receipt['npm_build_ok']} | cargo={receipt['cargo_check_ok']}")
        print("SUMMARY: SUPPORT/APP_TAURI/receipts/imperium_core_versioning_foundation_summary.json")
        print("RECEIPT: SUPPORT/APP_TAURI/receipts/imperium_core_versioning_foundation_receipt.json")
        if errors: print("ERRORS: " + " | ".join(errors[:4]))
        if warnings: print("WARNINGS: " + " | ".join(warnings[:2]))
    return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
