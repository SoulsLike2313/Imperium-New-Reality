#!/usr/bin/env python3
"""Mechanicus Operational Power Auditor V0.1.1.

Read-only/evidence-only scanner for language/tool/passport coverage.
Outputs are written outside the source repo under LOCAL_HANDOFF.

V0.1.1 fixes:
- --out FILE.json now writes a single machine JSON file.
- --out DIR treats DIR as report root and writes a report bundle under it.
- --out-root remains the default report-root option.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

VERSION = "0.1.1"
SURFACE = "MECHANICUS_OPERATIONAL_POWER_AUDITOR_V0_1_1"

LANG_BY_EXT = {
    ".py": "python",
    ".js": "javascript_node",
    ".cjs": "javascript_node",
    ".mjs": "javascript_node",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".h": "cpp",
    ".c": "c",
    ".sql": "sqlite_sql",
    ".ps1": "powershell_pwsh",
    ".sh": "shell",
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "playwright-report",
    "test-results",
    "dist",
    "build",
}

SCRIPT_EXTS = set(LANG_BY_EXT)


def now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def iter_files(repo: Path):
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        root_path = Path(root)
        for name in files:
            path = root_path / name
            try:
                rel = path.relative_to(repo).as_posix()
            except ValueError:
                continue
            yield path, rel


def is_tool_like(rel: str, ext: str) -> bool:
    low = rel.lower()
    if ext not in SCRIPT_EXTS:
        return False
    markers = [
        "/tools/",
        "/reporting/",
        "scanner",
        "audit",
        "builder",
        "bridge",
        "manager",
        "registry",
        "hygiene",
        "validator",
        "smoke",
        "packager",
        "launcher",
    ]
    return any(m in low for m in markers)


def build_report(repo: Path, dry_run: bool = False) -> dict[str, Any]:
    mech_root = repo / "ORGANS" / "MECHANICUS" / "TOOL_INTELLIGENCE"
    passport_path = mech_root / "PASSPORTS" / "seed_tool_passports_v0_1.json"
    language_path = mech_root / "REGISTRIES" / "language_registry_v0_1.json"
    research_path = mech_root / "RESEARCH_QUEUE" / "tool_research_queue_v0_1.json"

    passports = read_json(passport_path, {"tools": []})
    language_registry = read_json(language_path, {"languages": []})
    research_queue = read_json(research_path, {"items": []})

    registered_paths = {t.get("path", "").replace("\\", "/"): t for t in passports.get("tools", [])}
    registered_tool_ids = {t.get("tool_id") for t in passports.get("tools", []) if t.get("tool_id")}

    language_counts: dict[str, int] = {}
    script_entities: list[dict[str, Any]] = []
    unregistered_tool_like: list[dict[str, Any]] = []

    for path, rel in iter_files(repo):
        ext = path.suffix.lower()
        lang = LANG_BY_EXT.get(ext)
        if not lang:
            continue
        language_counts[lang] = language_counts.get(lang, 0) + 1
        tool_like = is_tool_like(rel, ext)
        registered = rel in registered_paths
        entity = {
            "path": rel,
            "extension": ext,
            "language": lang,
            "tool_like": tool_like,
            "registered_passport": registered,
            "size_bytes": path.stat().st_size,
        }
        script_entities.append(entity)
        if tool_like and not registered:
            unregistered_tool_like.append(entity)

    validation_gap = []
    for tool in passports.get("tools", []):
        if not tool.get("validation"):
            validation_gap.append({"tool_id": tool.get("tool_id"), "path": tool.get("path")})

    total_scripts = len(script_entities)
    registered_count = sum(1 for e in script_entities if e["registered_passport"])
    tool_like_total = sum(1 for e in script_entities if e["tool_like"])

    summary = {
        "languages_detected": len(language_counts),
        "script_entities_total": total_scripts,
        "tool_like_scripts_total": tool_like_total,
        "registered_tool_passports_total": len(registered_tool_ids),
        "registered_script_paths_total": registered_count,
        "unregistered_tool_like_total": len(unregistered_tool_like),
        "validation_gap_total": len(validation_gap),
        "research_queue_total": len(research_queue.get("items", [])),
    }

    if total_scripts:
        summary["script_passport_path_coverage_percent"] = round(registered_count * 100 / total_scripts, 2)
    else:
        summary["script_passport_path_coverage_percent"] = 0

    verdict = "PASS_WITH_WARNINGS" if unregistered_tool_like or validation_gap else "PASS"

    return {
        "status": verdict,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "repo_root": str(repo),
        "dry_run": dry_run,
        "summary": summary,
        "language_counts": dict(sorted(language_counts.items())),
        "language_registry_total": len(language_registry.get("languages", [])),
        "registered_tool_ids": sorted(registered_tool_ids),
        "unregistered_tool_like_sample": sorted(unregistered_tool_like, key=lambda x: x["path"])[:100],
        "validation_gap": validation_gap,
        "research_queue_sample": research_queue.get("items", [])[:20],
        "next_recommendations_ru": [
            "Свести все tool-like scripts в Mechanicus passports.",
            "Подключить Data Atlas к seed_tool_passports_v0_1.json.",
            "Добавить UI карточки: Language Distribution, Tool Passport Coverage, Unregistered Scripts.",
            "Сделать первый task assessment report: язык/инструмент/алгоритм под конкретную задачу.",
        ],
    }


def write_report_bundle(report: dict[str, Any], output_root: Path) -> Path:
    run_root = output_root / f"MECHANICUS_OPERATIONAL_POWER_REPORT_{now_stamp()}"
    run_root.mkdir(parents=True, exist_ok=True)
    report["output_root"] = str(run_root)

    (run_root / "MACHINE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    with (run_root / "language_counts.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["language", "count"])
        for lang, count in sorted(report.get("language_counts", {}).items()):
            w.writerow([lang, count])

    with (run_root / "unregistered_tool_like_sample.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["path", "extension", "language", "tool_like", "registered_passport", "size_bytes"])
        w.writeheader()
        for row in report.get("unregistered_tool_like_sample", [])[:500]:
            w.writerow(row)

    md = [
        "# Mechanicus Operational Power Report V0.1.1",
        "",
        f"Status: **{report['status']}**",
        f"Generated: `{report['generated_at_utc']}`",
        f"Repo: `{report['repo_root']}`",
        "",
        "## Summary",
        "",
    ]
    for k, v in report.get("summary", {}).items():
        md.append(f"- {k}: `{v}`")
    md += ["", "## Language counts", ""]
    for lang, count in sorted(report.get("language_counts", {}).items()):
        md.append(f"- {lang}: `{count}`")
    md += ["", "## First recommendations", ""]
    for item in report.get("next_recommendations_ru", []):
        md.append(f"- {item}")
    (run_root / "OWNER_READABLE_REPORT_RU.md").write_text("\n".join(md), encoding="utf-8")
    return run_root


def write_single_json(report: dict[str, Any], output_file: Path) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    report["output_file"] = str(output_file)
    output_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_file


def resolve_output(args: argparse.Namespace) -> tuple[str, Path]:
    if args.out:
        target = Path(args.out)
        if target.suffix.lower() == ".json":
            return "file", target
        return "bundle", target
    return "bundle", Path(args.out_root)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[4]))
    parser.add_argument("--out-root", default="E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS")
    parser.add_argument("--out", default=None, help="Output target: FILE.json for single JSON, or DIR for a report bundle root.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    report = build_report(repo, dry_run=args.dry_run)

    if not args.dry_run:
        mode, target = resolve_output(args)
        if mode == "file":
            write_single_json(report, target)
        else:
            write_report_bundle(report, target)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
