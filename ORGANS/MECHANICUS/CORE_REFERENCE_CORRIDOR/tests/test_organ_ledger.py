from __future__ import annotations

import json
from pathlib import Path

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.organ_ledger import GREAT_NINE, THRONE, OrganLedger, validate_ledger
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.organ_ledger import CHECKS
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.organ_verdict import Verdict, build_validated_claim


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
VALIDATOR = REPOSITORY_ROOT / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/organ_evidence_validator.py"
SCHEMA = REPOSITORY_ROOT / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/schemas/organ_participation.schema.json"


def test_complete_participation_is_structural_but_unvalidated_refs_are_not_proven(tmp_path):
    task = {
        "task_id": "TASK-FIXTURE",
        "base_head": "a" * 40,
        "organ_depth_plan": {},
        "warp": {"warp_id": "WARP-FIXTURE", "path": str(tmp_path)},
    }
    refs = {organ: [f"evidence:{organ}"] for organ in [*GREAT_NINE, THRONE]}
    ledger = OrganLedger(tmp_path / "ledger.json", "TASK-FIXTURE", evidence_root=tmp_path, validator_root=tmp_path)
    ledger.record_phase("PREFLIGHT", task, refs)
    data = ledger.record_phase("POSTCHECK", task, refs)
    assert validate_ledger(data) == []
    assert data["overall_verdict"] == Verdict.NOT_PROVEN.value
    assert all(item["verdict"] == Verdict.NOT_PROVEN.value for item in data["records"])

    missing = {**data, "records": [item for item in data["records"] if not (item["phase"] == "POSTCHECK" and item["organ_id"] == "CUSTODES")]}
    assert any("CUSTODES" in error for error in validate_ledger(missing))

    forged_throne = {**data, "records": [dict(item) for item in data["records"]]}
    throne = next(item for item in forged_throne["records"] if item["phase"] == "POSTCHECK" and item["organ_id"] == THRONE)
    throne["verdict"] = Verdict.PASS_PROVEN.value
    throne["confidence"] = 1.0
    assert any("PASS_PROVEN" in error for error in validate_ledger(forged_throne))

    forged_not_applicable = {**data, "records": [dict(item) for item in data["records"]]}
    record = forged_not_applicable["records"][0]
    record["verdict"] = Verdict.NOT_APPLICABLE_PROVEN.value
    assert any("applicability validator" in error for error in validate_ledger(forged_not_applicable))


def test_organ_specific_validator_runs_produce_schema_valid_records(tmp_path):
    task_id = "TASK-ORGAN-LEDGER-VALIDATED-FIXTURE"
    warp_id = "WARP-ORGAN-LEDGER-VALIDATED-FIXTURE"
    base_head = "c" * 40
    task = {
        "task_id": task_id,
        "base_head": base_head,
        "organ_depth_plan": {},
        "warp": {"warp_id": warp_id, "path": str(tmp_path)},
    }
    claims_by_organ = {}
    for organ_id in [*GREAT_NINE, THRONE]:
        evidence = tmp_path / f"{organ_id.lower()}.json"
        evidence.write_text(
            json.dumps(
                {
                    "schema_version": "phase1.organ_validation_fixture.v0_1",
                    "task_id": task_id,
                    "warp_id": warp_id,
                    "base_head": base_head,
                    "organ_id": organ_id,
                    "measured_checks": [
                        {
                            "check_id": check_id,
                            "expected": True,
                            "observed": True,
                            "evidence_id": f"fixture:{organ_id}:{check_id}",
                            "verdict": Verdict.BLOCK.value,
                        }
                        for check_id in CHECKS[organ_id]
                    ],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        claims_by_organ[organ_id] = {
            "claims": {
                check_id: build_validated_claim(
                    evidence,
                    validator_path=VALIDATOR,
                    organ_id=organ_id,
                    check_id=check_id,
                    task_id=task_id,
                    warp_id=warp_id,
                    base_head=base_head,
                )
                for check_id in CHECKS[organ_id]
            }
        }

    ledger = OrganLedger(
        tmp_path / "validated-ledger.json",
        task_id,
        evidence_root=tmp_path,
        validator_root=REPOSITORY_ROOT,
    )
    data = ledger.record_phase("POSTCHECK", task, claims_by_organ)
    assert data["overall_verdict"] == Verdict.PASS_PROVEN.value
    assert validate_ledger(data, require_phases=("POSTCHECK",)) == []
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    for record in data["records"]:
        assert set(schema["required"]) <= set(record)
        assert record["verdict"] in schema["properties"]["verdict"]["enum"]
        assert record["validator_id"] == "organ_evidence_validator_v1"
        assert record["validator_version"] == "1.0.0"
        assert Path(record["validator_executable_path"]).is_absolute()
        assert len(record["validator_sha256"]) == 64
        assert record["exit_code"] == 0
        assert len(record["measured_checks"]) == len(record["required_checks"])
        assert record["failed_checks"] == []
        assert all(item["observed"] is True for item in record["measured_checks"])
