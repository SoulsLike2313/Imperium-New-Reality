#!/usr/bin/env python3
"""Playwright proof for Important Six dashboard L2 action surface."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1"
GROUP_SAFE_ACTIONS = [
    "ADMIN_FULL_NEWGEN_FILE_AUDIT",
    "TRANSFER_SEND_TASKPACK_VM2_DRY_RUN",
    "MECHANICUS_CHECK_REQUIRED_TOOLS",
    "INQUISITION_REPO_HYGIENE_AUDIT",
    "ASTRONOMICON_REGISTER_TASK_DRAFT",
    "DIFF_COMPARE_HEADS",
    "OWNER_QUESTIONS_LIST",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_cmd(cmd: list[str], timeout_sec: float | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
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
    except FileNotFoundError as exc:
        return {
            "command": cmd,
            "returncode": 127,
            "stdout": "",
            "stderr": str(exc),
            "timed_out": False,
        }


def fetch_json(url: str, timeout_sec: float) -> dict[str, Any] | list[Any]:
    with urllib.request.urlopen(url, timeout=timeout_sec) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[4]
    default_out_dir = (
        repo_root
        / "IMPERIUM_NEW_GENERATION"
        / "REPORTS"
        / "TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1"
    )
    parser = argparse.ArgumentParser(description="Run Playwright checks for Important Six dashboard L2.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8766")
    parser.add_argument("--timeout-sec", type=float, default=120.0)
    parser.add_argument("--timeout-ms", type=int, default=120000)
    parser.add_argument("--out-dir", type=Path, default=default_out_dir)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--screenshot", type=Path, default=None)
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = args.report.resolve() if args.report else out_dir / "dashboard_l2_playwright_report.json"
    screenshot_path = args.screenshot.resolve() if args.screenshot else out_dir / "dashboard_l2_screenshot.png"

    steps: list[dict[str, Any]] = []
    blockers: list[str] = []
    warnings: list[str] = []

    def add_step(name: str, status: str, details: Any) -> None:
        steps.append({"step": name, "status": status, "details": details})
        if status == "BLOCK":
            blockers.append(name)
        elif status == "WARN":
            warnings.append(name)

    for endpoint in ("/api/status", "/api/actions", "/api/action-history", "/api/owner-questions", "/api/diff/status"):
        url = args.base_url.rstrip("/") + endpoint
        try:
            payload = fetch_json(url, timeout_sec=args.timeout_sec)
            add_step(f"api_{endpoint}", "PASS", {"url": url, "json_type": type(payload).__name__})
        except Exception as exc:  # noqa: BLE001
            add_step(f"api_{endpoint}", "BLOCK", {"url": url, "error": str(exc)})

    version_cmd = run_cmd(["python", "-m", "playwright", "--version"], timeout_sec=60)
    add_step("python_playwright_version", "PASS" if version_cmd["returncode"] == 0 else "BLOCK", version_cmd)

    install_cmd = run_cmd(["python", "-m", "playwright", "install", "chromium"], timeout_sec=600)
    install_status = "PASS" if install_cmd["returncode"] == 0 else "WARN"
    add_step("python_playwright_install_chromium", install_status, install_cmd)

    ui_details: dict[str, Any] = {
        "page_loaded": False,
        "clicked_actions": [],
        "action_click_errors": [],
        "history_action_ids": [],
        "result_box_text": "",
        "screenshot_saved": False,
        "errors": [],
    }

    try:
        from playwright.sync_api import Error as PlaywrightError  # type: ignore
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # noqa: BLE001
        add_step("import_playwright_sync_api", "BLOCK", str(exc))
    else:
        add_step("import_playwright_sync_api", "PASS", "ok")
        verdict_for_ui = "PASS"
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1920, "height": 1200})
                page.goto(args.base_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
                page.wait_for_selector(".group-card", timeout=args.timeout_ms)
                ui_details["page_loaded"] = True

                for action_id in GROUP_SAFE_ACTIONS:
                    card = page.locator("article.action-item", has_text=action_id).first
                    if card.count() == 0:
                        ui_details["action_click_errors"].append({"action_id": action_id, "error": "card_not_found"})
                        verdict_for_ui = "BLOCK"
                        continue
                    button = card.locator("button.run-btn").first
                    try:
                        button.click(timeout=args.timeout_ms)
                        page.wait_for_timeout(1200)
                        ui_details["clicked_actions"].append(action_id)
                    except PlaywrightError as exc:
                        ui_details["action_click_errors"].append({"action_id": action_id, "error": str(exc)})
                        verdict_for_ui = "BLOCK"

                history_resp = page.request.get(args.base_url.rstrip("/") + "/api/action-history?limit=400", timeout=args.timeout_ms)
                if history_resp.ok:
                    payload = history_resp.json()
                    entries = payload.get("entries", []) if isinstance(payload, dict) else []
                    if isinstance(entries, list):
                        ui_details["history_action_ids"] = [str(item.get("action_id", "")) for item in entries if isinstance(item, dict)]
                    for action_id in GROUP_SAFE_ACTIONS:
                        if action_id not in ui_details["history_action_ids"]:
                            ui_details["action_click_errors"].append({"action_id": action_id, "error": "missing_in_history"})
                            if verdict_for_ui == "PASS":
                                verdict_for_ui = "WARN"
                else:
                    ui_details["errors"].append("history_endpoint_failed")
                    verdict_for_ui = "BLOCK"

                try:
                    ui_details["result_box_text"] = page.locator("#resultBox").inner_text(timeout=args.timeout_ms)
                except PlaywrightError:
                    ui_details["result_box_text"] = ""
                    if verdict_for_ui == "PASS":
                        verdict_for_ui = "WARN"

                page.screenshot(path=str(screenshot_path), full_page=True)
                ui_details["screenshot_saved"] = screenshot_path.exists()
                if not ui_details["screenshot_saved"]:
                    ui_details["errors"].append("screenshot_not_saved")
                    verdict_for_ui = "BLOCK"

                browser.close()
        except Exception as exc:  # noqa: BLE001
            ui_details["errors"].append(str(exc))
            verdict_for_ui = "BLOCK"

        add_step(
            "playwright_ui_checks",
            "PASS" if verdict_for_ui == "PASS" else ("WARN" if verdict_for_ui == "WARN" else "BLOCK"),
            ui_details,
        )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report_payload = {
        "schema_id": "important_six_dashboard_l2_playwright_report_v0_1",
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "base_url": args.base_url,
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "steps": steps,
        "group_safe_actions": GROUP_SAFE_ACTIONS,
        "screenshot_path": str(screenshot_path),
    }
    write_json(report_path, report_payload)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

