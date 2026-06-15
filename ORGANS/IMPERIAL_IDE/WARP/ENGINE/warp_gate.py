#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WARP RELEASE GATE (V0.1)

Nothing leaves the warp zone unless the gate says RELEASE. This is the hard
engineering rule you asked for: "если сделали не оч круто и не смогли
переделать — просто не выпустили продукт из варп-зоны".

Evidence levels (mirror of the system GOST EVOLVE ladder):
  E1 exists, E2 self-claim, E3 executed, E4 stable replay, E5 audit, E6 owner UX.

Verdicts:
  RELEASE  - all required criteria met at/above min evidence; product may be
             promoted out of warp via a gated release plan.
  HOLD     - something required is unmet but fixable; stays in warp.
  DISCARD  - integrity violation (e.g. fake-green: pass claimed without
             evidence). Product is rejected; kernel never touched.
"""

_EVIDENCE_ORDER = {"E1": 1, "E2": 2, "E3": 3, "E4": 4, "E5": 5, "E6": 6}


def _ev(level):
    return _EVIDENCE_ORDER.get(str(level).upper(), 0)


def evaluate(criteria, metrics, min_evidence="E3"):
    """
    criteria: list of {id, required(bool), metric, expect, min_evidence?}
    metrics:  dict metric_id -> {value, evidence_level, claimed_pass?}
    """
    min_req = _ev(min_evidence)
    failed, reasons, fake_green = [], [], []

    for c in criteria:
        cid = c.get("id")
        metric_id = c.get("metric", cid)
        required = c.get("required", True)
        expect = c.get("expect", True)
        c_min = _ev(c.get("min_evidence", min_evidence))
        m = metrics.get(metric_id)

        if m is None:
            if required:
                failed.append(cid)
                reasons.append("%s: no metric reported" % cid)
            continue

        value = m.get("value")
        ev_level = _ev(m.get("evidence_level", "E1"))
        claimed_pass = m.get("claimed_pass", value == expect)

        # FAKE-GREEN detection: claims pass but evidence below threshold.
        if claimed_pass and value == expect and ev_level < c_min:
            fake_green.append(cid)
            reasons.append(
                "%s: claimed pass but evidence %s < required %s"
                % (cid, m.get("evidence_level"), c.get("min_evidence", min_evidence))
            )
            continue

        if value != expect:
            if required:
                failed.append(cid)
                reasons.append("%s: value=%r expected=%r" % (cid, value, expect))
        elif ev_level < c_min and required:
            failed.append(cid)
            reasons.append(
                "%s: evidence %s < required %s"
                % (cid, m.get("evidence_level"), c.get("min_evidence", min_evidence))
            )

    if fake_green:
        verdict = "DISCARD"
    elif failed:
        verdict = "HOLD"
    else:
        verdict = "RELEASE"

    return {
        "verdict": verdict,
        "failed": failed,
        "fake_green": fake_green,
        "reasons": reasons,
        "min_evidence": min_evidence,
        "released": verdict == "RELEASE",
    }
