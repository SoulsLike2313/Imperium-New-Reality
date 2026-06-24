#!/usr/bin/env python3
"""E3 self-test for inq_land_gate_v0_1. Pure-python, no pytest dependency.

Proves each gate fires on its negative fixture and a clean land passes:
  T1 clean ff land + canonical path + truthful base      -> ALLOW (exit 0)
  T2 stale base (local HEAD != origin/master)            -> DENY  (G1_BASE_STALE)
  T3 rogue top-level root (_CORE/...)                     -> DENY  (G2_ROGUE_ROOT)
  T4 unknown organ under ORGANS/                          -> DENY  (G2_UNKNOWN_ORGAN)
  T5 provenance lie (declared base != real parent)        -> DENY  (G3_PROVENANCE_LIE)
  T6 the historical OWNER-PROFILE-0001 rogue map          -> DENY  (catches my real mistake)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / "TOOLS"
sys.path.insert(0, str(TOOLS))
import inq_land_gate_v0_1 as gate  # noqa: E402

HEAD = "461e23ceebdc0a3b174ceda65409fcfee8a35447"
OLD = "8bd511d6ef53ab4be2b2d157092a2ed2c13296bb"


def mkmanifest(task_id, base, target_map):
    return {
        "task_id": task_id,
        "expected_reality_head": base,
        "integration": {"mode": "copy", "map": target_map},
    }


def run_case(name, manifest, live_head, origin_head, parent_sha, want_verdict, want_reason_substr=None):
    rec = gate.evaluate(manifest, None, live_head, origin_head, parent_sha, mode="ENFORCED")
    ok = rec["verdict"] == want_verdict
    if want_reason_substr is not None:
        ok = ok and any(want_reason_substr in r for r in rec["deny_reasons"])
    status = "PASS" if ok else "FAIL"
    print("[%s] %s -> verdict=%s reasons=%s" % (status, name, rec["verdict"], rec["deny_reasons"]))
    return ok


def main():
    results = []
    # T1 clean
    results.append(run_case(
        "T1_clean_land",
        mkmanifest("KERNEL-GATE-0001", HEAD, {"files/x.py": "ORGANS/INQUISITION/TOOLS/x.py"}),
        HEAD, HEAD, HEAD, "ALLOW"))
    # T2 stale base
    results.append(run_case(
        "T2_stale_base",
        mkmanifest("KERNEL-GATE-0001", OLD, {"files/x.py": "ORGANS/INQUISITION/TOOLS/x.py"}),
        OLD, HEAD, OLD, "DENY", "G1_BASE_STALE"))
    # T3 rogue root
    results.append(run_case(
        "T3_rogue_root",
        mkmanifest("OWNER-PROFILE-0001", HEAD, {"files/p.md": "_CORE/OWNER_PROFILE.md"}),
        HEAD, HEAD, HEAD, "DENY", "G2_ROGUE_ROOT"))
    # T4 unknown organ
    results.append(run_case(
        "T4_unknown_organ",
        mkmanifest("X-0001", HEAD, {"files/s.py": "ORGANS/Inquisitorium/Sentinels/s.py"}),
        HEAD, HEAD, HEAD, "DENY", "G2_UNKNOWN_ORGAN"))
    # T5 provenance lie
    results.append(run_case(
        "T5_provenance_lie",
        mkmanifest("X-0001", OLD, {"files/x.py": "ORGANS/INQUISITION/TOOLS/x.py"}),
        HEAD, HEAD, HEAD, "DENY", "G3_PROVENANCE_LIE"))
    # T6 the real historical OWNER-PROFILE-0001 rogue map (multi-root)
    results.append(run_case(
        "T6_owner_profile_real_map",
        mkmanifest("OWNER-PROFILE-0001", HEAD, {
            "files/OWNER_PROFILE.md": "_CORE/OWNER_PROFILE.md",
            "files/OWNER.role.yaml": "Officio/Roles/OWNER.role.yaml",
            "files/owner_burnout_check.py": "Inquisitorium/Sentinels/owner_burnout_check.py",
        }),
        HEAD, HEAD, HEAD, "DENY", "G2_ROGUE_ROOT"))
    total = len(results)
    passed = sum(1 for r in results if r)
    print("\n%d/%d PASSED" % (passed, total))
    if passed == total:
        print("E3 RESULT: ALL PASSED")
        return 0
    print("E3 RESULT: FAILURES PRESENT")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
