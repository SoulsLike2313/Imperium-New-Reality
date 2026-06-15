#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP end-to-end smoke test.

Proves the core promise: kernel stays clean, products only leave through GATE,
fake-green is discarded, honest PASS is released as a pending-owner plan.

Run: python warp_smoke.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "ENGINE"))

from warp_zone import WarpSession  # noqa: E402


def _make_fake_kernel(root):
    os.makedirs(os.path.join(root, "ORGANS", "ASTRONOMICON", "CORE"), exist_ok=True)
    with open(os.path.join(root, "ORGANS", "ASTRONOMICON", "CORE", "route.py"),
              "w", encoding="utf-8") as fh:
        fh.write("def route():\n    return 'baseline'\n")


def _scenario(tmp, fake_green):
    core = os.path.join(tmp, "kernel")
    warp = os.path.join(tmp, "warp_runtime")
    _make_fake_kernel(core)
    s = WarpSession(task="build third party dashboard", kind="THIRD_PARTY",
                    core_root=core, warp_root=warp,
                    trigger="auto" if fake_green else "manual")
    s.register("kernel", "CORE", mode="read")
    s.register("organ", "MECHANICUS", mode="dry-run")
    s.register("servitor", "CAP-ALPHA", mode="dry-run")
    s.set_plan(["build", "test", "gate"])
    s.set_criteria([
        {"id": "builds", "metric": "builds", "required": True, "expect": True, "min_evidence": "E3"},
        {"id": "tests_pass", "metric": "tests_pass", "required": True, "expect": True, "min_evidence": "E3"},
    ])
    s.advance("BUILD")
    # write a product artifact (lives only in WARP, never in kernel)
    s.write_artifact("PRODUCTS/dashboard/app.py", "print('dashboard')\n",
                     target_zone="UNKNOWN")
    # also touch a CORE-zone path to prove kernel baseline is untouched
    s.write_artifact("ORGANS/ASTRONOMICON/CORE/route.py",
                     "def route():\n    return 'changed in warp'\n",
                     target_zone="CORE")
    s.advance("VALIDATE")
    if fake_green:
        # claims pass but only E1 evidence -> must be discarded
        s.record_metric("builds", value=True, evidence_level="E1")
        s.record_metric("tests_pass", value=True, evidence_level="E1")
    else:
        s.record_metric("builds", value=True, evidence_level="E3", note="compiled")
        s.record_metric("tests_pass", value=True, evidence_level="E3", note="pytest ok")
    s.advance("GATE")
    res = s.run_gate()
    if res["verdict"] == "RELEASE":
        s.release()
    elif res["verdict"] == "DISCARD":
        s.discard(reason="; ".join(res.get("reasons", [])))
    elif res["verdict"] == "HOLD":
        s.hold(reason="; ".join(res.get("reasons", [])))
    s.save_manifest()

    # verify kernel baseline file is byte-for-byte untouched
    with open(os.path.join(core, "ORGANS", "ASTRONOMICON", "CORE", "route.py"),
              "r", encoding="utf-8") as fh:
        kernel_after = fh.read()
    kernel_clean = (kernel_after == "def route():\n    return 'baseline'\n")
    return s, res, kernel_clean


def main():
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        s1, r1, clean1 = _scenario(os.path.join(tmp, "a"), fake_green=True)
        print("== SCENARIO 1: fake-green ==")
        print("  verdict:", r1["verdict"], "| reasons:", r1.get("reasons"))
        print("  kernel untouched:", clean1)
        print("  staged diffs:", len(s1.changes))
        ok = ok and r1["verdict"] == "DISCARD" and clean1

        s2, r2, clean2 = _scenario(os.path.join(tmp, "b"), fake_green=False)
        print("== SCENARIO 2: honest pass ==")
        print("  verdict:", r2["verdict"], "| reasons:", r2.get("reasons"))
        print("  kernel untouched:", clean2)
        rel = s2.manifest().get("release")
        print("  release status:", (rel or {}).get("status"),
              "| kernel_touched:", (rel or {}).get("kernel_touched"))
        ok = ok and r2["verdict"] == "RELEASE" and clean2
        ok = ok and (rel or {}).get("kernel_touched") is False

    print("\nSMOKE RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
