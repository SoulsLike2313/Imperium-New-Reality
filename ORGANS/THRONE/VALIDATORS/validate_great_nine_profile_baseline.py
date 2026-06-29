#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, datetime as dt, hashlib, json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "GREAT-NINE-PROFILE-VALIDATORS-0001"
VALIDATOR_ID = "throne_great_nine_profile_baseline_validator.v0_1"

GREAT_NINE = [
    "ASTRONOMICON", "ADMINISTRATUM", "DOCTRINARIUM", "MECHANICUS", "INQUISITION",
    "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "OFFICIO_AGENTIS"
]

REQUIRED_FILES = ["README.md", "ORGAN_CARD.json", "MANIFEST.json", "FUNCTIONS.md"]
REQUIRED_DIRS = ["MATRICES", "SCHEMAS", "VALIDATORS", "RECEIPTS", "REPORTS", "TESTS", "TUI", "DASHBOARDS", "EYES", "BLOCK", "LESSONS", "NEGATIVE_LESSONS"]

RECEIPT_REL = "ORGANS/THRONE/RECEIPTS/great_nine_profile_baseline_receipt.json"
REPORT_REL = "ORGANS/THRONE/REPORTS/GREAT_NINE_PROFILE_BASELINE_REPORT_V0_1.md"

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024*1024), b""):
            h.update(c)
    return h.hexdigest()

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def pct(done: int, total: int) -> float:
    return round(max(0.0, min(100.0, done * 100.0 / max(1, total))), 2)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    repo = Path(ap.parse_args().repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    organs: Dict[str, Any] = {}

    matrix = repo / "ORGANS/THRONE/MATRICES/THRONE_GREAT_NINE_PROFILE_STRICTNESS_MATRIX_V0_1.json"
    matrix_ok = matrix.is_file()
    add(checks, "strictness_matrix_exists", matrix_ok, {"path": "ORGANS/THRONE/MATRICES/THRONE_GREAT_NINE_PROFILE_STRICTNESS_MATRIX_V0_1.json"})
    if not matrix_ok:
        errors.append("Strictness matrix missing")

    for organ in GREAT_NINE:
        root = repo / "ORGANS" / organ
        missing_files = [f for f in REQUIRED_FILES if not (root / f).is_file()]
        missing_dirs = [d for d in REQUIRED_DIRS if not (root / d).is_dir()]
        validator = root / "VALIDATORS" / f"validate_{organ.lower()}_profile.py"
        receipt = root / "RECEIPTS" / f"{organ.lower()}_profile_receipt.json"
        report = root / "REPORTS" / f"{organ}_PROFILE_VALIDATION_REPORT_V0_1.md"
        card = root / "ORGAN_CARD.json"
        manifest = root / "MANIFEST.json"

        card_ok = False
        receipt_ok = False
        validator_declared = False
        forbidden_actions_count = 0
        declared_functions_count = 0

        try:
            c = read_json(card) if card.is_file() else {}
            card_ok = c.get("organ_id") == organ and c.get("great_nine_member") is True
            validator_declared = bool(c.get("declared_validators"))
            forbidden_actions_count = len(c.get("forbidden_actions", [])) if isinstance(c.get("forbidden_actions"), list) else 0
            declared_functions_count = len(c.get("declared_functions", [])) if isinstance(c.get("declared_functions"), list) else 0
        except Exception:
            card_ok = False

        try:
            r = read_json(receipt) if receipt.is_file() else {}
            receipt_ok = r.get("verdict") == "PASS_PROFILE_BASELINE"
        except Exception:
            receipt_ok = False

        checks_total = 9
        checks_passed = sum([
            root.is_dir(),
            not missing_files,
            not missing_dirs,
            card_ok,
            manifest.is_file(),
            validator.is_file(),
            receipt_ok,
            report.is_file(),
            validator_declared and forbidden_actions_count >= 4 and declared_functions_count >= 5
        ])
        score = pct(checks_passed, checks_total)

        organ_errors = []
        if not root.is_dir(): organ_errors.append("organ directory missing")
        if missing_files: organ_errors.append("missing files: " + ", ".join(missing_files))
        if missing_dirs: organ_errors.append("missing dirs: " + ", ".join(missing_dirs))
        if not card_ok: organ_errors.append("ORGAN_CARD invalid")
        if not validator.is_file(): organ_errors.append("profile validator missing")
        if not receipt_ok: organ_errors.append("profile receipt missing/not PASS")
        if not report.is_file(): organ_errors.append("profile report missing")
        if forbidden_actions_count < 4: organ_errors.append("not enough forbidden actions")
        if declared_functions_count < 5: organ_errors.append("not enough declared functions")

        organs[organ] = {
            "score": score,
            "checks_passed": checks_passed,
            "checks_total": checks_total,
            "missing_files": missing_files,
            "missing_dirs": missing_dirs,
            "card_ok": card_ok,
            "validator_exists": validator.is_file(),
            "receipt_pass": receipt_ok,
            "report_exists": report.is_file(),
            "declared_functions_count": declared_functions_count,
            "forbidden_actions_count": forbidden_actions_count,
            "errors": organ_errors
        }

    all_pass = all(not o["errors"] for o in organs.values())
    add(checks, "all_great_nine_profile_baselines_pass", all_pass, {
        "failed_organs": [k for k,v in organs.items() if v["errors"]]
    })
    if not all_pass:
        errors.extend(f"{k}: {v['errors']}" for k, v in organs.items() if v["errors"])

    score = round(sum(v["score"] for v in organs.values()) / len(organs), 2)
    verdict = "PASS_GREAT_NINE_PROFILE_BASELINE" if not errors else "FAIL_GREAT_NINE_PROFILE_BASELINE"

    receipt = {
        "receipt_id": "receipt.throne.great_nine_profile_baseline.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": utc(),
        "great_nine_profile_score": score,
        "organs": organs,
        "checks": checks,
        "errors": errors,
        "meaning": "This proves baseline profile credibility for the Great Nine. It does not prove full organ implementation."
    }

    rpath = repo / RECEIPT_REL
    repath = repo / REPORT_REL
    rpath.parent.mkdir(parents=True, exist_ok=True)
    repath.parent.mkdir(parents=True, exist_ok=True)
    rpath.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [f"- `{k}`: `{v['score']}` — errors: {', '.join(v['errors']) if v['errors'] else 'none'}" for k,v in sorted(organs.items())]
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"

    report = f"""# GREAT NINE PROFILE BASELINE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
great_nine_profile_score: `{score}`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Meaning

This is a baseline profile audit.

It confirms whether every Great Nine organ has a passport, machine card, manifest, functions file, profile validator, profile receipt, and forbidden-action boundary.

It does not claim full organ implementation.

## Organs

{chr(10).join(lines)}

## Checks

{checks_md}

## Errors

{errors_md}

## Receipt

`{RECEIPT_REL}`
"""
    repath.write_text(report, encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "great_nine_profile_score": score,
        "receipt": RECEIPT_REL,
        "report": REPORT_REL,
        "errors": errors
    }, ensure_ascii=False, indent=2))

    return 0 if verdict == "PASS_GREAT_NINE_PROFILE_BASELINE" else 1

if __name__ == "__main__":
    raise SystemExit(main())
