import { invoke } from "@tauri-apps/api/core";
import "./styles.css";

const IMPERIUM_TAURI_SHELL = "IMPERIUM_TAURI_SHELL";
const IMPERIUM_APP_PLATFORM = "IMPERIUM_APP_PLATFORM";
const IMPERIUM_CORE_PRODUCT_NAME = "Imperium Core";
const IMPERIUM_CORE_VERSIONING = "IMPERIUM_CORE_VERSIONING_V0_1";
const IMPERIUM_CORE_UPDATE_FLOW = "IMPERIUM_CORE_UPDATE_FLOW_TERMINAL_STAGED_V0_1";
const IMPERIUM_APP_UI_TARGET_FORM = "IMPERIUM_APP_UI_TARGET_FORM";
const IMPERIUM_APP_UI_CABIN_FRAME = "IMPERIUM_APP_UI_CABIN_FRAME";
const IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3 = "IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3";
const COMMAND_RAIL = "COMMAND_RAIL";
const COMMAND_DECK_V3 = "COMMAND_DECK_V3";
const UX_PROOF_MARKER = "UX_PROOF_MARKER";
const CABIN_FRAME_UX_PROOF = "CABIN_FRAME_UX_PROOF";
const ORGAN_HUB_ROOM = "ORGAN_HUB_ROOM";
const PATCH_FORGE_ROOM = "PATCH_FORGE_ROOM_DEPRECATED_ASTRONOMICON_OWNS_REGISTRATION_AND_LAUNCH";
const MECHANICUS_ROOM = "MECHANICUS_ROOM";
const PATCH_REGISTRY = "PATCH_REGISTRY";
const LANGUAGE_POWER_CODEX = "LANGUAGE_POWER_CODEX";
const AQUARIUM = "AQUARIUM";
const APP_COCKPIT_MERGED_INTO_PLATFORM = "APP_COCKPIT_MERGED_INTO_PLATFORM";
const NO_FAKE_EXECUTION_CLAIMED_MARKER = "No fake execution claimed";
const FPS_LOCK_TARGET = 60;
const RUNTIME_FPS_PROOF = "RUNTIME_FPS_PROOF";
const ASTRONOMICON_PATCH_PICKER_DARK_LIST_V0_1 = "ASTRONOMICON_PATCH_PICKER_DARK_LIST_V0_1";
const APP_REGISTRATION_PATCH_ID = "IMPERIUM-APP-ASTRONOMICON-MECHANICUS-REGISTRATION-0001";
const DAILY_UI_REFIT_CANDIDATE_PATCH_ID = "IMPERIUM-APP-DAILY-USE-UI-REFIT-CANDIDATE-0001";
const TWO_PHASE_REGISTRATION_MARKER = "IMPERIUM_APP_TWO_PHASE_ORGAN_REGISTRATION_V0_1";
const DAILY_USE_UI_REFIT_POLISHED = "IMPERIUM_APP_DAILY_USE_UI_REFIT_POLISHED_V0_1";
const COMPACT_PROOF_DIGEST = "COMPACT_PROOF_DIGEST_V0_1";

let activeRoom = "astronomicon";
let patchPacks = [];
let selectedPatchId = "";
let patchSearch = "";
let registeredPatchId = "";
let registeredPatchStatus = "none";
let organSummary = null;
let organSummaryStatus = "not_loaded";
let languagePowers = [];
let aquariumLines = [];
let runtimeFpsProofSent = false;
let frameDeltas = [];
let lastFrame = 0;
let uxActionCount = 0;
let fpsDisplay = "60.0";
let imperiumCoreVersion = { current_version: "0.1.0-alpha.0", available_version: "0.1.0-alpha.0", update_available: false, update_status: "CURRENT" };

const roomList = [
  { id: "organ-hub", label: "Organ Hub", marker: ORGAN_HUB_ROOM, icon: "✦", purpose: "organs" },
  { id: "mechanicus", label: "Mechanicus", marker: MECHANICUS_ROOM, icon: "⌬", purpose: "machine" },
  { id: "astronomicon", label: "Astronomicon", marker: "ASTRONOMICON_ROOM", icon: "✶", purpose: "intake" },
  { id: "throne", label: "Throne", marker: "THRONE_ROOM", icon: "♛", purpose: "crown" },
  { id: "eyes", label: "Eyes Room", marker: "EYES_ROOM", icon: "◉", purpose: "viewer" },
  { id: "seed-core", label: "Seed Core", marker: "SEED_CORE_ROOM", icon: "◇", purpose: "runtime" },
];

const knownOrgans = [
  { id: "ASTRONOMICON", title: "Astronomicon", status: "reference implementation", gate: "local crown-aware", note: "intake, patch form, readouts, advisory direction", icon: "✶", grade: "REF" },
  { id: "MECHANICUS", title: "Mechanicus", status: "next primary organ", gate: "Gate 1–2 forming", note: "machine reality, toolchains, build/runtime proof", icon: "⌬", grade: "NEXT" },
  { id: "DOCTRINARIUM", title: "Doctrinarium", status: "support law organ", gate: "six-gate canon landed", note: "laws, schemas, operator school", icon: "⚖", grade: "LAW" },
  { id: "CUSTODES", title: "Custodes", status: "prosecutor", gate: "universal matrix received", note: "external accusation and anti-self-trust", icon: "♜", grade: "PROS" },
  { id: "THRONE", title: "Throne", status: "special Crown organ", gate: "crown-gate laws received", note: "local success cannot become global fake readiness", icon: "♛", grade: "CROWN" },
  { id: "ADMINISTRATUM", title: "Administratum", status: "deferred to last", gate: "Owner intent fixed", note: "registrar/ledger after organs self-report", icon: "▣", grade: "LAST" },
];

const fallbackLanguagePowers = [
  { language: "Python", role: "orchestration, receipts, scans, JSON", use_when: "glue scripts, WARP helpers, reports", proof: "python --version; py_compile", warning: "Python binds; it does not replace compile proof" },
  { language: "Rust", role: "strict validators, Tauri backend, compiled proof", use_when: "trust-critical gates, parsers, state", proof: "rustc; cargo check; cargo test", warning: "stronger proof, slower iteration" },
  { language: "Go", role: "portable CLI, workers, network utilities", use_when: "fast simple binaries and external tools", proof: "go version; go test; go build", warning: "practical force, less strict than Rust" },
  { language: "C++", role: "deep optimization and native hot paths", use_when: "only after profiling proves need", proof: "cl/g++; cmake build", warning: "chosen by measured necessity only" },
  { language: "TypeScript", role: "Tauri frontend and operator surfaces", use_when: "rooms, panels, visual control", proof: "node; npm; npm run build", warning: "UI renders truth, does not prove truth" },
  { language: "PowerShell", role: "Windows host runners", use_when: "WARP scripts and command sequencing", proof: "pwsh --version; receipt exists", warning: "Windows lane with quoting discipline" },
];

const trialMission = {
  task_id: "IMPERIUM-APP-DAILY-USE-UI-REFIT-CANDIDATE-0001",
  title: "Daily-use UI refit candidate",
  class: "UI_PRODUCT_SURFACE_OR_VISUAL_RUNTIME",
  goal: "Перебрать daily-use UI: чистый органальный лог, premium gothic-metal surface, two-phase registration, node boundaries, dependency impact, and future Eyes/Canvas integration plan.",
  expected_stack: ["JavaScript/TypeScript", "CSS modules/tokens", "Rust/Tauri commands", "JSON contracts", "Python validators", "PowerShell WARP runner", "FPS + screenshot fidelity proof"],
  mechanicus_pressure: ["monolith control", "node boundary map", "visual stack plan", "dependency impact", "runtime proof"]
};

function nowStamp() {
  return new Date().toLocaleTimeString();
}

function activeRoomLabel() {
  return roomList.find((room) => room.id === activeRoom)?.label || activeRoom;
}

function markUx(actionName) {
  uxActionCount += 1;
  logAquarium("UX", `${UX_PROOF_MARKER} ${COMMAND_DECK_V3} action=${actionName} count=${uxActionCount}`);
}

function logAquarium(kind, message) {
  const line = `[${nowStamp()}][${kind}] ${message}`;
  aquariumLines = [...aquariumLines.slice(-60), line];
  render();
}

async function callAnyCommand(names, payload = {}) {
  let lastError = null;
  for (const name of names) {
    try {
      const result = await invoke(name, payload);
      logAquarium("PASS", `${name} returned`);
      return { ok: true, command: name, result };
    } catch (err) {
      lastError = err;
    }
  }
  logAquarium("WARN", `Backend command unavailable: ${names.join(", ")} :: ${String(lastError || "")}`);
  return { ok: false, error: String(lastError || "command not available") };
}


async function refreshImperiumCoreVersion() {
  const response = await callAnyCommand(["get_imperium_core_version_state"]);
  if (response.ok) {
    imperiumCoreVersion = response.result || imperiumCoreVersion;
    if (imperiumCoreVersion.update_available) {
      logAquarium("UPDATE", `Imperium Core update available: ${imperiumCoreVersion.current_version} → ${imperiumCoreVersion.available_version}`);
    }
  }
  render();
}

async function initializeImperiumCoreUpdate() {
  markUx("imperium_core_update_initialize");
  const requestedVersion = imperiumCoreVersion?.available_version || "";
  const response = await callAnyCommand(["initialize_imperium_core_update"], { requestedVersion, requested_version: requestedVersion });
  if (response.ok) {
    logAquarium("UPDATE", `Imperium Core update initialized: ${response.result?.verdict || "PASS"}`);
  } else {
    logAquarium("BLOCKED", `Imperium Core update init failed: ${response.error}`);
  }
  await refreshImperiumCoreVersion();
}

function renderCoreVersionStrip() {
  const current = imperiumCoreVersion?.current_version || "unknown";
  const available = imperiumCoreVersion?.available_version || current;
  const status = imperiumCoreVersion?.update_available ? "UPDATE_AVAILABLE" : "CURRENT";
  return `<div class="core-version-strip" data-marker="${IMPERIUM_CORE_VERSIONING}">
    <span><b>Current version</b><em>${escapeHtml(current)}</em></span>
    <span><b>Available</b><em>${escapeHtml(available)}</em></span>
    <span class="version-status ${imperiumCoreVersion?.update_available ? "hot" : "ok"}">${status}</span>
    <button id="imperium-core-update" class="update-button ${imperiumCoreVersion?.update_available ? "lit" : ""}" ${imperiumCoreVersion?.update_available ? "" : "disabled"}>Update</button>
  </div>`;
}

function normalizePatches(result) {
  const raw = Array.isArray(result) ? result :
    Array.isArray(result?.patches) ? result.patches :
    Array.isArray(result?.items) ? result.items :
    Array.isArray(result?.patch_packs) ? result.patch_packs : [];

  return raw.map((item) => {
    if (typeof item === "string") return { patch_id: item, status: "DISCOVERED", runner: "" };
    return {
      patch_id: item.patch_id || item.id || item.name || item.title || "UNKNOWN_PATCH",
      status: item.status || item.state || "DISCOVERED",
      runner: item.runner || item.runner_path || item.run_script || item.has_runner ? "RUNNER" : "",
      path: item.path || item.patch_path || "",
      modified_unix: Number(item.modified_unix || item.modified || 0),
      workflow_phase: item.workflow_phase || item.phase || "STANDARD_WARP_PATCH_PACK",
      launch_allowed: item.launch_allowed !== undefined ? Boolean(item.launch_allowed) : true,
      registered: Boolean(item.registered),
    };
  }).filter((x) => x.patch_id && x.patch_id !== "UNKNOWN_PATCH");
}

async function refreshPatchPacks() {
  markUx("refresh_patch_packs");
  const response = await callAnyCommand(["discover_patch_packs", "list_patch_packs", "get_patch_packs", "refresh_patch_registry", "list_warp_patch_packs"]);
  if (response.ok) {
    patchPacks = normalizePatches(response.result);
    const preferred = patchPacks.find((p) => p.patch_id === DAILY_UI_REFIT_CANDIDATE_PATCH_ID) || patchPacks.find((p) => p.patch_id === APP_REGISTRATION_PATCH_ID) || patchPacks[0];
    selectedPatchId = selectedPatchId && patchPacks.some((p) => p.patch_id === selectedPatchId) ? selectedPatchId : (preferred?.patch_id || "");
    logAquarium("PATCH", `Patch packs visible: ${patchPacks.length}`);
  } else if (patchPacks.length === 0) {
    patchPacks = [{ patch_id: "PATCH_REGISTRY_BACKEND_PENDING", status: "LOCAL_PLACEHOLDER", runner: "—" }];
    selectedPatchId = patchPacks[0].patch_id;
    logAquarium("PATCH", "Backend patch discovery unavailable; showing non-execution placeholder");
  }
  render();
}


function normalizeOrganRegistrationResult(result) {
  const summary = result?.organ_summary || result;
  return summary && summary.astronomicon && summary.mechanicus ? summary : null;
}

function summarizeArray(items, limit = 6) {
  if (!Array.isArray(items) || items.length === 0) return "none";
  const head = items.slice(0, limit).map((item) => typeof item === "string" ? item : (item.toolchain || item.zone || item.name || JSON.stringify(item).slice(0, 60)));
  const rest = items.length > limit ? ` +${items.length - limit}` : "";
  return `${head.join(", ")}${rest}`;
}


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function sortedPatchPacks() {
  return [...patchPacks].sort((a, b) => {
    if (a.patch_id === DAILY_UI_REFIT_CANDIDATE_PATCH_ID) return -1;
    if (b.patch_id === DAILY_UI_REFIT_CANDIDATE_PATCH_ID) return 1;
    if (a.patch_id === APP_REGISTRATION_PATCH_ID) return -1;
    if (b.patch_id === APP_REGISTRATION_PATCH_ID) return 1;
    return Number(b.modified_unix || 0) - Number(a.modified_unix || 0) || String(a.patch_id).localeCompare(String(b.patch_id));
  });
}

function visiblePatchPacks(limit = 14) {
  const query = patchSearch.trim().toUpperCase();
  const items = sortedPatchPacks().filter((p) => !query || p.patch_id.toUpperCase().includes(query));
  return items.slice(0, limit);
}

function patchPickLabel(p) {
  const flags = [];
  if (p.patch_id === DAILY_UI_REFIT_CANDIDATE_PATCH_ID) flags.push("next candidate");
  if (p.patch_id === APP_REGISTRATION_PATCH_ID) flags.push("current proof");
  if (p.workflow_phase === "CANDIDATE_INTAKE_PACK") flags.push("candidate");
  if (p.launch_allowed === false) flags.push("analysis only");
  if (p.registered) flags.push("registered");
  if (p.has_runner || p.runner) flags.push("runner");
  if (p.modified_unix) flags.push("recent");
  return flags.join(" · ") || (p.status || "discovered");
}

async function registerPatchPack() {
  markUx("astronomicon_register_patch_pack");
  if (!selectedPatchId || selectedPatchId === "PATCH_REGISTRY_BACKEND_PENDING") {
    logAquarium("BLOCKED", "No real patch selected for Astronomicon registration");
    return;
  }
  const response = await callAnyCommand([
    "register_patch_pack_with_organs",
    "analyze_patch_pack_organ_summary",
    "register_patch_pack"
  ], { patchId: selectedPatchId, patch_id: selectedPatchId });
  registeredPatchId = selectedPatchId;
  if (response.ok) {
    const summary = normalizeOrganRegistrationResult(response.result);
    organSummary = summary;
    organSummaryStatus = summary ? "organ_summary_ready" : "registered_without_organ_summary";
    registeredPatchStatus = response.result?.verdict || "backend_registered";
    if (summary) {
      logAquarium("ASTRONOMICON", `${summary.astronomicon?.verdict || "REGISTERED"} patch=${selectedPatchId}`);
      logAquarium("MECHANICUS", `${summary.mechanicus?.verdict || "SUMMARY"} class=${summary.mechanicus?.task_class || "unknown"}`);
      logAquarium("WORKFLOW", `${workflowPhase(summary)} → ${workflowLaunchLabel(summary)}`);
    } else {
      logAquarium("PATCH", `Registered patch pack without organ summary: ${registeredPatchId}`);
    }
  } else {
    organSummaryStatus = "backend_unavailable_local_registration_only";
    registeredPatchStatus = "local_registered_backend_pending";
    logAquarium("PATCH", `Local registration only: ${registeredPatchId}; ${NO_FAKE_EXECUTION_CLAIMED_MARKER}`);
  }
  render();
}

async function runRegisteredPatchPack() {
  markUx("astronomicon_launch_registered_polished_pack");
  if (!registeredPatchId) {
    logAquarium("BLOCKED", "Astronomicon launch gate requires a registered polished pack");
    return;
  }
  const response = await callAnyCommand(["run_registered_patch_pack", "run_registered_patch", "run_patch_pack", "run_warp_patch_pack"], { patchId: registeredPatchId, patch_id: registeredPatchId });
  if (response.ok) {
    logAquarium("RUN", `Astronomicon launch gate requested for polished pack: ${registeredPatchId}`);
    if (response.result) logAquarium("RUN", JSON.stringify(response.result).slice(0, 900));
  } else {
    logAquarium("BLOCKED", `Astronomicon launch gate blocked or unavailable for ${registeredPatchId}; ${NO_FAKE_EXECUTION_CLAIMED_MARKER}`);
  }
  render();
}

async function loadLanguagePowers() {
  markUx("load_language_powers");
  const response = await callAnyCommand(["get_mechanicus_language_codex", "load_language_power_codex", "load_language_powers", "get_language_powers", "mechanicus_language_powers"]);
  if (response.ok) {
    const raw = Array.isArray(response.result) ? response.result :
      Array.isArray(response.result?.languages) ? response.result.languages :
      Array.isArray(response.result?.powers) ? response.result.powers :
      Array.isArray(response.result?.languages) ? response.result.languages :
      Array.isArray(response.result?.language_powers) ? response.result.language_powers : [];
    languagePowers = raw.length ? raw : fallbackLanguagePowers;
  } else {
    languagePowers = fallbackLanguagePowers;
    logAquarium("MECHANICUS", "Loaded fallback Language Power Codex from frontend law");
  }
  render();
}

async function saveAquariumLog() {
  markUx("save_aquarium_log");
  const body = aquariumLines.join("\n");
  const response = await callAnyCommand(["save_aquarium_log", "save_app_log", "write_app_log"], { body, log: body, content: body });
  if (!response.ok) {
    const blob = new Blob([body], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `imperium_aquarium_${Date.now()}.log`;
    a.click();
    URL.revokeObjectURL(url);
    logAquarium("SAVE", "Aquarium log offered as browser download fallback");
  }
}

async function openLogs() {
  markUx("open_logs");
  const response = await callAnyCommand(["open_logs", "open_app_logs", "open_log_folder"]);
  if (!response.ok) logAquarium("INFO", "Open logs backend unavailable; use SUPPORT/APP_TAURI/logs or receipts");
}

function renderRoomNav() {
  return `<nav class="room-nav" aria-label="Imperium rooms">
    ${roomList.map((room) => `
      <button class="room-button ${activeRoom === room.id ? "active" : ""}" data-room="${room.id}">
        <span class="room-icon">${room.icon}</span>
        <span class="room-label">${room.label}</span>
        <small>${room.marker}</small>
      </button>
    `).join("")}
  </nav>`;
}

function renderStatusTiles() {
  return `<div class="status-tile-row">
    <div class="status-tile"><b>${fpsDisplay}</b><span>FPS</span></div>
    <div class="status-tile"><b>${patchPacks.length}</b><span>Patch Packs</span></div>
    <div class="status-tile"><b>${uxActionCount}</b><span>UX Proofs</span></div>
    <div class="status-tile"><b>0</b><span>Global Assembled</span></div>
  </div>`;
}

function renderOrganHub() {
  return `<section class="room-panel organ-hub-panel" data-marker="${ORGAN_HUB_ROOM}">
    <div class="panel-title-row">
      <div>
        <p class="eyebrow">ORGAN HUB</p>
        <h2>Organ Hub</h2>
        <p class="muted">The application remains the main Imperium shell. Operational cockpit powers are rooms inside it, not a replacement.</p>
      </div>
    </div>
    ${renderStatusTiles()}
    <div class="organ-grid">
      ${knownOrgans.map((organ) => `
        <article class="organ-card">
          <div class="organ-grade">${organ.grade}</div>
          <div class="organ-sigil">${organ.icon}</div>
          <div class="organ-body">
            <span class="organ-id">${organ.id}</span>
            <h3>${organ.title}</h3>
            <p>${organ.note}</p>
            <div class="organ-meta">
              <span>${organ.status}</span>
              <span>${organ.gate}</span>
            </div>
          </div>
        </article>
      `).join("")}
    </div>
  </section>`;
}

function renderPatchForge() {
  return `<section class="room-panel patch-forge-panel deprecated-forge" data-marker="${PATCH_FORGE_ROOM}">
    <p class="eyebrow">PATCH FORGE DEPRECATED</p>
    <h2>Registration and launch moved to Astronomicon</h2>
    <p class="muted">Candidate and polished pack flow is owned by Astronomicon. Mechanicus answers with machine stack and debt. This panel remains only as a compatibility marker.</p>
    <div class="control-row"><button id="goto-astronomicon">Open Astronomicon</button></div>
  </section>`;
}


function workflowPhase(summary) {
  return summary?.two_phase_workflow?.phase || summary?.mechanicus?.workflow_phase || "NO_REGISTRATION_YET";
}

function workflowLaunchLabel(summary) {
  const flow = summary?.two_phase_workflow;
  if (!flow) return "WAITING_FOR_REGISTRATION";
  if (flow.candidate_registration) return "POLISHED_PACK_REQUIRED_BEFORE_RUN";
  return flow.launch_allowed_from_app ? "LAUNCH_GATE_AVAILABLE_AFTER_OWNER_REVIEW" : "RUN_BLOCKED";
}

function renderTwoPhaseWorkflow(summary) {
  const flow = summary?.two_phase_workflow;
  const phase = workflowPhase(summary);
  const launch = workflowLaunchLabel(summary);
  const candidateState = flow?.candidate_registration ? "ACTIVE" : (summary ? "NOT_THIS_PACK" : "WAITING");
  const polishedState = flow?.polished_pack_required ? "REQUIRED" : (summary ? "NOT_REQUIRED_BY_THIS_PACK" : "WAITING");
  const launchState = launch;
  return `<div class="two-phase-board" data-marker="${TWO_PHASE_REGISTRATION_MARKER}">
    <article class="phase-card ${candidateState === "ACTIVE" ? "hot" : ""}"><b>1 · Candidate</b><span>${candidateState}</span><small>Органы читают намерение, стек, долги и риск. Запуск запрещён.</small></article>
    <article class="phase-card ${polishedState === "REQUIRED" ? "warn" : ""}"><b>2 · Polished Pack</b><span>${polishedState}</span><small>Собирается после органальной сводки и проходит повторную регистрацию.</small></article>
    <article class="phase-card"><b>3 · Launch Gate</b><span>${launchState}</span><small>Только после polished registration + Owner review.</small></article>
    <article class="phase-card"><b>Current phase</b><span>${phase}</span><small>Рабочий цикл: кандидат → отполированный пакет → запуск.</small></article>
  </div>`;
}

function renderMechanicusProofDigest(mech) {
  if (!mech) return `<div class="proof-digest empty">Register a pack to receive Mechanicus proof digest.</div>`;
  const zones = mech.dependency_impact?.zones || [];
  const touched = zones.filter((z) => z.touched).map((z) => z.zone);
  return `<div class="proof-digest">
    <div><b>Task class</b><span>${escapeHtml(mech.task_class || "unknown")}</span></div>
    <div><b>Launch</b><span>${escapeHtml(mech.real_execution || "BLOCKED")}</span></div>
    <div><b>Touched nodes</b><span>${escapeHtml(summarizeArray(touched, 4))}</span></div>
    <div><b>Cascade rule</b><span>${escapeHtml(mech.dependency_impact?.cascade_rule || "nodes must be revalidated")}</span></div>
  </div>`;
}


function proofStateLabel(value, fallback = "WAITING") {
  const text = String(value || fallback);
  if (text.includes("PASS") || text.includes("REGISTERABLE")) return { text, tone: "pass" };
  if (text.includes("DEBT") || text.includes("REQUIRED") || text.includes("BLOCKED")) return { text, tone: "warn" };
  if (text.includes("FAIL") || text.includes("DIRTY")) return { text, tone: "fail" };
  return { text, tone: "idle" };
}

function renderDailyProofLedger(astro, mech) {
  const rows = [
    ["Astronomicon", astro?.verdict, "pack shape + intake phase"],
    ["Mechanicus", mech?.verdict, mech?.task_class || "machine class pending"],
    ["Monolith", mech?.monolith_risk, "node split / cascade risk"],
    ["Visual", mech?.visual_stack?.required ? "VISUAL_STACK_REQUIRED" : "not required", "FPS + reference proof when UI is touched"],
    ["Launch", mech?.real_execution || "BLOCKED_BY_POLICY", "candidate cannot run; polished requires Owner review"],
  ];
  return `<div class="daily-proof-ledger" data-marker="${COMPACT_PROOF_DIGEST}">
    ${rows.map(([label, value, note]) => {
      const state = proofStateLabel(value);
      return `<article class="proof-row ${state.tone}"><b>${escapeHtml(label)}</b><span>${escapeHtml(state.text)}</span><small>${escapeHtml(note)}</small></article>`;
    }).join("")}
  </div>`;
}

function renderNodeBoundaryMap(mech) {
  const zones = mech?.dependency_impact?.zones || [];
  const fallback = [
    { zone: "main.js", impact: "room state / events / registration digest", touched: false },
    { zone: "styles.css", impact: "surface tokens / layout density", touched: false },
    { zone: "src-tauri/main.rs", impact: "backend command bridge", touched: false },
    { zone: "receipts", impact: "truth evidence storage", touched: false },
  ];
  const normalized = (zones.length ? zones : fallback).slice(0, 6).map((z) => ({
    zone: z.zone || z.node || "unknown node",
    impact: z.impact || z.reason || "revalidate dependent nodes only",
    touched: Boolean(z.touched),
  }));
  return `<div class="node-boundary-map" data-marker="MECHANICUS_NODE_BOUNDARY_MAP_V0_1">
    <p class="eyebrow">MECHANICUS NODE BOUNDARIES</p>
    <div class="node-grid">
      ${normalized.map((z) => `<article class="node-card ${z.touched ? "hot" : "quiet"}"><b>${escapeHtml(z.zone)}</b><span>${escapeHtml(z.impact)}</span></article>`).join("")}
    </div>
  </div>`;
}

function renderAstronomicon() {
  // Registration and launch buttons intentionally remain in-app, but daily workflow uses terminal until UI form is mature.

  const astro = organSummary?.astronomicon;
  const mech = organSummary?.mechanicus;
  const languages = mech?.languages || [];
  const missing = mech?.missing_capabilities || [];
  const validators = mech?.required_validators || [];
  const visiblePatches = visiblePatchPacks();
  const selectedPatch = patchPacks.find((p) => p.patch_id === selectedPatchId);
  return `<section class="room-panel astronomicon-intake-panel" data-marker="ASTRONOMICON_ROOM" data-picker-marker="${ASTRONOMICON_PATCH_PICKER_DARK_LIST_V0_1}">
    <p class="eyebrow">ASTRONOMICON / PATCH PACK INTAKE</p>
    <h2>Astronomicon Registration</h2>
    <p class="muted">Astronomicon owns registration and launch gates. Mechanicus returns stack, node/monolith risk, visual debt and dependency impact. Candidate packs cannot run.</p>
    <div class="patch-picker-box">
      <div class="patch-picker-head">
        <input id="patch-search" value="${escapeHtml(patchSearch)}" placeholder="Поиск pack id: app, eyes, mechanicus, throne..." aria-label="Patch pack search" />
        <button id="refresh-patches">Refresh</button>
        <button id="register-patch">Register via Astronomicon → Mechanicus</button>
        <button id="run-patch" class="danger-soft">Launch polished only</button>
      </div>
      <div class="patch-selected-card">
        <span class="eyebrow">SELECTED PATCH PACK</span>
        <b>${escapeHtml(selectedPatchId || "none")}</b>
        <small>${escapeHtml(selectedPatch ? patchPickLabel(selectedPatch) : "not in current visible registry")}</small>
      </div>
      <div class="patch-list" role="listbox" aria-label="Patch pack list">
        ${(visiblePatches.length ? visiblePatches : [{ patch_id: "NO_PATCHES_MATCH_FILTER", status: "EMPTY" }]).map((p) => `
          <button class="patch-pick ${selectedPatchId === p.patch_id ? "selected" : ""}" data-patch-id="${escapeHtml(p.patch_id)}" type="button">
            <span>${escapeHtml(p.patch_id)}</span>
            <small>${escapeHtml(patchPickLabel(p))}</small>
          </button>
        `).join("")}
      </div>
      <div class="trial-task-box compact-trial">
        <p class="eyebrow">NEXT HARD TRIAL CANDIDATE — WARP candidate pack after this patch</p>
        <h3>${trialMission.task_id}</h3>
        <p>${trialMission.goal}</p>
      </div>
    </div>
    <div class="status-strip">
      <span>Selected: <b>${selectedPatchId || "none"}</b></span>
      <span>Registered: <b>${registeredPatchId || "none"}</b></span>
      <span>Summary: <b>${organSummaryStatus}</b></span>
    </div>
    ${renderTwoPhaseWorkflow(organSummary)}
    <div class="daily-use-proof-stack" data-marker="${DAILY_USE_UI_REFIT_POLISHED}">
      ${renderMechanicusProofDigest(mech)}
      ${renderDailyProofLedger(astro, mech)}
      ${renderNodeBoundaryMap(mech)}
    </div>
    <div class="organ-verdict-grid compact-verdict-grid">
      <article class="verdict-card astro-card">
        <p class="eyebrow">ASTRONOMICON</p>
        <h3>${astro?.verdict || "WAITING_FOR_REGISTRATION"}</h3>
        <p>Shape: ${astro?.checks ? `files=${astro.checks.land_file_count}, runner=${astro.checks.runner_exists}, manifest=${astro.checks.manifest_exists}` : "not checked"}</p>
      </article>
      <article class="verdict-card mech-card">
        <p class="eyebrow">MECHANICUS</p>
        <h3>${mech?.verdict || "WAITING_FOR_ASTRONOMICON"}</h3>
        <p>Class: <b>${mech?.task_class || "not classified"}</b></p>
      </article>
    </div>
    <div class="mechanicus-summary-grid compact-mechanicus-grid">
      <div class="mini-panel"><b>Languages</b><span>${summarizeArray(languages)}</span></div>
      <div class="mini-panel"><b>Validators</b><span>${summarizeArray(validators, 5)}</span></div>
      <div class="mini-panel"><b>Monolith risk</b><span>${mech?.monolith_risk || "not checked"}</span></div>
      <div class="mini-panel"><b>Visual stack</b><span>${mech?.visual_stack?.required ? summarizeArray(mech.visual_stack.stack, 5) : "not required"}</span></div>
      <div class="mini-panel wide"><b>Missing / Debt</b><span>${summarizeArray(missing, 8)}</span></div>
    </div>
  </section>`;
}

function renderMechanicus() {
  const powers = languagePowers.length ? languagePowers : fallbackLanguagePowers;
  return `<section class="room-panel" data-marker="${MECHANICUS_ROOM}">
    <p class="eyebrow">MECHANICUS / ${LANGUAGE_POWER_CODEX}</p>
    <h2>Language Power Codex</h2>
    <p class="muted">Python binds orchestration. Mechanicus chooses the minimal sufficient language for the task, proves the toolchain, and refuses prestige-driven language selection.</p>
    <div class="control-row"><button id="load-languages">Load language powers</button></div>
    <div class="law-box"><strong>Machine Law:</strong><span>A language is available only after Mechanicus proves its toolchain. Compilation proof belongs to the language; Python records and orchestrates.</span></div>
    ${organSummary?.mechanicus ? `<div class="mechanicus-live-verdict"><p class="eyebrow">LAST PATCH VERDICT</p><h3>${organSummary.mechanicus.verdict}</h3><p>${organSummary.mechanicus.task_class} · ${organSummary.mechanicus.monolith_risk}</p><small>${summarizeArray(organSummary.mechanicus.missing_capabilities || [], 8)}</small></div>` : ""}
    <div class="table-wrap">
      <table>
        <thead><tr><th>Language</th><th>Role</th><th>Use when</th><th>Proof</th><th>Warning</th></tr></thead>
        <tbody>
          ${powers.map((p) => `<tr><td><b>${p.language}</b></td><td>${p.role}</td><td>${p.use_when}</td><td><code>${p.proof}</code></td><td>${p.warning || ""}</td></tr>`).join("")}
        </tbody>
      </table>
    </div>
  </section>`;
}

function renderPlaceholderRoom(title, marker, body) {
  return `<section class="room-panel" data-marker="${marker}">
    <p class="eyebrow">${marker}</p>
    <h2>${title}</h2>
    <p class="muted">${body}</p>
    <div class="placeholder-sigil">✦</div>
  </section>`;
}

function renderActiveRoom() {
  if (activeRoom === "organ-hub") return renderOrganHub();
  if (activeRoom === "patch-forge") return renderAstronomicon();
  if (activeRoom === "mechanicus") return renderMechanicus();
  if (activeRoom === "astronomicon") return renderAstronomicon();
  if (activeRoom === "throne") return renderPlaceholderRoom("Throne", "THRONE_ROOM", "Special Crown organ. Blocks local success from becoming global fake readiness.");
  if (activeRoom === "eyes") return renderPlaceholderRoom("Eyes Room", "EYES_ROOM", "Frozen baseline v0.5.3.1 integration target. No new graph visual work claimed.");
  if (activeRoom === "seed-core") return renderPlaceholderRoom("Seed Core", "SEED_CORE_ROOM", "Future IDE-bound derivative runtime. Not claimed ready.");
  return renderOrganHub();
}

function renderCommandRail() {
  return `<aside class="command-rail" data-marker="${COMMAND_RAIL}">
    <div class="rail-section rail-level">
      <p class="eyebrow">COMMAND RAIL</p>
      <div class="level-emblem">♜</div>
      <h2>LEVEL 5</h2>
      <div class="rail-metric"><span>Proof XP</span><b>430</b></div>
      <div class="rail-metric"><span>Clean Streak</span><b>6</b></div>
      <div class="rail-metric"><span>Global assembled</span><b>0</b></div>
    </div>
    <div class="rail-section">
      <h3>Active Room</h3>
      <div class="rail-readout"><b>${activeRoomLabel()}</b><span>${activeRoom}</span></div>
    </div>
    <div class="rail-section">
      <h3>Patch State</h3>
      <div class="rail-readout"><b>${registeredPatchId || "none"}</b><span>${registeredPatchStatus}</span></div>
    </div>
    <div class="rail-section">
      <h3>Truth Boundary</h3>
      <ul>
        <li>UI renders truth</li>
        <li>Receipts prove truth</li>
        <li>UX proof is not execution proof</li>
      </ul>
    </div>
    <div class="rail-section rail-actions">
      <button data-quick="organ-hub">Hub</button>
      <button data-quick="astronomicon">Astro</button>
      <button data-quick="mechanicus">Mech</button>
    </div>
  </aside>`;
}

function renderAquarium() {
  return `<section class="aquarium" data-marker="${AQUARIUM}">
    <div class="aquarium-head">
      <div><p class="eyebrow">AQUARIUM</p><h2>Proof Digest</h2><small>last 14 lines · receipts hold full truth</small></div>
      <div class="control-row small">
        <button id="copy-aquarium">Copy log</button>
        <button id="clear-aquarium">Clear log</button>
        <button id="save-aquarium">Save log</button>
        <button id="open-logs">Open logs</button>
      </div>
    </div>
    <pre>${aquariumLines.slice(-14).join("\n")}</pre>
  </section>`;
}

function render() {
  const app = document.querySelector("#app");
  app.innerHTML = `
    <main class="app-shell" data-marker="${IMPERIUM_APP_PLATFORM}" data-ui-target="${IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3}">
      <header class="hero">
        <div class="imperial-crest" aria-hidden="true">♛</div>
        <div class="hero-copy">
          <p class="eyebrow">IMPERIUM CORE</p>
          <h1>Imperium Core</h1>
          <p>Versioned daily cockpit. Terminal patches stage new versions; the app renders current truth and update readiness.</p>
          ${renderCoreVersionStrip()}
        </div>
        <div class="hud">
          <span><i>◎</i><b>FPS</b><em id="fps-readout">${fpsDisplay}</em><small>/ target ${FPS_LOCK_TARGET}</small></span>
          <span><i>▣</i><b>Repo</b><em>E:\\IMPERIUM_REALITY</em></span>
          <span><i>✥</i><b>Marker</b><em>${IMPERIUM_TAURI_SHELL}</em></span>
          <span><i>✦</i><b>Deck</b><em>${COMMAND_DECK_V3}</em></span>
          <span><i>⬡</i><b>Core</b><em>${imperiumCoreVersion?.current_version || "unknown"}</em><small>${imperiumCoreVersion?.update_available ? "update ready" : "current"}</small></span>
        </div>
      </header>
      <div class="cabin-layout">
        ${renderRoomNav()}
        <div class="main-deck">${renderActiveRoom()}</div>
        ${renderCommandRail()}
        ${renderAquarium()}
      </div>
    </main>
  `;

  document.querySelectorAll("[data-room]").forEach((button) => {
    button.addEventListener("click", () => {
      activeRoom = button.getAttribute("data-room");
      markUx(`nav_${activeRoom}`);
    });
  });

  document.querySelectorAll("[data-quick]").forEach((button) => {
    button.addEventListener("click", () => {
      activeRoom = button.getAttribute("data-quick");
      markUx(`quick_${activeRoom}`);
    });
  });

  document.querySelector("#patch-search")?.addEventListener("input", (event) => {
    patchSearch = event.target.value;
    markUx("filter_patch_list");
    render();
  });
  document.querySelectorAll("[data-patch-id]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedPatchId = button.getAttribute("data-patch-id") || "";
      markUx("select_patch_from_dark_list");
      render();
    });
  });
  document.querySelector("#refresh-patches")?.addEventListener("click", refreshPatchPacks);
  document.querySelector("#register-patch")?.addEventListener("click", registerPatchPack);
  document.querySelector("#run-patch")?.addEventListener("click", runRegisteredPatchPack);
  document.querySelector("#goto-astronomicon")?.addEventListener("click", () => { activeRoom = "astronomicon"; markUx("goto_astronomicon_registration"); });
  document.querySelector("#load-languages")?.addEventListener("click", loadLanguagePowers);
  document.querySelector("#copy-aquarium")?.addEventListener("click", async () => {
    markUx("copy_aquarium_log");
    await navigator.clipboard.writeText(aquariumLines.join("\n"));
    logAquarium("COPY", "Aquarium copied to clipboard");
  });
  document.querySelector("#clear-aquarium")?.addEventListener("click", () => {
    uxActionCount += 1;
    aquariumLines = [`[${nowStamp()}][UX] ${UX_PROOF_MARKER} ${COMMAND_DECK_V3} action=clear_aquarium_log count=${uxActionCount}`];
    render();
  });
  document.querySelector("#save-aquarium")?.addEventListener("click", saveAquariumLog);
  document.querySelector("#open-logs")?.addEventListener("click", openLogs);
  document.querySelector("#imperium-core-update")?.addEventListener("click", initializeImperiumCoreUpdate);
}

async function recordRuntimeFpsProof(payload) {
  if (runtimeFpsProofSent) return;
  runtimeFpsProofSent = true;
  try {
    const result = await invoke("record_runtime_fps_proof", { payload });
    logAquarium("PASS", `RUNTIME_FPS_PROOF_RECEIPT: ${result?.receipt || JSON.stringify(result).slice(0, 250)}`);
    logAquarium("PASS", `RUNTIME_FPS_AVG: ${payload.average_fps.toFixed(2)} / target ${payload.target_fps}`);
  } catch (error) {
    logAquarium("WARN", `runtime fps proof command unavailable: ${String(error)}`);
  }
}

function startFpsWatchdog() {
  const tick = (timestamp) => {
    if (lastFrame > 0) {
      const delta = timestamp - lastFrame;
      frameDeltas.push(delta);
      if (frameDeltas.length > 240) frameDeltas.shift();

      const fps = 1000 / delta;
      fpsDisplay = fps.toFixed(1);
      const readout = document.querySelector("#fps-readout");
      if (readout) readout.textContent = fpsDisplay;

      const warmupFrames = 30;
      const minimumSampleCount = 180;
      if (!runtimeFpsProofSent && frameDeltas.length >= warmupFrames + minimumSampleCount) {
        const samples = frameDeltas.slice(warmupFrames, warmupFrames + minimumSampleCount);
        const fpsSamples = samples.map((ms) => 1000 / ms);
        const averageFps = fpsSamples.reduce((a, b) => a + b, 0) / fpsSamples.length;
        const minFps = Math.min(...fpsSamples);
        const maxFrameMs = Math.max(...samples);
        const slowFrames = samples.filter((ms) => ms > 24).length;
        recordRuntimeFpsProof({
          marker: RUNTIME_FPS_PROOF,
          target_fps: FPS_LOCK_TARGET,
          average_fps: averageFps,
          min_fps: minFps,
          max_frame_ms: maxFrameMs,
          sample_count: samples.length,
          slow_frame_count: slowFrames,
          slow_frame_ratio: slowFrames / samples.length,
          reduce_motion_mode: false,
          user_agent: navigator.userAgent,
          app_marker: IMPERIUM_APP_PLATFORM,
          ui_target_marker: IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3,
          generated_at: new Date().toISOString()
        });
      }
    }
    lastFrame = timestamp;
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

aquariumLines = [
  `[${nowStamp()}][AUTH] Imperium Core command deck awakened`,
  `[${nowStamp()}][STYLE] ${IMPERIUM_APP_UI_RIGHT_RAIL_COMMAND_DECK_V3}: right rail / gothic metal / cyber proof lines`,
  `[${nowStamp()}][LAW] UI renders truth; core receipts prove truth`,
  `[${nowStamp()}][LAW] ${NO_FAKE_EXECUTION_CLAIMED_MARKER}`,
  `[${nowStamp()}][UX] ${UX_PROOF_MARKER} ${COMMAND_DECK_V3} action=initial_render count=0`
];

render();
startFpsWatchdog();
refreshImperiumCoreVersion();
refreshPatchPacks();
