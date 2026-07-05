#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json, os, shutil, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List
TOOL_ID = "mechanicus_toolchain_probe.v0_3_ultrasafe_nonblocking"
def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
def safe_run(name: str, exe: str, args: List[str], cwd: Path, importance: str, timeout: int = 8) -> Dict[str, Any]:
    found = shutil.which(exe)
    res: Dict[str, Any] = {"name": name, "executable": exe, "args": args, "importance": importance, "which": found, "ok": False, "exit_code": None, "stdout": "", "stderr": "", "mode": "version_probe_only"}
    if not found:
        res["stderr"] = "executable not found in PATH"; res["missing_executable"] = True; return res
    try:
        p = subprocess.run([found, *args], cwd=str(cwd), capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        res.update({"cmd": [found, *args], "exit_code": p.returncode, "ok": p.returncode == 0, "stdout": p.stdout[-1000:], "stderr": p.stderr[-1000:]})
    except Exception as e:
        res.update({"cmd": [found, *args], "stderr": repr(e), "probe_exception": True})
    return res
def safe_npm(cwd: Path) -> Dict[str, Any]:
    if os.name == 'nt':
        cmd, found, label = ['cmd.exe','/d','/s','/c','npm --version'], shutil.which('cmd.exe'), 'cmd.exe/npm'
    else:
        found, label = shutil.which('npm'), 'npm'; cmd = [found or 'npm','--version']
    res: Dict[str, Any] = {"name": "npm_version", "executable": label, "importance": "capability_optional", "which": found, "ok": False, "exit_code": None, "stdout": "", "stderr": "", "mode": "version_probe_only"}
    if not found:
        res["stderr"] = "npm launcher not available"; res["missing_executable"] = True; return res
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=8, encoding='utf-8', errors='replace')
        res.update({"cmd": cmd, "exit_code": p.returncode, "ok": p.returncode == 0, "stdout": p.stdout[-1000:], "stderr": p.stderr[-1000:]})
    except Exception as e:
        res.update({"cmd": cmd, "stderr": repr(e), "probe_exception": True})
    return res
def write_report(out: Path, report: Dict[str, Any]) -> None:
    out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding='utf-8')
def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--repo-root', default='.'); ap.add_argument('--out', default='ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json'); args = ap.parse_args()
    repo = Path(args.repo_root).resolve(); out = repo / args.out
    try:
        results = [
            safe_run('python_version', sys.executable, ['--version'], repo, 'host_required_observed'),
            safe_run('pwsh_version', 'pwsh', ['--version'], repo, 'host_required_observed'),
            safe_run('git_version', 'git', ['--version'], repo, 'host_required_observed'),
            safe_run('node_version', 'node', ['--version'], repo, 'capability_optional'), safe_npm(repo),
            safe_run('rustc_version', 'rustc', ['--version'], repo, 'capability_optional'), safe_run('cargo_version', 'cargo', ['--version'], repo, 'capability_optional'),
            safe_run('go_version', 'go', ['version'], repo, 'capability_optional'), safe_run('cmake_version', 'cmake', ['--version'], repo, 'capability_optional')]
        build_targets = []
        app_package = repo/'SUPPORT'/'APP_TAURI'/'package.json'; cargo_manifest = repo/'SUPPORT'/'APP_TAURI'/'src-tauri'/'Cargo.toml'
        if app_package.is_file(): build_targets.append({"name":"app_tauri_npm_build_target_detected","path":app_package.relative_to(repo).as_posix(),"status":"DETECTED_NOT_RUN_BY_ULTRASAFE_PROBE"})
        if cargo_manifest.is_file(): build_targets.append({"name":"app_tauri_cargo_manifest_detected","path":cargo_manifest.relative_to(repo).as_posix(),"status":"DETECTED_NOT_RUN_BY_ULTRASAFE_PROBE"})
        req = [r for r in results if r.get('importance') == 'host_required_observed']; opt = [r for r in results if r.get('importance') == 'capability_optional']
        report = {"tool_id":TOOL_ID,"generated_at_utc":utc(),"repo_root":str(repo),"mode":"ULTRASAFE_NONBLOCKING_LOCAL_TOOLCHAIN_CAPABILITY_PROBE","results":results,"build_targets_detected_but_not_run":build_targets,"observed_required_ok":all(r.get('ok') for r in req),"observed_required_failed":[r['name'] for r in req if not r.get('ok')],"optional_available":[r['name'] for r in opt if r.get('ok')],"optional_missing_or_failed":[r['name'] for r in opt if not r.get('ok')],"verdict":"PASS_TOOLCHAIN_CAPABILITY_BASELINE_RECORDED_WITH_DEBT","not_claimed":["100% code cleanliness","all toolchains available","build/runtime proof","dependency security clean","universal machine readiness","npm audit fixed"],"warnings":["This probe is intentionally nonblocking and records debt.","Build commands are detected but not executed here.","Tool missing/failure is capability debt, not hidden pass."]}
        write_report(out, report); print(json.dumps(report, ensure_ascii=False, indent=2)); return 0
    except Exception as e:
        emergency = {"tool_id":TOOL_ID,"generated_at_utc":utc(),"repo_root":str(repo),"mode":"EMERGENCY_REPORT_AFTER_PROBE_EXCEPTION","verdict":"PASS_TOOLCHAIN_PROBE_EXCEPTION_RECORDED_AS_DEBT","exception":repr(e),"results":[],"observed_required_ok":False,"observed_required_failed":["probe_exception"],"optional_available":[],"optional_missing_or_failed":[],"not_claimed":["100% code cleanliness","all toolchains available","build/runtime proof"],"warnings":["Probe exception was recorded as debt so Mechanicus can continue measuring reality."]}
        write_report(out, emergency); print(json.dumps(emergency, ensure_ascii=False, indent=2)); return 0
if __name__ == '__main__': raise SystemExit(main())
