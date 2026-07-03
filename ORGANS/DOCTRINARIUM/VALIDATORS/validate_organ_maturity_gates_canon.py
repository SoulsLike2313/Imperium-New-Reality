
from __future__ import annotations
import argparse, datetime as dt, json
from pathlib import Path
from typing import Any, Dict, List
EXPECTED_GATES = ["G1_IDENTITY_AND_JURISDICTION","G2_CONTRACT_AND_EVIDENCE","G3_OPERATIONAL_SURFACE","G4_ADVISORY_AND_HARDENING","G5_EXTERNAL_TRUST","G6_INTEGRATION_AND_MATURITY_LOOP"]
def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def load_json(path: Path):
    try: return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e: return None, str(e)
def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any]|None=None): checks.append({"name":name,"status":"PASS" if ok else "FAIL","details":details or {}})

TASK_ID="ORGAN-MATURITY-GATES-CANON-0001"; VALIDATOR_ID="doctrinarium_organ_maturity_gates_canon_validator.v0_1"
LAW=Path("ORGANS/DOCTRINARIUM/LAWS/ORGAN_MATURITY_GATES_CANON_V0_1.md")
SCHEMA=Path("ORGANS/DOCTRINARIUM/SCHEMAS/ORGAN_MATURITY_GATE_SCHEMA_V0_1.json")
SCORE=Path("ORGANS/DOCTRINARIUM/MATRICES/ORGAN_MATURITY_SCORE_MATRIX_V0_1.json")
RECEIPT=Path("ORGANS/DOCTRINARIUM/RECEIPTS/organ_maturity_gates_canon_receipt.json")
SUMMARY=Path("ORGANS/DOCTRINARIUM/REPORTS/ORGAN_MATURITY_GATES_CANON_SUMMARY_V0_1.json")
REPORT=Path("ORGANS/DOCTRINARIUM/REPORTS/ORGAN_MATURITY_GATES_CANON_REPORT_V0_1.md")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root", default="."); ap.add_argument("--apply", action="store_true"); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    law_path=repo/LAW; law_text=law_path.read_text(encoding="utf-8") if law_path.is_file() else ""
    add(checks,"canon_law_file_exists",law_path.is_file(),{"path":LAW.as_posix(),"bytes":law_path.stat().st_size if law_path.is_file() else 0})
    if not law_path.is_file(): errors.append("canon law file missing")
    required=["Organs do not differ by maturity form","Gate 1","Gate 2","Gate 3","Gate 4","Gate 5","Gate 6","No score may be granted without evidence","Game layer renders truth","Core evidence proves truth"]
    missing=[p for p in required if p not in law_text]
    add(checks,"canon_law_contains_six_gate_and_truth_laws",not missing,{"missing_phrases":missing})
    if missing: errors.append("canon law missing required six-gate/truth phrases")
    schema,err=load_json(repo/SCHEMA) if (repo/SCHEMA).is_file() else ({},"missing")
    add(checks,"gate_schema_exists_and_parses",err is None,{"path":SCHEMA.as_posix(),"error":err})
    if err: errors.append("gate schema missing or invalid")
    gates=schema.get("required_gates",[]) if isinstance(schema,dict) else []
    ids=[g.get("gate_id") for g in gates if isinstance(g,dict)]
    add(checks,"schema_has_exactly_six_canonical_gates",ids==EXPECTED_GATES,{"expected":EXPECTED_GATES,"actual":ids})
    if ids!=EXPECTED_GATES: errors.append("schema does not contain exact canonical six gates in order")
    ev_ok=len(gates)==6 and all(isinstance(g.get("required_evidence_classes"),list) and len(g.get("required_evidence_classes"))>=5 for g in gates)
    add(checks,"each_gate_declares_required_evidence_classes",ev_ok,{"counts":[len(g.get("required_evidence_classes",[])) for g in gates] if isinstance(gates,list) else []})
    if not ev_ok: errors.append("one or more gates have insufficient evidence classes")
    cr=schema.get("claim_rules",{}) if isinstance(schema,dict) else {}
    cr_ok=all(cr.get(k) is True for k in ["claims_must_map_to_evidence","scores_must_map_to_evidence","self_validators_do_not_grant_external_trust","local_crown_does_not_grant_global_core_readiness","game_layer_cannot_claim_truth"])
    add(checks,"schema_contains_anti_fake_green_claim_rules",cr_ok,{"claim_rules":cr})
    if not cr_ok: errors.append("schema anti-fake-green claim rules incomplete")
    score,serr=load_json(repo/SCORE) if (repo/SCORE).is_file() else ({},"missing")
    add(checks,"score_matrix_exists_and_parses",serr is None,{"path":SCORE.as_posix(),"error":serr})
    if serr: errors.append("score matrix missing or invalid")
    sids=[g.get("gate_id") for g in score.get("gates",[])] if isinstance(score,dict) else []
    add(checks,"score_matrix_covers_exact_six_gates",sids==EXPECTED_GATES,{"actual":sids})
    if sids!=EXPECTED_GATES: errors.append("score matrix does not cover exact six gates")
    verdict="PASS_ORGAN_MATURITY_GATES_CANON_READY" if not errors else "FAIL_ORGAN_MATURITY_GATES_CANON"; generated=utc()
    summary={"summary_id":"doctrinarium.organ_maturity_gates_canon_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"checks":checks,"errors":errors,"warnings":warnings,"expected_gates":EXPECTED_GATES,"meaning":"Defines the universal six-gate maturity model for all Imperium organs."}
    receipt={"receipt_id":"receipt.doctrinarium.organ_maturity_gates_canon.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"checks":checks,"errors":errors,"warnings":warnings,"law":LAW.as_posix(),"schema":SCHEMA.as_posix(),"score_matrix":SCORE.as_posix()}
    write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,receipt)
    checks_md="\n".join(f"- `{c['status']}` — {c['name']}" for c in checks); errors_md="\n".join(f"- {e}" for e in errors) if errors else "- none"; warnings_md="\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo/REPORT).write_text(f"""# ORGAN MATURITY GATES CANON REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{generated}`\n\n## Meaning\n\nThis validator proves that the universal six-gate organ maturity canon exists, parses and contains the required anti-fake-green laws.\n\n## Checks\n\n{checks_md}\n\n## Warnings\n\n{warnings_md}\n\n## Errors\n\n{errors_md}\n""", encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"errors":errors,"warnings":warnings}, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1
if __name__=="__main__": raise SystemExit(main())
