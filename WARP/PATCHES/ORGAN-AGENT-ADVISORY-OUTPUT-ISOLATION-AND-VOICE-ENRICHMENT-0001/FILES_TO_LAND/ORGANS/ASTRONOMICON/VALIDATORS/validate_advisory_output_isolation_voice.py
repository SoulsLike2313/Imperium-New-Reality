#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

TASK_ID = "ORGAN-AGENT-ADVISORY-OUTPUT-ISOLATION-AND-VOICE-ENRICHMENT-0001"
VALIDATOR_ID = "organ_agent_advisory_output_isolation_voice_validator.v0_1"

MATRIX = Path("ORGANS/ASTRONOMICON/MATRICES/ORGAN_AGENT_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_MATRIX_V0_1.json")
DOCTRINE = Path("ORGANS/ASTRONOMICON/DOCTRINE/ORGAN_AGENT_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_ENRICHMENT_V0_1.md")
TOOL = Path("ORGANS/ASTRONOMICON/TOOLS/organ_agent_advisory.py")
GLOBAL_SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_SUMMARY_V0_1.json")
GLOBAL_REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_REPORT_V0_1.md")

RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/organ_agent_advisory_output_isolation_voice_receipt.json")
REPORT = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_REPORT_V0_1.md")
SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_SUMMARY_V0_1.json")

ORGANS = ["ASTRONOMICON","ADMINISTRATUM","DOCTRINARIUM","MECHANICUS","INQUISITION","CUSTODES","STRATEGIUM","SCHOLA_IMPERIALIS","OFFICIO_AGENTIS","THRONE"]
FORBIDDEN = ["run", "execute", "apply", "commit", "push", "delete", "remove", "copy", "mutate", "запусти", "выполни", "примени", "закоммить", "запушь", "удали", "скопируй", "измени"]
REQUIRED_VOICE = ["what_is_visible","why_this_zone_matters","what_raises_success_probability","what_reduces_success_probability","evidence_considered","not_claimed"]

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
        return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()

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

def text_has_forbidden(text: str) -> List[str]:
    low = text.lower()
    hits = []
    for term in FORBIDDEN:
        if re.search(r"\b" + re.escape(term.lower()) + r"\b", low) if term.isascii() else term.lower() in low:
            hits.append(term)
    return hits

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    checks: List[Dict[str, Any]] = []
    errors: List[str] = []
    warnings: List[str] = []

    for rel in [MATRIX, DOCTRINE, TOOL]:
        ok = (repo / rel).is_file()
        add(checks, f"{rel.name}_exists", ok, {"path": rel.as_posix()})
        if not ok:
            errors.append(f"missing {rel.as_posix()}")

    matrix, err = load_json(repo / MATRIX) if (repo / MATRIX).is_file() else ({}, "missing")
    add(checks, "output_isolation_matrix_parses", err is None, {"error": err})
    if err:
        errors.append("matrix parse failed: " + err)

    # 1. Generate global summary and store hashes.
    code, out, errout = run_py(repo, TOOL, ["--repo-root", str(repo)])
    add(checks, "global_advisory_generation_runs", code == 0, {"stderr": errout[-1000:]})
    if code != 0:
        errors.append("global advisory generation failed")

    global_before_hash = sha(repo / GLOBAL_SUMMARY)
    global_report_before_hash = sha(repo / GLOBAL_REPORT)
    global_data, global_err = load_json(repo / GLOBAL_SUMMARY)
    add(checks, "global_summary_parses", global_err is None, {"error": global_err})
    if global_err:
        errors.append("global summary parse failed")
        global_data = {}

    advisories = global_data.get("advisories", []) if isinstance(global_data, dict) else []
    add(checks, "global_summary_has_all_10_organs", len(advisories) == 10, {"count": len(advisories)})
    if len(advisories) != 10:
        errors.append("global summary does not contain 10 organs")

    # 2. Generate one single-organ advisory, should not touch global files.
    single_json = repo / "ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_INQUISITION_V0_1.json"
    single_md = repo / "ORGANS/ASTRONOMICON/REPORTS/ORGAN_AGENT_ADVISORY_INQUISITION_V0_1.md"
    if single_json.exists():
        single_json.unlink()
    if single_md.exists():
        single_md.unlink()

    code, out, errout = run_py(repo, TOOL, ["--repo-root", str(repo), "--organ", "INQUISITION"])
    add(checks, "single_organ_advisory_generation_runs", code == 0, {"stderr": errout[-1000:]})
    if code != 0:
        errors.append("single-organ advisory generation failed")

    add(checks, "single_organ_json_written", single_json.is_file(), {"path": str(single_json.relative_to(repo)) if single_json.is_file() else str(single_json)})
    add(checks, "single_organ_markdown_written", single_md.is_file(), {"path": str(single_md.relative_to(repo)) if single_md.is_file() else str(single_md)})
    if not single_json.is_file() or not single_md.is_file():
        errors.append("single-organ isolated outputs missing")

    global_after_hash = sha(repo / GLOBAL_SUMMARY)
    global_report_after_hash = sha(repo / GLOBAL_REPORT)
    add(checks, "single_organ_did_not_overwrite_global_summary", global_before_hash == global_after_hash, {"before": global_before_hash, "after": global_after_hash})
    add(checks, "single_organ_did_not_overwrite_global_report", global_report_before_hash == global_report_after_hash, {"before": global_report_before_hash, "after": global_report_after_hash})
    if global_before_hash != global_after_hash:
        errors.append("single-organ advisory overwrote global summary")
    if global_report_before_hash != global_report_after_hash:
        errors.append("single-organ advisory overwrote global report")

    single_data, single_err = load_json(single_json)
    add(checks, "single_organ_json_parses", single_err is None, {"error": single_err})
    if single_err:
        errors.append("single-organ JSON parse failed")
        single_data = {}

    single_items = single_data.get("advisories", []) if isinstance(single_data, dict) else []
    add(checks, "single_organ_has_one_advisory", len(single_items) == 1, {"count": len(single_items)})
    if len(single_items) != 1:
        errors.append("single-organ output does not contain exactly one advisory")

    missing_voice = []
    forbidden_hits = []
    for item in advisories + single_items:
        for field in REQUIRED_VOICE:
            if field not in item:
                missing_voice.append({"organ": item.get("organ_id"), "field": field})
        combined_text = " ".join([
            str(item.get("advisory_text", "")),
            str(item.get("what_is_visible", "")),
            str(item.get("why_this_zone_matters", "")),
            " ".join(map(str, item.get("what_raises_success_probability", []))),
            " ".join(map(str, item.get("what_reduces_success_probability", []))),
        ])
        hits = text_has_forbidden(combined_text)
        if hits:
            forbidden_hits.append({"organ": item.get("organ_id"), "hits": hits, "text": combined_text[:500]})

    add(checks, "voice_enrichment_fields_present", not missing_voice, {"missing": missing_voice[:20]})
    add(checks, "voice_has_no_direct_action_commands", not forbidden_hits, {"violations": forbidden_hits[:10]})
    if missing_voice:
        errors.append("voice enrichment fields missing")
    if forbidden_hits:
        errors.append("voice text contains direct action terms")

    # 3. Restore global generation at the end so normal global output remains fresh.
    code, out, errout = run_py(repo, TOOL, ["--repo-root", str(repo)])
    add(checks, "global_advisory_regenerated_after_test", code == 0, {"stderr": errout[-1000:]})
    if code != 0:
        errors.append("failed to regenerate global advisory after test")

    verdict = "PASS_ADVISORY_OUTPUT_ISOLATION_AND_VOICE_ENRICHED" if not errors else "FAIL_ADVISORY_OUTPUT_ISOLATION_AND_VOICE"
    generated = utc()

    summary = {
        "summary_id": "astronomicon.advisory_output_isolation_voice_validation_summary.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "global_advisory_count": len(advisories),
        "single_organ_test": "INQUISITION",
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "next_layer_recommendation": "After this bug fix, move to red+blue team tools and skills foundation."
    }
    receipt = {
        "receipt_id": "receipt.astronomicon.advisory_output_isolation_voice.v0_1",
        "task_id": TASK_ID,
        "validator_id": VALIDATOR_ID,
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "meaning": "Single-organ advisory is isolated and organ voice is enriched without direct action commands."
    }

    for p in [SUMMARY, RECEIPT, REPORT]:
        (repo / p).parent.mkdir(parents=True, exist_ok=True)
    (repo / SUMMARY).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (repo / RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo / REPORT).write_text(f"""# ORGAN AGENT ADVISORY OUTPUT ISOLATION AND VOICE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`  
repo_head: `{git_head(repo)}`

## Meaning

The single-organ advisory output bug is fixed.

`imperium advise organ INQUISITION` writes isolated per-organ files and does not overwrite global advisory summary/report.

The organ voice is now richer: visible state, why the zone matters, probability raisers/reducers, evidence considered, and not-claimed boundaries.

## Next

Red + Blue team tools and skills foundation.

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
        "global_advisory_count": len(advisories),
        "single_organ_test": "INQUISITION",
        "receipt": RECEIPT.as_posix(),
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings
    }, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
