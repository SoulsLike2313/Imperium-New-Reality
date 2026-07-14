from __future__ import annotations

import copy

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase7_claim_reconciliation import (
    BLOCKED,
    NOT_READY,
    PASS_PROVEN,
    PASS_WITH_DEBT,
    calculate_campaign_verdict,
    current_organ_status,
    extract_verdict,
)
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.phase7_disk_auditor import (
    GREAT_NINE,
    REQUIRED_DEBT_IDS,
    THRONE,
    canonical_registry_digest,
    claim_status_errors,
    self_test,
)


def test_phase7_verdict_extraction_accepts_historical_key_shapes() -> None:
    assert extract_verdict({"PHASE_VERDICT": "A"}) == "A"
    assert extract_verdict({"phase_verdict": "B"}) == "B"
    assert extract_verdict({"verdict": "C"}) == "C"
    assert extract_verdict({}) == "NOT_PROVEN"


def test_phase7_campaign_verdict_is_fail_closed() -> None:
    good = [{"verdict": "PASS_PROVEN"} for _ in range(6)]
    assert calculate_campaign_verdict(good, blockers=[], debts=[]) == PASS_PROVEN
    assert calculate_campaign_verdict(good, blockers=[], debts=[{"x": 1}]) == PASS_WITH_DEBT
    assert calculate_campaign_verdict(good, blockers=["x"], debts=[]) == BLOCKED
    assert (
        calculate_campaign_verdict(
            [*good[:-1], {"verdict": "NOT_PROVEN"}],
            blockers=[],
            debts=[],
        )
        == NOT_READY
    )


def test_phase7_historical_organ_rows_are_never_promoted() -> None:
    ledger = {
        "records": [
            {
                "organ_id": organ_id,
                "phase": "POSTCHECK",
                "verdict": "PASS_PROVEN",
                "confidence": 1.0,
            }
            for organ_id in [*GREAT_NINE, THRONE]
        ]
    }
    current = current_organ_status(ledger)
    assert set(current) == {*GREAT_NINE, THRONE}
    assert all(row["verdict"] == "NOT_PROVEN" for row in current.values())
    assert all(
        row["claim_state"] == "HISTORICAL_NOT_PROMOTED"
        for row in current.values()
    )
    assert all(row["historical_verdict"] == "PASS_PROVEN" for row in current.values())


def _valid_status() -> dict:
    return {
        "authority": "PHASE7_CURRENT_CLAIM_AUTHORITY",
        "implementation_head": "a" * 40,
        "campaign_verdict": PASS_WITH_DEBT,
        "organ_ring_verdict": "NOT_PROVEN",
        "organs": {
            organ_id: {
                "verdict": "NOT_PROVEN",
                "claim_state": "HISTORICAL_NOT_PROMOTED",
            }
            for organ_id in [*GREAT_NINE, THRONE]
        },
        "debts": [{"debt_id": item} for item in sorted(REQUIRED_DEBT_IDS)],
        "scope_boundary": {
            "reference_corridor_only": True,
            "core_v1_complete": False,
            "all_organs_operational": False,
            "land_authorized": False,
            "master_mutated": False,
        },
        "superseded_claims": [
            {"path": "OWNER_RESULT.md"},
            {"path": "OWNER_REVIEW_READY_RECEIPT.json"},
            {"path": "ORGAN_PARTICIPATION_LEDGER.json"},
        ],
    }


def test_phase7_independent_claim_status_rejects_overclaim_mutations() -> None:
    status = _valid_status()
    assert claim_status_errors(status, "a" * 40) == []

    promoted = copy.deepcopy(status)
    promoted["organs"]["THRONE"]["verdict"] = "PASS_PROVEN"
    assert any("ORGAN_CURRENT_OVERCLAIM" in error for error in claim_status_errors(promoted, "a" * 40))

    no_ui_debt = copy.deepcopy(status)
    no_ui_debt["debts"] = [
        row
        for row in no_ui_debt["debts"]
        if row["debt_id"] != "LIVE_UI_NONBLOCKING_ACTION_DEFERRED"
    ]
    assert any("REQUIRED_DEBTS_MISSING" in error for error in claim_status_errors(no_ui_debt, "a" * 40))

    core_complete = copy.deepcopy(status)
    core_complete["scope_boundary"]["core_v1_complete"] = True
    assert "SCOPE_BOUNDARY_INVALID" in claim_status_errors(core_complete, "a" * 40)


def test_phase7_registry_digest_mutation_is_detected() -> None:
    registry = {"schema_version": "x", "capabilities": []}
    registry["registry_digest"] = canonical_registry_digest(registry)
    tampered = copy.deepcopy(registry)
    tampered["capabilities"].append({"capability_id": "ROGUE"})
    assert canonical_registry_digest(tampered) != tampered["registry_digest"]


def test_phase7_disk_auditor_self_test_detects_all_mutations() -> None:
    result = self_test()
    assert result["verdict"] == "MUTATIONS_DETECTED"
    assert result["count"] == 5
