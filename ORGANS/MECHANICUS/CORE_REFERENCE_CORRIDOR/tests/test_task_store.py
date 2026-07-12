from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.constants import TASK_STATE_ROUTE
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.errors import (
    ConcurrentUpdateError,
    GateDeniedError,
    InvalidTransitionError,
    StaleBaseError,
    TaskAlreadyExistsError,
    TaskStoreError,
    TaskValidationError,
)
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.task_store import TaskStore


BASE_HEAD = "a" * 40


def _task(**overrides: Any) -> dict[str, Any]:
    task: dict[str, Any] = {
        "task_id": "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001",
        "task_type": "SERVITOR_TASK_PACK",
        "owner_intent": {"statement": "Build the bounded reference corridor"},
        "created_at_utc": "2026-07-12T20:35:39Z",
        "base_head": BASE_HEAD,
        "branch": "servitor/reference-corridor",
        "scope": {"mode": "EXTERNAL_EXACT_HEAD_GIT_WORKTREE"},
        "allowed_read_roots": ["E:/fixture/reality", "E:/fixture/warp"],
        "allowed_write_roots": ["E:/fixture/warp"],
        "acceptance_tests": ["task_state_is_atomic"],
        "confidence_components": {},
        "selected_strategy": None,
        "current_state": "OWNER_INTENT",
        "state_version": 1,
        "organ_depth_plan": {},
        "owner_decisions": [],
        "created_by": "CODEX",
    }
    task.update(overrides)
    return task


def test_create_load_and_versioned_single_task(tmp_path: Path) -> None:
    store = TaskStore(tmp_path, expected_base_head=BASE_HEAD)

    created = store.create(_task())
    loaded = TaskStore(tmp_path, expected_base_head=BASE_HEAD).load()

    assert created == loaded
    assert loaded["state_version"] == 1
    assert loaded["current_state"] == "OWNER_INTENT"
    assert len(store.load_transition_log()) == 1
    with pytest.raises(TaskAlreadyExistsError):
        store.create(_task(task_id="ANOTHER"))


def test_missing_required_field_is_rejected(tmp_path: Path) -> None:
    task = _task()
    del task["owner_intent"]

    with pytest.raises(TaskValidationError, match="owner_intent"):
        TaskStore(tmp_path).create(task)


def test_transition_route_and_owner_gate_are_default_deny(tmp_path: Path) -> None:
    store = TaskStore(tmp_path, expected_base_head=BASE_HEAD)
    state = store.create(_task())

    with pytest.raises(InvalidTransitionError):
        store.transition("SPECIFICATION", expected_version=state["state_version"])

    for target in TASK_STATE_ROUTE[1:8]:
        state = store.transition(target, expected_version=state["state_version"])
    assert state["current_state"] == "OWNER_LAUNCH_APPROVAL"

    with pytest.raises(GateDeniedError):
        store.transition("EXACT_HEAD_WARP", expected_version=state["state_version"])

    state = store.transition(
        "EXACT_HEAD_WARP",
        expected_version=state["state_version"],
        owner_decision={"decision_id": "OWNER-1", "action": "approve_launch"},
        gate_evidence={"instruction_ref": "TASK_START_ACK.json"},
    )
    assert state["state_version"] == 9
    assert state["owner_decisions"][-1]["decision"] == "APPROVE_LAUNCH"
    assert store.allowed_targets() == ("SAFE_EXECUTION",)


def test_stale_base_blocks_without_changing_state(tmp_path: Path) -> None:
    store = TaskStore(tmp_path)
    store.create(_task())

    with pytest.raises(StaleBaseError):
        store.transition(
            "TASK_REGISTRATION",
            expected_version=1,
            expected_base_head="b" * 40,
        )
    assert store.load()["state_version"] == 1


def test_restart_recovers_durable_pending_transaction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = TaskStore(tmp_path, expected_base_head=BASE_HEAD)
    store.create(_task())

    def simulate_crash_before_marker_removal() -> None:
        raise OSError("simulated process interruption")

    monkeypatch.setattr(store, "_remove_pending_locked", simulate_crash_before_marker_removal)
    with pytest.raises(TaskStoreError, match="recovery marker retained"):
        store.transition("TASK_REGISTRATION", expected_version=1)
    assert store.pending_path.is_file()

    restarted = TaskStore(tmp_path, expected_base_head=BASE_HEAD)
    recovered = restarted.load()
    assert recovered["current_state"] == "TASK_REGISTRATION"
    assert recovered["state_version"] == 2
    assert not restarted.pending_path.exists()
    assert len(restarted.load_transition_log()) == 2


def test_concurrent_writers_allow_only_one_expected_version(tmp_path: Path) -> None:
    TaskStore(tmp_path, expected_base_head=BASE_HEAD).create(_task())
    barrier = threading.Barrier(3)

    def attempt() -> str:
        store = TaskStore(tmp_path, expected_base_head=BASE_HEAD)
        barrier.wait(timeout=5)
        try:
            store.transition("TASK_REGISTRATION", expected_version=1)
        except ConcurrentUpdateError:
            return "VERSION_CONFLICT"
        return "COMMITTED"

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(attempt) for _ in range(2)]
        barrier.wait(timeout=5)
        outcomes = sorted(future.result(timeout=5) for future in futures)

    assert outcomes == ["COMMITTED", "VERSION_CONFLICT"]
    assert TaskStore(tmp_path).load()["state_version"] == 2
