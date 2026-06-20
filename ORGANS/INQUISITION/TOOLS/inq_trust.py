#!/usr/bin/env python3
"""inq_trust.py -- Inquisition trust ledger manager.

Two modes:
  --check (default):  read authors.json; emit verdict for author.
    trust >= trust_min_permit (0.5)  -> OK
    trust <  trust_min_permit         -> BLOCK_TRUST
                                         UNLESS author.probation_remaining > 0,
                                         in which case emit HINT_PROBATION (Q13).
  --update --outcome OK|BLOCK : mutate authors.json with delta:
    OK    -> trust += trust_delta_ok (x trust_delta_ok.streak_multiplier if streak>=threshold)
             streak_ok += 1, cycles_ok += 1, cycles_total += 1,
             probation_remaining = max(0, probation_remaining - 1)
    BLOCK -> trust += trust_delta_block (negative), streak_ok = 0,
             cycles_block += 1, cycles_total += 1.
    Trust clamp to [0.0, 1.0]. OWNER_MANUAL is immune to negative deltas.

CLI:
  inq_trust.py --pack-dir <d> --task-id <id> --author <a> --stage <s>
               [--reports-dir <d>] [--trust-file <p>] [--config-dir <d>]
               [--update] [--outcome OK|BLOCK]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_INPUT_INVALID
from inq_patterns import load_thresholds


def _find_authors_file(start: Path, override: Optional[Path]) -> Optional[Path]:
    if override and override.is_file():
        return override.resolve()
    rel = Path("ORGANS/INQUISITION/TRUST/authors.json")
    cur = start if start.is_dir() else start.parent
    for cand in [cur, *cur.parents]:
        for prefix in ("", "files"):
            t = (cand / prefix / rel) if prefix else (cand / rel)
            if t.is_file():
                return t.resolve()
    return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_author_entry(trust: Dict[str, Any], author: str, baseline: float) -> Dict[str, Any]:
    authors = trust.setdefault("authors", {})
    if author not in authors:
        authors[author] = {
            "trust": baseline,
            "baseline": baseline,
            "cycles_total": 0,
            "cycles_ok": 0,
            "cycles_block": 0,
            "streak_ok": 0,
            "probation_remaining": 3 if author != "OWNER_MANUAL" else 0,
            "first_seen_utc": None,
            "last_seen_utc": None,
            "notes": "auto-registered by inq_trust on first sighting",
        }
    return authors[author]


def _baseline_for(author: str, thresholds: Dict[str, Any]) -> float:
    if author == "OWNER_MANUAL":
        return float(thresholds["thresholds"]["trust_baseline_owner"]["value"])
    return float(thresholds["thresholds"]["trust_baseline_llm"]["value"])


def check(
    *,
    pack_dir: Path,
    task_id: str,
    author: str,
    stage: str,
    reports_dir: str,
    trust_file: Optional[Path],
    config_dir: Optional[Path],
) -> int:
    vb = VerdictBuilder(tool="inq_trust", task_id=task_id, author=author, stage=stage)
    try:
        thresholds = load_thresholds(config_dir)
    except Exception as e:
        vb.fail_closed(f"thresholds_load_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    af = _find_authors_file(pack_dir, trust_file)
    if af is None:
        vb.fail_closed("authors.json not found")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    try:
        with af.open(encoding="utf-8") as f:
            trust = json.load(f)
    except Exception as e:
        vb.fail_closed(f"authors_read_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec

    baseline = _baseline_for(author, thresholds)
    entry = trust.get("authors", {}).get(author) or _ensure_author_entry(trust, author, baseline)
    score = float(entry.get("trust", baseline))
    probation = int(entry.get("probation_remaining", 0))
    min_permit = float(thresholds["thresholds"]["trust_min_permit"]["value"])

    vb.add_finding(
        author=author,
        trust=score,
        baseline=entry.get("baseline", baseline),
        probation_remaining=probation,
        cycles_total=entry.get("cycles_total", 0),
        cycles_ok=entry.get("cycles_ok", 0),
        cycles_block=entry.get("cycles_block", 0),
        streak_ok=entry.get("streak_ok", 0),
        min_permit=min_permit,
    )

    if score < min_permit:
        if probation > 0 and author != "OWNER_MANUAL":
            vb.hint(
                "PROBATION",
                f"trust {score:.3f} < {min_permit:.3f} but probation_remaining={probation}; granting HINT_PROBATION (Q13)",
            )
        else:
            vb.block(
                "TRUST",
                f"trust {score:.3f} < {min_permit:.3f} for author {author!r}",
            )
    elif score < min_permit + 0.05:
        vb.hint("TRUST_LOW", f"trust {score:.3f} barely above min_permit {min_permit:.3f}")
    else:
        vb.ok(f"trust {score:.3f} >= {min_permit:.3f}")

    _, _, ec = vb.write(reports_dir=reports_dir)
    return ec


def update(
    *,
    pack_dir: Path,
    task_id: str,
    author: str,
    stage: str,
    reports_dir: str,
    trust_file: Optional[Path],
    config_dir: Optional[Path],
    outcome: str,
) -> int:
    vb = VerdictBuilder(tool="inq_trust", task_id=task_id, author=author, stage=stage)
    if outcome not in ("OK", "BLOCK"):
        vb.fail_closed(f"invalid outcome: {outcome!r} (must be OK or BLOCK)")
        d, _, _ = vb.write(reports_dir=reports_dir)
        d_ec = d.get("exit_code", 4)
        return EXIT_INPUT_INVALID if d_ec == 2 else d_ec
    try:
        thresholds = load_thresholds(config_dir)
    except Exception as e:
        vb.fail_closed(f"thresholds_load_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    af = _find_authors_file(pack_dir, trust_file)
    if af is None:
        vb.fail_closed("authors.json not found")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec
    try:
        with af.open(encoding="utf-8") as f:
            trust = json.load(f)
    except Exception as e:
        vb.fail_closed(f"authors_read_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec

    baseline = _baseline_for(author, thresholds)
    entry = _ensure_author_entry(trust, author, baseline)
    score = float(entry.get("trust", baseline))
    streak = int(entry.get("streak_ok", 0))
    cycles_total = int(entry.get("cycles_total", 0))
    cycles_ok = int(entry.get("cycles_ok", 0))
    cycles_block = int(entry.get("cycles_block", 0))
    probation = int(entry.get("probation_remaining", 0))

    ok_spec = thresholds["thresholds"]["trust_delta_ok"]
    block_delta = float(thresholds["thresholds"]["trust_delta_block"]["value"])
    base_ok_delta = float(ok_spec["value"])
    streak_thresh = int(ok_spec.get("streak_multiplier_threshold", 5))
    streak_mult = float(ok_spec.get("streak_multiplier", 1.5))

    if outcome == "OK":
        new_streak = streak + 1
        delta = base_ok_delta * (streak_mult if new_streak >= streak_thresh else 1.0)
        score = min(1.0, score + delta)
        cycles_ok += 1
        cycles_total += 1
        probation = max(0, probation - 1)
        entry.update({
            "trust": round(score, 4),
            "streak_ok": new_streak,
            "cycles_ok": cycles_ok,
            "cycles_total": cycles_total,
            "probation_remaining": probation,
            "last_seen_utc": _utc_now(),
        })
        if entry.get("first_seen_utc") is None:
            entry["first_seen_utc"] = entry["last_seen_utc"]
        vb.ok(f"trust updated for {author}: {score:.4f} (streak={new_streak}, delta=+{delta:.4f})")
    else:  # BLOCK
        # OWNER_MANUAL is immune to negative deltas (charter)
        if author == "OWNER_MANUAL":
            entry.update({
                "cycles_block": cycles_block + 1,
                "cycles_total": cycles_total + 1,
                "streak_ok": 0,
                "last_seen_utc": _utc_now(),
            })
            vb.ok(f"OWNER_MANUAL BLOCK recorded but trust immune ({score:.4f})")
        else:
            score = max(0.0, score + block_delta)
            entry.update({
                "trust": round(score, 4),
                "cycles_block": cycles_block + 1,
                "cycles_total": cycles_total + 1,
                "streak_ok": 0,
                "last_seen_utc": _utc_now(),
            })
            if entry.get("first_seen_utc") is None:
                entry["first_seen_utc"] = entry["last_seen_utc"]
            vb.ok(f"trust decreased for {author}: {score:.4f} (delta={block_delta:.4f})")

    trust["updated_utc"] = _utc_now()
    try:
        af.write_text(json.dumps(trust, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        vb.fail_closed(f"authors_write_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec

    vb.add_finding(
        outcome=outcome,
        new_trust=score,
        new_streak_ok=entry["streak_ok"],
        new_probation_remaining=entry["probation_remaining"],
    )
    vb.set_evidence(str(af))
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
    ap.add_argument("--trust-file", default=None)
    ap.add_argument("--config-dir", default=None)
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--outcome", choices=["OK", "BLOCK"], default=None)
    args = ap.parse_args()
    pack_dir = Path(args.pack_dir).resolve()
    if not pack_dir.is_dir():
        d = {
            "schema_version": "inq.verdict.v0_1",
            "verdict": "FAIL_CLOSED",
            "stage": args.stage,
            "reasons": [f"pack_dir not a directory: {pack_dir}"],
            "tool": "inq_trust",
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
        trust_file=Path(args.trust_file).resolve() if args.trust_file else None,
        config_dir=Path(args.config_dir).resolve() if args.config_dir else None,
    )
    if args.update:
        if args.outcome is None:
            d = {
                "schema_version": "inq.verdict.v0_1",
                "verdict": "FAIL_CLOSED",
                "stage": args.stage,
                "reasons": ["--update requires --outcome OK|BLOCK"],
                "tool": "inq_trust",
                "task_id": args.task_id,
                "author": args.author,
                "exit_code": EXIT_INPUT_INVALID,
            }
            sys.stdout.write(json.dumps(d, ensure_ascii=False) + "\n")
            return EXIT_INPUT_INVALID
        return update(outcome=args.outcome, **common)
    return check(**common)


if __name__ == "__main__":
    sys.exit(main())
