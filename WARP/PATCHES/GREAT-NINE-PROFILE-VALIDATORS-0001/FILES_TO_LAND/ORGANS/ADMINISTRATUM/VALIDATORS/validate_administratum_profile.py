#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, datetime as dt, hashlib, json
from pathlib import Path
from typing import Any, Dict, List

ORGAN_ID = "ADMINISTRATUM"
VALIDATOR_ID = f"{ORGAN_ID.lower()}_profile_validator.v0_1"
TASK_ID = "GREAT-NINE-PROFILE-VALIDATORS-0001"

REQUIRED_FILES = ["README.md", "ORGAN_CARD.json", "MANIFEST.json", "FUNCTIONS.md"]
REQUIRED_DIRS = [
    "MATRICES", "SCHEMAS", "VALIDATORS", "RECEIPTS", "REPORTS", "TESTS",
    "TUI", "DASHBOARDS", "EYES", "BLOCK", "LESSONS", "NEGATIVE_LESSONS"
]
REQUIRED_CARD_FIELDS = [
    "organ_id", "display_name", "organ_type", "great_nine_member",
    "primary_role", "declared_functions", "declared_tools",
    "declared_validators", "declared_receipts", "forbidden_actions",
    "required_slots", "owner"
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024*1024), b""):
            h.update(c)
    return h.hexdigest()

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    repo = Path(ap.parse_args().repo_root).resolve()

    root = repo / "ORGANS" / ORGAN_ID
    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    add(checks, "organ_directory_exists", root.is_dir(), {"path": f"ORGANS/{ORGAN_ID}"})
    if not root.is_dir():
        errors.append(f"Organ directory missing: ORGANS/{ORGAN_ID}")

    missing_files = [f for f in REQUIRED_FILES if not (root / f).is_file()]
    missing_dirs = [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
    add(checks, "required_files_exist", not missing_files, {"missing_files": missing_files})
    add(checks, "required_dirs_exist", not missing_dirs, {"missing_dirs": missing_dirs})
    errors.extend(f"Missing file: {f}" for f in missing_files)
    errors.extend(f"Missing dir: {d}" for d in missing_dirs)

    card = {}
    card_path = root / "ORGAN_CARD.json"
    try:
        if card_path.is_file():
            card = read_json(card_path)
        add(checks, "organ_card_json_parse", bool(card), {})
    except Exception as e:
        add(checks, "organ_card_json_parse", False, {"error": str(e)})
        errors.append(f"ORGAN_CARD.json parse failed: {e}")

    missing_fields = [f for f in REQUIRED_CARD_FIELDS if f not in card]
    add(checks, "organ_card_required_fields", not missing_fields, {"missing_fields": missing_fields})
    errors.extend(f"ORGAN_CARD missing field: {f}" for f in missing_fields)

    identity_ok = card.get("organ_id") == ORGAN_ID and card.get("great_nine_member") is True
    add(checks, "organ_identity_matches", identity_ok, {
        "organ_id": card.get("organ_id"),
        "great_nine_member": card.get("great_nine_member")
    })
    if not identity_ok:
        errors.append("Organ identity mismatch or great_nine_member is not true")

    declared_functions = card.get("declared_functions", [])
    declared_validators = card.get("declared_validators", [])
    forbidden_actions = card.get("forbidden_actions", [])
    declared_receipts = card.get("declared_receipts", [])

    add(checks, "declared_functions_nonempty", isinstance(declared_functions, list) and len(declared_functions) >= 5, {"count": len(declared_functions) if isinstance(declared_functions, list) else None})
    add(checks, "declared_validators_nonempty", isinstance(declared_validators, list) and len(declared_validators) >= 1, {"count": len(declared_validators) if isinstance(declared_validators, list) else None})
    add(checks, "forbidden_actions_nonempty", isinstance(forbidden_actions, list) and len(forbidden_actions) >= 4, {"count": len(forbidden_actions) if isinstance(forbidden_actions, list) else None})
    add(checks, "declared_receipts_nonempty", isinstance(declared_receipts, list) and len(declared_receipts) >= 1, {"count": len(declared_receipts) if isinstance(declared_receipts, list) else None})

    if not isinstance(declared_functions, list) or len(declared_functions) < 5:
        errors.append("Need at least 5 declared functions")
    if not isinstance(declared_validators, list) or len(declared_validators) < 1:
        errors.append("Need at least 1 declared validator")
    if not isinstance(forbidden_actions, list) or len(forbidden_actions) < 4:
        errors.append("Need at least 4 forbidden actions")
    if not isinstance(declared_receipts, list) or len(declared_receipts) < 1:
        errors.append("Need at least 1 declared receipt")

    validator_file = root / "VALIDATORS" / f"validate_{ORGAN_ID.lower()}_profile.py"
    validator_exists = validator_file.is_file()
    add(checks, "profile_validator_file_exists", validator_exists, {"path": str(validator_file.relative_to(repo)) if validator_exists else None})
    if not validator_exists:
        errors.append("Profile validator file missing")

    manifest_ok = False
    manifest_path = root / "MANIFEST.json"
    try:
        manifest = read_json(manifest_path) if manifest_path.is_file() else {}
        files = manifest.get("files", [])
        wanted = {f"ORGANS/{ORGAN_ID}/README.md", f"ORGANS/{ORGAN_ID}/ORGAN_CARD.json", f"ORGANS/{ORGAN_ID}/FUNCTIONS.md"}
        listed = {x.get("path") for x in files if isinstance(x, dict)}
        manifest_ok = wanted.issubset(listed)
        add(checks, "manifest_lists_core_profile_files", manifest_ok, {"missing_from_manifest": sorted(wanted - listed)})
    except Exception as e:
        add(checks, "manifest_lists_core_profile_files", False, {"error": str(e)})
        errors.append(f"MANIFEST.json parse/check failed: {e}")

    receipt_rel = f"ORGANS/{ORGAN_ID}/RECEIPTS/{ORGAN_ID.lower()}_profile_receipt.json"
    report_rel = f"ORGANS/{ORGAN_ID}/REPORTS/{ORGAN_ID}_PROFILE_VALIDATION_REPORT_V0_1.md"

    file_hashes = {}
    for f in REQUIRED_FILES:
        p = root / f
        if p.is_file():
            file_hashes[f"ORGANS/{ORGAN_ID}/{f}"] = sha(p)
    if validator_exists:
        file_hashes[f"ORGANS/{ORGAN_ID}/VALIDATORS/{validator_file.name}"] = sha(validator_file)

    verdict = "PASS_PROFILE_BASELINE" if not errors else "FAIL_PROFILE_BASELINE"

    receipt = {
        "receipt_id": f"receipt.{ORGAN_ID.lower()}.profile.v0_1",
        "task_id": TASK_ID,
        "organ_id": ORGAN_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": utc(),
        "profile_baseline": {
            "required_files": REQUIRED_FILES,
            "required_dirs": REQUIRED_DIRS,
            "declared_functions_count": len(declared_functions) if isinstance(declared_functions, list) else 0,
            "declared_validators_count": len(declared_validators) if isinstance(declared_validators, list) else 0,
            "forbidden_actions_count": len(forbidden_actions) if isinstance(forbidden_actions, list) else 0
        },
        "file_hashes_sha256": file_hashes,
        "checks": checks,
        "warnings": warnings,
        "errors": errors
    }

    receipt_path = repo / receipt_rel
    report_path = repo / report_rel
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"

    report = f"""# {ORGAN_ID} PROFILE VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
organ_id: `{ORGAN_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Meaning

This report proves the organ has a baseline passport/profile shape and an executable profile validator.

It does not prove the organ is fully implemented.

## Checks

{checks_md}

## Errors

{errors_md}

## Receipt

`{receipt_rel}`
"""
    report_path.write_text(report, encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "organ_id": ORGAN_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "receipt": receipt_rel,
        "report": report_rel,
        "errors": errors
    }, ensure_ascii=False, indent=2))

    return 0 if verdict == "PASS_PROFILE_BASELINE" else 1

if __name__ == "__main__":
    raise SystemExit(main())
