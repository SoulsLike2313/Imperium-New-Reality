#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, datetime as dt, hashlib, json
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "THRONE-KERNEL-ANATOMY-AND-CORE-V1-TARGET-0001"
VALIDATOR_ID = "throne_kernel_anatomy_validator.v0_1"
THRONE = Path("ORGANS/THRONE")
MATRIX_DIR = THRONE / "MATRICES"
DOC = THRONE / "SELF_KNOWLEDGE/CORE_V1_TARGET.md"
RECEIPT = THRONE / "RECEIPTS/throne_kernel_anatomy_receipt.json"
REPORT = THRONE / "REPORTS/THRONE_KERNEL_ANATOMY_REPORT_V0_1.md"

REQUIRED = {
 "THRONE_KERNEL_ANATOMY_MATRIX_V0_1.json":["kernel_identity","organ_kernel_roles","external_kernel_lessons","non_goals"],
 "THRONE_CORE_V1_DEFINITION_MATRIX_V0_1.json":["oath","must_capabilities","v1_gate","benchmark_policy"],
 "THRONE_KERNEL_BOUNDARY_MATRIX_V0_1.json":["zones","allowed_returns","forbidden_mutations","proof_requirements"],
 "THRONE_REQUEST_PACKET_MATRIX_V0_1.json":["packet_types","task_pack_required_fields","patch_pack_required_fields","routing_rules"],
 "THRONE_OBJECT_REGISTRY_MATRIX_V0_1.json":["registered_object_classes","required_fields","registry_owner"],
 "THRONE_ORGAN_SERVICE_STACK_MATRIX_V0_1.json":["default_task_stack","default_patch_stack","stack_law"],
 "THRONE_SERVITOR_EXECUTION_BOUNDARY_MATRIX_V0_1.json":["servitor_identity","allowed","forbidden","stop_conditions"],
 "THRONE_EVIDENCE_CHAIN_MATRIX_V0_1.json":["chain","minimum_evidence","fake_green_guards"],
 "THRONE_TRUST_BOUNDARY_MATRIX_V0_1.json":["trust_layers","required_questions","verdict_rules"],
 "THRONE_INTEGRATION_KERNEL_MATRIX_V0_1.json":["integration_states","admission_path","kernel_rights_rule"],
 "THRONE_HUMAN_READABILITY_MATRIX_V0_1.json":["tui_v1_must","human_translation_fields","non_goals"],
 "THRONE_CORE_V1_READINESS_SCORING_MATRIX_V0_1.json":["dimensions","v1_gate_logic"],
}

CONCEPTS = [
 "validated_hybrid_meta_kernel","TASK_PACK","PATCH_PACK","no_core_mutation","servitor",
 "evidence","trust","throne_verdict","human_readability","benchmark_deferred",
 "great_nine_required_before_benchmark"
]

def utc(): return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024), b""): h.update(c)
    return h.hexdigest()
def read_json(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def add(checks, name, ok, details=None): checks.append({"name":name,"status":"PASS" if ok else "FAIL","details":details or {}})
def flat(x: Any) -> str:
    out=[]
    def w(v):
        if isinstance(v, dict):
            for k,val in v.items(): out.append(str(k)); w(val)
        elif isinstance(v, list):
            for i in v: w(i)
        elif v is not None: out.append(str(v))
    w(x); return "\n".join(out)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()

    checks=[]; errors=[]; matrices={}; hashes={}
    missing=[]; malformed=[]; section_errors=[]

    for fname, sections in REQUIRED.items():
        p = root / MATRIX_DIR / fname
        if not p.is_file():
            missing.append(str(MATRIX_DIR/fname)); continue
        try:
            data = read_json(p); matrices[fname]=data; hashes[str(MATRIX_DIR/fname)] = sha(p)
            for s in sections:
                if s not in data: section_errors.append(f"{fname} missing section {s}")
        except Exception as e:
            malformed.append(f"{fname}: {e}")

    add(checks,"required_matrices_exist", not missing, {"missing": missing})
    add(checks,"required_matrices_parse_json", not malformed, {"malformed": malformed})
    add(checks,"required_matrix_sections_present", not section_errors, {"section_errors": section_errors})
    errors += [f"Missing matrix: {x}" for x in missing] + [f"Malformed matrix: {x}" for x in malformed] + section_errors

    doc_path = root / DOC
    doc_ok = doc_path.is_file() and len(doc_path.read_text(encoding="utf-8", errors="replace").strip()) > 200
    add(checks,"core_v1_self_knowledge_doc_exists", doc_ok, {"path": str(DOC)})
    if not doc_ok: errors.append("CORE_V1_TARGET.md missing or too small")

    all_text = "\n".join(flat(m) for m in matrices.values()).lower()
    concept_presence={}
    for c in CONCEPTS:
        ok = c.lower() in all_text
        concept_presence[c]=ok
        if not ok: errors.append(f"Required concept missing: {c}")
    add(checks,"required_concepts_present", all(concept_presence.values()), concept_presence)

    core_def = matrices.get("THRONE_CORE_V1_DEFINITION_MATRIX_V0_1.json", {})
    v1_gate = core_def.get("v1_gate", {}) if isinstance(core_def, dict) else {}
    bp = core_def.get("benchmark_policy", {}) if isinstance(core_def, dict) else {}
    benchmark_deferred = bool(v1_gate.get("benchmark_not_now")) and "DEFERRED" in str(bp.get("status","")).upper()
    add(checks,"benchmark_explicitly_deferred_until_ready", benchmark_deferred, {"v1_gate": v1_gate, "benchmark_policy": bp})
    if not benchmark_deferred: errors.append("Benchmark deferral is not explicit enough")

    boundary = matrices.get("THRONE_KERNEL_BOUNDARY_MATRIX_V0_1.json", {})
    no_core = bool(boundary.get("allowed_returns")) and bool(boundary.get("forbidden_mutations"))
    add(checks,"no_core_mutation_boundary_defined", no_core, {})
    if not no_core: errors.append("No-core-mutation boundary incomplete")

    tui = matrices.get("THRONE_HUMAN_READABILITY_MATRIX_V0_1.json", {}).get("tui_v1_must", [])
    required_tui = ["task_list","task_lifecycle_status","current_organ_or_stage","pass_fail_criteria","fix_loop_state","receipts","export_zip","context_compression","throne_warning_block_panel"]
    missing_tui = [x for x in required_tui if x not in tui]
    add(checks,"tui_v1_minimum_present", not missing_tui, {"missing_tui": missing_tui})
    if missing_tui: errors.append(f"TUI v1 minimum missing: {missing_tui}")

    servitor = matrices.get("THRONE_SERVITOR_EXECUTION_BOUNDARY_MATRIX_V0_1.json", {}).get("servitor_identity", {})
    task_only = "TASK_PACK" in str(servitor.get("works_only_from","")).upper()
    add(checks,"servitor_bound_to_task_pack", task_only, {"servitor_identity": servitor})
    if not task_only: errors.append("Servitor is not explicitly bound to TASK_PACK")

    verdict = "PASS_TARGET_DEFINED" if not errors else "FAIL_TARGET_INCOMPLETE"
    receipt = {
      "receipt_id":"receipt.throne_kernel_anatomy.v0_1",
      "task_id":TASK_ID,
      "validator_id":VALIDATOR_ID,
      "verdict":verdict,
      "generated_at_utc":utc(),
      "mode":"MEASURE_ONLY",
      "matrices_checked":list(REQUIRED.keys()),
      "matrix_hashes_sha256":hashes,
      "checks":checks,
      "errors":errors,
      "meaning":"PASS_TARGET_DEFINED means Core v1 target anatomy is defined enough for later deeper validators; it does not mean Core v1 is achieved."
    }

    (root/RECEIPT).parent.mkdir(parents=True, exist_ok=True)
    (root/REPORT).parent.mkdir(parents=True, exist_ok=True)
    (root/RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in checks)
    errors_md = "\n".join(f"- {e}" for e in errors) if errors else "- none"
    report = f"""# THRONE KERNEL ANATOMY REPORT V0.1

task_id: `{TASK_ID}`
validator_id: `{VALIDATOR_ID}`
verdict: `{verdict}`
generated_at_utc: `{receipt['generated_at_utc']}`

## Meaning

This report fixes the next layer of Throne knowledge: what makes Imperium Core v1 a working hybrid meta-kernel.

It does not claim Core v1 is achieved.

## Matrices checked

{chr(10).join('- `' + x + '`' for x in REQUIRED.keys())}

## Checks

{checks_md}

## Errors

{errors_md}

## Receipt

`{RECEIPT.as_posix()}`
"""
    (root/REPORT).write_text(report, encoding="utf-8")

    print(json.dumps({"task_id":TASK_ID,"validator_id":VALIDATOR_ID,"verdict":verdict,"receipt":RECEIPT.as_posix(),"report":REPORT.as_posix(),"errors":errors}, ensure_ascii=False, indent=2))
    return 0 if verdict == "PASS_TARGET_DEFINED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
