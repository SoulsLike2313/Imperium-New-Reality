#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OWNER-DOCS-VALIDATION-WARP-0001
Stdlib-only validator for Owner foundation documents.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re, sys
from pathlib import Path
from typing import Any

TASK_ID = "OWNER-DOCS-VALIDATION-WARP-0001"
VALIDATOR_ID = "owner_foundation_docs_validator.v0_1"
OWNER_DOCS_DIR = Path("ORGANS/_CORE_GOVERNANCE/OWNER_DECISIONS")
PATCH_DIR = Path("WARP/PATCHES/OWNER-DOCS-VALIDATION-WARP-0001")
RECEIPT_PATH = PATCH_DIR / "RECEIPTS/owner_docs_validation_receipt.json"
REPORT_PATH = PATCH_DIR / "REPORTS/OWNER_DOCS_VALIDATION_REPORT_V0_1.md"

REQUIRED_OWNER_DOCS = [
    "README.md",
    "OWNER_ANSWER_LOCK_V0_1.md",
    "OWNER_ANSWER_LOCK_V0_1.json",
    "OWNER_DECISION_INDEX_V0_1.json",
    "TERMS_AND_AXIOMS_V0_1.md",
    "IMPERIUM_REFORM_ROADMAP_V0_1.md",
    "IMPLEMENTATION_ZONES_V0_1.json",
    "THRONE_CROWN_ORGAN_DECISION_V0_1.md",
    "OWNER_LAND_POLICY_V0_1.md",
    "VALIDATION_BACKLOG_V0_1.md",
    "STAGE_0_DIRECT_REALITY_ADMISSION_NOTE_V0_1.md",
]
ROOT_REQUIRED_FILES = ["OWNER_DOCS_FILE_MANIFEST_SHA256.json"]
GREAT_NINE = ["ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION","CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS"]
EXPECTED_ZONES = set(range(10))


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path):
    try:
        return path.read_text(encoding="utf-8"), None
    except Exception as e:
        return None, f"TEXT_READ_ERROR: {path}: {e}"


def read_json(path: Path):
    txt, err = read_text(path)
    if err:
        return None, err
    try:
        return json.loads(txt), None
    except Exception as e:
        return None, f"JSON_PARSE_ERROR: {path}: {e}"


def flatten(x: Any) -> list[str]:
    out: list[str] = []
    def walk(v: Any):
        if isinstance(v, str): out.append(v)
        elif isinstance(v, dict):
            for k,val in v.items():
                out.append(str(k)); walk(val)
        elif isinstance(v, list):
            for i in v: walk(i)
        elif v is not None: out.append(str(v))
    walk(x)
    return out


def check(checks: list[dict], name: str, ok: bool, details=None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})


def collect_zones(obj: Any) -> set[int]:
    text = "\n".join(flatten(obj))
    found: set[int] = set()
    for m in re.finditer(r"(?:zone|зона)[^0-9]*([0-9])", text, flags=re.I):
        found.add(int(m.group(1)))
    def walk(v: Any):
        if isinstance(v, dict):
            for k,val in v.items():
                if str(k).lower() in {"zone", "zone_id", "id", "number", "index"}:
                    if isinstance(val, int): found.add(val)
                    elif isinstance(val, str):
                        m = re.search(r"\b([0-9])\b", val)
                        if m: found.add(int(m.group(1)))
                walk(val)
        elif isinstance(v, list):
            for i in v: walk(i)
    walk(obj)
    return found


def validate(repo_root: Path) -> dict:
    checks, errors = [], []
    owner_dir = repo_root / OWNER_DOCS_DIR
    check(checks, "owner_docs_dir_exists", owner_dir.is_dir(), {"path": OWNER_DOCS_DIR.as_posix()})
    if not owner_dir.is_dir(): errors.append(f"Missing owner docs dir: {OWNER_DOCS_DIR}")

    present, missing, hashes = [], [], {}
    for rel in REQUIRED_OWNER_DOCS:
        p = owner_dir / rel
        if p.is_file():
            present.append(rel); hashes[(OWNER_DOCS_DIR / rel).as_posix()] = sha256_file(p)
        else:
            missing.append(rel); errors.append(f"Missing required Owner document: {OWNER_DOCS_DIR / rel}")
    check(checks, "required_owner_documents_present", not missing, {"expected_count": len(REQUIRED_OWNER_DOCS), "present_count": len(present), "missing": missing})

    missing_roots = [rel for rel in ROOT_REQUIRED_FILES if not (repo_root / rel).is_file()]
    for rel in missing_roots: errors.append(f"Missing required root file: {rel}")
    check(checks, "required_root_files_present", not missing_roots, {"missing": missing_roots})

    json_data, text_fail, json_fail = {}, [], []
    for rel in REQUIRED_OWNER_DOCS:
        p = owner_dir / rel
        if not p.is_file(): continue
        if rel.endswith(".json"):
            d,e = read_json(p)
            if e: json_fail.append(e); errors.append(e)
            else: json_data[rel] = d
        else:
            _,e = read_text(p)
            if e: text_fail.append(e); errors.append(e)
    for rel in ROOT_REQUIRED_FILES:
        p = repo_root / rel
        if p.is_file():
            d,e = read_json(p)
            if e: json_fail.append(e); errors.append(e)
            else: json_data[rel] = d
    check(checks, "markdown_and_text_are_utf8", not text_fail, {"failures": text_fail})
    check(checks, "json_files_parse_as_utf8_json", not json_fail, {"failures": json_fail})

    lock_text = "\n".join(flatten(json_data.get("OWNER_ANSWER_LOCK_V0_1.json", {}))).upper()
    decision_results = {
        "throne_crown_organ": "CROWN_ORGAN" in lock_text,
        "throne_measure_only": "MEASURE_ONLY" in lock_text,
        "override_owner_only": "OWNER_ONLY" in lock_text or ("OWNER" in lock_text and "OVERRIDE" in lock_text),
        "visual_refit_frozen": "FROZEN" in lock_text and ("VISUAL" in lock_text or "REFIT" in lock_text),
        "great_nine_present": all(o in lock_text for o in GREAT_NINE),
    }
    for k,v in decision_results.items():
        if not v: errors.append(f"Required decision not found or unclear: {k}")
    check(checks, "required_owner_decisions_present", all(decision_results.values()), {**decision_results, "great_nine": GREAT_NINE})

    zones_found = collect_zones(json_data.get("IMPLEMENTATION_ZONES_V0_1.json", {}))
    missing_zones = sorted(EXPECTED_ZONES - zones_found)
    if missing_zones: errors.append(f"Missing implementation zones: {missing_zones}")
    check(checks, "implementation_zones_0_to_9_present", not missing_zones, {"found": sorted(zones_found), "missing": missing_zones})

    backlog = owner_dir / "VALIDATION_BACKLOG_V0_1.md"
    backlog_text, _ = read_text(backlog) if backlog.is_file() else ("", "missing")
    backlog_ok = bool(backlog_text and len(backlog_text.strip()) > 100)
    if not backlog_ok: errors.append("VALIDATION_BACKLOG_V0_1.md is missing or too small")
    check(checks, "validation_backlog_non_empty", backlog_ok, {"chars": len(backlog_text or "")})

    readme = owner_dir / "README.md"
    readme_text, _ = read_text(readme) if readme.is_file() else ("", "missing")
    refs = ["OWNER_ANSWER_LOCK_V0_1", "IMPERIUM_REFORM_ROADMAP_V0_1", "THRONE_CROWN_ORGAN_DECISION_V0_1", "OWNER_LAND_POLICY_V0_1", "VALIDATION_BACKLOG_V0_1"]
    missing_refs = [r for r in refs if r not in (readme_text or "")]
    if missing_refs: errors.append(f"README missing core refs: {missing_refs}")
    check(checks, "owner_decisions_readme_references_core_docs", not missing_refs, {"missing_refs": missing_refs})

    fake_green = bool(hashes) and len(present) == len(REQUIRED_OWNER_DOCS)
    if not fake_green: errors.append("Fake-green guard failed: no actual hashes or missing docs")
    check(checks, "fake_green_guard_actual_file_hashes_collected", fake_green, {"hash_count": len(hashes)})

    verdict = "PASS" if not errors else "FAIL"
    return {
        "receipt_id": "receipt.owner_docs_validation.v0_1",
        "task_id": TASK_ID,
        "verdict": verdict,
        "generated_at_utc": now(),
        "validator": {
            "validator_id": VALIDATOR_ID,
            "version": "0.1.0",
            "sovereign_owner": "THRONE",
            "validated_domain": OWNER_DOCS_DIR.as_posix(),
            "implementation_custodian": "MECHANICUS",
            "trust_auditor": "CUSTODES",
            "adversarial_checker": "INQUISITION",
            "receipt_registry": "ADMINISTRATUM",
            "canon_reference": "DOCTRINARIUM",
            "current_host": (PATCH_DIR / "VALIDATORS").as_posix(),
            "future_home": "ORGANS/THRONE/VALIDATORS",
        },
        "mode": "WARP_VALIDATION",
        "required_documents": {"expected_count": len(REQUIRED_OWNER_DOCS), "present_count": len(present), "missing": missing, "documents": REQUIRED_OWNER_DOCS},
        "required_root_files": {"expected": ROOT_REQUIRED_FILES, "missing": missing_roots},
        "required_decisions": {**decision_results, "great_nine": GREAT_NINE},
        "implementation_zones": {"expected": sorted(EXPECTED_ZONES), "found": sorted(zones_found), "missing": missing_zones},
        "document_hashes_sha256": hashes,
        "checks": checks,
        "errors": errors,
        "fake_green_guard": "PASS" if fake_green and not errors else "FAIL",
    }


def write_outputs(repo_root: Path, receipt: dict):
    rp, mp = repo_root / RECEIPT_PATH, repo_root / REPORT_PATH
    rp.parent.mkdir(parents=True, exist_ok=True)
    mp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in receipt.get("checks", []))
    errors = receipt.get("errors") or []
    err_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    report = f"""# OWNER DOCS VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Organ responsibility

- Sovereign owner: `THRONE`
- Implementation custodian: `MECHANICUS`
- Trust auditor: `CUSTODES`
- Adversarial checker: `INQUISITION`
- Receipt registry: `ADMINISTRATUM`
- Canon reference: `DOCTRINARIUM`

## Required documents

Expected: `{receipt['required_documents']['expected_count']}`  
Present: `{receipt['required_documents']['present_count']}`  
Missing: `{len(receipt['required_documents']['missing'])}`

## Checks

{checks_md}

## Errors

{err_md}

## Receipt

`{RECEIPT_PATH.as_posix()}`

## Meaning

This report proves whether the direct-Reality Owner foundation documents are structurally present and minimally machine-checkable.

It does not yet prove that the full Imperium is valid.
"""
    mp.write_text(report, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()
    receipt = validate(repo_root)
    write_outputs(repo_root, receipt)
    print(json.dumps({"task_id": TASK_ID, "validator": VALIDATOR_ID, "verdict": receipt["verdict"], "receipt": RECEIPT_PATH.as_posix(), "report": REPORT_PATH.as_posix(), "errors": receipt.get("errors", [])}, ensure_ascii=False, indent=2))
    return 0 if receipt["verdict"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
