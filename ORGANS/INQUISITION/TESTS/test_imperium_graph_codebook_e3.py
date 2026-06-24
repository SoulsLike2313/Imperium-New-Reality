"""E3 self-test for GRAPH-SPEC-0001 (Imperium Graph doctrine v0.1)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK_ROOT = HERE.parents[3]
DOC = PACK_ROOT / "files" / "ORGANS" / "DOCTRINARIUM" / "IMPERIUM_GRAPH.md"

results = []
def check(name, ok, detail=""):
    results.append(bool(ok))
    suffix = (" -> " + detail) if (detail and not ok) else ""
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, suffix))

# T1: parses utf-8-sig, non-trivial size
try:
    text = DOC.read_text(encoding="utf-8-sig")
    check("T1_doc_parses_utf8", len(text) > 3000, "too short: %d bytes" % len(text))
except Exception as e:
    check("T1_doc_parses_utf8", False, str(e))
    print("\n0/8 PASSED\nE3 RESULT: FAILURES PRESENT")
    sys.exit(1)

# T2: all twelve canonical sections present
required_sections = [
    "NODE_TYPES", "STATUS_VOCABULARY", "EDGE_TYPES", "VIEW_TYPES",
    "VISUAL_MAPPING", "COMPOSITION_RULES", "TRANSMISSION_CONTRACTS",
    "ANNOTATION_CONTRACT", "INDEXER_CONTRACT", "VIEWER_CONTRACT",
    "VERSIONING", "SIGNATURE",
]
missing = [s for s in required_sections if s not in text]
check("T2_all_sections_present", not missing, "missing: %s" % missing)

# T3: nine node types declared
required_nodes = ["organ", "sub_organ", "doctrine", "agent", "task", "land", "receipt", "sentinel", "thread"]
missing_n = [n for n in required_nodes if (n + " ") not in text and (n + "        ") not in text]
# simpler: just substring check
missing_n = [n for n in required_nodes if n not in text]
check("T3_node_types_present", not missing_n, "missing: %s" % missing_n)

# T4: six views present
required_views = ["overview", "organ_drilldown", "provenance_chain", "time_slice", "sentinel_pulse", "doctrine_map"]
missing_v = [v for v in required_views if v not in text]
check("T4_six_views_present", not missing_v, "missing: %s" % missing_v)

# T5: EYES_V2 anchored by name and version
eyes_anchored = ("EYES_V2.md" in text) and ("v0.2" in text)
check("T5_eyes_v2_anchored", eyes_anchored)

# T6: URL schema example present (canonical query keys)
required_url_keys = ["v=V", "organ=", "since=", "focus=", "depth="]
missing_u = [k for k in required_url_keys if k not in text]
check("T6_url_schema_present", not missing_u, "missing url keys: %s" % missing_u)

# T7: annotation storage_key declared and forbids repo writes
annot_ok = ("imperium.graph.annotations.v1" in text) and ("repo_write    : forbidden" in text)
check("T7_annotation_contract_ok", annot_ok)

# T8: viewer stack pinned (HTML + Cytoscape.js) and indexer artifact path declared
stack_ok = ("Cytoscape.js" in text) and ("SUPPORT/graph_snapshot.json" in text) and ("SUPPORT/viewer/" in text)
check("T8_viewer_stack_pinned", stack_ok)

total = len(results)
passed = sum(1 for r in results if r)
print("\n%d/%d PASSED" % (passed, total))
print("E3 RESULT: " + ("ALL PASSED" if passed == total else "FAILURES PRESENT"))
sys.exit(0 if passed == total else 1)
