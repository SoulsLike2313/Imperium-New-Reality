#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
passport_v0_2_auto_registrar

Mechanicus tool: scans legacy v0_1 tool-passports in the repo, infers v0_2 fields
from paired source files (lang from ext, validators from CLI flags, exec_mode
from --apply/--dry-run hints, owner_gated from destructive ops), and writes
v0_2 draft passports beside originals. Never deletes v0_1 (additive doctrine).

Usage:
    python passport_v0_2_auto_registrar.py --self-test
    python passport_v0_2_auto_registrar.py --repo <repo_root> --out <ledger.json> --dry-run
    python passport_v0_2_auto_registrar.py --repo <repo_root> --out <ledger.json> --apply

Output statuses (per entry):
    drafted              - written as <tool>_tool_passport_v0_2.json with _draft=true
    registered           - written, all fields high-confidence, _draft=false
    skipped_v0_2_exists  - v0_2 target file already present
    skipped_not_legacy   - input not recognized as legacy tool-passport
    skipped_meta_schema  - input is a JSON schema, not a tool passport
    skipped_not_a_tool_passport - input is organ block / data atlas passport
    parse_error          - JSON parse failure

Exit codes:
    0   all entries handled cleanly
    1   one or more parse_error entries (non-fatal warning)
    2   fatal error (bad CLI args, repo not found)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_ID_V0_2 = "imperium.tool_passport.v0_2"
LEDGER_SCHEMA_ID = "imperium.passport_v0_2_registration_ledger.v0_1"
REGISTRAR_VERSION = "v0_2"

# ---------- helpers ----------

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> Optional[dict]:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    # tolerate utf-8 with optional BOM
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)
    path.write_bytes(text.encode("utf-8"))


# ---------- classification ----------

_LEGACY_FILE_RE = re.compile(r"^(.+)_tool_passport[s]?_v[0-9_]+\.json$")
_META_SCHEMA_NAMES = (
    "tool_passport_schema",
    "imperium_tool_passport",
    "imperium_passport_index",
    "file_passport_schema",
)


def _classify(passport_path: Path, j: Optional[dict]) -> str:
    name = passport_path.name
    name_lower = name.lower()
    posix = passport_path.as_posix()

    if j is None:
        return "parse_error"

    if name_lower.endswith(".schema.json"):
        return "skipped_meta_schema"
    for stem in _META_SCHEMA_NAMES:
        if name_lower.startswith(stem):
            return "skipped_meta_schema"

    if "ORGAN_BLOCK_PASSPORT" in name or "/BLOCK/PASSPORT/" in posix:
        return "skipped_not_a_tool_passport"
    if "DATA_ATLAS_PASSPORT" in name or "/DATA_ATLAS/" in posix:
        return "skipped_not_a_tool_passport"

    schema_id = (j.get("schema_id") or "").lower()
    if schema_id == SCHEMA_ID_V0_2:
        return "skipped_already_v0_2"

    if "tool_passport" in schema_id:
        return "legacy"
    if _LEGACY_FILE_RE.match(name):
        return "legacy"

    return "unknown_shape"


# ---------- inference ----------

_OWNER_FROM_PATH = (
    ("/MECHANICUS/", "MECHANICUS"),
    ("/INQUISITION/", "INQUISITION"),
    ("/DOCTRINARIUM/", "DOCTRINARIUM"),
    ("/ADMINISTRATUM/", "ADMINISTRATUM"),
    ("/ASTRONOMICON/", "ASTRONOMICON"),
    ("/IMPERIAL_IDE/", "IMPERIAL_IDE"),
    ("/OFFICIO_AGENTIS/", "OFFICIO_AGENTIS"),
    ("/SPECULUM/", "SPECULUM"),
    ("/OBSERVATORIUM/", "OBSERVATORIUM"),
    ("/_CORE_GOVERNANCE/", "_CORE_GOVERNANCE"),
)

_OWNER_FROM_PREFIX = (
    ("inquisition_", "INQUISITION"),
    ("trinity_", "MECHANICUS"),
    ("warp_", "MECHANICUS"),
    ("patch_", "MECHANICUS"),
    ("evidence_", "INQUISITION"),
    ("imperium_", "_CORE_GOVERNANCE"),
    ("seed_", "MECHANICUS"),
    ("hygiene_", "INQUISITION"),
)

_LANG_BY_EXT = {
    ".py": "python",
    ".ps1": "powershell",
    ".psm1": "powershell",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".md": "markdown",
    ".html": "html",
    ".css": "css",
}

_DESTRUCTIVE_RE = re.compile(
    r"(os\.remove|shutil\.rmtree|os\.unlink|Remove-Item|--force\b|--apply\b|git\s+commit|git\s+push|os\.rename)",
    re.IGNORECASE,
)


def _extract_tool_id(passport_path: Path) -> str:
    base = passport_path.stem  # without .json
    m = _LEGACY_FILE_RE.match(passport_path.name)
    if m:
        return m.group(1)
    return base


def _infer_owner(passport_path: Path, existing_owner: Optional[str], tool_id: str) -> Tuple[str, str]:
    if existing_owner and isinstance(existing_owner, str):
        return existing_owner, "preserved"
    posix = passport_path.as_posix()
    for needle, owner in _OWNER_FROM_PATH:
        if needle in posix:
            return owner, "from_path"
    for prefix, owner in _OWNER_FROM_PREFIX:
        if tool_id.startswith(prefix):
            return owner, "from_tool_id_prefix"
    return "MECHANICUS", "fallback_default"


def _find_paired_source(repo_root: Path, tool_id: str) -> List[Path]:
    """Search ORGANS/** for files whose stem starts with tool_id or equals tool_id."""
    matches: List[Path] = []
    organs = repo_root / "ORGANS"
    if not organs.is_dir():
        return matches
    exts = set(_LANG_BY_EXT.keys())
    # skip extensions we don't want as "source of tool"
    skip_lang_exts = {".md", ".html", ".css"}
    tool_id_l = tool_id.lower()
    for p in organs.rglob("*"):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext not in exts:
            continue
        if ext in skip_lang_exts:
            continue
        stem_l = p.stem.lower()
        if stem_l == tool_id_l or stem_l.startswith(tool_id_l + "_") or stem_l.startswith(tool_id_l + "."):
            matches.append(p)
    # rank: shortest path first (canonical placement preferred)
    matches.sort(key=lambda x: (len(x.as_posix()), x.as_posix()))
    return matches[:5]


def _scan_source_hints(src: Path) -> Dict[str, bool]:
    try:
        body = src.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    return {
        "has_self_test":   "--self-test" in body,
        "has_dry_run":     "--dry-run" in body,
        "has_apply":       "--apply" in body,
        "has_argparse":    ("argparse" in body) or ("ArgumentParser" in body),
        "has_destructive": bool(_DESTRUCTIVE_RE.search(body)),
        "has_git_write":   bool(re.search(r"git\s+(commit|push|add)", body)),
    }


def _build_validators(lang: str, hints: Dict[str, bool]) -> List[dict]:
    if lang == "python":
        v = [{
            "id": "syntax",
            "type": "command",
            "command": "python -m py_compile {tool_path}",
            "timeout_seconds": 10,
        }]
        if hints.get("has_self_test"):
            v.append({
                "id": "self_test",
                "type": "command",
                "command": "python {tool_path} --self-test",
                "timeout_seconds": 30,
            })
        if hints.get("has_argparse"):
            v.append({
                "id": "help",
                "type": "command",
                "command": "python {tool_path} --help",
                "timeout_seconds": 5,
            })
        return v
    if lang == "powershell":
        return [{
            "id": "syntax",
            "type": "command",
            "command": "powershell -NoProfile -Command \"& { [scriptblock]::Create((Get-Content -Raw -LiteralPath '{tool_path}')) | Out-Null }\"",
            "timeout_seconds": 10,
        }]
    if lang == "typescript":
        return [{
            "id": "tsc_noemit",
            "type": "command",
            "command": "tsc --noEmit {tool_path}",
            "timeout_seconds": 60,
        }]
    if lang == "rust":
        return [{
            "id": "cargo_check",
            "type": "command",
            "command": "cargo check --manifest-path {tool_path}",
            "timeout_seconds": 180,
        }]
    return []


def _infer_exec_mode(hints: Dict[str, bool]) -> str:
    if hints.get("has_apply"):
        return "live"
    if hints.get("has_dry_run"):
        return "paper"
    return "static"


def _infer_owner_gated(hints: Dict[str, bool]) -> bool:
    if hints.get("has_destructive") or hints.get("has_git_write") or hints.get("has_apply"):
        return True
    return False


def _humanize(tool_id: str) -> str:
    parts = tool_id.replace("_", " ").split()
    return " ".join(p.capitalize() for p in parts)


# ---------- core register ----------

def register_one(passport_path: Path, repo_root: Path, dry_run: bool) -> dict:
    rel = passport_path.relative_to(repo_root).as_posix() if passport_path.is_relative_to(repo_root) else passport_path.as_posix()
    j = _read_json(passport_path)
    cls = _classify(passport_path, j)

    if cls in ("parse_error", "skipped_meta_schema", "skipped_not_a_tool_passport", "skipped_already_v0_2", "unknown_shape"):
        return {
            "path": rel,
            "status": "skipped_not_legacy" if cls == "unknown_shape" else cls,
            "reason": cls,
        }

    # legacy -> compute v0_2
    assert j is not None  # narrowing
    tool_id = _extract_tool_id(passport_path)
    target_name = passport_path.with_name(f"{tool_id}_tool_passport_v0_2.json")

    if target_name.exists():
        return {
            "path": rel,
            "status": "skipped_v0_2_exists",
            "target": target_name.relative_to(repo_root).as_posix() if target_name.is_relative_to(repo_root) else target_name.as_posix(),
        }

    owner_organ, owner_source = _infer_owner(passport_path, j.get("owner_organ"), tool_id)

    sources = _find_paired_source(repo_root, tool_id)
    lang: Optional[str] = None
    hints: Dict[str, bool] = {}
    src_used: Optional[Path] = None
    confidence: Dict[str, str] = {"owner_organ": owner_source}

    if sources:
        src_used = sources[0]
        lang = _LANG_BY_EXT.get(src_used.suffix.lower())
        hints = _scan_source_hints(src_used)
        confidence["lang"] = "from_source_ext"
    else:
        existing_lang = j.get("lang")
        if isinstance(existing_lang, str) and existing_lang:
            lang = existing_lang
            confidence["lang"] = "preserved"
        else:
            lang = "python"  # safe default; flagged as draft
            confidence["lang"] = "fallback_default"

    validators = _build_validators(lang or "python", hints)
    if validators:
        confidence["validators"] = "auto_built" if sources else "auto_minimal"
    exec_mode = _infer_exec_mode(hints) if sources else "static"
    confidence["exec_mode"] = "from_source_scan" if sources else "fallback_default"
    owner_gated = _infer_owner_gated(hints) if sources else True
    confidence["owner_gated"] = "from_source_scan" if sources else "safe_default_true"

    # high confidence when source found AND at least 1 validator AND owner from path/preserved
    is_complete = bool(sources) and len(validators) >= 1 and owner_source in ("preserved", "from_path")

    name_v = j.get("name") if isinstance(j.get("name"), str) and j.get("name") else _humanize(tool_id)

    target: Dict[str, Any] = {
        "schema_id": SCHEMA_ID_V0_2,
        "tool_id": tool_id,
        "name": name_v,
        "version": "v0_2",
        "owner_organ": owner_organ,
        "lang": lang,
        "validators": validators,
        "exec_mode": exec_mode,
        "owner_gated": owner_gated,
        "_draft": (not is_complete),
        "_auto_registered_at": _utc_now_iso(),
        "_auto_registrar_version": REGISTRAR_VERSION,
        "_confidence": confidence,
        "_source_paths": [
            (s.relative_to(repo_root).as_posix() if s.is_relative_to(repo_root) else s.as_posix())
            for s in sources
        ],
        "_legacy_passport_path": rel,
    }

    # preserve user-defined extras from legacy (non-conflicting keys)
    reserved = set(target.keys()) | {"schema_id", "validators"}
    extras = {k: v for k, v in j.items() if k not in reserved and not k.startswith("_")}
    if extras:
        target["_legacy_extras"] = extras

    result = {
        "path": rel,
        "status": "drafted" if target["_draft"] else "registered",
        "target": target_name.relative_to(repo_root).as_posix() if target_name.is_relative_to(repo_root) else target_name.as_posix(),
        "tool_id": tool_id,
        "owner_organ": owner_organ,
        "lang": lang,
        "exec_mode": exec_mode,
        "owner_gated": owner_gated,
        "validators_count": len(validators),
        "sources_found": len(sources),
        "confidence": confidence,
    }

    if not dry_run:
        _write_json(target_name, target)
        result["written"] = True
    else:
        result["written"] = False

    return result


# ---------- search ----------

_SEARCH_GLOBS = (
    "ORGANS/**/*_tool_passport_v*.json",
    "ORGANS/**/*_tool_passports_v*.json",
    "ORGANS/**/PASSPORTS/*.json",
)


def _find_passports(repo_root: Path) -> List[Path]:
    seen: Dict[str, Path] = {}
    for pat in _SEARCH_GLOBS:
        for p in repo_root.glob(pat):
            if p.is_file():
                seen[p.as_posix()] = p
    return sorted(seen.values(), key=lambda x: x.as_posix())


# ---------- CLI ----------

def run(repo_root: Path, out_path: Path, dry_run: bool) -> int:
    start = time.time()
    passports = _find_passports(repo_root)

    results: List[dict] = []
    summary: Dict[str, int] = {
        "total": 0,
        "registered": 0,
        "drafted": 0,
        "skipped_v0_2_exists": 0,
        "skipped_already_v0_2": 0,
        "skipped_meta_schema": 0,
        "skipped_not_a_tool_passport": 0,
        "skipped_not_legacy": 0,
        "parse_error": 0,
    }

    for pp in passports:
        r = register_one(pp, repo_root, dry_run=dry_run)
        results.append(r)
        summary["total"] += 1
        st = r.get("status", "skipped_not_legacy")
        if st in summary:
            summary[st] += 1

    elapsed_ms = int((time.time() - start) * 1000)

    ledger = {
        "schema_id": LEDGER_SCHEMA_ID,
        "generated_at": _utc_now_iso(),
        "generator": "passport_v0_2_auto_registrar",
        "generator_version": REGISTRAR_VERSION,
        "mode": "dry_run" if dry_run else "apply",
        "repo_root": repo_root.as_posix(),
        "elapsed_ms": elapsed_ms,
        "summary": summary,
        "results": results,
    }

    _write_json(out_path, ledger)

    print("")
    print("=== passport_v0_2_auto_registrar :: %s ===" % ("dry_run" if dry_run else "apply"))
    for k in ("total", "registered", "drafted", "skipped_v0_2_exists", "skipped_already_v0_2",
              "skipped_meta_schema", "skipped_not_a_tool_passport", "skipped_not_legacy", "parse_error"):
        print("  %-32s = %d" % (k, summary[k]))
    print("  ledger                          -> %s" % out_path.as_posix())

    if summary["parse_error"] > 0:
        return 1
    return 0


def _self_test() -> int:
    """5 in-memory classification + registration cases. No filesystem writes."""
    import tempfile
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        pdir = repo / "ORGANS" / "MECHANICUS" / "TOOL_INTELLIGENCE" / "PASSPORTS"
        pdir.mkdir(parents=True)
        srcdir = repo / "ORGANS" / "MECHANICUS" / "TOOL_INTELLIGENCE" / "SAMPLE"
        srcdir.mkdir(parents=True)

        # case 1: legacy + paired python source with --self-test + --apply -> registered, owner_gated true, live
        (srcdir / "sample_tool.py").write_text(
            "import argparse\nap = argparse.ArgumentParser()\nap.add_argument('--self-test', action='store_true')\nap.add_argument('--apply', action='store_true')\nargs = ap.parse_args()\nimport os\n# os.remove pattern marker for destructive scan\n",
            encoding="utf-8",
        )
        p1 = pdir / "sample_tool_tool_passports_v0_1.json"
        _write_json(p1, {"schema_id": "imperium.tool_passport.v0_1", "name": "Sample Tool"})
        r1 = register_one(p1, repo, dry_run=True)
        ok1 = (r1["status"] == "registered" and r1["lang"] == "python" and r1["exec_mode"] == "live"
               and r1["owner_gated"] is True and r1["validators_count"] >= 2)
        print("case 1 legacy+paired src   : %s  (status=%s, lang=%s, exec=%s, gated=%s, v=%d)" % (
            "OK" if ok1 else "FAIL", r1["status"], r1["lang"], r1.get("exec_mode"), r1.get("owner_gated"), r1.get("validators_count", 0)))
        if not ok1: failures += 1

        # case 2: legacy WITHOUT source -> drafted, owner_gated true safe-default
        p2 = pdir / "ghost_tool_tool_passports_v0_1.json"
        _write_json(p2, {"schema_id": "imperium.tool_passport.v0_1"})
        r2 = register_one(p2, repo, dry_run=True)
        ok2 = (r2["status"] == "drafted" and r2["owner_gated"] is True and r2["sources_found"] == 0)
        print("case 2 legacy no source    : %s  (status=%s, sources=%d)" % (
            "OK" if ok2 else "FAIL", r2["status"], r2.get("sources_found", -1)))
        if not ok2: failures += 1

        # case 3: organ block passport -> skipped_not_a_tool_passport
        blockdir = repo / "ORGANS" / "DOCTRINARIUM" / "BLOCK" / "PASSPORT"
        blockdir.mkdir(parents=True)
        p3 = blockdir / "ORGAN_BLOCK_PASSPORT_V0_1.json"
        _write_json(p3, {"schema_id": "imperium.organ_block_passport.v0_1"})
        r3 = register_one(p3, repo, dry_run=True)
        ok3 = (r3["status"] == "skipped_not_a_tool_passport")
        print("case 3 organ block         : %s  (status=%s)" % ("OK" if ok3 else "FAIL", r3["status"]))
        if not ok3: failures += 1

        # case 4: meta schema -> skipped_meta_schema
        p4 = pdir / "tool_passport_schema_v0_1.json"
        _write_json(p4, {"schema_id": "imperium.tool_passport_schema.v0_1", "type": "object"})
        r4 = register_one(p4, repo, dry_run=True)
        ok4 = (r4["status"] == "skipped_meta_schema")
        print("case 4 meta schema         : %s  (status=%s)" % ("OK" if ok4 else "FAIL", r4["status"]))
        if not ok4: failures += 1

        # case 5: already v0_2 -> skipped_already_v0_2
        p5 = pdir / "already_v0_2_tool_passport_v0_2.json"
        _write_json(p5, {"schema_id": SCHEMA_ID_V0_2, "tool_id": "already_v0_2", "version": "v0_2"})
        r5 = register_one(p5, repo, dry_run=True)
        ok5 = (r5["status"] == "skipped_already_v0_2")
        print("case 5 already v0_2        : %s  (status=%s)" % ("OK" if ok5 else "FAIL", r5["status"]))
        if not ok5: failures += 1

        # case 6: apply mode writes file beside (cleanup automatic via tempdir)
        r6 = register_one(p1, repo, dry_run=False)
        if r6.get("status") == "skipped_v0_2_exists":
            # first call dry_run did not write; second call dry_run=False should write
            pass
        target_path = repo / "ORGANS" / "MECHANICUS" / "TOOL_INTELLIGENCE" / "PASSPORTS" / "sample_tool_tool_passport_v0_2.json"
        ok6 = target_path.exists()
        print("case 6 apply writes file   : %s  (exists=%s)" % ("OK" if ok6 else "FAIL", ok6))
        if not ok6: failures += 1

        # case 7: second apply -> skipped_v0_2_exists
        r7 = register_one(p1, repo, dry_run=False)
        ok7 = (r7["status"] == "skipped_v0_2_exists")
        print("case 7 second apply idemp. : %s  (status=%s)" % ("OK" if ok7 else "FAIL", r7["status"]))
        if not ok7: failures += 1

    if failures == 0:
        print("self-test ok (7 cases)")
        return 0
    print("self-test FAILED: %d failures" % failures)
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Mechanicus passport v0_2 auto-registrar")
    ap.add_argument("--repo", type=str, default=None, help="repo root (default: current dir)")
    ap.add_argument("--out", type=str, default=None, help="ledger output path (JSON)")
    ap.add_argument("--dry-run", action="store_true", help="do not write v0_2 passports; produce ledger only")
    ap.add_argument("--apply", action="store_true", help="write v0_2 passports beside originals (additive)")
    ap.add_argument("--self-test", action="store_true", help="run in-memory tests, exit 0 on success")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.dry_run and not args.apply:
        print("error: one of --dry-run / --apply / --self-test required", file=sys.stderr)
        return 2
    if args.dry_run and args.apply:
        print("error: --dry-run and --apply are mutually exclusive", file=sys.stderr)
        return 2

    repo = Path(args.repo) if args.repo else Path.cwd()
    if not repo.is_dir():
        print("error: repo root not found: %s" % repo, file=sys.stderr)
        return 2

    if not args.out:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.out = str(repo / "_LOCAL_HANDOFF" / "MIGRATION" / ("v0_2_registration_%s.json" % ts))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    return run(repo, out_path, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
