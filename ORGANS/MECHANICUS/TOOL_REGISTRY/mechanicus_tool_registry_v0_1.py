#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

SURFACE = "MECHANICUS_ACTION_REGISTRY_V0_8_1"


def entry(action_id, handler, command, cwd, timeout_sec, writes_allowed, allowed_write_roots, safety, evidence_outputs):
    return {
        "id": action_id,
        "action_id": action_id,
        "handler": handler,
        "command": command,
        "cwd": cwd,
        "timeout_sec": timeout_sec,
        "writes_allowed": writes_allowed,
        "allowed_write_roots": allowed_write_roots,
        "safety": safety,
        "evidence_outputs": evidence_outputs,
        "arbitrary_shell": False,
        "commit_push_exposed": False,
        "source": SURFACE,
    }


DEFAULT_ACTIONS = [
    entry("refresh_snapshot", "snapshot", None, "REPO_ROOT", 20, False, [], "READ_ONLY", ["api_snapshot"]),
    entry("create_warp", "warp_manager:create", ["python", "warp_manager.py", "create"], "REPO_ROOT", 240, True, ["E:/IMPERIUM_WARPS", "E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "COPY_CONTOUR_NO_GIT_METADATA", ["warp_marker", "runtime_registry"]),
    entry("start_work", "warp_manager:start-work", ["python", "warp_manager.py", "start-work"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "REQUIRES_ACTIVE_TASK_AND_WARP", ["stage_ledger", "administratum_receipts", "stage_gates", "inquisition_findings"]),
    entry("export_task_template", "warp_manager:export-task-template", ["python", "warp_manager.py", "export-task-template"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/TASK_FORMS"], "LOCAL_HANDOFF_ONLY", ["taskpack_template_zip"]),
    entry("register_taskpack_pc", "astronomicon_taskpack_registration_skill", ["python", "astronomicon_taskpack_registration_skill_v0_1.py"], "REPO_ROOT", 180, True, ["E:/IMPERIUM_WARPS", "E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "ASTRONOMICON_ADMISSION_ALLOWLIST", ["admission_receipt", "runtime_active_task"]),
    entry("validate_warp", "warp_manager:validate", ["python", "warp_manager.py", "validate"], "REPO_ROOT", 120, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "INQUISITION_READ_MOSTLY", ["inquisition_findings"]),
    entry("build_report_bundle", "final_report_bundle_builder:build", ["python", "final_report_bundle_builder_v0_1.py", "build"], "REPO_ROOT", 180, True, ["E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "REPORT_OUTPUT_ONLY", ["final_report_bundle_zip", "final_report_manifest"]),
    entry("mechanicus_register_tool", "mechanicus_tool_registry:ensure-defaults", ["python", "mechanicus_tool_registry_v0_1.py", "ensure-defaults"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_WARPS"], "TOOL_REGISTRY_ONLY", ["tool_registry"]),
    entry("mechanicus_list_tools", "mechanicus_tool_registry:list", ["python", "mechanicus_tool_registry_v0_1.py", "list"], "REPO_ROOT", 60, False, [], "READ_ONLY", ["tool_registry_snapshot"]),
    entry("run_playwright", "playwright:test", ["playwright", "test"], "WEB_SANCTUM", 300, True, ["E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "EVIDENCE_OUTPUT_ONLY", ["playwright_results", "html_report"]),
    entry("run_playwright_screenshots", "playwright:screenshots", ["playwright", "test", "web_sanctum_screenshots.spec.ts"], "WEB_SANCTUM", 300, True, ["E:/IMPERIUM_LOCAL_HANDOFF/SERVITOR_OUTPUTS"], "EVIDENCE_OUTPUT_ONLY", ["owner_visible_screenshots"]),
    entry("open_warp", "explorer", ["explorer", "{warp_path}"], "WARP_ROOT", 20, False, [], "EXPLORER_ONLY", ["operator_visible_folder"]),
    entry("open_reports", "explorer", ["explorer", "{output_root}"], "OUTPUT_ROOT", 20, False, [], "EXPLORER_ONLY", ["operator_visible_folder"]),
    entry("open_playwright_report", "playwright:show-report", ["playwright", "show-report"], "WEB_SANCTUM", 20, False, [], "LOCAL_REPORT_ONLY", ["html_report"]),
    entry("open_tui", "imperial_tui", ["python", "imperial_tui.py"], "REPO_ROOT", 20, False, [], "DETACHED_LOCAL_TOOL", ["operator_visible_process"]),
    entry("open_tk", "imperial_launcher", ["python", "imperial_launcher.py"], "REPO_ROOT", 20, False, [], "DETACHED_LOCAL_TOOL", ["operator_visible_process"]),
    entry("stage_start_current", "warp_manager:stage-start", ["python", "warp_manager.py", "stage-start"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "ADMINISTRATUM_STAGE_RECEIPT", ["stage_ledger", "administratum_receipt"]),
    entry("stage_submit_evidence", "warp_manager:stage-evidence", ["python", "warp_manager.py", "stage-evidence"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "EVIDENCE_MARKER_ONLY", ["stage_ledger", "administratum_receipt"]),
    entry("stage_run_gate", "warp_manager:stage-gate", ["python", "warp_manager.py", "stage-gate"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "ASTRONOMICON_STAGE_GATE", ["astronomicon_stage_gates", "stage_ledger"]),
    entry("stage_close_stage", "warp_manager:stage-close", ["python", "warp_manager.py", "stage-close"], "REPO_ROOT", 60, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "GATE_REQUIRED_STAGE_CLOSE", ["stage_ledger", "administratum_receipt"]),
    entry("promotion_preview", "warp_manager:promotion-preview", ["python", "warp_manager.py", "promotion-preview"], "REPO_ROOT", 90, True, ["E:/IMPERIUM_LOCAL_HANDOFF/WARP_RUNS"], "NO_COMMIT_NO_PUSH_PREVIEW", ["promotion_preview", "diff_stat", "dirty_classification"]),
    entry("runtime_hygiene_scan", "runtime_hygiene:scan", ["python", "imperium_runtime_hygiene_v0_1.py", "scan"], "REPO_ROOT", 90, False, [], "SCAN_ONLY_NO_DELETE", ["runtime_hygiene_report"]),
    entry("node_probe", "resource_fleet:node-probe", ["python", "imperium_node_probe_v0_1.py"], "REPO_ROOT", 60, False, [], "READ_ONLY_NODE_DIAGNOSTIC", ["node_probe_report"]),

]


def registry_path(repo):
    return Path(repo) / "ORGANS" / "MECHANICUS" / "TOOL_REGISTRY" / "tool_registry.json"


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"tools": []}


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def ensure_defaults(data):
    existing = {item.get("action_id") or item.get("id"): item for item in data.get("tools", []) if isinstance(item, dict)}
    tools = []
    for default in DEFAULT_ACTIONS:
        current = existing.get(default["action_id"], {})
        merged = dict(default)
        merged["registered_at_utc"] = current.get("registered_at_utc") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        tools.append(merged)
    data.update(
        {
            "status": "PASS",
            "surface": SURFACE,
            "schema_version": "0.8.1",
            "updated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tools": tools,
        }
    )
    return data


def validate_registry(data):
    required = {"action_id", "handler", "command", "cwd", "timeout_sec", "writes_allowed", "allowed_write_roots", "safety", "evidence_outputs"}
    findings = []
    for item in data.get("tools", []):
        missing = sorted(required - set(item))
        if missing:
            findings.append({"action_id": item.get("action_id") or item.get("id"), "missing": missing})
        if item.get("arbitrary_shell") or item.get("commit_push_exposed"):
            findings.append({"action_id": item.get("action_id") or item.get("id"), "unsafe_exposure": True})
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("cmd", nargs="?", default="list")
    parser.add_argument("--tool-id", default="")
    args = parser.parse_args()
    path = registry_path(args.repo_root)
    data = load(path)
    if args.cmd in {"ensure-defaults", "register-sample"}:
        data = ensure_defaults(data)
        save(path, data)
    elif args.cmd == "validate":
        data = ensure_defaults(data)
        findings = validate_registry(data)
        selected = any(item.get("action_id") == args.tool_id for item in data.get("tools", [])) if args.tool_id else True
        print(json.dumps({"status": "PASS" if not findings and selected else "BLOCKED", "surface": SURFACE, "tool_id": args.tool_id, "found": selected, "findings": findings}, indent=2))
        return
    print(json.dumps({"status": "PASS", "surface": SURFACE, "registry": data, "findings": validate_registry(data)}, indent=2))


if __name__ == "__main__":
    main()
