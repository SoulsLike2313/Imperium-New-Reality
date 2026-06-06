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

TASK_ID = "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"
REPORT_DIR = Path(
    "IMPERIUM_NEW_GENERATION/AGENT_IDE/REPORTS/"
    "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"
)
APP_DIR = Path(__file__).resolve().parents[1] / "APP"
VIEW_MODEL_DIR = Path(__file__).resolve().parents[1] / "VIEW_MODEL"
WEB_DIR = Path(__file__).resolve().parents[1] / "WEB_PROJECTION"
PLAYWRIGHT_DIR = Path(__file__).resolve().parents[1] / "PLAYWRIGHT"
TOOLS_DIR = Path(__file__).resolve().parents[1] / "TOOLS"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(VIEW_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(VIEW_MODEL_DIR))

from agent_ide_view_model_builder_v0_2 import build_and_persist_models, discover_repo_root  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str, timeout: float = 5.0) -> Dict[str, Any]:
    with urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def status_worst(statuses: List[str]) -> str:
    if any(item == "FAIL" for item in statuses):
        return "FAIL"
    if any(item == "BLOCKED" for item in statuses):
        return "BLOCKED"
    if any(item == "PASS_WITH_WARNINGS" for item in statuses):
        return "PASS_WITH_WARNINGS"
    return "PASS"


def run_source_truth(repo_root: Path) -> Dict[str, Any]:
    required_files = [
        "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/file_passports_v0_1.jsonl",
        "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/file_atlas_index_v0_1.json",
        "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/organ_file_map_v0_1.json",
        "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/route_connection_surface_index_v0_1.json",
        "IMPERIUM_NEW_GENERATION/ADMINISTRATUM/FILE_ATLAS/owner_pain_to_file_map_v0_1.json",
    ]
    missing = [item for item in required_files if not (repo_root / item).exists()]

    parse_errors: List[str] = []
    for rel in required_files:
        full = repo_root / rel
        if not full.exists() or full.suffix == ".jsonl":
            continue
        try:
            read_json(full)
        except Exception as exc:
            parse_errors.append(f"{rel}::{exc}")

    head = subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()
    branch = subprocess.check_output(["git", "-C", str(repo_root), "branch", "--show-current"], text=True).strip()

    status = "PASS" if not missing and not parse_errors else "FAIL"
    return {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": status,
        "required_files": required_files,
        "missing_files": missing,
        "parse_errors": parse_errors,
        "git": {"head": head, "branch": branch},
    }


def run_view_model(repo_root: Path) -> Dict[str, Any]:
    build_summary = build_and_persist_models(repo_root)
    dashboard_path = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/VIEW_MODEL/dashboard_view_model_v0_1.json"
    block_path = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/VIEW_MODEL/block_view_model_v0_1.json"

    missing = [item for item in [dashboard_path, block_path] if not item.exists()]
    required_dashboard_keys = [
        "truth",
        "organs",
        "atlas_summary",
        "language_gate_surface",
        "route_surface",
        "report_receipt_summary",
        "owner_pain_surface",
        "self_validator_surface",
        "file_passports_projection",
    ]

    missing_keys: List[str] = []
    if dashboard_path.exists():
        dashboard_payload = read_json(dashboard_path)
        for key in required_dashboard_keys:
            if key not in dashboard_payload:
                missing_keys.append(key)
    else:
        dashboard_payload = {}

    status = "PASS" if not missing and not missing_keys else "FAIL"
    return {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": status,
        "build_summary": build_summary,
        "missing_files": [item.as_posix() for item in missing],
        "missing_dashboard_keys": missing_keys,
        "truth_head": dashboard_payload.get("truth", {}).get("git", {}).get("head", ""),
    }


def run_script(repo_root: Path, relative_script: str, extra_args: List[str] | None = None) -> Dict[str, Any]:
    cmd = [sys.executable, str(repo_root / relative_script)]
    if extra_args:
        cmd.extend(extra_args)
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    payload: Dict[str, Any] = {
        "command": " ".join(cmd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
    if completed.stdout.strip():
        try:
            payload["parsed_stdout"] = json.loads(completed.stdout)
        except json.JSONDecodeError:
            pass
    return payload


def run_projection_health(repo_root: Path, port: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    script = WEB_DIR / "agent_ide_web_projection_server_v0_1.py"
    proc = subprocess.Popen(
        [sys.executable, str(script), "--host", "127.0.0.1", "--port", str(port), "--repo-root", str(repo_root)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    health_url = f"http://127.0.0.1:{port}/api/health"
    dashboard_url = f"http://127.0.0.1:{port}/api/view-model"
    status = "PASS"
    notes: List[str] = []
    dashboard: Dict[str, Any] = {}

    try:
        deadline = time.time() + 10
        healthy = False
        while time.time() < deadline:
            try:
                _ = fetch_json(health_url, timeout=2.0)
                healthy = True
                break
            except Exception:
                time.sleep(0.25)

        if not healthy:
            status = "FAIL"
            notes.append("Projection health endpoint not reachable")
        else:
            health = fetch_json(health_url, timeout=4.0)
            dashboard = fetch_json(dashboard_url, timeout=4.0)
            if health.get("status") != "PASS":
                status = "FAIL"
                notes.append("/api/health status is not PASS")
            if "ui_mode" not in health:
                status = "PASS_WITH_WARNINGS"
                notes.append("ui_mode missing in health payload")
            if not dashboard.get("route_surface", {}).get("required_alias"):
                status = "FAIL"
                notes.append("route_surface.required_alias missing")
            if dashboard.get("truth", {}).get("required_route_alias") != "imperium-vm3":
                if status != "FAIL":
                    status = "PASS_WITH_WARNINGS"
                notes.append("required route alias differs from imperium-vm3")
    except URLError as exc:
        status = "FAIL"
        notes.append(str(exc))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

    return (
        {
            "task_id": TASK_ID,
            "timestamp_utc": utc_now(),
            "status": status,
            "health_url": health_url,
            "dashboard_url": dashboard_url,
            "notes": notes,
        },
        dashboard,
    )


def run_private_content_policy_check(dashboard: Dict[str, Any]) -> Dict[str, Any]:
    projection = dashboard.get("file_passports_projection", [])
    violations: List[str] = []

    for item in projection:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", ""))
        cls = str(item.get("classification", ""))
        visibility = str(item.get("projection_visibility", ""))
        if cls in {"PRIVATE_CONTEXT", "LOCAL_CONTEXT"} and path != "[RESTRICTED]":
            violations.append(f"restricted class leaked path: {path}")
        upper = path.upper().replace("\\", "/")
        if ("/PRIVATE/" in upper or "/LOCAL/" in upper) and visibility != "SUMMARY_ONLY":
            violations.append(f"private/local visible beyond summary: {path}")

    status = "PASS" if not violations else "FAIL"
    return {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": status,
        "violations": violations,
        "projection_count": len(projection),
    }


def run_truth_marker_parity(report_dir: Path) -> Dict[str, Any]:
    marker_path = report_dir / "dom_truth_marker_snapshot.json"
    if not marker_path.exists():
        return {
            "task_id": TASK_ID,
            "timestamp_utc": utc_now(),
            "status": "PASS_WITH_WARNINGS",
            "reason": "DOM_MARKER_SNAPSHOT_MISSING",
            "marker_snapshot_path": marker_path.as_posix(),
            "mismatches": ["snapshot missing"],
        }

    payload = read_json(marker_path)
    mismatches = payload.get("mismatches", []) if isinstance(payload, dict) else ["invalid snapshot payload"]
    if not isinstance(mismatches, list):
        mismatches = ["invalid mismatches format"]

    status = "PASS" if not mismatches else "FAIL"
    return {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": status,
        "marker_snapshot_path": marker_path.as_posix(),
        "mismatches": mismatches,
        "dom": payload.get("dom", {}) if isinstance(payload, dict) else {},
        "expected": payload.get("expected", {}) if isinstance(payload, dict) else {},
    }


def run_mechanicus_registration_check(repo_root: Path) -> Dict[str, Any]:
    registration_path = (
        repo_root
        / "IMPERIUM_NEW_GENERATION/MECHANICUS/REPORTS/"
        / "TASK-NEWGEN-AGENT-IDE-WEB-SHELL-REACT-TAURI-PLAYWRIGHT-PARITY-PC-V0_1"
        / "agent_ide_tool_registration_entries_v0_1.json"
    )

    required_tool_ids = {
        "AGENT_IDE_VIEW_MODEL_BUILDER_V0_2",
        "AGENT_IDE_WEB_PROJECTION_SERVER_V0_1",
        "AGENT_IDE_REACT_BUILD_CHECK_V0_1",
        "AGENT_IDE_DESKTOP_SHELL_PROBE_V0_1",
        "AGENT_IDE_PLAYWRIGHT_PARITY_CAPTURE_V0_2",
        "AGENT_IDE_SELF_VALIDATOR_V0_2",
    }

    if not registration_path.exists():
        return {
            "task_id": TASK_ID,
            "timestamp_utc": utc_now(),
            "status": "FAIL",
            "reason": "REGISTRATION_FILE_MISSING",
            "registration_path": registration_path.as_posix(),
            "missing_tool_ids": sorted(required_tool_ids),
        }

    payload = read_json(registration_path)
    tools = payload.get("tools", []) if isinstance(payload, dict) else []
    tool_ids = {str(item.get("tool_id", "")) for item in tools if isinstance(item, dict)}
    missing = sorted(required_tool_ids - tool_ids)
    status = "PASS" if not missing else "FAIL"

    return {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": status,
        "registration_path": registration_path.as_posix(),
        "missing_tool_ids": missing,
        "registered_tool_ids": sorted(tool_ids),
    }


def aggregate(receipts: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    statuses = {name: payload.get("status", "UNPROVEN") for name, payload in receipts.items()}
    verdict = status_worst(list(statuses.values()))
    return {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": verdict,
        "receipts": statuses,
        "receipt_paths": {name: payload.get("receipt_path", "") for name, payload in receipts.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent IDE web-shell self validator V0.2.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    parser.add_argument("--port", type=int, default=4173, help="Projection server local port.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else discover_repo_root()
    report_dir = repo_root / REPORT_DIR
    report_dir.mkdir(parents=True, exist_ok=True)

    receipts: Dict[str, Dict[str, Any]] = {}

    source_truth = run_source_truth(repo_root)
    source_truth_path = report_dir / "source_truth_receipt.json"
    write_json(source_truth_path, source_truth)
    receipts["source_truth_receipt"] = {**source_truth, "receipt_path": source_truth_path.as_posix()}

    view_model = run_view_model(repo_root)
    view_model_path = report_dir / "view_model_receipt.json"
    write_json(view_model_path, view_model)
    receipts["view_model_receipt"] = {**view_model, "receipt_path": view_model_path.as_posix()}

    desktop_probe = run_script(
        repo_root,
        "IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_desktop_shell_probe_v0_1.py",
        ["--repo-root", str(repo_root)],
    )
    desktop_decision_path = repo_root / "IMPERIUM_NEW_GENERATION/AGENT_IDE/DESKTOP_SHELL/tauri_or_electron_decision_v0_1.json"
    desktop_status = "FAIL"
    if desktop_decision_path.exists():
        desktop_status = str(read_json(desktop_decision_path).get("status", "FAIL"))
    desktop_payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": desktop_status if desktop_probe.get("returncode") == 0 else "FAIL",
        "probe_result": desktop_probe,
        "desktop_decision_path": desktop_decision_path.as_posix(),
    }
    desktop_path = report_dir / "desktop_shell_receipt.json"
    write_json(desktop_path, desktop_payload)
    receipts["desktop_shell_receipt"] = {**desktop_payload, "receipt_path": desktop_path.as_posix()}

    react_build = run_script(
        repo_root,
        "IMPERIUM_NEW_GENERATION/AGENT_IDE/TOOLS/agent_ide_react_build_check_v0_1.py",
        ["--repo-root", str(repo_root)],
    )
    react_receipt_path = report_dir / "react_build_check_receipt.json"
    react_status = "FAIL"
    if react_receipt_path.exists():
        react_status = str(read_json(react_receipt_path).get("status", "FAIL"))
    react_payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": react_status if react_build.get("returncode") == 0 else "FAIL",
        "build_result": react_build,
        "receipt_path_ref": react_receipt_path.as_posix(),
    }
    react_path = report_dir / "react_surface_receipt.json"
    write_json(react_path, react_payload)
    receipts["react_surface_receipt"] = {**react_payload, "receipt_path": react_path.as_posix()}

    web_projection, dashboard = run_projection_health(repo_root, args.port)
    web_projection_path = report_dir / "web_projection_receipt.json"
    write_json(web_projection_path, web_projection)
    receipts["web_projection_receipt"] = {**web_projection, "receipt_path": web_projection_path.as_posix()}

    private_policy = run_private_content_policy_check(dashboard)
    private_policy_path = report_dir / "private_content_policy_receipt.json"
    write_json(private_policy_path, private_policy)
    receipts["private_content_policy_receipt"] = {**private_policy, "receipt_path": private_policy_path.as_posix()}

    playwright_capture = run_script(
        repo_root,
        "IMPERIUM_NEW_GENERATION/AGENT_IDE/PLAYWRIGHT/agent_ide_playwright_capture_v0_2.py",
        ["--repo-root", str(repo_root), "--port", str(args.port)],
    )
    playwright_manifest_path = report_dir / "playwright_screenshot_manifest.json"
    playwright_status = "FAIL"
    if playwright_manifest_path.exists():
        playwright_status = str(read_json(playwright_manifest_path).get("status", "FAIL"))
    playwright_payload = {
        "task_id": TASK_ID,
        "timestamp_utc": utc_now(),
        "status": playwright_status if playwright_capture.get("returncode") == 0 else "FAIL",
        "capture_result": playwright_capture,
        "manifest_path": playwright_manifest_path.as_posix(),
    }
    playwright_path = report_dir / "playwright_capture_receipt.json"
    write_json(playwright_path, playwright_payload)
    receipts["playwright_capture_receipt"] = {**playwright_payload, "receipt_path": playwright_path.as_posix()}

    marker_parity = run_truth_marker_parity(report_dir)
    marker_parity_path = report_dir / "truth_parity_receipt.json"
    write_json(marker_parity_path, marker_parity)
    receipts["truth_parity_receipt"] = {**marker_parity, "receipt_path": marker_parity_path.as_posix()}

    mechanicus_check = run_mechanicus_registration_check(repo_root)
    mechanicus_path = report_dir / "mechanicus_registration_receipt.json"
    write_json(mechanicus_path, mechanicus_check)
    receipts["mechanicus_registration_receipt"] = {**mechanicus_check, "receipt_path": mechanicus_path.as_posix()}

    summary = aggregate(receipts)
    summary_path = report_dir / "self_validation_summary.json"
    write_json(summary_path, summary)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["status"] in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
