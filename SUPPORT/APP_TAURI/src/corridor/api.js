import { invoke } from "@tauri-apps/api/core";

export const CORRIDOR_BRIDGE_COMMANDS = Object.freeze({
  snapshot: "corridor_ui_snapshot",
  action: "corridor_ui_action",
});

function isRecord(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function validateAction(action, panelId) {
  if (!isRecord(action) || typeof action.id !== "string" || action.id.length === 0) {
    throw new Error(`Corridor snapshot contains an invalid action in panel ${panelId}`);
  }
  if (typeof action.label !== "string" || action.label.length === 0) {
    throw new Error(`Corridor action ${action.id} has no backend label`);
  }
  if (typeof action.enabled !== "boolean") {
    throw new Error(`Corridor action ${action.id} has no explicit enabled gate`);
  }
}

function validateCard(card, panelId) {
  if (!isRecord(card) || typeof card.id !== "string" || card.id.length === 0) {
    throw new Error(`Corridor snapshot contains an invalid card in panel ${panelId}`);
  }
  if (typeof card.title !== "string" || card.title.length === 0) {
    throw new Error(`Corridor card ${card.id} has no backend title`);
  }
}

export function validateCorridorSnapshot(snapshot) {
  if (!isRecord(snapshot)) {
    throw new Error("Corridor backend returned a non-object snapshot");
  }
  if (typeof snapshot.contract_id !== "string" || snapshot.contract_id.length === 0) {
    throw new Error("Corridor snapshot is missing contract_id");
  }
  if (!Array.isArray(snapshot.panels)) {
    throw new Error("Corridor snapshot is missing backend panels");
  }

  const panelIds = new Set();
  const actionIds = new Set();
  for (const panel of snapshot.panels) {
    if (!isRecord(panel) || typeof panel.id !== "string" || panel.id.length === 0) {
      throw new Error("Corridor snapshot contains a panel without an id");
    }
    if (panelIds.has(panel.id)) {
      throw new Error(`Corridor snapshot contains duplicate panel ${panel.id}`);
    }
    panelIds.add(panel.id);
    if (typeof panel.title !== "string" || panel.title.length === 0) {
      throw new Error(`Corridor panel ${panel.id} has no backend title`);
    }
    if (!Array.isArray(panel.cards) || !Array.isArray(panel.actions)) {
      throw new Error(`Corridor panel ${panel.id} must supply cards and actions arrays`);
    }
    for (const card of panel.cards) validateCard(card, panel.id);
    for (const action of panel.actions) {
      validateAction(action, panel.id);
      if (actionIds.has(action.id)) {
        throw new Error(`Corridor snapshot contains duplicate action ${action.id}`);
      }
      actionIds.add(action.id);
    }
  }
  return snapshot;
}

function snapshotFromResponse(response) {
  if (isRecord(response?.snapshot)) {
    return validateCorridorSnapshot(response.snapshot);
  }
  if (Array.isArray(response?.panels)) {
    return validateCorridorSnapshot(response);
  }
  return null;
}

export async function fetchCorridorSnapshot() {
  const response = await invoke(CORRIDOR_BRIDGE_COMMANDS.snapshot);
  return validateCorridorSnapshot(response);
}

export async function dispatchCorridorAction(actionId, payload = {}) {
  if (typeof actionId !== "string" || actionId.length === 0) {
    throw new Error("A backend-supplied action id is required");
  }
  if (!isRecord(payload)) {
    throw new Error("Corridor action payload must be an object");
  }
  const result = await invoke(CORRIDOR_BRIDGE_COMMANDS.action, { actionId, payload });
  return { result, snapshot: snapshotFromResponse(result) };
}
