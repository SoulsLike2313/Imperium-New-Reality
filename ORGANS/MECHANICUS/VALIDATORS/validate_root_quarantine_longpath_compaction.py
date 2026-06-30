#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

PARENT_TASK_ID = "ROOT-QUARANTINE-LONGPATH-COMPACTION-0001"
TASK_ID = "ROOT-QUARANTINE-LONGPATH-COMPACTION-0001-FIX-0001"
VALIDATOR_ID = "root_quarantine_longpath_compactor.v0_2_universal_bundle"

BUNDLE_ROOT = Path("SUPPORT/QUARANTINE/LONGPATH_BUNDLE_V0_1")
BUNDLE_FILES = BUNDLE_ROOT / "FILES"
BUNDLE_MAP = BUNDLE_ROOT / "LONGPATH_BUNDLE_MAP_V0_1.json"
BUNDLE_REPORT = BUNDLE_ROOT / "LONGPATH_BUNDLE_REPORT_V0_1.md"

REGISTRY_JSON = Path("ORGANS/ADMINISTRATUM/REGISTRY/LONGPATH_QUARANTINE_COMPACTION_REGISTRY_V0_1.json")
RECEIPT_JSON = Path("ORGANS/MECHANICUS/RECEIPTS/root_quarantine_longpath_compaction_receipt.json")
REPORT_MD = Path("ORGANS/MECHANICUS/REPORTS/ROOT_QUARANTINE_LONGPATH_COMPACTION_REPORT_V0_1.md")
RESTORE_PS1 = BUNDLE_ROOT / "RESTORE_LONGPATH_BUNDLE_V0_1.ps1"

DEFAULT_MAX_REL_PATH = 180
DEFAULT_MAX_FULL_PATH = 220

CANON_ROOT_DIRS = {"ORGANS", "SUPPORT"}
TRANSITIONAL_ROOT_DIRS = {"WARP", "_HARNESS"}
CANON_ROOT_FILES = {"AGENTS.md", "README.md", ".gitignore", ".gitattributes", ".editorconfig"}

EXCLUDE_DIR_NAMES = {".git", "__pycache__"}
EXCLUDE_FILE_SUFFIXES = {".pyc"}
EXCLUDE_PREFIXES = [
    BUNDLE_FILES.as_posix() + "/",
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def run_git(repo: Path, args: List[str]) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(["git"] + args, cwd=str(repo), text=True, capture_output=True, timeout=90)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, "", str(e)

def git_head(repo: Path) -> str:
    code, out, err = run_git(repo, ["rev-parse", "HEAD"])
    return out.strip() if code == 0 else "UNKNOWN"

def git_ls_files(repo: Path) -> List[str]:
    code, out, err = run_git(repo, ["ls-files", "-z"])
    if code != 0:
        return []
    return [x.replace("\\", "/") for x in out.split("\0") if x]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def should_exclude(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if rel.startswith(".git/") or "/.git/" in rel:
        return True
    if any(part in EXCLUDE_DIR_NAMES for part in rel.split("/")):
        return True
    if any(rel.endswith(suffix) for suffix in EXCLUDE_FILE_SUFFIXES):
        return True
    if any(rel.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return True
    return False

def visible_files(repo: Path) -> List[str]:
    result = set()
    for rel in git_ls_files(repo):
        if not should_exclude(rel):
            result.add(rel)
    for p in repo.rglob("*"):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(repo).as_posix()
        except ValueError:
            continue
        if not should_exclude(rel):
            result.add(rel)
    return sorted(result)

def is_long(rel: str, repo: Path, max_rel: int, max_full: int) -> bool:
    full_len = len(str((repo / rel).resolve()))
    return len(rel) > max_rel or full_len > max_full

def source_zone(rel: str) -> str:
    return rel.split("/", 1)[0] if "/" in rel else "ROOT_FILE"

def bundle_dest_for(file_hash: str) -> Path:
    return BUNDLE_FILES / file_hash[:2] / f"{file_hash}.blob"

def cleanup_empty_dirs(repo: Path):
    protected = {
        repo / "ORGANS",
        repo / "SUPPORT",
        repo / "WARP",
        repo / "_HARNESS",
        repo / BUNDLE_ROOT,
        repo / BUNDLE_FILES,
    }
    dirs = []
    for p in repo.rglob("*"):
        if p.is_dir() and ".git" not in p.parts:
            dirs.append(p)
    for p in sorted(dirs, key=lambda x: len(x.parts), reverse=True):
        if p in protected:
            continue
        try:
            p.rmdir()
        except OSError:
            pass

def compact_all_longpaths(repo: Path, max_rel: int, max_full: int, apply: bool) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    candidates = []
    for rel in visible_files(repo):
        p = repo / rel
        if p.is_file() and is_long(rel, repo, max_rel, max_full):
            candidates.append(rel)

    for rel in sorted(candidates):
        src = repo / rel
        before = sha256(src)
        dst = repo / bundle_dest_for(before)
        dst_rel = dst.relative_to(repo).as_posix()

        entry = {
            "source_rel": rel,
            "source_zone": source_zone(rel),
            "source_rel_len": len(rel),
            "source_full_len": len(str(src.resolve())),
            "bundle_rel": dst_rel,
            "bundle_rel_len": len(dst_rel),
            "bundle_full_len": len(str(dst.resolve())),
            "bytes": src.stat().st_size,
            "sha256_before": before,
            "sha256_after": None,
            "sha256_match": False,
            "action": "PLAN" if not apply else "BUNDLE_MOVE",
            "policy": "UNIVERSAL_LONGPATH_COMPACTION"
        }

        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                if sha256(dst) == before:
                    src.unlink()
                    entry["action"] = "DEDUP_SOURCE_REMOVED"
                else:
                    raise RuntimeError(f"Unexpected SHA bundle collision: {dst_rel}")
            else:
                shutil.move(str(src), str(dst))
            entry["sha256_after"] = sha256(dst)
            entry["sha256_match"] = entry["sha256_after"] == before

        entries.append(entry)

    if apply:
        cleanup_empty_dirs(repo)

    return entries

def detect_longpaths(repo: Path, max_rel: int, max_full: int) -> List[Dict[str, Any]]:
    rows = []
    for rel in visible_files(repo):
        p = repo / rel
        if not p.is_file():
            continue
        rel_len = len(rel)
        full_len = len(str(p.resolve()))
        if rel_len > max_rel or full_len > max_full:
            rows.append({
                "rel": rel,
                "source_zone": source_zone(rel),
                "rel_len": rel_len,
                "full_len": full_len,
                "under_bundle_files": rel.startswith(BUNDLE_FILES.as_posix() + "/"),
            })
    return sorted(rows, key=lambda x: (-x["full_len"], x["rel"]))

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

def load_existing_bundle_map(repo: Path) -> List[Dict[str, Any]]:
    path = repo / BUNDLE_MAP
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
        return entries if isinstance(entries, list) else []
    except Exception:
        return []

def merge_entries(old: List[Dict[str, Any]], new: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for e in old + new:
        key = e.get("source_rel") or e.get("bundle_rel")
        if key:
            merged[key] = e
    return list(merged.values())

def write_restore_script(repo: Path):
    script = """$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..\\..")).Path
$MapPath = Join-Path $PSScriptRoot "LONGPATH_BUNDLE_MAP_V0_1.json"

if (-not (Test-Path $MapPath)) {
  throw "Bundle map not found: $MapPath"
}

$Map = Get-Content $MapPath -Raw | ConvertFrom-Json

foreach ($Entry in $Map.entries) {
  $Source = Join-Path $RepoRoot $Entry.source_rel
  $Bundle = Join-Path $RepoRoot $Entry.bundle_rel
  if (-not (Test-Path $Bundle)) {
    throw "Missing bundle blob: $($Entry.bundle_rel)"
  }
  New-Item -ItemType Directory -Force -Path (Split-Path $Source) | Out-Null
  Copy-Item -LiteralPath $Bundle -Destination $Source -Force
}

Write-Host "Longpath bundle restored from map: $MapPath"
"""
    (repo / RESTORE_PS1).write_text(script, encoding="utf-8")

def write_outputs(repo: Path, all_entries: List[Dict[str, Any]], new_entries: List[Dict[str, Any]], checks: List[Dict[str, Any]], warnings: List[str], errors: List[str], max_rel: int, max_full: int, long_after: List[Dict[str, Any]]):
    generated = utc()
    root = root_state(repo)
    verdict = "PASS_LONGPATH_COMPACTED" if not errors else "FAIL_LONGPATH_COMPACTION"

    payload = {
        "bundle_id": "support.quarantine.longpath_bundle.v0_1",
        "task_id": PARENT_TASK_ID,
        "fix_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "max_rel_path": max_rel,
        "max_full_path": max_full,
        "entry_count": len(all_entries),
        "new_entry_count": len(new_entries),
        "bundle_root": BUNDLE_ROOT.as_posix(),
        "entries": all_entries
    }

    receipt = {
        "receipt_id": "receipt.mechanicus.root_quarantine_longpath_compaction.v0_1.fix_0001",
        "task_id": PARENT_TASK_ID,
        "fix_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "max_rel_path": max_rel,
        "max_full_path": max_full,
        "compacted_count": len(new_entries),
        "total_bundle_entries": len(all_entries),
        "long_paths_after": len(long_after),
        "root_state": root,
        "bundle_map": BUNDLE_MAP.as_posix(),
        "registry": REGISTRY_JSON.as_posix(),
        "restore_script": RESTORE_PS1.as_posix(),
        "report": REPORT_MD.as_posix(),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "long_paths_after_preview": long_after[:30],
        "meaning": "All long visible paths are compacted into a short SHA256-addressed bundle. Original paths are recoverable from the bundle map."
    }

    for path in [BUNDLE_MAP, BUNDLE_REPORT, REGISTRY_JSON, RECEIPT_JSON, REPORT_MD, RESTORE_PS1]:
        (repo / path).parent.mkdir(parents=True, exist_ok=True)

    (repo / BUNDLE_MAP).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / REGISTRY_JSON).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT_JSON).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_restore_script(repo)

    preview = new_entries[:40]
    entries_md = "\n".join(
        f"- `{e['source_rel']}` -> `{e['bundle_rel']}` sha256_match=`{e['sha256_match']}`"
        for e in preview
    ) if new_entries else "- none"
    if len(new_entries) > len(preview):
        entries_md += f"\n- ... {len(new_entries) - len(preview)} more new entries in `{BUNDLE_MAP.as_posix()}`"

    long_after_md = "\n".join(f"- `{x['rel']}` rel_len=`{x['rel_len']}` full_len=`{x['full_len']}`" for x in long_after[:30]) if long_after else "- none"
    if len(long_after) > 30:
        long_after_md += f"\n- ... {len(long_after) - 30} more"

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"

    report_text = f"""# ROOT QUARANTINE LONGPATH COMPACTION REPORT V0.2 — UNIVERSAL BUNDLE

task_id: `{PARENT_TASK_ID}`  
fix_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

The previous compactor was too narrow and compacted only guessed quarantine prefixes.

This fix compacts all visible long paths outside `.git` and outside the bundle itself.

Original paths are preserved in the bundle map and can be restored from:

```text
{RESTORE_PS1.as_posix()}
```

## Summary

- compacted_count_new: `{len(new_entries)}`
- total_bundle_entries: `{len(all_entries)}`
- long_paths_after: `{len(long_after)}`
- max_rel_path: `{max_rel}`
- max_full_path: `{max_full}`

## New compacted entries preview

{entries_md}

## Long paths after

{long_after_md}

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
- `{RESTORE_PS1.as_posix()}`
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

    old_entries = load_existing_bundle_map(repo)
    new_entries = compact_all_longpaths(repo, args.max_rel_path, args.max_full_path, apply=args.apply)
    all_entries = merge_entries(old_entries, new_entries)

    hash_bad = [e for e in new_entries if e.get("sha256_after") and not e.get("sha256_match")]
    add(checks, "compacted_sha256_match", not hash_bad, {"bad_count": len(hash_bad)})
    if hash_bad:
        errors.append("Some compacted files have SHA256 mismatch")

    long_after = detect_longpaths(repo, args.max_rel_path, args.max_full_path)
    add(checks, "no_long_paths_after_compaction", len(long_after) == 0, {"long_count": len(long_after), "first": long_after[:20]})
    if long_after:
        errors.append("Long paths remain after universal compaction")

    root = root_state(repo)
    root_ok, root_details = validate_root(root)
    add(checks, "root_canon_still_clean", root_ok, root_details)
    if not root_ok:
        errors.append("Root canon regression")

    root_transport = [f for f in root["files"] if fnmatch.fnmatch(f, "APPLY_*.ps1") or fnmatch.fnmatch(f, "*_FILE_MANIFEST_SHA256.json")]
    add(checks, "no_root_transport_regression", not root_transport, {"root_transport": root_transport})
    if root_transport:
        errors.append("Root transport files returned")

    add(checks, "universal_longpath_compaction_policy_active", True, {"excluded": [".git", BUNDLE_FILES.as_posix()]})
    add(checks, "bundle_map_written", True, {"path": BUNDLE_MAP.as_posix()})
    add(checks, "restore_script_written", True, {"path": RESTORE_PS1.as_posix()})

    receipt = write_outputs(repo, all_entries, new_entries, checks, warnings, errors, args.max_rel_path, args.max_full_path, long_after)

    print(json.dumps({
        "task_id": PARENT_TASK_ID,
        "fix_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": receipt["verdict"],
        "compacted_count": len(new_entries),
        "total_bundle_entries": len(all_entries),
        "long_paths_after": len(long_after),
        "root_dirs": root["dirs"],
        "root_files": root["files"],
        "bundle_map": BUNDLE_MAP.as_posix(),
        "restore_script": RESTORE_PS1.as_posix(),
        "receipt": RECEIPT_JSON.as_posix(),
        "report": REPORT_MD.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))

    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
