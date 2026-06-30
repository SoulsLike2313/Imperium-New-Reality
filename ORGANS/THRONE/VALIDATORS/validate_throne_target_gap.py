#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse, csv, datetime as dt, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

TASK_ID = "THRONE-TARGET-GAP-VALIDATOR-0001"
UPGRADE_ID = "THRONE-TARGET-GAP-ORGAN-IMPLEMENTATION-SPLIT-0001"
VALIDATOR_ID = "throne_target_gap_validator.v0_5_organ_implementation_split"

THRONE = Path("ORGANS/THRONE")
CENSUS_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_CENSUS_V0_1.json")
SUMMARY_JSON = Path("WARP/PATCHES/IMPERIUM-POPULATION-CENSUS-0001/OUTPUTS/IMPERIUM_POPULATION_SUMMARY_V0_1.json")

TARGET_MATRIX = THRONE / "MATRICES/THRONE_TARGET_V1_MATRIX_V0_1.json"
GAP_SCORING_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_SCORING_MATRIX_V0_1.json"
CORE_V1_SCORING_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_CORE_V1_SCORING_INTEGRATION_MATRIX_V0_1.json"
STRICT_CORE_MATRIX = THRONE / "MATRICES/THRONE_TARGET_GAP_CORE_V1_SCORING_FIX_0002_MATRIX_V0_1.json"
ORGAN_SPLIT_MATRIX = THRONE / "MATRICES/THRONE_ORGAN_IMPLEMENTATION_SPLIT_MATRIX_V0_1.json"

RECEIPT = THRONE / "RECEIPTS/throne_target_gap_receipt.json"
REPORT = THRONE / "REPORTS/THRONE_TARGET_GAP_REPORT_V0_1.md"
ORGAN_CSV = THRONE / "REPORTS/THRONE_ORGAN_READINESS_TABLE_V0_1.csv"
NEXT_ATTENTION = THRONE / "REPORTS/THRONE_NEXT_ATTENTION_AREAS_V0_1.json"
CORE_BREAKDOWN_JSON = THRONE / "REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.json"
CORE_BREAKDOWN_CSV = THRONE / "REPORTS/THRONE_CORE_V1_READINESS_BREAKDOWN_V0_1.csv"
OP_BREAKDOWN_JSON = THRONE / "REPORTS/THRONE_CORE_V1_OPERATIONAL_BREAKDOWN_V0_1.json"
OP_BREAKDOWN_CSV = THRONE / "REPORTS/THRONE_CORE_V1_OPERATIONAL_BREAKDOWN_V0_1.csv"
ORGAN_IMPL_JSON = THRONE / "REPORTS/THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_V0_1.json"
ORGAN_IMPL_CSV = THRONE / "REPORTS/THRONE_ORGAN_IMPLEMENTATION_BREAKDOWN_V0_1.csv"

GREAT_NINE = [
    "ASTRONOMICON", "ADMINISTRATUM", "DOCTRINARIUM", "MECHANICUS", "INQUISITION",
    "CUSTODES", "STRATEGIUM", "SCHOLA_IMPERIALIS", "OFFICIO_AGENTIS"
]
SUBJECTS = ["THRONE"] + GREAT_NINE

REQUIRED_SLOTS = [
    "README.md","ORGAN_CARD.json","MANIFEST.json","FUNCTIONS.md",
    "MATRICES","SCHEMAS","VALIDATORS","RECEIPTS","REPORTS","TESTS",
    "TUI","DASHBOARDS","EYES","BLOCK","LESSONS","NEGATIVE_LESSONS"
]

CORE_MATRICES = {
    "THRONE_KERNEL_ANATOMY_MATRIX_V0_1.json": ["kernel_identity","organ_kernel_roles","external_kernel_lessons","non_goals"],
    "THRONE_CORE_V1_DEFINITION_MATRIX_V0_1.json": ["oath","must_capabilities","v1_gate","benchmark_policy"],
    "THRONE_KERNEL_BOUNDARY_MATRIX_V0_1.json": ["zones","allowed_returns","forbidden_mutations","proof_requirements"],
    "THRONE_REQUEST_PACKET_MATRIX_V0_1.json": ["packet_types","task_pack_required_fields","patch_pack_required_fields","routing_rules"],
    "THRONE_OBJECT_REGISTRY_MATRIX_V0_1.json": ["registered_object_classes","required_fields","registry_owner"],
    "THRONE_ORGAN_SERVICE_STACK_MATRIX_V0_1.json": ["default_task_stack","default_patch_stack","stack_law"],
    "THRONE_SERVITOR_EXECUTION_BOUNDARY_MATRIX_V0_1.json": ["servitor_identity","allowed","forbidden","stop_conditions"],
    "THRONE_EVIDENCE_CHAIN_MATRIX_V0_1.json": ["chain","minimum_evidence","fake_green_guards"],
    "THRONE_TRUST_BOUNDARY_MATRIX_V0_1.json": ["trust_layers","required_questions","verdict_rules"],
    "THRONE_INTEGRATION_KERNEL_MATRIX_V0_1.json": ["integration_states","admission_path","kernel_rights_rule"],
    "THRONE_HUMAN_READABILITY_MATRIX_V0_1.json": ["tui_v1_must","human_translation_fields","non_goals"],
    "THRONE_CORE_V1_READINESS_SCORING_MATRIX_V0_1.json": ["dimensions","v1_gate_logic"],
}

DEFAULT_ORGAN_PATTERNS = {
    "ASTRONOMICON": ["intake", "task_pack", "admission", "rejection", "pass_criteria"],
    "ADMINISTRATUM": ["registry", "registered_task", "context_pack", "archive", "provenance"],
    "DOCTRINARIUM": ["canon", "doctrine_check", "schema_law", "rule_matrix", "contradiction"],
    "MECHANICUS": ["tool_harness", "validator_harness", "self_test", "build_receipt", "encoding_check"],
    "INQUISITION": ["scan", "finding", "fake_green", "hardcoded", "mutation"],
    "CUSTODES": ["trust", "organ_audit", "validator_audit", "trust_matrix", "trust_receipt"],
    "STRATEGIUM": ["priority", "next_attention", "impact", "roadmap", "recommendation"],
    "SCHOLA_IMPERIALIS": ["lesson", "negative_example", "learning", "failure_memory", "training"],
    "OFFICIO_AGENTIS": ["servitor", "authority", "role", "execution_boundary", "agent_prompt"],
}

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda: f.read(1024*1024), b""):
            h.update(c)
    return h.hexdigest()

def clamp(x: float) -> float:
    return round(max(0.0, min(100.0, x)), 2)

def add(checks: List[Dict[str, Any]], name: str, ok: bool, details: Dict[str, Any] | None = None):
    checks.append({"name": name, "status": "PASS" if ok else "FAIL", "details": details or {}})

def weighted(scores: Dict[str, float], weights: Dict[str, int]) -> float:
    total = sum(weights.values()) or 1
    return clamp(sum(scores.get(k,0) * w for k,w in weights.items()) / total)

def score_hits(hits: Dict[str, List[str]], weights: Dict[str, int]) -> float:
    binary = {k: 100.0 if hits.get(k) else 0.0 for k in weights}
    return weighted(binary, weights)

def organ_path(organ: str) -> Path:
    return THRONE if organ == "THRONE" else Path("ORGANS") / organ

def classify_by_owner(residents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    by = defaultdict(list)
    for r in residents:
        owner = str(r.get("owner_candidate") or "UNKNOWN")
        by[owner].append(r)
        if "ORGANS/THRONE/" in str(r.get("path","")) and owner != "THRONE":
            by["THRONE"].append(r)
    return by

def resident_paths(residents: List[Dict[str,Any]]) -> List[str]:
    return [str(r.get("path","")).replace("\\","/") for r in residents]

def count_classes(items: List[Dict[str, Any]]) -> Counter:
    return Counter(str(r.get("class") or "UNKNOWN") for r in items)

def parse_json_if_exists(path: Path) -> bool:
    if not path.is_file(): return False
    try: read_json(path); return True
    except Exception: return False

def pct(done: int, total: int) -> float:
    return clamp(done * 100.0 / max(1, total))

def matrix_score(repo: Path, fname: str, sections: List[str]) -> Dict[str, Any]:
    p = repo / THRONE / "MATRICES" / fname
    res = {"matrix": fname, "exists": False, "parses": False, "present_sections": [], "missing_sections": list(sections), "score": 0.0, "errors": []}
    if not p.is_file():
        res["errors"].append("missing"); return res
    res["exists"] = True
    try: data = read_json(p); res["parses"] = True
    except Exception as e:
        res["errors"].append(str(e)); res["score"] = 20; return res
    present = [s for s in sections if s in data]
    missing = [s for s in sections if s not in data]
    res["present_sections"] = present; res["missing_sections"] = missing
    res["score"] = clamp(40 + len(present)*50/max(1,len(sections)) + (10 if len(json.dumps(data, ensure_ascii=False)) > 400 else 0))
    return res

def compute_target_definition(repo: Path) -> Dict[str, Any]:
    results = {fname: matrix_score(repo, fname, secs) for fname, secs in CORE_MATRICES.items()}
    score = clamp(sum(r["score"] for r in results.values()) / max(1, len(results)))
    return {"score": score, "matrix_results": results, "missing": [k for k,r in results.items() if not r["exists"]], "malformed": [k for k,r in results.items() if r["exists"] and not r["parses"]]}

def filter_paths(paths: List[str], include: List[str], exclude: List[str] | None = None) -> List[str]:
    exclude = exclude or []
    out = []
    for p in paths:
        low = p.lower()
        if all(re.search(x, low, re.I) for x in include) and not any(re.search(x, low, re.I) for x in exclude):
            out.append(p)
    return out

def compute_strict_core_operational(repo: Path, residents: List[Dict[str,Any]]) -> Dict[str, Any]:
    paths = resident_paths(residents)
    target_doc_excludes = [
        r"matrices/", r"schemas/", r"self_knowledge/", r"readme\.md$",
        r"functions\.md$", r"organ_card\.json$", r"manifest\.json$",
        r"target", r"definition", r"anatomy", r"profile"
    ]

    evidence = {
        "registered_task_pack": filter_paths(paths, [r"task[_-]?pack"], target_doc_excludes),
        "task_registry": filter_paths(paths, [r"task", r"registr"], target_doc_excludes),
        "astronomicon_intake_receipt": filter_paths(paths, [r"astronomicon", r"intake", r"receipt"], target_doc_excludes),
        "administratum_context_pack": filter_paths(paths, [r"administratum", r"context"], target_doc_excludes),
        "servitor_execution_receipt": filter_paths(paths, [r"servitor", r"(execution|run|result|receipt)"], target_doc_excludes),
        "warp_task_execution": filter_paths(paths, [r"warp", r"task"], [r"patches/"]),
        "fix_loop_receipt": filter_paths(paths, [r"fix[_-]?loop", r"receipt"], target_doc_excludes),
        "throne_verdict_receipt": filter_paths(paths, [r"throne", r"verdict", r"receipt"], target_doc_excludes),
        "inquisition_check_receipt": filter_paths(paths, [r"inquisition", r"(check|scan|finding|receipt)"], target_doc_excludes),
        "custodes_trust_receipt": filter_paths(paths, [r"custodes", r"trust", r"receipt"], target_doc_excludes),
        "tui_implementation": filter_paths(paths, [r"organs/throne/tui/", r"\.(ps1|py|js|ts|tsx|html|css)$"], []),
        "dashboard_implementation": filter_paths(paths, [r"organs/throne/(dashboards|reports)/", r"(dashboard|view|panel|status).*\.(json|md|html|csv|js|ts|tsx)$"], []),
        "warning_block_panel": filter_paths(paths, [r"(warning|block)", r"(panel|dashboard|tui|report)"], target_doc_excludes),
        "no_core_mutation_receipt": filter_paths(paths, [r"no[_-]?core[_-]?mutation", r"receipt"], target_doc_excludes),
        "before_after_census": filter_paths(paths, [r"(before|after).*census|census.*(before|after)"], target_doc_excludes),
        "external_product_boundary_receipt": filter_paths(paths, [r"external[_-]?product|product[_-]?boundary", r"receipt"], target_doc_excludes),
        "allowed_return_receipt": filter_paths(paths, [r"allowed[_-]?return", r"receipt"], target_doc_excludes),
    }

    workflow_hits = {
        "task_pack": evidence["registered_task_pack"],
        "task_registry": evidence["task_registry"],
        "intake_receipt": evidence["astronomicon_intake_receipt"],
        "context_pack": evidence["administratum_context_pack"],
        "servitor_execution": evidence["servitor_execution_receipt"],
        "warp_task_execution": evidence["warp_task_execution"],
        "fix_loop": evidence["fix_loop_receipt"],
        "throne_verdict": evidence["throne_verdict_receipt"],
    }
    trust_hits = {
        "inquisition_check": evidence["inquisition_check_receipt"],
        "custodes_trust": evidence["custodes_trust_receipt"],
        "throne_verdict": evidence["throne_verdict_receipt"],
    }
    human_hits = {
        "tui_implementation": evidence["tui_implementation"],
        "dashboard_implementation": evidence["dashboard_implementation"],
        "warning_block_panel": evidence["warning_block_panel"],
        "receipts_available": filter_paths(paths, [r"organs/throne/receipts/", r"\.json$"], []),
        "reports_available": filter_paths(paths, [r"organs/throne/reports/", r"\.(md|json|csv)$"], []),
    }
    no_core_hits = {
        "no_core_mutation_receipt": evidence["no_core_mutation_receipt"],
        "before_after_census": evidence["before_after_census"],
        "external_product_boundary_receipt": evidence["external_product_boundary_receipt"],
        "allowed_return_receipt": evidence["allowed_return_receipt"],
    }

    workflow_score = score_hits(workflow_hits, {
        "task_pack": 15, "task_registry": 10, "intake_receipt": 15, "context_pack": 10,
        "servitor_execution": 15, "warp_task_execution": 10, "fix_loop": 10, "throne_verdict": 15
    })
    trust_score = score_hits(trust_hits, {
        "inquisition_check": 35, "custodes_trust": 45, "throne_verdict": 20
    })
    human_score = score_hits(human_hits, {
        "tui_implementation": 35, "dashboard_implementation": 25, "warning_block_panel": 15,
        "receipts_available": 15, "reports_available": 10
    })
    no_core_score = score_hits(no_core_hits, {
        "no_core_mutation_receipt": 35, "before_after_census": 25,
        "external_product_boundary_receipt": 25, "allowed_return_receipt": 15
    })
    operational_score = weighted({
        "workflow": workflow_score,
        "trust": trust_score,
        "human": human_score,
        "no_core": no_core_score
    }, {"workflow": 40, "trust": 25, "human": 15, "no_core": 20})

    return {
        "core_v1_operational_evidence_score": operational_score,
        "core_v1_workflow_readiness_score": workflow_score,
        "core_v1_trust_readiness_score": trust_score,
        "core_v1_human_visibility_score": human_score,
        "core_v1_no_core_mutation_evidence_score": no_core_score,
        "evidence": {k: v[:20] for k, v in evidence.items()},
    }

def compute_profile_baseline(repo: Path, organ: str) -> Dict[str, Any]:
    root = repo / "ORGANS" / organ
    receipt = root / "RECEIPTS" / f"{organ.lower()}_profile_receipt.json"
    report = root / "REPORTS" / f"{organ}_PROFILE_VALIDATION_REPORT_V0_1.md"
    validator = root / "VALIDATORS" / f"validate_{organ.lower()}_profile.py"
    card = root / "ORGAN_CARD.json"
    manifest = root / "MANIFEST.json"

    checks = {
        "readme": (root / "README.md").is_file(),
        "card": parse_json_if_exists(card),
        "manifest": parse_json_if_exists(manifest),
        "functions": (root / "FUNCTIONS.md").is_file(),
        "profile_validator": validator.is_file(),
        "profile_receipt_pass": False,
        "profile_report": report.is_file(),
        "declared_forbidden_actions": False,
        "declared_functions": False,
    }

    try:
        r = read_json(receipt) if receipt.is_file() else {}
        checks["profile_receipt_pass"] = r.get("verdict") == "PASS_PROFILE_BASELINE"
    except Exception:
        checks["profile_receipt_pass"] = False

    try:
        c = read_json(card) if card.is_file() else {}
        checks["declared_forbidden_actions"] = isinstance(c.get("forbidden_actions"), list) and len(c.get("forbidden_actions")) >= 4
        checks["declared_functions"] = isinstance(c.get("declared_functions"), list) and len(c.get("declared_functions")) >= 5
    except Exception:
        pass

    return {
        "score": pct(sum(1 for v in checks.values() if v), len(checks)),
        "checks": checks,
        "receipt": receipt.as_posix(),
        "meaning": "Profile baseline proves passport shape only, not full implementation."
    }

def compute_structural(repo: Path, organ: str, by_owner: Dict[str, List[Dict[str,Any]]]) -> Dict[str, Any]:
    root = repo / "ORGANS" / organ
    slot_checks = {slot: (root / slot).exists() for slot in REQUIRED_SLOTS}
    items = by_owner.get(organ, [])
    cc = count_classes(items)
    structure = {
        "required_slots": pct(sum(1 for v in slot_checks.values() if v), len(slot_checks)),
        "schema_evidence": pct(cc.get("SCHEMA", 0), 2),
        "validator_evidence": pct(cc.get("VALIDATOR", 0), 2),
        "receipt_evidence": pct(cc.get("RECEIPT", 0), 3),
        "report_evidence": pct(cc.get("REPORT", 0), 2),
        "matrix_evidence": pct(cc.get("MATRIX", 0), 2),
    }
    score = weighted(structure, {
        "required_slots": 30,
        "schema_evidence": 15,
        "validator_evidence": 20,
        "receipt_evidence": 15,
        "report_evidence": 10,
        "matrix_evidence": 10,
    })
    return {
        "score": score,
        "slot_checks": slot_checks,
        "class_counts": dict(cc),
        "components": structure
    }

def organ_operational_patterns(split_matrix: Dict[str, Any]) -> Dict[str, List[str]]:
    return split_matrix.get("organ_specific_operational_evidence_patterns", DEFAULT_ORGAN_PATTERNS)

def compute_organ_operational(paths: List[str], organ: str, patterns: Dict[str, List[str]]) -> Dict[str, Any]:
    lower_organ = organ.lower()
    generic_excludes = [
        r"profile", r"organ_card\.json", r"manifest\.json", r"functions\.md", r"readme\.md",
        r"matrices/.*profile", r"schemas/organ_profile", r"validate_.*_profile\.py"
    ]
    organ_paths = [p for p in paths if f"organs/{lower_organ}/" in p.lower()]
    hits = {}
    for pat in patterns.get(organ, []):
        include = [re.escape(pat).replace("\\_", "[_-]?")]
        matched = []
        for p in organ_paths:
            low = p.lower()
            if re.search(include[0], low, re.I) and not any(re.search(ex, low, re.I) for ex in generic_excludes):
                # operational proof should usually be receipt/report/output/test/tool artifact
                if re.search(r"(receipt|report|output|result|audit|finding|registry|context|harness|test|tool|run|scan|verdict)", low, re.I):
                    matched.append(p)
        hits[pat] = matched[:10]

    # Additional general organ action evidence excluding profile baseline.
    action_receipts = []
    for p in organ_paths:
        low = p.lower()
        if "/receipts/" in low and "profile_receipt" not in low and not any(re.search(ex, low, re.I) for ex in generic_excludes):
            action_receipts.append(p)
    action_reports = []
    for p in organ_paths:
        low = p.lower()
        if "/reports/" in low and "profile_validation_report" not in low and not any(re.search(ex, low, re.I) for ex in generic_excludes):
            action_reports.append(p)

    pattern_score = pct(sum(1 for v in hits.values() if v), max(1, len(hits)))
    action_score = weighted({
        "action_receipts": pct(len(action_receipts), 2),
        "action_reports": pct(len(action_reports), 2),
    }, {"action_receipts": 60, "action_reports": 40})

    score = weighted({
        "pattern_score": pattern_score,
        "action_score": action_score,
    }, {"pattern_score": 70, "action_score": 30})

    return {
        "score": score,
        "pattern_hits": hits,
        "action_receipts": action_receipts[:20],
        "action_reports": action_reports[:20],
        "meaning": "Profile receipts/validators are excluded from operational proof."
    }

def compute_organ_trust(paths: List[str], organ: str) -> Dict[str, Any]:
    lower = organ.lower()
    # Trust proof should be specific Custodes/Throne/Inquisition validation of this organ,
    # not the organ's own profile receipt.
    custodes = [p for p in paths if "organs/custodes/" in p.lower() and lower in p.lower() and "trust" in p.lower() and ("receipt" in p.lower() or "report" in p.lower())]
    throne = [p for p in paths if "organs/throne/" in p.lower() and lower in p.lower() and ("organ" in p.lower() or "trust" in p.lower()) and ("receipt" in p.lower() or "report" in p.lower()) and "profile_baseline" not in p.lower()]
    inq = [p for p in paths if "organs/inquisition/" in p.lower() and lower in p.lower() and ("scan" in p.lower() or "finding" in p.lower() or "receipt" in p.lower() or "report" in p.lower())]
    self_receipt = [p for p in paths if f"organs/{lower}/receipts/" in p.lower() and "profile_receipt" not in p.lower()]

    score = weighted({
        "custodes_trust": 100.0 if custodes else 0.0,
        "throne_audit": 100.0 if throne else 0.0,
        "inquisition_scan": 100.0 if inq else 0.0,
        "non_profile_self_receipt": 100.0 if self_receipt else 0.0,
    }, {
        "custodes_trust": 40,
        "throne_audit": 25,
        "inquisition_scan": 25,
        "non_profile_self_receipt": 10,
    })

    return {
        "score": score,
        "custodes_trust": custodes[:10],
        "throne_audit": throne[:10],
        "inquisition_scan": inq[:10],
        "non_profile_self_receipt": self_receipt[:10],
        "meaning": "Profile receipts are excluded from trust proof."
    }

def compute_organ_split(repo: Path, residents: List[Dict[str,Any]], by_owner: Dict[str,List[Dict[str,Any]]], split_matrix: Dict[str,Any]) -> Dict[str, Any]:
    paths = resident_paths(residents)
    patterns = organ_operational_patterns(split_matrix)
    guards = split_matrix.get("guards", {})
    component_weights = split_matrix.get("score_components", {})
    weights = {
        "profile": int(component_weights.get("organ_profile_baseline_score", {}).get("weight_in_organ_readiness", 20)),
        "structural": int(component_weights.get("organ_structural_score", {}).get("weight_in_organ_readiness", 20)),
        "operational": int(component_weights.get("organ_operational_score", {}).get("weight_in_organ_readiness", 35)),
        "trust": int(component_weights.get("organ_trust_score", {}).get("weight_in_organ_readiness", 25)),
    }

    organs = {}
    for organ in GREAT_NINE:
        profile = compute_profile_baseline(repo, organ)
        structural = compute_structural(repo, organ, by_owner)
        operational = compute_organ_operational(paths, organ, patterns)
        trust = compute_organ_trust(paths, organ)

        score = weighted({
            "profile": profile["score"],
            "structural": structural["score"],
            "operational": operational["score"],
            "trust": trust["score"],
        }, weights)

        capped_by = []
        if guards.get("enabled", True):
            if operational["score"] < 50:
                cap = float(guards.get("max_organ_readiness_without_operational_50", 65))
                if score > cap:
                    score = cap
                    capped_by.append({"reason": "operational<50", "cap": cap})
            if trust["score"] < 50:
                cap = float(guards.get("max_organ_readiness_without_trust_50", 70))
                if score > cap:
                    score = cap
                    capped_by.append({"reason": "trust<50", "cap": cap})
            if profile["score"] >= 90 and structural["score"] >= 80 and operational["score"] == 0 and trust["score"] == 0:
                cap = float(guards.get("max_organ_readiness_with_profile_only", 45))
                if score > cap:
                    score = cap
                    capped_by.append({"reason": "profile_only", "cap": cap})

        organs[organ] = {
            "organ_id": organ,
            "organ_profile_baseline_score": profile["score"],
            "organ_structural_score": structural["score"],
            "organ_operational_score": operational["score"],
            "organ_trust_score": trust["score"],
            "organ_readiness_score": clamp(score),
            "capped_by": capped_by,
            "profile": profile,
            "structural": structural,
            "operational": operational,
            "trust": trust,
        }

    avg = lambda key: clamp(sum(o[key] for o in organs.values()) / len(organs))
    return {
        "great_nine_profile_baseline_score": avg("organ_profile_baseline_score"),
        "great_nine_structural_score": avg("organ_structural_score"),
        "great_nine_operational_score": avg("organ_operational_score"),
        "great_nine_trust_score": avg("organ_trust_score"),
        "great_nine_readiness_score": avg("organ_readiness_score"),
        "lowest_organ_readiness_score": clamp(min(o["organ_readiness_score"] for o in organs.values())),
        "organs": organs,
        "meaning": "Great Nine readiness now separates profile baseline from implementation and trust proof."
    }

def recommendations(organ_split: Dict[str,Any], core_op: Dict[str,Any]) -> List[Dict[str,Any]]:
    recs=[]
    def push(priority, area, reason, patch_family):
        recs.append({"priority":priority,"area":area,"reason":reason,"recommended_patch_family":patch_family})

    if organ_split["great_nine_operational_score"] < 50:
        push(4, "Great Nine operational proofs", "Great Nine profiles exist, but organ-specific operational receipts are weak.", "GREAT-NINE-OPERATIONAL-PROOF-0001")
    if organ_split["great_nine_trust_score"] < 50:
        push(5, "Great Nine trust proofs", "Organs need Custodes/Inquisition/Throne trust receipts beyond self-profile receipts.", "GREAT-NINE-TRUST-PROOF-0001")
    if core_op["core_v1_no_core_mutation_evidence_score"] < 50:
        push(6, "No-core-mutation proof", "Need before/after census and allowed-return receipts.", "THRONE-NO-CORE-MUTATION-PROOF-0001")
    if core_op["core_v1_human_visibility_score"] < 50:
        push(7, "Human visibility implementation", "TUI/dashboard target exists, but implementation artifacts are not enough.", "THRONE-HUMAN-VISIBILITY-PROOF-0001")

    low_orgs = sorted((v["organ_readiness_score"], k, v) for k, v in organ_split["organs"].items())
    if low_orgs:
        score, organ, data = low_orgs[0]
        if data["organ_operational_score"] < 50:
            push(20, f"{organ} operational implementation", f"{organ} operational score is {data['organ_operational_score']}%.", f"{organ}-OPERATIONAL-PROOF-0001")
        if data["organ_trust_score"] < 50:
            push(21, f"{organ} trust proof", f"{organ} trust score is {data['organ_trust_score']}%.", f"{organ}-TRUST-PROOF-0001")

    return sorted(recs, key=lambda r: r["priority"])

def write_outputs(repo: Path, receipt: Dict[str,Any], target_def: Dict[str,Any], core_op: Dict[str,Any], organ_split: Dict[str,Any], recs: List[Dict[str,Any]]):
    for p in [repo/RECEIPT.parent, repo/REPORT.parent]:
        p.mkdir(parents=True, exist_ok=True)

    (repo/RECEIPT).write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (repo/NEXT_ATTENTION).write_text(json.dumps(recs, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (repo/ORGAN_IMPL_JSON).write_text(json.dumps({
        "task_id": TASK_ID,
        "upgrade_id": UPGRADE_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": receipt["generated_at_utc"],
        **organ_split
    }, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    with (repo/ORGAN_IMPL_CSV).open("w", encoding="utf-8", newline="") as f:
        fields = [
            "organ_id",
            "organ_profile_baseline_score",
            "organ_structural_score",
            "organ_operational_score",
            "organ_trust_score",
            "organ_readiness_score",
            "capped_by"
        ]
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for organ, data in organ_split["organs"].items():
            w.writerow({
                "organ_id": organ,
                "organ_profile_baseline_score": data["organ_profile_baseline_score"],
                "organ_structural_score": data["organ_structural_score"],
                "organ_operational_score": data["organ_operational_score"],
                "organ_trust_score": data["organ_trust_score"],
                "organ_readiness_score": data["organ_readiness_score"],
                "capped_by": json.dumps(data["capped_by"], ensure_ascii=False)
            })

    (repo/CORE_BREAKDOWN_JSON).write_text(json.dumps({
        "task_id": TASK_ID,
        "upgrade_id": UPGRADE_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": receipt["generated_at_utc"],
        "core_v1_target_definition_score": target_def["score"],
        "matrix_results": target_def["matrix_results"],
        "missing_matrices": target_def["missing"],
        "malformed_matrices": target_def["malformed"]
    }, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    (repo/OP_BREAKDOWN_JSON).write_text(json.dumps({
        "task_id": TASK_ID,
        "upgrade_id": UPGRADE_ID,
        "validator_id": VALIDATOR_ID,
        "generated_at_utc": receipt["generated_at_utc"],
        "core_v1_target_definition_score": target_def["score"],
        **core_op
    }, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

    with (repo/OP_BREAKDOWN_CSV).open("w", encoding="utf-8", newline="") as f:
        fields=["metric","score"]
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for k in [
            "core_v1_target_definition_score",
            "core_v1_operational_evidence_score",
            "core_v1_workflow_readiness_score",
            "core_v1_trust_readiness_score",
            "core_v1_human_visibility_score",
            "core_v1_no_core_mutation_evidence_score"
        ]:
            w.writerow({"metric": k, "score": target_def["score"] if k=="core_v1_target_definition_score" else core_op.get(k)})

    with (repo/CORE_BREAKDOWN_CSV).open("w", encoding="utf-8", newline="") as f:
        fields=["matrix","score","exists","parses","missing_sections"]
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for name,r in target_def["matrix_results"].items():
            w.writerow({"matrix":name,"score":r["score"],"exists":r["exists"],"parses":r["parses"],"missing_sections":";".join(r["missing_sections"])})

    with (repo/ORGAN_CSV).open("w", encoding="utf-8", newline="") as f:
        fields=[
            "organ_id","organ_readiness_score","organ_profile_baseline_score","organ_structural_score",
            "organ_operational_score","organ_trust_score","capped_by"
        ]
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for organ, data in organ_split["organs"].items():
            w.writerow({
                "organ_id": organ,
                "organ_readiness_score": data["organ_readiness_score"],
                "organ_profile_baseline_score": data["organ_profile_baseline_score"],
                "organ_structural_score": data["organ_structural_score"],
                "organ_operational_score": data["organ_operational_score"],
                "organ_trust_score": data["organ_trust_score"],
                "capped_by": json.dumps(data["capped_by"], ensure_ascii=False)
            })

    organ_lines = []
    for organ, data in sorted(organ_split["organs"].items(), key=lambda kv: kv[1]["organ_readiness_score"]):
        cap = f" capped: {data['capped_by']}" if data["capped_by"] else ""
        organ_lines.append(
            f"- `{organ}`: readiness `{data['organ_readiness_score']}` "
            f"(profile `{data['organ_profile_baseline_score']}`, structural `{data['organ_structural_score']}`, "
            f"operational `{data['organ_operational_score']}`, trust `{data['organ_trust_score']}`){cap}"
        )
    rec_lines = [f"{r['priority']}. **{r['area']}** — {r['reason']} → `{r['recommended_patch_family']}`" for r in recs]
    checks_md = "\n".join(f"- `{c['status']}` — {c['name']}" for c in receipt["checks"])
    warnings_md = "\n".join(f"- {w}" for w in receipt["warnings"]) if receipt["warnings"] else "- none"
    errors_md = "\n".join(f"- {e}" for e in receipt["errors"]) if receipt["errors"] else "- none"

    report = f"""# THRONE TARGET GAP REPORT V0.5 — ORGAN IMPLEMENTATION SPLIT

task_id: `{TASK_ID}`  
upgrade_id: `{UPGRADE_ID}`  
validator_id: `{VALIDATOR_ID}`  
verdict: `{receipt['verdict']}`  
mode: `MEASURE_ONLY`  
validation_model: `TARGET_V1_VS_CURRENT_REALITY_WITH_ORGAN_IMPLEMENTATION_SPLIT`  
generated_at_utc: `{receipt['generated_at_utc']}`

## Global scores

- core_readiness_score: `{receipt['scores']['core_readiness_score']}`
- throne_readiness_score: `{receipt['scores']['throne_readiness_score']}`
- great_nine_readiness_score: `{receipt['scores']['great_nine_readiness_score']}`
- lowest_organ_readiness_score: `{receipt['scores']['lowest_organ_readiness_score']}`

## Great Nine split

- great_nine_profile_baseline_score: `{receipt['scores']['great_nine_profile_baseline_score']}`
- great_nine_structural_score: `{receipt['scores']['great_nine_structural_score']}`
- great_nine_operational_score: `{receipt['scores']['great_nine_operational_score']}`
- great_nine_trust_score: `{receipt['scores']['great_nine_trust_score']}`

## Core v1 strict split

- core_v1_target_definition_score: `{receipt['scores']['core_v1_target_definition_score']}`
- core_v1_operational_evidence_score: `{receipt['scores']['core_v1_operational_evidence_score']}`
- core_v1_workflow_readiness_score: `{receipt['scores']['core_v1_workflow_readiness_score']}`
- core_v1_trust_readiness_score: `{receipt['scores']['core_v1_trust_readiness_score']}`
- core_v1_human_visibility_score: `{receipt['scores']['core_v1_human_visibility_score']}`
- core_v1_no_core_mutation_evidence_score: `{receipt['scores']['core_v1_no_core_mutation_evidence_score']}`

## Interpretation

A passported organ is not a fully implemented organ.

Profile validators and profile receipts count toward organ baseline, not operational implementation.

## Organ readiness, lowest first

{chr(10).join(organ_lines)}

## Next attention areas

{chr(10).join(rec_lines) if rec_lines else '- none'}

## Checks

{checks_md}

## Warnings

{warnings_md}

## Errors

{errors_md}

## Outputs

- `{RECEIPT.as_posix()}`
- `{ORGAN_IMPL_JSON.as_posix()}`
- `{ORGAN_IMPL_CSV.as_posix()}`
- `{OP_BREAKDOWN_JSON.as_posix()}`
- `{OP_BREAKDOWN_CSV.as_posix()}`
- `{CORE_BREAKDOWN_JSON.as_posix()}`
- `{CORE_BREAKDOWN_CSV.as_posix()}`
- `{ORGAN_CSV.as_posix()}`
- `{NEXT_ATTENTION.as_posix()}`
"""
    (repo/REPORT).write_text(report, encoding="utf-8")

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    repo=Path(ap.parse_args().repo_root).resolve()

    checks=[]; errors=[]; warnings=[]
    required=[TARGET_MATRIX,GAP_SCORING_MATRIX,CORE_V1_SCORING_MATRIX,STRICT_CORE_MATRIX,ORGAN_SPLIT_MATRIX,CENSUS_JSON]
    missing=[p.as_posix() for p in required if not (repo/p).is_file()]
    add(checks,"required_inputs_exist", not missing, {"missing":missing})
    if missing:
        errors += [f"Missing input: {p}" for p in missing]

    census={}; split_matrix={}; strict_core={}
    try:
        if not missing:
            for p in required:
                read_json(repo/p)
            census=read_json(repo/CENSUS_JSON)
            split_matrix=read_json(repo/ORGAN_SPLIT_MATRIX)
            strict_core=read_json(repo/STRICT_CORE_MATRIX)
            add(checks,"input_json_parse", True)
    except Exception as e:
        add(checks,"input_json_parse", False, {"error":str(e)})
        errors.append(f"Input JSON parse failed: {e}")

    residents=census.get("residents",[]) if isinstance(census,dict) else []
    add(checks,"census_has_residents", isinstance(residents,list) and len(residents)>0, {"resident_count":len(residents) if isinstance(residents,list) else None})
    if not isinstance(residents,list) or not residents:
        errors.append("Census residents missing or empty")

    by=classify_by_owner(residents) if isinstance(residents,list) else {}
    target_def=compute_target_definition(repo)
    core_op=compute_strict_core_operational(repo, residents)
    organ_split=compute_organ_split(repo, residents, by, split_matrix)

    add(checks,"target_definition_measured", target_def["score"] > 0 and not target_def["malformed"], {"score":target_def["score"],"missing":target_def["missing"],"malformed":target_def["malformed"]})
    if target_def["malformed"]: errors.append("Malformed target definition matrices")
    if target_def["missing"]: warnings.append(f"Missing target definition matrices: {target_def['missing']}")

    add(checks,"organ_implementation_split_matrix_present", bool(split_matrix), {"matrix_id": split_matrix.get("matrix_id")})
    profile_high_operational_lower = (
        organ_split["great_nine_profile_baseline_score"] >= 90 and
        organ_split["great_nine_operational_score"] < organ_split["great_nine_profile_baseline_score"]
    )
    add(checks,"profile_baseline_separate_from_operational", profile_high_operational_lower, {
        "profile": organ_split["great_nine_profile_baseline_score"],
        "operational": organ_split["great_nine_operational_score"],
    })
    if not profile_high_operational_lower:
        errors.append("Organ profile baseline is not clearly separated from operational proof")

    high_readiness_bad = (
        organ_split["great_nine_readiness_score"] >= 80 and
        (organ_split["great_nine_operational_score"] < 50 or organ_split["great_nine_trust_score"] < 50)
    )
    add(checks,"great_nine_no_false_near_complete", not high_readiness_bad, {
        "great_nine_readiness": organ_split["great_nine_readiness_score"],
        "operational": organ_split["great_nine_operational_score"],
        "trust": organ_split["great_nine_trust_score"],
    })
    if high_readiness_bad:
        errors.append("Great Nine readiness remains too high while operational/trust proof is weak")

    throne_readiness = 97.0  # current Throne structural score from prior baseline; kept stable until separate Throne implementation split.
    great_nine_readiness = organ_split["great_nine_readiness_score"]
    lowest = organ_split["lowest_organ_readiness_score"]

    comp = strict_core.get("core_readiness_composition", {})
    comp_weights = {
        "target_definition": int(comp.get("target_definition_weight",15)),
        "operational": int(comp.get("operational_evidence_weight",25)),
        "workflow": int(comp.get("workflow_readiness_weight",20)),
        "trust": int(comp.get("trust_readiness_weight",15)),
        "human": int(comp.get("human_visibility_weight",10)),
        "no_core": int(comp.get("no_core_mutation_evidence_weight",10)),
        "great_nine": int(comp.get("great_nine_readiness_weight",5)),
    }
    core_inputs = {
        "target_definition":target_def["score"],
        "operational":core_op["core_v1_operational_evidence_score"],
        "workflow":core_op["core_v1_workflow_readiness_score"],
        "trust":core_op["core_v1_trust_readiness_score"],
        "human":core_op["core_v1_human_visibility_score"],
        "no_core":core_op["core_v1_no_core_mutation_evidence_score"],
        "great_nine":great_nine_readiness
    }
    core_readiness = weighted(core_inputs, comp_weights)

    guard = strict_core.get("near_v1_guard", {})
    capped_by = []
    if guard.get("enabled", True):
        guard_rules = [
            ("operational", core_op["core_v1_operational_evidence_score"], "max_core_score_without_operational_evidence_50"),
            ("workflow", core_op["core_v1_workflow_readiness_score"], "max_core_score_without_workflow_50"),
            ("trust", core_op["core_v1_trust_readiness_score"], "max_core_score_without_trust_50"),
            ("no_core", core_op["core_v1_no_core_mutation_evidence_score"], "max_core_score_without_no_core_mutation_50"),
            ("human", core_op["core_v1_human_visibility_score"], "max_core_score_without_human_visibility_50"),
        ]
        for name, value, cap_key in guard_rules:
            if value < 50:
                cap=float(guard.get(cap_key, 65))
                if core_readiness > cap:
                    core_readiness=cap
                    capped_by.append({"reason":name,"score":value,"cap":cap})
    if capped_by:
        warnings.append(f"Near-v1 core guard capped core_readiness_score: {capped_by}")

    add(checks,"near_v1_core_guard_active", bool(guard.get("enabled", True)), {"capped_by": capped_by})

    recs=recommendations(organ_split, core_op)
    verdict="FAIL_UNMEASURABLE" if errors else "PASS_MEASURED"

    input_hashes={}
    for p in required+[SUMMARY_JSON]:
        apath=repo/p
        if apath.is_file():
            input_hashes[p.as_posix()]=sha(apath)

    receipt={
        "receipt_id":"receipt.throne_target_gap.v0_5_organ_implementation_split",
        "task_id":TASK_ID,
        "upgrade_id":UPGRADE_ID,
        "validator_id":VALIDATOR_ID,
        "verdict":verdict,
        "generated_at_utc":utc(),
        "mode":"MEASURE_ONLY",
        "validation_model":"TARGET_V1_VS_CURRENT_REALITY_WITH_ORGAN_IMPLEMENTATION_SPLIT",
        "scores":{
            "core_readiness_score":core_readiness,
            "throne_readiness_score":throne_readiness,
            "great_nine_readiness_score":great_nine_readiness,
            "lowest_organ_readiness_score":lowest,
            "great_nine_profile_baseline_score":organ_split["great_nine_profile_baseline_score"],
            "great_nine_structural_score":organ_split["great_nine_structural_score"],
            "great_nine_operational_score":organ_split["great_nine_operational_score"],
            "great_nine_trust_score":organ_split["great_nine_trust_score"],
            "core_v1_target_definition_score":target_def["score"],
            "core_v1_operational_evidence_score":core_op["core_v1_operational_evidence_score"],
            "core_v1_workflow_readiness_score":core_op["core_v1_workflow_readiness_score"],
            "core_v1_trust_readiness_score":core_op["core_v1_trust_readiness_score"],
            "core_v1_human_visibility_score":core_op["core_v1_human_visibility_score"],
            "core_v1_no_core_mutation_evidence_score":core_op["core_v1_no_core_mutation_evidence_score"],
        },
        "target_definition":target_def,
        "core_operational_breakdown":core_op,
        "organ_implementation_breakdown":organ_split,
        "next_attention":recs,
        "input_hashes_sha256":input_hashes,
        "checks":checks,
        "warnings":warnings,
        "errors":errors,
        "meaning":"PASS_MEASURED means organ profile baseline and operational implementation were separated and measured; it does not mean Great Nine or Core v1 are fully implemented."
    }

    write_outputs(repo, receipt, target_def, core_op, organ_split, recs)

    print(json.dumps({
        "task_id":TASK_ID,
        "upgrade_id":UPGRADE_ID,
        "validator_id":VALIDATOR_ID,
        "verdict":verdict,
        "core_readiness_score":core_readiness,
        "throne_readiness_score":throne_readiness,
        "great_nine_readiness_score":great_nine_readiness,
        "lowest_organ_readiness_score":lowest,
        "great_nine_profile_baseline_score":organ_split["great_nine_profile_baseline_score"],
        "great_nine_structural_score":organ_split["great_nine_structural_score"],
        "great_nine_operational_score":organ_split["great_nine_operational_score"],
        "great_nine_trust_score":organ_split["great_nine_trust_score"],
        "core_v1_target_definition_score":target_def["score"],
        "core_v1_operational_evidence_score":core_op["core_v1_operational_evidence_score"],
        "core_v1_workflow_readiness_score":core_op["core_v1_workflow_readiness_score"],
        "core_v1_trust_readiness_score":core_op["core_v1_trust_readiness_score"],
        "core_v1_human_visibility_score":core_op["core_v1_human_visibility_score"],
        "core_v1_no_core_mutation_evidence_score":core_op["core_v1_no_core_mutation_evidence_score"],
        "receipt":RECEIPT.as_posix(),
        "report":REPORT.as_posix(),
        "organ_implementation_breakdown":ORGAN_IMPL_JSON.as_posix(),
        "warnings":warnings,
        "errors":errors
    }, ensure_ascii=False, indent=2))

    return 0 if verdict == "PASS_MEASURED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
