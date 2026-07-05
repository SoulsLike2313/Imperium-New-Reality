#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

def run_cmd(name: str, cmd: List[str], cwd: Path, timeout: int = 30, importance: str = "optional") -> Dict[str, Any]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
        return {
            "name": name,
            "cmd": cmd,
            "importance": importance,
            "exit_code": p.returncode,
            "ok": p.returncode == 0,
            "stdout": p.stdout[-2000:],
            "stderr": p.stderr[-2000:]
        }
    except FileNotFoundError as e:
        return {
            "name": name,
            "cmd": cmd,
            "importance": importance,
            "exit_code": None,
            "ok": False,
            "stdout": "",
            "stderr": str(e),
            "missing_executable": True
        }
    except Exception as e:
        return {
            "name": name,
            "cmd": cmd,
            "importance": importance,
            "exit_code": None,
            "ok": False,
            "stdout": "",
            "stderr": str(e)
        }

def npm_cmd(*args: str) -> List[str]:
    if os.name == "nt":
        return ["cmd.exe", "/d", "/s", "/c", "npm " + " ".join(args)]
    return ["npm", *args]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default="ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    # Nonblocking baseline probe:
    # - This tool writes local machine truth and capability debt.
    # - It does NOT fail the whole patch just because a host tool is missing or weirdly unavailable
    #   from a Python subprocess. The outer WARP runner already proves pwsh for this run.
    # - 100% cleanliness/toolchain readiness is still NOT claimed.
    commands = [
        ("python_version", [sys.executable, "--version"], "host_required_observed"),
        ("pwsh_version", ["pwsh", "--version"], "host_required_observed"),
        ("git_version", ["git", "--version"], "host_required_observed"),
        ("node_version", ["node", "--version"], "capability_optional"),
        ("npm_version", npm_cmd("--version"), "capability_optional"),
        ("rustc_version", ["rustc", "--version"], "capability_optional"),
        ("cargo_version", ["cargo", "--version"], "capability_optional"),
        ("go_version", ["go", "version"], "capability_optional"),
    ]

    results = [run_cmd(name, cmd, repo, importance=importance) for name, cmd, importance in commands]

    app_dir = repo / "SUPPORT" / "APP_TAURI"
    if (app_dir / "package.json").is_file():
        results.append(run_cmd("npm_build_app_tauri_if_present", npm_cmd("run", "build"), app_dir, timeout=240, importance="capability_optional_build"))
    manifest = repo / "SUPPORT" / "APP_TAURI" / "src-tauri" / "Cargo.toml"
    if manifest.is_file():
        results.append(run_cmd("cargo_check_app_tauri_if_present", ["cargo", "check", "--manifest-path", str(manifest)], repo, timeout=240, importance="capability_optional_build"))

    observed_required = [r for r in results if r.get("importance") == "host_required_observed"]
    observed_required_ok = all(r["ok"] for r in observed_required)

    report = {
        "tool_id": "mechanicus_toolchain_probe.v0_2_nonblocking_baseline",
        "repo_root": str(repo),
        "mode": "NONBLOCKING_LOCAL_TOOLCHAIN_CAPABILITY_PROBE",
        "results": results,
        "observed_required_ok": observed_required_ok,
        "observed_required_failed": [r["name"] for r in observed_required if not r["ok"]],
        "optional_available": [r["name"] for r in results if r["ok"] and r.get("importance", "").startswith("capability_optional")],
        "optional_missing_or_failed": [r["name"] for r in results if not r["ok"] and r.get("importance", "").startswith("capability_optional")],
        "verdict": "PASS_TOOLCHAIN_BASELINE_RECORDED_WITH_DEBT" if not observed_required_ok or any(not r["ok"] for r in results if r.get("importance", "").startswith("capability_optional")) else "PASS_TOOLCHAIN_BASELINE_RECORDED",
        "not_claimed": [
            "universal toolchain readiness",
            "100% code cleanliness",
            "all optional compilers available",
            "dependency security clean",
            "npm audit fixed"
        ],
        "warnings": [
            "Local toolchain proof is local machine truth, not universal readiness.",
            "Tool unavailable or command failure is recorded as capability/validation debt, not hidden.",
            "npm audit fix --force is intentionally not run.",
            "This nonblocking probe exists so Mechanicus can measure reality before it is strong enough to block on every missing capability."
        ]
    }

    out = repo / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    # Always return 0 once the report is written. Validator will inspect the report and keep the no-fake-clean boundary.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
