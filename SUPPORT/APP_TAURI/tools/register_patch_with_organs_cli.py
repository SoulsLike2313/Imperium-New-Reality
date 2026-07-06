#!/usr/bin/env python3
"""Astronomicon -> Mechanicus terminal registration proof.

Script-first command for daily work while Tauri UI is overloaded.
It registers/analyzes a WARP patch pack without executing it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

PATCH_ID_RE = re.compile(r"^[A-Z0-9_.-]{1,180}$")
TEXT_SUFFIXES = {".md", ".json", ".jsonl", ".py", ".ps1", ".js", ".ts", ".css", ".html", ".rs", ".toml", ".yml", ".yaml"}


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / "ORGANS").is_dir() and (candidate / "WARP").is_dir():
            return candidate
    raise SystemExit("Repo root with ORGANS and WARP not found")


def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def safe_patch_id(patch_id: str) -> bool:
    return bool(PATCH_ID_RE.match(patch_id)) and ".." not in patch_id and "/" not in patch_id and "\\" not in patch_id


def iter_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted([p for p in root.rglob("*") if p.is_file()])


def rels_under(files_to_land: Path) -> list[str]:
    return [p.relative_to(files_to_land).as_posix() for p in iter_files(files_to_land)]


def infer_language(rel: str) -> str | None:
    if rel.endswith(".py"):
        return "Python"
    if rel.endswith(".ps1"):
        return "PowerShell"
    if rel.endswith(".rs") or "src-tauri" in rel:
        return "Rust"
    if rel.endswith(".js"):
        return "JavaScript"
    if rel.endswith(".ts"):
        return "TypeScript"
    if rel.endswith(".css"):
        return "CSS"
    if rel.endswith(".json") or rel.endswith(".jsonl"):
        return "JSON"
    if rel.endswith(".md"):
        return "Markdown"
    if rel.endswith(".toml"):
        return "TOML"
    return None


def infer_phase(patch_id: str, patch_dir: Path, intent: Any | None) -> str:
    up = patch_id.upper()
    if "CANDIDATE" in up or (patch_dir / "INTENT.json").is_file() or intent:
        return "CANDIDATE_INTAKE_PACK"
    if "POLISHED" in up or "RUN_READY" in up or (patch_dir / "POLISHED_PACK.json").is_file():
        return "POLISHED_EXECUTION_PACK"
    return "STANDARD_WARP_PATCH_PACK"


def task_class(patch_id: str, rels: list[str]) -> str:
    joined = (patch_id + " " + " ".join(rels)).upper()
    if any(k in joined for k in ["UI", "TAURI", "APP", "CSS", "CANVAS", "EYES", "VISUAL"]):
        return "UI_PRODUCT_SURFACE_OR_VISUAL_RUNTIME"
    if any(k in joined for k in ["MECHANICUS", "TOOL", "LANGUAGE", "BUILD", "VALIDATOR"]):
        return "MECHANICUS_TOOLING_OR_VALIDATION"
    if any(k in joined for k in ["THRONE", "CUSTODES", "LAW", "GOVERNANCE"]):
        return "GOVERNANCE_OR_CROWN_VALIDATION"
    return "GENERAL_WARP_PATCH"


def line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except Exception:
        return 0


def has_control_chars(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        data = path.read_bytes()
    except Exception:
        return True
    return any((b < 32 and b not in (9, 10, 13)) for b in data)


def analyze(repo: Path, patch_id: str) -> dict[str, Any]:
    if not safe_patch_id(patch_id):
        raise SystemExit(f"Unsafe patch id: {patch_id}")
    patch_dir = repo / "WARP" / "PATCHES" / patch_id
    files_to_land = patch_dir / "FILES_TO_LAND"
    runner = sorted(patch_dir.glob("RUN_*.ps1"))
    manifest = patch_dir / "PATCH_FILE_MANIFEST_SHA256.json"
    patch_pack = patch_dir / "PATCH_PACK.md"
    intent = read_json(patch_dir / "INTENT.json")
    rels = rels_under(files_to_land)
    phase = infer_phase(patch_id, patch_dir, intent)

    languages = sorted({lang for rel in rels if (lang := infer_language(rel))})
    expected = []
    if isinstance(intent, dict):
        expected = [str(x) for x in intent.get("mechanicus_expected_languages", []) if isinstance(x, str)]
        languages = sorted(set(languages).union(expected))

    touches_ui = any(x in languages for x in ["JavaScript", "TypeScript", "CSS", "Rust"]) or any("SUPPORT/APP_TAURI" in r for r in rels)
    main_js_lines = line_count(repo / "SUPPORT/APP_TAURI/src/main.js")
    css_lines = line_count(repo / "SUPPORT/APP_TAURI/src/styles.css")
    touches_main = any(r == "SUPPORT/APP_TAURI/src/main.js" for r in rels)
    touches_css = any(r == "SUPPORT/APP_TAURI/src/styles.css" for r in rels)
    monolith = "LOW_NON_UI_PATCH"
    if touches_main or touches_css or main_js_lines > 420 or css_lines > 950:
        monolith = "HIGH_REQUIRES_MODULE_DECOMPOSITION"
    elif touches_ui:
        monolith = "MEDIUM_UI_SURFACE_REQUIRES_NODE_BOUNDARIES"

    validators = ["patch_pack_shape_smoke", "no_control_chars", "json_parse"]
    if "Python" in languages:
        validators.append("python_py_compile")
    if "PowerShell" in languages:
        validators.append("pwsh_runner_exit_code")
    if any(x in languages for x in ["JavaScript", "TypeScript"]):
        validators.append("npm_run_build")
    if "Rust" in languages:
        validators.append("cargo_check")
    if touches_ui:
        validators.extend(["ui_reference_fidelity_or_screenshot_proof", "runtime_fps_proof"])

    missing = []
    if touches_ui:
        missing.append("UI_REFERENCE_FIDELITY_TOOLING_REQUIRED_IF_TARGET_UI")
    joined = (patch_id + " " + " ".join(rels)).upper()
    if any(k in joined for k in ["EYES", "CANVAS", "GAME"]):
        missing.append("GAME_OR_CANVAS_RUNTIME_CAPABILITY_NOT_FULLY_INVENTORIED")
    if monolith.startswith("HIGH"):
        missing.append("APP_TAURI_MONOLITH_DECOMPOSITION_REQUIRED")

    dirty_files = [p.relative_to(repo).as_posix() for p in iter_files(patch_dir) if has_control_chars(p)]
    shape_ok = patch_dir.is_dir() and files_to_land.is_dir() and patch_pack.is_file() and bool(runner) and manifest.is_file() and not dirty_files
    astro_verdict = "BLOCKED_DIRTY_OR_INCOMPLETE_PACK"
    if shape_ok:
        astro_verdict = "REGISTERABLE_CANDIDATE_PACK" if phase == "CANDIDATE_INTAKE_PACK" else "REGISTERABLE_PATCH_PACK"

    mech_verdict = "MECHANICUS_ACCEPTS_DRY_VALIDATION_PATH"
    if phase == "CANDIDATE_INTAKE_PACK":
        mech_verdict = "MECHANICUS_ANALYZES_CANDIDATE_REQUIRES_POLISHED_PACK"
    elif missing:
        mech_verdict = "MECHANICUS_ACCEPTS_WITH_VISIBLE_DEBT"

    launch_allowed = phase == "POLISHED_EXECUTION_PACK" and shape_ok
    report = {
        "task_id": "IMPERIUM-APP-ASTRONOMICON-TERMINAL-FIRST-WORKFLOW-0001",
        "patch_id": patch_id,
        "generated_at_unix": int(time.time()),
        "repo_root": str(repo),
        "verdict": "PASS_TERMINAL_ORGAN_REGISTRATION_ANALYSIS_READY" if shape_ok else "FAIL_TERMINAL_ORGAN_REGISTRATION_ANALYSIS",
        "astronomicon": {
            "verdict": astro_verdict,
            "phase": phase,
            "shape": {
                "patch_dir": patch_dir.is_dir(),
                "patch_pack_md": patch_pack.is_file(),
                "files_to_land": files_to_land.is_dir(),
                "runner": bool(runner),
                "manifest": manifest.is_file(),
                "land_file_count": len(rels),
                "dirty_control_char_files": dirty_files,
            },
        },
        "mechanicus": {
            "verdict": mech_verdict,
            "task_class": task_class(patch_id, rels),
            "languages": languages,
            "required_validators": validators,
            "monolith_risk": monolith,
            "visual_stack_required": touches_ui,
            "missing_capabilities": missing,
            "dependency_impact": {
                "nodes": [
                    {"node": "SUPPORT/APP_TAURI/src/main.js", "touched": touches_main, "line_count_now": main_js_lines},
                    {"node": "SUPPORT/APP_TAURI/src/styles.css", "touched": touches_css, "line_count_now": css_lines},
                    {"node": "SUPPORT/APP_TAURI/src-tauri/src/main.rs", "touched": any(r == "SUPPORT/APP_TAURI/src-tauri/src/main.rs" for r in rels)},
                    {"node": "WARP/PATCHES", "touched": any(r.startswith("WARP/PATCHES") for r in rels)},
                ],
                "cascade_rule": "Only dependent nodes need revalidation; no global rewrite without dependency evidence.",
            },
            "real_execution": "BLOCKED_FOR_CANDIDATE" if phase == "CANDIDATE_INTAKE_PACK" else "BLOCKED_UNLESS_POLISHED_AND_OWNER_APPROVED",
        },
        "workflow": {
            "phase": phase,
            "candidate_registration": phase == "CANDIDATE_INTAKE_PACK",
            "polished_pack_required": phase == "CANDIDATE_INTAKE_PACK",
            "launch_allowed": launch_allowed,
            "launch_gate": "ASTRONOMICON_ONLY",
        },
        "errors": [] if shape_ok else ["Patch pack is dirty or incomplete; see astronomicon.shape."],
        "warnings": ["Terminal proof only; UI renders a digest but receipts/reports prove truth."],
    }
    return report


def write_outputs(repo: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    rid = report["patch_id"].lower().replace("-", "_")
    out_dir = repo / "SUPPORT" / "APP_TAURI" / "receipts"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"terminal_organ_registration_{rid}_report.json"
    summary_path = out_dir / f"terminal_organ_registration_{rid}_summary.json"
    summary = {
        "patch_id": report["patch_id"],
        "verdict": report["verdict"],
        "astronomicon_verdict": report["astronomicon"]["verdict"],
        "mechanicus_verdict": report["mechanicus"]["verdict"],
        "task_class": report["mechanicus"]["task_class"],
        "workflow_phase": report["workflow"]["phase"],
        "launch_allowed": report["workflow"]["launch_allowed"],
        "monolith_risk": report["mechanicus"]["monolith_risk"],
        "languages": report["mechanicus"]["languages"],
        "missing_capabilities": report["mechanicus"]["missing_capabilities"],
        "report": report_path.as_posix(),
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report_path, summary_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--patch-id", required=True)
    ap.add_argument("--json", action="store_true", help="print full JSON report")
    args = ap.parse_args()
    repo = find_repo_root(Path(args.repo_root))
    report = analyze(repo, args.patch_id)
    report_path, summary_path = write_outputs(repo, report)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"TASK: TERMINAL_ORGAN_REGISTRATION")
        print(f"PATCH: {report['patch_id']}")
        print(f"VERDICT: {report['verdict']}")
        print(f"ASTRONOMICON: {report['astronomicon']['verdict']} | PHASE: {report['workflow']['phase']}")
        print(f"MECHANICUS: {report['mechanicus']['verdict']} | CLASS: {report['mechanicus']['task_class']}")
        print(f"LANG: {', '.join(report['mechanicus']['languages']) or 'none'}")
        print(f"MONOLITH: {report['mechanicus']['monolith_risk']} | LAUNCH_ALLOWED: {report['workflow']['launch_allowed']}")
        if report["mechanicus"]["missing_capabilities"]:
            print("DEBT: " + ", ".join(report["mechanicus"]["missing_capabilities"][:4]))
        print(f"SUMMARY: {summary_path.as_posix()}")
        print(f"REPORT: {report_path.as_posix()}")
    return 0 if report["verdict"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
