#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import fnmatch
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "ROOT-QUARANTINE-LONGPATH-COMPACTION-0001"
VALIDATOR_ID = "root_quarantine_longpath_compactor.v0_1"

BUNDLE_ROOT = Path("SUPPORT/QUARANTINE/LONGPATH_BUNDLE_V0_1")
BUNDLE_FILES = BUNDLE_ROOT / "FILES"
BUNDLE_MAP = BUNDLE_ROOT / "LONGPATH_BUNDLE_MAP_V0_1.json"
BUNDLE_REPORT = BUNDLE_ROOT / "LONGPATH_BUNDLE_REPORT_V0_1.md"

REGISTRY_JSON = Path("ORGANS/ADMINISTRATUM/REGISTRY/LONGPATH_QUARANTINE_COMPACTION_REGISTRY_V0_1.json")
RECEIPT_JSON = Path("ORGANS/MECHANICUS/RECEIPTS/root_quarantine_longpath_compaction_receipt.json")
REPORT_MD = Path("ORGANS/MECHANICUS/REPORTS/ROOT_QUARANTINE_LONGPATH_COMPACTION_REPORT_V0_1.md")

DEFAULT_MAX_REL_PATH = 180
DEFAULT_MAX_FULL_PATH = 220

CANON_ROOT_DIRS = {"ORGANS", "SUPPORT"}
TRANSITIONAL_ROOT_DIRS = {"WARP", "_HARNESS"}
CANON_ROOT_FILES = {"AGENTS.md", "README.md", ".gitignore", ".gitattributes", ".editorconfig"}

TARGET_PREFIXES = [
    "SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/",
    "SUPPORT/QUARANTINE/ROOT_PATCH_BACKUPS_PENDING_BACKUP_POLICY/",
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def run_git(repo: Path, args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(["git"] + args, cwd=str(repo), text=True, capture_output=True, timeout=90)
    return p.returncode, p.stdout, p.stderr

def git_head(repo: Path) -> str:
    code, out, err = run_git(repo, ["rev-parse", "HEAD"])
    return out.strip() if code == 0 else "UNKNOWN"

def git_ls_files(repo: Path) -> List[str]:
    code, out, err = run_git(repo, ["ls-files"])
    if code != 0:
        return []
    return [x.strip().replace("\\", "/") for x in out.splitlines() if x.strip()]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def list_visible_files(repo: Path) -> List[str]:
    tracked = set(git_ls_files(repo))
    visible = set(tracked)
    for root in ["ORGANS", "SUPPORT", "WARP", "_HARNESS"]:
        p = repo / root
        if p.exists():
            for f in p.rglob("*"):
                if f.is_file() and "__pycache__" not in f.parts and not f.name.endswith(".pyc"):
                    visible.add(f.relative_to(repo).as_posix())
    for f in repo.iterdir():
        if f.is_file() and f.name != ".git":
            visible.add(f.name)
    return sorted(visible)

def is_target_longpath(rel: str, repo: Path, max_rel: int, max_full: int) -> bool:
    if rel.startswith(BUNDLE_ROOT.as_posix() + "/"):
        return False
    if not any(rel.startswith(prefix) for prefix in TARGET_PREFIXES):
        return False
    full_len = len(str((repo / rel).resolve()))
    return len(rel) > max_rel or full_len > max_full

def bundle_dest_for(rel: str, file_hash: str) -> Path:
    # Very short deterministic path; original path lives only in JSON map.
    return BUNDLE_FILES / file_hash[:2] / f"{file_hash}.blob"

def compact(repo: Path, max_rel: int, max_full: int, apply: bool) -> List[Dict[str, Any]]:
    files = list_visible_files(repo)
    candidates = [rel for rel in files if (repo / rel).is_file() and is_target_longpath(rel, repo, max_rel, max_full)]
    entries: List[Dict[str, Any]] = []

    for rel in candidates:
        src = repo / rel
        before = sha256(src)
        dst_rel = bundle_dest_for(rel, before).as_posix()
        dst = repo / dst_rel

        entry = {
            "source_rel": rel,
            "source_rel_len": len(rel),
            "source_full_len": len(str(src.resolve())),
            "bundle_rel": dst_rel,
            "bundle_rel_len": len(dst_rel),
            "bundle_full_len": len(str(dst.resolve())),
            "bytes": src.stat().st_size,
            "sha256_before": before,
            "sha256_after": None,
            "sha256_match": False,
            "action": "PLAN" if not apply else "BUNDLE_MOVE"
        }

        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                if sha256(dst) == before:
                    src.unlink()
                    entry["action"] = "DEDUP_SOURCE_REMOVED"
                else:
                    # SHA collision should be impossible, but keep deterministic error evidence.
                    raise RuntimeError(f"Bundle destination collision with different hash: {dst_rel}")
            else:
                shutil.move(str(src), str(dst))
            entry["sha256_after"] = sha256(dst)
            entry["sha256_match"] = entry["sha256_after"] == before

        entries.append(entry)

    if apply:
        # remove empty directories under old quarantine branches
        for prefix in TARGET_PREFIXES:
            root = repo / prefix
            if root.exists():
                for d in sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda p: len(p.parts), reverse=True):
                    try:
                        d.rmdir()
                    except OSError:
                        pass
                try:
                    root.rmdir()
                except OSError:
                    pass

    return entries

def detect_longpaths(repo: Path, max_rel: int, max_full: int) -> List[Dict[str, Any]]:
    out = []
    for rel in list_visible_files(repo):
        p = repo / rel
        if not p.is_file():
            continue
        rel_len = len(rel)
        full_len = len(str(p.resolve()))
        if rel_len > max_rel or full_len > max_full:
            out.append({
                "rel": rel,
                "rel_len": rel_len,
                "full_len": full_len,
                "under_target_quarantine": any(rel.startswith(prefix) for prefix in TARGET_PREFIXES),
                "under_bundle": rel.startswith(BUNDLE_ROOT.as_posix() + "/")
            })
    return sorted(out, key=lambda x: (-x["full_len"], x["rel"]))

def root_state(repo: Path) -> Dict[str, Any]:
    dirs, files = [], []
    for p in sorted(repo.iterdir(), key=lambda x: x.name.lower()):
        if p.name == ".git":
            continue
        if p.is_dir():
            dirs.append(p.name)
        elif p.is_file():
            files.append(p.name)
    return {"dirs": dirs, "files": files}

def validate_root(root: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    allowed_dirs = CANON_ROOT_DIRS | TRANSITIONAL_ROOT_DIRS
    bad_dirs = [d for d in root["dirs"] if d not in allowed_dirs]
    bad_files = [f for f in root["files"] if f not in CANON_ROOT_FILES]
    return (not bad_dirs and not bad_files), {"bad_dirs": bad_dirs, "bad_files": bad_files}

def write_outputs(repo: Path, entries: List[Dict[str, Any]], checks: List[Dict[str, Any]], warnings: List[str], errors: List[str], max_rel: int, max_full: int):
    generated = utc()
    root = root_state(repo)
    verdict = "PASS_LONGPATH_COMPACTED" if not errors else "FAIL_LONGPATH_COMPACTION"

    payload = {
        "bundle_id": "support.quarantine.longpath_bundle.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "max_rel_path": max_rel,
        "max_full_path": max_full,
        "entry_count": len(entries),
        "bundle_root": BUNDLE_ROOT.as_posix(),
        "entries": entries
    }

    receipt = {
        "receipt_id": "receipt.mechanicus.root_quarantine_longpath_compaction.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "max_rel_path": max_rel,
        "max_full_path": max_full,
        "compacted_count": len(entries),
        "root_state": root,
        "bundle_map": BUNDLE_MAP.as_posix(),
        "registry": REGISTRY_JSON.as_posix(),
        "report": REPORT_MD.as_posix(),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "meaning": "Long quarantine paths are compacted into a short SHA256-addressed bundle so pre-push long-path gates can pass while original paths remain recoverable from the map."
    }

    for path in [BUNDLE_MAP, BUNDLE_REPORT, REGISTRY_JSON, RECEIPT_JSON, REPORT_MD]:
        (repo / path).parent.mkdir(parents=True, exist_ok=True)

    (repo / BUNDLE_MAP).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / REGISTRY_JSON).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT_JSON).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    preview = entries[:40]
    entries_md = "\n".join(
        f"- `{e['source_rel']}` -> `{e['bundle_rel']}` sha256_match=`{e['sha256_match']}`"
        for e in preview
    ) if entries else "- none"
    if len(entries) > len(preview):
        entries_md += f"\n- ... {len(entries) - len(preview)} more entries in `{BUNDLE_MAP.as_posix()}`"

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"

    report_text = f"""# ROOT QUARANTINE LONGPATH COMPACTION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The previous governance commit was blocked by the pre-push long-path gate.

This patch compacts long quarantine paths into a short SHA256-addressed bundle:

```text
{BUNDLE_ROOT.as_posix()}
```

Original paths are not lost. They are stored in:

```text
{BUNDLE_MAP.as_posix()}
```

## Summary

- compacted_count: `{len(entries)}`
- max_rel_path: `{max_rel}`
- max_full_path: `{max_full}`

## Entries preview

{entries_md}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{BUNDLE_MAP.as_posix()}`
- `{REGISTRY_JSON.as_posix()}`
- `{RECEIPT_JSON.as_posix()}`
"""
    (repo / REPORT_MD).write_text(report_text, encoding="utf-8")
    (repo / BUNDLE_REPORT).write_text(report_text, encoding="utf-8")

    return receipt

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--max-rel-path", type=int, default=DEFAULT_MAX_REL_PATH)
    ap.add_argument("--max-full-path", type=int, default=DEFAULT_MAX_FULL_PATH)
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    checks: List[Dict[str, Any]] = []
    warnings: List[str] = []
    errors: List[str] = []

    entries = compact(repo, args.max_rel_path, args.max_full_path, apply=args.apply)

    hash_bad = [e for e in entries if e.get("sha256_after") and not e.get("sha256_match")]
    add(checks, "compacted_sha256_match", not hash_bad, {"bad_count": len(hash_bad)})
    if hash_bad:
        errors.append("Some compacted files have SHA256 mismatch")

    long_after = detect_longpaths(repo, args.max_rel_path, args.max_full_path)
    # Bundle blob paths are allowed only if still within max full path. They should be short.
    true_long_after = [x for x in long_after if not x.get("under_bundle")]
    bundle_long = [x for x in long_after if x.get("under_bundle")]

    add(checks, "no_non_bundle_long_paths_after_compaction", len(true_long_after) == 0, {"long_count": len(true_long_after), "first": true_long_after[:10]})
    if true_long_after:
        errors.append("Non-bundle long paths remain after compaction")

    add(checks, "bundle_paths_within_limit", len(bundle_long) == 0, {"bundle_long_count": len(bundle_long), "first": bundle_long[:10]})
    if bundle_long:
        errors.append("Bundle paths are still too long")

    root = root_state(repo)
    root_ok, root_details = validate_root(root)
    add(checks, "root_canon_still_clean", root_ok, root_details)
    if not root_ok:
        errors.append("Root canon regression")

    root_transport = [f for f in root["files"] if fnmatch.fnmatch(f, "APPLY_*.ps1") or fnmatch.fnmatch(f, "*_FILE_MANIFEST_SHA256.json")]
    add(checks, "no_root_transport_regression", not root_transport, {"root_transport": root_transport})
    if root_transport:
        errors.append("Root transport files returned")

    add(checks, "bundle_map_written", True, {"path": BUNDLE_MAP.as_posix()})
    add(checks, "compaction_registry_written", True, {"path": REGISTRY_JSON.as_posix()})

    receipt = write_outputs(repo, entries, checks, warnings, errors, args.max_rel_path, args.max_full_path)

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": receipt["verdict"],
        "compacted_count": len(entries),
        "long_paths_after": len(long_after),
        "non_bundle_long_paths_after": len(true_long_after),
        "root_dirs": root["dirs"],
        "root_files": root["files"],
        "bundle_map": BUNDLE_MAP.as_posix(),
        "receipt": RECEIPT_JSON.as_posix(),
        "report": REPORT_MD.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))

    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())

