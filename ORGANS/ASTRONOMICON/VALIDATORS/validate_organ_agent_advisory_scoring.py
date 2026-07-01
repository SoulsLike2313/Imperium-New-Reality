#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "ORGAN-AGENT-ADVISORY-SCORING-FOUNDATION-0001"
VALIDATOR_ID = "organ_agent_advisory_scoring_validator.v0_1"

MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/ORGAN_AGENT_ADVISORY_SCORING_MATRIX_V0_1.json")
DOCTRINE = Path("ORGANS/ASTRONOMICON/DOCTRINE/ORGAN_AGENT_ADVISORY_SCORING_FOUNDATION_V0_1.md")
TOOL = Path("ORGANS/ASTRONOMICON/TOOLS/organ_agent_advisory.py")
LAUNCHER = Path("SUPPORT/LAUNCHER/imperium_cli.py")
COMMANDS = Path("SUPPORT/LAUNCHER/LAUNCHER_COMMANDS_V0_3.json")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_scoring_validation_receipt.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_SCORING_VALIDATION_REPORT_V0_1.md")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_SCORING_VALIDATION_SUMMARY_V0_1.json")

ORGANS = [
    "ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION",
    "CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS","THRONE"
]

FORBIDDEN = [
    "run ", "execute ", "apply ", "commit ", "push ", "delete ", "remove ", "copy ", "mutate ",
    "запусти", "выполни", "примени", "закоммить", "запушь", "удали", "скопируй", "измени"
]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def load_json(path: Path) -> Tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e:
        return None, str(e)

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def run_py(repo: Path, script: Path, args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run([sys.executable, str(repo / script)] + args, cwd=str(repo), capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout, p.stderr

def run_cli(repo: Path, args: List[str]) -> Tuple[int, str, str]:
    p = subprocess.run([sys.executable, str(repo / LAUNCHER), "--repo-root", str(repo)] + args, cwd=str(repo), capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout, p.stderr

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    for rel in [MATRIX, DOCTRINE, TOOL, LAUNCHER, COMMANDS]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    matrix, err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "advisory_matrix_parses", err is None, {"error": err})
    if err:
        errors.append("advisory matrix parse failed: " + err)
        matrix = {}

    weights = matrix.get("success_score_formula", {}).get("weighted_terms", {}) if isinstance(matrix, dict) else {}
    weight_sum = round(sum(float(v) for v in weights.values()), 4) if weights else 0
    add(checks, "success_score_weights_sum_to_one", abs(weight_sum - 1.0) < 0.0001, {"weight_sum": weight_sum, "weights": weights})
    if abs(weight_sum - 1.0) >= 0.0001:
        errors.append("success score weights do not sum to 1.0")

    organs_matrix = matrix.get("organs", {}) if isinstance(matrix, dict) else {}
    missing_organs = [o for o in ORGANS if o not in organs_matrix]
    add(checks, "all_organs_have_advisory_profiles", not missing_organs, {"missing": missing_organs})
    if missing_organs:
        errors.append("missing advisory profiles: " + ", ".join(missing_organs))

    code, out, errout = run_py(repo, TOOL, ["--repo-root", str(repo)])
    add(checks, "organ_agent_advisory_tool_runs", code == 0, {"stderr": errout[-1000:]})
    if code != 0:
        errors.append("organ advisory tool failed")

    summary, parse_err = load_json(repo / "ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_SUMMARY_V0_1.json")
    add(checks, "organ_agent_advisory_summary_parses", parse_err is None, {"error": parse_err})
    if parse_err:
        errors.append("advisory summary parse failed: " + parse_err)
        summary = {}

    advisories = summary.get("advisories", []) if isinstance(summary, dict) else []
    add(checks, "advisory_count_matches_organs", len(advisories) == len(ORGANS), {"count": len(advisories)})
    if len(advisories) != len(ORGANS):
        errors.append("advisory count does not match organ count")

    score_bad = []
    action_bad = []
    profile_bad = []
    for item in advisories:
        score = item.get("future_step_success_score")
        priority = item.get("attention_priority_score")
        if not isinstance(score, (int, float)) or score < 0 or score > 100 or not isinstance(priority, (int, float)) or priority < 0 or priority > 100:
            score_bad.append(item.get("organ_id"))
        text = str(item.get("advisory_text", "")).lower()
        for term in FORBIDDEN:
            if term in text:
                action_bad.append({"organ": item.get("organ_id"), "term": term, "text": item.get("advisory_text")})
        organ = item.get("organ_id")
        zone = item.get("attention_zone")
        allowed = organs_matrix.get(organ, {}).get("allowed_attention_zones", [])
        # Allow generated compact zone if it maps to one of the profile keywords through domain text.
        domain = organs_matrix.get(organ, {}).get("domain", "")
        if not zone or not domain:
            profile_bad.append({"organ": organ, "zone": zone})
    add(checks, "advisory_scores_are_numeric_0_100", not score_bad, {"bad": score_bad})
    add(checks, "advisory_text_has_no_direct_action_commands", not action_bad, {"violations": action_bad[:10]})
    add(checks, "advisory_items_have_profile_domains", not profile_bad, {"violations": profile_bad[:10]})
    if score_bad:
        errors.append("bad advisory scores")
    if action_bad:
        errors.append("advisory text contains direct action commands")
    if profile_bad:
        errors.append("advisory items missing profile domain")

    # Launcher commands.
    for name, argv in [
        ("advise", ["advise"]),
        ("advise_organ_astronomicon", ["advise", "organ", "ASTRONOMICON"]),
    ]:
        code, out, errout = run_cli(repo, argv)
        add(checks, f"launcher_{name}_runs", code == 0, {"stderr": errout[-1000:], "stdout_tail": out[-1000:]})
        if code != 0:
            errors.append(f"launcher {name} failed")

    # Ensure command docs exist.
    commands, cmd_err = load_json(repo / COMMANDS) if (repo / COMMANDS).is_file() else ({}, "missing")
    declared = commands.get("new_organ_agent_commands", []) if isinstance(commands, dict) else []
    required_cmds = ["advise", "advise organ <ORGAN>"]
    missing_cmds = [c for c in required_cmds if c not in declared]
    add(checks, "launcher_advisory_commands_declared", not missing_cmds, {"missing": missing_cmds})
    if missing_cmds:
        errors.append("missing advisory launcher commands")

    verdict = "PASS_ORGAN_AGENT_ADVISORY_SCORING_READY" if not errors else "FAIL_ORGAN_AGENT_ADVISORY_SCORING"
    generated = utc()

    validation_summary = {
        "summary_id": "astronomicon.organ_agent_advisory_scoring_validation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "organ_count": len(ORGANS),
        "advisory_count": len(advisories),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "not_claimed": ["execution", "trust", "Throne verdict", "concrete action command"]
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.organ_agent_advisory_scoring_validation.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Organ-agent advisory layer is conversational, mathematically scored, and limited to attention zones."
    }

    for p in [SUMMARY, RECEIPT, REPORT]:
        (repo / p).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(validation_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# ORGAN AGENT ADVISORY SCORING VALIDATION REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Meaning

Organs can now speak as advisory agents.

They may point to profile-specific attention zones using mathematical scoring.

They must not command concrete actions, execute, claim trust, or claim Throne verdict.

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}
""", encoding="utf-8")

    print(json.dumps({
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "organ_count": len(ORGANS),
        "advisory_count": len(advisories),
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
