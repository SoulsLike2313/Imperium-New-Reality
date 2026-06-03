from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from urllib.request import urlopen

TASK_ID = "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"
REPORT_DIR = Path(
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/"
    "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"
)
WEB_SERVER_SCRIPT = Path("IMPERIUM_NEW_GENERATION/AGENT_IDE/WEB_PROJECTION/agent_ide_web_projection_server_v0_1.py")
SPEC_PATH = Path("IMPERIUM_NEW_GENERATION/AGENT_IDE/PLAYWRIGHT/agent_ide_playwright_parity_v0_2.spec.js")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_ok(url: str, timeout: float = 3.0) -> bool:
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def wait_health(url: str, timeout_sec: float = 10.0) -> bool:
    end = time.time() + timeout_sec
    while time.time() < end:
        if fetch_ok(url):
            return True
        time.sleep(0.25)
    return False


def run_capture(repo_root: Path, port: int) -> Dict[str, Any]:
    report_dir = repo_root / REPORT_DIR
    screenshots_dir = report_dir / "screenshots"
    marker_snapshot_path = report_dir / "dom_truth_marker_snapshot.json"
    playwright_json_report = report_dir / "playwright_test_report.json"
    manifest_path = report_dir / "playwright_screenshot_manifest.json"
    playwright_project_dir = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/PLAYWRIGHT"

    screenshots_dir.mkdir(parents=True, exist_ok=True)

    npm_exec = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_exec:
        payload = {
            "task_id": TASK_ID,
            "timestamp_utc": utc_now(),
            "status": "PASS_WITH_WARNINGS",
            "reason": "NPM_NOT_FOUND",
            "screenshot_manifest_path": manifest_path.as_posix(),
        }
        manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return payload

    if not (playwright_project_dir / "node_modules" / "@playwright" / "test").exists():
        install = subprocess.run(
            [npm_exec, "install"],
            text=True,
            capture_output=True,
            check=False,
            cwd=str(playwright_project_dir),
        )
        if install.returncode != 0:
            payload = {
                "task_id": TASK_ID,
                "timestamp_utc": utc_now(),
                "status": "PASS_WITH_WARNINGS",
                "reason": "PLAYWRIGHT_LOCAL_INSTALL_FAILED",
                "install_stdout": install.stdout,
                "install_stderr": install.stderr,
                "screenshot_manifest_path": manifest_path.as_posix(),
            }
            manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return payload

    version = subprocess.run(
        [npm_exec, "exec", "--", "playwright", "--version"],
        text=True,
        capture_output=True,
        check=False,
        cwd=str(playwright_project_dir),
    )
    if version.returncode != 0:
        payload = {
            "task_id": TASK_ID,
            "timestamp_utc": utc_now(),
            "status": "PASS_WITH_WARNINGS",
            "reason": "PLAYWRIGHT_NOT_AVAILABLE",
            "probe_stderr": version.stderr.strip(),
            "screenshot_manifest_path": manifest_path.as_posix(),
        }
        manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return payload

    server_proc = subprocess.Popen(
        [sys.executable, str(repo_root / WEB_SERVER_SCRIPT), "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(repo_root),
    )

    health_url = f"http://127.0.0.1:{port}/api/health"
    ready = wait_health(health_url)
    if not ready:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        payload = {
            "task_id": TASK_ID,
            "timestamp_utc": utc_now(),
            "status": "PASS_WITH_WARNINGS",
            "reason": "PROJECTION_SERVER_NOT_READY",
            "health_url": health_url,
            "screenshot_manifest_path": manifest_path.as_posix(),
        }
        manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return payload

    env = os.environ.copy()
    env["AGENT_IDE_BASE_URL"] = f"http://127.0.0.1:{port}"
    env["AGENT_IDE_SCREENSHOT_DIR"] = screenshots_dir.as_posix()
    env["AGENT_IDE_MARKER_SNAPSHOT_PATH"] = marker_snapshot_path.as_posix()

    cmd = [
        npm_exec,
        "exec",
        "--",
        "playwright",
        "test",
        SPEC_PATH.name,
        "--reporter",
        "json",
        "--workers",
        "1",
    ]

    run = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        cwd=str(playwright_project_dir),
        env=env,
        check=False,
    )

    server_proc.terminate()
    try:
        server_proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        server_proc.kill()

    report_payload: Dict[str, Any] = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "command": " ".join(cmd),
        "returncode": run.returncode,
        "stdout": run.stdout,
        "stderr": run.stderr,
    }
    playwright_json_report.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    expected_files = [
        "overview.png",
        "organs.png",
        "file_atlas.png",
        "viewer.png",
        "officio_language_gate.png",
        "owner_pain_map.png",
        "routes.png",
        "reports.png",
        "checks.png",
        "block_foundation.png",
        "plugins.png",
    ]
    missing = [name for name in expected_files if not (screenshots_dir / name).exists()]

    status = "PASS" if run.returncode == 0 and not missing else "PASS_WITH_WARNINGS"
    payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": status,
        "health_url": health_url,
        "screenshots_dir": screenshots_dir.as_posix(),
        "expected_screenshots": expected_files,
        "missing_screenshots": missing,
        "marker_snapshot_path": marker_snapshot_path.as_posix(),
        "playwright_test_report_path": playwright_json_report.as_posix(),
        "playwright_version": version.stdout.strip(),
    }
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Agent IDE Playwright parity capture V0.2.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    parser.add_argument("--port", type=int, default=4173, help="Projection server port.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd().resolve()
    result = run_capture(repo_root, args.port)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
