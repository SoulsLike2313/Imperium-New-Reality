"""Independent semantic validator for the Thin IDE snapshot contract."""

from __future__ import annotations

from typing import Any


REQUIRED_PANELS = {
    "new_task": "New Task",
    "task_state": "Task State",
    "great_nine_throne": "Great Nine + Throne",
    "owner_decisions": "Owner Decisions",
    "warp": "WARP",
    "capability_registry": "Capability Registry",
    "execution_trace": "Execution Trace",
    "evidence": "Evidence",
    "diff": "Diff",
    "checkpoints": "Checkpoints",
    "known_gaps": "Known Gaps",
}


def validate_ui_contract(snapshot: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if snapshot.get("contract_id") != "IMPERIUM_CORE_REFERENCE_CORRIDOR_THIN_IDE_V0_1":
        errors.append("contract_id mismatch")
    panels = snapshot.get("panels")
    if not isinstance(panels, list):
        return [*errors, "panels must be an array"]
    by_id = {item.get("id"): item for item in panels if isinstance(item, dict)}
    if set(by_id) != set(REQUIRED_PANELS):
        errors.append("panel id set mismatch")
    action_ids: list[str] = []
    card_ids: list[str] = []
    for panel_id, title in REQUIRED_PANELS.items():
        panel = by_id.get(panel_id, {})
        if panel.get("title") != title:
            errors.append(f"panel title mismatch: {panel_id}")
        if not isinstance(panel.get("cards"), list) or not isinstance(panel.get("actions"), list):
            errors.append(f"panel collections invalid: {panel_id}")
            continue
        for card in panel["cards"]:
            if not card.get("id") or not card.get("title") or not isinstance(card.get("fields"), list):
                errors.append(f"card contract invalid: {panel_id}")
            card_ids.append(card.get("id"))
        for action in panel["actions"]:
            if not action.get("id") or not action.get("label") or not isinstance(action.get("enabled"), bool):
                errors.append(f"action contract invalid: {panel_id}")
            action_ids.append(action.get("id"))
    if len(card_ids) != len(set(card_ids)):
        errors.append("duplicate card ids")
    if len(action_ids) != len(set(action_ids)):
        errors.append("duplicate action ids")
    registry_actions = {item.get("action_id") for item in registry.get("ui_actions", [])}
    if set(action_ids) != registry_actions:
        errors.append("snapshot/registry action parity mismatch")
    capabilities = {item.get("capability_id") for item in registry.get("capabilities", [])}
    for action in registry.get("ui_actions", []):
        if action.get("capability_id") and action["capability_id"] not in capabilities:
            errors.append(f"unknown capability reference: {action['action_id']}")
    return errors

