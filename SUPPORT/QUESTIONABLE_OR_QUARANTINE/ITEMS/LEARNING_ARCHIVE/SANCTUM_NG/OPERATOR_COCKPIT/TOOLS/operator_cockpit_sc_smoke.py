#!/usr/bin/env python3
"""Smoke runner for stable vs candidate operator cockpit tracks."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260523-NEWGEN-SANCTUM-COCKPIT-STABLE-CANDIDATE-VISUAL-OBSERVABILITY-PC-V0_1"
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


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def add_step(steps: list[dict[str, Any]], warnings: list[str], blockers: list[str], step: str, status: str, details: Any) -> None:
    steps.append({"step": step, "status": status, "details": details})
    if status == "WARN":
        warnings.append(step)
    if status == "BLOCK":
        blockers.append(step)


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[4]
    default_report_dir = default_repo_root / f"{BASE_REL}/REPORTS/{TASK_ID_DEFAULT}"
    parser = argparse.ArgumentParser(description="Run stable/candidate cockpit smoke checks.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_report_dir / "operator_cockpit_sc_smoke_report.json")
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

    sc_builder = repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_sc_builder.py"
    sc_validator = repo_root / f"{BASE_REL}/TOOLS/operator_cockpit_sc_validator.py"

    build_cmd = [
        "python",
        str(sc_builder),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
    ]
    build_res = run_command(build_cmd, repo_root)
    add_step(
        steps,
        warnings,
        blockers,
        "build_stable_candidate_state",
        "PASS" if build_res["returncode"] == 0 else "BLOCK",
        build_res,
    )

    stable_url = (
        f"http://127.0.0.1:{args.port}/IMPERIUM_NEW_GENERATION/"
        "SANCTUM_NG/APP/operator_cockpit_l1.html"
    )
    candidate_url = (
        f"http://127.0.0.1:{args.port}/IMPERIUM_NEW_GENERATION/"
        "SANCTUM_NG/APP/operator_cockpit_candidate.html"
    )

    server_cmd = ["python", "-m", "http.server", str(args.port), "--bind", "127.0.0.1"]
    server_proc = subprocess.Popen(
        server_cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    ready = False
    for _ in range(20):
        if http_ok(stable_url) and http_ok(candidate_url):
            ready = True
            break
        time.sleep(0.25)

    add_step(
        steps,
        warnings,
        blockers,
        "local_urls_ready",
        "PASS" if ready else "BLOCK",
        {"stable_url": stable_url, "candidate_url": candidate_url},
    )

    matrix_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    edge_path = detect_edge()
    temp_profile_dir: Path | None = None

    captures = [
        ("overview_1920x1080_en", 1920, 1080, stable_url, candidate_url),
        (
            "evidence_1920x1700_ru",
            1920,
            1700,
            f"{stable_url}?lang=ru&focus=evidence-diff",
            f"{candidate_url}?lang=ru&focus=evidence-diff",
        ),
    ]

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
        temp_profile_dir = Path(tempfile.mkdtemp(prefix="imperium_edge_profile_sc_"))
        for name, width, height, stable_target, candidate_target in captures:
            stable_png = screenshot_dir / f"stable_{name}.png"
            candidate_png = screenshot_dir / f"candidate_{name}.png"
            for label, url, png in (
                ("stable", stable_target, stable_png),
                ("candidate", candidate_target, candidate_png),
            ):
                cmd = [
                    str(edge_path),
                    "--headless=new",
                    "--disable-gpu",
                    "--hide-scrollbars",
                    "--virtual-time-budget=7000",
                    f"--user-data-dir={temp_profile_dir}",
                    f"--window-size={width},{height}",
                    f"--screenshot={png}",
                    url,
                ]
                shot_res = run_command(cmd, repo_root, timeout_sec=70.0)
                ok = shot_res["returncode"] == 0 and png.exists() and png.stat().st_size > 0
                status = "PASS" if ok else "WARN"
                add_step(steps, warnings, blockers, f"screenshot_{label}_{name}", status, shot_res)
                matrix_rows.append(
                    {
                        "name": f"{label}_{name}",
                        "track": label,
                        "viewport": f"{width}x{height}",
                        "url": url,
                        "status": status,
                        "path": png.relative_to(repo_root).as_posix() if png.exists() else "MISSING",
                        "size_bytes": png.stat().st_size if png.exists() else 0,
                    }
                )
            if stable_png.exists() and candidate_png.exists():
                stable_hash = sha256_of(stable_png)
                candidate_hash = sha256_of(candidate_png)
                comparison_rows.append(
                    {
                        "name": name,
                        "stable_path": stable_png.relative_to(repo_root).as_posix(),
                        "candidate_path": candidate_png.relative_to(repo_root).as_posix(),
                        "stable_sha256": stable_hash,
                        "candidate_sha256": candidate_hash,
                        "is_identical": stable_hash == candidate_hash,
                    }
                )

    if temp_profile_dir and temp_profile_dir.exists():
        shutil.rmtree(temp_profile_dir, ignore_errors=True)

    if server_proc.poll() is None:
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()
    add_step(steps, warnings, blockers, "server_shutdown", "PASS", {"port": args.port})

    matrix_payload = {
        "schema_id": "OPERATOR_COCKPIT_STABLE_CANDIDATE_SCREENSHOT_MATRIX_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "captures": matrix_rows,
    }
    matrix_path = report_dir / "screenshot_matrix.json"
    matrix_path.write_text(json.dumps(matrix_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    has_delta = any(not item["is_identical"] for item in comparison_rows)
    comparison_payload = {
        "schema_id": "OPERATOR_COCKPIT_STABLE_CANDIDATE_COMPARISON_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "pairs": comparison_rows,
        "candidate_visual_delta_detected": has_delta,
        "notes": [
            "Hash difference is used as machine-level visual delta signal.",
            "Human review is required in FINAL_REPORT before promotion decision.",
        ],
    }
    comparison_path = report_dir / "stable_candidate_comparison.json"
    comparison_path.write_text(json.dumps(comparison_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    validate_cmd = [
        "python",
        str(sc_validator),
        "--repo-root",
        str(repo_root),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
    ]
    validate_res = run_command(validate_cmd, repo_root)
    if validate_res["returncode"] == 0:
        validate_status = "PASS"
    else:
        validate_status = "BLOCK"
    add_step(steps, warnings, blockers, "validate_stable_candidate", validate_status, validate_res)

    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"
    else:
        verdict = "PASS"

    smoke_report = {
        "schema_id": "OPERATOR_COCKPIT_STABLE_CANDIDATE_SMOKE_REPORT_V0_1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "stable_url": stable_url,
        "candidate_url": candidate_url,
        "steps": steps,
        "warnings": warnings,
        "blockers": blockers,
        "screenshot_matrix_ref": matrix_path.relative_to(repo_root).as_posix(),
        "comparison_ref": comparison_path.relative_to(repo_root).as_posix(),
        "claim_boundary": "IMPROVED_PC_OPERATOR_SHELL_ONLY",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(smoke_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"operator_cockpit_sc_smoke_verdict={verdict}")
    print(f"operator_cockpit_sc_smoke_report={output.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
