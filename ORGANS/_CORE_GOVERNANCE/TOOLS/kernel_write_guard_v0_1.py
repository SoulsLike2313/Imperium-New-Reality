#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kernel_write_guard_v0_1.py
==========================
CANONICAL_PIPELINE stage 3 (BOUNDARY) guard. Parses
KERNEL_BOUNDARY_CONTRACT.md §2 to derive kernel patterns and emits a verdict
receipt for a list of changed paths.

OBSERVER mode (default for v0_1): always exits 0. Verdict is logged for audit
but never blocks. ENFORCED mode is toggled when
ORGANS/_CORE_GOVERNANCE/EMPEROR/SEAL_STATUS.json:mode == "ENFORCED". In
ENFORCED mode, verdict DENY exits 1.

NO_LLM_IN_PIPELINE: pure stdlib, deterministic.

Usage:
    python3 kernel_write_guard_v0_1.py \
        --changed-paths changed.txt --task-id DOCTR-TOOLS-0001 \
        --actor-role LOGOS_PRIME --bypass owner_manual
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import sys
from pathlib import Path


SCHEMA_VERSION = "imperium.kernel_write_guard.v0_1"
TOOL_NAME = "kernel_write_guard_v0_1"

KERNEL_BOUNDARY_LAW = "ORGANS/DOCTRINARIUM/LAWS/KERNEL_BOUNDARY_CONTRACT.md"
SEAL_STATUS_PATH = "ORGANS/_CORE_GOVERNANCE/EMPEROR/SEAL_STATUS.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_run_dir_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def parse_kernel_patterns(law_path: Path) -> list[str]:
    """Extract kernel patterns from §2 of KERNEL_BOUNDARY_CONTRACT.md.

    The section is delimited by '## §2 KERNEL_PATTERNS' (header) and the next
    '## ' header. Patterns live inside a triple-backtick code block within
    that section.
    """
    text = law_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_section = False
    in_code = False
    patterns: list[str] = []
    for line in lines:
        if line.startswith("## ") and "KERNEL_PATTERNS" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                patterns.append(stripped)
    return patterns


def load_seal_mode(repo_root: Path) -> str:
    fp = repo_root / SEAL_STATUS_PATH
    if not fp.exists():
        return "OBSERVER"
    try:
        data = json.loads(fp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "OBSERVER"
    mode = data.get("mode", "OBSERVER")
    return mode if mode in ("OBSERVER", "ENFORCED") else "OBSERVER"


def classify(changed_paths: list[str], patterns: list[str]) -> list[str]:
    touched: list[str] = []
    for cp in changed_paths:
        normalized = cp.replace("\\", "/").lstrip("./")
        for pat in patterns:
            if fnmatch.fnmatchcase(normalized, pat) or _glob_double_star(normalized, pat):
                touched.append(normalized)
                break
    return touched


def _glob_double_star(path: str, pattern: str) -> bool:
    """fnmatch does not honor '**' as recursive glob; emulate it."""
    if "**" not in pattern:
        return False
    # Split on '**', match prefix and suffix anchored.
    parts = pattern.split("**")
    if len(parts) == 1:
        return fnmatch.fnmatchcase(path, pattern)
    cursor = 0
    # Prefix
    head = parts[0]
    if head and not path.startswith(head):
        return False
    cursor = len(head)
    # Middle segments: each must be findable in order.
    for mid in parts[1:-1]:
        if not mid:
            continue
        idx = path.find(mid, cursor)
        if idx < 0:
            return False
        cursor = idx + len(mid)
    tail = parts[-1]
    if tail and not path.endswith(tail):
        return False
    return True


def build_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog=TOOL_NAME, description="Imperium kernel-write guard (CANONICAL_PIPELINE stage 3).")
    p.add_argument("--repo-root", default=".", help="Repository root (default cwd).")
    p.add_argument("--changed-paths", required=True, help="Path to a file containing one repo-relative changed path per line.")
    p.add_argument("--task-id", default=None, help="Pack task_id for receipt.")
    p.add_argument("--commit-sha", default=None, help="Commit sha for receipt.")
    p.add_argument("--actor-role", default="LOGOS_PRIME", help="Declared actor role.")
    p.add_argument("--bypass", choices=["none", "owner_manual"], default="none", help="Declared bypass.")
    p.add_argument("--seal-factors", default="", help="Comma-separated EMPEROR_SEAL factors present.")
    p.add_argument("--threshold", choices=["2_of_3", "3_of_3"], default=None, help="Required seal threshold for this operation.")
    p.add_argument("--output-dir", default=None, help="Override receipt output dir.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = build_args(argv)
    repo_root = Path(args.repo_root).resolve()

    law_path = repo_root / KERNEL_BOUNDARY_LAW
    if not law_path.exists():
        sys.stderr.write(f"[guard] KERNEL_BOUNDARY_CONTRACT not found at {KERNEL_BOUNDARY_LAW}\n")
        return 2
    patterns = parse_kernel_patterns(law_path)
    if not patterns:
        sys.stderr.write("[guard] KERNEL_BOUNDARY_CONTRACT §2 parsed zero patterns; refusing.\n")
        return 2

    changed_file = Path(args.changed_paths)
    if not changed_file.exists():
        sys.stderr.write(f"[guard] changed-paths file not found: {args.changed_paths}\n")
        return 2
    changed = [ln.strip() for ln in changed_file.read_text(encoding="utf-8").splitlines() if ln.strip()]

    touched = classify(changed, patterns)
    mode = load_seal_mode(repo_root)
    bypass_declared = (args.bypass == "owner_manual")
    seal_factors = [f.strip() for f in args.seal_factors.split(",") if f.strip()]

    deny_reasons: list[str] = []
    if touched:
        if bypass_declared:
            verdict = "ALLOW_WITH_BYPASS"
        elif seal_factors:
            need = 2 if args.threshold == "2_of_3" or args.threshold is None else 3
            if len(seal_factors) >= need:
                verdict = "ALLOW"
            else:
                verdict = "DENY"
                deny_reasons.append(f"Seal threshold not met: have {len(seal_factors)}, need {need}.")
        else:
            verdict = "DENY"
            deny_reasons.append("Kernel paths touched without bypass or seal factors.")
    else:
        verdict = "ALLOW"

    receipt = {
        "schema_version":       SCHEMA_VERSION,
        "mode":                 mode,
        "task_id":              args.task_id,
        "commit_sha":           args.commit_sha,
        "changed_paths":        changed,
        "kernel_paths_touched": touched,
        "kernel_patterns_used": patterns,
        "verdict":              verdict,
        "authority": {
            "actor_role":       args.actor_role,
            "factors_present":  seal_factors,
            "threshold":        args.threshold,
            "bypass_declared":  bypass_declared,
            "bypass_authority": "OWNER_MANUAL" if bypass_declared else "NONE",
            "seal_ttl_seconds": None,
            "seal_issued_at":   None,
            "seal_expires_at":  None,
        },
        "deny_reasons":        deny_reasons,
        "verified_at":         utc_now_iso(),
        "verifier":            TOOL_NAME,
        "law_sha256":          sha256_file(law_path),
        "prior_receipt_sha256":None,
        "ledger_seq":          None,
    }

    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = repo_root / "_HARNESS" / "_RUNS" / utc_run_dir_stamp() / "KERNEL_GUARD"
    out_dir.mkdir(parents=True, exist_ok=True)

    sid = args.commit_sha or args.task_id or "adhoc"
    safe_sid = str(sid).replace(":", "-").replace("/", "-")
    out_path = out_dir / f"{safe_sid}.json"
    out_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sys.stdout.write(f"[guard] mode={mode} verdict={verdict} touched={len(touched)} receipt={out_path}\n")

    if mode == "ENFORCED" and verdict in ("DENY", "INVALID"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
