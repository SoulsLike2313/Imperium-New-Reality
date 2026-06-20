#!/usr/bin/env python3
"""inq_trace.py -- Inquisition scan trace cache (Q21).

Caches per-file scan results keyed by (signatures_hash, file_sha256).
Auto-invalidates when SIGNATURES.json content hash changes.

Cache layout:
  <cache_root>/<sig_hash[:12]>/<file_sha256[:2]>/<file_sha256>.json

Default cache_root: <pack_dir>/_INQUISITION/TRACE_CACHE

CLI:
  inq_trace.py --status                 # report current sig_hash + cache stats
  inq_trace.py --invalidate             # clear cache for outdated sig_hash
  inq_trace.py --invalidate-all         # nuke entire cache
  inq_trace.py --has --file <path>      # check if a file's result is cached
  inq_trace.py --put --file <path> --tool <name> --verdict <json-file>
  inq_trace.py --get --file <path> --tool <name>

All commands write a verdict-shaped JSON to stdout (Q19).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_INPUT_INVALID
from inq_patterns import _find_config_dir  # noqa: F401 (intentional shared)


def _file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sig_hash(config_dir: Optional[Path]) -> str:
    from inq_patterns import _find_config_dir as _fc
    cd = config_dir or _fc()
    sig = (cd / "SIGNATURES.json").read_bytes()
    return hashlib.sha256(sig).hexdigest()


def _cache_root(pack_dir: Path, override: Optional[Path]) -> Path:
    if override is not None:
        return override.resolve()
    return (pack_dir / "_INQUISITION" / "TRACE_CACHE").resolve()


def _entry_path(cache_root: Path, sig_h: str, file_h: str, tool: str) -> Path:
    return cache_root / sig_h[:12] / file_h[:2] / f"{file_h}__{tool}.json"


def cmd_status(pack_dir: Path, cache_root: Path, sig_h: str, vb: VerdictBuilder) -> int:
    total = 0
    valid = 0
    if cache_root.is_dir():
        for sig_dir in cache_root.iterdir():
            if not sig_dir.is_dir():
                continue
            sub_count = sum(1 for p in sig_dir.rglob("*.json") if p.is_file())
            total += sub_count
            if sig_dir.name == sig_h[:12]:
                valid += sub_count
    vb.ok(f"trace cache status: total={total}, valid={valid}")
    vb.add_finding(
        cache_root=str(cache_root),
        signatures_hash=sig_h,
        signatures_hash_short=sig_h[:12],
        cache_entries_total=total,
        cache_entries_valid_for_current_signatures=valid,
    )
    return 0


def cmd_invalidate(cache_root: Path, sig_h: str, vb: VerdictBuilder, nuke: bool) -> int:
    removed = 0
    if cache_root.is_dir():
        if nuke:
            removed = sum(1 for _ in cache_root.rglob("*.json"))
            shutil.rmtree(cache_root, ignore_errors=True)
            cache_root.mkdir(parents=True, exist_ok=True)
        else:
            for sig_dir in list(cache_root.iterdir()):
                if sig_dir.is_dir() and sig_dir.name != sig_h[:12]:
                    removed += sum(1 for _ in sig_dir.rglob("*.json"))
                    shutil.rmtree(sig_dir, ignore_errors=True)
    vb.ok(f"invalidated {removed} stale cache entries (nuke={nuke})")
    vb.add_finding(removed=removed, nuke=nuke)
    return 0


def cmd_get(
    cache_root: Path, sig_h: str, file_path: Path, tool: str, vb: VerdictBuilder
) -> int:
    if not file_path.is_file():
        vb.fail_closed(f"file not found: {file_path}")
        return 4
    fh = _file_sha256(file_path)
    ep = _entry_path(cache_root, sig_h, fh, tool)
    if ep.is_file():
        try:
            data = json.loads(ep.read_text(encoding="utf-8"))
            vb.ok(f"cache hit for {file_path.name} / {tool}")
            vb.add_finding(file_sha256=fh, entry_path=str(ep), cached_verdict=data)
            return 0
        except Exception as e:
            vb.fail_closed(f"cache_read_error: {e}")
            return 2
    vb.noop(f"cache miss for {file_path.name} / {tool}")
    vb.add_finding(file_sha256=fh, expected_path=str(ep))
    return 0


def cmd_has(
    cache_root: Path, sig_h: str, file_path: Path, tool: str, vb: VerdictBuilder
) -> int:
    if not file_path.is_file():
        vb.fail_closed(f"file not found: {file_path}")
        return 4
    fh = _file_sha256(file_path)
    ep = _entry_path(cache_root, sig_h, fh, tool)
    if ep.is_file():
        vb.ok("cached")
        vb.add_finding(file_sha256=fh, entry_path=str(ep), cached=True)
    else:
        vb.noop("not cached")
        vb.add_finding(file_sha256=fh, expected_path=str(ep), cached=False)
    return 0


def cmd_put(
    cache_root: Path,
    sig_h: str,
    file_path: Path,
    tool: str,
    verdict_file: Path,
    vb: VerdictBuilder,
) -> int:
    if not file_path.is_file():
        vb.fail_closed(f"file not found: {file_path}")
        return 4
    if not verdict_file.is_file():
        vb.fail_closed(f"verdict file not found: {verdict_file}")
        return 4
    try:
        data = json.loads(verdict_file.read_text(encoding="utf-8"))
    except Exception as e:
        vb.fail_closed(f"verdict_read_error: {e}")
        return 2
    fh = _file_sha256(file_path)
    ep = _entry_path(cache_root, sig_h, fh, tool)
    try:
        ep.parent.mkdir(parents=True, exist_ok=True)
        ep.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        vb.fail_closed(f"cache_write_error: {e}")
        return 2
    vb.ok("stored")
    vb.add_finding(file_sha256=fh, entry_path=str(ep))
    return 0


def _ensure_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> int:
    _ensure_utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", default=".")
    ap.add_argument("--cache-root", default=None)
    ap.add_argument("--config-dir", default=None)
    ap.add_argument("--task-id", default="TRACE")
    ap.add_argument("--author", default="OWNER_MANUAL")
    ap.add_argument("--stage", default="H6_ON_DEMAND")
    ap.add_argument("--reports-dir", default="ORGANS/INQUISITION/REPORTS")
    ap.add_argument("--file", default=None)
    ap.add_argument("--tool", default=None)
    ap.add_argument("--verdict", default=None, help="path to verdict JSON file (for --put)")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true")
    group.add_argument("--invalidate", action="store_true")
    group.add_argument("--invalidate-all", action="store_true")
    group.add_argument("--has", action="store_true")
    group.add_argument("--get", action="store_true")
    group.add_argument("--put", action="store_true")
    args = ap.parse_args()
    pack_dir = Path(args.pack_dir).resolve()
    cache_root = _cache_root(pack_dir, Path(args.cache_root).resolve() if args.cache_root else None)
    cache_root.mkdir(parents=True, exist_ok=True)
    vb = VerdictBuilder(tool="inq_trace", task_id=args.task_id, author=args.author, stage=args.stage)
    try:
        sig_h = _sig_hash(Path(args.config_dir).resolve() if args.config_dir else None)
    except Exception as e:
        vb.fail_closed(f"sig_hash_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=args.reports_dir)
        return ec
    if args.status:
        cmd_status(pack_dir, cache_root, sig_h, vb)
    elif args.invalidate:
        cmd_invalidate(cache_root, sig_h, vb, nuke=False)
    elif args.invalidate_all:
        cmd_invalidate(cache_root, sig_h, vb, nuke=True)
    elif args.has or args.get or args.put:
        if not args.file or not args.tool:
            vb.fail_closed("--has/--get/--put require --file and --tool")
        else:
            file_path = Path(args.file).resolve()
            if args.has:
                cmd_has(cache_root, sig_h, file_path, args.tool, vb)
            elif args.get:
                cmd_get(cache_root, sig_h, file_path, args.tool, vb)
            else:  # put
                if not args.verdict:
                    vb.fail_closed("--put requires --verdict <path>")
                else:
                    cmd_put(cache_root, sig_h, file_path, args.tool, Path(args.verdict).resolve(), vb)
    _, _, ec = vb.write(reports_dir=args.reports_dir)
    return ec


if __name__ == "__main__":
    sys.exit(main())
