#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imperium.passport_index.v0_1 - passport_index_builder v0_1

Walks the repository, finds every *_tool_passport_v*.json under ORGANS/,
validates each against imperium.tool_passport.v0_2 (best-effort, stdlib only),
and emits a passport_index.json conforming to imperium.passport_index.v0_1.

Owner-gated: false. Exec mode: static. Safe to run unattended.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import time
from pathlib import Path
from typing import Tuple, List, Dict, Any

try:
    from rich.console import Console
    from rich.table import Table
    HAS_RICH = True
except Exception:
    HAS_RICH = False

PASSPORT_GLOB_RE = re.compile(r"^.+_tool_passport_v[0-9_]+\.json$")
SCHEMA_ID_V0_2 = "imperium.tool_passport.v0_2"
REQUIRED_V0_2 = {
    "schema_id", "tool_id", "name", "version", "owner_organ",
    "lang", "validators", "exec_mode", "owner_gated",
}
TOOL_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
VERSION_RE = re.compile(r"^v[0-9]+(_[0-9]+)*$")
VALID_EXEC_MODES = {"static", "sim", "paper", "shadow", "live"}


def find_passports(repo_root: Path) -> List[Path]:
    organs = repo_root / "ORGANS"
    if not organs.is_dir():
        return []
    results: List[Path] = []
    for path in organs.rglob("*.json"):
        if PASSPORT_GLOB_RE.match(path.name):
            results.append(path)
    return sorted(results)


def validate_passport(data: Dict[str, Any]) -> Tuple[str, bool, List[str]]:
    """Returns (schema_version, valid, errors)."""
    errors: List[str] = []
    schema_id = data.get("schema_id", "")
    if schema_id == SCHEMA_ID_V0_2:
        missing = REQUIRED_V0_2 - set(data.keys())
        if missing:
            errors.append(f"missing required keys: {sorted(missing)}")
        tid = data.get("tool_id", "")
        if not isinstance(tid, str) or not TOOL_ID_RE.match(tid):
            errors.append(f"tool_id must match ^[a-z][a-z0-9_]*$, got {tid!r}")
        ver = data.get("version", "")
        if not isinstance(ver, str) or not VERSION_RE.match(ver):
            errors.append(f"version must match ^v[0-9]+(_[0-9]+)*$, got {ver!r}")
        em = data.get("exec_mode", "")
        if em not in VALID_EXEC_MODES:
            errors.append(f"exec_mode must be one of {sorted(VALID_EXEC_MODES)}, got {em!r}")
        if not isinstance(data.get("owner_gated"), bool):
            errors.append("owner_gated must be boolean")
        validators = data.get("validators")
        if not isinstance(validators, list) or len(validators) < 1:
            errors.append("validators must be a non-empty array")
        else:
            for i, v in enumerate(validators):
                if not isinstance(v, dict) or not v.get("name") or not v.get("exec"):
                    errors.append(f"validators[{i}] missing name or exec")
        return "v0_2", len(errors) == 0, errors
    if isinstance(schema_id, str) and schema_id.startswith("imperium.") and ".v0_1" in schema_id:
        return "v0_1", True, ["legacy v0_1 passport (no v0_2 contract enforced)"]
    return "unknown", False, [f"unknown schema_id: {schema_id!r}"]


def derive_organ(passport_path: Path, repo_root: Path) -> str:
    try:
        rel = passport_path.relative_to(repo_root / "ORGANS")
        return rel.parts[0]
    except ValueError:
        return "UNKNOWN"


def build_index(repo_root: Path) -> Dict[str, Any]:
    passports = find_passports(repo_root)
    entries: List[Dict[str, Any]] = []
    by_organ:      Dict[str, int] = {}
    by_lang:       Dict[str, int] = {}
    by_exec_mode:  Dict[str, int] = {}
    by_capability: Dict[str, int] = {}
    v0_2_count = 0
    v0_1_count = 0
    bad_count  = 0
    error_entries: List[Dict[str, Any]] = []

    for ppath in passports:
        rel_pp = str(ppath.relative_to(repo_root)).replace("\\", "/")
        try:
            data = json.loads(ppath.read_text(encoding="utf-8-sig"))
        except Exception as e:
            bad_count += 1
            error_entries.append({"passport_path": rel_pp, "error": f"parse: {e}"})
            entries.append({
                "passport_path": rel_pp, "tool_id": "?",
                "schema_version": "unknown", "schema_valid": False,
                "validators_count": 0, "tool_path": "", "tool_exists": False,
            })
            continue

        schema_version, valid, errs = validate_passport(data)
        if schema_version == "v0_2":
            v0_2_count += 1
        elif schema_version == "v0_1":
            v0_1_count += 1
        else:
            bad_count += 1
        if errs and schema_version != "v0_1":
            error_entries.append({"passport_path": rel_pp, "errors": errs})

        organ = data.get("owner_organ") or derive_organ(ppath, repo_root)
        lang = data.get("lang", "unknown")
        exec_mode = data.get("exec_mode", "unknown")
        caps = data.get("capability_tags") or []
        tool_path = data.get("tool_path", "")
        tool_exists = bool(tool_path) and (repo_root / tool_path).is_file()

        by_organ[organ] = by_organ.get(organ, 0) + 1
        by_lang[lang] = by_lang.get(lang, 0) + 1
        by_exec_mode[exec_mode] = by_exec_mode.get(exec_mode, 0) + 1
        for c in caps:
            by_capability[c] = by_capability.get(c, 0) + 1

        entries.append({
            "passport_path":    rel_pp,
            "tool_id":          data.get("tool_id", "?"),
            "name":             data.get("name", ""),
            "version":          data.get("version", ""),
            "owner_organ":      organ,
            "lang":             lang,
            "exec_mode":        exec_mode,
            "schema_version":   schema_version,
            "schema_valid":     valid,
            "validators_count": len(data.get("validators") or []),
            "tool_path":        tool_path,
            "tool_exists":      tool_exists,
        })

    return {
        "schema_id":       "imperium.passport_index.v0_1",
        "generated_at":    _dt.datetime.now().astimezone().isoformat(),
        "generator":       "passport_index_builder_v0_1.py",
        "repo_root":       str(repo_root),
        "total_passports": len(entries),
        "schema_compliance": {
            "v0_2_compliant": v0_2_count,
            "v0_1_legacy":    v0_1_count,
            "non_compliant":  bad_count,
            "errors":         error_entries,
        },
        "by_organ":      by_organ,
        "by_lang":       by_lang,
        "by_exec_mode":  by_exec_mode,
        "by_capability": by_capability,
        "passports":     entries,
    }


def render(index: Dict[str, Any]) -> None:
    if not HAS_RICH:
        print(json.dumps({
            "total_passports": index["total_passports"],
            "schema_compliance": index["schema_compliance"],
            "by_organ": index["by_organ"],
            "by_lang": index["by_lang"],
        }, ensure_ascii=False, indent=2))
        return
    c = Console()
    t = Table(title="Imperium \u00b7 Passport Index", title_style="bold gold1")
    t.add_column("tool_id", style="bold")
    t.add_column("organ")
    t.add_column("lang")
    t.add_column("ver")
    t.add_column("mode")
    t.add_column("schema")
    t.add_column("\u2713", justify="center")
    t.add_column("V#", justify="right")
    t.add_column("file?", justify="center")
    t.add_column("passport_path", overflow="fold")
    for p in index["passports"]:
        ok = "[green]\u2713[/]" if p["schema_valid"] else "[red]\u2717[/]"
        fx = "[green]\u2713[/]" if p.get("tool_exists") else "[yellow]?[/]"
        t.add_row(
            str(p.get("tool_id", "?")),
            str(p.get("owner_organ", "?")),
            str(p.get("lang", "?")),
            str(p.get("version", "")),
            str(p.get("exec_mode", "")),
            str(p.get("schema_version", "?")),
            ok,
            str(p.get("validators_count", 0)),
            fx,
            str(p.get("passport_path", "")),
        )
    c.print(t)
    sc = index["schema_compliance"]
    c.print(
        f"\n[bold]total[/]: {index['total_passports']}  "
        f"\u00b7  [green]v0_2[/]: {sc['v0_2_compliant']}  "
        f"\u00b7  [yellow]v0_1 legacy[/]: {sc['v0_1_legacy']}  "
        f"\u00b7  [red]non-compliant[/]: {sc['non_compliant']}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Imperium passport index v0_1")
    ap.add_argument("--repo", default=".", help="Repository root (default: cwd)")
    ap.add_argument("--out",  default=None, help="Output JSON path")
    ap.add_argument("--self-test", action="store_true", help="Run synthetic self-test and exit")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        synth_ok = {
            "schema_id": SCHEMA_ID_V0_2, "tool_id": "synth_tool", "name": "Synth",
            "version": "v0_1", "owner_organ": "MECHANICUS", "lang": "python",
            "validators": [{"name": "x", "exec": "echo ok"}],
            "exec_mode": "static", "owner_gated": True,
        }
        synth_bad = {"schema_id": "imperium.unknown.v0_0"}
        sv1, ok1, _ = validate_passport(synth_ok)
        sv2, ok2, errs2 = validate_passport(synth_bad)
        print(f"self-test ok-passport : version={sv1} valid={ok1}")
        print(f"self-test bad-passport: version={sv2} valid={ok2} errors={errs2}")
        return 0 if (ok1 and not ok2) else 1

    repo_root = Path(args.repo).resolve()
    if not (repo_root / "ORGANS").is_dir():
        print(f"error: ORGANS/ not found at {repo_root}", file=sys.stderr)
        return 2

    t0 = time.monotonic()
    index = build_index(repo_root)
    dt = time.monotonic() - t0

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.quiet:
        render(index)
        print(f"\nelapsed: {int(dt*1000)} ms")
        if args.out:
            print(f"index  : {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
