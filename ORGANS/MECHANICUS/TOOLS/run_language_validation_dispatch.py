#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import py_compile
import tomllib
from pathlib import Path
from typing import Any, Dict, List

EXCLUDE_DIRS = {
    ".git", "node_modules", "target", "dist", "build", "__pycache__",
    ".venv", "venv", ".mypy_cache", ".ruff_cache", ".pytest_cache",
    ".next", ".turbo", ".idea", ".vscode"
}

def is_current_source_candidate(path: Path, repo: Path) -> bool:
    rel = path.relative_to(repo).as_posix()
    if rel.startswith("WARP/PATCHES/") or "/FILES_TO_LAND/" in rel:
        return False
    parts = set(path.relative_to(repo).parts)
    if parts & EXCLUDE_DIRS:
        return False
    return True

def files(repo: Path, suffixes: set[str]) -> List[Path]:
    out = []
    for path in repo.rglob("*"):
        if path.is_file() and path.suffix.lower() in suffixes and is_current_source_candidate(path, repo):
            out.append(path)
    return out

def cap(items: List[Any], n: int = 80) -> List[Any]:
    return items[:n]

def load_toolchain(repo: Path) -> Dict[str, Any]:
    path = repo / "ORGANS/MECHANICUS/REPORTS/MECHANICUS_TOOLCHAIN_PROOF_REPORT_V0_1.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}

def tool_ok(toolchain: Dict[str, Any], names: List[str]) -> bool:
    results = {r.get("name"): r for r in toolchain.get("results", []) or []}
    return all(bool(results.get(n, {}).get("ok")) for n in names)

def validate_json(repo: Path) -> Dict[str, Any]:
    errors = []
    target_files = files(repo, {".json", ".jsonl"})
    for path in target_files:
        rel = path.relative_to(repo).as_posix()
        try:
            if path.suffix.lower() == ".jsonl":
                for i, line in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
                    if line.strip():
                        json.loads(line)
            else:
                json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as e:
            errors.append({"path": rel, "error": str(e)})
    return {
        "language": "JSON/JSONL",
        "lane_id": "json_evidence",
        "files_checked": len(target_files),
        "ok": not errors,
        "baseline_type": "parse_all_current_non_patch_json",
        "errors": cap(errors),
        "debt_kind": "governance_evidence_parse_debt" if errors else None
    }

def validate_toml(repo: Path) -> Dict[str, Any]:
    errors = []
    target_files = files(repo, {".toml"})
    for path in target_files:
        try:
            tomllib.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as e:
            errors.append({"path": path.relative_to(repo).as_posix(), "error": str(e)})
    return {
        "language": "TOML",
        "lane_id": "toml_config",
        "files_checked": len(target_files),
        "ok": not errors,
        "baseline_type": "parse_all_current_toml",
        "errors": cap(errors)
    }

def validate_python(repo: Path) -> Dict[str, Any]:
    errors = []
    target_files = files(repo, {".py"})
    for path in target_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as e:
            errors.append({"path": path.relative_to(repo).as_posix(), "error": str(e)})
    return {
        "language": "Python",
        "lane_id": "python",
        "files_checked": len(target_files),
        "ok": not errors,
        "baseline_type": "py_compile_current_non_patch_python",
        "errors": cap(errors),
        "not_claimed": ["ruff clean", "mypy clean", "pytest clean"]
    }

def validate_markdown(repo: Path) -> Dict[str, Any]:
    target_files = files(repo, {".md"})
    empty = []
    for path in target_files:
        if not path.read_text(encoding="utf-8", errors="replace").strip():
            empty.append(path.relative_to(repo).as_posix())
    return {
        "language": "Markdown",
        "lane_id": "markdown_docs",
        "files_checked": len(target_files),
        "ok": not empty,
        "baseline_type": "non_empty_markdown_current_non_patch",
        "errors": [{"path": x, "error": "empty markdown"} for x in cap(empty)],
        "not_claimed": ["markdownlint clean", "link integrity"]
    }

def validate_powershell(repo: Path, toolchain: Dict[str, Any]) -> Dict[str, Any]:
    target_files = files(repo, {".ps1", ".psm1", ".psd1"})
    pwsh_ok = tool_ok(toolchain, ["pwsh_version"])
    return {
        "language": "PowerShell",
        "lane_id": "powershell",
        "files_checked": len(target_files),
        "ok": pwsh_ok or len(target_files) == 0,
        "baseline_type": "powershell_surface_and_toolchain_detection_no_parser_yet",
        "toolchain_ok": pwsh_ok,
        "errors": [] if pwsh_ok or len(target_files) == 0 else [{"path": "", "error": "PowerShell files exist but pwsh unavailable"}],
        "not_claimed": ["PowerShell parser clean", "PSScriptAnalyzer clean", "runner contract proof"]
    }

def validate_rust(repo: Path, toolchain: Dict[str, Any]) -> Dict[str, Any]:
    target_files = files(repo, {".rs"})
    manifests = [p.relative_to(repo).as_posix() for p in files(repo, {".toml"}) if p.name == "Cargo.toml"]
    cargo_ok = tool_ok(toolchain, ["rustc_version", "cargo_version"])
    return {
        "language": "Rust",
        "lane_id": "rust",
        "files_checked": len(target_files),
        "ok": cargo_ok or len(target_files) == 0,
        "baseline_type": "rust_surface_and_toolchain_detection_no_cargo_check",
        "toolchain_ok": cargo_ok,
        "cargo_manifests_detected": manifests,
        "errors": [] if cargo_ok or len(target_files) == 0 else [{"path": "", "error": "Rust files exist but rust/cargo toolchain unavailable"}],
        "not_claimed": ["cargo check", "cargo fmt", "cargo clippy", "cargo test"]
    }

def validate_node_frontend(repo: Path, toolchain: Dict[str, Any]) -> Dict[str, Any]:
    target_files = files(repo, {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"})
    package_files = [p.relative_to(repo).as_posix() for p in files(repo, {".json"}) if p.name == "package.json"]
    node_ok = tool_ok(toolchain, ["node_version", "npm_version"])
    return {
        "language": "JavaScript/TypeScript",
        "lane_id": "node_frontend",
        "files_checked": len(target_files),
        "ok": node_ok or len(target_files) == 0,
        "baseline_type": "node_frontend_surface_and_toolchain_detection_no_npm_build",
        "toolchain_ok": node_ok,
        "package_json_detected": package_files,
        "errors": [] if node_ok or len(target_files) == 0 else [{"path": "", "error": "JS/TS files exist but node/npm toolchain unavailable"}],
        "not_claimed": ["npm build", "eslint clean", "tsc clean", "npm audit clean"]
    }

def validate_css(repo: Path, toolchain: Dict[str, Any]) -> Dict[str, Any]:
    target_files = files(repo, {".css", ".scss"})
    errors = []
    for path in target_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if text.count("{") != text.count("}"):
            errors.append({"path": path.relative_to(repo).as_posix(), "error": "brace count mismatch"})
    return {
        "language": "CSS",
        "lane_id": "css_ui",
        "files_checked": len(target_files),
        "ok": not errors,
        "baseline_type": "css_structural_brace_balance_current_non_patch",
        "errors": cap(errors),
        "not_claimed": ["stylelint clean", "token coverage", "reference fidelity", "no CSS monolith"]
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default="ORGANS/MECHANICUS/REPORTS/MECHANICUS_LANGUAGE_VALIDATION_BASELINE_V0_1.json")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    toolchain = load_toolchain(repo)

    checks = [
        validate_json(repo),
        validate_toml(repo),
        validate_python(repo),
        validate_markdown(repo),
        validate_powershell(repo, toolchain),
        validate_rust(repo, toolchain),
        validate_node_frontend(repo, toolchain),
        validate_css(repo, toolchain),
    ]

    debt = []
    for c in checks:
        if not c.get("ok"):
            debt.append({
                "language": c.get("language"),
                "lane_id": c.get("lane_id"),
                "files_checked": c.get("files_checked"),
                "baseline_type": c.get("baseline_type"),
                "error_count_visible": len(c.get("errors", [])),
                "errors": c.get("errors", [])
            })

    report = {
        "tool_id": "mechanicus_language_validator_dispatch_baseline.v0_2_lane_expanded",
        "repo_root": str(repo),
        "mode": "LANE_EXPANDED_BASELINE_MEASURED_WITH_VALIDATION_DEBT",
        "checks": checks,
        "all_baseline_checks_clean": not debt,
        "validation_debt": debt,
        "verdict": "PASS_BASELINE_CLEAN_FOR_IMPLEMENTED_LANE_CHECKS" if not debt else "PASS_BASELINE_MEASURED_WITH_VALIDATION_DEBT",
        "not_claimed": [
            "100% code cleanliness",
            "all linters present",
            "all type checkers present",
            "all strict build lanes passed",
            "dependency security clean",
            "architecture clean"
        ],
        "warnings": [
            "This baseline intentionally does not claim 100% clean.",
            "Strict build/lint/type/security layers remain future work.",
            "Patch-pack payload is excluded from current-source baseline checks.",
            "Build proof is not code purity proof."
        ]
    }
    out = repo / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
