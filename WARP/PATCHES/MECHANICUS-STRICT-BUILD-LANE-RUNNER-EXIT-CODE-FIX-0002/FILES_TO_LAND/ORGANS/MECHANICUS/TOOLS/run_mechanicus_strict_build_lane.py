#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import py_compile
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

TOOL_ID = "mechanicus_strict_build_lane_foundation_runner.v0_2_exit_code_consistent"
LEGACY_VALIDATOR_MARKER = "mechanicus_strict_build_lane_foundation_runner.v0_1"
DEFAULT_OUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_REPORT_V0_1.json")
DEFAULT_MD = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_BUILD_LANE_REPORT_V0_1.md")

EXCLUDE_DIRS = {
    ".git", "node_modules", "target", "dist", "build", "__pycache__",
    ".venv", "venv", ".mypy_cache", ".ruff_cache", ".pytest_cache",
    ".next", ".turbo", ".idea", ".vscode"
}

def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def is_current_source_candidate(path: Path, repo: Path) -> bool:
    try:
        rel = path.relative_to(repo)
    except Exception:
        return False
    if set(rel.parts) & EXCLUDE_DIRS:
        return False
    rels = rel.as_posix()
    if rels.startswith("WARP/PATCHES/") or "/FILES_TO_LAND/" in rels:
        return False
    return True

def run_cmd(cmd: List[str], cwd: Path, timeout: int = 600) -> Dict[str, Any]:
    started = utc()
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
        return {
            "started_at_utc": started,
            "finished_at_utc": utc(),
            "cmd": cmd,
            "cwd": str(cwd),
            "exit_code": p.returncode,
            "ok": p.returncode == 0,
            "stdout_tail": p.stdout[-12000:],
            "stderr_tail": p.stderr[-12000:]
        }
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout if isinstance(e.stdout, str) else ""
        stderr = e.stderr if isinstance(e.stderr, str) else ""
        return {
            "started_at_utc": started,
            "finished_at_utc": utc(),
            "cmd": cmd,
            "cwd": str(cwd),
            "exit_code": None,
            "ok": False,
            "timeout": True,
            "stdout_tail": stdout[-12000:],
            "stderr_tail": stderr[-12000:],
            "error": f"timeout after {timeout}s"
        }
    except Exception as e:
        return {
            "started_at_utc": started,
            "finished_at_utc": utc(),
            "cmd": cmd,
            "cwd": str(cwd),
            "exit_code": None,
            "ok": False,
            "error": repr(e),
            "stdout_tail": "",
            "stderr_tail": ""
        }

def which(name: str) -> Optional[str]:
    return shutil.which(name) or shutil.which(name + ".cmd") or shutil.which(name + ".exe")

def python_compile_lane(repo: Path) -> Dict[str, Any]:
    errors = []
    count = 0
    for path in sorted(repo.rglob("*.py")):
        if not is_current_source_candidate(path, repo):
            continue
        count += 1
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as e:
            errors.append({"path": path.relative_to(repo).as_posix(), "error": str(e)})
    return {
        "target_id": "python_compile_current_non_patch",
        "lane": "python_compile",
        "detected": count > 0,
        "files_checked": count,
        "ok": len(errors) == 0,
        "errors": errors[:80],
        "not_claimed": ["ruff", "mypy", "pytest", "import runtime"]
    }

def pwsh_probe_lane(repo: Path) -> Dict[str, Any]:
    exe = which("pwsh")
    if not exe:
        return {
            "target_id": "powershell_host_probe",
            "lane": "powershell_host_probe",
            "detected": True,
            "ok": False,
            "toolchain": {"pwsh": None},
            "errors": [{"error": "pwsh not found"}],
            "not_claimed": ["PSScriptAnalyzer", "runner execution proof"]
        }
    res = run_cmd([exe, "-NoLogo", "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"], repo, timeout=60)
    return {
        "target_id": "powershell_host_probe",
        "lane": "powershell_host_probe",
        "detected": True,
        "ok": bool(res.get("ok")),
        "toolchain": {"pwsh": exe},
        "command_result": res,
        "errors": [] if res.get("ok") else [{"error": "pwsh version probe failed"}],
        "not_claimed": ["PSScriptAnalyzer", "all runners valid"]
    }

def npm_build_lane(repo: Path) -> Dict[str, Any]:
    app = repo / "SUPPORT" / "APP_TAURI"
    package_json = app / "package.json"
    if not package_json.is_file():
        return {
            "target_id": "support_app_tauri_npm_build",
            "lane": "tauri_frontend_npm_build",
            "detected": False,
            "ok": True,
            "debt": "NO_PACKAGE_JSON_PRESENT",
            "not_claimed": ["npm build"]
        }

    npm = which("npm")
    if not npm:
        return {
            "target_id": "support_app_tauri_npm_build",
            "lane": "tauri_frontend_npm_build",
            "detected": True,
            "ok": False,
            "toolchain": {"npm": None},
            "errors": [{"error": "npm not found"}],
            "not_claimed": ["dependency install"]
        }

    node_modules = app / "node_modules"
    dependency_state = "node_modules_present" if node_modules.exists() else "node_modules_missing_no_install_attempted"
    cmd = ["cmd.exe", "/d", "/s", "/c", "npm run build"] if os.name == "nt" else [npm, "run", "build"]
    res = run_cmd(cmd, app, timeout=600)
    return {
        "target_id": "support_app_tauri_npm_build",
        "lane": "tauri_frontend_npm_build",
        "detected": True,
        "ok": bool(res.get("ok")),
        "toolchain": {"npm": npm, "node": which("node")},
        "dependency_state": dependency_state,
        "command_result": res,
        "errors": [] if res.get("ok") else [{"error": "npm run build failed", "dependency_state": dependency_state, "exit_code": res.get("exit_code")}],
        "not_claimed": ["npm test", "npm audit", "eslint", "tsc unless part of build", "runtime proof"]
    }

def cargo_check_lane(repo: Path) -> Dict[str, Any]:
    manifest = repo / "SUPPORT" / "APP_TAURI" / "src-tauri" / "Cargo.toml"
    if not manifest.is_file():
        return {
            "target_id": "support_app_tauri_cargo_check",
            "lane": "tauri_rust_cargo_check",
            "detected": False,
            "ok": True,
            "debt": "NO_CARGO_MANIFEST_PRESENT",
            "not_claimed": ["cargo check"]
        }

    cargo = which("cargo")
    rustc = which("rustc")
    if not cargo or not rustc:
        return {
            "target_id": "support_app_tauri_cargo_check",
            "lane": "tauri_rust_cargo_check",
            "detected": True,
            "ok": False,
            "toolchain": {"cargo": cargo, "rustc": rustc},
            "errors": [{"error": "cargo/rustc not found"}],
            "not_claimed": ["cargo fmt", "cargo clippy", "cargo test"]
        }

    res = run_cmd([cargo, "check", "--manifest-path", str(manifest)], repo, timeout=900)
    return {
        "target_id": "support_app_tauri_cargo_check",
        "lane": "tauri_rust_cargo_check",
        "detected": True,
        "ok": bool(res.get("ok")),
        "toolchain": {"cargo": cargo, "rustc": rustc},
        "manifest": manifest.relative_to(repo).as_posix(),
        "command_result": res,
        "errors": [] if res.get("ok") else [{"error": "cargo check failed", "exit_code": res.get("exit_code")}],
        "not_claimed": ["cargo fmt", "cargo clippy", "cargo test", "runtime proof"]
    }

def build_report(repo: Path) -> Dict[str, Any]:
    targets = [
        python_compile_lane(repo),
        pwsh_probe_lane(repo),
        npm_build_lane(repo),
        cargo_check_lane(repo),
    ]
    blocking_failures = []
    foundation_debt = []
    for t in targets:
        if t.get("detected") and not t.get("ok"):
            blocking_failures.append({
                "target_id": t.get("target_id"),
                "lane": t.get("lane"),
                "errors": t.get("errors", []),
                "command_result": t.get("command_result", {})
            })
        if not t.get("detected"):
            foundation_debt.append({
                "target_id": t.get("target_id"),
                "lane": t.get("lane"),
                "debt": t.get("debt", "TARGET_NOT_PRESENT")
            })
    verdict = "PASS_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION" if not blocking_failures else "FAIL_MECHANICUS_STRICT_BUILD_LANE_FOUNDATION"
    expected_exit_code = 0 if verdict.startswith("PASS") and len(blocking_failures) == 0 else 1
    return {
        "tool_id": TOOL_ID,
        "legacy_validator_marker": LEGACY_VALIDATOR_MARKER,
        "generated_at_utc": utc(),
        "repo_root": str(repo),
        "targets": targets,
        "target_count": len(targets),
        "blocking_failure_count": len(blocking_failures),
        "foundation_debt_count": len(foundation_debt),
        "blocking_failures": blocking_failures,
        "foundation_debt": foundation_debt,
        "verdict": verdict,
        "exit_code_contract": {
            "rule": "process exit code must be 0 when verdict is PASS and blocking_failure_count is 0, else 1",
            "expected_exit_code": expected_exit_code
        },
        "not_claimed": [
            "tests passed",
            "linters passed",
            "type checking passed unless part of build",
            "security audit clean",
            "runtime FPS proof",
            "UI reference fidelity",
            "semantic correctness"
        ],
        "warnings": [
            "Strict build lane foundation does not install dependencies.",
            "Build proof is separate from code cleanliness and runtime proof.",
            "Local host pass is not universal host readiness."
        ]
    }

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = json.loads(json.dumps(data, ensure_ascii=False, default=str))
    path.write_text(json.dumps(safe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def write_md(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    target_lines = []
    for t in report.get("targets", []):
        target_lines.append(f"- `{t.get('target_id')}` — detected=`{t.get('detected')}` ok=`{t.get('ok')}` lane=`{t.get('lane')}`")
    failures = "\n".join(f"- `{f.get('target_id')}` — {json.dumps(f.get('errors', []), ensure_ascii=False)}" for f in report.get("blocking_failures", [])) or "- none"
    path.write_text(f"""# MECHANICUS STRICT BUILD LANE REPORT V0.1

tool_id: `{report['tool_id']}`  
verdict: `{report['verdict']}`  
generated_at_utc: `{report['generated_at_utc']}`  
expected_exit_code: `{report['exit_code_contract']['expected_exit_code']}`

## Targets

{chr(10).join(target_lines)}

## Blocking failures

{failures}

## Boundary

```text
Build proof is not code cleanliness.
Build proof is not runtime proof.
No dependency installation was attempted.
```
""", encoding="utf-8")

def main() -> int:
    configure_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--md-out", default=str(DEFAULT_MD))
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    try:
        report = build_report(repo)
        write_json(repo / args.out, report)
        write_md(repo / args.md_out, report)

        summary = {
            "tool_id": TOOL_ID,
            "verdict": report.get("verdict"),
            "target_count": report.get("target_count"),
            "blocking_failure_count": report.get("blocking_failure_count"),
            "foundation_debt_count": report.get("foundation_debt_count"),
            "expected_exit_code": report.get("exit_code_contract", {}).get("expected_exit_code"),
            "targets": [
                {
                    "target_id": t.get("target_id"),
                    "lane": t.get("lane"),
                    "detected": t.get("detected"),
                    "ok": t.get("ok"),
                    "dependency_state": t.get("dependency_state")
                }
                for t in report.get("targets", [])
            ],
            "report": str(args.out)
        }
        print(json.dumps(summary, ensure_ascii=True, indent=2))
        return int(report.get("exit_code_contract", {}).get("expected_exit_code", 1))
    except Exception as e:
        failure = {
            "tool_id": TOOL_ID,
            "legacy_validator_marker": LEGACY_VALIDATOR_MARKER,
            "generated_at_utc": utc(),
            "repo_root": str(Path(args.repo_root).resolve()),
            "verdict": "FAIL_MECHANICUS_STRICT_BUILD_LANE_RUNNER_EXCEPTION",
            "blocking_failure_count": 1,
            "blocking_failures": [{"target_id": "runner_exception", "error": repr(e)}],
            "exception_trace_tail": traceback.format_exc()[-6000:],
            "exit_code_contract": {"expected_exit_code": 1}
        }
        try:
            write_json(Path(args.repo_root).resolve() / args.out, failure)
        except Exception:
            pass
        print(json.dumps({"tool_id": TOOL_ID, "verdict": failure["verdict"], "error": repr(e)}, ensure_ascii=True, indent=2))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
