
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

TASK_ID="ORGAN-MATURITY-GATES-CANON-0001"; VALIDATOR_ID="throne_organ_maturity_crown_gate_matrix_validator.v0_1"
MATRIX=Path("ORGANS/THRONE/MATRICES/ORGAN_MATURITY_CROWN_GATE_MATRIX_V0_1.json")
LAW=Path("ORGANS/DOCTRINARIUM/LAWS/ORGAN_MATURITY_GATES_CANON_V0_1.md")
SCHEMA=Path("ORGANS/DOCTRINARIUM/SCHEMAS/ORGAN_MATURITY_GATE_SCHEMA_V0_1.json")
RECEIPT=Path("ORGANS/THRONE/RECEIPTS/organ_maturity_crown_gate_matrix_receipt.json")
SUMMARY=Path("ORGANS/THRONE/REPORTS/ORGAN_MATURITY_CROWN_GATE_MATRIX_SUMMARY_V0_1.json")
REPORT=Path("ORGANS/THRONE/REPORTS/ORGAN_MATURITY_CROWN_GATE_MATRIX_REPORT_V0_1.md")
FORBIDDEN=["core_v1_ready","great_nine_assembled","throne_complete","global_organ_assembled","visual_work_unfrozen","game_projection_truth_source"]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root", default="."); ap.add_argument("--apply", action="store_true"); args=ap.parse_args(); repo=Path(args.repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    m,err=load_json(repo/MATRIX) if (repo/MATRIX).is_file() else ({},"missing")
    add(checks,"throne_crown_gate_matrix_exists_and_parses",err is None,{"path":MATRIX.as_posix(),"error":err})
    if err: errors.append("Throne crown gate matrix missing or invalid")
    reqs=m.get("gate_requirements",[]) if isinstance(m,dict) else []
    ids=[g.get("gate_id") for g in reqs if isinstance(g,dict)]
    add(checks,"throne_matrix_covers_exact_six_gates",ids==EXPECTED_GATES,{"expected":EXPECTED_GATES,"actual":ids})
    if ids!=EXPECTED_GATES: errors.append("Throne matrix does not cover exact six gates")
    laws=m.get("crown_laws",[]) if isinstance(m,dict) else []; text="\n".join(laws).lower() if isinstance(laws,list) else ""
    laws_ok=("local organ maturity is not core v1 readiness" in text and "local crown confirmation is not great nine assembled" in text and "game projection is display" in text)
    add(checks,"throne_crown_laws_prevent_local_to_global_pollution",laws_ok,{"crown_laws":laws})
    if not laws_ok: errors.append("Throne crown laws do not sufficiently prevent local-to-global pollution")
    forbidden=m.get("forbidden_global_mutations",[]) if isinstance(m,dict) else []; f_ok=all(x in forbidden for x in FORBIDDEN)
    add(checks,"throne_matrix_declares_forbidden_global_mutations",f_ok,{"expected":FORBIDDEN,"actual":forbidden})
    if not f_ok: errors.append("Throne matrix missing required forbidden global mutations")
    allowed=m.get("local_crown_allowed_outputs",[]) if isinstance(m,dict) else []; a_ok="organ_local_crown_confirmed" in allowed and "organ_maturity_gate_score" in allowed
    add(checks,"throne_matrix_allows_local_outputs_without_global_claims",a_ok,{"allowed":allowed})
    if not a_ok: errors.append("Throne matrix does not declare safe local crown outputs")
    law_text=(repo/LAW).read_text(encoding="utf-8") if (repo/LAW).is_file() else ""; law_ok="Core v1 is not achieved" in law_text
    add(checks,"doctrinarium_law_contains_core_v1_boundary",law_ok,{"law_path":LAW.as_posix()})
    if not law_ok: errors.append("Doctrinarium law missing Core v1 boundary language")
    schema,serr=load_json(repo/SCHEMA) if (repo/SCHEMA).is_file() else ({},"missing"); sids=[g.get("gate_id") for g in schema.get("required_gates",[])] if isinstance(schema,dict) else []
    aligned=serr is None and sids==ids==EXPECTED_GATES
    add(checks,"throne_matrix_aligned_with_doctrinarium_schema",aligned,{"schema_error":serr,"schema_ids":sids,"matrix_ids":ids})
    if not aligned: errors.append("Throne matrix not aligned with Doctrinarium schema")
    verdict="PASS_THRONE_ORGAN_MATURITY_CROWN_GATE_MATRIX_READY" if not errors else "FAIL_THRONE_ORGAN_MATURITY_CROWN_GATE_MATRIX"; generated=utc()
    summary={"summary_id":"throne.organ_maturity_crown_gate_matrix_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"checks":checks,"errors":errors,"warnings":warnings}
    receipt={"receipt_id":"receipt.throne.organ_maturity_crown_gate_matrix.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"checks":checks,"errors":errors,"warnings":warnings,"matrix":MATRIX.as_posix(),"law":LAW.as_posix(),"schema":SCHEMA.as_posix()}
    write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,receipt)
    checks_md="\n".join(f"- `{c['status']}` — {c['name']}" for c in checks); errors_md="\n".join(f"- {e}" for e in errors) if errors else "- none"
    (repo/REPORT).write_text(f"""# THRONE ORGAN MATURITY CROWN GATE MATRIX REPORT V0.1\n\ntask_id: `{TASK_ID}`  \nvalidator_id: `{VALIDATOR_ID}`  \nverdict: `{verdict}`  \ngenerated_at_utc: `{generated}`\n\n## Meaning\n\nThrone receives a universal crown gate matrix that blocks local organ maturity from becoming false global readiness.\n\n## Checks\n\n{checks_md}\n\n## Errors\n\n{errors_md}\n""", encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"errors":errors,"warnings":warnings}, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1
if __name__=="__main__": raise SystemExit(main())
