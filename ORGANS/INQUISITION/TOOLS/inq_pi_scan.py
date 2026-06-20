#!/usr/bin/env python3
"""inq_pi_scan.py -- Inquisition prompt-injection scanner (7 categories).

Reads all text files under --pack-dir, applies all 7 PI category patterns from
SIGNATURES.json. Computes cumulative weight across non-fixture files.
Files under `_HARNESS/_FIXTURES/INQ/...` are recorded but their weight does NOT
count toward BLOCK threshold (fixtures legitimately contain PI patterns).

Adaptive thresholds (Q4):
  - LLM authors (NOTION_OPUS/CODEX/GROK): BLOCK at total_weight >= 3
  - OWNER_MANUAL:                          BLOCK at total_weight >= 5

Verdict ladder:
  weight == 0 and no findings -> OK
  weight  > 0 and < threshold -> HINT_PI
  weight >= threshold         -> BLOCK_PI  (or HINT_PI_OVERRIDDEN if --force-inq)

CLI mirrors inq_secrets.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_INPUT_INVALID
from inq_patterns import compile_pi_patterns, load_signatures, load_thresholds

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml",
    ".sh", ".ps1", ".env", ".md", ".txt", ".rst", ".tex", ".log",
    ".html", ".css", ".sql", ".cfg", ".ini", ".xml", ".jsonl", ".ndjson",
}
MAX_FILE_BYTES = 2 * 1024 * 1024

LLM_AUTHORS = {"NOTION_OPUS", "CODEX", "GROK"}


def _iter_pack_files(pack_dir: Path) -> List[Path]:
    out: List[Path] = []
    for root, dirs, fnames in os.walk(pack_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".git")]
        for f in fnames:
            p = Path(root) / f
            if p.suffix.lower() in TEXT_EXTENSIONS:
                out.append(p)
    return out


def _is_fixture_file(file_path: Path, pack_dir: Path) -> bool:
    try:
        rel = file_path.resolve().relative_to(pack_dir.resolve())
    except ValueError:
        return False
    parts = [p.lower() for p in rel.parts]
    return ("_harness" in parts and "_fixtures" in parts and "inq" in parts) or (
        "_fixtures" in parts and "inq" in parts
    )


def scan(
    pack_dir: Path,
    *,
    task_id: str,
    author: str,
    stage: str,
    reports_dir: str,
    force_inq: bool,
    config_dir: Optional[Path],
) -> int:
    vb = VerdictBuilder(tool="inq_pi_scan", task_id=task_id, author=author, stage=stage)
    try:
        sigs = load_signatures(config_dir)
        thresholds = load_thresholds(config_dir)
    except Exception as e:
        vb.fail_closed(f"config_load_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec

    patterns = compile_pi_patterns(sigs)
    files = _iter_pack_files(pack_dir)
    findings: List[Dict[str, Any]] = []
    total_weight = 0

    for fpath in files:
        is_fixture = _is_fixture_file(fpath, pack_dir)
        try:
            if fpath.stat().st_size > MAX_FILE_BYTES:
                continue
            text = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        try:
            rel = str(fpath.relative_to(pack_dir))
        except ValueError:
            rel = str(fpath)
        for cat, weight, compiled in patterns:
            for rgx in compiled:
                for m in rgx.finditer(text):
                    line_no = text.count("\n", 0, m.start()) + 1
                    snippet = m.group(0)[:80].replace("\n", " ")
                    finding = {
                        "file": rel,
                        "line": line_no,
                        "category": cat,
                        "weight": weight,
                        "snippet": snippet,
                        "fixture": is_fixture,
                    }
                    findings.append(finding)
                    if not is_fixture:
                        total_weight += weight

    if author in LLM_AUTHORS:
        block_threshold = int(thresholds["thresholds"]["pi_score_block_llm"]["value"])
    else:
        block_threshold = int(thresholds["thresholds"]["pi_score_block_owner"]["value"])

    real_findings = [f for f in findings if not f["fixture"]]

    if total_weight >= block_threshold:
        if force_inq:
            vb.hint(
                "PI_OVERRIDDEN",
                f"PI weight {total_weight} >= {block_threshold} overridden by --force-inq (author={author})",
            )
            vb.add_recommendation("override logged per charter I10")
        else:
            vb.block(
                "PI",
                f"PI cumulative weight {total_weight} >= {block_threshold} (author={author})",
            )
    elif real_findings:
        vb.hint(
            "PI",
            f"PI matches found ({len(real_findings)} non-fixture); weight {total_weight} < {block_threshold}",
        )
    else:
        if findings:
            vb.ok(f"clean ({len(files)} files; {len(findings)} fixture-only matches ignored)")
        else:
            vb.ok(f"clean ({len(files)} files scanned, 0 PI matches)")

    for f in findings:
        vb.add_finding(**f)

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
    ap.add_argument("--force-inq", action="store_true")
    ap.add_argument("--config-dir", default=None)
    args = ap.parse_args()
    pack_dir = Path(args.pack_dir).resolve()
    if not pack_dir.is_dir():
        d = {
            "schema_version": "inq.verdict.v0_1",
            "verdict": "FAIL_CLOSED",
            "stage": args.stage,
            "reasons": [f"pack_dir not a directory: {pack_dir}"],
            "tool": "inq_pi_scan",
            "task_id": args.task_id,
            "author": args.author,
            "exit_code": EXIT_INPUT_INVALID,
        }
        sys.stdout.write(json.dumps(d, ensure_ascii=False) + "\n")
        return EXIT_INPUT_INVALID
    return scan(
        pack_dir,
        task_id=args.task_id,
        author=args.author,
        stage=args.stage,
        reports_dir=args.reports_dir,
        force_inq=args.force_inq,
        config_dir=Path(args.config_dir).resolve() if args.config_dir else None,
    )


if __name__ == "__main__":
    sys.exit(main())
