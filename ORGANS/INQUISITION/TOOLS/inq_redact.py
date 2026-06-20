#!/usr/bin/env python3
"""inq_redact.py -- Inquisition redaction scanner.

v0_1 scope: scanner only. Walks JSON / JSONL files in --pack-dir, applies
redaction targets from REDACTION_PATTERNS.json, emits HINT_REDACT_TARGETS
listing all matches. In PRE-ADMIT (default --dry-run), no file is mutated.

With --apply, a sanitized copy of each affected file is written under
--out-dir (default `_HARNESS/_NEGATIVE_EXPERIENCE/<task_id>/sanitized/`).
Originals in --pack-dir are never overwritten.

Charter rules honored:
  - Recursive deep scan over nested JSON objects/arrays (Q10 recursive=true).
  - Mask token from REDACTION_PATTERNS.mask_token (default <<INQ_REDACTED>>).
  - Token-like detection reuses SIGNATURES.secrets patterns.

CLI:
  inq_redact.py --pack-dir <dir> --task-id <id> --author <a> --stage <s>
                [--reports-dir <dir>] [--apply] [--out-dir <dir>]
                [--config-dir <dir>]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inq_report import VerdictBuilder, EXIT_INPUT_INVALID
from inq_patterns import compile_secret_patterns, load_redaction, load_signatures


def _iter_json_files(pack_dir: Path) -> List[Path]:
    out: List[Path] = []
    for root, dirs, fnames in os.walk(pack_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".git")]
        for f in fnames:
            if f.endswith(".json") or f.endswith(".jsonl"):
                out.append(Path(root) / f)
    return out


def _looks_token_like(s: Any, secret_pats) -> bool:
    if not isinstance(s, str):
        return False
    for _, rgx, _ in secret_pats:
        if rgx.search(s):
            return True
    return False


def _key_matches_rule(key: str, rule: Dict[str, Any]) -> bool:
    km = rule.get("key_match")
    if km and km == key:
        return True
    kmr = rule.get("key_match_regex")
    if kmr:
        try:
            if re.search(kmr, key):
                return True
        except re.error:
            pass
    return False


def _path_matches_rule(file_path: Path, pack_dir: Path, rule: Dict[str, Any]) -> bool:
    pm = rule.get("path_match")
    if not pm:
        return True  # rule without path filter applies to all files
    try:
        rel = str(file_path.resolve().relative_to(pack_dir.resolve()))
    except ValueError:
        rel = str(file_path)
    return pm in rel


def _walk(
    node: Any,
    json_path: List[str],
    file_path: Path,
    pack_dir: Path,
    rules: Dict[str, Dict[str, Any]],
    secret_pats,
    findings: List[Dict[str, Any]],
    apply: bool,
    mask: str,
) -> Any:
    if isinstance(node, dict):
        new_d: Dict[str, Any] = {}
        for k, v in node.items():
            child_path = json_path + [str(k)]
            new_v = _walk(v, child_path, file_path, pack_dir, rules, secret_pats, findings, apply, mask)
            redact_this = False
            for rname, rule in rules.items():
                if not _path_matches_rule(file_path, pack_dir, rule):
                    continue
                if not _key_matches_rule(str(k), rule):
                    continue
                if rule.get("redact_always"):
                    redact_this = True
                    findings.append({
                        "file": str(file_path),
                        "json_path": ".".join(child_path),
                        "rule": rname,
                        "reason": "key_match_always",
                    })
                elif rule.get("redact_if_token_like") and _looks_token_like(new_v, secret_pats):
                    redact_this = True
                    findings.append({
                        "file": str(file_path),
                        "json_path": ".".join(child_path),
                        "rule": rname,
                        "reason": "token_like_in_value",
                    })
            if redact_this and apply:
                new_d[k] = mask
            else:
                new_d[k] = new_v
        return new_d
    if isinstance(node, list):
        return [
            _walk(v, json_path + [f"[{i}]"], file_path, pack_dir, rules, secret_pats, findings, apply, mask)
            for i, v in enumerate(node)
        ]
    return node


def scan(
    pack_dir: Path,
    *,
    task_id: str,
    author: str,
    stage: str,
    reports_dir: str,
    config_dir: Optional[Path],
    apply: bool,
    out_dir: Optional[Path],
) -> int:
    vb = VerdictBuilder(tool="inq_redact", task_id=task_id, author=author, stage=stage)
    try:
        red = load_redaction(config_dir)
        sigs = load_signatures(config_dir)
    except Exception as e:
        vb.fail_closed(f"config_load_error: {type(e).__name__}: {e}")
        _, _, ec = vb.write(reports_dir=reports_dir)
        return ec

    secret_pats = compile_secret_patterns(sigs)
    rules = red.get("targets", {})
    mask = red.get("mask_token", "<<INQ_REDACTED>>")

    files = _iter_json_files(pack_dir)
    findings: List[Dict[str, Any]] = []
    sanitized: List[str] = []

    for jf in files:
        try:
            if jf.suffix == ".jsonl":
                if not apply:
                    with jf.open(encoding="utf-8") as f:
                        for lineno, line in enumerate(f, 1):
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                d = json.loads(line)
                            except json.JSONDecodeError:
                                continue
                            local: List[Dict[str, Any]] = []
                            _walk(d, [f"#{lineno}"], jf, pack_dir, rules, secret_pats, local, False, mask)
                            findings.extend(local)
                continue
            with jf.open(encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        local_findings: List[Dict[str, Any]] = []
        new_d = _walk(d, [], jf, pack_dir, rules, secret_pats, local_findings, apply, mask)
        findings.extend(local_findings)
        if apply and local_findings and out_dir is not None:
            try:
                rel = jf.resolve().relative_to(pack_dir.resolve())
            except ValueError:
                rel = Path(jf.name)
            target = (out_dir / rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(new_d, ensure_ascii=False, indent=2), encoding="utf-8")
            sanitized.append(str(target))

    if findings:
        if apply:
            vb.hint(
                "REDACT_APPLIED",
                f"{len(findings)} redaction findings; {len(sanitized)} sanitized file(s) written under {out_dir}",
            )
        else:
            vb.hint(
                "REDACT_TARGETS",
                f"{len(findings)} redaction findings (dry-run; pack not mutated)",
            )
    else:
        vb.ok(f"clean ({len(files)} JSON file(s) scanned, 0 redaction targets matched)")
    for f in findings:
        vb.add_finding(**f)
    if sanitized:
        vb.set_evidence(";".join(sanitized))
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
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--config-dir", default=None)
    args = ap.parse_args()
    pack_dir = Path(args.pack_dir).resolve()
    if not pack_dir.is_dir():
        d = {
            "schema_version": "inq.verdict.v0_1",
            "verdict": "FAIL_CLOSED",
            "stage": args.stage,
            "reasons": [f"pack_dir not a directory: {pack_dir}"],
            "tool": "inq_redact",
            "task_id": args.task_id,
            "author": args.author,
            "exit_code": EXIT_INPUT_INVALID,
        }
        sys.stdout.write(json.dumps(d, ensure_ascii=False) + "\n")
        return EXIT_INPUT_INVALID
    out_dir = None
    if args.apply:
        out_dir = Path(args.out_dir).resolve() if args.out_dir else (
            Path("_HARNESS/_NEGATIVE_EXPERIENCE") / args.task_id / "sanitized"
        )
        out_dir.mkdir(parents=True, exist_ok=True)
    return scan(
        pack_dir,
        task_id=args.task_id,
        author=args.author,
        stage=args.stage,
        reports_dir=args.reports_dir,
        config_dir=Path(args.config_dir).resolve() if args.config_dir else None,
        apply=args.apply,
        out_dir=out_dir,
    )


if __name__ == "__main__":
    sys.exit(main())
