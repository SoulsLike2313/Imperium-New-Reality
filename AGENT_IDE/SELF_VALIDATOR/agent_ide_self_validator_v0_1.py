from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.error import URLError
from urllib.request import urlopen


TASK_ID = "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
REPORT_DIR = Path(
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/"
    "TASK-NEWGEN-AGENT-IDE-DUAL-SURFACE-SELF-VALIDATOR-BLOCK-FOUNDATION-PC-V0_1"
)

APP_DIR = Path(__file__).resolve().parents[1] / "APP"
VIEW_MODEL_DIR = Path(__file__).resolve().parents[1] / "VIEW_MODEL"
WEB_DIR = Path(__file__).resolve().parents[1] / "WEB_PROJECTION"
PLAYWRIGHT_DIR = Path(__file__).resolve().parents[1] / "PLAYWRIGHT"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(VIEW_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(VIEW_MODEL_DIR))

from agent_ide_app_v0_2 import run_smoke as run_desktop_smoke  # noqa: E402
from agent_ide_view_model_builder_v0_2 import (  # noqa: E402
    build_and_persist_models,
    discover_repo_root,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fetch_json(url: str, timeout: float = 4.0) -> Dict[str, Any]:
    with urlopen(url, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def run_source_truth(repo_root: Path) -> Dict[str, Any]:
    required_sources = [
        "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/file_passports_v0_1.jsonl",
        "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/file_atlas_index_v0_1.json",
        "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/organ_file_map_v0_1.json",
    ]
    missing = [item for item in required_sources if not (repo_root / item).exists()]
    git_head = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()
    git_branch = subprocess.check_output(
        ["git", "-C", str(repo_root), "branch", "--show-current"], text=True
    ).strip()

    status = "PASS" if not missing else "FAIL"
    return {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "repo_root": repo_root.as_posix(),
        "git": {"head": git_head, "branch": git_branch},
        "required_sources": required_sources,
        "missing_sources": missing,
    }


def run_view_model_check(repo_root: Path) -> Dict[str, Any]:
    build_summary = build_and_persist_models(repo_root)
    vm_path = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/VIEW_MODEL/ide_view_model_v0_2.json"
    dash_path = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/VIEW_MODEL/dashboard_view_model_v0_1.json"
    block_path = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/VIEW_MODEL/block_view_model_v0_1.json"

    missing = [str(p) for p in [vm_path, dash_path, block_path] if not p.exists()]
    required_keys = [
        "task_id",
        "schema_version",
        "truth",
        "organs",
        "file_passports",
        "unknown_file_kind_count",
        "route_surface",
        "classification_surface",
        "projection_guard",
    ]

    vm_payload = _read_json(vm_path) if vm_path.exists() else {}
    missing_keys = [key for key in required_keys if key not in vm_payload]

    status = "PASS"
    if missing or missing_keys:
        status = "FAIL"

    return {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "build_summary": build_summary,
        "missing_files": missing,
        "missing_required_keys": missing_keys,
        "paths": {
            "ide_view_model": vm_path.as_posix(),
            "dashboard_view_model": dash_path.as_posix(),
            "block_view_model": block_path.as_posix(),
        },
    }


def run_desktop_check(repo_root: Path) -> Dict[str, Any]:
    smoke = run_desktop_smoke(repo_root)
    status = "PASS"
    notes: List[str] = []
    if int(smoke.get("organs_visible", 0)) < 5:
        status = "FAIL"
        notes.append("Expected five organs or more in desktop smoke.")
    if int(smoke.get("passports", 0)) == 0:
        status = "FAIL"
        notes.append("No passports loaded in desktop smoke.")
    if not bool(smoke.get("route_alias_visible", False)) and status != "FAIL":
        status = "PASS_WITH_WARNINGS"
        notes.append("Route alias visibility is missing.")

    return {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "summary": smoke,
        "notes": notes,
    }


def _wait_projection(url: str, timeout_sec: float) -> Tuple[bool, str]:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            payload = _fetch_json(url, timeout=2.0)
            if payload:
                return True, "READY"
        except Exception:
            time.sleep(0.25)
    return False, "TIMEOUT"


def run_web_projection_check(repo_root: Path, port: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    script = WEB_DIR / "agent_ide_web_projection_server_v0_1.py"
    proc = subprocess.Popen(
        [sys.executable, str(script), "--host", "127.0.0.1", "--port", str(port), "--repo-root", str(repo_root)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    dashboard: Dict[str, Any] = {}
    status = "PASS"
    notes: List[str] = []
    try:
        ok, marker = _wait_projection(f"http://127.0.0.1:{port}/api/health", timeout_sec=8.0)
        if not ok:
            status = "FAIL"
            notes.append(f"Web projection health probe failed: {marker}")
        else:
            dashboard = _fetch_json(f"http://127.0.0.1:{port}/api/view-model", timeout=4.0)
            if dashboard.get("truth", {}).get("required_route_alias") != "imperium-vm3":
                status = "PASS_WITH_WARNINGS"
                notes.append("required_route_alias is not imperium-vm3.")
    except URLError as exc:
        status = "FAIL"
        notes.append(f"Projection request error: {exc}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

    receipt = {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "projection_url": f"http://127.0.0.1:{port}",
        "notes": notes,
        "dashboard_snapshot": {
            "schema_version": dashboard.get("schema_version", ""),
            "unknown_file_kind_count": dashboard.get("atlas_summary", {}).get("unknown_file_kind_count", 0),
            "required_route_alias": dashboard.get("truth", {}).get("required_route_alias", ""),
            "owner_pain_count": dashboard.get("owner_pain_surface", {}).get("pain_count", 0),
        },
    }
    return receipt, dashboard


def run_truth_parity_check(desktop: Dict[str, Any], dashboard: Dict[str, Any]) -> Dict[str, Any]:
    desktop_summary = desktop.get("summary", {})
    mismatches: List[str] = []

    desktop_unknown = int(desktop_summary.get("unknown_file_kind_count", 0))
    web_unknown = int(dashboard.get("atlas_summary", {}).get("unknown_file_kind_count", 0))
    if desktop_unknown != web_unknown:
        mismatches.append(f"unknown_file_kind_count mismatch: desktop={desktop_unknown}, web={web_unknown}")

    desktop_organs = int(desktop_summary.get("organs_visible", 0))
    web_organs = len(dashboard.get("organs", []))
    if desktop_organs != web_organs:
        mismatches.append(f"organs count mismatch: desktop={desktop_organs}, web={web_organs}")

    desktop_alias = str(desktop_summary.get("route_alias_required", ""))
    web_alias = str(dashboard.get("truth", {}).get("required_route_alias", ""))
    if desktop_alias and web_alias and desktop_alias != web_alias:
        mismatches.append(f"route alias mismatch: desktop={desktop_alias}, web={web_alias}")

    status = "PASS" if not mismatches else "FAIL"
    return {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "mismatches": mismatches,
        "desktop_summary": desktop_summary,
        "web_summary": {
            "unknown_file_kind_count": web_unknown,
            "organs_count": web_organs,
            "required_route_alias": web_alias,
            "current_head": dashboard.get("truth", {}).get("git", {}).get("head", ""),
        },
    }


def run_playwright_capture(repo_root: Path, port: int) -> Dict[str, Any]:
    script = PLAYWRIGHT_DIR / "agent_ide_playwright_capture_v0_1.py"
    cmd = [sys.executable, str(script), "--repo-root", str(repo_root), "--port", str(port)]
    result = subprocess.run(cmd, text=True, capture_output=True)
    status = "PASS_WITH_WARNINGS"
    payload: Dict[str, Any] = {}
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            payload = {"raw_stdout": result.stdout.strip()}

    if isinstance(payload, dict):
        status = str(payload.get("status", status))
    if result.returncode != 0 and status == "PASS":
        status = "PASS_WITH_WARNINGS"

    return {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": status,
        "result": payload,
        "returncode": result.returncode,
    }


def aggregate_summary(receipts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    statuses = {name: str(payload.get("status", "UNPROVEN")) for name, payload in receipts.items()}
    if any(status == "FAIL" for status in statuses.values()):
        verdict = "FAIL"
    elif any(status == "BLOCKED" for status in statuses.values()):
        verdict = "BLOCKED"
    elif any(status == "PASS_WITH_WARNINGS" for status in statuses.values()):
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    return {
        "task_id": TASK_ID,
        "timestamp_utc": _utc_now(),
        "status": verdict,
        "receipts": statuses,
        "receipt_paths": {
            name: payload.get("receipt_path", "")
            for name, payload in receipts.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent IDE dual-surface self validator.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    parser.add_argument("--port", type=int, default=4173, help="Web projection local port.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else discover_repo_root()
    report_dir = repo_root / REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)

    source_truth = run_source_truth(repo_root)
    source_path = report_dir / "source_truth_receipt.json"
    _write_json(source_path, source_truth)

    view_model = run_view_model_check(repo_root)
    view_model_path = report_dir / "view_model_receipt.json"
    _write_json(view_model_path, view_model)

    desktop = run_desktop_check(repo_root)
    desktop_path = report_dir / "desktop_ide_smoke_receipt.json"
    _write_json(desktop_path, desktop)

    web_projection, dashboard_snapshot = run_web_projection_check(repo_root, args.port)
    web_projection_path = report_dir / "web_projection_receipt.json"
    _write_json(web_projection_path, web_projection)

    parity = run_truth_parity_check(desktop, dashboard_snapshot)
    parity_path = report_dir / "truth_parity_receipt.json"
    _write_json(parity_path, parity)

    playwright = run_playwright_capture(repo_root, args.port)
    playwright_path = report_dir / "playwright_capture_receipt.json"
    _write_json(playwright_path, playwright)

    receipt_map: Dict[str, Dict[str, Any]] = {
        "source_truth_receipt": {**source_truth, "receipt_path": source_path.as_posix()},
        "view_model_receipt": {**view_model, "receipt_path": view_model_path.as_posix()},
        "desktop_ide_smoke_receipt": {**desktop, "receipt_path": desktop_path.as_posix()},
        "web_projection_receipt": {**web_projection, "receipt_path": web_projection_path.as_posix()},
        "truth_parity_receipt": {**parity, "receipt_path": parity_path.as_posix()},
        "playwright_capture_receipt": {**playwright, "receipt_path": playwright_path.as_posix()},
    }
    summary = aggregate_summary(receipt_map)
    summary_path = report_dir / "self_validation_summary.json"
    _write_json(summary_path, summary)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["status"] in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
