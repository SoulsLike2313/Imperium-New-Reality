"""Single task-local capability and control-action registry.

The legacy Mechanicus registries remain read-only migration inputs.  This file
owns the only registry used by the reference corridor CLI and Thin IDE.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from .pinned_tools import (
    GIT_HASH_ENV,
    GIT_PATH_ENV,
    PWSH_HASH_ENV,
    PWSH_PATH_ENV,
)


REGISTRY_SCHEMA = "imperium.core_reference_corridor.capability_registry.v0_1"
VALID_ADMISSION_STATES = {"CANDIDATE", "VALIDATING", "ACTIVE", "QUARANTINED", "DISABLED"}
REQUIRED_CAPABILITY_FIELDS = {
    "capability_id",
    "type",
    "adapter_id",
    "executable_path",
    "executable_sha256",
    "version",
    "admission_state",
    "declared_effect",
    "actual_effect_class",
    "allowed_operations",
    "allowed_read_roots",
    "allowed_write_roots",
    "timeout_seconds",
    "environment_profile",
    "cost_model",
    "trust_level",
    "last_validation",
    "quarantine_reason",
}


class RegistryError(RuntimeError):
    """Default-deny registry failure."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    clone = dict(value)
    clone.pop("registry_digest", None)
    payload = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


def _ui_actions() -> list[dict[str, Any]]:
    return [
        {"action_id": "refresh_state", "label": "Refresh", "panel_id": "task_state", "effect": "READ_ONLY"},
        {"action_id": "create_test_task", "label": "Create Test Task", "panel_id": "new_task", "effect": "CONTROL_STATE"},
        {"action_id": "approve_launch", "label": "Approve Launch", "panel_id": "owner_decisions", "effect": "OWNER_DECISION"},
        {"action_id": "stop_task", "label": "Stop", "panel_id": "owner_decisions", "effect": "OWNER_DECISION"},
        {"action_id": "continue_checkpoint", "label": "Continue Checkpoint", "panel_id": "owner_decisions", "effect": "OWNER_DECISION"},
        {"action_id": "accept_risk", "label": "Accept Risk", "panel_id": "owner_decisions", "effect": "OWNER_DECISION"},
        {"action_id": "create_exact_head_warp", "label": "Create WARP", "panel_id": "warp", "effect": "MANAGED_WARP_MUTATION"},
        {"action_id": "run_core_diagnostic", "label": "Run Diagnostic", "panel_id": "execution_trace", "effect": "READ_ONLY", "capability_id": "CORE_DIAGNOSTIC"},
        {"action_id": "accept_result", "label": "Accept Result", "panel_id": "owner_decisions", "effect": "OWNER_DECISION"},
        {"action_id": "reject_result", "label": "Reject Result", "panel_id": "owner_decisions", "effect": "OWNER_DECISION"},
        {"action_id": "request_rework", "label": "Request Rework", "panel_id": "owner_decisions", "effect": "OWNER_DECISION"},
        {"action_id": "prepare_land_plan", "label": "Prepare Land Plan", "panel_id": "diff", "effect": "OWNER_DECISION"},
        {"action_id": "forbid_land", "label": "Forbid Land", "panel_id": "owner_decisions", "effect": "OWNER_DECISION"},
        {"action_id": "discard_warp", "label": "Discard WARP", "panel_id": "warp", "effect": "MANAGED_WARP_MUTATION"},
        {"action_id": "destroy_warp", "label": "Destroy WARP", "panel_id": "warp", "effect": "MANAGED_WARP_DESTRUCTIVE"},
    ]


def _module_capability(
    context: Any,
    report_root: Path,
    *,
    capability_id: str,
    module_name: str,
    adapter_name: str,
    effect: str,
    timeout_seconds: int,
) -> dict[str, Any]:
    executable = Path(sys.executable).resolve()
    adapter = Path(context.worktree_root) / "ORGANS" / "MECHANICUS" / "CORE_REFERENCE_CORRIDOR" / adapter_name
    return {
        "capability_id": capability_id,
        "type": "PYTHON_MODULE",
        "adapter_id": "FIXED_ARGV_PYTHON_MODULE_V0_1",
        "adapter_path": str(adapter),
        "adapter_sha256": sha256_file(adapter),
        "executable_path": str(executable),
        "executable_sha256": sha256_file(executable),
        "version": platform.python_version(),
        "admission_state": "ACTIVE",
        "declared_effect": effect,
        "actual_effect_class": effect,
        "allowed_operations": ["run"],
        "allowed_read_roots": [str(context.reality_root), str(context.worktree_root)],
        "allowed_write_roots": [str(report_root)] if effect != "READ_ONLY" else [],
        "timeout_seconds": timeout_seconds,
        "environment_profile": "CORE_MINIMAL_HOST_V0_1",
        "cost_model": {"unit": "local_process", "estimated_units": 1, "external_cost": 0},
        "trust_level": "TASK_LOCAL_HOST_BOUND",
        "last_validation": "PENDING_FIRST_EXECUTION",
        "quarantine_reason": "",
        "fixed_argv": ["-m", f"ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.{module_name}", "--write"],
        "parameter_schema": {"type": "object", "additionalProperties": False},
    }



def _resolve_host_tool(path_env: str, hash_env: str, names: tuple[str, ...]) -> tuple[Path, str, str]:
    configured = os.environ.get(path_env, "").strip()
    if configured:
        candidate = Path(configured)
    else:
        located = next((shutil.which(name) for name in names if shutil.which(name)), None)
        if not located:
            raise RegistryError("SYSTEM_TOOL_MISSING", "/".join(names))
        candidate = Path(located)
    if not candidate.is_absolute():
        raise RegistryError("SYSTEM_TOOL_PATH_NOT_ABSOLUTE", str(candidate))
    try:
        executable = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RegistryError("SYSTEM_TOOL_UNAVAILABLE", str(exc)) from exc
    if executable.name.casefold() not in {name.casefold() for name in names}:
        raise RegistryError("SYSTEM_TOOL_NAME_REJECTED", executable.name)
    actual_hash = sha256_file(executable)
    expected = os.environ.get(hash_env, "").strip()
    if expected and expected.casefold() != actual_hash.casefold():
        raise RegistryError("SYSTEM_TOOL_HASH_MISMATCH", str(executable))
    version = subprocess.run(
        [str(executable), "--version"],
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    if version.returncode != 0:
        raise RegistryError("SYSTEM_TOOL_VERSION_PROBE_FAILED", str(executable))
    return executable, actual_hash, version.stdout.strip() or version.stderr.strip()


def _system_tool_capability(
    context: Any,
    *,
    capability_id: str,
    path_env: str,
    hash_env: str,
    names: tuple[str, ...],
    operations: list[str],
) -> dict[str, Any]:
    executable, digest, version = _resolve_host_tool(path_env, hash_env, names)
    return {
        "capability_id": capability_id,
        "type": "SYSTEM_EXECUTABLE",
        "adapter_id": "PINNED_EXECUTABLE_V0_1",
        "adapter_path": str(executable),
        "adapter_sha256": digest,
        "executable_path": str(executable),
        "executable_sha256": digest,
        "version": version,
        "admission_state": "ACTIVE",
        "declared_effect": "READ_ONLY",
        "actual_effect_class": "READ_ONLY",
        "allowed_operations": operations,
        "allowed_read_roots": [str(context.reality_root), str(context.worktree_root)],
        "allowed_write_roots": [],
        "timeout_seconds": 60,
        "environment_profile": "RUST_PYTHON_BRIDGE_MINIMAL_ENV_V2",
        "cost_model": {"unit": "local_process", "estimated_units": 1, "external_cost": 0},
        "trust_level": "HOST_PINNED_HASH_VERIFIED",
        "last_validation": "PENDING_FIRST_BRIDGE_USE",
        "quarantine_reason": "",
        "fixed_argv": [],
        "parameter_schema": {"type": "object", "additionalProperties": False},
    }

def build_default_registry(context: Any, report_root: Path) -> dict[str, Any]:
    python_path = Path(sys.executable).resolve()
    package_root = Path(context.worktree_root) / "ORGANS" / "MECHANICUS" / "CORE_REFERENCE_CORRIDOR"
    diagnostic_path = package_root / "diagnostic_tool.py"
    if not diagnostic_path.is_file():
        raise RegistryError("ADAPTER_MISSING", f"diagnostic adapter not found: {diagnostic_path}")
    registry: dict[str, Any] = {
        "schema_version": REGISTRY_SCHEMA,
        "registry_id": "IMPERIUM_CORE_REFERENCE_CORRIDOR_0001_CAPABILITIES",
        "authority": "TASK_LOCAL_CANONICAL_SINGLE_SOURCE",
        "task_id": "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001",
        "base_head": context.head,
        "host_scope": platform.system() + "-" + platform.machine(),
        "default_policy": "DENY",
        "legacy_sources": [
            {"path": "ORGANS/MECHANICUS/REGISTRY/tool_registry.json", "status": "LEGACY_READ_ONLY"},
            {"path": "ORGANS/MECHANICUS/REGISTRY/capability_registry.json", "status": "LEGACY_READ_ONLY"},
            {"path": "ORGANS/MECHANICUS/TOOL_REGISTRY/tool_registry.json", "status": "LEGACY_READ_ONLY"},
            {"path": "SUPPORT/APP_TAURI/state/patch_pack_registry.json", "status": "DEPRECATED_UNSAFE"},
        ],
        "capabilities": [
            {
                "capability_id": "CORE_DIAGNOSTIC",
                "type": "PYTHON_MODULE",
                "adapter_id": "FIXED_ARGV_PYTHON_MODULE_V0_1",
                "adapter_path": str(diagnostic_path),
                "adapter_sha256": sha256_file(diagnostic_path),
                "executable_path": str(python_path),
                "executable_sha256": sha256_file(python_path),
                "version": platform.python_version(),
                "admission_state": "ACTIVE",
                "declared_effect": "READ_ONLY",
                "actual_effect_class": "READ_ONLY",
                "allowed_operations": ["diagnose"],
                "allowed_read_roots": [str(context.reality_root), str(context.worktree_root)],
                "allowed_write_roots": [],
                "timeout_seconds": 10,
                "environment_profile": "CORE_MINIMAL_HOST_V0_1",
                "cost_model": {"unit": "local_process", "estimated_units": 1, "external_cost": 0},
                "trust_level": "TASK_LOCAL_HOST_BOUND",
                "last_validation": "PENDING_FIRST_EXECUTION",
                "quarantine_reason": "",
                "fixed_argv": [
                    "-m",
                    "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.diagnostic_tool",
                    "--json",
                ],
                "parameter_schema": {"type": "object", "additionalProperties": False},
            },
            _module_capability(
                context,
                report_root,
                capability_id="CORE_REPORT_BUILDER",
                module_name="report_builder",
                adapter_name="report_builder.py",
                effect="MUTATING",
                timeout_seconds=60,
            ),
            _module_capability(
                context,
                report_root,
                capability_id="CORE_VALIDATION_SUITE",
                module_name="validation_runner",
                adapter_name="validation_runner.py",
                effect="MUTATING",
                timeout_seconds=300,
            ),
            _system_tool_capability(
                context,
                capability_id="CORE_GIT",
                path_env=GIT_PATH_ENV,
                hash_env=GIT_HASH_ENV,
                names=("git.exe", "git"),
                operations=["repository_read", "diff_read", "status_read"],
            ),
            _system_tool_capability(
                context,
                capability_id="CORE_PWSH",
                path_env=PWSH_PATH_ENV,
                hash_env=PWSH_HASH_ENV,
                names=("pwsh.exe", "pwsh"),
                operations=["version_probe"],
            ),
        ],
        "ui_actions": _ui_actions(),
        "extension_points": [
            {"extension_id": name, "status": "SCAFFOLD_ONLY", "proof": "NOT_OPERATIONALLY_PROVEN"}
            for name in [
                "API_ADAPTERS",
                "MCP_REGISTRY_CONFIGURATION",
                "SKILLS_REGISTRY_EDITOR",
                "EXTERNAL_LLM_ADAPTERS",
                "QUIET_INTERNAL_ANALYSIS",
                "COST_TIME_ESTIMATOR",
                "LIVE_CAUSAL_GRAPH",
                "DAILY_AND_THREE_DAY_REPORTS",
                "LEARNED_RULE_PROPOSALS",
                "FUTURE_CODING_ABSTRACTION_LAYER",
            ]
        ],
        "report_root": str(report_root),
    }
    validation = next(item for item in registry["capabilities"] if item["capability_id"] == "CORE_VALIDATION_SUITE")
    validation["allowed_write_roots"].extend(
        [
            str(Path(context.worktree_root) / "SUPPORT" / "APP_TAURI" / "dist"),
            str(Path(context.worktree_root) / "SUPPORT" / "APP_TAURI" / "src-tauri" / "target"),
        ]
    )
    registry["registry_digest"] = canonical_digest(registry)
    return registry


class CapabilityRegistry:
    def __init__(self, path: Path | str):
        self.path = Path(path).resolve()
        self.data: dict[str, Any] = {}

    def initialize(self, context: Any, report_root: Path | str) -> dict[str, Any]:
        self.data = build_default_registry(context, Path(report_root).resolve())
        self.validate(self.data, verify_files=True)
        atomic_write_json(self.path, self.data)
        return self.data

    def reconcile(self, context: Any, report_root: Path | str) -> dict[str, Any]:
        desired = build_default_registry(context, Path(report_root).resolve())
        if self.path.is_file():
            current = self.load(verify_files=False)
            previous = {item.get("capability_id"): item for item in current.get("capabilities", [])}
            for item in desired["capabilities"]:
                old = previous.get(item["capability_id"])
                if old and old.get("adapter_sha256") == item.get("adapter_sha256") and old.get("executable_sha256") == item.get("executable_sha256"):
                    item["last_validation"] = old.get("last_validation", item["last_validation"])
        desired["registry_digest"] = canonical_digest(desired)
        self.validate(desired, verify_files=True)
        self.data = desired
        atomic_write_json(self.path, desired)
        return desired

    def load(self, *, verify_files: bool = True) -> dict[str, Any]:
        try:
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RegistryError("REGISTRY_UNAVAILABLE", str(exc)) from exc
        self.validate(self.data, verify_files=verify_files)
        return self.data

    @staticmethod
    def validate(data: dict[str, Any], *, verify_files: bool = True) -> None:
        if data.get("schema_version") != REGISTRY_SCHEMA or data.get("default_policy") != "DENY":
            raise RegistryError("REGISTRY_POLICY_INVALID", "schema/default deny mismatch")
        if canonical_digest(data) != data.get("registry_digest"):
            raise RegistryError("REGISTRY_DIGEST_MISMATCH", "canonical digest does not match")
        seen: set[str] = set()
        for item in data.get("capabilities", []):
            missing = sorted(REQUIRED_CAPABILITY_FIELDS - set(item))
            if missing:
                raise RegistryError("CAPABILITY_FIELDS_MISSING", ",".join(missing))
            capability_id = item["capability_id"]
            if capability_id in seen:
                raise RegistryError("CAPABILITY_DUPLICATE", capability_id)
            seen.add(capability_id)
            if item["admission_state"] not in VALID_ADMISSION_STATES:
                raise RegistryError("ADMISSION_STATE_INVALID", capability_id)
            if verify_files and item["admission_state"] == "ACTIVE":
                executable = Path(item["executable_path"])
                adapter = Path(item.get("adapter_path", ""))
                if not executable.is_file() or sha256_file(executable) != item["executable_sha256"]:
                    raise RegistryError("EXECUTABLE_IDENTITY_MISMATCH", capability_id)
                if not adapter.is_file() or sha256_file(adapter) != item.get("adapter_sha256"):
                    raise RegistryError("ADAPTER_IDENTITY_MISMATCH", capability_id)
        action_ids = [item.get("action_id") for item in data.get("ui_actions", [])]
        if len(action_ids) != len(set(action_ids)) or any(not item for item in action_ids):
            raise RegistryError("UI_ACTION_DUPLICATE_OR_EMPTY", "action catalog invalid")

    def resolve(self, capability_id: str, operation: str) -> dict[str, Any]:
        data = self.data or self.load()
        matches = [item for item in data["capabilities"] if item["capability_id"] == capability_id]
        if not matches:
            raise RegistryError("CAPABILITY_NOT_REGISTERED", capability_id)
        item = matches[0]
        if item["admission_state"] != "ACTIVE":
            raise RegistryError("CAPABILITY_NOT_ACTIVE", capability_id)
        if operation not in item["allowed_operations"]:
            raise RegistryError("OPERATION_NOT_ALLOWED", f"{capability_id}:{operation}")
        return item

    def action(self, action_id: str) -> dict[str, Any]:
        data = self.data or self.load()
        for item in data.get("ui_actions", []):
            if item.get("action_id") == action_id:
                return item
        raise RegistryError("UI_ACTION_NOT_REGISTERED", action_id)
