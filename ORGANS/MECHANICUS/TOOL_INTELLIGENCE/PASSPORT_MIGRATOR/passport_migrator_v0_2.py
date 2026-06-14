#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
passport_migrator_v0_2 (refined classifier)

Mechanicus tool: migrates canonical-shape legacy v0_1 tool-passports to v0_2
in-place (rewrites schema_id, validates required fields). Refuses to guess
missing fields. Now also recognizes meta-schema files by filename prefix
(tool_passport_schema_*, imperium_tool_passport_*, imperium_passport_index_*,
file_passport_schema_*) and routes them to skipped_meta_schema.

For non-canonical legacy passports requiring field-inference, use the sibling
tool passport_v0_2_auto_registrar.

Usage:
    python passport_migrator_v0_2.py --self-test
    python passport_migrator_v0_2.py --repo <repo_root> --out <ledger.json> --dry-run
    python passport_migrator_v0_2.py --repo <repo_root> --out <ledger.json> --apply
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_ID_V0_2 = "imperium.tool_passport.v0_2"
LEDGER_SCHEMA_ID = "imperium.passport_migration_ledger.v0_1"
MIGRATOR_VERSION = "v0_2"
REQUIRED_FIELDS_V0_2 = (
    "tool_id", "name", "version", "owner_organ",
    "lang", "validators", "exec_mode", "owner_gated",
)

_LEGACY_FILE_RE = re.compile(r"^(.+)_tool_passport[s]?_v[0-9_]+\.json$")
_META_SCHEMA_PREFIXES = (
    "tool_passport_schema",
    "imperium_tool_passport",
    "imperium_passport_index",
    "file_passport_schema",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> Optional[dict]:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)
    path.write_bytes(text.encode("utf-8"))


def classify(passport_path: Path, j: Optional[dict]) -> str:
    name = passport_path.name
    name_lower = name.lower()
    posix = passport_path.as_posix()

    if j is None:
        return "parse_error"

    # 1) meta-schema by extension
    if name_lower.endswith(".schema.json"):
        return "skipped_meta_schema"

    # 2) meta-schema by filename prefix (NEW in v0.10.3)
    for stem in _META_SCHEMA_PREFIXES:
        if name_lower.startswith(stem):
            return "skipped_meta_schema"

    # 3) organ block / data atlas
    if "ORGAN_BLOCK_PASSPORT" in name or "/BLOCK/PASSPORT/" in posix:
        return "skipped_not_a_tool_passport"
    if "DATA_ATLAS_PASSPORT" in name or "/DATA_ATLAS/" in posix:
        return "skipped_not_a_tool_passport"

    schema_id = (j.get("schema_id") or "").lower()

    # 4) already v0_2 (canonical)
    if schema_id == SCHEMA_ID_V0_2:
        return "skipped_already_v0_2"

    # 5) explicit v0_1 tool passport by schema_id
    if "tool_passport" in schema_id:
        return "legacy"

    # 6) filename pattern
    if _LEGACY_FILE_RE.match(name):
        return "legacy"

    return "non_compliant"


def _check_required(j: dict) -> List[str]:
    missing: List[str] = []
    for k in REQUIRED_FIELDS_V0_2:
        v = j.get(k)
        if v is None or (isinstance(v, str) and v == "") or (isinstance(v, (list, dict)) and len(v) == 0):
            missing.append(k)
    return missing


def _backup(path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / path.name
    n = 1
    while target.exists():
        target = backup_dir / (path.stem + ("_%02d" % n) + path.suffix)
        n += 1
    shutil.copy2(path, target)
    return target


def _migrate_inplace(path: Path, j: dict, backup_dir: Path) -> Tuple[Path, Path]:
    backup_path = _backup(path, backup_dir)
    j2 = dict(j)
    j2["schema_id"] = SCHEMA_ID_V0_2
    if not isinstance(j2.get("version"), str) or not j2["version"].startswith("v"):
        j2["version"] = "v0_2"
    _write_json(path, j2)
    return path, backup_path


_SEARCH_GLOBS = (
    "ORGANS/**/*_tool_passport_v*.json",
    "ORGANS/**/*_tool_passports_v*.json",
    "ORGANS/**/PASSPORTS/*.json",
)


def find_passports(repo_root: Path) -> List[Path]:
    seen: Dict[str, Path] = {}
    for pat in _SEARCH_GLOBS:
        for p in repo_root.glob(pat):
            if p.is_file():
                seen[p.as_posix()] = p
    return sorted(seen.values(), key=lambda x: x.as_posix())


def migrate_one(passport_path: Path, repo_root: Path, backup_dir: Path, dry_run: bool) -> dict:
    rel = passport_path.relative_to(repo_root).as_posix() if passport_path.is_relative_to(repo_root) else passport_path.as_posix()
    j = _read_json(passport_path)
    cls = classify(passport_path, j)

    if cls == "parse_error":
        return {"path": rel, "status": "parse_error", "missing": [], "notes": ["json parse failed"]}
    if cls in ("skipped_meta_schema", "skipped_not_a_tool_passport", "skipped_already_v0_2", "non_compliant"):
        if cls == "non_compliant":
            return {"path": rel, "status": "manual_migration_needed", "missing": ["schema_id-not-recognized"], "notes": ["shape not recognized as tool passport"]}
        return {"path": rel, "status": cls, "missing": [], "notes": []}

    # legacy -> field check
    assert j is not None
    missing = _check_required(j)
    if missing:
        return {
            "path": rel,
            "status": "manual_migration_needed",
            "missing": missing,
            "notes": ["required v0_2 fields missing; use passport_v0_2_auto_registrar to draft, or edit manually"],
        }

    if dry_run:
        return {
            "path": rel,
            "status": "planned",
            "missing": [],
            "notes": ["all required fields present; would migrate schema_id -> v0_2"],
        }

    _, backup_path = _migrate_inplace(passport_path, j, backup_dir)
    backup_rel = backup_path.relative_to(repo_root).as_posix() if backup_path.is_relative_to(repo_root) else backup_path.as_posix()
    return {
        "path": rel,
        "status": "applied",
        "missing": [],
        "notes": ["schema_id -> v0_2"],
        "backup_path": backup_rel,
    }


def run(repo_root: Path, out_path: Path, dry_run: bool) -> int:
    start = time.time()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = repo_root / "ORGANS" / "MECHANICUS" / "TOOL_INTELLIGENCE" / "PASSPORT_MIGRATOR" / "BACKUPS" / ts

    passports = find_passports(repo_root)
    results: List[dict] = []
    summary: Dict[str, int] = {
        "total": 0,
        "skipped_already_v0_2": 0,
        "skipped_meta_schema": 0,
        "skipped_not_a_tool_passport": 0,
        "planned": 0,
        "applied": 0,
        "manual_migration_needed": 0,
        "parse_error": 0,
    }

    for pp in passports:
        r = migrate_one(pp, repo_root, backup_dir, dry_run=dry_run)
        results.append(r)
        summary["total"] += 1
        st = r.get("status")
        if st in summary:
            summary[st] += 1

    elapsed_ms = int((time.time() - start) * 1000)
    ledger = {
        "schema_id": LEDGER_SCHEMA_ID,
        "generated_at": _utc_now_iso(),
        "generator": "passport_migrator_v0_2",
        "generator_version": MIGRATOR_VERSION,
        "mode": "dry_run" if dry_run else "apply",
        "repo_root": repo_root.as_posix(),
        "backup_dir": backup_dir.as_posix(),
        "elapsed_ms": elapsed_ms,
        "summary": summary,
        "results": results,
    }
    _write_json(out_path, ledger)

    print("")
    print("=== passport_migrator_v0_2 :: %s ===" % ("dry_run" if dry_run else "apply"))
    for k in ("total", "skipped_already_v0_2", "skipped_meta_schema", "skipped_not_a_tool_passport",
              "planned", "applied", "manual_migration_needed", "parse_error"):
        print("  %-32s = %d" % (k, summary[k]))
    print("  ledger                          -> %s" % out_path.as_posix())

    if summary["manual_migration_needed"] > 0:
        return 1
    if summary["parse_error"] > 0:
        return 1
    return 0


def _self_test() -> int:
    import tempfile
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        pdir = repo / "ORGANS" / "MECHANICUS" / "TOOL_INTELLIGENCE" / "PASSPORTS"
        pdir.mkdir(parents=True)
        blockdir = repo / "ORGANS" / "INQUISITION" / "BLOCK" / "PASSPORT"
        blockdir.mkdir(parents=True)
        backup_dir = repo / "_b"

        # case 1: legacy good (all fields present) -> planned
        legacy_good = {
            "schema_id": "imperium.tool_passport.v0_1",
            "tool_id": "sample",
            "name": "Sample",
            "version": "v0_1",
            "owner_organ": "MECHANICUS",
            "lang": "python",
            "validators": [{"id": "syntax", "type": "command", "command": "python -m py_compile x", "timeout_seconds": 10}],
            "exec_mode": "static",
            "owner_gated": False,
        }
        p1 = pdir / "sample_tool_passport_v0_1.json"
        _write_json(p1, legacy_good)
        r1 = migrate_one(p1, repo, backup_dir, dry_run=True)
        ok1 = r1["status"] == "planned"
        print("case 1 legacy good           : %s  (%s)" % ("OK" if ok1 else "FAIL", r1["status"]))
        if not ok1: failures += 1

        # case 2: organ block -> skipped_not_a_tool_passport
        p2 = blockdir / "ORGAN_BLOCK_PASSPORT_V0_1.json"
        _write_json(p2, {"schema_id": "imperium.organ_block_passport.v0_1"})
        r2 = migrate_one(p2, repo, backup_dir, dry_run=True)
        ok2 = r2["status"] == "skipped_not_a_tool_passport"
        print("case 2 organ block           : %s  (%s)" % ("OK" if ok2 else "FAIL", r2["status"]))
        if not ok2: failures += 1

        # case 3: .schema.json -> skipped_meta_schema
        p3 = pdir / "some.schema.json"
        _write_json(p3, {"type": "object"})
        r3 = migrate_one(p3, repo, backup_dir, dry_run=True)
        ok3 = r3["status"] == "skipped_meta_schema"
        print("case 3 .schema.json          : %s  (%s)" % ("OK" if ok3 else "FAIL", r3["status"]))
        if not ok3: failures += 1

        # case 4: NEW - tool_passport_schema_v0_1.json -> skipped_meta_schema (filename prefix rule)
        p4 = pdir / "tool_passport_schema_v0_1.json"
        _write_json(p4, {"schema_id": "imperium.tool_passport_schema.v0_1", "type": "object"})
        r4 = migrate_one(p4, repo, backup_dir, dry_run=True)
        ok4 = r4["status"] == "skipped_meta_schema"
        print("case 4 tool_passport_schema  : %s  (%s) <NEW>" % ("OK" if ok4 else "FAIL", r4["status"]))
        if not ok4: failures += 1

        # case 5: legacy missing fields -> manual_migration_needed
        p5 = pdir / "evidence_x_tool_passports_v0_1.json"
        _write_json(p5, {"schema_id": "imperium.tool_passport.v0_1"})
        r5 = migrate_one(p5, repo, backup_dir, dry_run=True)
        ok5 = r5["status"] == "manual_migration_needed" and "validators" in r5["missing"]
        print("case 5 typo evidence missing : %s  (%s missing=%s)" % ("OK" if ok5 else "FAIL", r5["status"], r5.get("missing")))
        if not ok5: failures += 1

        # case 6: apply mode migrates schema_id
        r6 = migrate_one(p1, repo, backup_dir, dry_run=False)
        ok6 = r6["status"] == "applied"
        if ok6:
            j_after = _read_json(p1)
            ok6 = j_after is not None and j_after.get("schema_id") == SCHEMA_ID_V0_2
        print("case 6 apply migrates schema : %s  (%s)" % ("OK" if ok6 else "FAIL", r6["status"]))
        if not ok6: failures += 1

    if failures == 0:
        print("self-test ok (6 cases)")
        return 0
    print("self-test FAILED: %d failures" % failures)
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Mechanicus passport migrator v0_2")
    ap.add_argument("--repo", type=str, default=None)
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.dry_run and not args.apply:
        print("error: one of --dry-run / --apply / --self-test required", file=sys.stderr)
        return 2
    if args.dry_run and args.apply:
        print("error: --dry-run and --apply are mutually exclusive", file=sys.stderr)
        return 2

    repo = Path(args.repo) if args.repo else Path.cwd()
    if not repo.is_dir():
        print("error: repo root not found: %s" % repo, file=sys.stderr)
        return 2

    if not args.out:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.out = str(repo / "_LOCAL_HANDOFF" / "MIGRATION" / ("v0_2_migration_%s.json" % ts))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    return run(repo, out_path, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
