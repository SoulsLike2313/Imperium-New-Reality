from __future__ import annotations

import json
from pathlib import Path

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.organ_ledger import CHECKS
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.organ_verdict import (
    OPERATIONAL,
    SCAFFOLD_ONLY,
    Verdict,
    VerdictContext,
    assess_check,
    build_validated_claim,
    enforce_throne_guard,
    evaluate_organ,
    sha256_file,
)


TASK_ID = "TASK-TRUTH-HARDENING-FIXTURE"
WARP_ID = "WARP-TRUTH-HARDENING-FIXTURE"
BASE_HEAD = "a" * 40
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
VALIDATOR = REPOSITORY_ROOT / "ORGANS/MECHANICUS/CORE_REFERENCE_CORRIDOR/organ_evidence_validator.py"


def _context(tmp_path: Path) -> VerdictContext:
    return VerdictContext(TASK_ID, WARP_ID, BASE_HEAD, tmp_path.resolve(), REPOSITORY_ROOT)


def _evidence(
    tmp_path: Path,
    organ_id: str,
    checks: dict[str, object],
    *,
    name: str,
    task_id: str = TASK_ID,
    warp_id: str = WARP_ID,
    base_head: str = BASE_HEAD,
) -> Path:
    path = tmp_path / f"{name}.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "phase1.organ_check_fixture.v0_1",
                "task_id": task_id,
                "warp_id": warp_id,
                "base_head": base_head,
                "organ_id": organ_id,
                "measured_checks": [
                    {
                        "check_id": check_id,
                        "expected": True,
                        "observed": value not in {False, Verdict.BLOCK.value, "FAIL"},
                        "evidence_id": f"fixture:{name}:{check_id}",
                        "verdict": Verdict.PASS_PROVEN.value,
                    }
                    for check_id, value in checks.items()
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return path


def _claim(
    path: Path,
    organ_id: str,
    check_id: str,
    *,
    classification: str = OPERATIONAL,
) -> dict:
    return build_validated_claim(
        path,
        validator_path=VALIDATOR,
        organ_id=organ_id,
        check_id=check_id,
        task_id=TASK_ID,
        warp_id=WARP_ID,
        base_head=BASE_HEAD,
        classification=classification,
    )


def _operational_claims(tmp_path: Path, organ_id: str) -> dict[str, dict]:
    checks = {check_id: Verdict.PASS_PROVEN.value for check_id in CHECKS[organ_id]}
    path = _evidence(tmp_path, organ_id, checks, name=f"{organ_id.lower()}-all")
    return {check_id: _claim(path, organ_id, check_id) for check_id in CHECKS[organ_id]}


def test_phase1_01_reference_without_validator_is_not_proven(tmp_path: Path) -> None:
    check_id = CHECKS["MECHANICUS"][0]
    path = _evidence(tmp_path, "MECHANICUS", {check_id: Verdict.PASS_PROVEN.value}, name="no-validator")
    result = assess_check(
        "MECHANICUS",
        check_id,
        {"evidence_ref": str(path), "evidence_sha256": sha256_file(path), "classification": OPERATIONAL},
        _context(tmp_path),
    )
    assert result["verdict"] == Verdict.NOT_PROVEN.value
    assert result["reasons"] == ["VALIDATOR_EXECUTION_MISSING"]


def test_phase1_02_missing_evidence_reference_is_not_proven(tmp_path: Path) -> None:
    result = assess_check(
        "MECHANICUS",
        CHECKS["MECHANICUS"][0],
        {"classification": OPERATIONAL},
        _context(tmp_path),
    )
    assert result["verdict"] == Verdict.NOT_PROVEN.value
    assert result["reasons"] == ["EVIDENCE_REF_MISSING"]


def test_phase1_03_modified_evidence_is_blocked(tmp_path: Path) -> None:
    check_id = CHECKS["MECHANICUS"][0]
    path = _evidence(tmp_path, "MECHANICUS", {check_id: Verdict.PASS_PROVEN.value}, name="tampered")
    claim = _claim(path, "MECHANICUS", check_id)
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    result = assess_check("MECHANICUS", check_id, claim, _context(tmp_path))
    assert result["verdict"] == Verdict.BLOCK.value
    assert result["reasons"] == ["EVIDENCE_HASH_MISMATCH"]


def test_phase1_04_validator_nonzero_is_blocked_with_process_metadata(tmp_path: Path) -> None:
    check_id = CHECKS["MECHANICUS"][0]
    path = _evidence(tmp_path, "MECHANICUS", {check_id: Verdict.BLOCK.value}, name="validator-red")
    claim = _claim(path, "MECHANICUS", check_id)
    result = assess_check("MECHANICUS", check_id, claim, _context(tmp_path))
    assert claim["validator_execution"]["exit_code"] == 2
    assert result["verdict"] == Verdict.BLOCK.value
    assert result["validator_executable_path"]
    assert result["exact_argv"][2] == "--evidence"
    assert result["finished_at_utc"]


def test_phase1_05_required_check_absent_is_not_proven_with_zero_exit(tmp_path: Path) -> None:
    first, absent = CHECKS["MECHANICUS"]
    path = _evidence(tmp_path, "MECHANICUS", {first: Verdict.PASS_PROVEN.value}, name="required-absent")
    claims = {first: _claim(path, "MECHANICUS", first), absent: _claim(path, "MECHANICUS", absent)}
    assert claims[absent]["validator_execution"]["exit_code"] == 0
    assert claims[absent]["validator_execution"]["result"]["verdict"] == Verdict.NOT_PROVEN.value
    result = evaluate_organ("MECHANICUS", CHECKS["MECHANICUS"], claims, _context(tmp_path))
    assert result["verdict"] == Verdict.NOT_PROVEN.value
    assert result["not_proven"][0]["check_id"] == absent


def test_phase1_06_scaffold_evidence_cannot_be_pass_proven(tmp_path: Path) -> None:
    claims = _operational_claims(tmp_path, "MECHANICUS")
    scaffold_check = CHECKS["MECHANICUS"][1]
    claims[scaffold_check]["classification"] = SCAFFOLD_ONLY
    result = evaluate_organ("MECHANICUS", CHECKS["MECHANICUS"], claims, _context(tmp_path))
    assert result["verdict"] == Verdict.NOT_PROVEN.value
    assert any(item["check_id"] == scaffold_check for item in result["not_proven"])


def test_phase1_07_accepted_debt_lowers_confidence_below_one(tmp_path: Path) -> None:
    result = evaluate_organ(
        "MECHANICUS",
        CHECKS["MECHANICUS"],
        _operational_claims(tmp_path, "MECHANICUS"),
        _context(tmp_path),
        accepted_debt=["OWNER_ACCEPTED_NON_CRITICAL_DEBT"],
    )
    assert result["verdict"] == Verdict.PASS_WITH_DEBT.value
    assert 0 < result["confidence"] < 1
    assert result["confidence_basis"]["accepted_debt_count"] == 1
    assert result["confidence_basis"]["required_checks_total"] == len(CHECKS["MECHANICUS"])
    assert result["confidence_basis"]["required_checks_passed"] == len(CHECKS["MECHANICUS"])
    assert result["confidence_basis"]["evidence_integrity"] == 1.0
    assert result["confidence_basis"]["reproducibility"] == 1.0


def test_phase1_08_throne_cannot_pass_over_critical_organ_block(tmp_path: Path) -> None:
    throne = evaluate_organ(
        "THRONE", CHECKS["THRONE"], _operational_claims(tmp_path, "THRONE"), _context(tmp_path)
    )
    assert throne["verdict"] == Verdict.PASS_PROVEN.value
    throne["organ_id"] = "THRONE"
    guarded = enforce_throne_guard(
        throne,
        [
            {
                "organ_id": "MECHANICUS",
                "check_results": [
                    {
                        "check_id": "typed_executor_validated",
                        "critical": True,
                        "verdict": Verdict.BLOCK.value,
                        "reasons": ["VALIDATOR_PROCESS_FAILED"],
                    }
                ],
            }
        ],
    )
    assert guarded["verdict"] == Verdict.BLOCK.value
    assert guarded["confidence"] == 0
    assert guarded["proven"]
    assert guarded["not_proven"]
    assert guarded["accepted_debt"] == []
    assert guarded["blocking_evidence"][0]["organ_id"] == "MECHANICUS"


def test_phase1_09_wrong_task_or_warp_binding_is_blocked(tmp_path: Path) -> None:
    check_id = CHECKS["MECHANICUS"][0]
    for field in ("task", "warp"):
        path = _evidence(
            tmp_path,
            "MECHANICUS",
            {check_id: Verdict.PASS_PROVEN.value},
            name=f"wrong-{field}",
            task_id="WRONG-TASK" if field == "task" else TASK_ID,
            warp_id="WRONG-WARP" if field == "warp" else WARP_ID,
        )
        result = assess_check("MECHANICUS", check_id, _claim(path, "MECHANICUS", check_id), _context(tmp_path))
        assert result["verdict"] == Verdict.BLOCK.value
        assert any("BINDING_MISMATCH" in reason for reason in result["reasons"])


def test_phase1_10_wrong_base_head_binding_is_blocked(tmp_path: Path) -> None:
    check_id = CHECKS["MECHANICUS"][0]
    path = _evidence(
        tmp_path,
        "MECHANICUS",
        {check_id: Verdict.PASS_PROVEN.value},
        name="wrong-base",
        base_head="b" * 40,
    )
    result = assess_check("MECHANICUS", check_id, _claim(path, "MECHANICUS", check_id), _context(tmp_path))
    assert result["verdict"] == Verdict.BLOCK.value
    assert result["reasons"] == ["BASE_HEAD_BINDING_MISMATCH"]


def test_phase1_11_declared_pass_cannot_override_failed_observation(tmp_path: Path) -> None:
    check_id = CHECKS["MECHANICUS"][0]
    path = _evidence(tmp_path, "MECHANICUS", {check_id: Verdict.BLOCK.value}, name="observed-failure")
    document = json.loads(path.read_text(encoding="utf-8"))
    document["measured_checks"][0]["verdict"] = Verdict.PASS_PROVEN.value
    path.write_text(json.dumps(document, sort_keys=True), encoding="utf-8")
    result = assess_check("MECHANICUS", check_id, _claim(path, "MECHANICUS", check_id), _context(tmp_path))
    assert result["verdict"] == Verdict.BLOCK.value
    assert result["reasons"] == ["VALIDATOR_PROCESS_FAILED"]
    measured = result["validator_execution"]["result"]["measured_check"]
    assert measured["expected"] is True
    assert measured["observed"] is False


def test_phase1_12_contradictory_evidence_blocks(tmp_path: Path) -> None:
    check_id = CHECKS["MECHANICUS"][0]
    path = _evidence(tmp_path, "MECHANICUS", {check_id: Verdict.PASS_PROVEN.value}, name="contradiction")
    document = json.loads(path.read_text(encoding="utf-8"))
    document["contradictions"] = ["fixture:counter-evidence"]
    path.write_text(json.dumps(document, sort_keys=True), encoding="utf-8")
    result = assess_check("MECHANICUS", check_id, _claim(path, "MECHANICUS", check_id), _context(tmp_path))
    assert result["verdict"] == Verdict.BLOCK.value
    assert result["validator_execution"]["result"]["reasons"] == ["CONTRADICTORY_EVIDENCE_PRESENT"]


def test_phase1_13_throne_cannot_pass_over_critical_not_proven(tmp_path: Path) -> None:
    throne = evaluate_organ(
        "THRONE", CHECKS["THRONE"], _operational_claims(tmp_path, "THRONE"), _context(tmp_path)
    )
    assert throne["verdict"] == Verdict.PASS_PROVEN.value
    guarded = enforce_throne_guard(
        throne,
        [
            {
                "organ_id": "ASTRONOMICON",
                "check_results": [
                    {
                        "check_id": "taskpack_digest_admitted",
                        "critical": True,
                        "verdict": Verdict.NOT_PROVEN.value,
                        "reasons": ["VALIDATOR_EXECUTION_MISSING"],
                    }
                ],
            }
        ],
    )
    assert guarded["verdict"] == Verdict.NOT_PROVEN.value
    assert guarded["confidence"] < 1.0
    assert guarded["not_proven"][-1]["reasons"] == ["CRITICAL_ORGAN_NOT_PROVEN"]


def test_phase1_14_unadmitted_validator_adapter_is_blocked(tmp_path: Path) -> None:
    check_id = CHECKS["MECHANICUS"][0]
    path = _evidence(tmp_path, "MECHANICUS", {check_id: Verdict.PASS_PROVEN.value}, name="rogue-validator")
    claim = _claim(path, "MECHANICUS", check_id)
    # Keep this fixture inside the admitted validator root so the assertion
    # exercises adapter admission, not the earlier path-scope guard.
    rogue = VALIDATOR.with_name("organ_verdict.py")
    claim["validator_execution"]["validator_adapter_path"] = str(rogue)
    claim["validator_execution"]["validator_adapter_sha256"] = sha256_file(rogue)
    claim["validator_execution"]["exact_argv"][1] = str(rogue)
    result = assess_check("MECHANICUS", check_id, claim, _context(tmp_path))
    assert result["verdict"] == Verdict.BLOCK.value
    assert result["reasons"] == ["VALIDATOR_ADAPTER_NOT_ADMITTED"]
