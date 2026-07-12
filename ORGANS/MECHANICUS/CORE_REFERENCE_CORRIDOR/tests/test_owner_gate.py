from __future__ import annotations

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.owner_gate import (
    OwnerDecisionRequired,
    OwnerGate,
    OwnerGateError,
    THRONE_RISK_FIELDS,
)


def test_owner_launch_and_land_gates_require_explicit_current_decisions(tmp_path):
    gate = OwnerGate(tmp_path)
    with pytest.raises(OwnerDecisionRequired):
        gate.require("LAUNCH", "TASK-0001", "WARP-0001")

    gate.record_decision(
        "decision-launch",
        task_id="TASK-0001",
        action="APPROVE_LAUNCH",
        rationale="Owner launches the isolated corridor.",
        evidence_refs=["owner-input:0001"],
    )
    assert gate.require("LAUNCH", "TASK-0001", "WARP-0001")["allowed"] is True

    with pytest.raises(OwnerDecisionRequired):
        gate.require("PREPARE_LAND", "TASK-0001", "WARP-0001")
    gate.record_decision(
        "decision-land-plan",
        task_id="TASK-0001",
        warp_id="WARP-0001",
        action="ALLOW_LAND_PREPARATION",
        rationale="Prepare a plan only; do not land.",
        evidence_refs=["evidence:review"],
    )
    receipt = gate.require("PREPARE_LAND", "TASK-0001", "WARP-0001")
    assert receipt["decision_ref"] == "decision-land-plan"

    gate.record_decision(
        "decision-forbid-land",
        task_id="TASK-0001",
        warp_id="WARP-0001",
        action="FORBID_LAND",
        rationale="Owner supersedes land preparation.",
        evidence_refs=["evidence:risk"],
    )
    with pytest.raises(OwnerDecisionRequired):
        gate.require("PREPARE_LAND", "TASK-0001", "WARP-0001")


def test_throne_risk_requires_complete_causal_proof_and_owner_acceptance(tmp_path):
    gate = OwnerGate(tmp_path)
    risk = {
        "risk_id": "risk-0001",
        "task_id": "TASK-0001",
        "warp_id": "WARP-0001",
        "evidence": ["evidence:validator-failure"],
        "causal_chain": ["invalid input", "unsafe write", "Reality drift"],
        "affected_scope": ["ORGANS/MECHANICUS"],
        "probability": 0.4,
        "severity": "HIGH",
        "expected_consequences": ["out-of-scope mutation"],
    }
    recorded = gate.record_throne_risk(risk)
    assert all(field in recorded for field in THRONE_RISK_FIELDS)
    with pytest.raises(OwnerDecisionRequired):
        gate.require("ACCEPT_RISK", "TASK-0001", "WARP-0001", risk_id="risk-0001")
    gate.record_decision(
        "decision-risk",
        task_id="TASK-0001",
        action="ACCEPT_RISK",
        rationale="Owner accepts the documented bounded risk.",
        evidence_refs=["evidence:validator-failure"],
        details={"risk_id": "risk-0001"},
    )
    assert gate.require("ACCEPT_RISK", "TASK-0001", "WARP-0001", risk_id="risk-0001")["allowed"]

    incomplete = dict(risk)
    incomplete["risk_id"] = "risk-0002"
    incomplete.pop("causal_chain")
    with pytest.raises(OwnerGateError, match="missing Throne risk fields"):
        gate.record_throne_risk(incomplete)


def test_throne_pass_without_proof_is_blocked_and_budget_overrun_pauses():
    with pytest.raises(OwnerGateError, match="PASS requires referenced proof"):
        OwnerGate.validate_throne_assessment({"verdict": "PASS_PROVEN", "evidence_refs": []})
    assert OwnerGate.validate_throne_assessment(
        {"verdict": "PASS_PROVEN", "evidence_refs": ["evidence:throne-postcheck"]}
    )["validated"]

    pause = OwnerGate.evaluate_budget_pause(
        estimated_cost=10,
        actual_cost=15.01,
        estimated_seconds=100,
        elapsed_seconds=200,
    )
    assert pause["verdict"] == "PAUSE"
    assert set(pause["reasons"]) == {"COST_EXCEEDED_150_PERCENT", "TIME_REACHED_200_PERCENT"}
