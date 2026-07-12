from __future__ import annotations

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.organ_ledger import GREAT_NINE, THRONE, OrganLedger, validate_ledger


def test_complete_participation_passes_and_missing_organ_or_throne_proof_blocks(tmp_path):
    task = {"task_id": "TASK-FIXTURE", "base_head": "a" * 40, "organ_depth_plan": {}}
    refs = {organ: [f"evidence:{organ}"] for organ in [*GREAT_NINE, THRONE]}
    ledger = OrganLedger(tmp_path / "ledger.json", "TASK-FIXTURE")
    ledger.record_phase("PREFLIGHT", task, refs)
    data = ledger.record_phase("POSTCHECK", task, refs)
    assert validate_ledger(data) == []

    missing = {**data, "records": [item for item in data["records"] if not (item["phase"] == "POSTCHECK" and item["organ_id"] == "CUSTODES")]}
    assert any("CUSTODES" in error for error in validate_ledger(missing))

    no_throne_proof = {**data, "records": [dict(item) for item in data["records"]]}
    throne = next(item for item in no_throne_proof["records"] if item["phase"] == "POSTCHECK" and item["organ_id"] == THRONE)
    throne["evidence_refs"] = []
    assert any("Throne PASS has no evidence" in error for error in validate_ledger(no_throne_proof))

