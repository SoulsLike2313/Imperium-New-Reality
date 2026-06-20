#!/usr/bin/env python3
"""inq_audit.py -- Inquisition immutable audit log (charter I6 APPEND_ONLY, I10 OVERRIDE_LOGGED).

Writes every verdict (or generic event) to an append-only JSONL log:
  <audit_root>/audit_<YYYY-MM>.jsonl

Log file is monthly-rotated. Each line carries hash-chain pointer to previous
entry's SHA-256 for tamper-evidence:
  { ..., "_chain_prev_sha256": "<sha256 of previous line text>" }

The very first entry of a new file carries "_chain_prev_sha256": "GENESIS".

CLI:
  inq_audit.py --append --verdict <path>         # append a verdict JSON
  inq_audit.py --append-event --event-json '<j>' # append arbitrary event JSON
  inq_audit.py --verify-chain                    # walk chain, report tampering
  inq_audit.py --query --author <a> [--stage <s>] [--since <iso>] [--limit N]
  inq_audit.py --stats                           # totals per verdict/stage
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_INPUT_INVALID

GENESIS = "GENESIS"


def _audit_root_default(pack_dir: Path, override: Optional[Path]) -> Path:
    if override is not None:
        return override.resolve()
    return (pack_dir / "_INQUISITION" / "AUDIT").resolve()


def _current_log_file(audit_root: Path) -> Path:
    audit_root.mkdir(parents=True, exist_ok=True)
    ym = datetime.now(timezone.utc).strftime("%Y-%m")
    return audit_root / f"audit_{ym}.jsonl"


def _last_line_sha256(log_file: Path) -> str:
    # CRLF-safe: binary read, strip both \r and \n so hash is over the canonical
    # JSON line bytes regardless of how Windows or POSIX wrote the file.
    if not log_file.is_file() or log_file.stat().st_size == 0:
        return GENESIS
    last = ""
    with log_file.open("rb") as f:
        for chunk in f:
            line = chunk.decode("utf-8", errors="replace").rstrip("\r\n")
            if line:
                last = line
    if not last:
        return GENESIS
    return hashlib.sha256(last.encode("utf-8")).hexdigest()


def _append(log_file: Path, event: Dict[str, Any]) -> Tuple[str, str]:
    # CRLF-safe: open in binary append mode and write explicit LF so the on-disk
    # bytes are identical on Windows and POSIX. Hash is computed over the canonical
    # JSON line without any trailing newline byte(s).
    prev = _last_line_sha256(log_file)
    record = dict(event)
    record.setdefault("audit_appended_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    record["_chain_prev_sha256"] = prev
    line = json.dumps(record, ensure_ascii=False)
    with log_file.open("ab") as f:
        f.write(line.encode("utf-8") + b"\n")
    return prev, hashlib.sha256(line.encode("utf-8")).hexdigest()


def _verify_chain(log_file: Path) -> Tuple[bool, int, Optional[int]]:
    """Return (ok, lines_checked, first_bad_line_no). CRLF-safe."""
    if not log_file.is_file():
        return True, 0, None
    prev = GENESIS
    n = 0
    # Read in binary and strip \r\n so the chain hash matches _append/_last_line
    # regardless of CRLF translation that text mode would do on Windows.
    with log_file.open("rb") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                return False, n, lineno
            n += 1
            claimed = d.get("_chain_prev_sha256")
            if claimed != prev:
                return False, n, lineno
            prev = hashlib.sha256(line.encode("utf-8")).hexdigest()
    return True, n, None


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
    ap.add_argument("--audit-root", default=None)
    ap.add_argument("--task-id", default="AUDIT")
    ap.add_argument("--author", default="INQUISITION")
    ap.add_argument("--stage", default="H6_ON_DEMAND")
    ap.add_argument("--reports-dir", default="ORGANS/INQUISITION/REPORTS")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--append", action="store_true")
    group.add_argument("--append-event", action="store_true")
    group.add_argument("--verify-chain", action="store_true")
    group.add_argument("--query", action="store_true")
    group.add_argument("--stats", action="store_true")
    ap.add_argument("--verdict", default=None)
    ap.add_argument("--event-json", default=None)
    ap.add_argument("--author-filter", default=None)
    ap.add_argument("--stage-filter", default=None)
    ap.add_argument("--since", default=None)
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args()
    pack_dir = Path(args.pack_dir).resolve()
    audit_root = _audit_root_default(
        pack_dir, Path(args.audit_root).resolve() if args.audit_root else None
    )
    log_file = _current_log_file(audit_root)
    vb = VerdictBuilder(tool="inq_audit", task_id=args.task_id, author=args.author, stage=args.stage)

    if args.append:
        if not args.verdict:
            vb.fail_closed("--append requires --verdict <path>")
            _, _, ec = vb.write(reports_dir=args.reports_dir)
            return ec
        try:
            d = json.loads(Path(args.verdict).read_text(encoding="utf-8"))
        except Exception as e:
            vb.fail_closed(f"verdict_read_error: {type(e).__name__}: {e}")
            _, _, ec = vb.write(reports_dir=args.reports_dir)
            return ec
        prev, cur = _append(log_file, d)
        vb.ok("appended")
        vb.add_finding(log_file=str(log_file), prev_sha256=prev, line_sha256=cur)
        _, _, ec = vb.write(reports_dir=args.reports_dir)
        return ec

    if args.append_event:
        if not args.event_json:
            vb.fail_closed("--append-event requires --event-json <json>")
            _, _, ec = vb.write(reports_dir=args.reports_dir)
            return ec
        try:
            d = json.loads(args.event_json)
        except Exception as e:
            vb.fail_closed(f"event_json_parse_error: {type(e).__name__}: {e}")
            _, _, ec = vb.write(reports_dir=args.reports_dir)
            return ec
        prev, cur = _append(log_file, d)
        vb.ok("event appended")
        vb.add_finding(log_file=str(log_file), prev_sha256=prev, line_sha256=cur)
        _, _, ec = vb.write(reports_dir=args.reports_dir)
        return ec

    if args.verify_chain:
        files = sorted(audit_root.glob("audit_*.jsonl")) if audit_root.is_dir() else []
        if not files:
            vb.noop("no audit logs present")
            _, _, ec = vb.write(reports_dir=args.reports_dir)
            return ec
        all_ok = True
        results = []
        for lf in files:
            ok, n, bad = _verify_chain(lf)
            results.append({"file": str(lf), "ok": ok, "lines_checked": n, "first_bad_line": bad})
            all_ok = all_ok and ok
        if all_ok:
            vb.ok(f"chain intact across {len(files)} log file(s)")
        else:
            vb.block("AUDIT", "chain integrity violation detected")
        for r in results:
            vb.add_finding(**r)
        _, _, ec = vb.write(reports_dir=args.reports_dir)
        return ec

    if args.query or args.stats:
        files = sorted(audit_root.glob("audit_*.jsonl")) if audit_root.is_dir() else []
        matches: List[Dict[str, Any]] = []
        stats: Dict[str, int] = {}
        for lf in files:
            with lf.open(encoding="utf-8") as f:
                for raw in f:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        d = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if args.author_filter and d.get("author") != args.author_filter:
                        continue
                    if args.stage_filter and d.get("stage") != args.stage_filter:
                        continue
                    if args.since:
                        ts = d.get("issued_utc") or d.get("audit_appended_utc")
                        if ts and ts < args.since:
                            continue
                    matches.append(d)
                    v = d.get("verdict", "NON_VERDICT")
                    stats[v] = stats.get(v, 0) + 1
        if args.stats:
            vb.ok(f"stats over {sum(stats.values())} events")
            for k, c in sorted(stats.items()):
                vb.add_finding(verdict=k, count=c)
        else:
            limited = matches[-args.limit:] if args.limit > 0 else matches
            vb.ok(f"matched {len(matches)} events; returning last {len(limited)}")
            for d in limited:
                vb.add_finding(
                    verdict=d.get("verdict"),
                    tool=d.get("tool"),
                    task_id=d.get("task_id"),
                    author=d.get("author"),
                    issued_utc=d.get("issued_utc"),
                )
        _, _, ec = vb.write(reports_dir=args.reports_dir)
        return ec

    return 0


if __name__ == "__main__":
    sys.exit(main())
