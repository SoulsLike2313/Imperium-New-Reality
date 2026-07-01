#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "ASTRONOMICON-PATCH-PACK-INTAKE-AND-VALIDATION-SMOKE-0001"
MATRIX_PATH = Path("ORGANS/ASTRONOMICON/MATRICES/ASTRONOMICON_PATCH_PACK_SMOKE_VALIDATION_MATRIX_V0_1.json")

VERDICT_PATTERN = re.compile(r"\b(PASS[_A-Z0-9-]*|FAIL[_A-Z0-9-]*|PARTIAL[_A-Z0-9-]*|CLOSED[_A-Z0-9-]*|UNPROVEN[_A-Z0-9-]*)\b")
RECEIPT_PATTERN = re.compile(r"([A-Za-z0-9_\-/]+receipt[A-Za-z0-9_\-/]*\.json)", re.IGNORECASE)

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, str(e)

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def rel(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except Exception:
        return path.as_posix()

def find_patch_dirs(repo: Path, patch_id: str | None = None) -> List[Path]:
    root = repo / "WARP" / "PATCHES"
    if not root.is_dir():
        return []
    if patch_id:
        p = root / patch_id
        return [p] if p.is_dir() else []
    return sorted([p for p in root.iterdir() if p.is_dir()])

def find_intake_drafts(repo: Path) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for base in [repo / "WARP" / "TASKS", repo / "ORGANS" / "ASTRONOMICON" / "REPORTS" / "DRY_RUN_SELFTEST_TASKS"]:
        if not base.is_dir():
            continue
        for intake in base.glob("*/00_INTAKE"):
            if not intake.is_dir():
                continue
            text = ""
            for name in ["TASK_INTAKE_PACKET_V0_1.json", "TASK_CLASSIFICATION_V0_1.json", "OWNER_INTENT_CAPTURE_V0_1.json"]:
                p = intake / name
                if p.is_file():
                    text += " " + read_text(p)
            result[intake.parent.name] = [rel(repo, intake), text]
    return result

def parse_expected_from_text(text: str) -> Tuple[List[str], List[str]]:
    verdicts = sorted(set(VERDICT_PATTERN.findall(text or "")))
    receipts = sorted(set(RECEIPT_PATTERN.findall(text or "")))
    return verdicts, receipts

def parse_manifest_like(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    data, err = load_json(path)
    if err or not isinstance(data, dict):
        return {}
    return data

def find_actual_receipts(repo: Path, expected_receipts: List[str]) -> List[Dict[str, Any]]:
    found: List[Dict[str, Any]] = []
    if not expected_receipts:
        return []
    normalized_expected = [x.replace("\\", "/").lower() for x in expected_receipts]
    candidates = list((repo / "ORGANS").glob("*/RECEIPTS/*.json")) if (repo / "ORGANS").is_dir() else []
    candidates += list((repo / "WARP").glob("**/*receipt*.json")) if (repo / "WARP").is_dir() else []
    seen = set()
    for c in candidates:
        c_rel = rel(repo, c)
        if c_rel in seen:
            continue
        seen.add(c_rel)
        c_low = c_rel.lower()
        name_low = c.name.lower()
        matched = False
        if not normalized_expected:
            matched = True
        else:
            for exp in normalized_expected:
                exp_name = exp.split("/")[-1]
                if exp in c_low or exp_name == name_low:
                    matched = True
                    break
        if not matched:
            continue
        data, err = load_json(c)
        verdict = None
        task_id = None
        validator_id = None
        if not err and isinstance(data, dict):
            verdict = data.get("verdict")
            task_id = data.get("task_id")
            validator_id = data.get("validator_id")
        found.append({
            "path": c_rel,
            "verdict": verdict,
            "task_id": task_id,
            "validator_id": validator_id,
            "parse_error": err
        })
    return sorted(found, key=lambda x: x["path"])

def smoke_patch(repo: Path, patch_dir: Path, intake_index: Dict[str, List[str]]) -> Dict[str, Any]:
    patch_id = patch_dir.name
    patch_pack = patch_dir / "PATCH_PACK.md"
    manifest_path = patch_dir / "PATCH_FILE_MANIFEST_SHA256.json"
    files_to_land = patch_dir / "FILES_TO_LAND"
    runners = sorted([p for p in patch_dir.glob("RUN_*.ps1") if p.is_file()])
    manifest_v1 = patch_dir / "PATCH_PACK_MANIFEST_V0_1.json"

    errors: List[str] = []
    warnings: List[str] = []
    is_patch_pack = True

    if not patch_pack.is_file() and not manifest_v1.is_file():
        is_patch_pack = False
        errors.append("missing PATCH_PACK.md or PATCH_PACK_MANIFEST_V0_1.json")
    if not runners:
        warnings.append("missing RUN_*.ps1 runner or explicit no-runner declaration")
    if not manifest_path.is_file():
        warnings.append("missing PATCH_FILE_MANIFEST_SHA256.json or explicit manifest gap")
    if not files_to_land.is_dir():
        warnings.append("missing FILES_TO_LAND or explicit no-land declaration")

    text = ""
    if patch_pack.is_file():
        text += read_text(patch_pack)
    if manifest_v1.is_file():
        text += " " + read_text(manifest_v1)

    declared_verdicts, declared_receipts = parse_expected_from_text(text)

    manifest = parse_manifest_like(manifest_v1)
    if manifest:
        for key in ["expected_verdict", "expected_verdicts"]:
            v = manifest.get(key)
            if isinstance(v, str):
                declared_verdicts.append(v)
            elif isinstance(v, list):
                declared_verdicts += [str(x) for x in v]
        v = manifest.get("expected_receipts")
        if isinstance(v, list):
            declared_receipts += [str(x) for x in v]
        elif isinstance(v, str):
            declared_receipts.append(v)

    declared_verdicts = sorted(set([v for v in declared_verdicts if v]))
    declared_receipts = sorted(set([r for r in declared_receipts if r]))

    # Link to intake drafts only as informative evidence, not Task Pack.
    linked_intake_candidates = []
    p_text_low = text.lower()
    for task_id, pair in intake_index.items():
        intake_path, intake_text = pair
        if task_id.lower() in p_text_low or patch_id.lower().replace("-", "_") in intake_text.lower().replace("-", "_"):
            linked_intake_candidates.append({"task_id": task_id, "path": intake_path, "status": "INTAKE_DRAFT_ONLY"})

    actual_receipts = find_actual_receipts(repo, declared_receipts)

    matching_verdict_receipts = []
    for r in actual_receipts:
        if r.get("verdict") and (not declared_verdicts or r["verdict"] in declared_verdicts):
            matching_verdict_receipts.append(r)

    if not is_patch_pack:
        smoke_verdict = "NOT_A_PATCH_PACK"
        evidence_level = "DECLARED_ONLY"
    elif not declared_verdicts and not declared_receipts:
        smoke_verdict = "INSUFFICIENT_DECLARATION"
        evidence_level = "DECLARED_ONLY"
    elif declared_receipts and not actual_receipts:
        smoke_verdict = "PARTIAL"
        evidence_level = "DECLARED_ONLY"
    elif actual_receipts and declared_verdicts and matching_verdict_receipts:
        smoke_verdict = "CLOSED_BY_DECLARED_GOALS"
        evidence_level = "RECEIPT_VERDICT_MATCHES"
    elif actual_receipts and not declared_verdicts:
        smoke_verdict = "UNPROVEN_RECEIPT_ONLY"
        evidence_level = "RECEIPT_EXISTS"
    elif actual_receipts and declared_verdicts and not matching_verdict_receipts:
        smoke_verdict = "FAILED"
        evidence_level = "RECEIPT_EXISTS"
    else:
        smoke_verdict = "PARTIAL"
        evidence_level = "DECLARED_ONLY"

    return {
        "artifact_id": "ASTRONOMICON_PATCH_PACK_SMOKE_RESULT_V0_1",
        "patch_id": patch_id,
        "path": rel(repo, patch_dir),
        "is_patch_pack": is_patch_pack,
        "smoke_verdict": smoke_verdict,
        "evidence_level": evidence_level,
        "declared_expected_verdicts": declared_verdicts,
        "declared_expected_receipts": declared_receipts,
        "actual_receipts_found": actual_receipts,
        "matching_verdict_receipts": matching_verdict_receipts,
        "linked_intake_candidates": linked_intake_candidates,
        "shape": {
            "patch_pack_doc": rel(repo, patch_pack) if patch_pack.is_file() else None,
            "runner_count": len(runners),
            "manifest_exists": manifest_path.is_file(),
            "files_to_land_exists": files_to_land.is_dir()
        },
        "warnings": warnings,
        "errors": errors,
        "meaning": "Smoke comparison only. This is not trust, not Inquisition anti-fake-green, and not Throne verdict."
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--patch-id")
    ap.add_argument("--out", default="ORGANS/ASTRONOMICON/REPORTS/PATCH_PACK_SMOKE_VALIDATION_SUMMARY_V0_1.json")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    intake_index = find_intake_drafts(repo)
    patch_dirs = find_patch_dirs(repo, args.patch_id)
    results = [smoke_patch(repo, p, intake_index) for p in patch_dirs]

    out = repo / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "summary_id": "astronomicon.patch_pack_smoke_validation_summary.v0_1",
        "patch_id": PATCH_ID,
        "generated_at_utc": utc(),
        "target_patch_id": args.patch_id,
        "patch_count": len(results),
        "results": results,
        "meaning": "Astronomicon smoke-tested Patch Pack declarations against visible receipts without executing runners."
    }
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
