#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

PATCH_ID = "CUSTODES-ASTRONOMICON-VALIDATION-INVOKE-CONTRACT-FIX-0001"
MATRIX = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_VALIDATOR_INVOKE_CONTRACTS_V0_1.json")
SUMMARY = Path("ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/CUSTODES/REPORTS/CUSTODES_ASTRONOMICON_PROSECUTOR_AUDIT_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/CUSTODES/RECEIPTS/custodes_astronomicon_prosecutor_audit_receipt.json")

REQUIRED_CAPABILITIES = [
    "ORGANS/ASTRONOMICON/TOOLS/astronomicon_intake_dry_run.py",
    "ORGANS/ASTRONOMICON/TOOLS/astronomicon_patch_pack_smoke.py",
    "ORGANS/ASTRONOMICON/TOOLS/organ_agent_advisory.py",
    "ORGANS/ASTRONOMICON/TOOLS/astronomicon_red_blue_hardening.py",
    "ORGANS/ASTRONOMICON/RED_BLUE/ASTRONOMICON_RED_BLUE_HARDENING_MATRIX_V0_1.json",
    "ORGANS/ASTRONOMICON/RED_BLUE/ASTRONOMICON_RED_BLUE_HARDENING_CASES_V0_1.json",
    "ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_red_blue_hardening_scan_isolation_receipt.json",
]

BOUNDARY_FILES = [
    "ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SCAN_ISOLATION_SUMMARY_V0_1.json",
    "ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_SUMMARY_V0_1.json",
    "ORGANS/ASTRONOMICON/REPORTS/RED_BLUE_TEAM_LAUNCHER_SCAN_COMMANDS_SUMMARY_V0_1.json",
]

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

def pct(ok: int, total: int) -> float:
    return round(100.0 * ok / total, 2) if total else 0.0

def render_attempt(repo: Path, attempt: List[str]) -> List[str]:
    return [str(repo) if x == "{repo}" else x for x in attempt]

def parse_verdict(stdout: str, repo: Path, script: Path) -> str | None:
    text = (stdout or "").strip()
    if text:
        try:
            data = json.loads(text)
            if isinstance(data, dict) and data.get("verdict"):
                return str(data.get("verdict"))
        except Exception:
            pass
        for line in reversed(text.splitlines()):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    data = json.loads(line)
                    if isinstance(data, dict) and data.get("verdict"):
                        return str(data.get("verdict"))
                except Exception:
                    pass
    # fallback: check recent common receipts by validator family
    candidates = [
        repo / "ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_scoring_validation_receipt.json",
        repo / "ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_output_isolation_voice_receipt.json",
        repo / "ORGANS/ASTRONOMICON/RECEIPTS/red_blue_team_launcher_scan_commands_receipt.json",
        repo / "ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_red_blue_hardening_scan_isolation_receipt.json",
        repo / "ORGANS/ASTRONOMICON/RECEIPTS/patch_lifecycle_launcher_commands_receipt.json",
        repo / "ORGANS/ASTRONOMICON/RECEIPTS/patch_pack_lifecycle_validation_foundation_receipt.json",
        repo / "ORGANS/ASTRONOMICON/RECEIPTS/patch_pack_intake_validation_smoke_receipt.json",
    ]
    script_name = script.name
    for c in candidates:
        if c.is_file():
            data = load_json(c)
            if isinstance(data, dict) and data.get("verdict"):
                if (
                    ("advisory_scoring" in c.name and "advisory_scoring" in script_name) or
                    ("output_isolation" in c.name and "output_isolation" in script_name) or
                    ("launcher_scan" in c.name and "launcher_scan" in script_name) or
                    ("red_blue_hardening" in c.name and "red_blue_hardening" in script_name) or
                    ("lifecycle_launcher" in c.name and "lifecycle_launcher" in script_name) or
                    ("lifecycle_validation_foundation" in c.name and "lifecycle_validation_foundation" in script_name) or
                    ("intake_validation_smoke" in c.name and "intake_validation_smoke" in script_name)
                ):
                    return str(data.get("verdict"))
    return None

def run_validator(repo: Path, path: str, attempts: List[List[str]]) -> Dict[str, Any]:
    script = repo / path
    result = {
        "path": path,
        "status": "FAIL",
        "verdict": None,
        "exit_code": None,
        "winning_attempt": None,
        "attempts": [],
    }
    if not script.is_file():
        result["attempts"].append({"args": None, "exit_code": None, "stderr_tail": "missing script", "stdout_tail": ""})
        return result

    for attempt in attempts:
        args = render_attempt(repo, attempt)
        p = subprocess.run([sys.executable, str(script)] + args, cwd=str(repo), capture_output=True, text=True, timeout=180)
        verdict = parse_verdict(p.stdout, repo, script)
        record = {
            "args": args,
            "exit_code": p.returncode,
            "verdict": verdict,
            "stdout_tail": (p.stdout or "")[-1200:],
            "stderr_tail": (p.stderr or "")[-1200:],
        }
        result["attempts"].append(record)
        if p.returncode == 0 and verdict and verdict.startswith("PASS"):
            result.update({"status": "PASS", "verdict": verdict, "exit_code": p.returncode, "winning_attempt": args})
            return result

    last = result["attempts"][-1] if result["attempts"] else {}
    result["verdict"] = last.get("verdict")
    result["exit_code"] = last.get("exit_code")
    return result

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    matrix = load_json(repo / MATRIX)
    if not isinstance(matrix, dict):
        print(json.dumps({"verdict": "FAIL_CUSTODES_ASTRONOMICON_PROSECUTOR_VALIDATION", "indictments": ["invoke contract matrix missing"]}, ensure_ascii=False, indent=2))
        return 1

    contracts = matrix.get("validator_contracts", [])
    validators_tested = []
    indictments = []

    for c in contracts:
        path = c.get("path")
        attempts = c.get("attempts") or matrix.get("default_attempts") or [["--repo-root", "{repo}"]]
        row = run_validator(repo, path, attempts)
        validators_tested.append(row)
        if row["status"] != "PASS":
            indictments.append(f"validator failed {path}")

    identity_paths = [
        repo / "ORGANS/ASTRONOMICON",
        repo / "ORGANS/ASTRONOMICON/RED_BLUE/ORGAN_RED_BLUE_SKILLS_V0_1.json",
    ]
    identity_score = pct(sum(1 for p in identity_paths if p.exists()), len(identity_paths))

    capability_score = pct(sum(1 for p in REQUIRED_CAPABILITIES if (repo / p).is_file()), len(REQUIRED_CAPABILITIES))
    validator_working_score = pct(sum(1 for v in validators_tested if v["status"] == "PASS"), len(validators_tested))

    redblue = load_json(repo / "ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_RED_BLUE_HARDENING_SCAN_ISOLATION_SUMMARY_V0_1.json") or {}
    red_blue_truth_score = 100.0 if (
        redblue.get("red_team_proven_score") == 0.0 and
        redblue.get("blue_team_proven_score") == 0.0 and
        redblue.get("custodes_validation_score") == 0.0 and
        redblue.get("throne_confirmation_score") == 0.0
    ) else 0.0
    if red_blue_truth_score < 100:
        indictments.append("Astronomicon red/blue proof truth inflated before Custodes/Throne")

    boundary_text = ""
    for p in BOUNDARY_FILES:
        f = repo / p
        if f.is_file():
            boundary_text += f.read_text(encoding="utf-8", errors="replace").lower() + "\n"
    boundary_hits = sum(1 for token in ["not_claimed", "throne verdict", "custodes", "organ assembled"] if token in boundary_text)
    boundary_honesty_score = pct(boundary_hits, 4)

    evidence_chain_paths = REQUIRED_CAPABILITIES + [c.get("path") for c in contracts]
    evidence_chain_score = pct(sum(1 for p in evidence_chain_paths if p and (repo / p).is_file()), len(evidence_chain_paths))

    scores = [
        identity_score,
        capability_score,
        validator_working_score,
        boundary_honesty_score,
        red_blue_truth_score,
        evidence_chain_score,
    ]
    custodes_score = round(sum(scores) / len(scores), 2)
    throne_confirmation_score = 0.0

    if identity_score < 80: indictments.append("identity score below threshold")
    if capability_score < 80: indictments.append("capability evidence score below threshold")
    if validator_working_score < 100: indictments.append("not all Astronomicon validators passed under Custodes")
    if boundary_honesty_score < 80: indictments.append("boundary honesty score below threshold")
    if evidence_chain_score < 80: indictments.append("evidence chain score below threshold")

    verdict = "PASS_CUSTODES_ASTRONOMICON_PROSECUTOR_VALIDATION" if not indictments and custodes_score >= 85 else "FAIL_CUSTODES_ASTRONOMICON_PROSECUTOR_VALIDATION"
    generated = utc()
    summary = {
        "summary_id": "custodes.astronomicon_prosecutor_audit_summary.v0_2",
        "task_id": PATCH_ID,
        "validator_id": "custodes_audit_astronomicon.v0_2_invoke_contracts",
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "target_organ": "ASTRONOMICON",
        "identity_score": identity_score,
        "capability_evidence_score": capability_score,
        "validator_working_score": validator_working_score,
        "boundary_honesty_score": boundary_honesty_score,
        "red_blue_truth_score": red_blue_truth_score,
        "evidence_chain_score": evidence_chain_score,
        "custodes_validation_score": custodes_score,
        "throne_confirmation_score": throne_confirmation_score,
        "validators_tested": validators_tested,
        "indictments": indictments,
        "errors": indictments,
        "warnings": [],
        "not_claimed": ["Throne verdict", "organ assembled"]
    }
    receipt = {
        "receipt_id": "receipt.custodes.astronomicon_prosecutor_audit.v0_2",
        "task_id": PATCH_ID,
        "validator_id": "custodes_audit_astronomicon.v0_2_invoke_contracts",
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": indictments,
        "warnings": [],
        "meaning": "Custodes prosecuted Astronomicon using adaptive validator invocation contracts."
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)

    lines = [
        "# CUSTODES ASTRONOMICON PROSECUTOR AUDIT REPORT V0.2",
        "",
        f"verdict: `{verdict}`  ",
        f"custodes_validation_score: `{custodes_score}`  ",
        f"validator_working_score: `{validator_working_score}`  ",
        f"throne_confirmation_score: `{throne_confirmation_score}`",
        "",
        "## Meaning",
        "",
        "Custodes prosecutes Astronomicon honesty. Validator invocation uses declared/adaptive contracts.",
        "",
        "## Validators tested",
        ""
    ]
    for v in validators_tested:
        lines.append(f"- `{v['status']}` — `{v['path']}` — `{v.get('verdict')}` — attempt `{v.get('winning_attempt')}`")
    lines += ["", "## Indictments", ""]
    lines += [f"- {x}" for x in indictments] if indictments else ["- none"]
    lines += ["", "## Not claimed", "", "- Throne verdict", "- organ assembled"]
    (repo / REPORT).parent.mkdir(parents=True, exist_ok=True)
    (repo / REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
