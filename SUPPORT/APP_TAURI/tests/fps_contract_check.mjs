import fs from "node:fs";

const mainUrl = new URL("../src/main.js", import.meta.url);
const apiUrl = new URL("../src/corridor/api.js", import.meta.url);
const rustUrl = new URL("../src-tauri/src/main.rs", import.meta.url);
const mainSource = fs.readFileSync(mainUrl, "utf8");
const apiSource = fs.readFileSync(apiUrl, "utf8");
const rustSource = fs.readFileSync(rustUrl, "utf8");

function fail(verdict, detail) {
  console.error(JSON.stringify({ verdict, ...detail }, null, 2));
  process.exit(1);
}

const thinIde = mainSource.includes("fetchCorridorSnapshot")
  && mainSource.includes("dispatchCorridorAction");

if (thinIde) {
  const handlerBlock = rustSource.match(
    /invoke_handler\s*\(\s*tauri::generate_handler!\s*\[([\s\S]*?)\]\s*\)/,
  )?.[1];
  if (!handlerBlock) fail("FAIL_TAURI_HANDLER_MISSING", {});
  const handlerCommands = handlerBlock
    .split(",")
    .map((entry) => entry.trim().split("::").at(-1))
    .filter(Boolean);
  const forbidden = "record_runtime_fps_proof";
  const reachable = handlerCommands.includes(forbidden) || apiSource.includes(forbidden);
  if (reachable) {
    fail("FAIL_LEGACY_FPS_MUTATION_ROUTE_REACHABLE", { command: forbidden });
  }
  console.log(JSON.stringify({
    verdict: "PASS_LEGACY_FPS_MUTATION_ROUTE_FAIL_CLOSED",
    command: forbidden,
    performance_claim: "NOT_CLAIMED_BY_THIN_IDE",
  }, null, 2));
  process.exit(0);
}

const requiredLegacyFpsMarkers = [
  "FPS_LOCK_TARGET",
  "requestAnimationFrame",
  "PerformanceObserver",
  "fpsSamples",
  "reduceMotionMode",
];
const missing = requiredLegacyFpsMarkers.filter((marker) => !mainSource.includes(marker));
if (missing.length) fail("FAIL_FPS_CONTRACT", { missing });
console.log(JSON.stringify({
  verdict: "PASS_FPS_CONTRACT",
  target_fps: 60,
  frame_budget_ms: 16.67,
}, null, 2));
