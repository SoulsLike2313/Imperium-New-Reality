"""E3 self-test for PROV-FIX-228ED0E2-0001.

Validates structure and internal consistency of the provenance correction.
All paths resolve relative to PACK_ROOT so the test is portable.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # files/ORGANS/INQUISITION/TESTS
PACK_ROOT = HERE.parents[3]                      # pack root
RECEIPT = PACK_ROOT / "files" / "ORGANS" / "INQUISITION" / "REPORTS" / "provenance_corrections" / "PROV-FIX-228ED0E2-0001.json"
COMPANION = PACK_ROOT / "files" / "ORGANS" / "INQUISITION" / "REPORTS" / "provenance_corrections" / "PROV-FIX-228ED0E2-0001.md"

SHA_RE = re.compile(r"^[0-9a-f]{12,40}$")
REQ_TOP = ["schema_version", "correction_id", "issued_at", "issued_by", "target", "finding", "evidence", "effect", "signature"]
REQ_TARGET = ["commit_sha", "commit_subject", "authored_by_external_assistant", "landed_via"]
REQ_FINDING = ["declared_base_in_task_manifest", "actual_git_parent", "verdict", "gate_rule_that_would_have_caught_it"]

results = []

def check(name, ok, detail=""):
    results.append(ok)
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, (" -> " + detail) if detail and not ok else ""))

# T1: receipt JSON parses
try:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
    check("T1_receipt_parses_as_json", True)
except Exception as e:
    check("T1_receipt_parses_as_json", False, str(e))
    print("\n0/5 PASSED\nE3 RESULT: FAILURES PRESENT")
    sys.exit(1)

# T2: required fields present
missing_top = [k for k in REQ_TOP if k not in receipt]
missing_target = [k for k in REQ_TARGET if k not in receipt.get("target", {})]
missing_finding = [k for k in REQ_FINDING if k not in receipt.get("finding", {})]
check("T2_required_fields_present",
      not (missing_top or missing_target or missing_finding),
      "missing top=%s target=%s finding=%s" % (missing_top, missing_target, missing_finding))

# T3: SHAs are valid hex
tgt_sha = receipt["target"]["commit_sha"]
decl = receipt["finding"]["declared_base_in_task_manifest"]
parent = receipt["finding"]["actual_git_parent"]
shas_ok = all(SHA_RE.match(s) for s in (tgt_sha, decl, parent))
check("T3_shas_are_hex", shas_ok, "target=%s decl=%s parent=%s" % (tgt_sha, decl, parent))

# T4: declared_base != actual_parent (there must actually be a lie)
check("T4_lie_is_real", decl != parent,
      "declared and actual are identical - nothing to correct")

# T5: companion exists and references the target SHA
comp_ok = COMPANION.exists() and (tgt_sha[:7] in COMPANION.read_text(encoding="utf-8-sig"))
check("T5_companion_md_references_target", comp_ok)

total = len(results)
passed = sum(1 for r in results if r)
print("\n%d/%d PASSED" % (passed, total))
print("E3 RESULT: " + ("ALL PASSED" if passed == total else "FAILURES PRESENT"))
sys.exit(0 if passed == total else 1)
