#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict, List

TOOLCHAIN_REPORT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json")
LANE_READOUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_STRICT_LANGUAGE_LANE_READOUT_V0_1.json")
DEFAULT_OUT = Path("ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOL_INVENTORY_V0_1.json")

EXCLUDE_PARTS = {".git", "node_modules", "target", "dist", "build", "__pycache__", ".venv", "venv"}

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {"_load_error": str(e)}

def lane_for_path(rel: str) -> str:
    lower = rel.lower()
    if lower.endswith(".py"):
        return "python"
    if lower.endswith((".ps1", ".psm1", ".psd1")):
        return "powershell"
    if lower.endswith(".rs"):
        return "rust"
    if lower.endswith((".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx")):
        return "node_frontend"
    if lower.endswith((".css", ".scss")):
        return "css_ui"
    if lower.endswith((".json", ".jsonl")):
        return "json_evidence"
    if lower.endswith(".md"):
        return "markdown_docs"
    if lower.endswith(".toml"):
        return "toml_config"
    if lower.endswith(".go"):
        return "go_future"
    if lower.endswith((".cpp", ".cc", ".cxx", ".hpp", ".h", ".c")):
        return "cpp_future"
    return "unknown"

def kind_for_path(rel: str) -> str:
    r = rel.replace("\\", "/")
    name = Path(r).name
    if "/VALIDATORS/" in r or name.startswith("validate_"):
        return "validator"
    if "/TOOLS/" in r:
        return "tool"
    if name.startswith("RUN_") and name.endswith(".ps1"):
        return "warp_runner"
    if "/SUPPORT/APP_TAURI/" in r:
        return "app_runtime_component"
    if "/WARP/PATCHES/" in r:
        return "patch_payload"
    return "internal_file"

def provenance_for_path(rel: str) -> str:
    r = rel.replace("\\", "/")
    if "/WARP/PATCHES/" in r:
        return "warp_patch_candidate"
    return "repository_canonical"

def purpose_for_path(rel: str, kind: str) -> str:
    name = Path(rel).name
    if kind == "validator":
        return "validate Imperium evidence or implementation state"
    if kind == "tool":
        return "support Mechanicus/Imperium measurement, reporting or transformation"
    if kind == "warp_runner":
        return "execute WARP patch pack on Windows host"
    if kind == "app_runtime_component":
        return "support Tauri application runtime/operator surface"
    if kind == "patch_payload":
        return "candidate patch evidence/payload"
    return f"internal repository file: {name}"

def is_candidate_file(path: Path, repo: Path) -> bool:
    if not path.is_file():
        return False
    rel = path.relative_to(repo)
    if set(rel.parts) & EXCLUDE_PARTS:
        return False
    r = rel.as_posix()
    if "/REPORTS/" in r or "/RECEIPTS/" in r:
        return False
    if r.endswith((".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".part", ".mp4", ".mp3")):
        return False
    return any(seg in r for seg in ["/TOOLS/", "/VALIDATORS/", "/SUPPORT/APP_TAURI/", "/WARP/PATCHES/"]) or (Path(r).name.startswith("RUN_") and r.endswith(".ps1"))

def external_tools(repo: Path, toolchain: Dict[str, Any], generated: str) -> List[Dict[str, Any]]:
    out = []
    for result in toolchain.get("results", []) or []:
        name = result.get("name") or "unknown_external_tool"
        ok = bool(result.get("ok"))
        out.append({
            "tool_id": f"external::{name}",
            "tool_class": "external_tool",
            "name": name,
            "kind": "host_toolchain_probe",
            "path_or_command": result.get("which") or result.get("executable") or result.get("cmd") or name,
            "provenance": "installed_on_host",
            "owner_scope": "host_environment",
            "language_lane": "toolchain",
            "purpose": "external host capability discovered by Mechanicus toolchain probe",
            "admission_state": "ADMITTED_BASELINE" if ok else "REJECTED_REWORK_REQUIRED",
            "validation_evidence": {
                "source_report": TOOLCHAIN_REPORT.as_posix(),
                "ok": ok,
                "exit_code": result.get("exit_code"),
                "importance": result.get("importance")
            },
            "risks": [] if ok else ["missing_or_failed_external_toolchain_probe"],
            "last_seen_utc": generated
        })
    return out

def internal_tools(repo: Path, generated: str) -> List[Dict[str, Any]]:
    out = []
    for path in sorted(repo.rglob("*")):
        if not is_candidate_file(path, repo):
            continue
        rel = path.relative_to(repo).as_posix()
        kind = kind_for_path(rel)
        lane = lane_for_path(rel)
        provenance = provenance_for_path(rel)
        state = "CANDIDATE" if provenance == "warp_patch_candidate" else "ADMITTED_BASELINE"
        risks = []
        if lane == "unknown":
            risks.append("missing_language_lane")
            state = "REJECTED_REWORK_REQUIRED"
        if kind == "patch_payload":
            risks.append("patch_payload_not_canonical_tool_until_landed")
            state = "CANDIDATE"
        if path.stat().st_size == 0:
            risks.append("empty_file")
            state = "REJECTED_REWORK_REQUIRED"
        out.append({
            "tool_id": f"internal::{rel}",
            "tool_class": "internal_tool",
            "name": path.name,
            "kind": kind,
            "path_or_command": rel,
            "provenance": provenance,
            "owner_scope": "imperium_repository",
            "language_lane": lane,
            "purpose": purpose_for_path(rel, kind),
            "admission_state": state,
            "validation_evidence": {
                "file_exists": True,
                "size_bytes": path.stat().st_size,
                "baseline_state": "inventory_only_not_strict_validation"
            },
            "risks": risks,
            "last_seen_utc": generated
        })
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    generated = utc()

    toolchain = load_json(repo / TOOLCHAIN_REPORT)
    lane_readout = load_json(repo / LANE_READOUT)

    records = external_tools(repo, toolchain, generated) + internal_tools(repo, generated)
    counts_by_class: Dict[str, int] = {}
    counts_by_state: Dict[str, int] = {}
    counts_by_kind: Dict[str, int] = {}
    for rec in records:
        counts_by_class[rec["tool_class"]] = counts_by_class.get(rec["tool_class"], 0) + 1
        counts_by_state[rec["admission_state"]] = counts_by_state.get(rec["admission_state"], 0) + 1
        counts_by_kind[rec["kind"]] = counts_by_kind.get(rec["kind"], 0) + 1

    rejected = [r for r in records if r["admission_state"] == "REJECTED_REWORK_REQUIRED"]
    candidates = [r for r in records if r["admission_state"] == "CANDIDATE"]

    report = {
        "tool_id": "mechanicus_tool_inventory_scanner.v0_1",
        "generated_at_utc": generated,
        "repo_root": str(repo),
        "source_reports": {
            "toolchain": TOOLCHAIN_REPORT.as_posix(),
            "lane_readout": LANE_READOUT.as_posix()
        },
        "tool_count": len(records),
        "counts_by_class": counts_by_class,
        "counts_by_state": counts_by_state,
        "counts_by_kind": counts_by_kind,
        "records": records,
        "rejected_rework_required": rejected[:80],
        "candidate_tools": candidates[:80],
        "verdict": "PASS_TOOL_INVENTORY_RECORDED_WITH_CANDIDATES_AND_DEBT",
        "not_claimed": [
            "all internal tools strictly clean",
            "all external libraries discovered",
            "all tools admitted strict",
            "automatic installation or mutation"
        ],
        "warnings": [
            "Inventory is admission baseline, not strict tool validation.",
            "Patch payload tools are candidates until landed and validated.",
            "External tool availability is local host truth only."
        ]
    }
    out = repo / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
