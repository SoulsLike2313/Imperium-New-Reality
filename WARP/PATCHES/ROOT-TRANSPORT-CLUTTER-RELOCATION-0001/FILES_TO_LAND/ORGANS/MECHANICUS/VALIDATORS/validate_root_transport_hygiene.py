#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, datetime as dt, fnmatch, json, os, shutil, hashlib, subprocess, csv
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "ROOT-TRANSPORT-CLUTTER-RELOCATION-0001"
VALIDATOR_ID = "root_transport_hygiene_validator.v0_1"

APPLY_DIR = Path("SUPPORT/TRANSPORT/APPLY_SCRIPTS")
MANIFEST_DIR = Path("SUPPORT/TRANSPORT/FILE_MANIFESTS")
INDEX_JSON = Path("SUPPORT/TRANSPORT/ROOT_TRANSPORT_INDEX_V0_1.json")
INDEX_MD = Path("SUPPORT/TRANSPORT/ROOT_TRANSPORT_INDEX_V0_1.md")
REGISTRY_JSON = Path("ORGANS/ADMINISTRATUM/REGISTRY/ROOT_TRANSPORT_RELOCATION_REGISTRY_V0_1.json")
RECEIPT_JSON = Path("ORGANS/MECHANICUS/RECEIPTS/root_transport_hygiene_receipt.json")
REPORT_MD = Path("ORGANS/MECHANICUS/REPORTS/ROOT_TRANSPORT_HYGIENE_REPORT_V0_1.md")
MATRIX_JSON = Path("ORGANS/MECHANICUS/MATRICES/ROOT_TRANSPORT_HYGIENE_MATRIX_V0_1.json")

ROOT_PATTERNS = [
    ("APPLY_*.ps1", APPLY_DIR, "apply_script"),
    ("*_FILE_MANIFEST_SHA256.json", MANIFEST_DIR, "file_manifest"),
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def repo_status(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "status", "--porcelain"], cwd=str(repo), text=True, capture_output=True, timeout=30)
        return p.stdout
    except Exception as e:
        return f"git status unavailable: {e}"

def infer_patch_id(filename: str) -> str:
    name = filename
    for suffix in ["_FILE_MANIFEST_SHA256.json", ".ps1"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    if name.startswith("APPLY_"):
        name = name[len("APPLY_"):]
    return name.replace("_", "-").upper()

def collect_root_transport(repo: Path) -> List[Dict[str, Any]]:
    entries = []
    for pattern, dest_dir, kind in ROOT_PATTERNS:
        for p in sorted(repo.glob(pattern)):
            if not p.is_file():
                continue
            # Only root files: repo.glob(pattern) already root-only.
            entries.append({
                "kind": kind,
                "pattern": pattern,
                "source_rel": p.relative_to(repo).as_posix(),
                "destination_rel": (dest_dir / p.name).as_posix(),
                "filename": p.name,
                "patch_id_guess": infer_patch_id(p.name),
                "bytes": p.stat().st_size,
                "sha256_before": sha256(p)
            })
    return entries

def ensure_dirs(repo: Path):
    for d in [APPLY_DIR, MANIFEST_DIR, INDEX_JSON.parent, REGISTRY_JSON.parent, RECEIPT_JSON.parent, REPORT_MD.parent]:
        (repo / d).mkdir(parents=True, exist_ok=True)

def relocate(repo: Path, entries: List[Dict[str, Any]], dry_run: bool = False) -> List[Dict[str, Any]]:
    ensure_dirs(repo)
    result = []
    for e in entries:
        src = repo / e["source_rel"]
        dst = repo / e["destination_rel"]
        item = dict(e)
        item["action"] = "MOVE"
        item["dry_run"] = dry_run
        if src.resolve() == dst.resolve():
            item["action"] = "ALREADY_CANONICAL"
        elif dry_run:
            item["destination_exists_after"] = dst.exists()
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                # If same content, remove source; otherwise preserve collision.
                if sha256(dst) == e["sha256_before"]:
                    src.unlink()
                    item["action"] = "DEDUP_SOURCE_REMOVED"
                else:
                    collision = dst.with_name(dst.stem + "__COLLISION__" + e["sha256_before"][:12] + dst.suffix)
                    shutil.move(str(src), str(collision))
                    item["destination_rel"] = collision.relative_to(repo).as_posix()
                    item["action"] = "MOVE_WITH_COLLISION_RENAME"
            else:
                shutil.move(str(src), str(dst))
        actual = repo / item["destination_rel"]
        item["destination_exists_after"] = actual.is_file()
        item["sha256_after"] = sha256(actual) if actual.is_file() else None
        item["sha256_match"] = item["sha256_after"] == e["sha256_before"] if item["sha256_after"] else False
        result.append(item)
    return result

def write_outputs(repo: Path, entries: List[Dict[str, Any]], checks: List[Dict[str, Any]], warnings: List[str], errors: List[str], apply_mode: bool):
    ensure_dirs(repo)
    generated = utc()
    summary = {
        "total_relocated_entries": len(entries),
        "apply_scripts": sum(1 for e in entries if e["kind"] == "apply_script"),
        "file_manifests": sum(1 for e in entries if e["kind"] == "file_manifest"),
        "sha256_all_match": all(e.get("sha256_match") for e in entries) if entries else True,
        "apply_mode": apply_mode
    }
    index = {
        "index_id": "root_transport_index.v0_1",
        "patch_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "summary": summary,
        "entries": entries
    }
    registry = {
        "registry_id": "administratum.root_transport_relocation_registry.v0_1",
        "patch_id": TASK_ID,
        "generated_at_utc": generated,
        "meaning": "Registry of root transport files relocated from repo root into SUPPORT/TRANSPORT.",
        "entries": entries
    }
    receipt = {
        "receipt_id": "receipt.mechanicus.root_transport_hygiene.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": "PASS_ROOT_TRANSPORT_HYGIENE" if not errors else "FAIL_ROOT_TRANSPORT_HYGIENE",
        "generated_at_utc": generated,
        "summary": summary,
        "index": INDEX_JSON.as_posix(),
        "registry": REGISTRY_JSON.as_posix(),
        "report": REPORT_MD.as_posix(),
        "checks": checks,
        "warnings": warnings,
        "errors": errors
    }
    (repo / INDEX_JSON).write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / REGISTRY_JSON).write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT_JSON).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = []
    for e in entries:
        rows.append(
            f"| `{e['kind']}` | `{e['source_rel']}` | `{e['destination_rel']}` | `{e.get('sha256_match')}` | `{e.get('patch_id_guess')}` |"
        )
    table = "\n".join(rows) if rows else "| none | none | none | true | none |"
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    (repo / INDEX_MD).write_text(f"""# ROOT TRANSPORT INDEX V0.1

patch_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
generated_at_utc: `{generated}`

## Meaning

Root-level transport files were relocated into canonical support zones.

This preserves provenance while making repo root easier for humans and external agents to read.

## Summary

- total_relocated_entries: `{summary['total_relocated_entries']}`
- apply_scripts: `{summary['apply_scripts']}`
- file_manifests: `{summary['file_manifests']}`
- sha256_all_match: `{summary['sha256_all_match']}`

## Entries

| kind | source | destination | sha256_match | patch_id_guess |
|---|---|---|---|---|
{table}
""", encoding="utf-8")

    (repo / REPORT_MD).write_text(f"""# ROOT TRANSPORT HYGIENE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
generated_at_utc: `{generated}`

## Meaning

This report proves root-level transport clutter has been relocated without losing SHA256 provenance.

## Summary

- total_relocated_entries: `{summary['total_relocated_entries']}`
- apply_scripts: `{summary['apply_scripts']}`
- file_manifests: `{summary['file_manifests']}`
- sha256_all_match: `{summary['sha256_all_match']}`

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{INDEX_JSON.as_posix()}`
- `{INDEX_MD.as_posix()}`
- `{REGISTRY_JSON.as_posix()}`
- `{RECEIPT_JSON.as_posix()}`
""", encoding="utf-8")
    return receipt

def validate(repo: Path, relocated_entries: List[Dict[str, Any]], checks: List[Dict[str, Any]], errors: List[str]):
    root_apply = [p.name for p in repo.glob("APPLY_*.ps1") if p.is_file()]
    root_manifest = [p.name for p in repo.glob("*_FILE_MANIFEST_SHA256.json") if p.is_file()]
    add(checks, "root_has_no_apply_scripts", len(root_apply) == 0, {"remaining": root_apply})
    add(checks, "root_has_no_file_manifests", len(root_manifest) == 0, {"remaining": root_manifest})
    if root_apply:
        errors.append("Root still has APPLY_*.ps1: " + ", ".join(root_apply))
    if root_manifest:
        errors.append("Root still has *_FILE_MANIFEST_SHA256.json: " + ", ".join(root_manifest))

    dest_missing = [e for e in relocated_entries if not (repo / e["destination_rel"]).is_file()]
    hash_bad = [e for e in relocated_entries if not e.get("sha256_match")]
    add(checks, "all_relocated_destinations_exist", len(dest_missing) == 0, {"missing": [e["destination_rel"] for e in dest_missing]})
    add(checks, "all_relocated_sha256_match", len(hash_bad) == 0, {"bad": [e["destination_rel"] for e in hash_bad]})
    if dest_missing:
        errors.append("Some relocated destinations are missing")
    if hash_bad:
        errors.append("Some relocated hashes do not match")

    add(checks, "support_transport_dirs_exist", (repo / APPLY_DIR).is_dir() and (repo / MANIFEST_DIR).is_dir(), {})
    add(checks, "warp_patches_still_exists", (repo / "WARP/PATCHES").is_dir(), {})
    if not (repo / "WARP/PATCHES").is_dir():
        errors.append("WARP/PATCHES missing after relocation")

    add(checks, "matrix_exists", (repo / MATRIX_JSON).is_file(), {"path": MATRIX_JSON.as_posix()})
    if not (repo / MATRIX_JSON).is_file():
        errors.append("Root transport hygiene matrix missing")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true", help="Move root transport files into SUPPORT/TRANSPORT.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    checks: List[Dict[str, Any]] = []
    warnings: List[str] = []
    errors: List[str] = []

    before_status = repo_status(repo)
    candidates = collect_root_transport(repo)
    add(checks, "root_transport_candidates_collected", True, {"count": len(candidates), "files": [c["source_rel"] for c in candidates]})

    if args.dry_run:
        relocated = relocate(repo, candidates, dry_run=True)
        warnings.append("Dry run only; no files moved.")
    elif args.apply:
        relocated = relocate(repo, candidates, dry_run=False)
    else:
        relocated = []
        warnings.append("No --apply passed; validation-only mode.")

    validate(repo, relocated if args.apply or args.dry_run else [], checks, errors)

    if args.apply or args.dry_run:
        receipt = write_outputs(repo, relocated, checks, warnings, errors, apply_mode=args.apply)
    else:
        receipt = {
            "task_id": TASK_ID,
            "validator_id": VALIDATOR_ID,
            "verdict": "PASS_VALIDATE_ONLY" if not errors else "FAIL_VALIDATE_ONLY",
            "checks": checks,
            "warnings": warnings,
            "errors": errors
        }

    after_status = repo_status(repo)
    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": receipt.get("verdict"),
        "candidate_count": len(candidates),
        "relocated_count": len(relocated),
        "apply_scripts": sum(1 for e in relocated if e.get("kind") == "apply_script"),
        "file_manifests": sum(1 for e in relocated if e.get("kind") == "file_manifest"),
        "index": INDEX_JSON.as_posix(),
        "receipt": RECEIPT_JSON.as_posix(),
        "report": REPORT_MD.as_posix(),
        "errors": errors,
        "git_status_before_lines": len([x for x in before_status.splitlines() if x.strip()]),
        "git_status_after_lines": len([x for x in after_status.splitlines() if x.strip()])
    }, ensure_ascii=False, indent=2))

    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
