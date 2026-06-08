#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
text = lambda rel: (root / rel).read_text(encoding="utf-8")

main_js = text("app/main.js")
bridge = text("tools/local_bridge.py")
html = text("app/index.html")
styles = text("app/styles.css")
package = text("package.json")
manager = (root.parents[0] / "WARP" / "warp_manager.py").read_text(encoding="utf-8")
mechanicus = (root.parents[1] / "MECHANICUS" / "TOOL_REGISTRY" / "mechanicus_tool_registry_v0_1.py").read_text(encoding="utf-8")

checks = {
    "package_v081": "imperium-web-sanctum-v081" in package and "0.8.1" in package,
    "surface_v081": "WEB_SANCTUM_STAGE_LOOP_POLISH_AND_COPY_CONTOUR_V0_8_1" in main_js and "WEB_SANCTUM_STAGE_LOOP_POLISH_AND_COPY_CONTOUR_V0_8_1" in bridge,
    "runtime_registry_outside_source": "WARP_RUNS" in manager and "legacy_registry_path" in manager and "write_json(legacy_registry_path" not in manager,
    "stage_ledger_required_files": all(name in manager for name in ["stage_ledger.json", "administratum_receipts.jsonl", "astronomicon_stage_gates.json", "inquisition_findings.json"]),
    "structured_start_work_block": "NO_ACTIVE_ASTRONOMICON_TASKPACK" in manager and "NO_WARP_SELECTED" in manager,
    "warp_vitals_present": all(token in html for token in ["data-testid=\"warp-id\"", "data-testid=\"warp-path\"", "data-testid=\"warp-base\"", "data-testid=\"warp-current-stage\"", "data-testid=\"copy-warp-path\""]),
    "admission_summary_present": all(token in html for token in ["admissionVerdict", "admissionTaskId", "admissionPath", "admissionWarnings", "registrationTrace"]),
    "compact_jobs_present": "job-card" in main_js and "Machine Chronicle" in html and "job-summary" in html,
    "mechanicus_full_metadata": all(token in mechanicus for token in ["action_id", "handler", "command", "cwd", "timeout_sec", "writes_allowed", "allowed_write_roots", "evidence_outputs"]),
    "inquisition_checks_present": all(token in manager for token in ["forbidden_generated_files_absent", "no_commit_since_warp_base", "diff_stat", "commit_push_performed", "COPY_CONTOUR_HEAD_UNAVAILABLE"]),
    "no_arbitrary_shell_endpoint": "shell=True" not in bridge and "data-action=\"commit" not in html.lower() and "data-action=\"push" not in html.lower(),
    "playwright_output_redirect": "IMPERIUM_PLAYWRIGHT_OUTPUT_ROOT" in text("playwright.config.ts"),
    "stage_control_page_present": "page-stage" in html and "Stage Control" in html,
    "promotion_preview_page_present": "page-promotion" in html and "Promotion Preview" in html,
    "stage_loop_actions_present": "stage_start_current" in bridge and "promotion_preview" in bridge,
    "warp_stage_cli_present": "stage-start" in manager and "promotion-preview" in manager,
    "visual_premium_layer": all(token in styles for token in ["cathedral", "embers", "vault-lines", "stage-rail", "job-card", "job-summary", "action-pulse", "buttonSweep"]),
    "runtime_hygiene_present": "runtime_hygiene_scan" in bridge and "imperium_runtime_hygiene_v0_1.py" in bridge and "Runtime Hygiene" in html,
    "node_probe_present": "node_probe" in bridge and "imperium_node_probe_v0_1.py" in bridge,
    "owner_visible_no_old_versions": all(token not in html and token not in main_js and token not in package for token in ["V0.6", "V0.7", "V0.8<", "0.6.0", "0.7.0", "0.8.0"]),
}

print(json.dumps({"status": "PASS" if all(checks.values()) else "FAIL", "surface": "WEB_SANCTUM_STAGE_LOOP_POLISH_AND_COPY_CONTOUR_V0_8_1", "checks": checks}, indent=2))
