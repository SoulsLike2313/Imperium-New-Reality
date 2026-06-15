#!/usr/bin/env python3
"""Smoke run for Operator Cockpit L1 with screenshot matrix capture."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-OPERATOR-COCKPIT-L1-OWNER-POWER-PC-V0_1"
BASE_REL = "IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(cmd: list[str], cwd: Path | None = None, timeout_sec: float | None = None) -> dict[str, Any]:
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
            "timeout": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "returncode": 124,
            "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "timeout",
            "timeout": True,
        }


def detect_edge() -> Path | None:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def http_ok(url: str, timeout_sec: float = 5.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout_sec) as resp:
            return 200 <= int(resp.status) < 400
    except Exception:
        return False


def add_step(steps: list[dict[str, Any]], warnings: list[str], blockers: list[str], step: str, status: str, details: Any) -> None:
    steps.append({"step": step, "status": status, "details": details})
    if status == "WARN":
        warnings.append(step)
    if status == "BLOCK":
        blockers.append(step)


def read_validator_verdict(path: Path) -> str:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return "UNKNOWN"
    if not isinstance(payload, dict):
        return "UNKNOWN"
    return str(payload.get("verdict", "UNKNOWN")).upper()


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    parser = argparse.ArgumentParser(description="Run operator cockpit L1 smoke checks.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "operator_cockpit_l1_smoke_report.json")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output = args.output.resolve()
    screenshot_dir = report_dir / "SCREENSHOTS"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    for stale in screenshot_dir.glob("*.png"):
        stale.unlink()

    steps: list[dict[str, Any]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    builder = repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_l1_builder.py"
    validator = repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_l1_validator.py"

    build_cmd = [
        "python",
        str(builder),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
        "--build-small-continuity-pack",
    ]
    build_res = run_command(build_cmd, repo_root)
    add_step(
        steps,
        warnings,
        blockers,
        "build_state",
        "PASS" if build_res["returncode"] == 0 else "BLOCK",
        build_res,
    )

    server_cmd = [
        "python",
        "-m",
        "http.server",
        str(args.port),
        "--bind",
        "127.0.0.1",
    ]
    server_proc = subprocess.Popen(
        server_cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    base_url = (
        f"http://127.0.0.1:{args.port}/IMPERIUM_NEW_GENERATION/"
        "SANCTUM_NG/APP/operator_cockpit_l1.html"
    )
    ready = False
    for _ in range(20):
        if http_ok(base_url):
            ready = True
            break
        time.sleep(0.25)

    add_step(
        steps,
        warnings,
        blockers,
        "local_url_ready",
        "PASS" if ready else "BLOCK",
        {"url": base_url},
    )

    screenshot_matrix: list[dict[str, Any]] = []
    edge_path = detect_edge()
    temp_profile_dir: Path | None = None
    if edge_path is None:
        add_step(
            steps,
            warnings,
            blockers,
            "edge_detect",
            "WARN",
            "Microsoft Edge executable not found; screenshot capture skipped.",
        )
    elif ready:
        temp_profile_dir = Path(tempfile.mkdtemp(prefix="imperium_edge_profile_"))
        captures = [
            ("overview_1920x1080_en", 1920, 1080, base_url),
            ("overview_1920x1080_ru", 1920, 1080, f"{base_url}?lang=ru"),
            ("evidence_diff_1920x2200_ru", 1920, 2200, f"{base_url}?lang=ru"),
            ("transfer_routes_1920x1500_ru", 1920, 1500, f"{base_url}?lang=ru"),
            ("continuity_preview_1366x3200_ru", 1366, 3200, f"{base_url}?lang=ru"),
        ]
        for name, width, height, url in captures:
            png = screenshot_dir / f"{name}.png"
            cmd = [
                str(edge_path),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--virtual-time-budget=5000",
                f"--user-data-dir={temp_profile_dir}",
                f"--window-size={width},{height}",
                f"--screenshot={png}",
                url,
            ]
            shot_res = run_command(cmd, repo_root, timeout_sec=35.0)
            ok = shot_res["returncode"] == 0 and png.exists() and png.stat().st_size > 0
            status = "PASS" if ok else "WARN"
            screenshot_matrix.append(
                {
                    "name": name,
                    "viewport": f"{width}x{height}",
                    "url": url,
                    "status": status,
                    "path": png.relative_to(repo_root).as_posix() if png.exists() else "MISSING",
                    "size_bytes": png.stat().st_size if png.exists() else 0,
                }
            )
            add_step(steps, warnings, blockers, f"screenshot_{name}", status, shot_res)
    if temp_profile_dir and temp_profile_dir.exists():
        shutil.rmtree(temp_profile_dir, ignore_errors=True)

    if server_proc.poll() is None:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()
    add_step(steps, warnings, blockers, "server_shutdown", "PASS", {"port": args.port})

    screenshot_matrix_payload = {
        "schema_id": "OPERATOR_COCKPIT_L1_SCREENSHOT_MATRIX_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "captures": screenshot_matrix,
    }
    matrix_path = report_dir / "screenshot_matrix.json"
    matrix_path.write_text(json.dumps(screenshot_matrix_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    validate_cmd = [
        "python",
        str(validator),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
    ]
    validator_res = run_command(validate_cmd, repo_root)
    validator_report_path = report_dir / "operator_cockpit_l1_validator_report.json"
    validator_verdict = read_validator_verdict(validator_report_path)
    validator_res["validator_verdict"] = validator_verdict
    if validator_res["returncode"] != 0 or validator_verdict == "BLOCK":
        validator_status = "BLOCK"
    elif validator_verdict == "WARN":
        validator_status = "WARN"
    elif validator_verdict == "PASS":
        validator_status = "PASS"
    else:
        validator_status = "WARN"
    add_step(steps, warnings, blockers, "validate_state", validator_status, validator_res)

    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"
    else:
        verdict = "PASS"

    smoke_report = {
        "schema_id": "OPERATOR_COCKPIT_L1_SMOKE_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "local_url": base_url,
        "steps": steps,
        "warnings": warnings,
        "blockers": blockers,
        "screenshot_matrix_ref": matrix_path.relative_to(repo_root).as_posix(),
        "claim_boundary": "READ_ONLY_OWNER_COCKPIT_L1",
        "note": "If Edge is unavailable, screenshot capture degrades to WARN_SCREENSHOT_TOOL_UNAVAILABLE.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(smoke_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"operator_cockpit_smoke_verdict={verdict}")
    print(f"operator_cockpit_smoke_report={output.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
