#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, datetime as dt, fnmatch, json, os, shutil, hashlib, subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "GOVERNANCE-ROOT-AND-GREAT-NINE-RECONCILIATION-0001"
VALIDATOR_ID = "reality_root_governance_validator.v0_1"

ROOT_CANON_MATRIX = Path("ORGANS/THRONE/MATRICES/REALITY_ROOT_CANON_MATRIX_V0_1.json")
PILLAR_MATRIX = Path("ORGANS/THRONE/MATRICES/IMPERIUM_PILLAR_BOUNDARY_MATRIX_V0_1.json")
GREAT_NINE_MATRIX = Path("ORGANS/THRONE/MATRICES/GREAT_NINE_CANON_AND_ALIAS_MATRIX_V0_1.json")
POLICY_MD = Path("ORGANS/THRONE/SELF_KNOWLEDGE/REALITY_BOUNDARY_AND_STORAGE_POLICY_V0_1.md")
RECEIPT_SCHEMA = Path("ORGANS/THRONE/SCHEMAS/reality_root_governance_receipt.schema.json")

ROOT_ZONE_REGISTRY = Path("ORGANS/ADMINISTRATUM/REGISTRY/ROOT_ZONE_GOVERNANCE_REGISTRY_V0_1.json")
ROOT_DRIFT_REGISTRY = Path("ORGANS/ADMINISTRATUM/REGISTRY/ROOT_DRIFT_RELOCATION_REGISTRY_V0_1.json")
RECEIPT_JSON = Path("ORGANS/MECHANICUS/RECEIPTS/reality_root_governance_receipt.json")
REPORT_MD = Path("ORGANS/MECHANICUS/REPORTS/REALITY_ROOT_GOVERNANCE_REPORT_V0_1.md")

ALLOWED_ROOT_DIRS = {"ORGANS", "SUPPORT"}
ALLOWED_ROOT_FILES = {"AGENTS.md", "README.md", ".gitignore", ".gitattributes", ".editorconfig"}
TRANSITIONAL_DEBT_DIRS = {"WARP", "_HARNESS"}

GREAT_NINE = [
    "ASTRONOMICON", "ADMINISTRATUM", "DOCTRINARIUM", "MECHANICUS", "INQUISITION",
    "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "OFFICIO_AGENTIS"
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def run_git(repo: Path, args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(["git"] + args, cwd=str(repo), text=True, capture_output=True, timeout=60)
    return p.returncode, p.stdout, p.stderr

def git_head(repo: Path) -> str:
    code, out, err = run_git(repo, ["rev-parse", "HEAD"])
    return out.strip() if code == 0 else "UNKNOWN"

def list_root_entries(repo: Path) -> Dict[str, List[str]]:
    dirs, files = [], []
    for p in sorted(repo.iterdir(), key=lambda x: x.name.lower()):
        if p.name == ".git":
            continue
        if p.is_dir():
            dirs.append(p.name)
        elif p.is_file():
            files.append(p.name)
    return {"dirs": dirs, "files": files}

def gather_files(root: Path) -> List[Path]:
    if not root.exists():
        return []
    if root.is_file():
        return [root]
    out = []
    for p in root.rglob("*"):
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts and not p.name.endswith(".pyc"):
            out.append(p)
    return sorted(out)

def remove_empty_dirs(path: Path, stop: Path):
    try:
        while path != stop and path.exists():
            path.rmdir()
            path = path.parent
    except OSError:
        return

def map_destination(repo: Path, src: Path) -> Path | None:
    rel = src.relative_to(repo).as_posix()
    parts = rel.split("/")
    if parts[0] == "DOCTRINARIUM":
        return repo / "ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/DOCTRINARIUM" / Path(*parts[1:])
    if parts[0] == "REPORTS":
        return repo / "SUPPORT/QUARANTINE/ROOT_REPORTS_PENDING_HARNESS_INTAKE/REPORTS" / Path(*parts[1:])
    if parts[0] == "SCHEMAS":
        if len(parts) >= 3 and parts[1] == "AUTHORED" and parts[2] == "T4":
            return repo / "ORGANS/DOCTRINARIUM/SCHEMAS/AUTHORED/T4" / Path(*parts[3:])
        return repo / "ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT/SCHEMAS" / Path(*parts[1:])
    return None

def relocate_root_drift(repo: Path, apply: bool) -> List[Dict[str, Any]]:
    candidates = []
    for root_name in ["DOCTRINARIUM", "SCHEMAS", "REPORTS"]:
        candidates.extend(gather_files(repo / root_name))

    relocations = []
    for src in candidates:
        dst = map_destination(repo, src)
        if dst is None:
            continue
        rel_src = src.relative_to(repo).as_posix()
        rel_dst = dst.relative_to(repo).as_posix()
        before = sha256(src)
        entry = {
            "source_rel": rel_src,
            "destination_rel": rel_dst,
            "bytes": src.stat().st_size,
            "sha256_before": before,
            "sha256_after": None,
            "sha256_match": False,
            "action": "PLAN" if not apply else "MOVE",
        }
        if apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            final_dst = dst
            if final_dst.exists():
                if sha256(final_dst) == before:
                    src.unlink()
                    entry["action"] = "DEDUP_SOURCE_REMOVED"
                else:
                    final_dst = dst.with_name(dst.stem + "__COLLISION__" + before[:12] + dst.suffix)
                    shutil.move(str(src), str(final_dst))
                    entry["action"] = "MOVE_WITH_COLLISION_RENAME"
                    entry["destination_rel"] = final_dst.relative_to(repo).as_posix()
            else:
                shutil.move(str(src), str(final_dst))
            actual = repo / entry["destination_rel"]
            entry["sha256_after"] = sha256(actual) if actual.is_file() else None
            entry["sha256_match"] = entry["sha256_after"] == before if entry["sha256_after"] else False
        relocations.append(entry)

    if apply:
        for root_name in ["DOCTRINARIUM", "SCHEMAS", "REPORTS"]:
            root = repo / root_name
            if root.exists():
                # remove empty tree from leaves up
                for d in sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda p: len(p.parts), reverse=True):
                    try: d.rmdir()
                    except OSError: pass
                try: root.rmdir()
                except OSError: pass

    return relocations

def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def build_root_zone_registry(repo: Path, root_entries: Dict[str, List[str]], generated: str) -> Dict[str, Any]:
    zones = []
    for d in root_entries["dirs"]:
        if d in ALLOWED_ROOT_DIRS:
            status = "ALLOWED_REALITY_ROOT"
        elif d in TRANSITIONAL_DEBT_DIRS:
            status = "TRANSITIONAL_EXTERNALIZATION_DEBT"
        else:
            status = "ROOT_DRIFT"
        zones.append({"entry": d, "kind": "directory", "status": status})
    for f in root_entries["files"]:
        if f in ALLOWED_ROOT_FILES:
            status = "ALLOWED_REALITY_ROOT_FILE"
        elif fnmatch.fnmatch(f, "APPLY_*.ps1") or fnmatch.fnmatch(f, "*_FILE_MANIFEST_SHA256.json"):
            status = "FORBIDDEN_TRANSPORT_REGRESSION"
        else:
            status = "ROOT_DRIFT_FILE"
        zones.append({"entry": f, "kind": "file", "status": status})
    return {
        "registry_id": "administratum.root_zone_governance_registry.v0_1",
        "patch_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "allowed_root_dirs": sorted(ALLOWED_ROOT_DIRS),
        "allowed_root_files": sorted(ALLOWED_ROOT_FILES),
        "transitional_debt_dirs": sorted(TRANSITIONAL_DEBT_DIRS),
        "zones": zones
    }

def detect_external_pillars() -> Dict[str, Any]:
    candidates = {
        "IMPERIUM_WARP": Path(r"E:\IMPERIUM_WARP"),
        "IMPERIUM_HARNESS": Path(r"E:\IMPERIUM_HARNESS"),
    }
    return {name: {"path": str(path), "exists": path.exists()} for name, path in candidates.items()}

def validate(repo: Path, relocations: List[Dict[str, Any]], checks: List[Dict[str, Any]], warnings: List[str], errors: List[str]):
    required = [ROOT_CANON_MATRIX, PILLAR_MATRIX, GREAT_NINE_MATRIX, POLICY_MD, RECEIPT_SCHEMA]
    missing = [p.as_posix() for p in required if not (repo / p).is_file()]
    add(checks, "required_governance_files_exist", not missing, {"missing": missing})
    if missing:
        errors.append("Missing governance files: " + ", ".join(missing))

    root_entries = list_root_entries(repo)
    transport_regressions = [f for f in root_entries["files"] if fnmatch.fnmatch(f, "APPLY_*.ps1") or fnmatch.fnmatch(f, "*_FILE_MANIFEST_SHA256.json")]
    add(checks, "no_root_transport_regression", not transport_regressions, {"transport_regressions": transport_regressions})
    if transport_regressions:
        errors.append("Root transport regression: " + ", ".join(transport_regressions))

    forbidden_dirs_present = [d for d in ["DOCTRINARIUM", "SCHEMAS", "REPORTS"] if (repo / d).exists()]
    add(checks, "forbidden_root_drift_dirs_absent", not forbidden_dirs_present, {"present": forbidden_dirs_present})
    if forbidden_dirs_present:
        errors.append("Forbidden root drift dirs still present: " + ", ".join(forbidden_dirs_present))

    allowed_or_transitional = set(ALLOWED_ROOT_DIRS) | set(TRANSITIONAL_DEBT_DIRS)
    unknown_dirs = [d for d in root_entries["dirs"] if d not in allowed_or_transitional]
    unknown_files = [f for f in root_entries["files"] if f not in ALLOWED_ROOT_FILES]
    add(checks, "root_contains_only_allowed_or_transitional_entries", not unknown_dirs and not unknown_files, {"unknown_dirs": unknown_dirs, "unknown_files": unknown_files})
    if unknown_dirs or unknown_files:
        errors.append("Root contains non-canon entries: dirs=" + ",".join(unknown_dirs) + " files=" + ",".join(unknown_files))

    transitional_present = [d for d in root_entries["dirs"] if d in TRANSITIONAL_DEBT_DIRS]
    add(checks, "transitional_warp_harness_debt_recorded", True, {"present": transitional_present})
    if "WARP" in transitional_present:
        warnings.append("WARP remains inside Reality as transitional debt; canonical external home is E:/IMPERIUM_WARP.")
    if "_HARNESS" in transitional_present:
        warnings.append("_HARNESS remains inside Reality as transitional debt; canonical external home is E:/IMPERIUM_HARNESS.")

    hash_bad = [r for r in relocations if r.get("sha256_after") and not r.get("sha256_match")]
    add(checks, "relocated_sha256_match", not hash_bad, {"bad": [r["destination_rel"] for r in hash_bad]})
    if hash_bad:
        errors.append("Relocated SHA256 mismatch")

    # If source existed, destination must exist and match. If no source existed, no-op is OK.
    missing_dest = [r for r in relocations if not (repo / r["destination_rel"]).is_file()]
    add(checks, "relocated_destinations_exist", not missing_dest, {"missing": [r["destination_rel"] for r in missing_dest]})
    if missing_dest:
        errors.append("Some relocated destinations missing")

    # Great Nine canonical homes
    missing_organs = [o for o in GREAT_NINE if not (repo / "ORGANS" / o).is_dir()]
    add(checks, "great_nine_canonical_homes_exist", not missing_organs, {"missing_organs": missing_organs})
    if missing_organs:
        errors.append("Missing Great Nine canonical homes: " + ", ".join(missing_organs))

    add(checks, "throne_crown_home_exists", (repo / "ORGANS/THRONE").is_dir(), {})
    if not (repo / "ORGANS/THRONE").is_dir():
        errors.append("Missing Throne crown home")

    # Canon import destinations
    add(checks, "doctrinarium_import_zone_exists", (repo / "ORGANS/DOCTRINARIUM/LEGACY_ROOT_IMPORT").exists(), {})
    add(checks, "support_quarantine_exists", (repo / "SUPPORT/QUARANTINE").exists(), {})

def write_outputs(repo: Path, root_entries: Dict[str, List[str]], relocations: List[Dict[str, Any]], checks: List[Dict[str, Any]], warnings: List[str], errors: List[str], dry_run: bool):
    generated = utc()
    external_pillars = detect_external_pillars()
    verdict = "PASS_REALITY_ROOT_CANON_WITH_TRANSITIONAL_DEBT" if not errors else "FAIL_ROOT_CANON_DRIFT"

    root_state = {
        "dirs": root_entries["dirs"],
        "files": root_entries["files"],
        "allowed_root_dirs": sorted(ALLOWED_ROOT_DIRS),
        "allowed_root_files": sorted(ALLOWED_ROOT_FILES),
        "transitional_debt_dirs": sorted([d for d in root_entries["dirs"] if d in TRANSITIONAL_DEBT_DIRS]),
        "external_pillars": external_pillars
    }

    receipt = {
        "receipt_id": "receipt.mechanicus.reality_root_governance.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "root_state": root_state,
        "relocations": relocations,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "outputs": {
            "root_zone_registry": ROOT_ZONE_REGISTRY.as_posix(),
            "root_drift_registry": ROOT_DRIFT_REGISTRY.as_posix(),
            "receipt": RECEIPT_JSON.as_posix(),
            "report": REPORT_MD.as_posix()
        },
        "meaning": "Reality root canon is defined; obvious root drift is relocated; internal WARP/_HARNESS are recorded as transitional debt, not final v1 form."
    }

    if dry_run:
        return receipt

    registry = build_root_zone_registry(repo, root_entries, generated)
    drift_registry = {
        "registry_id": "administratum.root_drift_relocation_registry.v0_1",
        "patch_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "relocations": relocations,
        "meaning": "Registered moves from forbidden root drift zones into canonical import/quarantine homes."
    }

    for path in [ROOT_ZONE_REGISTRY, ROOT_DRIFT_REGISTRY, RECEIPT_JSON, REPORT_MD]:
        (repo / path).parent.mkdir(parents=True, exist_ok=True)

    (repo / ROOT_ZONE_REGISTRY).write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / ROOT_DRIFT_REGISTRY).write_text(json.dumps(drift_registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT_JSON).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    reloc_md = "\n".join(f"- `{r['source_rel']}` -> `{r['destination_rel']}` sha256_match=`{r.get('sha256_match')}` action=`{r.get('action')}`" for r in relocations) if relocations else "- none"
    dirs_md = "\n".join(f"- `{d}`" for d in root_entries["dirs"]) if root_entries["dirs"] else "- none"
    files_md = "\n".join(f"- `{f}`" for f in root_entries["files"]) if root_entries["files"] else "- none"
    ext_md = "\n".join(f"- `{k}`: `{v['path']}` exists=`{v['exists']}`" for k, v in external_pillars.items())

    (repo / REPORT_MD).write_text(f"""# REALITY ROOT GOVERNANCE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

This is the first Reality Canon / Root Law patch.

It defines `E:\\IMPERIUM_REALITY` as Core Reality, while `E:\\IMPERIUM_WARP` and `E:\\IMPERIUM_HARNESS` are external pillars.

Internal `WARP/` and `_HARNESS/` are not final root canon. They are recorded as transitional debt until dedicated externalization patches land.

## Current root directories

{dirs_md}

## Current root files

{files_md}

## External pillar visibility

{ext_md}

## Relocations

{reloc_md}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{ROOT_ZONE_REGISTRY.as_posix()}`
- `{ROOT_DRIFT_REGISTRY.as_posix()}`
- `{RECEIPT_JSON.as_posix()}`
""", encoding="utf-8")

    return receipt

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    checks: List[Dict[str, Any]] = []
    warnings: List[str] = []
    errors: List[str] = []

    relocations = relocate_root_drift(repo, apply=args.apply and not args.dry_run)
    root_entries = list_root_entries(repo)
    validate(repo, relocations, checks, warnings, errors)

    add(checks, "root_drift_relocation_registry_planned", True, {"relocation_count": len(relocations)})
    add(checks, "external_pillar_policy_defined", (repo / PILLAR_MATRIX).is_file(), {"warp": "E:/IMPERIUM_WARP", "harness": "E:/IMPERIUM_HARNESS"})
    add(checks, "great_nine_alias_policy_defined", (repo / GREAT_NINE_MATRIX).is_file(), {})

    receipt = write_outputs(repo, root_entries, relocations, checks, warnings, errors, dry_run=args.dry_run)

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": receipt["verdict"],
        "root_dirs": root_entries["dirs"],
        "root_files": root_entries["files"],
        "relocation_count": len(relocations),
        "transitional_debt_dirs": receipt["root_state"]["transitional_debt_dirs"],
        "external_pillars": receipt["root_state"]["external_pillars"],
        "receipt": RECEIPT_JSON.as_posix(),
        "report": REPORT_MD.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))

    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
