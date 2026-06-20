#!/usr/bin/env python3
"""inq_ban.py -- Inquisition ban-list manager (append-only).

Two modes:
  --check (default): read bans.jsonl, emit:
    BLOCK_BAN  if author currently banned (most recent event for author == 'ban')
    OK         otherwise
  --update --outcome BLOCK: append BLOCK event for author, then evaluate ban triggers:
    - 3 consecutive BLOCKs (Q8 trigger) -> append 'ban' event
    - >= 5 BLOCKs within last 7d window  -> append 'ban' event
    Ban duration: permanent_until_owner_manual (THRESHOLDS.ban_duration).

NOTE: I8 BAN_REQUIRES_PROOF -- ban events must include 'proof' list of report paths.
OWNER_MANUAL cannot be banned (charter immunity).

Authors.json's cycles_block field is the secondary source of truth for streak;
this tool walks bans.jsonl events to compute streak/window accurately.

CLI:
  inq_ban.py --pack-dir <d> --task-id <id> --author <a> --stage <s>
             [--reports-dir <d>] [--bans-file <p>] [--config-dir <d>]
             [--update] [--outcome BLOCK|OK] [--proof <path> ...]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_INPUT_INVALID
from inq_patterns import load_thresholds


def _find_bans_file(start: Path, override: Optional[Path]) -> Optional[Path]:
    if override and override.is_file():
        return override.resolve()
    rel = Path("ORGANS/INQUISITION/BAN_LIST/bans.jsonl")
    cur = start if start.is_dir() else start.parent
    for cand in [cur, *cur.parents]:
        for prefix in ("", "files"):
            t = (cand / prefix / rel) if prefix else (cand / rel)
            if t.is_file():
                return t.resolve()
    return None


def _read_events(bans_file: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    with bans_file.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                d["_lineno"] = lineno
                out.append(d)
            except json.JSONDecodeError:
                continue
    return out


def _is_banned_now(events: List[Dict[str, Any]], author: str) -> bool:
    # Most recent ban/unban event for this author wins.
    most_recent: Optional[Dict[str, Any]] = None
    for e in events:
        if e.get("author") != author:
            continue
        if e.get("event") in ("ban", "unban"):
            most_recent = e
    return most_recent is not None and most_recent.get("event") == "ban"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(ts: str) -> Optional[datetime]:
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _append_event(bans_file: Path, event: Dict[str, Any]) -> None:
    line = json.dumps(event, ensure_ascii=False)
    with bans_file.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def check(
    *,
    pack_dir: Path,
    task_id: str,
    author: str,
    stage: str,
    reports_dir: str,
    bans_file: Optional[Path],
) -> int:
    vb = VerdictBuilder(tool="inq_ban", task_id=task_id, author=author, stage=stage)
    bf = _find_bans_file(pack_dir, bans_file)
    if bf is None:
        vb.fail_closed("bans.jsonl not found")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    try:
        events = _read_events(bf)
    except Exception as e:
        vb.fail_closed(f"bans_read_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    if _is_banned_now(events, author):
        vb.block("BAN", f"author {author!r} is currently banned; unban requires OWNER_MANUAL pack")
        last = [e for e in events if e.get("author") == author and e.get("event") == "ban"][-1:]
        if last:
            vb.add_finding(**{k: v for k, v in last[0].items() if k != "_lineno"})
    else:
        vb.ok(f"author {author!r} not banned")
    _, _, ec = vb.write(reports_dir=reports_dir)
    return ec


def update(
    *,
    pack_dir: Path,
    task_id: str,
    author: str,
    stage: str,
    reports_dir: str,
    bans_file: Optional[Path],
    config_dir: Optional[Path],
    outcome: str,
    proof: List[str],
) -> int:
    vb = VerdictBuilder(tool="inq_ban", task_id=task_id, author=author, stage=stage)
    if outcome not in ("OK", "BLOCK"):
        vb.fail_closed(f"invalid outcome: {outcome!r}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    try:
        thresholds = load_thresholds(config_dir)
    except Exception as e:
        vb.fail_closed(f"thresholds_load_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    bf = _find_bans_file(pack_dir, bans_file)
    if bf is None:
        vb.fail_closed("bans.jsonl not found")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    if outcome == "OK":
        # Append OK event so streak window is accurate (resets consec)
        _append_event(bf, {
            "event": "ok",
            "author": author,
            "task_id": task_id,
            "utc": _utc_now(),
        })
        vb.ok(f"OK event appended for {author}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec

    # BLOCK path: append BLOCK event, then evaluate ban triggers.
    block_event = {
        "event": "block",
        "author": author,
        "task_id": task_id,
        "utc": _utc_now(),
        "proof": list(proof),
    }
    _append_event(bf, block_event)

    # OWNER_MANUAL cannot be banned (charter).
    if author == "OWNER_MANUAL":
        vb.ok(f"OWNER_MANUAL BLOCK recorded; immune to autoban")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec

    # Re-read events including new BLOCK; compute streak and weekly count.
    events = _read_events(bf)
    author_events = [e for e in events if e.get("author") == author and e.get("event") in ("ok", "block", "ban", "unban")]
    # consec blocks (most recent, walking backward until non-block)
    consec = 0
    for e in reversed(author_events):
        if e.get("event") == "block":
            consec += 1
        elif e.get("event") in ("ok", "unban"):
            break
        elif e.get("event") == "ban":
            break
    # weekly window
    now = datetime.now(timezone.utc)
    window_days = int(thresholds["thresholds"]["ban_burst_weekly"].get("window_days", 7))
    cutoff = now - timedelta(days=window_days)
    weekly = 0
    for e in author_events:
        if e.get("event") != "block":
            continue
        ts = _parse_utc(e.get("utc", ""))
        if ts is not None and ts >= cutoff:
            weekly += 1

    consec_thresh = int(thresholds["thresholds"]["ban_burst_consec"]["value"])
    weekly_thresh = int(thresholds["thresholds"]["ban_burst_weekly"]["value"])

    if consec >= consec_thresh or weekly >= weekly_thresh:
        # I8 BAN_REQUIRES_PROOF: ensure proof list is non-empty.
        if not proof:
            vb.fail_closed("ban trigger met but no proof paths provided (I8 BAN_REQUIRES_PROOF)")
            _, _, ec = vb.write(reports_dir=reports_dir)
            return ec
        ban_event = {
            "event": "ban",
            "author": author,
            "task_id": task_id,
            "utc": _utc_now(),
            "reason": f"autoban: consec={consec} (>={consec_thresh}) or weekly={weekly} (>={weekly_thresh})",
            "proof": list(proof),
            "unban_path": "OWNER_MANUAL (signed unban pack required)",
            "duration": str(thresholds["thresholds"]["ban_duration"]["value"]),
        }
        _append_event(bf, ban_event)
        vb.block("BAN", f"author {author!r} autobanned (consec={consec}, weekly={weekly})")
        vb.add_finding(**{k: v for k, v in ban_event.items()})
    else:
        vb.hint("BAN_TRACK",
                f"BLOCK recorded; consec={consec}/{consec_thresh}, weekly={weekly}/{weekly_thresh}")
        vb.add_finding(**{k: v for k, v in block_event.items()})

    vb.set_evidence(str(bf))
    _, _, ec = vb.write(reports_dir=reports_dir)
    return ec


def _ensure_utf8() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> int:
    _ensure_utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-dir", required=True)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--reports-dir", default="ORGANS/INQUISITION/REPORTS")
    ap.add_argument("--bans-file", default=None)
    ap.add_argument("--config-dir", default=None)
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--outcome", choices=["OK", "BLOCK"], default=None)
    ap.add_argument("--proof", action="append", default=[])
    args = ap.parse_args()
    pack_dir = Path(args.pack_dir).resolve()
    if not pack_dir.is_dir():
        d = {
            "schema_version": "inq.verdict.v0_1",
            "verdict": "FAIL_CLOSED",
            "stage": args.stage,
            "reasons": [f"pack_dir not a directory: {pack_dir}"],
            "tool": "inq_ban",
            "task_id": args.task_id,
            "author": args.author,
            "exit_code": EXIT_INPUT_INVALID,
        }
        sys.stdout.write(json.dumps(d, ensure_ascii=False) + "\n")
        return EXIT_INPUT_INVALID
    common = dict(
        pack_dir=pack_dir,
        task_id=args.task_id,
        author=args.author,
        stage=args.stage,
        reports_dir=args.reports_dir,
        bans_file=Path(args.bans_file).resolve() if args.bans_file else None,
    )
    if args.update:
        if args.outcome is None:
            d = {
                "schema_version": "inq.verdict.v0_1",
                "verdict": "FAIL_CLOSED",
                "stage": args.stage,
                "reasons": ["--update requires --outcome OK|BLOCK"],
                "tool": "inq_ban",
                "task_id": args.task_id,
                "author": args.author,
                "exit_code": EXIT_INPUT_INVALID,
            }
            sys.stdout.write(json.dumps(d, ensure_ascii=False) + "\n")
            return EXIT_INPUT_INVALID
        return update(
            outcome=args.outcome,
            config_dir=Path(args.config_dir).resolve() if args.config_dir else None,
            proof=args.proof,
            **common,
        )
    return check(**common)


if __name__ == "__main__":
    sys.exit(main())
