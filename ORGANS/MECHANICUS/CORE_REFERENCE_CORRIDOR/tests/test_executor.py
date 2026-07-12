from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.executor import ExecutionBlocked, execute_capability
from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.registry import CapabilityRegistry, RegistryError, canonical_digest, sha256_file


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, shell=False, check=True, capture_output=True, text=True)
    return result.stdout.strip()


@pytest.fixture()
def execution_fixture(tmp_path: Path):
    reality = tmp_path / "reality"
    warp = tmp_path / "warp"
    reality.mkdir()
    _git(reality, "init", "-b", "master")
    _git(reality, "config", "user.name", "Executor Test")
    _git(reality, "config", "user.email", "executor@example.invalid")
    (reality / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(reality, "add", "tracked.txt")
    _git(reality, "commit", "-m", "base")
    base = _git(reality, "rev-parse", "HEAD")
    _git(reality, "worktree", "add", "--detach", str(warp), base)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    return reality, warp, scripts, base


def _registry(path: Path, script: Path, reality: Path, warp: Path, *, effect: str = "READ_ONLY", timeout: float = 3, capability_id: str = "FIXTURE") -> CapabilityRegistry:
    executable = Path(sys.executable).resolve()
    entry = {
        "capability_id": capability_id,
        "type": "PYTHON_SCRIPT",
        "adapter_id": "FIXED_TEST_ADAPTER",
        "adapter_path": str(script),
        "adapter_sha256": sha256_file(script),
        "executable_path": str(executable),
        "executable_sha256": sha256_file(executable),
        "version": "fixture",
        "admission_state": "ACTIVE",
        "declared_effect": effect,
        "actual_effect_class": effect,
        "allowed_operations": ["run"],
        "allowed_read_roots": [str(reality), str(warp)],
        "allowed_write_roots": [str(warp / "allowed")] if effect != "READ_ONLY" else [],
        "timeout_seconds": timeout,
        "environment_profile": "FIXTURE_MINIMAL",
        "cost_model": {},
        "trust_level": "TEST_ONLY",
        "last_validation": "TEST",
        "quarantine_reason": "",
        "fixed_argv": [str(script)],
        "parameter_schema": {"type": "object", "additionalProperties": False},
    }
    data = {
        "schema_version": "imperium.core_reference_corridor.capability_registry.v0_1",
        "registry_id": "FIXTURE",
        "task_id": "TASK-FIXTURE",
        "default_policy": "DENY",
        "capabilities": [entry],
        "ui_actions": [],
    }
    data["registry_digest"] = canonical_digest(data)
    registry = CapabilityRegistry(path)
    registry.data = data
    return registry


def _state(warp: Path, base: str) -> dict:
    return {"task_id": "TASK-FIXTURE", "base_head": base, "warp": {"warp_id": "WARP-FIXTURE", "path": str(warp)}, "owner_decisions": []}


def test_exact_read_only_happy_path(execution_fixture):
    reality, warp, scripts, base = execution_fixture
    script = scripts / "happy.py"
    script.write_text('import json; print(json.dumps({"verdict":"PASS_PROVEN","value":7}))\n', encoding="utf-8")
    receipt = execute_capability(
        registry=_registry(scripts / "registry.json", script, reality, warp),
        capability_id="FIXTURE", operation="run", params={}, cwd=warp,
        task_state=_state(warp, base), reality_root=reality, worktree_root=warp,
        guard_roots=[reality, warp],
    )
    assert receipt["verdict"] == "PASS_PROVEN"
    assert receipt["result"]["value"] == 7
    assert receipt["pre_git_state"]["reality"] == receipt["post_git_state"]["reality"]


def test_unknown_and_malicious_runner_are_default_denied_without_execution(execution_fixture):
    reality, warp, scripts, base = execution_fixture
    sentinel = warp / "sentinel.txt"
    script = scripts / "malicious.ps1"
    script.write_text(f"Set-Content -LiteralPath '{sentinel}' -Value pwned\n", encoding="utf-8")
    registry = _registry(scripts / "registry.json", script, reality, warp, capability_id="SAFE_ONLY")
    with pytest.raises(RegistryError, match="CAPABILITY_NOT_REGISTERED"):
        execute_capability(
            registry=registry, capability_id="MALICIOUS_POWERSHELL", operation="run", params={}, cwd=warp,
            task_state=_state(warp, base), reality_root=reality, worktree_root=warp,
        )
    assert not sentinel.exists()


def test_unauthorized_write_is_observed_and_blocked(execution_fixture):
    reality, warp, scripts, base = execution_fixture
    script = scripts / "write.py"
    script.write_text('from pathlib import Path; Path("outside.txt").write_text("x"); print("{}")\n', encoding="utf-8")
    receipt = execute_capability(
        registry=_registry(scripts / "registry.json", script, reality, warp, effect="MUTATING"),
        capability_id="FIXTURE", operation="run", params={}, cwd=warp,
        task_state=_state(warp, base), reality_root=reality, worktree_root=warp,
        guard_roots=[reality, warp],
    )
    assert receipt["verdict"] == "BLOCK"
    assert "UNAUTHORIZED_WRITE_PATH" in receipt["block_reasons"]
    assert not (reality / "outside.txt").exists()


def test_timeout_kills_process_tree_and_crash_is_blocked(execution_fixture):
    reality, warp, scripts, base = execution_fixture
    sleeper = scripts / "sleep.py"
    sleeper.write_text("import time; time.sleep(10)\n", encoding="utf-8")
    timed = execute_capability(
        registry=_registry(scripts / "registry-timeout.json", sleeper, reality, warp, timeout=0.2),
        capability_id="FIXTURE", operation="run", params={}, cwd=warp,
        task_state=_state(warp, base), reality_root=reality, worktree_root=warp,
        guard_roots=[reality, warp],
    )
    assert timed["verdict"] == "BLOCK"
    assert timed["timeout_triggered"] is True
    assert timed["process_termination_result"]["tree_terminated"] is True

    crash = scripts / "crash.py"
    crash.write_text("raise SystemExit(9)\n", encoding="utf-8")
    failed = execute_capability(
        registry=_registry(scripts / "registry-crash.json", crash, reality, warp),
        capability_id="FIXTURE", operation="run", params={}, cwd=warp,
        task_state=_state(warp, base), reality_root=reality, worktree_root=warp,
        guard_roots=[reality, warp],
    )
    assert failed["verdict"] == "BLOCK"
    assert failed["exit_code"] == 9


def test_mutation_from_reality_is_blocked_before_process_start(execution_fixture):
    reality, warp, scripts, base = execution_fixture
    sentinel = reality / "must-not-exist.txt"
    script = scripts / "direct.py"
    script.write_text(f'from pathlib import Path; Path(r"{sentinel}").write_text("bad")\n', encoding="utf-8")
    registry = _registry(scripts / "registry.json", script, reality, warp, effect="MUTATING")
    with pytest.raises(ExecutionBlocked, match="MUTATION_OUTSIDE_ACTIVE_WARP"):
        execute_capability(
            registry=registry, capability_id="FIXTURE", operation="run", params={}, cwd=reality,
            task_state=_state(warp, base), reality_root=reality, worktree_root=warp,
        )
    assert not sentinel.exists()


def test_deterministic_replay_from_two_clean_clones(execution_fixture):
    reality, _, scripts, base = execution_fixture
    clone_one = reality.parent / "clone-one"
    clone_two = reality.parent / "clone-two"
    _git(reality.parent, "clone", "--no-local", str(reality), str(clone_one))
    _git(reality.parent, "clone", "--no-local", str(reality), str(clone_two))
    script = scripts / "replay.py"
    script.write_text('import json; print(json.dumps({"verdict":"PASS_PROVEN","deterministic":true}))\n'.replace("true", "True"), encoding="utf-8")

    receipts = []
    for index, clone in enumerate((clone_one, clone_two), start=1):
        receipts.append(
            execute_capability(
                registry=_registry(scripts / f"registry-{index}.json", script, clone, clone),
                capability_id="FIXTURE", operation="run", params={}, cwd=clone,
                task_state=_state(clone, base), reality_root=clone, worktree_root=clone,
                guard_roots=[clone],
            )
        )
    assert all(item["verdict"] == "PASS_PROVEN" for item in receipts)
    assert receipts[0]["stdout_hash"] == receipts[1]["stdout_hash"]
    assert receipts[0]["result"] == receipts[1]["result"]
    assert _git(reality, "status", "--porcelain=v1") == ""
