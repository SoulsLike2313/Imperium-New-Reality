import "./styles/corridor.css";
import { dispatchCorridorAction, fetchCorridorSnapshot } from "./corridor/api.js";
import { createCorridorState } from "./corridor/state.js";
import { bindCorridorActions, renderCorridor } from "./corridor/render.js";

const root = document.querySelector("#app");
const state = createCorridorState();

async function refreshSnapshot() {
  state.startRequest();
  try {
    state.receiveSnapshot(await fetchCorridorSnapshot());
  } catch (error) {
    state.failRequest(error);
  }
}

async function runAction(actionId, payload) {
  state.startRequest(actionId);
  try {
    const response = await dispatchCorridorAction(actionId, payload);
    const snapshot = response.snapshot ?? await fetchCorridorSnapshot();
    state.receiveSnapshot(snapshot, response.result);
  } catch (error) {
    state.failRequest(error);
  }
}

state.subscribe((view) => {
  renderCorridor(root, view);
  bindCorridorActions(root, runAction);
});

refreshSnapshot();
