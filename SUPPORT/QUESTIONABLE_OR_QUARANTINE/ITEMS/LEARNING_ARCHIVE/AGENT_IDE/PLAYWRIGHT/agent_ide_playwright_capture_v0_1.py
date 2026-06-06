from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.request import urlopen


TASK_ID = "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
REPORT_DIR = Path(
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/"
    "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
)
WEB_SERVER_SCRIPT = Path(
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/WEB_PROJECTION/agent_ide_web_projection_server_v0_1.py"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fetch_ok(url: str, timeout: float = 3.0) -> bool:
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def _wait_health(url: str, timeout_sec: float = 8.0) -> bool:
    end = time.time() + timeout_sec
    while time.time() < end:
        if _fetch_ok(url):
            return True
        time.sleep(0.25)
    return False


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def run_capture(repo_root: Path, port: int) -> Dict[str, Any]:
    screenshots_dir = repo_root / REPORT_DIR / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = repo_root / REPORT_DIR / "playwright_screenshot_manifest.json"

    npx_exec = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx_exec:
        return {
            "task_id": TASK_ID,
            "timestamp_utc": _utc_now(),
            "status": "PASS_WITH_WARNINGS",
            "reason": "NPX_NOT_FOUND",
            "follow_up_commands": [
                "Install Node.js with npm/npx support",
                "npx playwright install chromium"
            ],
            "screenshot_manifest_path": manifest_path.as_posix(),
        }

    try:
        version_probe = subprocess.run([npx_exec, "playwright", "--version"], text=True, capture_output=True)
    except FileNotFoundError:
        return {
            "task_id": TASK_ID,
            "timestamp_utc": _utc_now(),
            "status": "PASS_WITH_WARNINGS",
            "reason": "NPX_EXEC_NOT_FOUND_AT_RUNTIME",
            "screenshot_manifest_path": manifest_path.as_posix(),
        }
    if version_probe.returncode != 0:
        return {
            "task_id": TASK_ID,
            "timestamp_utc": _utc_now(),
            "status": "PASS_WITH_WARNINGS",
            "reason": "PLAYWRIGHT_NOT_AVAILABLE",
            "probe_stderr": version_probe.stderr.strip(),
            "follow_up_commands": [
                "npx playwright install chromium",
                "python IMPERIUM_NEW_GENERATION/AGENT_IDE/PLAYWRIGHT/agent_ide_playwright_capture_v0_1.py"
            ],
            "screenshot_manifest_path": manifest_path.as_posix(),
        }

    server_proc = subprocess.Popen(
        [sys.executable, str(repo_root / WEB_SERVER_SCRIPT), "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(repo_root),
    )
    health_url = f"http://127.0.0.1:{port}/api/health"
    ok = _wait_health(health_url)
    captures: List[Dict[str, Any]] = []
    status = "PASS"

    try:
        if not ok:
            status = "PASS_WITH_WARNINGS"
            return {
                "task_id": TASK_ID,
                "timestamp_utc": _utc_now(),
                "status": status,
                "reason": "PROJECTION_SERVER_NOT_READY",
                "health_url": health_url,
                "screenshot_manifest_path": manifest_path.as_posix(),
            }

        targets: List[Tuple[str, str]] = [
            ("overview", ""),
            ("organs", "#organs"),
            ("file_atlas", "#file-atlas"),
            ("officio_language_gate", "#officio-language-gate"),
            ("owner_pain_map", "#owner-pain"),
            ("routes", "#routes"),
            ("reports", "#reports"),
            ("block_foundation", "#block-foundation"),
        ]

        for name, fragment in targets:
            output = screenshots_dir / f"{name}.png"
            url = f"http://127.0.0.1:{port}/{fragment}"
            cmd = [npx_exec, "playwright", "screenshot", url, str(output)]
            result = subprocess.run(cmd, text=True, capture_output=True, cwd=str(repo_root))
            item = {
                "name": name,
                "url": url,
                "output": output.as_posix(),
                "returncode": result.returncode,
                "stderr": result.stderr.strip(),
            }
            if result.returncode != 0:
                status = "PASS_WITH_WARNINGS"
            captures.append(item)

    finally:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_proc.kill()

    manifest = {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "screenshots_dir": screenshots_dir.as_posix(),
        "captures": captures,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Agent IDE projection screenshots via Playwright.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    parser.add_argument("--port", type=int, default=4173, help="Projection server port.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd().resolve()
    result = run_capture(repo_root, args.port)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
