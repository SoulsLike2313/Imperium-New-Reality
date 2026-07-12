from __future__ import annotations

import copy

from ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.ui_contract import REQUIRED_PANELS, validate_ui_contract


def _fixture():
    registry = {
        "capabilities": [{"capability_id": "CAP-1"}],
        "ui_actions": [{"action_id": "action-1", "label": "Run", "panel_id": "task_state", "capability_id": "CAP-1"}],
    }
    panels = []
    for panel_id, title in REQUIRED_PANELS.items():
        panels.append(
            {
                "id": panel_id,
                "title": title,
                "cards": [{"id": f"card-{panel_id}", "title": title, "fields": []}],
                "actions": [{"id": "action-1", "label": "Run", "enabled": True}] if panel_id == "task_state" else [],
            }
        )
    snapshot = {"contract_id": "IMPERIUM_CORE_REFERENCE_CORRIDOR_THIN_IDE_V0_1", "panels": panels}
    return snapshot, registry


def test_exact_ui_contract_and_broken_parity_are_distinguished():
    snapshot, registry = _fixture()
    assert validate_ui_contract(snapshot, registry) == []

    broken = copy.deepcopy(snapshot)
    broken["panels"][1]["actions"] = []
    assert "snapshot/registry action parity mismatch" in validate_ui_contract(broken, registry)

    missing_panel = copy.deepcopy(snapshot)
    missing_panel["panels"].pop()
    assert "panel id set mismatch" in validate_ui_contract(missing_panel, registry)

