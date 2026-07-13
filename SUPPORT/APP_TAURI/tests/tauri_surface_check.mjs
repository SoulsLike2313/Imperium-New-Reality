import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(here, "..");
const repoRoot = execFileSync("git", ["rev-parse", "--show-toplevel"], {
  cwd: appRoot,
  encoding: "utf8",
}).trim();

function invariant(condition, message, detail = undefined) {
  if (!condition) throw Object.assign(new Error(message), { detail });
}

function sameMembers(actual, expected, label) {
  const left = [...actual].sort();
  const right = [...expected].sort();
  invariant(JSON.stringify(left) === JSON.stringify(right), `${label} mismatch`, { actual: left, expected: right });
}

const rustPath = path.join(appRoot, "src-tauri", "src", "main.rs");
const apiPath = path.join(appRoot, "src", "corridor", "api.js");
const inventoryPath = path.join(
  repoRoot,
  "ORGANS",
  "MECHANICUS",
  "REPORTS",
  "IMPERIUM-CORE-REFERENCE-CORRIDOR-TRUTH-HARDENING-0002",
  "TAURI_COMMAND_INVENTORY.json",
);
const rustSource = fs.readFileSync(rustPath, "utf8");
const apiSource = fs.readFileSync(apiPath, "utf8");
const inventory = JSON.parse(fs.readFileSync(inventoryPath, "utf8"));
const handlerBlock = rustSource.match(/invoke_handler\s*\(\s*tauri::generate_handler!\s*\[([\s\S]*?)\]\s*\)/)?.[1];
invariant(handlerBlock, "real Rust invoke_handler is missing");
const handlerCommands = handlerBlock
  .split(",")
  .map((entry) => entry.trim().split("::").at(-1))
  .filter(Boolean);
const frontendBlock = apiSource.match(/CORRIDOR_BRIDGE_COMMANDS\s*=\s*Object\.freeze\(\{([\s\S]*?)\}\)/)?.[1];
invariant(frontendBlock, "frontend corridor bridge contract is missing");
const frontendCommands = [...frontendBlock.matchAll(/\w+\s*:\s*"([^"]+)"/g)].map((match) => match[1]);

sameMembers(handlerCommands, inventory.registered_tauri_commands, "inventory/Rust invoke handler");
sameMembers(frontendCommands, handlerCommands, "frontend/Rust fail-closed surface");
invariant(inventory.surface_verdict === "LEGACY_MUTATION_SURFACE_CLOSED", "inventory surface verdict is not closed");
invariant(!Object.values(inventory.effect_classification).includes("UNKNOWN"), "reachable UNKNOWN command exists");
for (const command of inventory.commands) {
  if (command.effect === "MUTATING") {
    invariant(command.typed_executor_routed, `${command.command} bypasses typed executor`);
    invariant(command.owner_gate_required, `${command.command} bypasses Owner gate`);
    invariant(command.canonical_capability_registry_routed, `${command.command} bypasses capability registry`);
  }
}
for (const command of [
  "register_patch_pack",
  "register_patch_pack_with_organs",
  "record_runtime_fps_proof",
  "initialize_imperium_core_update",
]) {
  const probe = inventory.legacy_command_probes.find((item) => item.command === command);
  invariant(probe?.effect === "MUTATING", `${command} is not classified MUTATING`);
  invariant(probe?.direct_invocation_result === "BLOCK_COMMAND_NOT_REGISTERED", `${command} does not fail closed`);
}

console.log(JSON.stringify({
  verdict: "PASS_TAURI_LEGACY_MUTATION_SURFACE_CHECK",
  handler_commands: handlerCommands,
  frontend_commands: frontendCommands,
  required_legacy_blocked: 4,
}, null, 2));
