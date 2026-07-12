from __future__ import annotations

import json

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.checkpoint import (
    CheckpointError,
    CheckpointStore,
    CheckpointTamperError,
)


def _state(version: int, current: str) -> dict[str, object]:
    return {
        "task_id": "TASK-0001",
        "state_version": version,
        "current_state": current,
        "owner_decisions": [],
        "nested": {"preserved": [1, 2, 3]},
    }


def test_full_task_state_restore_is_exact_and_atomic(tmp_path):
    store = CheckpointStore(tmp_path)
    original = _state(4, "VALIDATION")
    store.create(
        "cp-validation",
        semantic_state="VALIDATION_COMPLETED",
        task_id="TASK-0001",
        task_state=original,
        git_state={"head": "a" * 40, "dirty": False},
        evidence_refs=["evidence:validation"],
    )
    target = tmp_path / "TASK_STATE.json"
    target.write_text(json.dumps(_state(5, "OWNER_REVIEW")), encoding="utf-8")

    receipt = store.restore(
        "cp-validation",
        target,
        expected_task_id="TASK-0001",
        expected_current_state_version=5,
    )

    assert receipt["verdict"] == "PASS_PROVEN"
    assert receipt["git_state_restore"] == "REFERENCE_ONLY_NOT_MUTATED"
    assert json.loads(target.read_text(encoding="utf-8")) == original


def test_partial_restore_returns_not_implemented_block_without_mutation(tmp_path):
    store = CheckpointStore(tmp_path)
    store.create(
        "cp-material",
        semantic_state="MATERIAL_CHANGE",
        task_id="TASK-0001",
        task_state=_state(2, "SAFE_EXECUTION"),
        git_state={"head": "b" * 40, "dirty": True},
        evidence_refs=["evidence:change"],
        dependencies={"files": ["a.txt", "b.txt"]},
    )
    target = tmp_path / "TASK_STATE.json"
    current = _state(3, "VALIDATION")
    target.write_text(json.dumps(current), encoding="utf-8")
    before = target.read_bytes()

    receipt = store.restore("cp-material", target, mode="PARTIAL", requested_keys=["nested"])

    assert receipt["verdict"] == "BLOCK"
    assert receipt["status"] == "NOT_IMPLEMENTED"
    assert receipt["reason_code"] == "PARTIAL_RESTORE_NOT_IMPLEMENTED"
    assert receipt["target_mutated"] is False
    assert target.read_bytes() == before


def test_checkpoint_tamper_and_restore_scope_are_blocked(tmp_path):
    checkpoints = tmp_path / "checkpoints"
    store = CheckpointStore(checkpoints)
    store.create(
        "cp-one",
        semantic_state="TASK_REGISTERED",
        task_id="TASK-0001",
        task_state=_state(1, "TASK_REGISTRATION"),
        git_state={"head": "c" * 40},
        evidence_refs=[],
    )
    path = checkpoints / "cp-one.json"
    path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(CheckpointTamperError):
        store.load("cp-one")

    clean_store = CheckpointStore(tmp_path / "clean-checkpoints")
    clean_store.create(
        "cp-two",
        semantic_state="FINAL_RESULT",
        task_id="TASK-0001",
        task_state=_state(9, "IMMUTABLE_EVIDENCE"),
        git_state={"head": "d" * 40},
        evidence_refs=["evidence:final"],
    )
    with pytest.raises(CheckpointError, match="outside allowed_restore_roots"):
        clean_store.restore("cp-two", tmp_path / "outside" / "TASK_STATE.json")
