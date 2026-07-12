from __future__ import annotations

import subprocess

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.owner_gate import OwnerDecisionRequired, OwnerGate
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.warp_manager import (
    WarpManager,
    WarpSafetyError,
    mark_disposable_fixture,
    prove_disposable_atomic_land_rollback,
)


def _git(repo, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repo, text=True, encoding="utf-8", capture_output=True, check=True, shell=False
    )
    return completed.stdout.strip()


def _repository(path):
    path.mkdir()
    _git(path, "init", "-b", "main")
    _git(path, "config", "user.name", "Corridor Test")
    _git(path, "config", "user.email", "corridor@example.invalid")
    (path / "payload.txt").write_text("base\n", encoding="utf-8")
    _git(path, "add", "payload.txt")
    _git(path, "commit", "-m", "base")
    return _git(path, "rev-parse", "HEAD")


def _decision(gate: OwnerGate, decision_id: str, action: str, *, warp: bool = True):
    return gate.record_decision(
        decision_id,
        task_id="TASK-0001",
        warp_id="WARP-0001" if warp else None,
        action=action,
        rationale=f"Fixture Owner decision: {action}",
        evidence_refs=["fixture:owner"],
    )


def test_exact_head_worktree_lifecycle_land_plan_and_safe_destroy(tmp_path):
    source = tmp_path / "source"
    managed = tmp_path / "warps"
    base = _repository(source)
    gate = OwnerGate(tmp_path / "gates")
    manager = WarpManager(source, managed, owner_gate=gate)

    created = manager.create("WARP-0001", "TASK-0001", base, scope=["ORGANS/MECHANICUS"])
    warp = managed / "WARP-0001"
    assert created.state == "CREATED"
    assert (warp / ".git").is_file()
    assert _git(warp, "rev-parse", "HEAD") == base
    detached = subprocess.run(
        ["git", "symbolic-ref", "-q", "HEAD"], cwd=warp, capture_output=True, text=True, check=False, shell=False
    )
    assert detached.returncode != 0

    with pytest.raises(OwnerDecisionRequired):
        manager.activate("WARP-0001")
    _decision(gate, "decision-launch", "APPROVE_LAUNCH", warp=False)
    assert manager.activate("WARP-0001").state == "ACTIVE"
    assert manager.execute("WARP-0001").state == "EXECUTING"
    (warp / "payload.txt").write_text("candidate\n", encoding="utf-8")
    assert manager.validate("WARP-0001", passed=True).state == "READY_FOR_REVIEW"

    _decision(gate, "decision-land-plan", "ALLOW_LAND_PREPARATION")
    plan = manager.prepare_land_plan("WARP-0001")
    assert plan["execution_performed"] is False
    assert plan["land_authorized"] is False
    assert plan["files_to_land"] == ["payload.txt"]
    assert _git(source, "rev-parse", "HEAD") == base

    _decision(gate, "decision-reject", "REJECT_RESULT")
    assert manager.reject("WARP-0001").state == "REJECTED"
    _decision(gate, "decision-discard", "DISCARD_WARP")
    assert manager.discard("WARP-0001").state == "DISCARDED"
    _decision(gate, "decision-destroy", "DESTROY_WARP")
    assert manager.destroy("WARP-0001").state == "DESTROYED"
    assert not warp.exists()
    assert _git(source, "rev-parse", "HEAD") == base


def test_create_blocks_dirty_or_stale_source_and_register_existing_verifies_detached(tmp_path):
    source = tmp_path / "source"
    managed = tmp_path / "warps"
    base = _repository(source)
    manager = WarpManager(source, managed)
    (source / "untracked.txt").write_text("dirty", encoding="utf-8")
    with pytest.raises(WarpSafetyError, match="not clean"):
        manager.create("WARP-DIRTY", "TASK-0001", base)
    (source / "untracked.txt").unlink()

    existing = managed / "WARP-EXISTING"
    _git(source, "worktree", "add", "--detach", str(existing), base)
    registered = manager.register_existing("WARP-EXISTING", "TASK-0001", existing, base)
    assert registered.git_metadata_verified is True
    assert registered.base_head == base

    (source / "payload.txt").write_text("stale candidate\n", encoding="utf-8")
    _git(source, "add", "payload.txt")
    _git(source, "commit", "-m", "new source head")
    with pytest.raises(WarpSafetyError, match="stale"):
        manager.create("WARP-STALE", "TASK-0001", base)


def test_atomic_land_and_rollback_proof_is_disposable_and_restores_ref(tmp_path):
    repo = tmp_path / "fixtures" / "repo"
    repo.parent.mkdir()
    base = _repository(repo)
    _git(repo, "branch", "landing-proof", base)
    (repo / "payload.txt").write_text("candidate\n", encoding="utf-8")
    _git(repo, "add", "payload.txt")
    _git(repo, "commit", "-m", "candidate")
    candidate = _git(repo, "rev-parse", "HEAD")

    with pytest.raises(WarpSafetyError, match="marked repository"):
        prove_disposable_atomic_land_rollback(
            repo,
            disposable_root=tmp_path / "fixtures",
            target_ref="refs/heads/landing-proof",
            candidate_head=candidate,
            expected_base=base,
        )
    mark_disposable_fixture(repo, tmp_path / "fixtures")
    proof = prove_disposable_atomic_land_rollback(
        repo,
        disposable_root=tmp_path / "fixtures",
        target_ref="refs/heads/landing-proof",
        candidate_head=candidate,
        expected_base=base,
    )

    assert proof["verdict"] == "PASS_PROVEN"
    assert proof["land_compare_and_swap_proven"] is True
    assert proof["rollback_compare_and_swap_proven"] is True
    assert _git(repo, "rev-parse", "refs/heads/landing-proof") == base


def test_failed_validation_is_contained_and_source_stays_unchanged(tmp_path):
    source = tmp_path / "source"
    managed = tmp_path / "warps"
    base = _repository(source)
    gate = OwnerGate(tmp_path / "gates")
    manager = WarpManager(source, managed, owner_gate=gate)
    manager.create("WARP-0001", "TASK-0001", base)
    _decision(gate, "decision-launch-failed", "APPROVE_LAUNCH", warp=False)
    manager.activate("WARP-0001")
    manager.execute("WARP-0001")

    record = manager.validate("WARP-0001", passed=False)

    assert record.state == "FAILED_CONTAINED"
    assert _git(source, "rev-parse", "HEAD") == base
    assert _git(source, "status", "--porcelain=v1") == ""
