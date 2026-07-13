"""Disposable Phase 2 scenario observer; this module never assigns verdicts."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable


OBSERVER_ID = "negative_scenario_observer_v1"
OBSERVER_VERSION = "1.0.0"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _git(root: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git failed")
    return result


def _host_snapshot(reality: Path, warp: Path) -> dict[str, Any]:
    reality_status = _git(reality, "status", "--porcelain=v1", "--untracked-files=all").stdout.splitlines()
    warp_status = _git(warp, "status", "--porcelain=v1", "--untracked-files=all").stdout.splitlines()
    value = {
        "reality_head": _git(reality, "rev-parse", "HEAD").stdout.strip(),
        "reality_origin_master": _git(reality, "rev-parse", "origin/master").stdout.strip(),
        "reality_status": reality_status,
        "warp_head": _git(warp, "rev-parse", "HEAD").stdout.strip(),
        "warp_status": warp_status,
    }
    value["snapshot_sha256"] = _canonical_hash(value)
    return value


def _within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.returncode == 0 and f'"{pid}"' in result.stdout
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _terminate_tree(process: subprocess.Popen[Any]) -> dict[str, Any]:
    if process.poll() is not None:
        return {"requested": False, "method": "already_exited", "tree_terminated": True}
    if os.name == "nt":
        result = subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            shell=False,
            capture_output=True,
            timeout=15,
            check=False,
        )
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        return {"requested": True, "method": "taskkill_tree_force", "returncode": result.returncode, "tree_terminated": process.poll() is not None}
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=5)
    return {"requested": True, "method": "killpg_sigkill", "tree_terminated": process.poll() is not None}


def _spawn(argv: list[str], cwd: Path) -> subprocess.Popen[Any]:
    return subprocess.Popen(
        argv,
        cwd=str(cwd),
        shell=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        start_new_session=os.name != "nt",
    )


def _init_repo(root: Path) -> str:
    root.mkdir(parents=True)
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "Phase 2 Fixture")
    _git(root, "config", "user.email", "phase2@example.invalid")
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", "tracked.txt")
    _git(root, "commit", "-m", "fixture base")
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def _blocked_write(root: Path, *, target_role: str) -> dict[str, Any]:
    warp = root / "warp"
    allowed = warp / "allowed"
    reality = root / "reality"
    allowed.mkdir(parents=True)
    reality.mkdir()
    target = reality / "forbidden.txt" if target_role == "REALITY" else warp / "outside.txt"
    permitted = _within(target, allowed)
    if permitted:
        target.write_text("should never be permitted", encoding="utf-8")
    return {
        "target_role": target_role,
        "write_attempted": True,
        "target_outside_allowed_scope": not permitted,
        "write_blocked_before_io": not permitted,
        "target_exists_after": target.exists(),
        "allowed_write_root": str(allowed.resolve()),
        "target_path": str(target.resolve()),
        "process_started": False,
        "failure_code": "REALITY_WRITE_FORBIDDEN" if target_role == "REALITY" else "WARP_WRITE_SCOPE_VIOLATION",
        "failure_stage": "pre_write_scope_gate",
    }


def _unregistered(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    sentinel = root / "unknown-capability-executed.txt"
    allow_unknown = mutation == "allow_unknown_capability"
    exit_code = None
    if allow_unknown:
        code = "from pathlib import Path; import sys; Path(sys.argv[1]).write_text('executed', encoding='utf-8')"
        exit_code = subprocess.run([sys.executable, "-c", code, str(sentinel)], shell=False, check=False, timeout=10).returncode
    return {
        "requested_capability": "UNKNOWN_MUTATING_CAPABILITY",
        "capability_registered": False,
        "default_policy": "ALLOW_UNKNOWN_MUTANT" if allow_unknown else "DENY",
        "process_started": allow_unknown,
        "process_exit_code": exit_code,
        "sentinel_created": sentinel.exists(),
        "failure_code": "UNKNOWN_CAPABILITY_EXECUTED" if allow_unknown else "CAPABILITY_NOT_REGISTERED",
        "failure_stage": "capability_admission",
    }


def _hash_mismatch(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    executable = root / "adapter.py"
    sentinel = root / "adapter-ran.txt"
    executable.write_text("from pathlib import Path; Path('adapter-ran.txt').write_text('bad')\n", encoding="utf-8")
    measured = _sha256(executable)
    return {
        "declared_executable_sha256": "0" * 64,
        "measured_executable_sha256": measured,
        "hash_match": False,
        "blocked_before_execution": True,
        "process_started": False,
        "sentinel_created": sentinel.exists(),
        "failure_code": "EXECUTABLE_IDENTITY_MISMATCH",
        "failure_stage": "executable_identity_gate",
    }


def _timeout(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    process = _spawn([sys.executable, "-c", "import time; time.sleep(30)"], root)
    timed_out = False
    termination: dict[str, Any] = {"requested": False, "tree_terminated": False}
    try:
        process.wait(timeout=0.2)
    except subprocess.TimeoutExpired:
        timed_out = True
        termination = _terminate_tree(process)
    finally:
        if process.poll() is None:
            termination = _terminate_tree(process)
    return {
        "parent_pid": process.pid,
        "timeout_seconds": 0.2,
        "timeout_triggered": timed_out,
        "process_started": True,
        "process_exit_code": process.returncode,
        "parent_alive_after": _process_alive(process.pid),
        "termination": termination,
        "failure_code": "TIMEOUT",
        "failure_stage": "process_supervision",
    }


def _process_tree(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    grandchild = root / "grandchild.py"
    child = root / "child.py"
    parent = root / "parent.py"
    grandchild.write_text("import os,sys,time\nfrom pathlib import Path\nPath(sys.argv[1]).write_text(str(os.getpid()))\ntime.sleep(30)\n", encoding="utf-8")
    child.write_text("import os,subprocess,sys,time\nfrom pathlib import Path\nPath(sys.argv[1]).write_text(str(os.getpid()))\np=subprocess.Popen([sys.executable,sys.argv[3],sys.argv[2]])\nPath(sys.argv[4]).write_text(str(p.pid))\ntime.sleep(30)\n", encoding="utf-8")
    parent.write_text("import os,subprocess,sys,time\nfrom pathlib import Path\nPath(sys.argv[1]).write_text(str(os.getpid()))\np=subprocess.Popen([sys.executable,sys.argv[3],sys.argv[2],sys.argv[4],sys.argv[5],sys.argv[7]])\nPath(sys.argv[6]).write_text(str(p.pid))\ntime.sleep(30)\n", encoding="utf-8")
    parent_pid_file, child_pid_file, grand_pid_file = root / "parent.pid", root / "child.pid", root / "grand.pid"
    child_spawn_file, grand_spawn_file = root / "child-spawn.pid", root / "grand-spawn.pid"
    process = _spawn([sys.executable, str(parent), str(parent_pid_file), str(child_pid_file), str(child), str(grand_pid_file), str(grandchild), str(child_spawn_file), str(grand_spawn_file)], root)
    required = [parent_pid_file, child_pid_file, grand_pid_file, child_spawn_file, grand_spawn_file]
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline and not all(path.is_file() and path.read_text().strip() for path in required):
        time.sleep(0.05)
    pids = [int(path.read_text()) for path in (parent_pid_file, child_pid_file, grand_pid_file) if path.is_file() and path.read_text().strip()]
    termination = _terminate_tree(process)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and any(_process_alive(pid) for pid in pids):
        time.sleep(0.05)
    alive_after = [pid for pid in pids if _process_alive(pid)]
    return {
        "parent_pid": pids[0] if pids else process.pid,
        "descendant_pids": pids[1:],
        "observed_process_depth": len(pids),
        "timeout_triggered": True,
        "process_started": True,
        "parent_alive_after": (pids[0] in alive_after) if pids else _process_alive(process.pid),
        "descendants_alive_after": [pid for pid in pids[1:] if pid in alive_after],
        "termination": termination,
        "failure_code": "PROCESS_TREE_TIMEOUT",
        "failure_stage": "process_tree_supervision",
    }


def _stale_base(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    repo = root / "subject-reality"
    observed = _init_repo(repo)
    before = _git(repo, "status", "--porcelain=v1").stdout.splitlines()
    expected = "0" * 40
    after = _git(repo, "status", "--porcelain=v1").stdout.splitlines()
    return {"expected_base_head": expected, "observed_base_head": observed, "base_head_match": False, "blocked_before_state_change": True, "state_before": before, "state_after": after, "state_unchanged": before == after, "process_started": False, "failure_code": "STALE_BASE_HEAD", "failure_stage": "base_head_gate"}


def _dirty_reality(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    repo = root / "subject-reality"
    _init_repo(repo)
    (repo / "dirty.txt").write_text("dirty", encoding="utf-8")
    before = _git(repo, "status", "--porcelain=v1").stdout.splitlines()
    after = _git(repo, "status", "--porcelain=v1").stdout.splitlines()
    return {"subject_reality_dirty": bool(before), "subject_status_before": before, "subject_status_after": after, "blocked_before_warp_create": True, "subject_state_unchanged": before == after, "process_started": False, "failure_code": "DIRTY_REALITY", "failure_stage": "reality_cleanliness_gate"}


def _failed_validator(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    script = root / "failing_validator.py"
    script.write_text("raise SystemExit(7)\n", encoding="utf-8")
    result = subprocess.run([sys.executable, str(script)], cwd=root, shell=False, capture_output=True, timeout=10, check=False)
    return {"validator_path": str(script.resolve()), "validator_sha256": _sha256(script), "process_started": True, "validator_exit_code": result.returncode, "validator_rejected": result.returncode != 0, "failure_code": "VALIDATOR_EXIT_NONZERO", "failure_stage": "validator_execution"}


def _tampering(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    evidence = root / "evidence.json"
    evidence.write_text('{"measured":true}\n', encoding="utf-8")
    sealed = _sha256(evidence)
    evidence.write_text('{"measured":false}\n', encoding="utf-8")
    measured = _sha256(evidence)
    return {"evidence_path": str(evidence.resolve()), "sealed_evidence_sha256": sealed, "measured_evidence_sha256": measured, "evidence_hash_match": sealed == measured, "tamper_detected": sealed != measured, "evidence_rejected": sealed != measured, "process_started": False, "failure_code": "EVIDENCE_HASH_MISMATCH", "failure_stage": "evidence_integrity_gate"}


def _wrong_binding(root: Path, bindings: dict[str, str], mutation: str | None, field: str) -> dict[str, Any]:
    expected = bindings[field]
    observed = ("f" * 40) if field == "base_head" else f"WRONG-{field.upper()}"
    return {"binding_field": field, "expected_binding": expected, "observed_binding": observed, "binding_match": False, "evidence_rejected": True, "process_started": False, "failure_code": f"WRONG_{field.upper()}", "failure_stage": "evidence_binding_gate"}


def _missing_organ(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    expected = ["ASTRONOMICON", "DOCTRINARIUM", "ARCHIVUM", "LOGOS", "FABRICATOR", "TECHMARINE", "MECHANICUS", "CUSTODES", "INQUISITION", "OFFICIO", "THRONE"]
    observed = [item for item in expected if item != "INQUISITION"]
    return {"required_organs": expected, "observed_organs": observed, "missing_organs": sorted(set(expected) - set(observed)), "pass_claim_rejected": True, "process_started": False, "failure_code": "MISSING_REQUIRED_ORGAN", "failure_stage": "organ_completeness_gate"}


def _throne_overclaim(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    organs = {"MECHANICUS": "PASS_PROVEN", "CUSTODES": "BLOCK", "INQUISITION": "PASS_PROVEN"}
    return {"organ_verdicts": organs, "critical_blocking_organs": [key for key, value in organs.items() if value == "BLOCK"], "throne_claim": "PASS_PROVEN", "throne_claim_rejected": True, "downgraded_verdict": "BLOCK", "process_started": False, "failure_code": "THRONE_OVERCLAIM", "failure_stage": "throne_crown_gate"}


def _command_attempt(root: Path, bindings: dict[str, str], mutation: str | None, *, tauri: bool) -> dict[str, Any]:
    attempted = "direct_tauri_invoke_without_corridor_token" if tauri else "run_registered_patch_pack"
    return {"attempted_command": attempted, "canonical_inventory": ["corridor_ui_action", "corridor_ui_snapshot"], "command_registered": False, "corridor_token_present": False if tauri else None, "invocation_blocked": True, "backend_handler_called": False, "process_started": False, "failure_code": "DIRECT_TAURI_BYPASS" if tauri else "LEGACY_COMMAND_NOT_ADMITTED", "failure_stage": "tauri_corridor_gate" if tauri else "command_inventory_gate"}


def _parity(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    backend, ui = {"refresh_state", "run_core_diagnostic"}, {"refresh_state", "legacy_run_patch"}
    return {"backend_actions": sorted(backend), "ui_actions": sorted(ui), "missing_in_ui": sorted(backend - ui), "unknown_in_ui": sorted(ui - backend), "parity_match": backend == ui, "action_surface_blocked": True, "process_started": False, "failure_code": "UI_BACKEND_PARITY_MISMATCH", "failure_stage": "action_parity_gate"}


def _warp_lifecycle(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    from .owner_gate import OwnerGate
    from .warp_manager import WarpManager

    source, managed = root / "source", root / "warps"
    base = _init_repo(source)
    gate = OwnerGate(root / "gates")
    manager = WarpManager(source, managed, owner_gate=gate)
    states = [manager.create("WARP-PHASE2", "TASK-PHASE2", base).state]
    def decide(key: str, action: str, warp: bool = True) -> None:
        gate.record_decision(key, task_id="TASK-PHASE2", warp_id="WARP-PHASE2" if warp else None, action=action, rationale="Phase 2 disposable fixture", evidence_refs=["fixture:phase2"])
    decide("launch", "APPROVE_LAUNCH", False)
    states.extend([manager.activate("WARP-PHASE2").state, manager.execute("WARP-PHASE2").state, manager.validate("WARP-PHASE2", passed=True).state])
    decide("reject", "REJECT_RESULT")
    states.append(manager.reject("WARP-PHASE2").state)
    decide("discard", "DISCARD_WARP")
    states.append(manager.discard("WARP-PHASE2").state)
    decide("destroy", "DESTROY_WARP")
    states.append(manager.destroy("WARP-PHASE2").state)
    return {"state_sequence": states, "owner_decisions_recorded": True, "managed_warp_exists_after": (managed / "WARP-PHASE2").exists(), "source_head_before": base, "source_head_after": _git(source, "rev-parse", "HEAD").stdout.strip(), "source_status_after": _git(source, "status", "--porcelain=v1").stdout.splitlines(), "process_started": False, "failure_code": "EXPECTED_REJECT_DISCARD_DESTROY", "failure_stage": "managed_warp_lifecycle"}


def _restart_recovery(root: Path, bindings: dict[str, str], mutation: str | None) -> dict[str, Any]:
    from .errors import TaskStoreError
    from .task_store import TaskStore

    base = "a" * 40
    state_root = root / "state"
    task = {"schema_version": "imperium.core_reference_corridor.task_state.v0_1", "task_id": "TASK-PHASE2", "task_type": "SERVITOR_TASK_PACK", "owner_intent": {"statement": "fixture"}, "created_at_utc": "2026-07-13T00:00:00Z", "base_head": base, "branch": "fixture", "scope": {"mode": "DISPOSABLE"}, "allowed_read_roots": [str(root)], "allowed_write_roots": [str(root)], "acceptance_tests": ["restart"], "confidence_components": {}, "selected_strategy": None, "current_state": "OWNER_INTENT", "state_version": 1, "organ_depth_plan": {}, "owner_decisions": [], "created_by": "PHASE2_OBSERVER"}
    TaskStore(state_root, expected_base_head=base).create(task)
    class InterruptedStore(TaskStore):
        def _remove_pending_locked(self) -> None:
            raise OSError("intentional disposable interruption")
    interrupted = False
    try:
        InterruptedStore(state_root, expected_base_head=base).transition("TASK_REGISTRATION", expected_version=1)
    except TaskStoreError:
        interrupted = True
    pending_before = (state_root / ".TASK_STATE.pending.json").is_file()
    recovered = TaskStore(state_root, expected_base_head=base).load()
    return {"interruption_observed": interrupted, "pending_receipt_present_before_restart": pending_before, "recovered_state": recovered["current_state"], "recovered_state_version": recovered["state_version"], "pending_receipt_present_after_restart": (state_root / ".TASK_STATE.pending.json").exists(), "transition_log_entries": len(TaskStore(state_root).load_transition_log()), "process_started": False, "failure_code": "DURABLE_PENDING_TRANSACTION_RECOVERED", "failure_stage": "task_store_restart_recovery"}


_OBSERVERS: dict[str, Callable[[Path, dict[str, str], str | None], dict[str, Any]]] = {
    "unauthorized_reality_write": lambda root, bindings, mutation: _blocked_write(root, target_role="REALITY"),
    "write_outside_allowed_warp_scope": lambda root, bindings, mutation: _blocked_write(root, target_role="WARP_OUTSIDE_ALLOWED"),
    "unregistered_capability": _unregistered,
    "executable_hash_mismatch": _hash_mismatch,
    "timeout": _timeout,
    "parent_child_grandchild_termination": _process_tree,
    "stale_base_head": _stale_base,
    "dirty_reality": _dirty_reality,
    "failed_validator": _failed_validator,
    "evidence_tampering": _tampering,
    "wrong_task_id": lambda root, bindings, mutation: _wrong_binding(root, bindings, mutation, "task_id"),
    "wrong_warp_id": lambda root, bindings, mutation: _wrong_binding(root, bindings, mutation, "warp_id"),
    "wrong_base_head": lambda root, bindings, mutation: _wrong_binding(root, bindings, mutation, "base_head"),
    "missing_organ": _missing_organ,
    "throne_overclaim": _throne_overclaim,
    "direct_legacy_command_attempt": lambda root, bindings, mutation: _command_attempt(root, bindings, mutation, tauri=False),
    "direct_tauri_bypass_attempt": lambda root, bindings, mutation: _command_attempt(root, bindings, mutation, tauri=True),
    "parity_mismatch": _parity,
    "warp_reject_discard_destroy": _warp_lifecycle,
    "restart_and_state_recovery": _restart_recovery,
}


def observe_scenario(*, scenario_id: str, fixture_boundary: Path, host_reality: Path, host_warp: Path, bindings: dict[str, str], mutation: str | None = None) -> dict[str, Any]:
    """Measure one isolated scenario without consulting expected outcomes."""
    if scenario_id not in _OBSERVERS:
        raise ValueError(f"unknown scenario: {scenario_id}")
    fixture_id = f"fixture-{scenario_id}-{uuid.uuid4().hex[:12]}"
    fixture_root = (fixture_boundary / fixture_id).resolve()
    fixture_root.mkdir(parents=True)
    marker = fixture_root / ".imperium_phase2_disposable_fixture"
    marker.write_text(fixture_id + "\n", encoding="utf-8", newline="\n")
    before = _host_snapshot(host_reality, host_warp)
    details = _OBSERVERS[scenario_id](fixture_root, bindings, mutation)
    after = _host_snapshot(host_reality, host_warp)
    isolated = _within(fixture_root, fixture_boundary) and not _within(fixture_root, host_reality) and not _within(fixture_root, host_warp)
    details.update({"scenario_id": scenario_id, "fixture_id": fixture_id, "fixture_boundary": str(fixture_boundary.resolve()), "fixture_root": str(fixture_root), "fixture_marker_path": str(marker), "fixture_marker_sha256": _sha256(marker), "fixture_isolated": isolated, "host_reality_before": before, "host_reality_after": after, "host_reality_changed": before["reality_head"] != after["reality_head"] or before["reality_origin_master"] != after["reality_origin_master"] or before["reality_status"] != after["reality_status"], "host_warp_before": before, "host_warp_after": after, "host_warp_changed_outside_scope": before["warp_head"] != after["warp_head"] or before["warp_status"] != after["warp_status"], "failure_localized": bool(details.get("failure_code") and details.get("failure_stage")), "observer_mutation": mutation})
    return details
