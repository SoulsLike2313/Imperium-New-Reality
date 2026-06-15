#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inquisition Evidence Migration Planner V0.1.

Read-only by default. Scans source repo for evidence/archive/cache spillover and
produces migration lanes for Evidence Vault adoption.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

SURFACE = "INQUISITION_EVIDENCE_MIGRATION_PLANNER_V0_1"
VERSION = "0.1.0"

IGNORE_DIR_NAMES = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
}
ARCHIVE_EXTS = (".zip", ".7z", ".rar", ".tar", ".tgz", ".gz")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")
EVIDENCE_EXTS = IMAGE_EXTS + (".html", ".har")
SPECIAL_EVIDENCE_SUFFIXES = (".trace.zip",)

@dataclass
class MigrationItem:
    item_id: str
    path: str
    storage_zone: str
    risk_type: str
    migration_lane: str
    confidence: str
    proposed_action: str
    reason: str
    source_allowed: bool
    vault_pack_group: str
    suggested_vault_path: str
    size_bytes: int
    mtime_utc: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def stable_id(text: str) -> str:
    return "MIG-" + hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:12]


def file_mtime_utc(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except OSError:
        return ""


def is_special_suffix(name_lower: str, suffixes: Tuple[str, ...]) -> bool:
    return any(name_lower.endswith(s) for s in suffixes)


def iter_source_files(repo_root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(repo_root):
        current_path = Path(current)
        rel_parts = current_path.relative_to(repo_root).parts if current_path != repo_root else ()
        # prune known non-source/runtime dirs inside repo
        dirs[:] = [d for d in dirs if d not in IGNORE_DIR_NAMES]
        if any(part in {".git", "node_modules", ".venv", "venv"} for part in rel_parts):
            continue
        for name in files:
            yield current_path / name


def detect_risk(path: Path, rel: str) -> Optional[str]:
    rel_u = "/" + rel.replace("\\", "/")
    name = path.name.lower()
    lower = rel.lower()
    if name.endswith(".pyc") or "/__pycache__/" in lower or "/.pytest_cache/" in lower:
        return "SOURCE_RUNTIME_CACHE"
    if is_special_suffix(name, SPECIAL_EVIDENCE_SUFFIXES):
        return "SOURCE_EVIDENCE_LEAK"
    if name.endswith(ARCHIVE_EXTS):
        return "SOURCE_ARCHIVE_REVIEW"
    if name.endswith(EVIDENCE_EXTS):
        # Ignore common docs pages? Keep conservative: report/html/screenshots are evidence-like.
        if "/docs/" in lower and not any(x in lower for x in ["screenshot", "capture", "report", "evidence"]):
            return None
        return "SOURCE_EVIDENCE_LEAK"
    if any(x in lower for x in ["playwright-report/", "test-results/"]):
        return "SOURCE_EVIDENCE_LEAK"
    return None


def classify(path: Path, rel: str, risk_type: str, vault_root: Path) -> Tuple[str, str, str, bool, str, str]:
    lower = "/" + rel.lower().replace("\\", "/")
    rel_parts = rel.split("/")
    top = rel_parts[0] if rel_parts else "ROOT"

    if risk_type == "SOURCE_RUNTIME_CACHE":
        return (
            "SAFE_CACHE_DELETE",
            "HIGH",
            "Delete by explicit safe-cache cleanup gate; do not pack.",
            False,
            "source_cache",
            "Runtime cache has no source truth value."
        )

    if risk_type == "SOURCE_ARCHIVE_REVIEW":
        if any(marker in lower for marker in ["/fixtures/", "/fixture_zips/", "/tests/fixtures/"]):
            return (
                "FIXTURE_ALLOWED_NEEDS_MANIFEST",
                "MEDIUM",
                "Keep only if fixture manifest/source exception is added; otherwise move to Vault.",
                False,
                f"fixture_archives/{top}",
                "Archive appears to support tests/fixtures but lacks lifecycle manifest."
            )
        if "/task_inbox/registered/" in lower:
            return (
                "OWNER_REVIEW_CLASSIFY",
                "MEDIUM",
                "Classify as registry payload, canonical taskpack, or migrate sealed copy to Vault.",
                False,
                f"taskpack_registry/{top}",
                "Registered taskpack archive may be canonical but still needs storage lifecycle decision."
            )
        if "/continuity/packs/" in lower or "/reports/" in lower:
            return (
                "PACK_TO_VAULT_CANDIDATE",
                "HIGH",
                "Seal into Evidence Vault pack, index in Data Atlas, then remove raw/archive from source by owner-reviewed patch.",
                False,
                f"historical_reports/{top}",
                "Report/continuity archive is evidence, not active source."
            )
        return (
            "OWNER_REVIEW_CLASSIFY",
            "MEDIUM",
            "Classify lifecycle before move/delete.",
            False,
            f"archives/{top}",
            "Archive under source tree hides contents from normal source review."
        )

    if risk_type == "SOURCE_EVIDENCE_LEAK":
        if any(marker in lower for marker in ["/fixtures/", "/fixture", "/assets/", "/static/"]):
            return (
                "KEEP_SOURCE_REGISTER_FIXTURE",
                "MEDIUM",
                "Keep only if registered as fixture/source asset in Data Atlas.",
                True,
                f"source_assets/{top}",
                "Image/html may be a fixture or source asset; requires explicit registration."
            )
        if any(marker in lower for marker in ["/reports/", "/captures/", "/screenshots/", "/evidence/", "/playwright-report/", "/test-results/"]):
            return (
                "PACK_TO_VAULT_CANDIDATE",
                "HIGH",
                "Move to Evidence Vault pack; source keeps only manifest/reference if needed.",
                False,
                f"source_evidence/{top}",
                "Report/screenshot/evidence output should not live as raw source file."
            )
        return (
            "OWNER_REVIEW_MOVE",
            "MEDIUM",
            "Review whether this is source asset or leaked evidence; move to Vault unless source asset is declared.",
            False,
            f"uncategorized_evidence/{top}",
            "Evidence-like file in source needs explicit lifecycle."
        )

    return (
        "OWNER_REVIEW_CLASSIFY",
        "LOW",
        "Classify lifecycle before action.",
        False,
        "unclassified",
        "Fallback classification."
    )


def suggested_vault_path(vault_root: Path, group: str, rel: str) -> str:
    safe_rel_name = rel.replace(":", "_").replace("\\", "/")
    return str((vault_root / "packs" / "migration_candidates" / group / safe_rel_name).as_posix())


def scan(repo_root: Path, vault_root: Path) -> List[MigrationItem]:
    items: List[MigrationItem] = []
    for path in iter_source_files(repo_root):
        try:
            rel = safe_rel(path, repo_root)
        except Exception:
            continue
        risk = detect_risk(path, rel)
        if not risk:
            continue
        lane, confidence, action, source_allowed, group, reason = classify(path, rel, risk, vault_root)
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        items.append(MigrationItem(
            item_id=stable_id(rel),
            path=rel,
            storage_zone="SOURCE_REPO",
            risk_type=risk,
            migration_lane=lane,
            confidence=confidence,
            proposed_action=action,
            reason=reason,
            source_allowed=source_allowed,
            vault_pack_group=group,
            suggested_vault_path=suggested_vault_path(vault_root, group, rel),
            size_bytes=size,
            mtime_utc=file_mtime_utc(path),
        ))
    return sorted(items, key=lambda x: (x.migration_lane, x.risk_type, x.path))


def counts(items: List[MigrationItem], attr: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for item in items:
        key = getattr(item, attr)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_counts_csv(path: Path, data: Dict[str, int], key_name: str) -> None:
    write_csv(path, [{key_name: k, "count": v} for k, v in data.items()], [key_name, "count"])


def owner_report(report: dict) -> str:
    lines = [
        "# Inquisition Evidence Migration Planner V0.1",
        "",
        f"Status: **{report['status']}**",
        f"Generated: `{report['generated_at_utc']}`",
        f"Repo: `{report['repo_root']}`",
        "",
        "## Summary",
        "",
    ]
    for k, v in report["summary"].items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## Migration lanes", ""]
    for k, v in report["migration_lane_counts"].items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## Risk counts", ""]
    for k, v in report["risk_counts"].items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## First recommendations", "",
        "- Do not delete source archives/evidence automatically.",
        "- First pack high-confidence report/evidence outputs into Evidence Vault.",
        "- Add fixture manifests for fixture archives/assets that must remain in source.",
        "- Safe-cache-delete lane may be executed by separate explicit gate.",
        "- Feed PACK_TO_VAULT_CANDIDATE and OWNER_REVIEW_MOVE lanes into Data Atlas cards.",
        "", "## Sample", ""]
    for item in report["sample"][:30]:
        lines.append(f"- **{item['migration_lane']} · {item['risk_type']}** `{item['path']}` — {item['proposed_action']}")
    lines.append("")
    return "\n".join(lines)


def execute_safe_cache_delete(items: List[MigrationItem], repo_root: Path) -> List[str]:
    actions: List[str] = []
    for item in items:
        if item.migration_lane != "SAFE_CACHE_DELETE":
            continue
        target = (repo_root / item.path).resolve()
        try:
            if not str(target).startswith(str(repo_root.resolve())):
                continue
            if target.is_file() and (target.name.endswith(".pyc") or "__pycache__" in target.parts):
                target.unlink(missing_ok=True)
                actions.append(f"deleted_file:{item.path}")
            elif target.is_dir() and target.name in {"__pycache__", ".pytest_cache"}:
                shutil.rmtree(target, ignore_errors=True)
                actions.append(f"deleted_dir:{item.path}")
        except Exception as exc:
            actions.append(f"failed:{item.path}:{exc}")
    return actions


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--vault-root", default="E:/IMPERIUM_EVIDENCE_VAULT")
    ap.add_argument("--out-root", default="E:/_LOCAL_HANDOFF/SERVITOR_OUTPUTS")
    ap.add_argument("--execute-safe-cache-delete", action="store_true")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    vault_root = Path(args.vault_root).resolve()
    out_root = Path(args.out_root).resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_root = out_root / f"INQUISITION_EVIDENCE_MIGRATION_PLAN_{stamp}"
    output_root.mkdir(parents=True, exist_ok=True)

    items = scan(repo_root, vault_root)
    actions: List[str] = []
    if args.execute_safe_cache_delete:
        actions = execute_safe_cache_delete(items, repo_root)
        # rescan after cleanup
        items = scan(repo_root, vault_root)

    lane_counts = counts(items, "migration_lane")
    risk_counts = counts(items, "risk_type")
    group_counts = counts(items, "vault_pack_group")
    bytes_total = sum(i.size_bytes for i in items)
    pack_candidate_bytes = sum(i.size_bytes for i in items if i.migration_lane == "PACK_TO_VAULT_CANDIDATE")

    summary = {
        "migration_items_total": len(items),
        "risk_types_detected": len(risk_counts),
        "migration_lanes_detected": len(lane_counts),
        "vault_pack_groups_detected": len(group_counts),
        "bytes_total": bytes_total,
        "pack_to_vault_candidate_total": lane_counts.get("PACK_TO_VAULT_CANDIDATE", 0),
        "pack_to_vault_candidate_bytes": pack_candidate_bytes,
        "safe_cache_delete_total": lane_counts.get("SAFE_CACHE_DELETE", 0),
        "fixture_manifest_needed_total": lane_counts.get("FIXTURE_ALLOWED_NEEDS_MANIFEST", 0),
    }
    status = "PASS_WITH_MIGRATION_PLAN" if items else "PASS_NO_MIGRATION_ITEMS"
    report = {
        "status": status,
        "surface": SURFACE,
        "version": VERSION,
        "generated_at_utc": utc_now(),
        "repo_root": str(repo_root),
        "vault_root": str(vault_root),
        "summary": summary,
        "risk_counts": risk_counts,
        "migration_lane_counts": lane_counts,
        "vault_pack_group_counts": group_counts,
        "execute_summary": {"executed_safe_cache_delete": bool(args.execute_safe_cache_delete), "actions": actions},
        "sample": [asdict(i) for i in items[:80]],
        "output_root": str(output_root),
    }

    (output_root / "MACHINE_REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    (output_root / "OWNER_READABLE_REPORT_RU.md").write_text(owner_report(report), encoding="utf-8", newline="\n")
    fieldnames = list(asdict(items[0]).keys()) if items else list(MigrationItem.__dataclass_fields__.keys())
    write_csv(output_root / "migration_plan.csv", [asdict(i) for i in items], fieldnames)
    write_counts_csv(output_root / "risk_counts.csv", risk_counts, "risk_type")
    write_counts_csv(output_root / "migration_lane_counts.csv", lane_counts, "migration_lane")
    write_counts_csv(output_root / "vault_pack_groups.csv", group_counts, "vault_pack_group")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
