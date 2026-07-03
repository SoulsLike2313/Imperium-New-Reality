
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

TASK_ID="ORGAN-MATURITY-GATES-CANON-0001"; VALIDATOR_ID="custodes_organ_maturity_prosecutor_matrix_validator.v0_1"
MATRIX=Path("ORGANS/CUSTODES/MATRICES/ORGAN_MATURITY_PROSECUTOR_MATRIX_V0_1.json")
SCHEMA=Path("ORGANS/DOCTRINARIUM/SCHEMAS/ORGAN_MATURITY_GATE_SCHEMA_V0_1.json")
RECEIPT=Path("ORGANS/CUSTODES/RECEIPTS/organ_maturity_prosecutor_matrix_receipt.json")
SUMMARY=Path("ORGANS/CUSTODES/REPORTS/ORGAN_MATURITY_PROSECUTOR_MATRIX_SUMMARY_V0_1.json")
REPORT=Path("ORGANS/CUSTODES/REPORTS/ORGAN_MATURITY_PROSECUTOR_MATRIX_REPORT_V0_1.md")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root", default="."); ap.add_argument("--apply", action="store_true"); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    m,err=load_json(repo/MATRIX) if (repo/MATRIX).is_file() else ({},"missing")
    add(checks,"custodes_prosecutor_matrix_exists_and_parses",err is None,{"path":MATRIX.as_posix(),"error":err})
    if err: errors.append("Custodes prosecutor matrix missing or invalid")
    ints=m.get("gate_interrogations",[]) if isinstance(m,dict) else []
    ids=[g.get("gate_id") for g in ints if isinstance(g,dict)]
    add(checks,"custodes_matrix_covers_exact_six_gates",ids==EXPECTED_GATES,{"expected":EXPECTED_GATES,"actual":ids})
    if ids!=EXPECTED_GATES: errors.append("Custodes matrix does not cover exact six gates")
    details=[]; q_ok=len(ints)==6
    for g in ints if isinstance(ints,list) else []:
        qc=len(g.get("questions",[])) if isinstance(g.get("questions"),list) else 0; bc=len(g.get("blocking_findings",[])) if isinstance(g.get("blocking_findings"),list) else 0; ok=qc>=3 and bc>=3; q_ok=q_ok and ok; details.append({"gate_id":g.get("gate_id"),"questions":qc,"blocking_findings":bc,"ok":ok})
    add(checks,"each_gate_has_prosecutor_questions_and_blocking_findings",q_ok,{"gates":details})
    if not q_ok: errors.append("one or more Custodes gates lack prosecutor questions/blocking findings")
    posture_ok=isinstance(m,dict) and m.get("prosecutor_posture")=="accuse_until_evidence_answers"
    add(checks,"custodes_posture_is_prosecutor_not_helper",posture_ok,{"prosecutor_posture":m.get("prosecutor_posture") if isinstance(m,dict) else None})
    if not posture_ok: errors.append("Custodes matrix does not declare prosecutor posture")
    pass_reqs=m.get("custodes_pass_requires",[]) if isinstance(m,dict) else []; reqs="\n".join(pass_reqs).lower() if isinstance(pass_reqs,list) else ""; no_self="self-trust" in reqs
    add(checks,"custodes_pass_requires_no_self_trust",no_self,{"custodes_pass_requires":pass_reqs})
    if not no_self: errors.append("Custodes pass requirements do not mention self-trust prohibition")
    schema,serr=load_json(repo/SCHEMA) if (repo/SCHEMA).is_file() else ({},"missing"); sids=[g.get("gate_id") for g in schema.get("required_gates",[])] if isinstance(schema,dict) else []
    aligned=serr is None and sids==ids==EXPECTED_GATES
    add(checks,"custodes_matrix_aligned_with_doctrinarium_schema",aligned,{"schema_error":serr,"schema_ids":sids,"matrix_ids":ids})
    if not aligned: errors.append("Custodes matrix not aligned with Doctrinarium schema")
    verdict="PASS_CUSTODES_ORGAN_MATURITY_PROSECUTOR_MATRIX_READY" if not errors else "FAIL_CUSTODES_ORGAN_MATURITY_PROSECUTOR_MATRIX"; generated=utc()
    summary={"summary_id":"custodes.organ_maturity_prosecutor_matrix_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"checks":checks,"errors":errors,"warnings":warnings}
    receipt={"receipt_id":"receipt.custodes.organ_maturity_prosecutor_matrix.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"checks":checks,"errors":errors,"warnings":warnings,"matrix":MATRIX.as_posix(),"schema":SCHEMA.as_posix()}
    write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,receipt)
    checks_md="\n".join(f"- `{c['status']}` — {c['name']}" for c in checks); errors_md="\n".join(f"- {e}" for e in errors) if errors else "- none"
    (repo/REPORT).write_text(f"""# CUSTODES ORGAN MATURITY PROSECUTOR MATRIX REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{generated}`\n\n## Meaning\n\nCustodes receives a universal prosecutor matrix for all organs under the six-gate canon.\n\n## Checks\n\n{checks_md}\n\n## Errors\n\n{errors_md}\n""", encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"errors":errors,"warnings":warnings}, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1
if __name__=="__main__": raise SystemExit(main())
