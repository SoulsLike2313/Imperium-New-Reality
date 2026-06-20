#!/usr/bin/env python3
"""inq_secrets.py -- Inquisition secret scanner (8 pattern classes + tiered entropy).

Reads all text files under --pack-dir, applies all 8 secret pattern classes from
SIGNATURES.json, and for the `generic_high_entropy` class applies tiered entropy gate:
  - code/json/config files: threshold from THRESHOLDS.secrets_entropy_code (4.5 default)
  - text/markdown files:    threshold from THRESHOLDS.secrets_entropy_text (5.0 default)

Demo-pack whitelist (Q11 combo): a finding is whitelisted ONLY when BOTH hold:
  - the offending file lives under `_HARNESS/_FIXTURES/INQ/...` inside the pack
  - TASK_MANIFEST.json contains `"demo_secrets_allowed": true`

Force override (Q12): --force-inq replaces BLOCK_SECRETS with HINT_SECRETS_OVERRIDDEN.
Override is always logged (charter I10).

CLI:
  inq_secrets.py --pack-dir <dir> --task-id <id> --author <author> --stage <stage>
                [--reports-dir <dir>] [--force-inq] [--config-dir <dir>]

Verdict JSON on stdout. Human log on stderr.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_INPUT_INVALID
from inq_patterns import compile_secret_patterns, load_signatures, load_thresholds

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml",
    ".sh", ".ps1", ".env", ".md", ".txt", ".rst", ".tex", ".log",
    ".html", ".css", ".sql", ".cfg", ".ini", ".xml", ".jsonl", ".ndjson",
}
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MiB cap per file


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    total = len(s)
    e = 0.0
    for c in counts.values():
        p = c / total
        e -= p * math.log2(p)
    return e


def _entropy_threshold_for(path: Path, thresholds: Dict[str, Any]) -> float:
    ext = path.suffix.lower()
    text_ext = thresholds["thresholds"]["secrets_entropy_text"].get(
        "applies_to_extensions", [".md", ".txt", ".rst", ".tex", ".log"]
    )
    if ext in text_ext:
        return float(thresholds["thresholds"]["secrets_entropy_text"]["value"])
    return float(thresholds["thresholds"]["secrets_entropy_code"]["value"])


def _iter_pack_files(pack_dir: Path) -> List[Path]:
    out: List[Path] = []
    for root, dirs, fnames in os.walk(pack_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".git")]
        for f in fnames:
            p = Path(root) / f
            if p.suffix.lower() in TEXT_EXTENSIONS:
                out.append(p)
    return out


def _is_whitelisted_demo_path(file_path: Path, pack_dir: Path, demo_allowed: bool) -> bool:
    if not demo_allowed:
        return False
    try:
        rel = file_path.resolve().relative_to(pack_dir.resolve())
    except ValueError:
        return False
    parts = [p.lower() for p in rel.parts]
    return "_harness" in parts and "_fixtures" in parts and "inq" in parts


def _load_manifest_demo_flag(pack_dir: Path) -> bool:
    mpath = pack_dir / "TASK_MANIFEST.json"
    if not mpath.is_file():
        return False
    try:
        with mpath.open(encoding="utf-8") as f:
            d = json.load(f)
        return bool(d.get("demo_secrets_allowed", False))
    except Exception:
        return False


def _mask_token(token: str) -> str:
    if len(token) <= 8:
        return "[redacted]"
    return token[:6] + "...<redacted>..." + token[-2:]


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
    vb = VerdictBuilder(tool="inq_secrets", task_id=task_id, author=author, stage=stage)
    try:
        sigs = load_signatures(config_dir)
        thresholds = load_thresholds(config_dir)
    except Exception as e:
        vb.fail_closed(f"config_load_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec

    patterns = compile_secret_patterns(sigs)
    demo_allowed = _load_manifest_demo_flag(pack_dir)
    files = _iter_pack_files(pack_dir)
    findings: List[Dict[str, Any]] = []

    for fpath in files:
        try:
            if fpath.stat().st_size > MAX_FILE_BYTES:
                continue
            text = fpath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        ent_threshold = _entropy_threshold_for(fpath, thresholds)
        is_whitelisted = _is_whitelisted_demo_path(fpath, pack_dir, demo_allowed)
        try:
            rel = str(fpath.relative_to(pack_dir))
        except ValueError:
            rel = str(fpath)
        for name, rgx, spec in patterns:
            for m in rgx.finditer(text):
                token = m.group(1) if m.groups() else m.group(0)
                if spec.get("entropy_check"):
                    e = _shannon_entropy(token)
                    if e < ent_threshold:
                        continue
                else:
                    e = None
                line_no = text.count("\n", 0, m.start()) + 1
                findings.append({
                    "file": rel,
                    "line": line_no,
                    "pattern": name,
                    "match_preview": _mask_token(token),
                    "match_length": len(token),
                    "entropy": round(e, 3) if e is not None else None,
                    "whitelisted_demo": is_whitelisted,
                })

    real_findings = [f for f in findings if not f["whitelisted_demo"]]
    wl_findings = [f for f in findings if f["whitelisted_demo"]]

    if not real_findings:
        if wl_findings:
            vb.ok(f"clean ({len(files)} files; {len(wl_findings)} demo-whitelisted)")
        else:
            vb.ok(f"clean ({len(files)} files scanned, 0 findings)")
    else:
        if force_inq:
            vb.hint(
                "SECRETS_OVERRIDDEN",
                f"{len(real_findings)} secret findings overridden by --force-inq (author={author})",
            )
            vb.add_recommendation("override logged per charter I10; review _NEGATIVE_EXPERIENCE entry")
        else:
            vb.block(
                "SECRETS",
                f"{len(real_findings)} secret findings detected across {len({f['file'] for f in real_findings})} file(s)",
            )
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
            "tool": "inq_secrets",
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
