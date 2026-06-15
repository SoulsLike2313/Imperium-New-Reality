#!/usr/bin/env python3
"""Playwright proof runner for Important Six dashboard L1.

This environment does not ship Python Playwright package, so this script uses
Node Playwright module from npx cache.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260524-NEWGEN-IMPORTANT-SIX-TUI-API-DASHBOARD-L1-VM3-V0_1"
EXPECTED_ORGANS = [
    "doctrinarium",
    "officio",
    "administratum",
    "astronomicon",
    "mechanicus",
    "inquisition",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_cmd(cmd: list[str], cwd: Path | None = None, timeout_sec: float | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout_sec,
        )
        return {
            "command": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "returncode": 124,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "timeout",
            "timed_out": True,
        }


def fetch_json(url: str, timeout_sec: float) -> dict[str, Any] | list[Any]:
    with urllib.request.urlopen(url, timeout=timeout_sec) as response:
        return json.loads(response.read().decode("utf-8"))


def find_playwright_module_path(explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        explicit = explicit.resolve()
        if explicit.exists():
            return explicit
        return None

    npx_root = Path.home() / ".npm" / "_npx"
    if not npx_root.exists():
        return None

    candidates = sorted(
        npx_root.glob("*/node_modules/playwright"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "index.js").exists():
            return candidate.resolve()
    return None


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[4]
    default_out_dir = repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/"
        "TASK-20260524-NEWGEN-IMPORTANT-SIX-TUI-API-DASHBOARD-L1-VM3-V0_1"
    )
    parser = argparse.ArgumentParser(description="Run Playwright proof for Important Six dashboard L1.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8766")
    parser.add_argument("--timeout-sec", type=float, default=60.0)
    parser.add_argument("--timeout-ms", type=int, default=60000)
    parser.add_argument("--out-dir", type=Path, default=default_out_dir)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--screenshot", type=Path, default=None)
    parser.add_argument("--playwright-module-path", type=Path, default=None)
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = args.report.resolve() if args.report else out_dir / "playwright_important_six_dashboard_l1_report.json"
    screenshot_path = (
        args.screenshot.resolve()
        if args.screenshot
        else out_dir / "important_six_dashboard_l1_screenshot.png"
    )

    steps: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []

    def add_step(name: str, status: str, details: Any) -> None:
        steps.append({"step": name, "status": status, "details": details})
        if status == "BLOCK":
            blockers.append(name)
        elif status == "WARN":
            warnings.append(name)

    # Ensure npx playwright CLI exists (and prepare cache).
    npx_version = run_cmd(["npx", "playwright", "--version"], timeout_sec=120)
    add_step("npx_playwright_version", "PASS" if npx_version["returncode"] == 0 else "BLOCK", npx_version)

    if npx_version["returncode"] == 0:
        install_cmd = run_cmd(["npx", "playwright", "install", "chromium"], timeout_sec=600)
        install_status = "PASS" if install_cmd["returncode"] == 0 else "BLOCK"
        add_step("npx_playwright_install_chromium", install_status, install_cmd)
    else:
        add_step("npx_playwright_install_chromium", "BLOCK", "Skipped due to missing npx playwright CLI")

    module_path = find_playwright_module_path(args.playwright_module_path)
    add_step(
        "resolve_playwright_module_path",
        "PASS" if module_path else "BLOCK",
        str(module_path) if module_path else "playwright module path not found in ~/.npm/_npx",
    )

    # API checks inside Playwright proof script.
    for endpoint in ("/api/status", "/api/organs", "/api/dashboard-state"):
        url = args.base_url.rstrip("/") + endpoint
        try:
            payload = fetch_json(url, timeout_sec=args.timeout_sec)
            add_step(
                f"api_json_{endpoint}",
                "PASS",
                {
                    "url": url,
                    "json_type": type(payload).__name__,
                },
            )
        except Exception as exc:  # noqa: BLE001
            add_step(f"api_json_{endpoint}", "BLOCK", {"url": url, "error": str(exc)})

    node_result: dict[str, Any] = {}

    if module_path is not None:
        js_code = r"""
const fs = require('fs');

(async () => {
  const modulePath = process.argv[2];
  const baseUrl = process.argv[3];
  const screenshotPath = process.argv[4];
  const timeoutMs = Number(process.argv[5]);
  const expectedOrgans = JSON.parse(process.argv[6]);

  const { chromium } = require(modulePath);

  let verdict = 'PASS';
  const detail = {
    generated_at_utc: new Date().toISOString(),
    panel_count: 0,
    panel_checks: [],
    screenshot_path: screenshotPath,
    screenshot_saved: false,
    errors: []
  };

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1200 } });

  try {
    const response = await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    detail.http_status = response ? response.status() : null;

    await page.waitForSelector('[data-organ-panel]', { timeout: timeoutMs });
    detail.panel_count = await page.locator('[data-organ-panel]').count();

    if (detail.panel_count !== 6) {
      verdict = 'BLOCK';
      detail.errors.push(`panel_count=${detail.panel_count}`);
    }

    for (const organKey of expectedOrgans) {
      const locator = page.locator(`[data-organ-panel="${organKey}"]`);
      const count = await locator.count();
      const check = { organ_key: organKey, present: count > 0, has_status: false, has_command: false, has_output: false, status: 'PASS' };
      if (count === 0) {
        check.status = 'BLOCK';
        verdict = 'BLOCK';
      } else {
        const panel = locator.first();
        const text = await panel.innerText();
        check.has_status = /PASS|WARN|BLOCK|UNKNOWN|Status|Verdict|Вердикт|Статус/i.test(text);
        check.has_command = /--smoke/.test(text) && /--sample/.test(text);
        check.has_output = (await panel.locator('.output-pre').count()) >= 2;
        if (!(check.has_status && check.has_command && check.has_output)) {
          check.status = 'WARN';
          if (verdict === 'PASS') {
            verdict = 'WARN';
          }
        }
      }
      detail.panel_checks.push(check);
    }

    await page.screenshot({ path: screenshotPath, fullPage: true });
    detail.screenshot_saved = fs.existsSync(screenshotPath);
    if (!detail.screenshot_saved) {
      verdict = 'BLOCK';
      detail.errors.push('screenshot_not_saved');
    }
  } catch (error) {
    verdict = 'BLOCK';
    detail.errors.push(String(error && error.stack ? error.stack : error));
  } finally {
    await browser.close();
  }

  const out = { verdict, detail };
  process.stdout.write(JSON.stringify(out));
  process.exit(verdict === 'PASS' ? 0 : 1);
})();
"""

        with tempfile.TemporaryDirectory(prefix="important_six_pw_") as temp_dir:
            js_path = Path(temp_dir) / "runner.js"
            js_path.write_text(js_code, encoding="utf-8")

            cmd = [
                "node",
                str(js_path),
                str(module_path),
                args.base_url,
                str(screenshot_path),
                str(args.timeout_ms),
                json.dumps(EXPECTED_ORGANS),
            ]
            js_exec = run_cmd(cmd, timeout_sec=max(120.0, args.timeout_sec))

            parsed_stdout: dict[str, Any] | None = None
            if js_exec["stdout"]:
                try:
                    payload = json.loads(js_exec["stdout"])
                    if isinstance(payload, dict):
                        parsed_stdout = payload
                except json.JSONDecodeError:
                    parsed_stdout = None

            node_result = {
                "command": cmd,
                "returncode": js_exec["returncode"],
                "stderr": js_exec["stderr"],
                "stdout_json": parsed_stdout,
            }
            status = "PASS" if js_exec["returncode"] == 0 else "BLOCK"
            add_step("playwright_ui_checks", status, node_result)
    else:
        add_step("playwright_ui_checks", "BLOCK", "Playwright module path unavailable")

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report_payload = {
        "schema_id": "playwright_important_six_dashboard_l1_report_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "base_url": args.base_url,
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "steps": steps,
        "screenshot_path": str(screenshot_path),
        "node_result": node_result,
    }

    write_json(report_path, report_payload)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
