#!/usr/bin/env python3
"""
imperium.passport_migrator.v0_2 - passport_migrator v0_2

Upgrade over v0_1:
  - explicit classifier that separates tool-passports from organ/data/agent passports,
    JSON Schemas, and other artefacts caught by the broad name match.
  - new statuses: 'skipped_not_a_tool_passport' and 'skipped_meta_schema' which
    do NOT trigger a non-zero exit and do NOT count against manual_migration_needed.
  - tolerant filename parser (handles typo 'tool_passports' with trailing s).

Usage identical to v0_1:
    python passport_migrator_v0_2.py --repo <REPO> --dry-run [--out PATH] [--quiet]
    python passport_migrator_v0_2.py --repo <REPO> --apply   [--out PATH] [--quiet]
    python passport_migrator_v0_2.py --self-test
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_ID_V0_2   = "imperium.tool_passport.v0_2"
SCHEMA_ID_LEDGER = "imperium.passport_migration_ledger.v0_2"

OWNER_ORGAN_ENUM = {
    "MECHANICUS", "IMPERIAL_IDE", "DOCTRINARIUM", "OFFICIO_AGENTIS",
    "SPECULUM", "INQUISITOR", "OBSERVATORIUM", "_CORE_GOVERNANCE",
}
LANG_ENUM = {
    "python", "rust", "typescript", "javascript",
    "powershell", "css", "html", "markdown", "mixed",
}
EXEC_MODE_ENUM = {"static", "sim", "paper", "shadow", "live"}

EXT_TO_LANG = {
    ".py":  "python",
    ".rs":  "rust",
    ".ts":  "typescript",
    ".tsx": "typescript",
    ".js":  "javascript",
    ".jsx": "javascript",
    ".ps1": "powershell",
    ".css": "css",
    ".html":"html",
    ".md":  "markdown",
}

# Tolerant: matches both `_tool_passport_v0_1.json` and `_tool_passports_v0_1.json` (typo).
PASSPORT_NAME_RE = re.compile(
    r"^(?P<tool>[a-z][a-z0-9_]*?)_tool_passports?_v(?P<ver>[0-9_]+)\.json$",
    re.IGNORECASE,
)
TOOL_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
VERSION_RE = re.compile(r"^v[0-9]+(_[0-9]+)*$")

# Path / name fragments that mean the file is NOT a tool passport.
NOT_TOOL_PATH_FRAGMENTS = (
    "/BLOCK/PASSPORT/",           # ORGANS/<ORGAN>/BLOCK/PASSPORT/ORGAN_BLOCK_PASSPORT_*
    "/DATA_ATLAS/",               # ORGANS/ADMINISTRATUM/DATA_ATLAS/DATA_ATLAS_PASSPORT_*
    "/EMPEROR/PASSPORT_OF_THE_EMPEROR",
    "/ROLE_PACKS/",               # role pack passports
    "/AGENT_PASSPORTS/",
    "/LEGACY_IMPORTED_ROOT_MIRROR/",
)
NOT_TOOL_FILENAME_RE = re.compile(
    r"^("
    r"ORGAN_BLOCK_PASSPORT|DATA_ATLAS_PASSPORT|FILE_PASSPORT|"
    r"file_passport_schema|emperor_passport|agent_passport|role_pack"
    r")",
    re.IGNORECASE,
)
NOT_TOOL_SCHEMA_IDS = {
    "imperium.organ_block_passport.v0_1",
    "imperium.data_atlas_passport.v0_1",
    "imperium.file_passport.v0_1",
    "imperium.emperor_passport.v0_1",
    "imperium.agent_passport.v0_1",
    "imperium.role_pack_passport.v0_1",
}


def find_passport_candidates(repo: Path):
    organs = repo / "ORGANS"
    if not organs.exists():
        return []
    cand = set()
    for p in organs.rglob("*_tool_passport*.json"):
        if p.is_file():
            cand.add(p.resolve())
    for d in organs.rglob("PASSPORTS"):
        if d.is_dir():
            for p in d.glob("*.json"):
                cand.add(p.resolve())
    for p in organs.rglob("*passport*.json"):
        if p.is_file():
            cand.add(p.resolve())
    return sorted(cand)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)


def preclassify_by_path(path: Path) -> str | None:
    """Returns a 'skip' classification when the file is clearly not a tool passport,
    based purely on path/name (cheap, no JSON load)."""
    name = path.name
    posix = str(path).replace("\\", "/")
    if name.endswith(".schema.json"):
        return "skipped_meta_schema"
    if NOT_TOOL_FILENAME_RE.match(name):
        return "skipped_not_a_tool_passport"
    for frag in NOT_TOOL_PATH_FRAGMENTS:
        if frag in posix:
            return "skipped_not_a_tool_passport"
    return None


def classify(passport, path: Path) -> str:
    pre = preclassify_by_path(path)
    if pre:
        return pre
    if not isinstance(passport, dict):
        return "non_compliant"
    sid = passport.get("schema_id")
    if sid == SCHEMA_ID_V0_2:
        return "skipped_already_v0_2"
    if isinstance(sid, str) and sid in NOT_TOOL_SCHEMA_IDS:
        return "skipped_not_a_tool_passport"
    if isinstance(sid, str) and "tool_passport" in sid:
        return "legacy"
    # heuristic: looks like a tool passport if it has tool_id + validators or version
    if isinstance(passport.get("tool_id"), str) and (
        "validators" in passport or "version" in passport
    ):
        return "legacy"
    return "non_compliant"


def derive_tool_id(passport, path: Path):
    if isinstance(passport, dict):
        for k in ("tool_id", "id"):
            v = passport.get(k)
            if isinstance(v, str) and TOOL_ID_RE.match(v):
                return v
    m = PASSPORT_NAME_RE.match(path.name)
    if m:
        return m.group("tool").lower()
    stem = path.stem.lower()
    stem = re.sub(r"_?passports?.*$", "", stem)
    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    if TOOL_ID_RE.match(stem):
        return stem
    return None


def derive_owner_organ(path: Path):
    parts = set(path.parts)
    for organ in OWNER_ORGAN_ENUM:
        if organ in parts:
            return organ
    return None


def derive_tool_path(passport, path: Path, repo: Path):
    if isinstance(passport, dict):
        tp = passport.get("tool_path")
        if isinstance(tp, str) and tp:
            return tp
    parent_dir = path.parent
    if parent_dir.name == "PASSPORTS":
        parent_dir = parent_dir.parent
    for ext in (".py", ".rs", ".ts", ".tsx", ".js", ".ps1"):
        for f in parent_dir.glob(f"*{ext}"):
            try:
                rel = f.resolve().relative_to(repo.resolve())
                return str(rel).replace("\\", "/")
            except ValueError:
                continue
    return None


def derive_lang(passport, path: Path, repo: Path):
    if isinstance(passport, dict):
        l = passport.get("lang")
        if l in LANG_ENUM:
            return l
    tp = derive_tool_path(passport, path, repo)
    if tp:
        ext = Path(tp).suffix.lower()
        if ext in EXT_TO_LANG:
            return EXT_TO_LANG[ext]
    return None


def build_v0_2(passport, path: Path, repo: Path):
    p = passport if isinstance(passport, dict) else {}
    missing = []
    notes = []
    new = {"schema_id": SCHEMA_ID_V0_2}

    tool_id = derive_tool_id(p, path)
    if not tool_id:
        missing.append("tool_id")
    else:
        new["tool_id"] = tool_id
        if p.get("tool_id") != tool_id:
            notes.append(f"tool_id derived: {tool_id}")

    name = p.get("name") if isinstance(p.get("name"), str) else None
    if not name and tool_id:
        name = tool_id.replace("_", " ").title()
        notes.append(f"name derived from tool_id: {name}")
    if not name:
        missing.append("name")
    else:
        new["name"] = name

    version = p.get("version") if isinstance(p.get("version"), str) else None
    if not version or not VERSION_RE.match(version):
        m = PASSPORT_NAME_RE.match(path.name)
        if m:
            version = "v" + m.group("ver")
            notes.append(f"version derived from filename: {version}")
        else:
            version = "v0_1"
            notes.append("version defaulted to v0_1")
    new["version"] = version

    organ = p.get("owner_organ")
    if organ not in OWNER_ORGAN_ENUM:
        organ = derive_owner_organ(path)
        if organ:
            notes.append(f"owner_organ derived from path: {organ}")
    if organ not in OWNER_ORGAN_ENUM:
        missing.append("owner_organ")
    else:
        new["owner_organ"] = organ

    lang = derive_lang(p, path, repo)
    if lang not in LANG_ENUM:
        missing.append("lang")
    else:
        new["lang"] = lang

    validators = p.get("validators")
    cleaned = []
    if isinstance(validators, list):
        for v in validators:
            if (
                isinstance(v, dict)
                and isinstance(v.get("name"), str)
                and isinstance(v.get("exec"), str)
            ):
                ent = {"name": v["name"], "exec": v["exec"]}
                tos = v.get("timeout_seconds")
                if isinstance(tos, (int, float)) and 1 <= tos <= 300:
                    ent["timeout_seconds"] = tos
                cleaned.append(ent)
    if cleaned:
        new["validators"] = cleaned
    else:
        missing.append("validators")

    exec_mode = p.get("exec_mode")
    if exec_mode not in EXEC_MODE_ENUM:
        exec_mode = "static"
        notes.append("exec_mode defaulted to static")
    new["exec_mode"] = exec_mode

    owner_gated = p.get("owner_gated")
    if not isinstance(owner_gated, bool):
        owner_gated = False
        notes.append("owner_gated defaulted to false")
    new["owner_gated"] = owner_gated

    for opt in (
        "build_system", "io_contract", "observability",
        "capability_tags", "depends_on", "doctrine_ref",
        "tool_path", "created_at",
    ):
        if opt in p and p[opt] is not None:
            new[opt] = p[opt]

    if "tool_path" not in new:
        tp = derive_tool_path(p, path, repo)
        if tp:
            new["tool_path"] = tp
            notes.append(f"tool_path derived: {tp}")

    new["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return new, missing, notes


def canonical_name(tool_id: str, version: str) -> str:
    return f"{tool_id}_tool_passport_{version}.json"


def migrate_one(path: Path, repo: Path, apply: bool, backup_dir: Path):
    rel = str(path.relative_to(repo)).replace("\\", "/")
    passport, err = load_json(path)
    if err:
        return {"path": rel, "status": "parse_error", "error": err}
    klass = classify(passport, path)
    if klass in ("skipped_already_v0_2", "skipped_meta_schema", "skipped_not_a_tool_passport"):
        return {"path": rel, "status": klass, "schema_classification_before": klass}
    if klass == "non_compliant":
        return {
            "path": rel,
            "status": "manual_migration_needed",
            "missing": ["schema_id-not-recognized"],
            "notes": ["file matches passport-like name but schema_id/structure unrecognized"],
            "schema_classification_before": klass,
        }
    new, missing, notes = build_v0_2(passport, path, repo)
    target_dir = path.parent
    if target_dir.name != "PASSPORTS":
        target_dir = target_dir / "PASSPORTS"
        notes.append("relocated into PASSPORTS/ subdirectory")
    target_name = canonical_name(new["tool_id"], new["version"]) if "tool_id" in new and "version" in new else None
    target_path = (target_dir / target_name) if target_name else None
    target_rel = (
        str(target_path.relative_to(repo)).replace("\\", "/") if target_path else None
    )
    result = {
        "path": rel,
        "status": "manual_migration_needed" if missing else ("applied" if apply else "planned"),
        "missing": missing,
        "notes": notes,
        "target_path": target_rel,
        "schema_classification_before": klass,
    }
    if missing or not target_path:
        return result
    if apply:
        bk = backup_dir / rel
        bk.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, bk)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            json.dumps(new, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if target_path.resolve() != path.resolve():
            path.unlink()
            result["removed_old"] = rel
    return result


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        # case 1: legacy good
        good = repo / "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/SAMPLE"
        (good / "PASSPORTS").mkdir(parents=True)
        (good / "sample_v0_1.py").write_text("# stub\n")
        legacy = {
            "schema_id": "imperium.tool_passport.v0_1",
            "tool_id": "sample",
            "name": "Sample",
            "version": "v0_1",
            "owner_organ": "MECHANICUS",
            "validators": [{"name": "syntax", "exec": "python -m py_compile {tool_path}"}],
        }
        lp = good / "PASSPORTS" / "sample_passport.json"
        lp.write_text(json.dumps(legacy), encoding="utf-8")
        # case 2: organ block passport (must be filtered)
        ob = repo / "ORGANS/INQUISITION/BLOCK/PASSPORT"
        ob.mkdir(parents=True)
        ob_path = ob / "ORGAN_BLOCK_PASSPORT_V0_1.json"
        ob_path.write_text(json.dumps({
            "schema_id": "imperium.organ_block_passport.v0_1",
            "organ": "INQUISITION",
        }), encoding="utf-8")
        # case 3: json schema (must be filtered by extension)
        sch = repo / "ORGANS/MECHANICUS/SCHEMAS"
        sch.mkdir(parents=True)
        sch_path = sch / "imperium_tool_passport_v0_2.schema.json"
        sch_path.write_text(json.dumps({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "tool passport v0_2",
        }), encoding="utf-8")
        # case 4: typo filename (passports with trailing s)
        ev = repo / "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/PASSPORTS"
        ev.mkdir(parents=True)
        ev_path = ev / "evidence_sealer_tool_passports_v0_1.json"
        ev_path.write_text(json.dumps({
            "schema_id": "imperium.tool_passport.v0_1",
            "tool_id": "evidence_sealer",
        }), encoding="utf-8")
        # case 5: bad legacy (no validators)
        bad = repo / "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/BAD"
        (bad / "PASSPORTS").mkdir(parents=True)
        bp = bad / "PASSPORTS" / "bad_passport.json"
        bp.write_text(json.dumps({
            "schema_id": "imperium.tool_passport.v0_1",
            "tool_id": "bad",
        }), encoding="utf-8")
        (bad / "bad.py").write_text("# stub\n")
        backup_dir = repo / "_BK"
        r1 = migrate_one(lp,      repo, apply=False, backup_dir=backup_dir)
        r2 = migrate_one(ob_path, repo, apply=False, backup_dir=backup_dir)
        r3 = migrate_one(sch_path,repo, apply=False, backup_dir=backup_dir)
        r4 = migrate_one(ev_path, repo, apply=False, backup_dir=backup_dir)
        r5 = migrate_one(bp,      repo, apply=False, backup_dir=backup_dir)
        print(f"case 1 legacy good        : {r1['status']}")
        print(f"case 2 organ block        : {r2['status']}")
        print(f"case 3 json schema        : {r3['status']}")
        print(f"case 4 typo evidence      : {r4['status']} missing={r4.get('missing', [])}")
        print(f"case 5 bad legacy         : {r5['status']} missing={r5.get('missing', [])}")
        assert r1["status"] == "planned", r1
        assert r2["status"] == "skipped_not_a_tool_passport", r2
        assert r3["status"] == "skipped_meta_schema", r3
        # case 4: missing validators (evidence has tool_id+schema_id but no validators)
        assert r4["status"] == "manual_migration_needed", r4
        assert "validators" in r4["missing"], r4
        # apply case 1
        ra = migrate_one(lp, repo, apply=True, backup_dir=backup_dir)
        assert ra["status"] == "applied", ra
        new_path = repo / ra["target_path"]
        loaded = json.loads(new_path.read_text(encoding="utf-8"))
        assert loaded["schema_id"] == SCHEMA_ID_V0_2
        assert loaded["lang"] == "python"
    print("self-test ok")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=str)
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    if not args.repo:
        print("ERROR: --repo required (or --self-test)", file=sys.stderr)
        return 2
    if args.apply and args.dry_run:
        print("ERROR: --apply and --dry-run are mutually exclusive", file=sys.stderr)
        return 2
    if not args.apply and not args.dry_run:
        args.dry_run = True

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"ERROR: repo not found: {repo}", file=sys.stderr)
        return 2

    t0 = time.time()
    candidates = find_passport_candidates(repo)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = repo / "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/PASSPORT_MIGRATOR/BACKUPS" / ts

    results = []
    for c in candidates:
        r = migrate_one(c, repo, apply=args.apply, backup_dir=backup_dir)
        results.append(r)
        if not args.quiet:
            print(f"[{r['status']:30}] {r['path']}")
            if r.get("missing"):
                print(f"  missing: {r['missing']}")
            for n in r.get("notes", []):
                print(f"  note   : {n}")
            if r.get("target_path"):
                print(f"  target : {r['target_path']}")

    summary = {
        "total":                       len(results),
        "skipped_already_v0_2":        sum(1 for r in results if r["status"] == "skipped_already_v0_2"),
        "skipped_meta_schema":         sum(1 for r in results if r["status"] == "skipped_meta_schema"),
        "skipped_not_a_tool_passport": sum(1 for r in results if r["status"] == "skipped_not_a_tool_passport"),
        "planned":                     sum(1 for r in results if r["status"] == "planned"),
        "applied":                     sum(1 for r in results if r["status"] == "applied"),
        "manual_migration_needed":     sum(1 for r in results if r["status"] == "manual_migration_needed"),
        "parse_error":                 sum(1 for r in results if r["status"] == "parse_error"),
    }

    ledger = {
        "schema_id":    SCHEMA_ID_LEDGER,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator":    "imperium.passport_migrator.v0_2",
        "mode":         "apply" if args.apply else "dry_run",
        "repo_root":    str(repo),
        "backup_dir":   str(backup_dir) if args.apply else None,
        "elapsed_ms":   int((time.time() - t0) * 1000),
        "summary":      summary,
        "results":      results,
    }

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(
            json.dumps(ledger, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if not args.quiet:
            print(f"\nledger written -> {args.out}")

    if not args.quiet:
        print(f"\nsummary: {summary}")

    if summary["parse_error"] or summary["manual_migration_needed"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
