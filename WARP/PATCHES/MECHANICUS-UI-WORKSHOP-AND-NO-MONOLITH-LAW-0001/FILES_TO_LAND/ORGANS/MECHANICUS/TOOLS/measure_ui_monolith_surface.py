#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_TARGETS = [
    "SUPPORT/APP_TAURI/src/main.js",
    "SUPPORT/APP_TAURI/src/styles.css",
    "SUPPORT/APP_TAURI/src-tauri/src/main.rs",
]

SOFT = {
    ".js": 260,
    ".mjs": 260,
    ".ts": 260,
    ".css": 520,
    ".rs": 360,
    ".py": 320,
    ".ps1": 260,
}

BLOCKING_NEW = {
    ".js": 420,
    ".mjs": 420,
    ".ts": 420,
    ".css": 900,
    ".rs": 520,
    ".py": 520,
    ".ps1": 420,
}

def count_function_lengths(text: str) -> List[Dict[str, Any]]:
    lines = text.splitlines()
    out: List[Dict[str, Any]] = []
    for i, line in enumerate(lines):
        m = re.search(r"\bfunction\s+([A-Za-z0-9_]+)\s*\(", line)
        if not m:
            continue
        name = m.group(1)
        brace = 0
        started = False
        for j in range(i, len(lines)):
            brace += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]:
                started = True
            if started and brace == 0:
                out.append({"name": name, "start_line": i + 1, "end_line": j + 1, "lines": j - i + 1})
                break
    return out

def scan_file(path: Path, repo: Path) -> Dict[str, Any]:
    rel = path.relative_to(repo).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    ext = path.suffix.lower()
    soft = SOFT.get(ext, 300)
    block = BLOCKING_NEW.get(ext, 500)
    result: Dict[str, Any] = {
        "path": rel,
        "extension": ext,
        "bytes": path.stat().st_size,
        "line_count": len(lines),
        "soft_threshold": soft,
        "blocking_new_threshold": block,
        "soft_exceeded": len(lines) > soft,
        "blocking_new_exceeded": len(lines) > block,
        "function_lengths": count_function_lengths(text) if ext in {".js", ".mjs", ".ts"} else [],
        "css_selector_blocks": text.count("{") if ext == ".css" else None,
        "reference_bitmap_mode_detected": "reference-target-full.png" in text or "REFERENCE_FIDELITY_BITMAP" in text,
        "invisible_hit_zone_mode_detected": "opacity: 0 !important" in text and "pointer-events: auto" in text,
    }
    result["max_function_lines"] = max([f["lines"] for f in result["function_lengths"]], default=0)
    return result

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--targets", nargs="*", default=DEFAULT_TARGETS)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    scans: List[Dict[str, Any]] = []
    missing: List[str] = []

    for target in args.targets:
        path = (repo / target).resolve()
        if path.is_file():
            scans.append(scan_file(path, repo))
        else:
            missing.append(target)

    summary = {
        "tool_id": "mechanicus_ui_monolith_surface_scanner.v0_1",
        "repo_root": str(repo),
        "target_count": len(args.targets),
        "scanned_count": len(scans),
        "missing": missing,
        "files": scans,
        "monolith_debt": [s for s in scans if s["soft_exceeded"]],
        "blocking_new_debt": [s for s in scans if s["blocking_new_exceeded"]],
        "reference_bitmap_risks": [s for s in scans if s["reference_bitmap_mode_detected"] or s["invisible_hit_zone_mode_detected"]],
        "meaning": "Scanner reports monolith risk and reference-bitmap risk. It does not fail legacy debt by itself."
    }

    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.out:
        out = repo / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
