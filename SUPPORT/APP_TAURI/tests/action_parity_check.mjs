import { execFileSync, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(here, "..");
const repoRoot = execFileSync("git", ["rev-parse", "--show-toplevel"], {
  cwd: appRoot,
  encoding: "utf8",
}).trim();

function invariant(condition, message, detail = undefined) {
  if (!condition) {
    const error = new Error(message);
    error.detail = detail;
    throw error;
  }
}

function sameMembers(actual, expected, label) {
  const left = [...actual].sort();
  const right = [...expected].sort();
  invariant(JSON.stringify(left) === JSON.stringify(right), `${label} mismatch`, { actual: left, expected: right });
}

function parseSnapshot() {
  const result = spawnSync(
    "python",
    ["-m", "ORGANS.MECHANICUS.CORE_REFERENCE_CORRIDOR.cli", "ui-snapshot"],
    { cwd: repoRoot, encoding: "utf8", timeout: 20_000, windowsHide: true },
  );
  invariant(!result.error, "ui-snapshot could not be started", String(result.error ?? ""));
  invariant(result.status === 0, "ui-snapshot returned a non-zero exit", {
    status: result.status,
    stdout: result.stdout,
    stderr: result.stderr,
  });
  try {
    return JSON.parse(result.stdout);
  } catch (error) {
    throw Object.assign(new Error("ui-snapshot did not return one JSON document"), {
      detail: { parse_error: String(error), stdout: result.stdout, stderr: result.stderr },
    });
  }
}

function capabilityIds(registry) {
  const ids = new Set();
  const collect = (container) => {
    if (Array.isArray(container)) {
      for (const item of container) {
        const id = item?.capability_id ?? item?.action_id ?? item?.id;
        if (typeof id === "string" && id) ids.add(id);
      }
    } else if (container && typeof container === "object") {
      for (const [key, item] of Object.entries(container)) {
        const id = item?.capability_id ?? item?.action_id ?? item?.id ?? key;
        if (typeof id === "string" && id) ids.add(id);
      }
    }
  };
  collect(registry.capabilities);
  collect(registry.actions);
  collect(registry.entries);
  return ids;
}

function registryUiActions(registry) {
  invariant(Array.isArray(registry.ui_actions), "canonical registry ui_actions must be an array");
  const actions = new Map();
  for (const action of registry.ui_actions) {
    invariant(typeof action?.action_id === "string" && action.action_id, "registry UI action has no action_id");
    invariant(!actions.has(action.action_id), `duplicate registry UI action ${action.action_id}`);
    actions.set(action.action_id, action);
  }
  return actions;
}

function attributeValues(markup, attribute) {
  const pattern = new RegExp(`${attribute}="([A-Za-z0-9_.:-]+)"`, "g");
  return [...markup.matchAll(pattern)].map((match) => match[1]);
}

const requiredPanels = new Map([
  ["new_task", "New Task"],
  ["task_state", "Task State"],
  ["great_nine_throne", "Great Nine + Throne"],
  ["owner_decisions", "Owner Decisions"],
  ["warp", "WARP"],
  ["capability_registry", "Capability Registry"],
  ["execution_trace", "Execution Trace"],
  ["evidence", "Evidence"],
  ["diff", "Diff"],
  ["checkpoints", "Checkpoints"],
  ["known_gaps", "Known Gaps"],
]);

const snapshot = parseSnapshot();
invariant(snapshot && typeof snapshot === "object" && !Array.isArray(snapshot), "snapshot must be an object");
invariant(typeof snapshot.contract_id === "string" && snapshot.contract_id.length > 0, "snapshot contract_id is required");
invariant(Array.isArray(snapshot.panels), "snapshot panels must be an array");
sameMembers(snapshot.panels.map((panel) => panel?.id), requiredPanels.keys(), "backend panel ids");

const cardIds = [];
const actions = [];
for (const panel of snapshot.panels) {
  invariant(panel.title === requiredPanels.get(panel.id), `backend title mismatch for panel ${panel.id}`);
  invariant(Array.isArray(panel.cards), `panel ${panel.id} must supply cards`);
  invariant(Array.isArray(panel.actions), `panel ${panel.id} must supply actions`);
  for (const card of panel.cards) {
    invariant(typeof card?.id === "string" && card.id.length > 0, `panel ${panel.id} contains a card without id`);
    invariant(typeof card?.title === "string" && card.title.length > 0, `card ${card?.id} has no backend title`);
    cardIds.push(card.id);
  }
  for (const action of panel.actions) {
    invariant(typeof action?.id === "string" && action.id.length > 0, `panel ${panel.id} contains an action without id`);
    invariant(typeof action?.label === "string" && action.label.length > 0, `action ${action?.id} has no backend label`);
    invariant(typeof action?.enabled === "boolean", `action ${action?.id} has no explicit enabled gate`);
    actions.push(action);
  }
}
invariant(new Set(cardIds).size === cardIds.length, "backend card ids must be unique");
invariant(new Set(actions.map((action) => action.id)).size === actions.length, "backend action ids must be unique");

const registryPath = path.join(
  repoRoot,
  "ORGANS",
  "MECHANICUS",
  "REPORTS",
  "IMPERIUM-CORE-REFERENCE-CORRIDOR-0001",
  "CAPABILITY_REGISTRY.json",
);
invariant(fs.existsSync(registryPath) && fs.statSync(registryPath).isFile(), "canonical capability registry is missing", registryPath);
const registry = JSON.parse(fs.readFileSync(registryPath, "utf8"));
const registeredCapabilities = capabilityIds(registry);
const registeredUiActions = registryUiActions(registry);
invariant(registeredCapabilities.size > 0, "canonical capability registry exposes no capability ids");
sameMembers(actions.map((action) => action.id), registeredUiActions.keys(), "snapshot/registry UI actions");
for (const action of actions) {
  const registryAction = registeredUiActions.get(action.id);
  invariant(action.label === registryAction.label, `UI action ${action.id} label differs from its registry entry`);
  if (registryAction.capability_id) {
    invariant(
      registeredCapabilities.has(registryAction.capability_id),
      `UI action ${action.id} names an unknown capability`,
      { capability_id: registryAction.capability_id },
    );
  }
}

const renderModuleUrl = pathToFileURL(path.join(appRoot, "src", "corridor", "render.js")).href;
const { renderCorridorMarkup } = await import(renderModuleUrl);
const markup = renderCorridorMarkup(snapshot);
sameMembers(attributeValues(markup, "data-panel-id"), snapshot.panels.map((panel) => panel.id), "rendered panel markers");
sameMembers(attributeValues(markup, "data-card-id"), cardIds, "rendered card markers");
sameMembers(attributeValues(markup, "data-action-id"), actions.map((action) => action.id), "rendered action markers");

const apiSource = fs.readFileSync(path.join(appRoot, "src", "corridor", "api.js"), "utf8");
const rustSource = fs.readFileSync(path.join(appRoot, "src-tauri", "src", "main.rs"), "utf8");
const bridgeBlock = apiSource.match(/CORRIDOR_BRIDGE_COMMANDS\s*=\s*Object\.freeze\(\{([\s\S]*?)\}\)/)?.[1];
invariant(bridgeBlock, "frontend bridge command contract is missing");
const frontendCommands = [...bridgeBlock.matchAll(/\w+\s*:\s*"([^"]+)"/g)].map((match) => match[1]);
const handlerBlock = rustSource.match(/invoke_handler\(tauri::generate_handler!\[([\s\S]*?)\]\)/)?.[1];
invariant(handlerBlock, "Rust Tauri invoke handler is missing");
const handlerCommands = handlerBlock
  .split(",")
  .map((entry) => entry.trim().split("::").at(-1))
  .filter(Boolean);
const corridorHandlerCommands = handlerCommands.filter((name) => name.startsWith("corridor_ui_"));
sameMembers(frontendCommands, corridorHandlerCommands, "frontend/Rust corridor command surface");
invariant(!handlerCommands.includes("run_registered_patch_pack"), "direct legacy runner remains in the Tauri invoke surface");
invariant(!/fn\s+run_registered_patch_pack\s*\(/.test(rustSource), "direct legacy runner implementation remains compiled");

console.log(JSON.stringify({
  verdict: "PASS_CORRIDOR_UI_BACKEND_SEMANTIC_PARITY",
  contract_id: snapshot.contract_id,
  panel_count: snapshot.panels.length,
  card_count: cardIds.length,
  action_count: actions.length,
  bridge_commands: frontendCommands.sort(),
}, null, 2));
