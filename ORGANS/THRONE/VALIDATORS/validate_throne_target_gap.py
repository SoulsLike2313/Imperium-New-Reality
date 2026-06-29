#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
THRONE-TARGET-GAP-VALIDATOR-0001.

First Throne-wide target gap validator.

Reads:
- Throne target v1 matrix
- population census outputs

Writes:
- throne_target_gap_receipt.json
- THRONE_TARGET_GAP_REPORT_V0_1.md
- THRONE_ORGAN_READINESS_TABLE_V0_1.csv
- THRONE_NEXT_ATTENTION_AREAS_V0_1.json

Verdict PASS_MEASURED means the gap was measured, not that the Imperium is healthy.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


TASK_ID = "THRONE-TARGET-GAP-VALIDATOR-0001"
VALIDATOR_ID = "throne_target_gap_validator.v0_1"

THRONE = Path("ORGANS/THRONE")
TARGET_MATRIX = THRONE / "MATRICES/THRONE_TARGET_V1_MATRIX_V0_1.json"
SCORING_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_SCORING_MATRIX_V0_1.json"

CENSUS_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_CENSUS_V0_1.json")
SUMMARY_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_SUMMARY_V0_1.json")
GAP_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_GAP_MAP_V0_1.json")

RECEIPT = THRONE / "RECEIPTS/throne_target_gap_receipt.json"
REPORT = THRONE / "REPORTS/THRONE_TARGET_GAP_REPORT_V0_1.md"
READINESS_CSV = THRONE / "REPORTS/THRONE_ORGAN_READINESS_TABLE_V0_1.csv"
NEXT_ATTENTION = THRONE / "REPORTS/THRONE_NEXT_ATTENTION_AREAS_V0_1.json"

DEFAULT_REQUIRED_SLOTS = [
    "README.md", "ORGAN_CARD.json", "MANIFEST.json", "FUNCTIONS.md",
    "MATRICES", "SCHEMAS", "VALIDATORS", "RECEIPTS", "REPORTS", "TESTS",
    "TUI", "DASHBOARDS", "EYES", "BLOCK", "LESSONS", "NEGATIVE_LESSONS"
]

GREAT_NINE = [
    "ASTRONOMICON", "ADMINISTRATUM", "DOCTRINARIUM", "MECHANICUS", "INQUISITION",
    "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "OFFICIO_AGENTIS"
]
SUBJECTS = ["THRONE"] + GREAT_NINE

DEFAULT_WEIGHTS = {
    "physical_presence_score": 10,
    "required_slot_score": 15,
    "identity_score": 10,
    "manifest_score": 10,
    "schema_coverage_score": 10,
    "validator_coverage_score": 15,
    "receipt_coverage_score": 10,
    "boundary_lifecycle_score": 10,
    "observability_score": 5,
    "trust_action_readiness_score": 5,
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add_check(checks: List[Dict[str, Any]], name: str, passed: bool, details: Dict[str, Any] | None = None) -> None:
    checks.append({"name": name, "status": "PASS" if passed else "FAIL", "details": details or {}})


def clamp(x: float) -> float:
    return round(max(0.0, min(100.0, x)), 2)


def score_bool(value: bool) -> float:
    return 100.0 if value else 0.0


def weighted(scores: Dict[str, float], weights: Dict[str, int]) -> float:
    total_weight = sum(weights.values()) or 1
    return clamp(sum(scores.get(k, 0.0) * w for k, w in weights.items()) / total_weight)


def organ_path(organ: str) -> Path:
    return THRONE if organ == "THRONE" else Path("ORGANS") / organ


def classify_residents_by_owner(residents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    by_owner = defaultdict(list)
    for r in residents:
        owner = str(r.get("owner_candidate") or "UNKNOWN")
        by_owner[owner].append(r)
        if organ_path("THRONE").as_posix() in str(r.get("path", "")) and owner != "THRONE":
            by_owner["THRONE"].append(r)
    return by_owner


def count_classes(items: List[Dict[str, Any]]) -> Counter:
    return Counter(str(r.get("class") or "UNKNOWN") for r in items)


def organ_slot_score(root: Path, required_slots: List[str], repo_root: Path) -> Tuple[float, List[str], List[str]]:
    present = []
    missing = []
    for slot in required_slots:
        p = repo_root / root / slot
        if p.exists():
            present.append(slot)
        else:
            missing.append(slot)
    return clamp(len(present) * 100.0 / max(1, len(required_slots))), present, missing


def parse_json_if_exists(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        read_json(path)
        return True
    except Exception:
        return False


def coverage_score(count: int, target: int) -> float:
    return clamp(count * 100.0 / max(1, target))


def compute_organ(repo_root: Path, organ: str, by_owner: Dict[str, List[Dict[str, Any]]], required_slots: List[str], weights: Dict[str, int]) -> Dict[str, Any]:
    root = organ_path(organ)
    abs_root = repo_root / root
    exists = abs_root.is_dir()

    slot_score, present_slots, missing_slots = organ_slot_score(root, required_slots, repo_root) if exists else (0.0, [], required_slots)

    card = abs_root / "ORGAN_CARD.json"
    manifest = abs_root / "MANIFEST.json"
    functions = abs_root / "FUNCTIONS.md"

    identity_ok = parse_json_if_exists(card)
    manifest_ok = parse_json_if_exists(manifest)
    functions_ok = functions.is_file()

    items = by_owner.get(organ, [])
    class_counts = count_classes(items)

    schema_count = class_counts.get("SCHEMA", 0)
    validator_count = class_counts.get("VALIDATOR", 0)
    receipt_count = class_counts.get("RECEIPT", 0)
    report_count = class_counts.get("REPORT", 0)
    matrix_count = class_counts.get("MATRIX", 0)

    has_warp = any(str(r.get("status")) == "WARP" for r in items)
    has_negative = any(str(r.get("status")) == "NEGATIVE_EXAMPLE" for r in items)
    has_quarantine = any(str(r.get("status")) == "QUARANTINE" for r in items)

    observability_parts = [
        (abs_root / "TUI").exists(),
        (abs_root / "DASHBOARDS").exists(),
        (abs_root / "EYES").exists(),
        (abs_root / "REPORTS").exists(),
    ]

    trust_action_hints = [
        validator_count > 0,
        receipt_count > 0,
        matrix_count > 0,
        functions_ok,
    ]

    scores = {
        "physical_presence_score": score_bool(exists),
        "required_slot_score": slot_score,
        "identity_score": score_bool(identity_ok),
        "manifest_score": score_bool(manifest_ok),
        "schema_coverage_score": coverage_score(schema_count, 3),
        "validator_coverage_score": coverage_score(validator_count, 2),
        "receipt_coverage_score": coverage_score(receipt_count, 3),
        "boundary_lifecycle_score": 100.0 if exists and not has_warp else 70.0 if exists else 0.0,
        "observability_score": clamp(sum(1 for x in observability_parts if x) * 100.0 / len(observability_parts)),
        "trust_action_readiness_score": clamp(sum(1 for x in trust_action_hints if x) * 100.0 / len(trust_action_hints)),
    }
    scores["organ_readiness_score"] = weighted(scores, weights)

    major_gaps = []
    if not exists:
        major_gaps.append("organ directory missing")
    for f in ["README.md", "ORGAN_CARD.json", "MANIFEST.json", "FUNCTIONS.md"]:
        if f in missing_slots:
            major_gaps.append(f"missing {f}")
    if schema_count == 0:
        major_gaps.append("no schema evidence")
    if validator_count == 0:
        major_gaps.append("no validator evidence")
    if receipt_count == 0:
        major_gaps.append("no receipt evidence")
    if has_warp:
        major_gaps.append("has WARP-status residents")
    if has_quarantine:
        major_gaps.append("has quarantine residents")
    if has_negative:
        major_gaps.append("has negative-example residents")

    return {
        "organ_id": organ,
        "path": root.as_posix(),
        "exists": exists,
        "scores": scores,
        "present_slots": present_slots,
        "missing_slots": missing_slots,
        "evidence_counts": {
            "residents": len(items),
            "schemas": schema_count,
            "validators": validator_count,
            "receipts": receipt_count,
            "reports": report_count,
            "matrices": matrix_count,
        },
        "major_gaps": major_gaps[:30],
    }


def recommend(organs: Dict[str, Any], census_summary: Dict[str, Any], census_gaps: Dict[str, Any]) -> List[Dict[str, Any]]:
    recs = []

    def push(priority: int, area: str, reason: str, patch_family: str):
        recs.append({
            "priority": priority,
            "area": area,
            "reason": reason,
            "recommended_patch_family": patch_family,
        })

    missing_readme = [o for o, d in organs.items() if "README.md" in d.get("missing_slots", []) and o != "THRONE"]
    missing_manifest = [o for o, d in organs.items() if "MANIFEST.json" in d.get("missing_slots", []) and o != "THRONE"]
    zero_validator = [o for o, d in organs.items() if d["evidence_counts"]["validators"] == 0]
    low_scores = sorted((d["scores"]["organ_readiness_score"], o) for o, d in organs.items())

    if missing_readme:
        push(10, "Great Nine README passports", f"Missing README: {', '.join(missing_readme[:9])}", "ORGAN-README-PASSPORT-STAMP-0001")
    if missing_manifest:
        push(20, "Great Nine manifests", f"Missing MANIFEST: {', '.join(missing_manifest[:9])}", "ORGAN-MANIFEST-STAMP-0001")
    if "ASTRONOMICON" in zero_validator or organs.get("ASTRONOMICON", {}).get("scores", {}).get("organ_readiness_score", 100) < 50:
        push(30, "Astronomicon relationship validation", "Astronomicon is entry gate; intake/fix-loop/pass criteria must be made measurable.", "THRONE-ASTRONOMICON-RELATIONSHIP-VALIDATION-0001")
    if organs.get("CUSTODES", {}).get("scores", {}).get("organ_readiness_score", 100) < 50:
        push(40, "Custodes trust layer", "Custodes readiness is low; organ validator trust cannot be audited deeply yet.", "CUSTODES-TRUST-LAYER-0001")
    if census_summary.get("validator_count", 0) < census_summary.get("schema_count", 0):
        push(50, "Schema-validator coverage", "Schema count exceeds validator count; declaration/evidence gap is visible.", "SCHEMA-VALIDATOR-COVERAGE-0001")
    if low_scores:
        score, organ = low_scores[0]
        push(60, f"Lowest organ readiness: {organ}", f"{organ} readiness is {score}%.", f"{organ}-GAP-CLOSURE-0001")

    return sorted(recs, key=lambda r: r["priority"])


def write_outputs(repo_root: Path, receipt: Dict[str, Any], organs: Dict[str, Any], next_attention: List[Dict[str, Any]]) -> None:
    for p in [repo_root / RECEIPT.parent, repo_root / REPORT.parent]:
        p.mkdir(parents=True, exist_ok=True)

    (repo_root / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo_root / NEXT_ATTENTION).write_text(json.dumps(next_attention, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (repo_root / READINESS_CSV).open("w", encoding="utf-8", newline="") as f:
        fields = [
            "organ_id", "exists", "organ_readiness_score", "physical_presence_score",
            "required_slot_score", "identity_score", "manifest_score",
            "schema_coverage_score", "validator_coverage_score", "receipt_coverage_score",
            "boundary_lifecycle_score", "observability_score", "trust_action_readiness_score",
            "schemas", "validators", "receipts", "reports", "missing_slots", "major_gaps"
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for organ, data in organs.items():
            row = {
                "organ_id": organ,
                "exists": data["exists"],
                "schemas": data["evidence_counts"]["schemas"],
                "validators": data["evidence_counts"]["validators"],
                "receipts": data["evidence_counts"]["receipts"],
                "reports": data["evidence_counts"]["reports"],
                "missing_slots": "; ".join(data["missing_slots"]),
                "major_gaps": "; ".join(data["major_gaps"]),
            }
            row.update(data["scores"])
            writer.writerow(row)

    score_lines = []
    for organ, data in sorted(organs.items(), key=lambda kv: kv[1]["scores"]["organ_readiness_score"]):
        score_lines.append(f"- `{organ}`: `{data['scores']['organ_readiness_score']}` — gaps: {', '.join(data['major_gaps'][:6]) or 'none'}")

    rec_lines = []
    for r in next_attention:
        rec_lines.append(f"{r['priority']}. **{r['area']}** — {r['reason']} → `{r['recommended_patch_family']}`")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in receipt["checks"])
    errors_md = "\n".join(f"- {e}" for e in receipt["errors"]) if receipt["errors"] else "- none"
    warnings_md = "\n".join(f"- {w}" for w in receipt.get("warnings", [])) if receipt.get("warnings") else "- none"

    report = f"""# THRONE TARGET GAP REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
mode: `MEASURE_ONLY`  
validation_model: `TARGET_V1_VS_CURRENT_REALITY`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Global scores

- core_readiness_score: `{receipt['scores']['core_readiness_score']}`
- throne_readiness_score: `{receipt['scores']['throne_readiness_score']}`
- great_nine_readiness_score: `{receipt['scores']['great_nine_readiness_score']}`
- lowest_organ_readiness_score: `{receipt['scores']['lowest_organ_readiness_score']}`

## Organ readiness, lowest first

{chr(10).join(score_lines)}

## Next attention areas

{chr(10).join(rec_lines) if rec_lines else '- none'}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{RECEIPT.as_posix()}`
- `{READINESS_CSV.as_posix()}`
- `{NEXT_ATTENTION.as_posix()}`

## Meaning

This report does not claim Imperium v1 is achieved.

It proves the Throne can compare a target v1 form against current Reality and produce a measured gap map.
"""
    (repo_root / REPORT).write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    required = [TARGET_MATRIX, SCORING_MATRIX, CENSUS_JSON]
    missing = [p.as_posix() for p in required if not (repo_root / p).is_file()]
    add_check(checks, "required_inputs_exist", not missing, {"missing": missing})
    if missing:
        errors.extend(f"Missing input: {p}" for p in missing)

    target = {}
    scoring = {}
    census = {}
    census_summary = {}
    census_gaps = {}
    try:
        if not missing:
            target = read_json(repo_root / TARGET_MATRIX)
            scoring = read_json(repo_root / SCORING_MATRIX)
            census = read_json(repo_root / CENSUS_JSON)
            if (repo_root / SUMMARY_JSON).is_file():
                census_summary = read_json(repo_root / SUMMARY_JSON)
            else:
                census_summary = census.get("summary", {})
            if (repo_root / GAP_JSON).is_file():
                census_gaps = read_json(repo_root / GAP_JSON)
            else:
                census_gaps = census.get("gaps", {})
            add_check(checks, "input_json_parse", True)
    except Exception as exc:
        add_check(checks, "input_json_parse", False, {"error": str(exc)})
        errors.append(f"Input JSON parse failed: {exc}")

    residents = census.get("residents", []) if isinstance(census, dict) else []
    add_check(checks, "census_has_residents", isinstance(residents, list) and len(residents) > 0, {"resident_count": len(residents) if isinstance(residents, list) else None})
    if not isinstance(residents, list) or not residents:
        errors.append("Census residents missing or empty")

    weights = scoring.get("weights", DEFAULT_WEIGHTS) if isinstance(scoring, dict) else DEFAULT_WEIGHTS
    required_slots = scoring.get("required_slots", DEFAULT_REQUIRED_SLOTS) if isinstance(scoring, dict) else DEFAULT_REQUIRED_SLOTS

    add_check(checks, "scoring_matrix_has_weights", all(k in weights for k in DEFAULT_WEIGHTS), {"weights": weights})
    if not all(k in weights for k in DEFAULT_WEIGHTS):
        errors.append("Scoring matrix missing required weights")

    add_check(checks, "target_matrix_exists_and_mentions_target", bool(target), {"target_keys": list(target.keys())[:20] if isinstance(target, dict) else []})
    if not target:
        errors.append("Target matrix empty")

    by_owner = classify_residents_by_owner(residents) if isinstance(residents, list) else {}
    organs = {organ: compute_organ(repo_root, organ, by_owner, required_slots, weights) for organ in SUBJECTS}

    throne_score = organs["THRONE"]["scores"]["organ_readiness_score"]
    great_nine_scores = [organs[o]["scores"]["organ_readiness_score"] for o in GREAT_NINE]
    great_nine_readiness = clamp(sum(great_nine_scores) / len(great_nine_scores))
    core_readiness = clamp((throne_score * 0.35) + (great_nine_readiness * 0.65))
    lowest = clamp(min([throne_score] + great_nine_scores))

    next_attention = recommend(organs, census_summary, census_gaps)

    all_scores_100 = all(d["scores"]["organ_readiness_score"] == 100 for d in organs.values())
    add_check(checks, "fake_green_guard_not_all_100", not all_scores_100, {})
    if all_scores_100:
        errors.append("Fake-green suspicion: all organs scored 100 in early target gap validation")

    if core_readiness < 100:
        warnings.append("Core readiness below target v1; this is expected and measured.")

    verdict = "FAIL_UNMEASURABLE" if errors else "PASS_MEASURED"

    input_hashes = {}
    for p in [TARGET_MATRIX, SCORING_MATRIX, CENSUS_JSON, SUMMARY_JSON, GAP_JSON]:
        ap = repo_root / p
        if ap.is_file():
            input_hashes[p.as_posix()] = sha256_file(ap)

    receipt = {
        "receipt_id": "receipt.throne_target_gap.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": utc_now(),
        "mode": "MEASURE_ONLY",
        "validation_model": "TARGET_V1_VS_CURRENT_REALITY",
        "scores": {
            "core_readiness_score": core_readiness,
            "throne_readiness_score": throne_score,
            "great_nine_readiness_score": great_nine_readiness,
            "lowest_organ_readiness_score": lowest,
        },
        "organs": organs,
        "next_attention": next_attention,
        "input_hashes_sha256": input_hashes,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "meaning": "PASS_MEASURED means the target gap was measured, not that Imperium v1 is achieved.",
    }

    write_outputs(repo_root, receipt, organs, next_attention)

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "core_readiness_score": core_readiness,
        "throne_readiness_score": throne_score,
        "great_nine_readiness_score": great_nine_readiness,
        "lowest_organ_readiness_score": lowest,
        "receipt": RECEIPT.as_posix(),
        "report": REPORT.as_posix(),
        "table": READINESS_CSV.as_posix(),
        "next_attention": NEXT_ATTENTION.as_posix(),
        "errors": errors,
    }, ensure_ascii=False, indent=2))

    return 0 if verdict in {"PASS_MEASURED", "WARN_PARTIAL_EVIDENCE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
