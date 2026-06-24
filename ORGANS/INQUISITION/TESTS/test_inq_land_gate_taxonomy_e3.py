"""E3 for INQ-GATE-TAXONOMY-FIX-0001.

Verifies that the patched inq_land_gate_v0_1.py:
  - Accepts integration.map in canonical list-of-{src,dst} shape (was crash bug).
  - Accepts integration.map in legacy dict {src:dst} shape (backward compat).
  - Recognizes canonical 'declared_base' manifest key (was DENY bug).
  - Still recognizes legacy 'expected_reality_head' and 'base' keys.
  - Continues to enforce G1/G2/G3 correctly on bad inputs.
"""
import sys, json, tempfile, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Resolve gate path: in sandbox-pack layout, gate lives at PACK_ROOT/files/ORGANS/...
# After land in repo, both this test and the gate live under ORGANS/INQUISITION/.
_cand_in_repo = HERE.parent / "TOOLS" / "inq_land_gate_v0_1.py"
_cand_in_pack = HERE.parents[3] / "files" / "ORGANS" / "INQUISITION" / "TOOLS" / "inq_land_gate_v0_1.py"
if _cand_in_repo.exists():
    GATE_PATH = _cand_in_repo
else:
    GATE_PATH = _cand_in_pack

spec = importlib.util.spec_from_file_location("inq_gate", str(GATE_PATH))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

results = []
def check(name, ok, detail=""):
    results.append(bool(ok))
    suffix = (" -> " + detail) if (detail and not ok) else ""
    print("[%s] %s%s" % ("PASS" if ok else "FAIL", name, suffix))

HEAD = "4f7462910000000000000000000000000000abcd"

# T1: list-shaped integration.map with valid paths, declared_base canonical -> ALLOW, no crash
manifest_list_ok = {
    "task_id": "TEST-LIST-OK",
    "declared_base": HEAD,
    "integration": {
        "map": [
            {"src": "files/ORGANS/DOCTRINARIUM/X.md", "dst": "ORGANS/DOCTRINARIUM/X.md"},
            {"src": "files/ORGANS/INQUISITION/TESTS/t.py", "dst": "ORGANS/INQUISITION/TESTS/t.py"},
        ]
    },
}
try:
    r1 = gate.evaluate(manifest_list_ok, None, HEAD, HEAD, HEAD, "ENFORCED")
    check("T1_list_shape_no_crash_allow",
          r1["verdict"] == "ALLOW" and r1["deny_reasons"] == [] and len(r1["changed_paths"]) == 2,
          "verdict=%s reasons=%s paths=%s" % (r1["verdict"], r1["deny_reasons"], r1["changed_paths"]))
except Exception as e:
    check("T1_list_shape_no_crash_allow", False, "raised: %r" % e)

# T2: dict-shaped integration.map (legacy) -> ALLOW
manifest_dict_ok = {
    "task_id": "TEST-DICT-OK",
    "declared_base": HEAD,
    "integration": {
        "map": {
            "files/ORGANS/SUPPORT/y.txt": "SUPPORT/y.txt",
            "files/ORGANS/MECHANICUS/z.py": "ORGANS/MECHANICUS/z.py",
        }
    },
}
try:
    r2 = gate.evaluate(manifest_dict_ok, None, HEAD, HEAD, HEAD, "ENFORCED")
    check("T2_dict_shape_legacy_allow",
          r2["verdict"] == "ALLOW" and r2["deny_reasons"] == [],
          "verdict=%s reasons=%s" % (r2["verdict"], r2["deny_reasons"]))
except Exception as e:
    check("T2_dict_shape_legacy_allow", False, "raised: %r" % e)

# T3: rogue top-level root -> DENY G2_ROGUE_ROOT
manifest_rogue = {
    "task_id": "TEST-ROGUE",
    "declared_base": HEAD,
    "integration": {"map": [{"src": "files/badroot/x.txt", "dst": "badroot/x.txt"}]},
}
r3 = gate.evaluate(manifest_rogue, None, HEAD, HEAD, HEAD, "ENFORCED")
check("T3_rogue_root_denied",
      r3["verdict"] == "DENY" and any("G2_ROGUE_ROOT" in x for x in r3["deny_reasons"]),
      "reasons=%s" % r3["deny_reasons"])

# T4: unknown organ -> DENY G2_UNKNOWN_ORGAN
manifest_unknown = {
    "task_id": "TEST-UNKNOWN",
    "declared_base": HEAD,
    "integration": {"map": [{"src": "files/ORGANS/FAKEORGAN/x.md", "dst": "ORGANS/FAKEORGAN/x.md"}]},
}
r4 = gate.evaluate(manifest_unknown, None, HEAD, HEAD, HEAD, "ENFORCED")
check("T4_unknown_organ_denied",
      r4["verdict"] == "DENY" and any("G2_UNKNOWN_ORGAN" in x for x in r4["deny_reasons"]),
      "reasons=%s" % r4["deny_reasons"])

# T5: missing all base keys -> DENY G1_NO_DECLARED_BASE
manifest_nobase = {
    "task_id": "TEST-NOBASE",
    "integration": {"map": [{"src": "a", "dst": "ORGANS/INQUISITION/x.py"}]},
}
r5 = gate.evaluate(manifest_nobase, None, HEAD, HEAD, HEAD, "ENFORCED")
check("T5_no_declared_base_denied",
      r5["verdict"] == "DENY" and any("G1_NO_DECLARED_BASE" in x for x in r5["deny_reasons"]),
      "reasons=%s" % r5["deny_reasons"])

# T6: declared_base canonical key recognized -> NO G1_NO_DECLARED_BASE
r6 = gate.evaluate(manifest_list_ok, None, HEAD, HEAD, HEAD, "ENFORCED")
check("T6_declared_base_canonical_key_ok",
      not any("G1_NO_DECLARED_BASE" in x for x in r6["deny_reasons"]) and r6["declared_base"] == HEAD)

# T7: legacy 'expected_reality_head' key still recognized
manifest_legacy = {
    "task_id": "TEST-LEGACY",
    "expected_reality_head": HEAD,
    "integration": {"map": [{"src": "a", "dst": "ORGANS/INQUISITION/x.py"}]},
}
r7 = gate.evaluate(manifest_legacy, None, HEAD, HEAD, HEAD, "ENFORCED")
check("T7_legacy_expected_reality_head_ok",
      r7["verdict"] == "ALLOW" and r7["declared_base"] == HEAD,
      "verdict=%s reasons=%s" % (r7["verdict"], r7["deny_reasons"]))

# T8: live != origin -> DENY G1_BASE_STALE
manifest_stale = dict(manifest_list_ok)
LIVE = "aaaaaaaa00000000000000000000000000000000"
ORIG = "bbbbbbbb00000000000000000000000000000000"
manifest_stale["declared_base"] = LIVE
r8 = gate.evaluate(manifest_stale, None, LIVE, ORIG, LIVE, "ENFORCED")
check("T8_stale_base_denied",
      r8["verdict"] == "DENY" and any("G1_BASE_STALE" in x for x in r8["deny_reasons"]),
      "reasons=%s" % r8["deny_reasons"])

# T9: provenance lie (declared != parent) -> DENY G3_PROVENANCE_LIE
manifest_lie = dict(manifest_list_ok)
manifest_lie["declared_base"] = "cccccccc00000000000000000000000000000000"
r9 = gate.evaluate(manifest_lie, None, HEAD, HEAD, HEAD, "ENFORCED")
check("T9_provenance_lie_denied",
      r9["verdict"] == "DENY" and any("G3_PROVENANCE_LIE" in x for x in r9["deny_reasons"]),
      "reasons=%s" % r9["deny_reasons"])

# T10: empty integration.map -> DENY G2_NO_TARGETS
manifest_empty = {
    "task_id": "TEST-EMPTY",
    "declared_base": HEAD,
    "integration": {"map": []},
}
r10 = gate.evaluate(manifest_empty, None, HEAD, HEAD, HEAD, "ENFORCED")
check("T10_empty_map_denied",
      r10["verdict"] == "DENY" and any("G2_NO_TARGETS" in x for x in r10["deny_reasons"]),
      "reasons=%s" % r10["deny_reasons"])

total = len(results)
passed = sum(1 for x in results if x)
print("\n%d/%d PASSED" % (passed, total))
print("E3 RESULT: " + ("ALL PASSED" if passed == total else "FAILURES PRESENT"))
sys.exit(0 if passed == total else 1)
