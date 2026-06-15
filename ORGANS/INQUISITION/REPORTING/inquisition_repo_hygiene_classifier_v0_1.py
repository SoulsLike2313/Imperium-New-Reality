#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Imperium Repo Hygiene Classifier v0.1

Read-only Inquisition classifier for Repo Hygiene & Passporting Batch 001.
It does not delete, move, or rewrite source. It scans git-tracked files,
assigns each file to an owner-review lane, and writes machine/owner reports
outside the repository.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

SURFACE = "INQUISITION_REPO_HYGIENE_CLASSIFIER_V0_1"
VERSION = "0.1.0"
SCHEMA = "imperium.repo_hygiene_classification.v0_1"

ARCHIVE_EXTS = {".zip", ".7z", ".rar", ".tar", ".gz", ".tgz", ".bz2", ".xz"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".ico"}
DATA_EXTS = {".json", ".jsonl", ".csv", ".tsv", ".sqlite", ".db", ".yaml", ".yml", ".xml"}
CODE_EXTS = {".py", ".ps1", ".js", ".ts", ".tsx", ".jsx", ".sh", ".bat", ".cmd", ".html", ".css"}
DOC_EXTS = {".md", ".txt", ".rst", ".adoc", ".pdf"}
RUNTIME_PARTS = {"__pycache__", ".pytest_cache", "node_modules", ".venv", "venv", "playwright-report", "test-results"}
LOCAL_ONLY_PREFIXES = (".imperium_patch_backups/", "_LOCAL_HANDOFF/", "LOCAL_HANDOFF/")
SMOKE_ROOT_PREFIXES = ("EVIDENCE_VAULT_SMOKE", "IMPERIUM_EVIDENCE_VAULT_SMOKE", "INTELLIGENCE_PACK_SMOKE")
PASSPORT_ROOT = "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/PASSPORTS"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(repo: Path, args: Sequence[str], *, ok_empty: bool = False) -> str:
    cp = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if cp.returncode != 0:
        if ok_empty:
            return ""
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or f"git {' '.join(args)} failed")
    return cp.stdout


def git_files(repo: Path) -> List[str]:
    out = run_git(repo, ["ls-files", "-z"])
    return [p.replace("\\", "/") for p in out.split("\0") if p]


def git_head(repo: Path) -> str:
    return run_git(repo, ["rev-parse", "HEAD"]).strip()


def git_branch(repo: Path) -> str:
    return run_git(repo, ["branch", "--show-current"], ok_empty=True).strip() or "DETACHED"


def kind_for(path: str) -> str:
    ext = Path(path).suffix.lower()
    lower = path.lower()
    if ext in ARCHIVE_EXTS or lower.endswith(".trace.zip") or lower.endswith(".har"):
        return "binary_or_archive"
    if ext in IMAGE_EXTS:
        return "binary_or_archive"
    if ext in CODE_EXTS:
        return "code"
    if ext in DOC_EXTS:
        return "document"
    if ext in DATA_EXTS:
        return "data_index"
    if not ext:
        return "no_extension"
    return "other"


def organ_for(path: str) -> str:
    parts = path.split("/")
    if not parts:
        return "ROOT"
    if parts[0] == "ORGANS" and len(parts) > 1:
        return parts[1]
    if parts[0] == "REPORTS":
        return "REPORTS_LEGACY"
    if parts[0].startswith("_"):
        return parts[0]
    if parts[0] in {"SUPPORT", "AGENTS", "DATA_ATLAS", "MECHANICUS", "INQUISITION"}:
        return parts[0]
    return "ROOT"


def has_runtime_marker(path: str) -> bool:
    lower = path.lower().replace("\\", "/")
    parts = set(lower.split("/"))
    if parts & {p.lower() for p in RUNTIME_PARTS}:
        return True
    return lower.endswith(".pyc") or lower.endswith(".pyo") or lower.endswith(".trace.zip") or lower.endswith(".har")


def is_local_only(path: str) -> bool:
    norm = path.replace("\\", "/")
    if norm.startswith(LOCAL_ONLY_PREFIXES):
        return True
    first = norm.split("/", 1)[0]
    return any(first.startswith(prefix) for prefix in SMOKE_ROOT_PREFIXES)


def looks_like_fixture(path: str) -> bool:
    lower = path.lower()
    tokens = ("fixture", "fixtures", "smoke_harness", "smoke_taskpack", "sample", "samples", "example", "examples", "testdata", "golden")
    return any(t in lower for t in tokens)


def looks_like_tool(path: str, kind: str) -> bool:
    if kind != "code":
        return False
    lower = path.lower()
    if not path.startswith("ORGANS/"):
        return False
    if "/reporting/" in lower or "/evidence_vault/" in lower or "/intelligence_pack/" in lower or "/tool_intelligence/" in lower:
        return True
    if lower.endswith(".py") or lower.endswith(".ps1"):
        return True
    return False


def iter_json_values(obj: Any) -> Iterable[Any]:
    if isinstance(obj, dict):
        for v in obj.values():
            yield v
            yield from iter_json_values(v)
    elif isinstance(obj, list):
        for v in obj:
            yield v
            yield from iter_json_values(v)


def collect_passported_paths(repo: Path) -> Set[str]:
    paths: Set[str] = set()
    root = repo / PASSPORT_ROOT
    if not root.exists():
        return paths
    for file in root.rglob("*.json"):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            continue
        for val in iter_json_values(data):
            if isinstance(val, str) and (val.startswith("ORGANS/") or val.startswith("SUPPORT/") or val.startswith("AGENTS")):
                norm = val.replace("\\", "/").strip("/")
                if "." in Path(norm).name or norm.endswith(".py") or norm.endswith(".ps1"):
                    paths.add(norm)
    return paths


def classify(path: str, passported: Set[str]) -> Dict[str, Any]:
    kind = kind_for(path)
    organ = organ_for(path)
    reasons: List[str] = []
    tags: List[str] = []
    lane = "KEEP_SOURCE"
    severity = "INFO"
    action = "Keep in source; no immediate hygiene action."

    if is_local_only(path):
        lane = "SAFE_RUNTIME_DELETE"
        severity = "CRITICAL"
        reasons.append("root-local-only zone is tracked")
        action = "Remove from git tracking; keep local copy only if operator needs it."
    elif has_runtime_marker(path):
        lane = "SAFE_RUNTIME_DELETE"
        severity = "HIGH"
        reasons.append("tracked runtime/cache/test artifact")
        action = "Owner-approved git rm --cached/remove if not required as fixture."
    elif organ == "REPORTS_LEGACY":
        if looks_like_fixture(path):
            lane = "FIXTURE_MANIFEST_REQUIRED"
            severity = "MEDIUM"
            reasons.append("legacy report fixture/source sample requires explicit source exception")
            action = "Add fixture manifest/source exception or migrate report evidence to Evidence Vault."
        else:
            lane = "PACK_TO_VAULT_CANDIDATE"
            severity = "MEDIUM"
            reasons.append("legacy report/evidence should be packed or indexed outside source")
            action = "Plan Evidence Vault pack/copy first; do not delete source without owner gate."
    elif kind == "binary_or_archive":
        if looks_like_fixture(path):
            lane = "FIXTURE_MANIFEST_REQUIRED"
            severity = "MEDIUM"
            reasons.append("binary/archive fixture requires manifest/source exception")
            action = "Create fixture manifest and explicit Data Atlas exception."
        else:
            lane = "PACK_TO_VAULT_CANDIDATE"
            severity = "HIGH"
            reasons.append("binary/archive asset in source requires vault/review lane")
            action = "Pack/copy to Evidence Vault or mark as canonical source asset with manifest."
    elif looks_like_tool(path, kind) and path not in passported:
        lane = "PASSPORT_REQUIRED"
        severity = "MEDIUM"
        reasons.append("tool-like source path missing Mechanicus passport coverage")
        action = "Add/extend Mechanicus tool passport with owner, safety, write scope and validation recipe."
    elif organ == "ROOT" and kind not in {"document", "data_index", "code", "no_extension"}:
        lane = "OWNER_REVIEW_MOVE"
        severity = "LOW"
        reasons.append("root file outside known organ/source convention")
        action = "Owner review: move into organ, support, or evidence lane."

    if looks_like_fixture(path):
        tags.append("fixture_like")
    if kind == "binary_or_archive":
        tags.append("binary_or_archive")
    if path.startswith("ORGANS/"):
        tags.append("organ_source_tree")
    if organ == "REPORTS_LEGACY":
        tags.append("legacy_reports")

    return {
        "path": path,
        "organ": organ,
        "file_kind": kind,
        "lane": lane,
        "severity": severity,
        "reasons": reasons or ["classified by default source policy"],
        "tags": tags,
        "recommended_action": action,
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["lane", "severity", "organ", "file_kind", "path", "recommended_action"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for row in rows:
            wr.writerow({k: row.get(k, "") for k in cols})


def build_sqlite(path: Path, manifest: Dict[str, Any], rows: List[Dict[str, Any]]) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    try:
        con.execute("CREATE TABLE manifest(key TEXT PRIMARY KEY, value TEXT)")
        con.execute("CREATE TABLE files(path TEXT PRIMARY KEY, organ TEXT, file_kind TEXT, lane TEXT, severity TEXT, recommended_action TEXT)")
        con.execute("CREATE TABLE lane_counts(lane TEXT PRIMARY KEY, count INTEGER)")
        con.execute("CREATE TABLE organ_lane_counts(organ TEXT, lane TEXT, count INTEGER, PRIMARY KEY(organ,lane))")
        for k, v in manifest.items():
            con.execute("INSERT INTO manifest(key,value) VALUES (?,?)", (k, json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)))
        for row in rows:
            con.execute("INSERT INTO files(path,organ,file_kind,lane,severity,recommended_action) VALUES (?,?,?,?,?,?)", (
                row["path"], row["organ"], row["file_kind"], row["lane"], row["severity"], row["recommended_action"]
            ))
        for lane, count in Counter(r["lane"] for r in rows).items():
            con.execute("INSERT INTO lane_counts(lane,count) VALUES (?,?)", (lane, count))
        c = Counter((r["organ"], r["lane"]) for r in rows)
        for (organ, lane), count in c.items():
            con.execute("INSERT INTO organ_lane_counts(organ,lane,count) VALUES (?,?,?)", (organ, lane, count))
        con.commit()
    finally:
        con.close()


def owner_board(report: Dict[str, Any]) -> str:
    lc = report["lane_counts"]
    oc = report["organ_review_counts"]
    lines = []
    lines.append(f"# Repo Hygiene Board — {report['patch_id']}")
    lines.append("")
    lines.append("Назначение: начать борьбу с грязью через lanes, а не через слепое удаление.")
    lines.append("")
    lines.append("## Итог")
    lines.append(f"- Status: {report['status']}")
    lines.append(f"- Source HEAD: `{report['source_head_short']}`")
    lines.append(f"- Files classified: {report['files_total']}")
    lines.append(f"- Review/action candidates: {report['action_required_total']}")
    lines.append(f"- Output SQLite: `REPO_HYGIENE_INDEX.sqlite`")
    lines.append("")
    lines.append("## Lanes")
    for lane in sorted(lc):
        lines.append(f"- {lane}: {lc[lane]}")
    lines.append("")
    lines.append("## Органы с review/action")
    for organ, count in sorted(oc.items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
        lines.append(f"- {organ}: {count}")
    lines.append("")
    lines.append("## Правило")
    lines.append("Никакого удаления source evidence без lane, evidence pack/manifest и owner gate. Первый проход только классифицирует и строит очереди.")
    return "\n".join(lines) + "\n"


def build(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    out_root = Path(args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    files = git_files(repo)
    head = git_head(repo)
    branch = git_branch(repo)
    passported = collect_passported_paths(repo)
    rows = [classify(p, passported) for p in files]

    lane_counts = dict(sorted(Counter(r["lane"] for r in rows).items()))
    severity_counts = dict(sorted(Counter(r["severity"] for r in rows).items()))
    file_kind_counts = dict(sorted(Counter(r["file_kind"] for r in rows).items()))
    organ_counts = dict(sorted(Counter(r["organ"] for r in rows).items()))
    organ_review_counts = Counter(r["organ"] for r in rows if r["lane"] != "KEEP_SOURCE")
    action_required = [r for r in rows if r["lane"] != "KEEP_SOURCE"]

    report = {
        "schema": SCHEMA,
        "surface": SURFACE,
        "version": VERSION,
        "status": "PASS_REPO_HYGIENE_CLASSIFIED",
        "generated_at_utc": utc_now(),
        "repo": str(repo),
        "source_head": head,
        "source_head_short": head[:12],
        "source_branch": branch,
        "patch_id": args.patch_id,
        "mode": "read_only_classification",
        "files_total": len(files),
        "action_required_total": len(action_required),
        "lane_counts": lane_counts,
        "severity_counts": severity_counts,
        "file_kind_counts": file_kind_counts,
        "organ_counts": organ_counts,
        "organ_review_counts": dict(sorted(organ_review_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "registered_tool_paths_total": len(passported),
        "lanes": {
            "KEEP_SOURCE": "No action required now.",
            "PASSPORT_REQUIRED": "Tool-like source needs Mechanicus passport coverage.",
            "PACK_TO_VAULT_CANDIDATE": "Evidence/report/archive candidate for Evidence Vault pack/copy before cleanup.",
            "FIXTURE_MANIFEST_REQUIRED": "Fixture/source exception must be explicit before keeping in source.",
            "OWNER_REVIEW_MOVE": "Human review required before moving/reclassifying.",
            "SAFE_RUNTIME_DELETE": "Tracked runtime/local-only artifact candidate for safe delete after owner gate."
        },
        "samples": {
            lane: [r for r in action_required if r["lane"] == lane][: int(args.max_samples_per_lane)]
            for lane in sorted(lane_counts)
            if lane != "KEEP_SOURCE"
        },
        "outputs": {
            "report": str(out_root / "REPO_HYGIENE_CLASSIFICATION_REPORT.json"),
            "owner_board": str(out_root / "OWNER_HYGIENE_BOARD_RU.md"),
            "lane_queue": str(out_root / "HYGIENE_LANE_QUEUE.jsonl"),
            "lane_counts": str(out_root / "HYGIENE_LANE_COUNTS.json"),
            "sqlite_index": str(out_root / "REPO_HYGIENE_INDEX.sqlite"),
        },
        "recommended_next_action_ru": "Review lane queues; create Batch 001 owner gate before moving/deleting/packing any source files."
    }

    write_json(out_root / "REPO_HYGIENE_CLASSIFICATION_REPORT.json", report)
    write_json(out_root / "LATEST_REPO_HYGIENE_REPORT.json", report)
    write_json(out_root / "HYGIENE_LANE_COUNTS.json", {
        "lane_counts": lane_counts,
        "severity_counts": severity_counts,
        "file_kind_counts": file_kind_counts,
        "organ_review_counts": report["organ_review_counts"],
    })
    write_jsonl(out_root / "HYGIENE_LANE_QUEUE.jsonl", action_required)
    write_csv(out_root / "HYGIENE_LANE_QUEUE.csv", action_required)
    (out_root / "OWNER_HYGIENE_BOARD_RU.md").write_text(owner_board(report), encoding="utf-8")
    build_sqlite(out_root / "REPO_HYGIENE_INDEX.sqlite", report, rows)
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Classify repo hygiene lanes without mutating source.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--patch-id", default="REPO-HYGIENE-BATCH-001")
    ap.add_argument("--max-samples-per-lane", type=int, default=20)
    args = ap.parse_args(argv)
    report = build(args)
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
