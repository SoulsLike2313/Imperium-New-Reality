#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "RED-BLUE-TEAM-TOOLS-AND-SKILLS-FOUNDATION-0001"
MATRIX = Path("ORGANS/DOCTRINARIUM/MATRICES/ORGAN_RED_BLUE_TEAM_SKILLS_MATRIX_V0_1.json")
SUMMARY = Path("ORGANS/INQUISITION/REPORTS/RED_BLUE_TEAM_SKILLS_SCAN_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/INQUISITION/REPORTS/RED_BLUE_TEAM_SKILLS_SCAN_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/INQUISITION/RECEIPTS/red_blue_team_skills_scan_receipt.json")

ORGANS = ["ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION","CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS","THRONE"]
FORBIDDEN_CLAIMS = ["RED_TEAM_PROVEN","BLUE_TEAM_PROVEN","CUSTODES_TRUST","THRONE_VERDICT","ORGAN_ASSEMBLED","EXECUTION_ALLOWED"]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git","rev-parse","--short","HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None

def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def skill_score(contract: Dict[str, Any]) -> Dict[str, Any]:
    red = contract.get("red_team", {}).get("skills", [])
    blue = contract.get("blue_team", {}).get("skills", [])
    future = contract.get("required_future_validators", [])
    forbidden = contract.get("forbidden_claims", [])
    proof_state = contract.get("proof_state")
    errors = []
    if len(red) < 3:
        errors.append("red_skills_less_than_3")
    if len(blue) < 3:
        errors.append("blue_skills_less_than_3")
    if len(future) < 4:
        errors.append("future_validators_less_than_4")
    for claim in FORBIDDEN_CLAIMS:
        if claim not in forbidden:
            errors.append(f"missing_forbidden_claim_{claim}")
    if proof_state != "DEFINED_NOT_PROVEN":
        errors.append("proof_state_must_be_DEFINED_NOT_PROVEN")
    red_defined = 100.0 if len(red) >= 3 else round(100 * len(red) / 3, 2)
    blue_defined = 100.0 if len(blue) >= 3 else round(100 * len(blue) / 3, 2)
    proof_score = 0.0
    risk_score = 100.0 - min(red_defined, blue_defined)
    return {
        "organ_id": contract.get("organ_id"),
        "red_defined_score": red_defined,
        "blue_defined_score": blue_defined,
        "red_proven_score": proof_score,
        "blue_proven_score": proof_score,
        "red_blue_definition_score": round((red_defined + blue_defined) / 2, 2),
        "red_blue_proof_score": 0.0,
        "risk_score": risk_score,
        "errors": errors,
        "attention_zone": "red_blue_defined_not_proven" if not errors else "red_blue_definition_gap",
        "advisory_text": f"{contract.get('organ_id')}: Red/Blue skills are defined but not proven. Future layer should focus on validator honesty and action proof."
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--organ")
    ap.add_argument("--out")
    args = ap.parse_args()

    repo = Path(args.repo_root).resolve()
    targets = [args.organ.upper().replace("-", "_")] if args.organ else ORGANS
    results = []
    errors = []
    for organ in targets:
        path = repo / "ORGANS" / organ / "RED_BLUE" / "ORGAN_RED_BLUE_SKILLS_V0_1.json"
        if not path.is_file():
            errors.append(f"missing {path.relative_to(repo).as_posix()}")
            continue
        contract = load_json(path)
        if not isinstance(contract, dict):
            errors.append(f"invalid json {path.relative_to(repo).as_posix()}")
            continue
        row = skill_score(contract)
        if row["errors"]:
            errors += [f"{organ}:{e}" for e in row["errors"]]
        results.append(row)

    red_defined = round(sum(r["red_defined_score"] for r in results) / len(results), 2) if results else 0.0
    blue_defined = round(sum(r["blue_defined_score"] for r in results) / len(results), 2) if results else 0.0
    red_proven = 0.0
    blue_proven = 0.0
    verdict = "PASS_RED_BLUE_SKILLS_DEFINED_NOT_PROVEN" if not errors and len(results) == len(targets) else "FAIL_RED_BLUE_SKILLS_FOUNDATION"

    summary = {
        "summary_id": "inquisition.red_blue_team_skills_scan_summary.v0_1",
        "patch_id": PATCH_ID,
        "generated_at_utc": utc(),
        "repo_head": git_head(repo),
        "target_organ": args.organ.upper().replace("-", "_") if args.organ else None,
        "verdict": verdict,
        "organ_count": len(results),
        "red_team_defined_score": red_defined,
        "blue_team_defined_score": blue_defined,
        "red_team_proven_score": red_proven,
        "blue_team_proven_score": blue_proven,
        "results": results,
        "errors": errors,
        "warnings": [],
        "not_claimed": ["red_team_proven", "blue_team_proven", "Custodes trust", "Throne verdict", "organ assembled"]
    }

    out = Path(args.out) if args.out else SUMMARY
    write_json(repo / out, summary)
    if not args.out:
        receipt = {
            "receipt_id": "receipt.inquisition.red_blue_team_skills_scan.v0_1",
            "task_id": PATCH_ID,
            "validator_id": "red_blue_team_skills_scan.v0_1",
            "verdict": verdict,
            "generated_at_utc": summary["generated_at_utc"],
            "summary": SUMMARY.as_posix(),
            "report": REPORT.as_posix(),
            "errors": errors,
            "warnings": [],
            "meaning": "All organ Red/Blue skills are defined but proof remains zero."
        }
        write_json(repo / RECEIPT, receipt)
        lines = [
            "# RED + BLUE TEAM SKILLS SCAN REPORT V0.1",
            "",
            f"verdict: `{verdict}`  ",
            f"red_team_defined_score: `{red_defined}`  ",
            f"blue_team_defined_score: `{blue_defined}`  ",
            f"red_team_proven_score: `{red_proven}`  ",
            f"blue_team_proven_score: `{blue_proven}`",
            "",
            "## Meaning",
            "",
            "Red/Blue skills are defined for organ profiles, but not yet proven.",
            "",
            "## Organs",
            ""
        ]
        for r in results:
            lines.append(f"- `{r['organ_id']}` — red_defined `{r['red_defined_score']}`, blue_defined `{r['blue_defined_score']}`, proof `0.0`, zone `{r['attention_zone']}`")
        lines += ["", "## Not claimed", "", "- Custodes trust", "- Throne verdict", "- organ assembled"]
        (repo / REPORT).parent.mkdir(parents=True, exist_ok=True)
        (repo / REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
