#!/usr/bin/env python3
"""Mechanicus code topology and monolith census for Imperium Core.

Script-first, no LLM dependency. Scans SUPPORT/APP_TAURI by default and reports
lines, languages, zones, monolith risks, dependency files and refactor targets.
"""
from __future__ import annotations

import argparse
import json
import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TASK_ID = "MECHANICUS-CODE-TOPOLOGY-V0-1"
VERDICT = "PASS_MECHANICUS_CODE_TOPOLOGY_READY"
TEXT_EXTS = {
    ".js", ".jsx", ".ts", ".tsx", ".css", ".scss", ".html", ".rs", ".py", ".ps1",
    ".json", ".jsonl", ".md", ".toml", ".yml", ".yaml", ".txt"
}
EXT_LANG = {
    ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".css": "CSS", ".scss": "CSS", ".html": "HTML", ".rs": "Rust", ".py": "Python",
    ".ps1": "PowerShell", ".json": "JSON", ".jsonl": "JSONL", ".md": "Markdown", ".toml": "TOML",
}
MONOLITH_THRESHOLDS = {
    ".js": 420,
    ".ts": 420,
    ".tsx": 420,
    ".css": 760,
    ".rs": 520,
    ".py": 520,
    ".ps1": 260,
}
BLOCKER_THRESHOLDS = {
    ".js": 800,
    ".ts": 800,
    ".tsx": 800,
    ".css": 1200,
    ".rs": 900,
    ".py": 900,
    ".ps1": 500,
}

IGNORE_PARTS = {"node_modules", "target", "dist", ".git", "__pycache__"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def should_skip(path: Path) -> bool:
    return any(part in IGNORE_PARTS for part in path.parts)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def count_lines(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def classify_zone(repo_root: Path, path: Path) -> str:
    r = rel(repo_root, path)
    if r.endswith("SUPPORT/APP_TAURI/src/main.js"):
        return "APP_FRONTEND_MONOLITH_CANDIDATE"
    if r.endswith("SUPPORT/APP_TAURI/src/styles.css"):
        return "APP_STYLE_SURFACE_MONOLITH_CANDIDATE"
    if "SUPPORT/APP_TAURI/src-tauri/src" in r:
        return "TAURI_RUST_COMMAND_BRIDGE"
    if "SUPPORT/APP_TAURI/tools" in r:
        return "APP_TERMINAL_TOOLS"
    if "SUPPORT/APP_TAURI/tests" in r:
        return "APP_TESTS_VALIDATORS"
    if "SUPPORT/APP_TAURI/receipts" in r:
        return "APP_EVIDENCE_RECEIPTS"
    if "SUPPORT/APP_TAURI/contracts" in r:
        return "APP_CONTRACTS"
    if "SUPPORT/APP_TAURI/src" in r:
        return "APP_FRONTEND_SOURCE"
    return "APP_OTHER"


def js_metrics(text: str) -> dict[str, int]:
    return {
        "function_like_count": len(re.findall(r"\bfunction\b|=>", text)),
        "event_listener_count": len(re.findall(r"addEventListener|onclick|onchange|oninput", text)),
        "invoke_count": len(re.findall(r"\binvoke\s*\(", text)),
        "query_selector_count": len(re.findall(r"querySelector|getElementById", text)),
    }


def css_metrics(text: str) -> dict[str, int]:
    return {
        "selector_block_count": len(re.findall(r"[^{}]+\{", text)),
        "media_query_count": len(re.findall(r"@media", text)),
        "root_token_count": len(re.findall(r"--[a-zA-Z0-9_-]+\s*:", text)),
    }


def rust_metrics(text: str) -> dict[str, int]:
    return {
        "tauri_command_count": len(re.findall(r"#\[tauri::command\]", text)),
        "function_count": len(re.findall(r"\bfn\s+[a-zA-Z0-9_]+", text)),
    }


def file_record(repo_root: Path, scope_root: Path, path: Path) -> dict[str, Any]:
    text = read_text(path)
    loc = count_lines(text)
    ext = path.suffix.lower()
    warn_at = MONOLITH_THRESHOLDS.get(ext)
    block_at = BLOCKER_THRESHOLDS.get(ext)
    risk = "OK"
    if block_at and loc >= block_at:
        risk = "BLOCKING_MONOLITH"
    elif warn_at and loc >= warn_at:
        risk = "MONOLITH_RISK"
    metrics: dict[str, Any] = {}
    if ext in {".js", ".ts", ".tsx", ".jsx"}:
        metrics.update(js_metrics(text))
    if ext in {".css", ".scss"}:
        metrics.update(css_metrics(text))
    if ext == ".rs":
        metrics.update(rust_metrics(text))
    return {
        "path": rel(repo_root, path),
        "scope_path": rel(scope_root, path),
        "ext": ext or "<none>",
        "language": EXT_LANG.get(ext, "Other"),
        "lines": loc,
        "zone": classify_zone(repo_root, path),
        "monolith_risk": risk,
        "metrics": metrics,
    }


def load_package_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"exists": True, "parse_error": str(exc)}
    deps = data.get("dependencies", {}) or {}
    dev = data.get("devDependencies", {}) or {}
    scripts = data.get("scripts", {}) or {}
    return {
        "exists": True,
        "name": data.get("name"),
        "version": data.get("version"),
        "dependency_count": len(deps),
        "dev_dependency_count": len(dev),
        "script_names": sorted(scripts.keys()),
        "dependencies": sorted(deps.keys()),
        "dev_dependencies": sorted(dev.keys()),
    }


def load_cargo_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"exists": True, "parse_error": str(exc)}
    pkg = data.get("package", {}) or {}
    deps = data.get("dependencies", {}) or {}
    return {
        "exists": True,
        "name": pkg.get("name"),
        "version": pkg.get("version"),
        "dependency_count": len(deps),
        "dependencies": sorted(deps.keys()),
    }


def build_topology(repo_root: Path, scope: str) -> dict[str, Any]:
    scope_root = (repo_root / scope).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not scope_root.exists():
        errors.append(f"scope missing: {scope}")
        records: list[dict[str, Any]] = []
    else:
        files = [p for p in scope_root.rglob("*") if p.is_file() and not should_skip(p) and p.suffix.lower() in TEXT_EXTS]
        records = [file_record(repo_root, scope_root, p) for p in sorted(files)]

    total_lines = sum(r["lines"] for r in records)
    by_language: dict[str, dict[str, int]] = {}
    by_zone: dict[str, dict[str, int]] = {}
    for r in records:
        lang = r["language"]
        z = r["zone"]
        by_language.setdefault(lang, {"files": 0, "lines": 0})
        by_language[lang]["files"] += 1
        by_language[lang]["lines"] += r["lines"]
        by_zone.setdefault(z, {"files": 0, "lines": 0})
        by_zone[z]["files"] += 1
        by_zone[z]["lines"] += r["lines"]

    monoliths = [r for r in records if r["monolith_risk"] != "OK"]
    blockers = [r for r in records if r["monolith_risk"] == "BLOCKING_MONOLITH"]
    monoliths_sorted = sorted(monoliths, key=lambda r: r["lines"], reverse=True)
    top_files = sorted(records, key=lambda r: r["lines"], reverse=True)[:20]

    if monoliths:
        warnings.append(f"monolith risk files visible: {len(monoliths)}")
    if blockers:
        warnings.append(f"blocking monolith files visible: {len(blockers)}")

    node_boundary_map = [
        {"node_id": "core_shell_header", "owner_file_hint": "SUPPORT/APP_TAURI/src/main.js", "responsibility": "product name, version strip, top truth markers", "split_recommendation": "extract shell-header module"},
        {"node_id": "left_room_nav", "owner_file_hint": "SUPPORT/APP_TAURI/src/main.js", "responsibility": "room navigation state", "split_recommendation": "extract room-nav module"},
        {"node_id": "astronomicon_registration", "owner_file_hint": "SUPPORT/APP_TAURI/src/main.js", "responsibility": "registration UI state, candidate/polished gates", "split_recommendation": "extract astronomicon-room module"},
        {"node_id": "mechanicus_digest", "owner_file_hint": "SUPPORT/APP_TAURI/src/main.js", "responsibility": "technical summary cards, language/validator/debt readout", "split_recommendation": "extract mechanicus-digest module"},
        {"node_id": "proof_digest", "owner_file_hint": "SUPPORT/APP_TAURI/src/main.js", "responsibility": "short proof log and receipt links", "split_recommendation": "extract proof-digest module"},
        {"node_id": "right_command_rail", "owner_file_hint": "SUPPORT/APP_TAURI/src/main.js", "responsibility": "active room, patch state, truth boundary, version/update hints", "split_recommendation": "extract command-rail module"},
        {"node_id": "style_tokens", "owner_file_hint": "SUPPORT/APP_TAURI/src/styles.css", "responsibility": "premium gothic/trash-polka tokens, density, surfaces", "split_recommendation": "split tokens/layout/components css files"},
        {"node_id": "tauri_commands", "owner_file_hint": "SUPPORT/APP_TAURI/src-tauri/src/main.rs", "responsibility": "backend bridge commands and receipts", "split_recommendation": "split command modules when Rust grows"},
    ]

    app_root = repo_root / "SUPPORT" / "APP_TAURI"
    package = load_package_json(app_root / "package.json")
    cargo = load_cargo_toml(app_root / "src-tauri" / "Cargo.toml")

    verdict = VERDICT if not errors else "FAIL_MECHANICUS_CODE_TOPOLOGY"
    return {
        "task_id": TASK_ID,
        "validator_id": "mechanicus_code_topology.v0_1",
        "verdict": verdict,
        "generated_at_utc": utc_now(),
        "scope": scope,
        "file_count": len(records),
        "total_lines": total_lines,
        "language_counts": by_language,
        "zone_counts": by_zone,
        "top_files_by_lines": top_files,
        "monolith_risk_count": len(monoliths),
        "blocking_monolith_count": len(blockers),
        "monolith_records": monoliths_sorted,
        "node_boundary_map": node_boundary_map,
        "package_json": package,
        "cargo_toml": cargo,
        "refactor_priority": [
            "split SUPPORT/APP_TAURI/src/main.js into shell/nav/astronomicon/mechanicus/proof modules",
            "split SUPPORT/APP_TAURI/src/styles.css into tokens/layout/components/rooms/proof css",
            "keep app registration/launch buttons present but terminal remains preferred until UI matures",
            "build a one-screen proof digest before adding Eyes/Canvas runtime",
        ],
        "errors": errors,
        "warnings": warnings,
    }


def write_md(report: dict[str, Any]) -> str:
    lines = [
        "# Mechanicus Code Topology V0.1", "",
        f"- verdict: `{report['verdict']}`",
        f"- generated_at_utc: `{report['generated_at_utc']}`",
        f"- scope: `{report['scope']}`",
        f"- file_count: `{report['file_count']}`",
        f"- total_lines: `{report['total_lines']}`",
        f"- monolith_risk_count: `{report['monolith_risk_count']}`",
        f"- blocking_monolith_count: `{report['blocking_monolith_count']}`",
        "", "## Languages", "",
    ]
    for lang, counts in sorted(report["language_counts"].items(), key=lambda item: item[1]["lines"], reverse=True):
        lines.append(f"- `{lang}`: files={counts['files']} lines={counts['lines']}")
    lines += ["", "## Top files by lines", ""]
    for r in report["top_files_by_lines"][:12]:
        lines.append(f"- `{r['path']}` lines={r['lines']} risk={r['monolith_risk']} zone={r['zone']}")
    if report["monolith_records"]:
        lines += ["", "## Monolith risks", ""]
        for r in report["monolith_records"][:12]:
            lines.append(f"- `{r['path']}` lines={r['lines']} risk={r['monolith_risk']}")
    lines += ["", "## Refactor priority", ""]
    for item in report["refactor_priority"]:
        lines.append(f"- {item}")
    if report["warnings"]:
        lines += ["", "## Warnings", ""]
        for w in report["warnings"]:
            lines.append(f"- {w}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--scope", default="SUPPORT/APP_TAURI")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    report = build_topology(repo_root, args.scope)

    reports_dir = repo_root / "ORGANS" / "MECHANICUS" / "REPORTS"
    receipts_dir = repo_root / "ORGANS" / "MECHANICUS" / "RECEIPTS"
    app_receipts = repo_root / "SUPPORT" / "APP_TAURI" / "receipts"
    reports_dir.mkdir(parents=True, exist_ok=True)
    receipts_dir.mkdir(parents=True, exist_ok=True)
    app_receipts.mkdir(parents=True, exist_ok=True)

    report_json = reports_dir / "MECHANICUS_CODE_TOPOLOGY_REPORT_V0_1.json"
    report_md = reports_dir / "MECHANICUS_CODE_TOPOLOGY_REPORT_V0_1.md"
    summary_json = reports_dir / "MECHANICUS_CODE_TOPOLOGY_SUMMARY_V0_1.json"
    receipt_json = receipts_dir / "mechanicus_code_topology_receipt.json"

    summary_keys = [
        "task_id", "verdict", "generated_at_utc", "scope", "file_count", "total_lines",
        "language_counts", "zone_counts", "monolith_risk_count", "blocking_monolith_count",
        "refactor_priority", "errors", "warnings"
    ]
    summary = {k: report[k] for k in summary_keys}
    summary["top_monoliths"] = [
        {"path": r["path"], "lines": r["lines"], "risk": r["monolith_risk"], "zone": r["zone"]}
        for r in report["monolith_records"][:8]
    ]
    summary["node_boundary_count"] = len(report["node_boundary_map"])

    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md.write_text(write_md(report), encoding="utf-8")
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    receipt = dict(summary)
    receipt.update({
        "report_json": rel(repo_root, report_json),
        "report_md": rel(repo_root, report_md),
        "summary": rel(repo_root, summary_json),
    })
    receipt_json.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    (app_receipts / "mechanicus_code_topology_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.compact:
        langs = ",".join(sorted(report["language_counts"].keys()))
        print(f"MECHANICUS: files={report['file_count']} lines={report['total_lines']} langs={langs}")
        print(f"MECH_MONOLITH: risks={report['monolith_risk_count']} blockers={report['blocking_monolith_count']} nodes={len(report['node_boundary_map'])}")
        if report["warnings"]:
            print("MECH_WARN: " + " | ".join(report["warnings"][:3]))
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
