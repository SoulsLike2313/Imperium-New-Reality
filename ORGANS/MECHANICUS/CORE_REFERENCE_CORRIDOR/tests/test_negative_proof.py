from __future__ import annotations

import json
from pathlib import Path

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.negative_proof_runner import (
    CATALOG_RELATIVE,
    run_negative_suite,
)
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.negative_proof_validator import (
    canonical_hash,
    validate_receipt,
)
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.registry import sha256_file
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.root_resolver import (
    resolve_repository_context,
)


@pytest.fixture(scope="module")
def phase2_suite(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    context = resolve_repository_context(Path(__file__).resolve())
    report = tmp_path_factory.mktemp("phase2-negative-proof") / "report"
    index = run_negative_suite(
        report=report,
        worktree=Path(context.worktree_root),
        reality=Path(context.reality_root),
    )
    return report, index


def _mutation(report: Path, folder: str) -> dict:
    return json.loads(
        (report / "PHASE_2_MUTATIONS" / folder / "MUTATION_RECEIPT.json").read_text(
            encoding="utf-8"
        )
    )


def test_phase2_01_expected_and_actual_have_independent_sources(
    phase2_suite: tuple[Path, dict],
) -> None:
    _, index = phase2_suite
    expected_path = Path(index["expected_source"]["path"])
    actual_path = Path(index["actual_source"]["path"])

    assert expected_path != actual_path
    assert expected_path.name == CATALOG_RELATIVE.name
    assert index["source_separation"] == {
        "different_files": True,
        "validator_imports_expectation_catalog": False,
    }
    assert index["expected_source"]["sha256"] == sha256_file(expected_path)
    assert index["actual_source"]["sha256"] == sha256_file(actual_path)


def test_phase2_02_all_twenty_scenarios_have_own_observation_receipt(
    phase2_suite: tuple[Path, dict],
) -> None:
    report, index = phase2_suite
    refs = [row["observation_receipt"] for row in index["scenarios"]]

    assert index["scenario_count"] == 20
    assert len(refs) == len(set(refs)) == 20
    for row in index["scenarios"]:
        path = report / row["observation_receipt"]
        receipt = json.loads(path.read_text(encoding="utf-8"))
        assert sha256_file(path) == row["observation_sha256"]
        assert receipt["scenario_id"] == row["scenario_id"]
        assert receipt["observations"]
        assert receipt["receipt_hash"] == canonical_hash(receipt)


def test_phase2_03_actual_is_recomputed_from_observations_not_expected(
    phase2_suite: tuple[Path, dict], tmp_path: Path
) -> None:
    report, index = phase2_suite
    row = next(item for item in index["scenarios"] if item["scenario_id"] == "timeout")
    receipt = json.loads((report / row["scenario_receipt"]).read_text(encoding="utf-8"))
    original_actual = receipt["actual_verdict"]
    receipt["expected_verdict"] = "MUTATED_EXPECTATION_MUST_NOT_DRIVE_ACTUAL"
    receipt["receipt_hash"] = canonical_hash(receipt)

    result = validate_receipt(
        receipt,
        report,
        task_id=receipt["task_id"],
        warp_id=receipt["warp_id"],
        base_head=receipt["base_head"],
    )

    assert result["actual_verdict"] == original_actual
    assert result["comparison_match"] is False
    assert result["validation_verdict"] == "BLOCK"


def test_phase2_04_declared_actual_cannot_override_observations(
    phase2_suite: tuple[Path, dict]
) -> None:
    report, index = phase2_suite
    row = next(
        item for item in index["scenarios"] if item["scenario_id"] == "dirty_reality"
    )
    receipt = json.loads((report / row["scenario_receipt"]).read_text(encoding="utf-8"))
    observation_actual = receipt["actual_verdict"]
    receipt["actual_verdict"] = "PASS_PROVEN"
    receipt["receipt_hash"] = canonical_hash(receipt)

    result = validate_receipt(
        receipt,
        report,
        task_id=receipt["task_id"],
        warp_id=receipt["warp_id"],
        base_head=receipt["base_head"],
    )

    assert result["actual_verdict"] == observation_actual
    assert result["declared_actual_match"] is False
    assert result["validation_verdict"] == "BLOCK"


def test_phase2_05_missing_observations_are_not_proven(
    phase2_suite: tuple[Path, dict]
) -> None:
    report, index = phase2_suite
    row = index["scenarios"][0]
    receipt = json.loads((report / row["scenario_receipt"]).read_text(encoding="utf-8"))
    receipt["observations"] = {}
    receipt["receipt_hash"] = canonical_hash(receipt)

    result = validate_receipt(
        receipt,
        report,
        task_id=receipt["task_id"],
        warp_id=receipt["warp_id"],
        base_head=receipt["base_head"],
    )

    assert result["actual_verdict"] == "NOT_PROVEN_OBSERVATIONS_MISSING"
    assert result["validation_verdict"] == "BLOCK"


def test_phase2_06_validator_checks_isolation_reality_hash_process_and_localization(
    phase2_suite: tuple[Path, dict]
) -> None:
    report, index = phase2_suite
    required = {
        "fixture_isolation",
        "reality_unchanged",
        "observation_evidence_hash",
        "observer_identity",
        "expected_entry_binding",
        "process_outcome_measured",
        "failure_localized",
    }
    for row in index["scenarios"]:
        validation = json.loads((report / row["validation_receipt"]).read_text(encoding="utf-8"))
        checks = validation["validator_result"]["checks"]
        assert required.issubset(checks)
        assert all(checks[name] for name in required)
        assert validation["validator_result"]["actual_source"] == "MEASURED_OBSERVATIONS_ONLY"


def test_phase2_07_mutation_broken_organ_verdict_red_then_green(
    phase2_suite: tuple[Path, dict]
) -> None:
    report, _ = phase2_suite
    receipt = _mutation(report, "01_broken_organ_verdict_calculation")

    assert receipt["red"]["actual_verdict"] == "PASS_PROVEN"
    assert receipt["red"]["suite_verdict"] == "BLOCK"
    assert receipt["green_after_restore"]["actual_verdict"] == "BLOCK_MISSING_ORGAN_PROVEN"
    assert receipt["verdict"] == "RED_DETECTED_GREEN_RESTORED"


def test_phase2_08_mutation_allow_unknown_capability_red_then_green(
    phase2_suite: tuple[Path, dict]
) -> None:
    report, _ = phase2_suite
    receipt = _mutation(report, "02_allow_unknown_capability")

    assert receipt["red"]["actual_verdict"] == "BLOCK_UNKNOWN_CAPABILITY_EXECUTED"
    assert receipt["red"]["suite_verdict"] == "BLOCK"
    assert receipt["green_after_restore"]["actual_verdict"] == "BLOCK_UNREGISTERED_CAPABILITY_PROVEN"
    assert receipt["verdict"] == "RED_DETECTED_GREEN_RESTORED"


def test_phase2_09_mutation_substitute_evidence_hash_red_then_green(
    phase2_suite: tuple[Path, dict]
) -> None:
    report, _ = phase2_suite
    receipt = _mutation(report, "03_substitute_evidence_hash")

    assert receipt["red"]["actual_verdict"] == "BLOCK_OBSERVATION_EVIDENCE_HASH_MISMATCH"
    assert receipt["red"]["suite_verdict"] == "BLOCK"
    assert receipt["green_after_restore"]["actual_verdict"] == "BLOCK_EVIDENCE_TAMPERING_PROVEN"
    assert receipt["verdict"] == "RED_DETECTED_GREEN_RESTORED"


def test_phase2_10_suite_acceptance_preserves_reality_and_campaign_partial(
    phase2_suite: tuple[Path, dict]
) -> None:
    _, index = phase2_suite

    assert index["phase_acceptance"] == "NEGATIVE_PROOF_HARDENING_PASS"
    assert index["reality"]["unchanged_and_clean"] is True
    assert index["campaign_verdict"] == "TRUTH_HARDENING_PARTIAL_NOT_READY"
    assert index["phase_3_started"] is False
    assert all(row["validation_verdict"] == "PASS" for row in index["scenarios"])
    assert all(row["red_detected"] and row["green_restored"] for row in index["mutations"])


def test_phase2_11_validation_runner_has_no_expected_equals_actual_shortcut() -> None:
    root = Path(__file__).resolve().parents[4]
    source = (
        root / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/validation_runner.py"
    ).read_text(encoding="utf-8")

    assert "actual = expected" not in source
    assert "def _negative_receipt" not in source
    assert "run_negative_suite(" in source
