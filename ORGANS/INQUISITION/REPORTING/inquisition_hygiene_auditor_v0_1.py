#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inquisition Hygiene Auditor V0.1.

Read-only diagnostic auditor for Imperium New Reality.
It detects risk signals and writes machine/owner reports outside source tree.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

VERSION = "0.1.0"
SURFACE = "INQUISITION_HYGIENE_AUDITOR_V0_1"
TEXT_SUFFIXES = {
    ".py", ".ps1", ".js", ".cjs", ".mjs", ".ts", ".tsx", ".html", ".css",
    ".json", ".md", ".txt", ".csv", ".yml", ".yaml", ".toml", ".sql", ".sh"
}
SCRIPT_SUFFIXES = {".py", ".ps1", ".js", ".cjs", ".mjs", ".ts", ".sh"}
EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "playwright-report", "test-results", "dist", "build", ".next", ".venv", "venv"
}
MOJIBAKE_MARKERS = [
    "Рџ", "рџ", "РЎ", "Рљ", "Рґ", "Рё", "Р°", "Рµ", "СЃ", "С‚", "СЂ", "СЏ",
    "В·", "в†", "вЂ", "в„", "вњ", "в–", "в▯", "ЊЂ", "њЃ", "нЬ", "нБ", "�",
]
TOOL_NAME_RE = re.compile(
    r"(tool|runner|scanner|auditor|smoke|check|validate|builder|manager|bridge|launcher|registry|packager|probe|hygiene|inquisition|mechanicus|atlas|warp)",
    re.IGNORECASE,
)


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stable_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha256("|".join(parts).encode("utf-8", errors="replace")).hexdigest()[:12]
    return f"{prefix}-{h}"


def rel_path(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def iter_files(repo: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(repo):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for name in files:
            yield root_path / name


def read_text(path: Path) -> Optional[str]:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None
    except Exception:
        return None


def organ_from_path(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "ORGANS":
        return parts[1]
    return "ROOT"


def finding(severity: str, risk_type: str, repo: Path, path: Path, evidence: str, why: str, action: str, blocking: bool = False, related_tool_id: str = "") -> Dict[str, Any]:
    rel = rel_path(repo, path)
    return {
        "finding_id": stable_id("FIND", severity, risk_type, rel, evidence),
        "severity": severity,
        "risk_type": risk_type,
        "path": rel,
        "organ": organ_from_path(rel),
        "evidence": evidence[:500],
        "why_it_matters": why,
        "recommended_next_action": action,
        "blocking_gate": blocking,
        "safe_to_ignore_until": "owner_review" if severity in {"CRITICAL", "WARNING"} else "next_hygiene_pass",
        "related_tool_id": related_tool_id,
        "related_atlas_entity": rel,
    }


def load_registered_paths(repo: Path) -> Tuple[set, List[str]]:
    paths = set()
    tool_ids: List[str] = []
    seed = repo / "ORGANS" / "MECHANICUS" / "TOOL_INTELLIGENCE" / "PASSPORTS" / "seed_tool_passports_v0_1.json"
    if not seed.exists():
        return paths, tool_ids
    try:
        data = json.loads(seed.read_text(encoding="utf-8-sig"))
    except Exception:
        return paths, tool_ids
    candidates = []
    if isinstance(data, dict):
        if isinstance(data.get("tools"), list):
            candidates = data["tools"]
        elif isinstance(data.get("tool_passports"), list):
            candidates = data["tool_passports"]
        elif isinstance(data.get("passports"), list):
            candidates = data["passports"]
    elif isinstance(data, list):
        candidates = data
    for item in candidates:
        if not isinstance(item, dict):
            continue
        tid = str(item.get("tool_id") or item.get("id") or "")
        if tid:
            tool_ids.append(tid)
        for key in ("path", "source_path", "script_path", "entrypoint", "relative_path"):
            val = item.get(key)
            if isinstance(val, str) and val:
                paths.add(val.replace("\\", "/"))
    return paths, tool_ids


def is_tool_like(path: Path, text: Optional[str]) -> bool:
    name = path.name
    if path.suffix.lower() not in SCRIPT_SUFFIXES:
        return False
    if name == "__init__.py":
        return False
    if TOOL_NAME_RE.search(name):
        return True
    if text and ("argparse" in text or "if __name__ ==" in text or "process.argv" in text):
        return True
    return False


def git_status(repo: Path) -> List[str]:
    try:
        cp = subprocess.run(["git", "-C", str(repo), "status", "--porcelain=v1", "-uall"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
        return cp.stdout.splitlines()
    except Exception:
        return []


def detect(repo: Path) -> Dict[str, Any]:
    registered_paths, registered_tool_ids = load_registered_paths(repo)
    findings: List[Dict[str, Any]] = []
    counters: Dict[str, int] = {}
    language_counts: Dict[str, int] = {}
    tool_like_total = 0
    unregistered_tool_like_total = 0

    suffix_to_language = {
        ".py": "python", ".ps1": "powershell_pwsh", ".js": "javascript_node", ".cjs": "javascript_node",
        ".mjs": "javascript_node", ".ts": "typescript", ".tsx": "typescript", ".sh": "shell",
        ".sql": "sqlite_sql", ".html": "html", ".css": "css", ".json": "json", ".md": "markdown",
    }

    for path in iter_files(repo):
        rel = rel_path(repo, path)
        suffix = path.suffix.lower()
        lang = suffix_to_language.get(suffix)
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + 1

        if "__pycache__" in path.parts or suffix in {".pyc", ".pyo"}:
            findings.append(finding(
                "WARNING", "PYTHON_CACHE_IN_SOURCE", repo, path,
                "Python cache artifact found in source tree.",
                "Cache files are generated runtime residue and should not define source truth.",
                "Remove cache artifacts and keep smoke guards excluding generated binaries.",
            ))
            continue

        if suffix == ".zip":
            findings.append(finding(
                "WARNING", "ARCHIVE_REVIEW_REQUIRED", repo, path,
                "Archive file exists under source tree.",
                "Archives hide contents from normal source review and can duplicate old truth.",
                "Classify lifecycle: source fixture, archive review, quarantine, or move to local handoff.",
            ))

        if "LEGACY_IMPORTED_ROOT_MIRROR" in rel:
            findings.append(finding(
                "INFO", "LEGACY_MIRROR_CONTAMINATION", repo, path,
                "Path belongs to LEGACY_IMPORTED_ROOT_MIRROR.",
                "Legacy mirrors increase duplicate/conflicting truth and require staged migration.",
                "Tag legacy lifecycle in Data Atlas and create quarantine/migration plan.",
            ))

        if any(token in rel for token in ["_LOCAL_HANDOFF", "SERVITOR_OUTPUTS", "WARP_RUNS", "playwright-report", "test-results"]):
            findings.append(finding(
                "CRITICAL", "SOURCE_RUNTIME_LEAK", repo, path,
                "Runtime/local output marker found in source path.",
                "Runtime evidence must live outside source to keep git truth clean.",
                "Move outputs to local handoff and add guard to prevent recurrence.",
                blocking=True,
            ))

        text = read_text(path)
        if text is not None:
            hits = [m for m in MOJIBAKE_MARKERS if m in text]
            if hits:
                findings.append(finding(
                    "CRITICAL", "ENCODING_MOJIBAKE", repo, path,
                    "Mojibake markers found: " + ", ".join(hits[:10]),
                    "Encoding corruption makes UI/docs/source untrustworthy and can spread through patches.",
                    "Restore file from clean UTF-8 source; patch only with pwsh 7+ or binary-safe copy.",
                    blocking=True,
                ))

            if is_tool_like(path, text):
                tool_like_total += 1
                normalized = rel.replace("\\", "/")
                if normalized not in registered_paths:
                    unregistered_tool_like_total += 1
                    findings.append(finding(
                        "WARNING", "NO_TOOL_PASSPORT", repo, path,
                        "Tool-like script not present in Mechanicus seed tool passports.",
                        "Agents cannot safely choose, validate, or explain unregistered tools.",
                        "Create tool passport or classify as legacy/quarantine/not-a-tool.",
                    ))

                if "subprocess" in text and "shell=True" in text:
                    findings.append(finding(
                        "CRITICAL", "WRITE_ACTION_WITHOUT_SAFETY", repo, path,
                        "subprocess usage with shell=True found in tool-like script.",
                        "Shell execution increases command injection and arbitrary shell risk.",
                        "Review safety model; prefer allowlisted args and explicit cwd/write roots.",
                        blocking=True,
                    ))

    # git untracked generated/cache dirt
    for line in git_status(repo):
        if "__pycache__" in line or line.endswith(".pyc"):
            fake_path = repo / line[3:].strip()
            findings.append(finding(
                "WARNING", "GENERATED_ARTIFACT_IN_SOURCE", repo, fake_path,
                "Git status reports generated cache dirt.",
                "Generated files in working tree hide real source changes.",
                "Clean generated artifacts before commit; update .gitignore if needed.",
            ))

    for f in findings:
        counters[f["risk_type"]] = counters.get(f["risk_type"], 0) + 1

    severity_counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    for f in findings:
        severity_counts[f["severity"]] = severity_counts.get(f["severity"], 0) + 1

    status = "PASS"
    if severity_counts.get("CRITICAL", 0) > 0:
        status = "FAIL_WITH_FINDINGS"
    elif severity_counts.get("WARNING", 0) > 0 or severity_counts.get("INFO", 0) > 0:
        status = "PASS_WITH_WARNINGS"

    return {
        "status": status,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "repo_root": str(repo),
        "summary": {
            "findings_total": len(findings),
            "critical_total": severity_counts.get("CRITICAL", 0),
            "warning_total": severity_counts.get("WARNING", 0),
            "info_total": severity_counts.get("INFO", 0),
            "risk_types_detected": len(counters),
            "tool_like_total": tool_like_total,
            "unregistered_tool_like_total": unregistered_tool_like_total,
            "registered_tool_passports_total": len(registered_tool_ids),
            "languages_detected": len(language_counts),
        },
        "severity_counts": severity_counts,
        "risk_counts": dict(sorted(counters.items(), key=lambda kv: (-kv[1], kv[0]))),
        "language_counts": dict(sorted(language_counts.items())),
        "registered_tool_ids": registered_tool_ids,
        "findings_sample": findings[:200],
        "findings": findings,
        "next_recommendations_ru": [
            "Показать Inquisition findings рядом с Data Atlas entity cards.",
            "Свести NO_TOOL_PASSPORT findings в Mechanicus паспортную очередь.",
            "Сначала закрывать CRITICAL encoding/runtime/source leak findings.",
            "Не запускать cleanup автоматически: только owner-reviewed patches.",
        ],
    }


def write_outputs(report: Dict[str, Any], out_root: Path) -> Path:
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = out_root / f"INQUISITION_HYGIENE_AUDIT_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "MACHINE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    with (run_dir / "findings.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["finding_id", "severity", "risk_type", "organ", "path", "evidence", "recommended_next_action", "blocking_gate"])
        writer.writeheader()
        for item in report.get("findings", []):
            writer.writerow({k: item.get(k, "") for k in writer.fieldnames})

    with (run_dir / "risk_counts.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["risk_type", "count"])
        for k, v in report.get("risk_counts", {}).items():
            writer.writerow([k, v])

    lines = [
        "# Inquisition Hygiene Report V0.1",
        "",
        f"Status: **{report['status']}**",
        f"Generated: `{report['generated_at_utc']}`",
        f"Repo: `{report['repo_root']}`",
        "",
        "## Summary",
        "",
    ]
    for k, v in report.get("summary", {}).items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## Risk counts", ""]
    for k, v in report.get("risk_counts", {}).items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## First recommendations", ""]
    for rec in report.get("next_recommendations_ru", []):
        lines.append(f"- {rec}")
    lines += ["", "## Findings sample", ""]
    for item in report.get("findings_sample", [])[:30]:
        lines.append(f"- **{item['severity']} · {item['risk_type']}** `{item['path']}` — {item['recommended_next_action']}")
    (run_dir / "OWNER_READABLE_REPORT_RU.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return run_dir


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--out-root", default="E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()
    report = detect(repo)
    report["dry_run"] = bool(args.dry_run)
    if args.dry_run:
        print(json.dumps({k: report[k] for k in ["status", "surface", "version", "generated_at_utc", "summary", "risk_counts"]}, ensure_ascii=False, indent=2))
        return 0
    run_dir = write_outputs(report, Path(args.out_root))
    report["output_root"] = str(run_dir)
    (run_dir / "MACHINE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "surface": report["surface"],
        "version": report["version"],
        "summary": report["summary"],
        "risk_counts": report["risk_counts"],
        "output_root": str(run_dir),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
