#!/usr/bin/env python3
# Trinity manifest validator v0_2 (Inquisition organ; zero external deps)
# Enforces hardened-form invariants + 5/7/10/14 etalon rule + live-gate.
import json, sys, argparse

SCHEMA_ID = "imperium.trinity_patch_manifest.v0_2"
TAX14 = ["GOVERNANCE","CLEANUP_HYGIENE","PASSPORTING","VALIDATION_PROOF","CONTINUITY",
         "TOOLING_MECHANICUS","UX_OBSERVABILITY","ROUTING_TASKING","SECURITY",
         "GHOST_EVOLVE_LEARNING","KNOWLEDGE_SCHOLA","STRATEGY_STRATEGIUM",
         "EXTERNAL_TRADING","EXTERNAL_FREELANCE_DELIVERY"]
VALID_FORMS = {5,7,10,14}
EXEC = {"static","sim","paper","shadow","live"}
REQ = ["manifest_schema","patch_id","patch_type","version","authority_refs","scope",
       "dirty_scope_expectation","forbidden_actions_checked","rollback","git_truth","function_directions"]

def validate(m):
    e=[]; w=[]
    if m.get("manifest_schema")!=SCHEMA_ID: e.append("manifest_schema must be %s" % SCHEMA_ID)
    for k in REQ:
        if k not in m: e.append("missing required field: %s" % k)
    if not isinstance(m.get("authority_refs"),list) or len(m.get("authority_refs",[]))<1:
        e.append("authority_refs must list >=1 canon clause")
    if m.get("dirty_scope_expectation") not in {"additive_only","classification_only","move_only","mixed"}:
        e.append("dirty_scope_expectation invalid")
    if not (m.get("rollback") or {}).get("backup_root"): e.append("rollback.backup_root required")
    gt=m.get("git_truth") or {}
    for k in ("expected_before","expected_after","contour"):
        if k not in gt: e.append("git_truth.%s required" % k)
    fd=m.get("function_directions") or {}
    tf=fd.get("target_form")
    if tf not in VALID_FORMS: e.append("target_form must be in {5,7,10,14}")
    dirs=fd.get("directions") or []
    declared=len(dirs); active=0; dormant=0; seen=set()
    for d in dirs:
        did=d.get("direction_id")
        if did not in TAX14: e.append("unknown direction_id: %s" % did)
        if did in seen: e.append("duplicate direction_id: %s" % did)
        seen.add(did)
        if d.get("execution_mode") not in EXEC: e.append("%s: bad execution_mode" % did)
        st=d.get("status","active")
        if st=="active":
            active+=1
            if not d.get("proof_receipt"): e.append("%s: active direction needs proof_receipt" % did)
        elif st=="dormant":
            dormant+=1
            if not d.get("dormant_declaration"): e.append("%s: dormant needs dormant_declaration" % did)
            if d.get("execution_mode")!="static": e.append("%s: dormant must be execution_mode=static" % did)
        else:
            e.append("%s: bad status %s" % (did, st))
        if d.get("execution_mode")=="live" and not m.get("owner_canon_amendment_ref"):
            e.append("%s: execution_mode=live BLOCKED without owner_canon_amendment_ref" % did)
    if tf and declared!=tf: e.append("declared directions (%d) != target_form (%s)" % (declared, tf))
    etalon_ok = (tf==14 and declared==14 and set(seen)==set(TAX14))
    if bool(fd.get("etalon")) and not etalon_ok:
        e.append("etalon=true requires target_form=14 and all 14 directions declared")
    return {"validator":"trinity_manifest_validator_v0_2","schema_id":SCHEMA_ID,
            "patch_id":m.get("patch_id"),"declared_count":declared,"active_count":active,
            "dormant_count":dormant,"etalon_ok":etalon_ok,
            "result":"PASS" if not e else "FAIL","errors":e,"warnings":w}

def main():
    ap=argparse.ArgumentParser(description="Validate a Trinity patch manifest (v0_2)")
    ap.add_argument("manifest")
    ap.add_argument("--out", default=None)
    a=ap.parse_args()
    m=json.load(open(a.manifest, encoding="utf-8"))
    r=validate(m)
    s=json.dumps(r, ensure_ascii=False, indent=2)
    if a.out:
        open(a.out,"w",encoding="utf-8").write(s)
    print(s)
    sys.exit(0 if r["result"]=="PASS" else 1)

if __name__=="__main__":
    main()
