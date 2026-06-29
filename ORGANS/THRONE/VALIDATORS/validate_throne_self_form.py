#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THRONE-CROWN-ORGAN-FOUNDATION-0001

Self-form validator for ORGANS/THRONE.
Stdlib-only. Generates receipt and report.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "THRONE-CROWN-ORGAN-FOUNDATION-0001"
VALIDATOR_ID = "throne_self_form_validator.v0_1"
THRONE_DIR = Path("ORGANS/THRONE")
RECEIPT_PATH = THRONE_DIR / "RECEIPTS/throne_self_form_receipt.json"
REPORT_PATH = THRONE_DIR / "REPORTS/THRONE_SELF_FORM_REPORT_V0_1.md"

GREAT_NINE = [
    "ASTRONOMICON", "ADMINISTRATUM", "DOCTRINARIUM", "MECHANICUS", "INQUISITION",
    "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "OFFICIO_AGENTIS"
]

REQUIRED_SLOTS = [
    "README.md", "ORGAN_CARD.json", "MANIFEST.json", "FUNCTIONS.md",
    "SELF_KNOWLEDGE", "MATRICES", "SCHEMAS", "VALIDATORS", "RECEIPTS",
    "REPORTS", "TESTS", "TUI", "DASHBOARDS", "EYES", "BLOCK", "LESSONS", "NEGATIVE_LESSONS"
]

REQUIRED_FILES = [
    "README.md", "ORGAN_CARD.json", "MANIFEST.json", "FUNCTIONS.md",
    "SELF_KNOWLEDGE/IDENTITY.md", "SELF_KNOWLEDGE/CALLING.md", "SELF_KNOWLEDGE/OBLIGATIONS.md", "SELF_KNOWLEDGE/BOUNDARIES.md",
    "MATRICES/THRONE_TARGET_V1_MATRIX_V0_1.json",
    "MATRICES/THRONE_ORGAN_RELATIONSHIP_MATRIX_V0_1.json",
    "MATRICES/THRONE_VALIDATION_MODE_MATRIX_V0_1.json",
    "SCHEMAS/throne_organ_card.schema.json",
    "SCHEMAS/throne_target_v1_matrix.schema.json",
    "SCHEMAS/throne_self_form_receipt.schema.json",
    "VALIDATORS/validate_throne_self_form.py",
    "TESTS/README.md",
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def add_check(checks: List[Dict[str, Any]], name: str, passed: bool, details: Dict[str, Any] | None = None) -> None:
    checks.append({"name": name, "status": "PASS" if passed else "FAIL", "details": details or {}})


def validate(repo_root: Path) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    throne_dir = repo_root / THRONE_DIR

    add_check(checks, "throne_dir_exists", throne_dir.is_dir(), {"path": str(THRONE_DIR)})
    if not throne_dir.is_dir():
        errors.append(f"Missing Throne dir: {THRONE_DIR}")

    missing_slots = []
    for slot in REQUIRED_SLOTS:
        if not (throne_dir / slot).exists():
            missing_slots.append(slot)
    add_check(checks, "required_slots_exist", not missing_slots, {"missing": missing_slots, "expected": REQUIRED_SLOTS})
    if missing_slots:
        errors.append(f"Missing required slots: {missing_slots}")

    missing_files = []
    file_hashes: Dict[str, str] = {}
    for rel in REQUIRED_FILES:
        p = throne_dir / rel
        if not p.is_file():
            missing_files.append(rel)
        else:
            file_hashes[(THRONE_DIR / rel).as_posix()] = sha256_file(p)
    add_check(checks, "required_files_exist", not missing_files, {"missing": missing_files})
    if missing_files:
        errors.append(f"Missing required files: {missing_files}")

    card = {}
    manifest = {}
    target = {}
    relationship = {}
    mode_matrix = {}
    json_errors = []
    for name, rel in {
        "organ_card": "ORGAN_CARD.json",
        "manifest": "MANIFEST.json",
        "target_v1": "MATRICES/THRONE_TARGET_V1_MATRIX_V0_1.json",
        "relationship": "MATRICES/THRONE_ORGAN_RELATIONSHIP_MATRIX_V0_1.json",
        "mode_matrix": "MATRICES/THRONE_VALIDATION_MODE_MATRIX_V0_1.json",
        "schema_card": "SCHEMAS/throne_organ_card.schema.json",
        "schema_target": "SCHEMAS/throne_target_v1_matrix.schema.json",
        "schema_receipt": "SCHEMAS/throne_self_form_receipt.schema.json",
    }.items():
        p = throne_dir / rel
        if p.is_file():
            try:
                data = read_json(p)
                if name == "organ_card": card = data
                elif name == "manifest": manifest = data
                elif name == "target_v1": target = data
                elif name == "relationship": relationship = data
                elif name == "mode_matrix": mode_matrix = data
            except Exception as exc:
                json_errors.append(f"{rel}: {exc}")
    add_check(checks, "json_files_parse", not json_errors, {"errors": json_errors})
    if json_errors:
        errors.extend(json_errors)

    card_checks = {
        "organ_id_THRONE": card.get("organ_id") == "THRONE",
        "organ_type_CROWN_ORGAN": card.get("organ_type") == "CROWN_ORGAN",
        "mode_MEASURE_ONLY": card.get("mode") == "MEASURE_ONLY",
        "validation_model_TARGET_V1_VS_CURRENT_REALITY": card.get("validation_model") == "TARGET_V1_VS_CURRENT_REALITY",
        "override_OWNER_ONLY": card.get("override_policy") == "OWNER_ONLY",
        "great_nine_exact": card.get("great_nine") == GREAT_NINE,
        "visual_refit_FROZEN": (card.get("visual_policy") or {}).get("visual_refit") == "FROZEN",
    }
    add_check(checks, "organ_card_required_decisions", all(card_checks.values()), card_checks)
    for k, v in card_checks.items():
        if not v:
            errors.append(f"ORGAN_CARD decision failed: {k}")

    manifest_required = set(manifest.get("required_files", [])) if isinstance(manifest, dict) else set()
    missing_in_manifest = [f for f in REQUIRED_FILES if f not in manifest_required]
    add_check(checks, "manifest_lists_required_files", not missing_in_manifest, {"missing_in_manifest": missing_in_manifest})
    if missing_in_manifest:
        errors.append(f"Manifest does not list required files: {missing_in_manifest}")

    target_checks = {
        "target_mode_TARGET_FORM": target.get("mode") == "TARGET_FORM",
        "target_score_100": target.get("target_score") == 100,
        "target_validation_model": target.get("validation_model") == "TARGET_V1_VS_CURRENT_REALITY",
        "target_has_throne": isinstance(target.get("throne"), dict),
        "target_has_great_nine": all(organ in (target.get("great_nine") or {}) for organ in GREAT_NINE),
    }
    add_check(checks, "target_v1_matrix_foundation", all(target_checks.values()), target_checks)
    for k, v in target_checks.items():
        if not v:
            errors.append(f"Target matrix check failed: {k}")

    relationship_has_all = all(organ in (relationship.get("relationships") or {}) for organ in GREAT_NINE)
    add_check(checks, "organ_relationship_matrix_has_great_nine", relationship_has_all, {"great_nine": GREAT_NINE})
    if not relationship_has_all:
        errors.append("Relationship matrix does not include all Great Nine")

    mode_current = mode_matrix.get("current_mode") == "MEASURE_ONLY"
    mode_owner = mode_matrix.get("owner_override") == "OWNER_ONLY"
    add_check(checks, "validation_mode_matrix_foundation", mode_current and mode_owner, {"current_mode": mode_matrix.get("current_mode"), "owner_override": mode_matrix.get("owner_override")})
    if not (mode_current and mode_owner):
        errors.append("Validation mode matrix does not declare MEASURE_ONLY / OWNER_ONLY")

    fake_green_guard = bool(file_hashes) and len(file_hashes) >= len(REQUIRED_FILES) - len(missing_files)
    add_check(checks, "fake_green_guard_actual_hashes_collected", fake_green_guard, {"hash_count": len(file_hashes)})
    if not fake_green_guard:
        errors.append("Fake-green guard failed: no file hashes collected")

    verdict = "PASS" if not errors else "FAIL"
    return {
        "receipt_id": "receipt.throne_self_form.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": utc_now(),
        "mode": "WARP_VALIDATION",
        "organ_id": "THRONE",
        "organ_type": "CROWN_ORGAN",
        "validation_model": "TARGET_V1_VS_CURRENT_REALITY",
        "throne_mode": card.get("mode"),
        "great_nine": GREAT_NINE,
        "checks": checks,
        "errors": errors,
        "file_hashes_sha256": file_hashes,
        "meaning": "PASS means the first Throne foundation is alive and measurable, not complete v1 readiness."
    }


def write_outputs(repo_root: Path, receipt: Dict[str, Any]) -> None:
    receipt_path = repo_root / RECEIPT_PATH
    report_path = repo_root / REPORT_PATH
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in receipt["checks"])
    errors_md = "\n".join(f"- {e}" for e in receipt["errors"]) if receipt["errors"] else "- none"
    report = f"""# THRONE SELF FORM REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Identity

- organ_id: `THRONE`
- organ_type: `CROWN_ORGAN`
- mode: `{receipt.get('throne_mode')}`
- validation_model: `TARGET_V1_VS_CURRENT_REALITY`

## Checks

{checks_md}

## Errors

{errors_md}

## Receipt

`{RECEIPT_PATH.as_posix()}`

## Meaning

The Throne foundation exists and can validate its own first form.

This is the first heartbeat of the Throne, not full v1 readiness.
"""
    report_path.write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    receipt = validate(repo_root)
    write_outputs(repo_root, receipt)
    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": receipt["verdict"],
        "receipt": RECEIPT_PATH.as_posix(),
        "report": REPORT_PATH.as_posix(),
        "errors": receipt["errors"],
    }, ensure_ascii=False, indent=2))
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
