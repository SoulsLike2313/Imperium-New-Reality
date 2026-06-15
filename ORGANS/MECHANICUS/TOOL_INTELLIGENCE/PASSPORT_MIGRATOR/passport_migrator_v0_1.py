#!/usr/bin/env python3
"""
imperium.passport_migrator.v0_1 - passport_migrator v0_1

Scans for legacy or non-canonical tool passports under ORGANS/ and migrates
them to imperium.tool_passport.v0_2 schema. Conservative: refuses to guess
missing required fields; reports them as 'manual_migration_needed'.

Usage:
    python passport_migrator_v0_1.py --repo <REPO> --dry-run [--out PATH] [--quiet]
    python passport_migrator_v0_1.py --repo <REPO> --apply   [--out PATH] [--quiet]
    python passport_migrator_v0_1.py --self-test
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
SCHEMA_ID_LEDGER = "imperium.passport_migration_ledger.v0_1"

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

PASSPORT_NAME_RE = re.compile(
    r"^(?P<tool>[a-z][a-z0-9_]*)_tool_passport_v(?P<ver>[0-9_]+)\.json$"
)
TOOL_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
VERSION_RE = re.compile(r"^v[0-9]+(_[0-9]+)*$")


def find_passport_candidates(repo: Path):
    organs = repo / "ORGANS"
    if not organs.exists():
        return []
    cand = set()
    # canonical name
    for p in organs.rglob("*_tool_passport_v*.json"):
        cand.add(p.resolve())
    # PASSPORTS dirs
    for d in organs.rglob("PASSPORTS"):
        if d.is_dir():
            for p in d.glob("*.json"):
                cand.add(p.resolve())
    # any *passport*.json under ORGANS
    for p in organs.rglob("*passport*.json"):
        if p.is_file():
            cand.add(p.resolve())
    return sorted(cand)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)


def classify(passport):
    if not isinstance(passport, dict):
        return "non_compliant"
    sid = passport.get("schema_id")
    if sid == SCHEMA_ID_V0_2:
        return "v0_2"
    if isinstance(sid, str) and "tool_passport" in sid:
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
        return m.group("tool")
    stem = path.stem.lower()
    stem = re.sub(r"_?passport.*$", "", stem)
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
    klass = classify(passport)
    if klass == "v0_2":
        return {"path": rel, "status": "skipped_already_v0_2"}
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
        sample = repo / "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/SAMPLE"
        (sample / "PASSPORTS").mkdir(parents=True)
        (sample / "sample_v0_1.py").write_text("# stub\n")
        legacy = {
            "schema_id": "imperium.tool_passport.v0_1",
            "tool_id": "sample",
            "name": "Sample",
            "version": "v0_1",
            "owner_organ": "MECHANICUS",
            "validators": [
                {"name": "syntax", "exec": "python -m py_compile {tool_path}"}
            ],
        }
        lp = sample / "PASSPORTS" / "sample_passport.json"
        lp.write_text(json.dumps(legacy, indent=2), encoding="utf-8")
        backup_dir = repo / "tmp_backup"
        r = migrate_one(lp, repo, apply=False, backup_dir=backup_dir)
        print(f"self-test dry-run : status={r['status']} missing={r.get('missing', [])} target={r.get('target_path')}")
        assert r["status"] == "planned", r
        r = migrate_one(lp, repo, apply=True, backup_dir=backup_dir)
        print(f"self-test apply   : status={r['status']} target={r.get('target_path')}")
        assert r["status"] == "applied", r
        new_path = repo / r["target_path"]
        assert new_path.exists()
        loaded = json.loads(new_path.read_text(encoding="utf-8"))
        assert loaded["schema_id"] == SCHEMA_ID_V0_2
        assert loaded["lang"] == "python"
        assert loaded["exec_mode"] == "static"
        # bad case: refuses without validators
        sample2 = repo / "ORGANS/MECHANICUS/TOOL_INTELLIGENCE/BAD"
        (sample2 / "PASSPORTS").mkdir(parents=True)
        (sample2 / "bad.py").write_text("# stub\n")
        bad = {"schema_id": "imperium.tool_passport.v0_1", "tool_id": "bad"}
        bp = sample2 / "PASSPORTS" / "bad_passport.json"
        bp.write_text(json.dumps(bad), encoding="utf-8")
        rb = migrate_one(bp, repo, apply=False, backup_dir=backup_dir)
        print(f"self-test bad     : status={rb['status']} missing={rb.get('missing', [])}")
        assert rb["status"] == "manual_migration_needed", rb
        assert "validators" in rb["missing"], rb
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
            print(f"[{r['status']:24}] {r['path']}")
            if r.get("missing"):
                print(f"  missing: {r['missing']}")
            for n in r.get("notes", []):
                print(f"  note   : {n}")
            if r.get("target_path"):
                print(f"  target : {r['target_path']}")

    summary = {
        "total": len(results),
        "skipped_already_v0_2":   sum(1 for r in results if r["status"] == "skipped_already_v0_2"),
        "planned":                sum(1 for r in results if r["status"] == "planned"),
        "applied":                sum(1 for r in results if r["status"] == "applied"),
        "manual_migration_needed":sum(1 for r in results if r["status"] == "manual_migration_needed"),
        "parse_error":            sum(1 for r in results if r["status"] == "parse_error"),
    }

    ledger = {
        "schema_id":   SCHEMA_ID_LEDGER,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator":   "imperium.passport_migrator.v0_1",
        "mode":        "apply" if args.apply else "dry_run",
        "repo_root":   str(repo),
        "backup_dir":  str(backup_dir) if args.apply else None,
        "elapsed_ms":  int((time.time() - t0) * 1000),
        "summary":     summary,
        "results":     results,
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
