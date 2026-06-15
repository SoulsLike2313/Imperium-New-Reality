"""safety_gate - every dangerous capability is OFF by default and lives here.

The owner spec demands: no unrestricted shell, no secrets staged, no real
execution without allowlist, no live LLM without provider config, no
destructive cleanup without owner batch, no kernel write without release gate,
no fake-green. This module is the single source of truth for those flags.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List

ACTION_REAL_SERVITOR = "real_servitor"
ACTION_UNSAFE_SHELL = "unsafe_shell"
ACTION_LIVE_LLM = "live_llm"
ACTION_DESTRUCTIVE = "destructive_cleanup"
ACTION_KERNEL_WRITE = "kernel_write"
ACTION_PUSH = "push"

SAFETY_REL = os.path.join("ORGANS", "INQUISITION", "SAFETY", "safety_state.json")
COMMAND_POLICY_REL = os.path.join("ORGANS", "MECHANICUS", "REGISTRY", "command_policy.json")


@dataclass
class SafetyState:
    allow_real: bool = False
    unsafe_shell: bool = False
    live_llm: bool = False
    real_servitor: bool = False
    destructive_cleanup: bool = False
    kernel_write: bool = False
    push_allowed: bool = False
    secrets_detected: bool = False
    runtime_staged: bool = False
    out_of_scope_diff: bool = False

    def to_dict(self) -> Dict[str, bool]:
        return asdict(self)


@dataclass
class GateCheck:
    action: str
    allowed: bool
    reasons: List[str]

    def to_dict(self) -> dict:
        return {"action": self.action, "allowed": self.allowed, "reasons": self.reasons}


def load_safety(repo_root: str) -> SafetyState:
    """Load safety flags. Missing/broken file => everything dangerous stays OFF."""
    path = os.path.join(repo_root, SAFETY_REL)
    state = SafetyState()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for k, v in data.items():
            if hasattr(state, k) and isinstance(v, bool):
                setattr(state, k, v)
    except (OSError, ValueError, json.JSONDecodeError):
        return SafetyState()
    return state


def load_command_policy(repo_root: str) -> dict:
    """Load current Mechanicus command policy. Missing file keeps safe defaults."""
    path = os.path.join(repo_root, COMMAND_POLICY_REL)
    fallback = {
        "arbitrary_shell_execution_allowed": False,
        "dry_run_required_by_default": True,
        "allowlisted_tool_ids_for_dry_run": [],
        "blocked_actions": ["execute_unregistered_tool", "arbitrary_shell"],
        "policy_loaded": False,
        "policy_path": path,
    }
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            data = json.load(fh)
        data["policy_loaded"] = True
        data["policy_path"] = path
        return data
    except (OSError, ValueError, json.JSONDecodeError):
        return fallback


def tool_allowed_for_dry_run(repo_root: str, tool_id: str) -> bool:
    policy = load_command_policy(repo_root)
    allowlist = policy.get("allowlisted_tool_ids_for_dry_run") or []
    return tool_id in allowlist


def safety_receipt_fields(repo_root: str, state: SafetyState | None = None) -> dict:
    """Fields used by OPS safety receipts and report gates."""
    state = state or load_safety(repo_root)
    policy = load_command_policy(repo_root)
    unknown_tool_blocked = not tool_allowed_for_dry_run(repo_root, "OPS_UNKNOWN_TOOL_SMOKE")
    return {
        "real_servitor_execution_enabled": state.real_servitor,
        "live_llm_backend_enabled": state.live_llm,
        "unsafe_shell_available": state.unsafe_shell,
        "arbitrary_shell_allowed": bool(policy.get("arbitrary_shell_execution_allowed", False)),
        "dry_run_default": bool(policy.get("dry_run_required_by_default", True)),
        "unknown_tool_blocked": unknown_tool_blocked,
        "secrets_staged": state.secrets_detected,
        "runtime_paths_staged": state.runtime_staged,
        "vm2_action": False,
        "vm3_action": False,
        "mechanicus_policy_loaded": bool(policy.get("policy_loaded", False)),
        "mechanicus_policy_path": policy.get("policy_path", ""),
        "result": "PASS_WITH_WARNINGS" if unknown_tool_blocked else "BLOCKED",
    }


def check(action: str, state: SafetyState) -> GateCheck:
    """Decide whether an action is permitted given the current safety state."""
    reasons: List[str] = []
    allowed = False
    if action == ACTION_REAL_SERVITOR:
        allowed = state.allow_real and state.real_servitor
        if not allowed:
            reasons.append("real servitor execution requires allow_real AND real_servitor")
    elif action == ACTION_UNSAFE_SHELL:
        allowed = state.unsafe_shell
        if not allowed:
            reasons.append("unrestricted shell is blocked")
    elif action == ACTION_LIVE_LLM:
        allowed = state.live_llm
        if not allowed:
            reasons.append("live LLM backend requires explicit provider config")
    elif action == ACTION_DESTRUCTIVE:
        allowed = state.destructive_cleanup
        if not allowed:
            reasons.append("destructive cleanup requires owner batch approval")
    elif action == ACTION_KERNEL_WRITE:
        allowed = state.kernel_write
        if not allowed:
            reasons.append("kernel write requires release gate")
    elif action == ACTION_PUSH:
        allowed = state.push_allowed and not state.secrets_detected and not state.out_of_scope_diff
        if not state.push_allowed:
            reasons.append("push not allowed by policy")
        if state.secrets_detected:
            reasons.append("secrets detected")
        if state.out_of_scope_diff:
            reasons.append("out-of-scope diff")
    else:
        reasons.append(f"unknown action: {action}")
    return GateCheck(action=action, allowed=allowed, reasons=reasons)


def require(action: str, state: SafetyState) -> None:
    """Raise PermissionError if the action is not allowed."""
    gc = check(action, state)
    if not gc.allowed:
        raise PermissionError(f"{action} blocked: {'; '.join(gc.reasons)}")


def safety_report(state: SafetyState) -> Dict[str, str]:
    """Human-facing safety screen, matching the owner spec section 5."""
    onoff = lambda b: "on" if b else "off"
    yesno = lambda b: "yes" if b else "no"
    blocked = lambda b: "available" if b else "blocked"
    return {
        "AllowReal": onoff(state.allow_real),
        "Unsafe shell": blocked(state.unsafe_shell),
        "Live LLM backend": onoff(state.live_llm),
        "Real servitor execution": blocked(state.real_servitor),
        "Secrets detected": yesno(state.secrets_detected),
        "Runtime staged": yesno(state.runtime_staged),
        "Out-of-scope diff": yesno(state.out_of_scope_diff),
        "Push allowed": yesno(state.push_allowed),
    }
