#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse, datetime as dt, json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "IMPERIUM-APP-UI-REFERENCE-TARGET-CONTRACT-AND-FIDELITY-GATE-0001"
VALIDATOR_ID = "mechanicus_ui_reference_target_contract_and_fidelity_gate_validator.v0_1"
CONTRACT = Path("SUPPORT/APP_TAURI/contracts/IMPERIUM_APP_UI_REFERENCE_TARGET_CONTRACT_V0_1.json")
FIDELITY_MATRIX = Path("ORGANS/MECHANICUS/MATRICES/IMPERIUM_APP_UI_REFERENCE_FIDELITY_GATE_MATRIX_V0_1.json")
CUSTODES_MATRIX = Path("ORGANS/CUSTODES/MATRICES/CUSTODES_UI_REFERENCE_PROSECUTOR_MATRIX_V0_1.json")
THRONE_MATRIX = Path("ORGANS/THRONE/MATRICES/THRONE_UI_REFERENCE_CROWN_GATE_MATRIX_V0_1.json")
RECEIPT = Path("ORGANS/MECHANICUS/RECEIPTS/imperium_app_ui_reference_target_contract_and_fidelity_gate_receipt.json")
SUMMARY = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_REFERENCE_TARGET_CONTRACT_AND_FIDELITY_GATE_SUMMARY_V0_1.json")
REPORT = Path("ORGANS/MECHANICUS/REPORTS/IMPERIUM_APP_UI_REFERENCE_TARGET_CONTRACT_AND_FIDELITY_GATE_REPORT_V0_1.md")

def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def load_json(path: Path):
    try: return json.loads(path.read_text(encoding="utf-8-sig")), None
    except Exception as e: return None, str(e)
def write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})
def has_all(text: str, needles: List[str]) -> bool: return all(n in text for n in needles)

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--repo-root", default="."); ap.add_argument("--apply", action="store_true")
    repo = Path(ap.parse_args().repo_root).resolve()
    checks=[]; errors=[]; warnings=[]
    contract, contract_err = load_json(repo/CONTRACT) if (repo/CONTRACT).is_file() else ({}, "missing")
    contract_text = json.dumps(contract, ensure_ascii=False) if isinstance(contract, dict) else ""
    contract_ok = contract_err is None and contract.get("contract_id")=="IMPERIUM_APP_UI_REFERENCE_TARGET_CONTRACT_V0_1" and has_all(contract_text,["Build proof is not target proof","FPS proof is not reference fidelity proof","UX proof is not backend execution proof","External outsource candidates are evidence, not canonical implementation","OWNER_ACCEPTED_REFERENCE_FORM"])
    add(checks,"reference_target_contract_exists_and_declares_no_fake_visual_green",contract_ok,{"path":CONTRACT.as_posix(),"error":contract_err})
    if not contract_ok: errors.append("reference target contract missing or incomplete")
    forbidden = contract.get("forbidden_claims_without_owner_acceptance",[]) if isinstance(contract,dict) else []
    forbidden_ok = all(x in forbidden for x in ["UI final","reference achieved","AAA complete","target form complete"])
    add(checks,"contract_forbids_final_ui_claims_without_owner_acceptance",forbidden_ok,{"forbidden":forbidden})
    if not forbidden_ok: errors.append("contract does not forbid visual final claims strongly enough")
    matrix, matrix_err = load_json(repo/FIDELITY_MATRIX) if (repo/FIDELITY_MATRIX).is_file() else ({}, "missing")
    dims = matrix.get("dimensions",[]) if isinstance(matrix,dict) else []
    weights_sum=sum(int(d.get("weight",0)) for d in dims if isinstance(d,dict))
    required={"layout_hierarchy","readability","deduplication","operational_law_anchor","heartbeat_telemetry","gothic_metal_material","trash_polka_restraint","ux_action_proof","truth_boundary"}
    ids={d.get("id") for d in dims if isinstance(d,dict)}
    matrix_ok=matrix_err is None and weights_sum==100 and required.issubset(ids)
    add(checks,"fidelity_gate_matrix_exists_weights_sum_to_100_and_covers_target_dimensions",matrix_ok,{"path":FIDELITY_MATRIX.as_posix(),"error":matrix_err,"weights_sum":weights_sum,"missing_dimensions":sorted(required-ids)})
    if not matrix_ok: errors.append("fidelity matrix missing, incomplete, or weights do not sum to 100")
    blockers=matrix.get("critical_blockers",[]) if isinstance(matrix,dict) else []
    blocker_ok=all(x in blockers for x in ["reference target claimed from build/FPS alone","final UI claimed without Owner acceptance","external candidate marked canonical without WARP"])
    add(checks,"fidelity_matrix_blocks_build_fps_to_reference_pollution",blocker_ok,{"critical_blockers":blockers})
    if not blocker_ok: errors.append("fidelity matrix does not block build/FPS-to-reference pollution")
    custodes,cerr=load_json(repo/CUSTODES_MATRIX) if (repo/CUSTODES_MATRIX).is_file() else ({}, "missing")
    ctext=json.dumps(custodes,ensure_ascii=False) if isinstance(custodes,dict) else ""
    cok=cerr is None and "prosecutor_not_helper" in ctext and "build_proof_treated_as_visual_proof" in ctext
    add(checks,"custodes_ui_reference_prosecutor_matrix_exists",cok,{"path":CUSTODES_MATRIX.as_posix(),"error":cerr})
    if not cok: errors.append("Custodes UI reference prosecutor matrix missing or weak")
    throne,terr=load_json(repo/THRONE_MATRIX) if (repo/THRONE_MATRIX).is_file() else ({}, "missing")
    ttext=json.dumps(throne,ensure_ascii=False) if isinstance(throne,dict) else ""
    tok=terr is None and "Local visual candidate cannot become global UI truth" in ttext and "No UI polish may be closed as complete without Owner accepted reference form" in ttext
    add(checks,"throne_ui_reference_crown_gate_matrix_exists",tok,{"path":THRONE_MATRIX.as_posix(),"error":terr})
    if not tok: errors.append("Throne UI reference crown gate matrix missing or weak")
    verdict="PASS_IMPERIUM_APP_UI_REFERENCE_TARGET_CONTRACT_AND_FIDELITY_GATE_READY" if not errors else "FAIL_IMPERIUM_APP_UI_REFERENCE_TARGET_CONTRACT_AND_FIDELITY_GATE"
    generated=utc()
    summary={"summary_id":"mechanicus.imperium_app_ui_reference_target_contract_and_fidelity_gate_summary.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"checks":checks,"errors":errors,"warnings":warnings,"meaning":"Locks the UI reference target and prevents build/FPS proof from being treated as visual target completion."}
    receipt={"receipt_id":"receipt.mechanicus.imperium_app_ui_reference_target_contract_and_fidelity_gate.v0_1","task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"generated_at_utc":generated,"checks":checks,"errors":errors,"warnings":warnings,"contract":CONTRACT.as_posix(),"fidelity_matrix":FIDELITY_MATRIX.as_posix(),"custodes_matrix":CUSTODES_MATRIX.as_posix(),"throne_matrix":THRONE_MATRIX.as_posix()}
    write_json(repo/SUMMARY,summary); write_json(repo/RECEIPT,receipt)
    checks_md="\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md="\n".join(f"- {e}" for e in errors) if errors else "- none"
    warnings_md="\n".join(f"- {w}" for w in warnings) if warnings else "- none"
    (repo/REPORT).write_text(f"""# IMPERIUM APP UI REFERENCE TARGET CONTRACT AND FIDELITY GATE REPORT V0.1

task_id: `{TASK_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{verdict}`  
generated_at_utc: `{generated}`

## Meaning

This patch does not change the UI. It locks the target and the evaluation law for future UI work.

The UI is not complete until Owner accepts the reference form. Build, FPS, HTTP 200, and npm/cargo proof are lower gates only.

## New law

```text
Build proof is not target proof.
FPS proof is not reference fidelity proof.
UX proof is not backend execution proof.
External outsource candidates are evidence, not canonical implementation.
```

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}
""", encoding="utf-8")
    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"receipt":RECEIPT.as_posix(),"summary":SUMMARY.as_posix(),"errors":errors,"warnings":warnings}, ensure_ascii=False, indent=2))
    return 0 if verdict.startswith("PASS") else 1
if __name__=="__main__": raise SystemExit(main())
