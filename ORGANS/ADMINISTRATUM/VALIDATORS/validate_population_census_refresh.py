#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, csv, datetime as dt, fnmatch, json, os, re, subprocess, hashlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "IMPERIUM-POPULATION-CENSUS-REFRESH-0001"
VALIDATOR_ID = "imperium_population_census_refresh_validator.v0_2"

CENSUS_JSON = Path("ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_POPULATION_CENSUS_CURRENT_V0_2.json")
SUMMARY_JSON = Path("ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_POPULATION_SUMMARY_CURRENT_V0_2.json")
ROOT_ZONES_JSON = Path("ORGANS/ADMINISTRATUM/REGISTRY/IMPERIUM_ROOT_ZONE_REGISTRY_V0_2.json")
RECEIPT_JSON = Path("ORGANS/ADMINISTRATUM/RECEIPTS/population_census_refresh_receipt.json")
REPORT_MD = Path("ORGANS/ADMINISTRATUM/REPORTS/IMPERIUM_POPULATION_CENSUS_REFRESH_REPORT_V0_2.md")
LEGACY_CENSUS_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_CENSUS_V0_1.json")
TRANSPORT_INDEX = Path("SUPPORT/TRANSPORT/ROOT_TRANSPORT_INDEX_V0_1.json")
MATRIX_JSON = Path("ORGANS/ADMINISTRATUM/MATRICES/IMPERIUM_POPULATION_CENSUS_REFRESH_MATRIX_V0_2.json")
STALE_MATRIX_JSON = Path("ORGANS/THRONE/MATRICES/CENSUS_STALENESS_GUARD_MATRIX_V0_1.json")

GREAT_NINE = {
    "ASTRONOMICON", "ADMINISTRATUM", "DOCTRINARIUM", "MECHANICUS", "INQUISITION",
    "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "OFFICIO_AGENTIS"
}
CROWN = {"THRONE"}

CANONICAL_ROOTS = {
    "ORGANS", "WARP", "SUPPORT", "REPORTS", "SCHEMAS", "DOCTRINARIUM", "_HARNESS",
    ".editorconfig", ".gitattributes", ".gitignore", "AGENTS.md", "README.md"
}

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def run_git(repo: Path, args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run(["git"] + args, cwd=str(repo), text=True, capture_output=True, timeout=60)
    return p.returncode, p.stdout, p.stderr

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024 * 1024), b""):
            h.update(c)
    return h.hexdigest()

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def git_ls_files(repo: Path) -> List[str]:
    code, out, err = run_git(repo, ["ls-files"])
    if code != 0:
        raise RuntimeError(err or "git ls-files failed")
    return [line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()]

def git_head(repo: Path) -> str:
    code, out, err = run_git(repo, ["rev-parse", "HEAD"])
    return out.strip() if code == 0 else "UNKNOWN"

def git_status_porcelain(repo: Path) -> str:
    code, out, err = run_git(repo, ["status", "--porcelain"])
    return out if code == 0 else ""

def first_segment(path: str) -> str:
    return path.split("/", 1)[0] if "/" in path else path

def infer_owner(path: str) -> str:
    parts = path.split("/")
    if not parts:
        return "UNKNOWN"
    root = parts[0]
    if root == "ORGANS" and len(parts) > 1:
        organ = parts[1]
        if organ in GREAT_NINE or organ in CROWN:
            return organ
        return f"ORGANS/{organ}"
    if root == "WARP":
        if len(parts) > 2 and parts[1] == "PATCHES":
            return f"WARP_PATCH/{parts[2]}"
        return "WARP"
    if root == "SUPPORT":
        if len(parts) > 1:
            return f"SUPPORT/{parts[1]}"
        return "SUPPORT"
    if root == "REPORTS":
        return "REPORTS"
    if root == "SCHEMAS":
        return "SCHEMAS"
    if root == "DOCTRINARIUM":
        return "DOCTRINARIUM_ROOT"
    if root == "_HARNESS":
        return "_HARNESS"
    if root in [".editorconfig", ".gitattributes", ".gitignore", "AGENTS.md", "README.md"]:
        return "ROOT_GOVERNANCE"
    return "UNKNOWN"

def infer_status(path: str) -> str:
    if path.startswith("WARP/"):
        return "WARP"
    if path.startswith("SUPPORT/TRANSPORT/"):
        return "TRANSPORT"
    if path.startswith("_HARNESS/"):
        return "HARNESS"
    if "/" not in path:
        return "ROOT"
    if path.startswith("ORGANS/") or path.startswith("DOCTRINARIUM/") or path.startswith("REPORTS/") or path.startswith("SCHEMAS/"):
        return "REALITY"
    if path.startswith("SUPPORT/"):
        return "SUPPORT"
    return "UNKNOWN"

def infer_class(path: str) -> str:
    low = path.lower()
    name = path.rsplit("/", 1)[-1].lower()
    if name == "patch_pack.md":
        return "PATCH_PACK"
    if "/validators/" in low and low.endswith(".py"):
        return "VALIDATOR"
    if "/receipts/" in low or "receipt" in name:
        return "RECEIPT"
    if "/reports/" in low or "report" in name:
        return "REPORT"
    if "/schemas/" in low or name.endswith(".schema.json"):
        return "SCHEMA"
    if "/matrices/" in low or "matrix" in name:
        return "MATRIX"
    if "/registry/" in low or "registry" in name or "index" in name:
        return "REGISTRY"
    if "/tests/" in low or "test" in name:
        return "TEST"
    if "/tools/" in low or "/tool" in low:
        return "TOOL"
    if "/tui/" in low:
        return "TUI"
    if "/dashboards/" in low:
        return "DASHBOARD"
    if "/eyes/" in low:
        return "EYES"
    if "/block/" in low:
        return "BLOCK"
    if "/lessons/" in low:
        return "LESSON"
    if "/negative_lessons/" in low or "negative" in name:
        return "NEGATIVE_LESSON"
    if "/support/transport/apply_scripts/" in low or name.startswith("apply_"):
        return "TRANSPORT_APPLY_SCRIPT"
    if "/support/transport/file_manifests/" in low or name.endswith("_file_manifest_sha256.json"):
        return "TRANSPORT_FILE_MANIFEST"
    if name.endswith(".ps1"):
        return "POWERSHELL"
    if name.endswith(".py"):
        return "PYTHON"
    if name.endswith(".json"):
        return "JSON"
    if name.endswith(".md"):
        return "MARKDOWN"
    if name in [".editorconfig", ".gitattributes", ".gitignore"]:
        return "ROOT_CONFIG"
    return "OTHER"

def resident_id(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]

def build_residents(repo: Path, files: List[str]) -> List[Dict[str, Any]]:
    residents = []
    for path in files:
        p = repo / path
        root_zone = first_segment(path)
        owner = infer_owner(path)
        cls = infer_class(path)
        status = infer_status(path)
        residents.append({
            "resident_id": f"resident.{resident_id(path)}",
            "path": path,
            "root_zone": root_zone,
            "owner": owner,
            "resident_class": cls,
            "status": status,
            "bytes": p.stat().st_size if p.is_file() else None,
            "sha256": sha256(p) if p.is_file() else None
        })
    return residents

def summarize(residents: List[Dict[str, Any]]) -> Dict[str, Any]:
    def count_by(key: str) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for r in residents:
            out[r[key]] = out.get(r[key], 0) + 1
        return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))

    total = len(residents)
    unknown_owner = sum(1 for r in residents if r["owner"] == "UNKNOWN")
    unknown_class = sum(1 for r in residents if r["resident_class"] == "OTHER")
    unknown_status = sum(1 for r in residents if r["status"] == "UNKNOWN")
    root_zone_summary = count_by("root_zone")
    owner_summary = count_by("owner")
    class_summary = count_by("resident_class")
    status_summary = count_by("status")
    coverage = {
        "owner_coverage_score": round((total - unknown_owner) * 100 / max(1, total), 2),
        "classification_coverage_score": round((total - unknown_class) * 100 / max(1, total), 2),
        "status_coverage_score": round((total - unknown_status) * 100 / max(1, total), 2),
        "unknown_owner_count": unknown_owner,
        "unknown_class_count": unknown_class,
        "unknown_status_count": unknown_status
    }
    return {
        "population_total": total,
        "root_zone_summary": root_zone_summary,
        "owner_summary": owner_summary,
        "class_summary": class_summary,
        "status_summary": status_summary,
        "coverage": coverage
    }

def load_json_if_exists(path: Path) -> Any | None:
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

def get_population_from_legacy(data: Any) -> int | None:
    if not isinstance(data, dict):
        return None
    for key in ["population_total"]:
        if isinstance(data.get(key), int):
            return data[key]
    if isinstance(data.get("residents"), list):
        return len(data["residents"])
    return None

def write_outputs(repo: Path, census: Dict[str, Any], summary: Dict[str, Any], root_registry: Dict[str, Any], receipt: Dict[str, Any], dry_run: bool):
    if dry_run:
        return
    for path in [CENSUS_JSON, SUMMARY_JSON, ROOT_ZONES_JSON, RECEIPT_JSON, REPORT_MD]:
        (repo / path).parent.mkdir(parents=True, exist_ok=True)

    (repo / CENSUS_JSON).write_text(json.dumps(census, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / SUMMARY_JSON).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / ROOT_ZONES_JSON).write_text(json.dumps(root_registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT_JSON).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    coverage = census["coverage"]
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in receipt["checks"])
    warnings_md = "\n".join(f"- {w}" for w in receipt["warnings"]) if receipt["warnings"] else "- none"
    errors_md = "\n".join(f"- {e}" for e in receipt["errors"]) if receipt["errors"] else "- none"
    rz_md = "\n".join(f"- `{k}`: `{v}`" for k, v in census["root_zone_summary"].items())

    (repo / REPORT_MD).write_text(f"""# IMPERIUM POPULATION CENSUS REFRESH REPORT V0.2

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Meaning

This report refreshes the current Imperium population census after root transport relocation.

The current census now lives as a first-class Administratum registry artifact.

Legacy WARP census artifacts remain historical unless explicitly refreshed.

## Summary

- population_total: `{census['population_total']}`
- tracked_file_count: `{census['tracked_file_count']}`
- repo_head: `{census['repo_head']}`
- owner_coverage_score: `{coverage['owner_coverage_score']}`
- classification_coverage_score: `{coverage['classification_coverage_score']}`
- status_coverage_score: `{coverage['status_coverage_score']}`
- unknown_owner_count: `{coverage['unknown_owner_count']}`
- unknown_class_count: `{coverage['unknown_class_count']}`
- unknown_status_count: `{coverage['unknown_status_count']}`

## Root zones

{rz_md}

## Transport hygiene state

- root_apply_scripts: `{census['root_transport_hygiene_state']['root_apply_scripts']}`
- root_file_manifests: `{census['root_transport_hygiene_state']['root_file_manifests']}`
- support_transport_index_exists: `{census['root_transport_hygiene_state']['support_transport_index_exists']}`

## Legacy comparison

- legacy_census_exists: `{receipt['legacy_comparison']['legacy_census_exists']}`
- legacy_population_total: `{receipt['legacy_comparison']['legacy_population_total']}`
- population_delta_vs_legacy: `{receipt['legacy_comparison']['population_delta_vs_legacy']}`

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{CENSUS_JSON.as_posix()}`
- `{SUMMARY_JSON.as_posix()}`
- `{ROOT_ZONES_JSON.as_posix()}`
- `{RECEIPT_JSON.as_posix()}`
""", encoding="utf-8")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    generated = utc()
    checks: List[Dict[str, Any]] = []
    warnings: List[str] = []
    errors: List[str] = []

    before_status = git_status_porcelain(repo)

    try:
        tracked_files = git_ls_files(repo)
        add(checks, "git_ls_files_available", True, {"tracked_file_count": len(tracked_files)})
    except Exception as e:
        tracked_files = []
        add(checks, "git_ls_files_available", False, {"error": str(e)})
        errors.append(f"git ls-files failed: {e}")

    # Include currently untracked patch outputs created by this run only after copy?
    # This census is of tracked Reality baseline + landed/working patch files visible to git after git add.
    # For pre-commit validation we also include existing working-tree files under canonical zones that may not yet be tracked.
    tracked_set = set(tracked_files)
    candidate_untracked = []
    for root in ["ORGANS", "SUPPORT", "WARP", "REPORTS", "SCHEMAS", "DOCTRINARIUM", "_HARNESS"]:
        base = repo / root
        if base.exists():
            for p in base.rglob("*"):
                if p.is_file() and ".git" not in p.parts:
                    rel = p.relative_to(repo).as_posix()
                    if rel not in tracked_set and "__pycache__" not in rel and not rel.endswith(".pyc"):
                        candidate_untracked.append(rel)
    all_files = sorted(tracked_set.union(candidate_untracked))

    residents = build_residents(repo, all_files)
    summary_core = summarize(residents)

    head = git_head(repo)

    root_apply = [p.name for p in repo.glob("APPLY_*.ps1") if p.is_file()]
    root_manifests = [p.name for p in repo.glob("*_FILE_MANIFEST_SHA256.json") if p.is_file()]
    transport_state = {
        "root_apply_scripts": root_apply,
        "root_file_manifests": root_manifests,
        "support_transport_index_exists": (repo / TRANSPORT_INDEX).is_file(),
        "support_transport_apply_count": len(list((repo / "SUPPORT/TRANSPORT/APPLY_SCRIPTS").glob("*"))) if (repo / "SUPPORT/TRANSPORT/APPLY_SCRIPTS").exists() else 0,
        "support_transport_manifest_count": len(list((repo / "SUPPORT/TRANSPORT/FILE_MANIFESTS").glob("*"))) if (repo / "SUPPORT/TRANSPORT/FILE_MANIFESTS").exists() else 0,
    }

    add(checks, "root_transport_clutter_absent", not root_apply and not root_manifests, {"root_apply": root_apply, "root_manifests": root_manifests})
    if root_apply or root_manifests:
        errors.append("Root transport clutter present after relocation")

    add(checks, "support_transport_index_exists", transport_state["support_transport_index_exists"], {"path": TRANSPORT_INDEX.as_posix()})
    if not transport_state["support_transport_index_exists"]:
        warnings.append("Support transport index not found; root relocation provenance may be incomplete")

    add(checks, "census_matrix_exists", (repo / MATRIX_JSON).is_file(), {"path": MATRIX_JSON.as_posix()})
    add(checks, "staleness_guard_matrix_exists", (repo / STALE_MATRIX_JSON).is_file(), {"path": STALE_MATRIX_JSON.as_posix()})
    if not (repo / MATRIX_JSON).is_file():
        errors.append("Census refresh matrix missing")
    if not (repo / STALE_MATRIX_JSON).is_file():
        errors.append("Census staleness guard matrix missing")

    unknown_roots = [z for z in summary_core["root_zone_summary"] if z not in CANONICAL_ROOTS]
    add(checks, "root_zones_registered", len(unknown_roots) == 0, {"unknown_root_zones": unknown_roots})
    if unknown_roots:
        warnings.append("Unknown root zones detected: " + ", ".join(unknown_roots))

    legacy_data = load_json_if_exists(repo / LEGACY_CENSUS_JSON)
    legacy_total = get_population_from_legacy(legacy_data)
    legacy_comparison = {
        "legacy_census_exists": legacy_data is not None,
        "legacy_census_path": LEGACY_CENSUS_JSON.as_posix(),
        "legacy_population_total": legacy_total,
        "population_delta_vs_legacy": (summary_core["population_total"] - legacy_total) if isinstance(legacy_total, int) else None,
        "legacy_is_current": False,
        "meaning": "Legacy WARP census is historical unless explicitly mirrored by a current Administratum refresh."
    }

    census = {
        "census_id": "imperium.population_census.current.v0_2",
        "patch_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": head,
        "tracked_file_count": len(tracked_files),
        "working_tree_visible_file_count": len(all_files),
        "population_total": summary_core["population_total"],
        "root_zone_summary": summary_core["root_zone_summary"],
        "owner_summary": summary_core["owner_summary"],
        "class_summary": summary_core["class_summary"],
        "status_summary": summary_core["status_summary"],
        "coverage": summary_core["coverage"],
        "root_transport_hygiene_state": transport_state,
        "legacy_comparison": legacy_comparison,
        "residents": residents
    }

    root_registry = {
        "registry_id": "imperium.root_zone_registry.v0_2",
        "patch_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": generated,
        "repo_head": head,
        "root_zones": [
            {
                "root_zone": zone,
                "count": count,
                "canonical": zone in CANONICAL_ROOTS,
                "meaning": {
                    "ORGANS": "Organ reality space",
                    "WARP": "Patch/task transient and provenance space",
                    "SUPPORT": "Support and transport utilities",
                    "REPORTS": "Top-level historical/reporting space",
                    "SCHEMAS": "Top-level schema authoring space",
                    "DOCTRINARIUM": "Legacy/root doctrinarium zone; requires governance reconciliation",
                    "_HARNESS": "Harness/testing zone",
                }.get(zone, "Root file or unknown zone")
            }
            for zone, count in summary_core["root_zone_summary"].items()
        ],
        "unknown_root_zones": unknown_roots
    }

    summary = {
        "summary_id": "imperium.population_summary.current.v0_2",
        "patch_id": TASK_ID,
        "generated_at_utc": generated,
        "repo_head": head,
        "population_total": summary_core["population_total"],
        "tracked_file_count": len(tracked_files),
        "working_tree_visible_file_count": len(all_files),
        "coverage": summary_core["coverage"],
        "root_zone_summary": summary_core["root_zone_summary"],
        "top_owners": dict(list(summary_core["owner_summary"].items())[:25]),
        "top_classes": dict(list(summary_core["class_summary"].items())[:25]),
        "status_summary": summary_core["status_summary"],
        "root_transport_hygiene_state": transport_state,
        "legacy_comparison": legacy_comparison
    }

    add(checks, "canonical_census_built", census["population_total"] > 0, {"population_total": census["population_total"]})
    add(checks, "coverage_measured", True, census["coverage"])
    add(checks, "legacy_comparison_built", True, legacy_comparison)

    verdict = "PASS_CENSUS_REFRESHED" if not errors else "FAIL_CENSUS_REFRESH"

    receipt = {
        "receipt_id": "receipt.administratum.population_census_refresh.v0_2",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": head,
        "population_total": census["population_total"],
        "tracked_file_count": census["tracked_file_count"],
        "working_tree_visible_file_count": census["working_tree_visible_file_count"],
        "coverage": census["coverage"],
        "root_zone_summary": census["root_zone_summary"],
        "root_transport_hygiene_state": transport_state,
        "legacy_comparison": legacy_comparison,
        "outputs": {
            "census": CENSUS_JSON.as_posix(),
            "summary": SUMMARY_JSON.as_posix(),
            "root_zones": ROOT_ZONES_JSON.as_posix(),
            "receipt": RECEIPT_JSON.as_posix(),
            "report": REPORT_MD.as_posix()
        },
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "meaning": "Current census is now an Administratum registry artifact with staleness guard data."
    }

    if not args.dry_run:
        write_outputs(repo, census, summary, root_registry, receipt, dry_run=False)

    after_status = git_status_porcelain(repo)

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "repo_head": head,
        "population_total": census["population_total"],
        "tracked_file_count": census["tracked_file_count"],
        "working_tree_visible_file_count": census["working_tree_visible_file_count"],
        "owner_coverage_score": census["coverage"]["owner_coverage_score"],
        "classification_coverage_score": census["coverage"]["classification_coverage_score"],
        "status_coverage_score": census["coverage"]["status_coverage_score"],
        "unknown_owner_count": census["coverage"]["unknown_owner_count"],
        "unknown_class_count": census["coverage"]["unknown_class_count"],
        "unknown_status_count": census["coverage"]["unknown_status_count"],
        "root_zone_count": len(census["root_zone_summary"]),
        "root_transport_hygiene_state": transport_state,
        "legacy_population_total": legacy_total,
        "population_delta_vs_legacy": legacy_comparison["population_delta_vs_legacy"],
        "census": CENSUS_JSON.as_posix(),
        "summary": SUMMARY_JSON.as_posix(),
        "root_zones": ROOT_ZONES_JSON.as_posix(),
        "receipt": RECEIPT_JSON.as_posix(),
        "report": REPORT_MD.as_posix(),
        "errors": errors,
        "git_status_before_lines": len([x for x in before_status.splitlines() if x.strip()]),
        "git_status_after_lines": len([x for x in after_status.splitlines() if x.strip()])
    }, ensure_ascii=False, indent=2))

    return 0 if verdict == "PASS_CENSUS_REFRESHED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
