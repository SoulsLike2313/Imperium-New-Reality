"""Owner-prompt constants for the bounded reference corridor."""

from __future__ import annotations


TASK_STATE_SCHEMA = "imperium.core_reference_corridor.task_state.v0_1"
TRANSITION_EVENT_SCHEMA = "imperium.core_reference_corridor.transition_event.v0_1"
PENDING_TRANSACTION_SCHEMA = "imperium.core_reference_corridor.pending_transaction.v0_1"

# The field list is copied from owner prompt section 5.2.  Adding metadata is
# permitted, but a persisted authoritative task may not omit any of these.
REQUIRED_TASK_FIELDS = frozenset(
    {
        "task_id",
        "task_type",
        "owner_intent",
        "created_at_utc",
        "base_head",
        "branch",
        "scope",
        "allowed_read_roots",
        "allowed_write_roots",
        "acceptance_tests",
        "confidence_components",
        "selected_strategy",
        "current_state",
        "state_version",
        "organ_depth_plan",
        "owner_decisions",
        "created_by",
    }
)

# Authoritative vertical route from owner prompt section 4.  These are task
# states, distinct from the evidence/checkpoint labels in section 5.10.
TASK_STATE_ROUTE = (
    "OWNER_INTENT",
    "TASK_REGISTRATION",
    "SPECIFICATION",
    "CONFIDENCE",
    "STRATEGY",
    "GREAT_NINE_PREFLIGHT",
    "THRONE_PREFLIGHT",
    "OWNER_LAUNCH_APPROVAL",
    "EXACT_HEAD_WARP",
    "SAFE_EXECUTION",
    "VALIDATION",
    "GREAT_NINE_POSTCHECK",
    "THRONE_REVIEW",
    "OWNER_ACCEPT_OR_REJECT",
    "LAND_PLAN_OR_DISCARD",
    "IMMUTABLE_EVIDENCE",
)

ALLOWED_STATE_TRANSITIONS = {
    source: frozenset({target})
    for source, target in zip(TASK_STATE_ROUTE, TASK_STATE_ROUTE[1:])
}
ALLOWED_STATE_TRANSITIONS[TASK_STATE_ROUTE[-1]] = frozenset()

# Decisions use the action vocabulary shared with the canonical registry.  A
# gate is checked while leaving an owner-decision state, so the waiting state
# itself can be persisted before any decision exists.
OWNER_GATE_REQUIREMENTS = {
    ("OWNER_LAUNCH_APPROVAL", "EXACT_HEAD_WARP"): frozenset(
        {"APPROVE_LAUNCH"}
    ),
    ("OWNER_ACCEPT_OR_REJECT", "LAND_PLAN_OR_DISCARD"): frozenset(
        {"ACCEPT_RESULT", "REJECT_RESULT", "REQUEST_REWORK"}
    ),
    ("LAND_PLAN_OR_DISCARD", "IMMUTABLE_EVIDENCE"): frozenset(
        {
            "PREPARE_LAND_PLAN",
            "PREPARE_LAND",
            "AUTHORIZE_LAND_PREPARATION",
            "ALLOW_LAND_PREPARATION",
            "FORBID_LAND",
            "DISCARD_WARP",
        }
    ),
}

INITIAL_STATE_VERSION = 1
STATE_FILENAME = "TASK_STATE.json"
TRANSITION_LOG_FILENAME = "STATE_TRANSITION_LOG.jsonl"
PENDING_TRANSACTION_FILENAME = ".TASK_STATE.pending.json"
LOCK_FILENAME = ".TASK_STATE.lock"
