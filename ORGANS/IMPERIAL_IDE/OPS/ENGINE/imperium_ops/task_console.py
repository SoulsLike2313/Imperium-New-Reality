"""task_console - turn a human request into a structured, validated TaskIntent.

This is the panel 2.2 brain: pick type/scope/risk/organs/push, get a stable
TASK-ID, and validate before anything is built.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

TASK_TYPES = [
    "audit",
    "repair",
    "build",
    "cleanup",
    "integration",
    "warp_experiment",
    "mechanicus_tool",
    "ide_extension",
    "governance_update",
    "report_generation",
]

SCOPES = [
    "PC_ONLY",
    "WARP_ONLY",
    "MECHANICUS_ONLY",
    "IMPERIAL_IDE",
    "ASTRONOMICON",
    "FULL_REPO",
]

RISK_LEVELS = [
    "READ_ONLY",
    "CONTROLLED_WRITE",
    "CLEANUP_STAGING",
    "DESTRUCTIVE_WITH_APPROVAL",
    "REAL_EXECUTION_GATED",
]

ORGANS = [
    "ASTRONOMICON",
    "MECHANICUS",
    "INQUISITION",
    "DOCTRINARIUM",
    "ADMINISTRATUM",
    "OFFICIO_AGENTIS",
    "STRATEGIUM",
    "SCHOLA_IMPERIALIS",
    "CUSTODES",
]

PUSH_POLICIES = ["NO_PUSH", "VALIDATED_PUSH", "OWNER_APPROVAL_PUSH"]

_DEFAULT_FORBIDDEN = [
    "kernel_write_without_release_gate",
    "unsafe_shell",
    "live_llm_without_provider_config",
    "real_servitor_without_allowlist",
    "push_secrets_or_local_configs",
    "fake_green_pass",
]

# keyword -> task_type, checked in order (first match wins).
_CLASSIFY_RULES = [
    ("mechanicus", "mechanicus_tool"),
    ("extension", "ide_extension"),
    ("warp", "warp_experiment"),
    ("governance", "governance_update"),
    ("passport", "governance_update"),
    ("constitution", "governance_update"),
    ("report", "report_generation"),
    ("audit", "audit"),
    ("review", "audit"),
    ("repair", "repair"),
    ("fix", "repair"),
    ("clean", "cleanup"),
    ("steriliz", "cleanup"),
    ("integrat", "integration"),
    ("wire", "integration"),
    ("connect", "integration"),
    ("build", "build"),
    ("add", "build"),
    ("create", "build"),
    ("make", "build"),
]


def classify(goal: str) -> str:
    """Best-effort task type from free text. mechanicus beats generic verbs."""
    text = (goal or "").lower()
    for kw, ttype in _CLASSIFY_RULES:
        if kw in text:
            return ttype
    return "build"


def slugify(text: str, max_words: int = 8) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text or "")
    words = [w.upper() for w in words][:max_words]
    return "-".join(words) or "TASK"


def make_task_id(task_type: str, title: str, version: str = "V0_1") -> str:
    type_part = task_type.upper().replace("_", "-")
    return f"TASK-NEWREALITY-{type_part}-{slugify(title)}-PC-{version}"


@dataclass
class TaskIntent:
    title: str
    goal: str
    task_type: str
    scope: str
    risk: str
    organs_route: List[str] = field(default_factory=list)
    allowed_write_scope: List[str] = field(default_factory=list)
    forbidden_actions: List[str] = field(default_factory=lambda: list(_DEFAULT_FORBIDDEN))
    push_policy: str = "VALIDATED_PUSH"
    version: str = "V0_1"
    task_id: str = ""

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "goal": self.goal,
            "task_type": self.task_type,
            "scope": self.scope,
            "risk": self.risk,
            "organs_route": self.organs_route,
            "allowed_write_scope": self.allowed_write_scope,
            "forbidden_actions": self.forbidden_actions,
            "push_policy": self.push_policy,
            "version": self.version,
        }


def _default_write_scope(scope: str) -> List[str]:
    mapping = {
        "PC_ONLY": ["ORGANS/IMPERIAL_IDE/OPS/STAGING/"],
        "WARP_ONLY": ["ORGANS/IMPERIAL_IDE/WARP/", "ORGANS/IMPERIAL_IDE/OPS/STAGING/"],
        "MECHANICUS_ONLY": ["ORGANS/MECHANICUS/", "ORGANS/IMPERIAL_IDE/OPS/STAGING/"],
        "IMPERIAL_IDE": ["ORGANS/IMPERIAL_IDE/", "ORGANS/IMPERIAL_IDE/OPS/STAGING/"],
        "ASTRONOMICON": ["ORGANS/ASTRONOMICON/", "ORGANS/IMPERIAL_IDE/OPS/STAGING/"],
        "FULL_REPO": ["ORGANS/", "ORGANS/IMPERIAL_IDE/OPS/STAGING/"],
    }
    return mapping.get(scope, ["ORGANS/IMPERIAL_IDE/OPS/STAGING/"])


def new_task(
    title: str,
    goal: str,
    task_type: Optional[str] = None,
    scope: str = "IMPERIAL_IDE",
    risk: str = "CONTROLLED_WRITE",
    organs_route: Optional[List[str]] = None,
    push_policy: str = "VALIDATED_PUSH",
    version: str = "V0_1",
) -> TaskIntent:
    ttype = task_type or classify(goal)
    intent = TaskIntent(
        title=title,
        goal=goal,
        task_type=ttype,
        scope=scope,
        risk=risk,
        organs_route=list(organs_route) if organs_route else ["ASTRONOMICON", "IMPERIAL_IDE"],
        allowed_write_scope=_default_write_scope(scope),
        push_policy=push_policy,
        version=version,
    )
    intent.task_id = make_task_id(ttype, title, version)
    return intent


def validate_intent(intent: TaskIntent) -> tuple[bool, List[str]]:
    problems: List[str] = []
    if not intent.title.strip():
        problems.append("title is empty")
    if not intent.goal.strip():
        problems.append("goal is empty")
    if intent.task_type not in TASK_TYPES:
        problems.append(f"unknown task_type: {intent.task_type}")
    if intent.scope not in SCOPES:
        problems.append(f"unknown scope: {intent.scope}")
    if intent.risk not in RISK_LEVELS:
        problems.append(f"unknown risk: {intent.risk}")
    if intent.push_policy not in PUSH_POLICIES:
        problems.append(f"unknown push_policy: {intent.push_policy}")
    for organ in intent.organs_route:
        if organ not in ORGANS and organ not in ("IMPERIAL_IDE",):
            problems.append(f"unknown organ in route: {organ}")
    if not intent.task_id.startswith("TASK-NEWREALITY-"):
        problems.append("task_id not formed")
    return (len(problems) == 0), problems
