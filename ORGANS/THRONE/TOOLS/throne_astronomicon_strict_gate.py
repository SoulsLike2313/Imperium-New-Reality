#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

PATCH_ID = "THRONE-ASTRONOMICON-STRICT-GATES-ANTI-SELF-DECEPTION-FIX-0001"
MATRIX = Path("ORGANS/THRONE/MATRICES/THRONE_ASTRONOMICON_STRICT_GATES_ANTI_SELF_DECEPTION_MATRIX_V0_2.json")
SUMMARY = Path("ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/THRONE/REPORTS/THRONE_ASTRONOMICON_STRICT_GATES_REPORT_V0_1.md")
RECEIPT = Path("ORGANS/THRONE/RECEIPTS/throne_astronomicon_strict_gates_receipt.json")
ASTRO_SUMMARY = Path("ORGANS/ASTRONOMICON/REPORTS/ASTRONOMICON_THRONE_STRICT_GATE_SUMMARY_V0_1.json")
ASTRO_RECEIPT = Path("ORGANS/ASTRONOMICON/RECEIPTS/astronomicon_throne_strict_gate_receipt.json")

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git_head(repo: Path) -> str:
    try:
        p = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=15)
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

def gate(name: str, ok: bool, score: float, evidence: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {"gate_id": name, "status": "PASS" if ok else "FAIL", "score": 100.0 if ok else 0.0 if score is None else score, "evidence": evidence, "details": details or {}}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo = Path(args.repo_root).resolve()

    matrix = load_json(repo / MATRIX)
    errors: List[str] = []
    warnings: List[str] = []
    if not isinstance(matrix, dict):
        matrix = {}
        errors.append("anti-self-deception matrix missing or invalid")

    required = matrix.get("required_inputs", {})
    thresholds = matrix.get("gate_thresholds", {})
    inputs = {}
    for key, rel in required.items():
        p = repo / rel
        data = load_json(p) if p.is_file() and p.suffix.lower() == ".json" else None
        inputs[key] = {"path": rel, "exists": p.exists(), "data": data}
        if not p.exists():
            errors.append(f"missing required input {key}: {rel}")

    rb = inputs.get("astronomicon_red_blue_hardening", {}).get("data") or {}
    custodes = inputs.get("custodes_prosecutor_audit", {}).get("data") or {}
    custodes_receipt = inputs.get("custodes_validation_receipt", {}).get("data") or {}
    rb_contract = inputs.get("organ_red_blue_contract", {}).get("data") or {}

    gates = []
    gates.append(gate("ASTRONOMICON_IDENTITY_EXACT", custodes.get("target_organ") == "ASTRONOMICON" and custodes.get("identity_score") == 100, custodes.get("identity_score"), required.get("custodes_prosecutor_audit",""), {"target_organ": custodes.get("target_organ")}))
    gates.append(gate("CAPABILITY_EVIDENCE_EXACT", custodes.get("capability_evidence_score") == 100, custodes.get("capability_evidence_score"), required.get("custodes_prosecutor_audit","")))
    gates.append(gate("VALIDATORS_WORK_UNDER_CUSTODES", custodes.get("validator_working_score") == 100, custodes.get("validator_working_score"), required.get("custodes_prosecutor_audit",""), {"validator_count": len(custodes.get("validators_tested", []))}))
    indictments = custodes.get("indictments", [])
    gates.append(gate("NO_CUSTODES_INDICTMENTS", isinstance(indictments, list) and len(indictments) == 0, 100.0 if isinstance(indictments, list) and not indictments else 0.0, required.get("custodes_prosecutor_audit",""), {"indictments": indictments}))
    gates.append(gate("CUSTODES_VALIDATION_EXACT", custodes.get("custodes_validation_score") == 100 and str(custodes.get("verdict","")).startswith("PASS") and str(custodes_receipt.get("verdict","")).startswith("PASS"), custodes.get("custodes_validation_score"), required.get("custodes_validation_receipt",""), {"audit_verdict": custodes.get("verdict"), "receipt_verdict": custodes_receipt.get("verdict")}))
    gates.append(gate("BOUNDARY_HONESTY_EXACT", custodes.get("boundary_honesty_score") == 100, custodes.get("boundary_honesty_score"), required.get("custodes_prosecutor_audit","")))
    gates.append(gate("EVIDENCE_CHAIN_EXACT", custodes.get("evidence_chain_score") == 100, custodes.get("evidence_chain_score"), required.get("custodes_prosecutor_audit","")))
    gates.append(gate("RED_BLUE_LOCAL_HARDENING_EXACT", rb.get("red_local_hardening_score") == 100 and rb.get("blue_local_hardening_score") == 100, min(float(rb.get("red_local_hardening_score", 0)), float(rb.get("blue_local_hardening_score", 0))), required.get("astronomicon_red_blue_hardening",""), {"red": rb.get("red_local_hardening_score"), "blue": rb.get("blue_local_hardening_score")}))
    gates.append(gate("PRIOR_THRONE_WAS_NOT_EXTERNAL_PROOF", rb.get("throne_confirmation_score") == 0.0 and custodes.get("throne_confirmation_score") == 0.0, 100.0 if rb.get("throne_confirmation_score") == 0.0 and custodes.get("throne_confirmation_score") == 0.0 else 0.0, required.get("astronomicon_red_blue_hardening",""), {"rb_throne_confirmation_score": rb.get("throne_confirmation_score"), "custodes_throne_confirmation_score": custodes.get("throne_confirmation_score")}))
    gates.append(gate("RED_BLUE_CONTRACT_DEFINED_NOT_PROVEN", rb_contract.get("organ_id") == "ASTRONOMICON" and rb_contract.get("proof_state") == "DEFINED_NOT_PROVEN", 100.0 if rb_contract.get("proof_state") == "DEFINED_NOT_PROVEN" else 0.0, required.get("organ_red_blue_contract",""), {"proof_state": rb_contract.get("proof_state")}))

    failed = [g for g in gates if g["status"] != "PASS"]
    if failed:
        errors += [f"gate failed: {g['gate_id']}" for g in failed]

    gate_score = round(sum(1 for g in gates if g["status"] == "PASS") * 100.0 / len(gates), 2) if gates else 0.0
    strict_pass = not errors and len(gates) >= 10 and gate_score == 100.0

    astronomicon_crown_order_score = 100.0 if strict_pass else 0.0
    # Compatibility fields remain, but truth fields disambiguate them.
    astronomicon_crown_gate_score = astronomicon_crown_order_score
    astronomicon_red_team_crown_score = astronomicon_crown_order_score
    astronomicon_blue_team_crown_score = astronomicon_crown_order_score
    astronomicon_throne_confirmed_score = astronomicon_crown_order_score

    throne_self_validation_score = 0.0
    external_witness_for_throne_score = 0.0
    astronomicon_assembled_score = 0.0

    crown_order_truth_state = "CROWN_ORDER_ISSUED_NOT_THRONE_SELF_PROVEN" if strict_pass else "CROWN_ORDER_BLOCKED"

    verdict = "PASS_THRONE_ASTRONOMICON_CROWN_ORDER_WITH_SELF_DECEPTION_GUARD" if strict_pass else "FAIL_THRONE_ASTRONOMICON_STRICT_GATES"
    generated = utc()
    summary = {
        "summary_id": "throne.astronomicon_strict_gates_summary.v0_2_anti_self_deception",
        "task_id": PATCH_ID,
        "validator_id": "throne_astronomicon_strict_gate.v0_2_anti_self_deception",
        "verdict": verdict,
        "generated_at_utc": generated,
        "repo_head": git_head(repo),
        "target_organ": "ASTRONOMICON",
        "crown_order_truth_state": crown_order_truth_state,
        "gate_count": len(gates),
        "gate_pass_count": sum(1 for g in gates if g["status"] == "PASS"),
        "astronomicon_crown_order_score": astronomicon_crown_order_score,
        "astronomicon_crown_gate_score": astronomicon_crown_gate_score,
        "astronomicon_red_team_crown_score": astronomicon_red_team_crown_score,
        "astronomicon_blue_team_crown_score": astronomicon_blue_team_crown_score,
        "astronomicon_throne_confirmed_score": astronomicon_throne_confirmed_score,
        "throne_self_validation_score": throne_self_validation_score,
        "external_witness_for_throne_score": external_witness_for_throne_score,
        "astronomicon_assembled_score": astronomicon_assembled_score,
        "custodes_validation_score": custodes.get("custodes_validation_score"),
        "custodes_indictment_count": len(indictments) if isinstance(indictments, list) else None,
        "gates": gates,
        "errors": errors,
        "warnings": warnings,
        "not_claimed": matrix.get("not_claimed", [])
    }
    receipt = {
        "receipt_id": "receipt.throne.astronomicon_strict_gates.v0_2_anti_self_deception",
        "task_id": PATCH_ID,
        "validator_id": "throne_astronomicon_strict_gate.v0_2_anti_self_deception",
        "verdict": verdict,
        "generated_at_utc": generated,
        "summary": SUMMARY.as_posix(),
        "report": REPORT.as_posix(),
        "errors": errors,
        "warnings": warnings,
        "meaning": "Throne issued a local Astronomicon Crown order while explicitly denying Throne self-validation."
    }
    astro_receipt = {
        "receipt_id": "receipt.astronomicon.throne_strict_gate.v0_2_anti_self_deception",
        "task_id": PATCH_ID,
        "validator_id": "throne_astronomicon_strict_gate.v0_2_anti_self_deception",
        "verdict": verdict,
        "generated_at_utc": generated,
        "throne_summary": SUMMARY.as_posix(),
        "astronomicon_crown_order_score": astronomicon_crown_order_score,
        "throne_self_validation_score": throne_self_validation_score,
        "astronomicon_assembled_score": astronomicon_assembled_score,
        "not_claimed": matrix.get("not_claimed", [])
    }
    write_json(repo / SUMMARY, summary)
    write_json(repo / RECEIPT, receipt)
    write_json(repo / ASTRO_SUMMARY, summary)
    write_json(repo / ASTRO_RECEIPT, astro_receipt)

    lines = [
        "# THRONE ASTRONOMICON STRICT GATES REPORT V0.2 — ANTI SELF-DECEPTION",
        "",
        f"verdict: `{verdict}`  ",
        f"crown_order_truth_state: `{crown_order_truth_state}`  ",
        f"astronomicon_crown_order_score: `{astronomicon_crown_order_score}`  ",
        f"throne_self_validation_score: `{throne_self_validation_score}`  ",
        f"external_witness_for_throne_score: `{external_witness_for_throne_score}`  ",
        f"astronomicon_assembled_score: `{astronomicon_assembled_score}`",
        "",
        "## Meaning",
        "",
        "Throne issued a local Crown order over Astronomicon evidence. This is not proof that Throne validated itself.",
        "",
        "## Gates",
        ""
    ]
    for g in gates:
        lines.append(f"- `{g['status']}` — `{g['gate_id']}` — score `{g['score']}` — evidence `{g['evidence']}`")
    lines += ["", "## Errors", ""]
    lines += [f"- {e}" for e in errors] if errors else ["- none"]
    lines += ["", "## Not claimed", ""]
    lines += [f"- {x}" for x in matrix.get("not_claimed", [])]
    (repo / REPORT).parent.mkdir(parents=True, exist_ok=True)
    (repo / REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1

if __name__ == "__main__":
    raise SystemExit(main())
