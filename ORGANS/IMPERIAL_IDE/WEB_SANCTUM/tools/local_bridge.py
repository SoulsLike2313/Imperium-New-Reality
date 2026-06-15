#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socketserver
import subprocess
import sys
import threading
import time
import uuid
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

SURFACE = "WEB_SANCTUM_VISUAL_INQUISITION_FAST_NAV_V0_8_4_1"
VERSION = "0.8.4.1"
TASK_ID = "H-TASK-NEWREALITY-PC-SERVITOR-WARP-RUNTIME-ACTIVE-TASK-STAGE-LEDGER-V0_7"


class ThreadingServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


JOB_LOCK = threading.RLock()
JOBS: dict[str, dict] = {}
MAX_LOG_CHARS = 16000
DATA_ATLAS_CACHE: dict[str, object] = {"repo": "", "ts": 0.0, "data": None}
DATA_ATLAS_CACHE_SEC = 600


def action(
    action_id: str,
    label: str,
    kind: str,
    handler: str,
    command: list[str] | None,
    cwd: str,
    timeout_sec: int,
    writes_allowed: bool,
    allowed_write_roots: list[str],
    safety: str,
    evidence_outputs: list[str],
) -> dict:
    return {
        "action_id": action_id,
        "label": label,
        "kind": kind,
        "handler": handler,
        "command": command,
        "cwd": cwd,
        "timeout_sec": timeout_sec,
        "writes_allowed": writes_allowed,
        "allowed_write_roots": allowed_write_roots,
        "safety": safety,
        "evidence_outputs": evidence_outputs,
        "arbitrary_shell": False,
    }


ACTION_DEFS = {
    item["action_id"]: item
    for item in [
        action("refresh_snapshot", "Refresh snapshot", "read", "snapshot", None, "REPO_ROOT", 20, False, [], "READ_ONLY", ["api_snapshot"]),
        action("create_warp", "Create WARP", "warp", "warp_manager:create", ["python", "warp_manager.py", "create"], "REPO_ROOT", 240, True, ["E:/IMPERIUM_WARPS", "E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "COPY_CONTOUR_NO_GIT_METADATA", ["warp_marker", "runtime_registry"]),
        action("start_work", "Start Work", "warp", "warp_manager:start-work", ["python", "warp_manager.py", "start-work"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "REQUIRES_ACTIVE_TASK_AND_WARP", ["stage_ledger", "administratum_receipts", "stage_gates", "inquisition_findings"]),
        action("export_task_template", "Download Task Form ZIP", "taskpack", "warp_manager:export-task-template", ["python", "warp_manager.py", "export-task-template"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/TASK_FORMS"], "LOCAL_HANDOFF_ONLY", ["taskpack_template_zip"]),
        action("register_taskpack_pc", "Register Taskpack on PC", "astronomicon", "astronomicon_taskpack_registration_skill", ["python", "astronomicon_taskpack_registration_skill_v0_1.py"], "REPO_ROOT", 180, True, ["E:/IMPERIUM_WARPS", "E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "ASTRONOMICON_ADMISSION_ALLOWLIST", ["admission_receipt", "runtime_active_task"]),
        action("validate_warp", "WARP Validation", "validation", "warp_manager:validate", ["python", "warp_manager.py", "validate"], "REPO_ROOT", 120, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "INQUISITION_READ_MOSTLY", ["inquisition_findings"]),
        action("stage_start_current", "Start next stage", "stage", "warp_manager:stage-start", ["python", "warp_manager.py", "stage-start"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "ADMINISTRATUM_STAGE_RECEIPT", ["stage_ledger", "administratum_receipt"]),
        action("stage_submit_evidence", "Mark stage evidence", "stage", "warp_manager:stage-evidence", ["python", "warp_manager.py", "stage-evidence"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "EVIDENCE_MARKER_ONLY", ["stage_ledger", "administratum_receipt"]),
        action("stage_run_gate", "Run stage gate", "stage", "warp_manager:stage-gate", ["python", "warp_manager.py", "stage-gate"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "ASTRONOMICON_STAGE_GATE", ["astronomicon_stage_gates", "stage_ledger"]),
        action("stage_close_stage", "Close current stage", "stage", "warp_manager:stage-close", ["python", "warp_manager.py", "stage-close"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "GATE_REQUIRED_STAGE_CLOSE", ["stage_ledger", "administratum_receipt"]),
        action("promotion_preview", "Promotion Preview", "promotion", "warp_manager:promotion-preview", ["python", "warp_manager.py", "promotion-preview"], "REPO_ROOT", 90, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "NO_COMMIT_NO_PUSH_PREVIEW", ["promotion_preview", "diff_stat", "dirty_classification"]),
        action("build_report_bundle", "Final Report Bundle", "administratum", "final_report_bundle_builder:build", ["python", "final_report_bundle_builder_v0_1.py", "build"], "REPO_ROOT", 180, True, ["E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "REPORT_OUTPUT_ONLY", ["final_report_bundle_zip", "final_report_manifest"]),
        action("mechanicus_register_tool", "Ensure action registry", "mechanicus", "mechanicus_tool_registry:ensure-defaults", ["python", "mechanicus_tool_registry_v0_1.py", "ensure-defaults"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_WARPS"], "TOOL_REGISTRY_ONLY", ["tool_registry"]),
        action("mechanicus_list_tools", "List Mechanicus tools", "mechanicus", "mechanicus_tool_registry:list", ["python", "mechanicus_tool_registry_v0_1.py", "list"], "REPO_ROOT", 60, False, [], "READ_ONLY", ["tool_registry_snapshot"]),
        action("run_playwright", "Run Playwright", "evidence", "playwright:test", ["playwright", "test"], "WEB_SANCTUM", 300, True, ["E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS", "E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "EVIDENCE_OUTPUT_ONLY", ["playwright_results", "html_report"]),
        action("run_playwright_screenshots", "Collect screenshots", "evidence", "playwright:screenshots", ["playwright", "test", "web_sanctum_screenshots.spec.ts"], "WEB_SANCTUM", 300, True, ["E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS", "E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "EVIDENCE_OUTPUT_ONLY", ["owner_visible_screenshots"]),
        action("visual_inquisition_audit_light", "Visual Inquisition Light", "evidence", "playwright:visual-inquisition-light", ["node", "sanctum_visual_inquisition_audit_v0_1.cjs", "--profile", "light", "--safe-actions"], "WEB_SANCTUM", 600, True, ["E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS", "E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "EVIDENCE_OUTPUT_ONLY_NO_SOURCE_SPRAWL", ["visual_audit_bundle", "csv_maps", "jpeg_screenshots", "owner_report"]),
        action("visual_inquisition_audit_balanced", "Visual Inquisition Mega Audit", "evidence", "playwright:visual-inquisition-balanced", ["node", "sanctum_visual_inquisition_audit_v0_1.cjs", "--profile", "balanced", "--safe-actions"], "WEB_SANCTUM", 900, True, ["E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS", "E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "EVIDENCE_OUTPUT_ONLY_NO_SOURCE_SPRAWL", ["visual_audit_bundle", "csv_maps", "key_png", "bulk_jpeg", "owner_report"]),
        action("visual_inquisition_audit_balanced_headed", "Visual Inquisition Headed", "evidence", "playwright:visual-inquisition-headed", ["node", "sanctum_visual_inquisition_audit_v0_1.cjs", "--profile", "balanced", "--safe-actions", "--headed"], "WEB_SANCTUM", 900, True, ["E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS", "E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "EVIDENCE_OUTPUT_ONLY_NO_SOURCE_SPRAWL", ["visual_audit_bundle", "browser_window", "owner_report"]),
        action("visual_inquisition_audit_full", "Visual Inquisition Full", "evidence", "playwright:visual-inquisition-full", ["node", "sanctum_visual_inquisition_audit_v0_1.cjs", "--profile", "full", "--safe-actions"], "WEB_SANCTUM", 1200, True, ["E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS", "E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "EVIDENCE_OUTPUT_ONLY_NO_SOURCE_SPRAWL", ["visual_audit_bundle", "full_capture", "csv_maps", "owner_report"]),
        action("open_warp", "Open WARP folder", "open", "explorer", ["explorer", "{warp_path}"], "WARP_ROOT", 20, False, [], "EXPLORER_ONLY", ["operator_visible_folder"]),
        action("open_reports", "Open reports", "open", "explorer", ["explorer", "{output_root}"], "OUTPUT_ROOT", 20, False, [], "EXPLORER_ONLY", ["operator_visible_folder"]),
        action("open_playwright_report", "Open Playwright report", "open", "playwright:show-report", ["playwright", "show-report"], "WEB_SANCTUM", 20, False, [], "LOCAL_REPORT_ONLY", ["html_report"]),
        action("open_visual_audit_outputs", "Open Visual Audit outputs", "open", "explorer:visual-inquisition-outputs", ["explorer", "{latest_visual_audit_output}"], "OUTPUT_ROOT", 20, False, [], "EXPLORER_ONLY", ["operator_visible_folder"]),
        action("open_tui", "Open TUI", "open", "imperial_tui", ["python", "imperial_tui.py"], "REPO_ROOT", 20, False, [], "DETACHED_LOCAL_TOOL", ["operator_visible_process"]),
        action("open_tk", "Open Tk fallback", "open", "imperial_launcher", ["python", "imperial_launcher.py"], "REPO_ROOT", 20, False, [], "DETACHED_LOCAL_TOOL", ["operator_visible_process"]),
        action("runtime_hygiene_scan", "Runtime Hygiene Scan", "administratum", "runtime_hygiene:scan", ["python", "imperium_runtime_hygiene_v0_1.py", "scan"], "REPO_ROOT", 90, False, [], "SCAN_ONLY_NO_DELETE", ["runtime_hygiene_report"]),
        action("data_atlas_scan", "Data Atlas Scan", "administratum", "data_atlas:scan", ["python", "data_atlas_scanner_v0_1.py"], "REPO_ROOT", 120, False, [], "READ_ONLY_CARTOGRAPHY_NO_DELETE_NO_MOVE", ["data_atlas_snapshot"]),
        action("node_probe", "Probe This Node", "strategium", "resource_fleet:node-probe", ["python", "imperium_node_probe_v0_1.py"], "REPO_ROOT", 60, False, [], "READ_ONLY_NODE_DIAGNOSTIC", ["node_probe_report"]),
    ]
}


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def trim(text: str, limit: int = MAX_LOG_CHARS) -> str:
    return text if len(text) <= limit else text[-limit:]


def git(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def run_cmd(cmd, cwd: Path, timeout: int = 120, env: dict | None = None) -> dict:
    started = time.time()
    try:
        process = subprocess.run(
            cmd,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            shell=False,
            env=env,
        )
        return {
            "status": "PASS" if process.returncode == 0 else "FAIL",
            "cmd": cmd,
            "cwd": str(cwd),
            "returncode": process.returncode,
            "duration_sec": round(time.time() - started, 2),
            "stdout": trim(process.stdout),
            "stderr": trim(process.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "TIMEOUT",
            "cmd": cmd,
            "cwd": str(cwd),
            "timeout": timeout,
            "duration_sec": round(time.time() - started, 2),
            "stdout": trim((exc.stdout or "") if isinstance(exc.stdout, str) else ""),
            "stderr": trim((exc.stderr or "") if isinstance(exc.stderr, str) else ""),
        }
    except Exception as exc:
        return {"status": "FAIL", "cmd": cmd, "cwd": str(cwd), "error": repr(exc)}


def launch_detached(cmd, cwd: Path) -> dict:
    try:
        flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0) if os.name == "nt" else 0
        subprocess.Popen(cmd, cwd=str(cwd), shell=False, creationflags=flags)
        return {"status": "PASS", "mode": "DETACHED", "cmd": cmd, "cwd": str(cwd)}
    except Exception as exc:
        return {"status": "FAIL", "mode": "DETACHED", "cmd": cmd, "cwd": str(cwd), "error": repr(exc)}


def find_repo_root(start) -> Path:
    path = Path(start).resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "ORGANS").exists():
            return candidate
    return path


def parse_json_from_stdout(stdout: str):
    try:
        return json.loads(stdout)
    except Exception:
        start = stdout.find("{")
        end = stdout.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(stdout[start : end + 1])
            except Exception:
                return None
    return None


def read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def compact_data_atlas_payload(data: dict, include_lanes: bool = True) -> dict:
    """Return a browser/job-safe Data Atlas digest without thousands of entities.

    The full atlas remains available only through /api/data-atlas. Job lists and
    /api/snapshot must stay small or the Sanctum navigation freezes while the
    browser parses huge JSON payloads every few seconds.
    """
    if not isinstance(data, dict):
        return {"status": "FAIL", "reason": "DATA_ATLAS_PAYLOAD_NOT_DICT"}
    keys = {
        "status",
        "surface",
        "version",
        "generated_at_utc",
        "repo_root",
        "branch",
        "head",
        "doctrine",
        "summary",
        "by_organ",
        "by_type",
        "by_health",
        "by_lifecycle",
        "by_cleanup_lane",
    }
    out = {key: data.get(key) for key in keys if key in data}
    if "entities" in data:
        out["entities_total_raw"] = len(data.get("entities") or [])
    if "entities_returned" in data:
        out["entities_returned"] = data.get("entities_returned")
    if "dirty_priority" in data:
        out["dirty_priority_sample"] = (data.get("dirty_priority") or [])[:8]
    if include_lanes and isinstance(data.get("cleanup_lanes"), dict):
        lanes = {}
        for lane, info in data.get("cleanup_lanes", {}).items():
            if not isinstance(info, dict):
                lanes[lane] = info
                continue
            lanes[lane] = {
                key: value
                for key, value in info.items()
                if key not in {"sample", "entities", "files"}
            }
            if "sample" in info:
                lanes[lane]["sample"] = (info.get("sample") or [])[:3]
        out["cleanup_lanes"] = lanes
    return out


def compact_result_for_ui(result, action: str | None = None) -> dict:
    """Bound job payload size for /api/jobs and /api/jobs/<id>."""
    if not isinstance(result, dict):
        return {"status": "PASS", "value": str(result)[:2000]}
    if action == "data_atlas_scan" or "entities" in result or "dirty_priority" in result or result.get("surface", "").startswith("ADMINISTRATUM_DATA_ATLAS"):
        return compact_data_atlas_payload(result)
    safe = dict(result)
    execution = safe.get("execution")
    if isinstance(execution, dict):
        execution = dict(execution)
        for key in ["stdout", "stderr"]:
            if isinstance(execution.get(key), str) and len(execution[key]) > 6000:
                execution[key] = trim(execution[key], 6000)
        safe["execution"] = execution
    for key in ["stdout", "stderr", "raw", "trace"]:
        if isinstance(safe.get(key), str) and len(safe[key]) > 6000:
            safe[key] = trim(safe[key], 6000)
    return safe


def data_atlas_cached_light(repo: Path) -> dict:
    repo = Path(repo).resolve()
    cached_repo = str(DATA_ATLAS_CACHE.get("repo") or "")
    cached_data = DATA_ATLAS_CACHE.get("data")
    if cached_repo == str(repo) and isinstance(cached_data, dict):
        return compact_data_atlas_payload(cached_data)
    return {
        "status": "NOT_LOADED",
        "surface": "ADMINISTRATUM_DATA_ATLAS_CARTOGRAPHIUM",
        "version": "cached-light",
        "summary": {},
        "doctrine": {
            "ru": "Atlas загружается по требованию, чтобы навигация Sanctum оставалась мгновенной.",
            "en": "Atlas is loaded on demand so Sanctum navigation stays instant.",
        },
    }


def run_json_tool(cmd, cwd: Path, timeout: int = 120, env: dict | None = None) -> dict:
    execution = run_cmd(cmd, cwd, timeout=timeout, env=env)
    payload = parse_json_from_stdout(execution.get("stdout", ""))
    if not isinstance(payload, dict):
        return execution
    payload["execution"] = {
        "returncode": execution.get("returncode"),
        "duration_sec": execution.get("duration_sec"),
        "cwd": execution.get("cwd"),
        "stderr": execution.get("stderr", ""),
    }
    return payload


def warp_script(repo: Path) -> Path:
    return repo / "ORGANS" / "IMPERIAL_IDE" / "WARP" / "warp_manager.py"


def warp_tool(repo: Path, *args: str) -> dict:
    return run_json_tool([sys.executable, str(warp_script(repo)), "--repo-root", str(repo), *args], repo, timeout=240)


def output_root(repo: Path) -> Path:
    configured = os.environ.get("IMPERIUM_SERVITOR_OUTPUT_ROOT")
    if configured:
        return Path(configured).resolve()
    return Path(repo.anchor) / "IMPERIUM_LOCAL_HANDOFF" / "SERVITOR_OUTPUTS" / TASK_ID


def playwright_env(repo: Path) -> dict:
    env = os.environ.copy()
    env["IMPERIUM_PLAYWRIGHT_OUTPUT_ROOT"] = str(output_root(repo) / "playwright")
    dependency_root = os.environ.get("IMPERIUM_PLAYWRIGHT_NODE_MODULES")
    if not dependency_root:
        marker = read_json(repo / ".imperium_warp.json", {})
        main_source = marker.get("main_source")
        candidates = []
        if main_source:
            candidates.append(Path(str(main_source) + "_H") / "ORGANS" / "IMPERIAL_IDE" / "WEB_SANCTUM" / "node_modules")
        candidates.append(repo / "ORGANS" / "IMPERIAL_IDE" / "WEB_SANCTUM" / "node_modules")
        for candidate in candidates:
            if candidate.exists():
                dependency_root = str(candidate)
                break
    if dependency_root:
        env["NODE_PATH"] = dependency_root
        env["PATH"] = str(Path(dependency_root) / ".bin") + os.pathsep + env.get("PATH", "")
    return env


def report_tool(repo: Path, *args: str) -> dict:
    script = repo / "ORGANS" / "ADMINISTRATUM" / "REPORTS" / "final_report_bundle_builder_v0_1.py"
    return run_json_tool(
        [sys.executable, str(script), "--repo-root", str(repo), "--out-dir", str(output_root(repo) / "runtime_report"), *args],
        repo,
        timeout=180,
    )


def mech_tool(repo: Path, *args: str) -> dict:
    script = repo / "ORGANS" / "MECHANICUS" / "TOOL_REGISTRY" / "mechanicus_tool_registry_v0_1.py"
    return run_json_tool([sys.executable, str(script), "--repo-root", str(repo), *args], repo, timeout=120)


def hygiene_tool(repo: Path, *args: str) -> dict:
    script = repo / "ORGANS" / "ADMINISTRATUM" / "RUNTIME_HYGIENE" / "imperium_runtime_hygiene_v0_1.py"
    return run_json_tool([sys.executable, str(script), "--repo-root", str(repo), *args], repo, timeout=120)


def node_probe_tool(repo: Path) -> dict:
    script = repo / "ORGANS" / "STRATEGIUM" / "RESOURCE_FLEET" / "imperium_node_probe_v0_1.py"
    return run_json_tool([sys.executable, str(script), "--repo-root", str(repo)], repo, timeout=60)


def visual_audit_output_root(repo: Path) -> Path:
    configured = os.environ.get("VISUAL_INQUISITION_OUTPUT_ROOT") or os.environ.get("IMPERIUM_VISUAL_AUDIT_OUTPUT_ROOT")
    if configured:
        return Path(configured).resolve()
    preferred = Path(repo.anchor) / "_LOCAL_HANDOFF" / "SERVITOR_OUTPUTS"
    return preferred


def latest_visual_audit_output(repo: Path) -> Path | None:
    root = visual_audit_output_root(repo)
    if not root.exists():
        return None
    candidates = [p for p in root.glob("MEGA_PLAYWRIGHT_AUDIT_*") if p.is_dir()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def visual_inquisition_tool(repo: Path, profile: str = "balanced", headed: bool = False) -> dict:
    sanctum = repo / "ORGANS" / "IMPERIAL_IDE" / "WEB_SANCTUM"
    runner = sanctum / "tools" / "sanctum_visual_inquisition_audit_v0_1.cjs"
    if not runner.exists():
        return {"status": "FAIL", "reason": "VISUAL_INQUISITION_RUNNER_NOT_FOUND", "runner": str(runner)}
    env = playwright_env(repo)
    env["SANCTUM_BASE_URL"] = env.get("SANCTUM_BASE_URL", "http://127.0.0.1:8792")
    env["AUDIT_PROFILE"] = profile
    env["VISUAL_INQUISITION_OUT"] = ""
    env["LOCAL_HANDOFF"] = str(Path(repo.anchor) / "_LOCAL_HANDOFF")
    args = ["node", str(runner), "--profile", profile, "--safe-actions"]
    if headed:
        args.append("--headed")
    timeout = 1200 if profile == "full" else 900 if profile == "balanced" else 600
    return run_json_tool(args, sanctum, timeout=timeout, env=env)


def data_atlas_tool(repo: Path, *args: str) -> dict:
    script = repo / "ORGANS" / "ADMINISTRATUM" / "DATA_ATLAS" / "data_atlas_scanner_v0_1.py"
    if not script.exists():
        return {"status": "FAIL", "reason": "DATA_ATLAS_SCANNER_NOT_FOUND", "script": str(script)}
    started = time.time()
    cmd = [sys.executable, str(script), "--repo-root", str(repo), *args]
    try:
        process = subprocess.run(cmd, cwd=str(repo), text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=120, shell=False)
        payload = parse_json_from_stdout(process.stdout)
        if not isinstance(payload, dict):
            return {
                "status": "FAIL" if process.returncode else "PASS",
                "reason": "DATA_ATLAS_JSON_PARSE_FAILED",
                "cmd": cmd,
                "returncode": process.returncode,
                "duration_sec": round(time.time() - started, 2),
                "stdout_tail": trim(process.stdout),
                "stderr": trim(process.stderr),
            }
        payload["execution"] = {
            "returncode": process.returncode,
            "duration_sec": round(time.time() - started, 2),
            "cwd": str(repo),
            "stderr": trim(process.stderr),
        }
        return payload
    except subprocess.TimeoutExpired as exc:
        return {"status": "TIMEOUT", "reason": "DATA_ATLAS_SCAN_TIMEOUT", "duration_sec": round(time.time() - started, 2), "stderr": trim((exc.stderr or "") if isinstance(exc.stderr, str) else "")}
    except Exception as exc:
        return {"status": "FAIL", "reason": "DATA_ATLAS_SCAN_EXCEPTION", "error": repr(exc)}


def data_atlas_snapshot(repo: Path, force: bool = False) -> dict:
    repo = Path(repo).resolve()
    now = time.time()
    cached_repo = str(DATA_ATLAS_CACHE.get("repo") or "")
    cached_ts = float(DATA_ATLAS_CACHE.get("ts") or 0)
    cached_data = DATA_ATLAS_CACHE.get("data")
    if not force and cached_repo == str(repo) and isinstance(cached_data, dict) and now - cached_ts < DATA_ATLAS_CACHE_SEC:
        return cached_data
    data = data_atlas_tool(repo, "--ui-limit", "15000")
    if not isinstance(data, dict):
        data = {"status": "FAIL", "reason": "DATA_ATLAS_SCAN_FAILED"}
    DATA_ATLAS_CACHE.update({"repo": str(repo), "ts": now, "data": data})
    return data


def snapshot(repo) -> dict:
    repo = Path(repo).resolve()
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    head = git(repo, "rev-parse", "HEAD") or "unknown"
    dirty_lines = [line for line in git(repo, "status", "--short").splitlines() if line.strip()]
    runtime = warp_tool(repo, "status")
    warp = runtime.get("registry") or {"mode": "NO_WARP_SELECTED", "path": "", "active_task_required": True, "stage_progress": {"done": 0, "total": 6}}
    task = runtime.get("active_task") or {"id": "NO_ACTIVE_TASK", "status": "WAITING_FOR_ASTRONOMICON_TASKPACK", "next_action": "Register a taskpack, then start work."}
    ledger = runtime.get("stage_ledger") or {}
    warp["current_stage"] = ledger.get("current_stage") or warp.get("current_stage", "task_intake")
    warp["dirty_status"] = "DIRTY" if dirty_lines else "CLEAN"
    warp["dirty_count"] = len(dirty_lines)
    warp["dirty_preview"] = dirty_lines[:20]
    is_warp = bool((repo / ".imperium_warp.json").exists()) or str(repo).upper().startswith("E:\\IMPERIUM_WARPS")
    return {
        "status": "PASS_WITH_WARNINGS" if dirty_lines else "PASS",
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": now_utc(),
        "contour": {
            "current_contour": "WARP_CONTOUR" if is_warp else "H_CONTOUR" if str(repo).endswith("_H") or branch.startswith("h/") else "MAIN_OR_UNKNOWN",
            "repo_root": str(repo).replace("\\", "/"),
            "branch": branch,
            "head": head,
            "dirty_count": len(dirty_lines),
        },
        "task": task,
        "warp": warp,
        "stage_ledger": ledger,
        "runtime_paths": runtime.get("runtime_paths", {}),
        "departments": ["FREELANCE", "TRADING"],
        "organs": ["DOCTRINARIUM", "OFFICIO_AGENTIS", "ASTRONOMICON", "ADMINISTRATUM", "MECHANICUS", "INQUISITION", "STRATEGIUM", "SCHOLA_IMPERIALIS"],
        "jobs": list_jobs(repo, limit=8),
        # Do not scan the 10k+ file Data Atlas inside /api/snapshot.
        # Snapshot is polled often and must remain lightweight for instant navigation.
        "data_atlas": data_atlas_cached_light(repo),
        "actions": ACTION_DEFS,
        "safety": {
            "real_execution_enabled": False,
            "live_llm_backend_enabled": False,
            "unsafe_shell_enabled": False,
            "trading_execution_enabled": False,
            "commit_push_exposed": False,
        },
    }


def action_callable(repo: Path, action_id: str, request: dict):
    if action_id == "refresh_snapshot":
        return lambda: {"status": "PASS", "snapshot": snapshot(repo)}
    if action_id == "create_warp":
        return lambda: warp_tool(repo, "create")
    if action_id == "start_work":
        return lambda: warp_tool(repo, "start-work")
    if action_id == "export_task_template":
        return lambda: warp_tool(repo, "export-task-template")
    if action_id == "validate_warp":
        return lambda: warp_tool(repo, "validate")
    if action_id == "stage_start_current":
        return lambda: warp_tool(repo, "stage-start")
    if action_id == "stage_submit_evidence":
        return lambda: warp_tool(repo, "stage-evidence", "--note", "Operator marked stage evidence from Web Sanctum.")
    if action_id == "stage_run_gate":
        return lambda: warp_tool(repo, "stage-gate")
    if action_id == "stage_close_stage":
        return lambda: warp_tool(repo, "stage-close")
    if action_id == "promotion_preview":
        return lambda: warp_tool(repo, "promotion-preview")
    if action_id == "build_report_bundle":
        return lambda: report_tool(repo, "build")
    if action_id == "mechanicus_register_tool":
        return lambda: mech_tool(repo, "ensure-defaults")
    if action_id == "mechanicus_list_tools":
        return lambda: mech_tool(repo, "list")
    if action_id == "runtime_hygiene_scan":
        return lambda: hygiene_tool(repo, "scan")
    if action_id == "data_atlas_scan":
        return lambda: data_atlas_snapshot(repo, force=True)
    if action_id == "node_probe":
        return lambda: node_probe_tool(repo)
    if action_id in {"run_playwright", "run_playwright_screenshots"}:
        sanctum = repo / "ORGANS" / "IMPERIAL_IDE" / "WEB_SANCTUM"
        script = "test:pw" if action_id == "run_playwright" else "test:pw:screenshots"
        return lambda: run_cmd(["npm", "run", script], sanctum, timeout=300, env=playwright_env(repo))
    if action_id == "visual_inquisition_audit_light":
        return lambda: visual_inquisition_tool(repo, "light", headed=False)
    if action_id == "visual_inquisition_audit_balanced":
        return lambda: visual_inquisition_tool(repo, "balanced", headed=False)
    if action_id == "visual_inquisition_audit_balanced_headed":
        return lambda: visual_inquisition_tool(repo, "balanced", headed=True)
    if action_id == "visual_inquisition_audit_full":
        return lambda: visual_inquisition_tool(repo, "full", headed=False)
    if action_id == "open_visual_audit_outputs":
        latest = latest_visual_audit_output(repo)
        return lambda: launch_detached(["explorer", str(latest)], repo) if latest else {"status": "BLOCKED", "reason": "NO_VISUAL_AUDIT_OUTPUTS_FOUND", "root": str(visual_audit_output_root(repo))}
    if action_id == "open_warp":
        warp_path = snapshot(repo).get("warp", {}).get("path")
        return lambda: launch_detached(["explorer", str(warp_path)], repo) if warp_path else {"status": "BLOCKED", "reason": "NO_WARP_SELECTED"}
    if action_id == "open_reports":
        return lambda: launch_detached(["explorer", str(output_root(repo))], repo)
    if action_id == "open_playwright_report":
        report_path = output_root(repo) / "playwright" / "report"
        return lambda: launch_detached(["explorer", str(report_path)], repo)
    if action_id == "open_tui":
        return lambda: launch_detached([sys.executable, str(repo / "ORGANS" / "IMPERIAL_IDE" / "WORKBENCH" / "TUI" / "imperial_tui.py")], repo)
    if action_id == "open_tk":
        return lambda: launch_detached([sys.executable, str(repo / "ORGANS" / "IMPERIAL_IDE" / "LAUNCHER" / "imperial_launcher.py")], repo)
    if action_id == "register_taskpack_pc":
        zip_path = str(request.get("zip_path", "")).strip()

        def register_taskpack() -> dict:
            if not zip_path or not zip_path.lower().endswith(".zip"):
                return {"status": "BLOCKED", "reason": "TASKPACK_ZIP_REQUIRED", "message": "Provide a .zip taskpack path."}
            if not Path(zip_path).is_file():
                return {"status": "BLOCKED", "reason": "TASKPACK_ZIP_NOT_FOUND", "message": "Taskpack ZIP path does not exist.", "zip_path": zip_path}
            skill = repo / "ORGANS" / "ASTRONOMICON" / "SKILLS" / "TASKPACK_REGISTRATION_SKILL" / "astronomicon_taskpack_registration_skill_v0_1.py"
            execution = run_json_tool([sys.executable, str(skill), "--zip-path", zip_path, "--contour", "PC"], repo, timeout=180)
            receipt = execution if isinstance(execution, dict) else {}
            verdict = receipt.get("verdict") or receipt.get("status")
            task_id = receipt.get("task_id", "")
            registered_path = receipt.get("registered_task_path") or receipt.get("registered_path", "")
            warnings = receipt.get("warnings") or []
            caps = receipt.get("caps") or receipt.get("capabilities") or {}
            receipt_path = receipt.get("receipt_path") or receipt.get("admission_receipt_path", "")
            activation = None
            if verdict in {"PASS", "PASS_WITH_WARNINGS"} and task_id:
                activation_args = [
                    "activate-task",
                    "--task-id",
                    str(task_id),
                    "--registered-path",
                    str(registered_path),
                    "--admission-verdict",
                    str(verdict),
                    "--caps",
                    json.dumps(caps, ensure_ascii=True),
                    "--receipt-path",
                    str(receipt_path),
                ]
                for warning in warnings:
                    activation_args.extend(["--warnings", str(warning)])
                activation = warp_tool(repo, *activation_args)
            return {
                "status": "PASS" if activation and activation.get("status") == "PASS" else verdict or execution.get("status", "FAIL"),
                "verdict": verdict,
                "task_id": task_id,
                "registered_path": registered_path,
                "caps": caps,
                "warnings": warnings,
                "receipt": receipt,
                "activation": activation,
            }

        return register_taskpack
    return None


def persisted_jobs_path(repo: Path) -> Path | None:
    runtime = warp_tool(repo, "status")
    run_path = runtime.get("runtime_paths", {}).get("run_dir")
    if not run_path:
        return None
    return Path(run_path) / "jobs.jsonl"


def persist_job(repo: Path, data: dict) -> None:
    path = persisted_jobs_path(repo)
    if not path:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(data, ensure_ascii=True) + "\n")


def read_persisted_jobs(repo: Path, limit: int = 20) -> list[dict]:
    path = persisted_jobs_path(repo)
    if not path or not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            items.append(json.loads(line))
        except Exception:
            continue
    return items[-limit:]


def new_job(repo: Path, action_id: str, request: dict, fn) -> dict:
    job_id = f"JOB-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    data = {
        "job_id": job_id,
        "action": action_id,
        "status": "RUNNING",
        "created_at_utc": now_utc(),
        "updated_at_utc": now_utc(),
        "request": {key: value for key, value in request.items() if key != "secret"},
        "result": None,
        "evidence_outputs": ACTION_DEFS[action_id]["evidence_outputs"],
    }
    with JOB_LOCK:
        JOBS[job_id] = data

    def run() -> None:
        try:
            result = fn()
            status = result.get("status", "PASS") if isinstance(result, dict) else "PASS"
        except Exception as exc:
            result = {"status": "FAIL", "error": repr(exc)}
            status = "FAIL"
        stored_result = compact_result_for_ui(result, action_id)
        with JOB_LOCK:
            JOBS[job_id]["status"] = status
            JOBS[job_id]["updated_at_utc"] = now_utc()
            JOBS[job_id]["result"] = stored_result
            completed = dict(JOBS[job_id])
        persist_job(repo, completed)

    threading.Thread(target=run, daemon=True).start()
    return {"status": "PASS", "surface": SURFACE, "job_id": job_id, "action": action_id, "message": "Job accepted by the allowlisted Web Sanctum runner."}


def list_jobs(repo: Path, limit=20):
    with JOB_LOCK:
        values = list(JOBS.values())[-limit:]
    if not values:
        values = read_persisted_jobs(repo, limit=limit)
    return [
        {
            "job_id": item["job_id"],
            "action": item["action"],
            "status": item["status"],
            "created_at_utc": item["created_at_utc"],
            "updated_at_utc": item["updated_at_utc"],
            "summary": (compact_result_for_ui(item.get("result") or {}, item.get("action")).get("reason") or compact_result_for_ui(item.get("result") or {}, item.get("action")).get("verdict") or compact_result_for_ui(item.get("result") or {}, item.get("action")).get("message") or compact_result_for_ui(item.get("result") or {}, item.get("action")).get("status") or ""),
            "result": compact_result_for_ui(item.get("result") or {}, item.get("action")),
        }
        for item in reversed(values)
    ]


def get_job(repo: Path, job_id: str):
    with JOB_LOCK:
        if job_id in JOBS:
            return JOBS.get(job_id)
    for item in reversed(read_persisted_jobs(repo, limit=200)):
        if item.get("job_id") == job_id:
            return item
    return None


class Handler(SimpleHTTPRequestHandler):
    repo_root: Path = None
    actions: bool = False

    def end_json(self, data, status=200):
        raw = json.dumps(data, indent=2).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("content-type", "application/json; charset=utf-8")
            self.send_header("cache-control", "no-store")
            self.send_header("content-length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            # Playwright/browser polling can close /api/jobs while the bridge is writing.
            # This is normal client disconnect noise, not an Imperium action failure.
            return

    def end_headers(self):
        self.send_header("cache-control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("pragma", "no-cache")
        self.send_header("expires", "0")
        super().end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self.end_json({"status": "PASS", "surface": SURFACE, "version": VERSION, "actions_enabled": self.actions, "repo_root": str(self.repo_root), "job_runner": True})
        elif path == "/api/snapshot":
            self.end_json(snapshot(self.repo_root))
        elif path == "/api/actions":
            self.end_json({"status": "PASS", "actions": ACTION_DEFS})
        elif path == "/api/data-atlas":
            query = urlparse(self.path).query
            self.end_json(data_atlas_snapshot(Path(self.repo_root), force="force=1" in query))
        elif path == "/api/jobs":
            self.end_json({"status": "PASS", "jobs": list_jobs(Path(self.repo_root))})
        elif path.startswith("/api/jobs/"):
            job_id = path.rsplit("/", 1)[-1]
            job = get_job(Path(self.repo_root), job_id)
            if job:
                job = dict(job)
                job["result"] = compact_result_for_ui(job.get("result") or {}, job.get("action"))
            self.end_json(job if job else {"status": "FAIL", "error": "job not found", "job_id": job_id}, 200 if job else 404)
        else:
            return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/action":
            self.end_json({"status": "FAIL", "error": "unknown endpoint"}, 404)
            return
        length = int(self.headers.get("content-length", "0") or 0)
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length else "{}"
        try:
            request = json.loads(body)
        except Exception:
            request = {}
        action_id = request.get("action") or request.get("action_id") or ""
        if not self.actions:
            self.end_json({"status": "BLOCKED", "message": "Actions disabled; read-only bridge is active.", "action": action_id, "actions_enabled": False})
            return
        if action_id not in ACTION_DEFS:
            self.end_json({"status": "BLOCKED", "message": "Action not allowlisted", "action": action_id}, 403)
            return
        fn = action_callable(Path(self.repo_root), action_id, request)
        if fn is None:
            self.end_json({"status": "BLOCKED", "message": "Action not implemented", "action": action_id}, 403)
            return
        self.end_json(new_job(Path(self.repo_root), action_id, request, fn))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="../../..")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8792)
    parser.add_argument("--actions", action="store_true")
    args = parser.parse_args()
    repo = find_repo_root(args.repo_root)
    app_dir = Path(__file__).resolve().parents[1] / "app"
    Handler.repo_root = repo
    Handler.actions = args.actions
    os.chdir(app_dir)
    print(f"WEB SANCTUM {SURFACE} serving {app_dir}")
    print(f"repo: {repo}")
    print(f"actions: {'ENABLED allowlisted only + job runner' if args.actions else 'DISABLED read-only'}")
    print(f"http://{args.host}:{args.port}/")
    with ThreadingServer((args.host, args.port), Handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
