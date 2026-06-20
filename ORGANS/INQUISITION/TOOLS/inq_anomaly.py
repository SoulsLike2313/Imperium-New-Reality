#!/usr/bin/env python3
"""inq_anomaly.py -- Inquisition anomaly detector.

Charter threshold `anomaly_first_author` = HINT (non-overridable):
  - If the pack author has cycles_total == 0 in authors.json, emit HINT_FIRST_AUTHOR.
  - Always informative, never blocks.

Additional v0_1 anomaly checks:
  - target_organ unusual (not in known 9 organs) -> HINT_ANOMALY_ORGAN
  - submitted_by unusual (not in known signer roles) -> HINT_ANOMALY_SUBMITTER
  - schema_version drift on TASK_MANIFEST.json (!= imperium.astra_task_pack.v0_1)
    -> HINT_ANOMALY_SCHEMA

CLI:
  inq_anomaly.py --pack-dir <dir> --task-id <id> --author <a> --stage <s>
                 [--reports-dir <dir>] [--trust-file <path>] [--config-dir <dir>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_INPUT_INVALID

KNOWN_ORGANS = {
    "ADMINISTRATUM", "ASTRONOMICON", "CUSTODES", "DOCTRINARIUM",
    "INQUISITION", "MECHANICUS", "OFFICIO_AGENTIS", "SCHOLA_IMPERIALIS",
    "STRATEGIUM", "THRONE",
}
KNOWN_SUBMITTERS = {"OWNER_MANUAL", "NOTION_OPUS", "CODEX", "GROK", "SERVITOR"}
KNOWN_SCHEMA = "imperium.astra_task_pack.v0_1"


def _find_authors_file(start: Path, override: Optional[Path]) -> Optional[Path]:
    if override and override.is_file():
        return override
    rel = Path("ORGANS/INQUISITION/TRUST/authors.json")
    cur = start if start.is_dir() else start.parent
    for cand in [cur, *cur.parents]:
        for prefix in ("", "files"):
            t = (cand / prefix / rel) if prefix else (cand / rel)
            if t.is_file():
                return t.resolve()
    return None


def detect(
    pack_dir: Path,
    *,
    task_id: str,
    author: str,
    stage: str,
    reports_dir: str,
    trust_file: Optional[Path],
) -> int:
    vb = VerdictBuilder(tool="inq_anomaly", task_id=task_id, author=author, stage=stage)
    anomalies: list = []

    # 1) First-author check via authors.json
    af = _find_authors_file(pack_dir, trust_file)
    if af is None:
        anomalies.append({
            "kind": "FIRST_AUTHOR_UNKNOWN",
            "detail": "authors.json not found; treating as first-author for safety",
        })
    else:
        try:
            with af.open(encoding="utf-8") as f:
                trust = json.load(f)
            entry = trust.get("authors", {}).get(author)
            if entry is None:
                anomalies.append({
                    "kind": "FIRST_AUTHOR",
                    "detail": f"author {author!r} not in authors.json (new author)",
                })
            elif int(entry.get("cycles_total", 0)) == 0:
                anomalies.append({
                    "kind": "FIRST_AUTHOR",
                    "detail": f"author {author!r} has cycles_total=0 (first cycle)",
                })
        except Exception as e:
            anomalies.append({
                "kind": "TRUST_READ_ERROR",
                "detail": f"{type(e).__name__}: {e}",
            })

    # 2) Manifest sanity
    mpath = pack_dir / "TASK_MANIFEST.json"
    if mpath.is_file():
        try:
            with mpath.open(encoding="utf-8") as f:
                m = json.load(f)
            if m.get("schema_version") != KNOWN_SCHEMA:
                anomalies.append({
                    "kind": "ANOMALY_SCHEMA",
                    "detail": f"manifest schema_version={m.get('schema_version')!r} != {KNOWN_SCHEMA!r}",
                })
            organ = m.get("target_organ", "")
            if organ and organ not in KNOWN_ORGANS:
                anomalies.append({
                    "kind": "ANOMALY_ORGAN",
                    "detail": f"target_organ={organ!r} not in known {sorted(KNOWN_ORGANS)}",
                })
            submitter = m.get("submitted_by", "")
            if submitter and submitter not in KNOWN_SUBMITTERS:
                anomalies.append({
                    "kind": "ANOMALY_SUBMITTER",
                    "detail": f"submitted_by={submitter!r} not in known {sorted(KNOWN_SUBMITTERS)}",
                })
        except Exception as e:
            anomalies.append({
                "kind": "MANIFEST_READ_ERROR",
                "detail": f"{type(e).__name__}: {e}",
            })
    else:
        anomalies.append({
            "kind": "MANIFEST_MISSING",
            "detail": "TASK_MANIFEST.json not found in pack_dir",
        })

    if not anomalies:
        vb.ok("no anomalies detected")
    else:
        primary = anomalies[0]["kind"]
        kind_suffix = "FIRST_AUTHOR" if primary == "FIRST_AUTHOR" else "ANOMALY"
        vb.hint(kind_suffix, f"{len(anomalies)} anomaly signal(s) (non-overridable, informative)")
        for a in anomalies:
            vb.add_finding(**a)

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
    ap.add_argument("--config-dir", default=None)  # accepted but unused (consistent CLI)
    args = ap.parse_args()
    pack_dir = Path(args.pack_dir).resolve()
    if not pack_dir.is_dir():
        d = {
            "schema_version": "inq.verdict.v0_1",
            "verdict": "FAIL_CLOSED",
            "stage": args.stage,
            "reasons": [f"pack_dir not a directory: {pack_dir}"],
            "tool": "inq_anomaly",
            "task_id": args.task_id,
            "author": args.author,
            "exit_code": EXIT_INPUT_INVALID,
        }
        sys.stdout.write(json.dumps(d, ensure_ascii=False) + "\n")
        return EXIT_INPUT_INVALID
    return detect(
        pack_dir,
        task_id=args.task_id,
        author=args.author,
        stage=args.stage,
        reports_dir=args.reports_dir,
        trust_file=Path(args.trust_file).resolve() if args.trust_file else None,
    )


if __name__ == "__main__":
    sys.exit(main())
