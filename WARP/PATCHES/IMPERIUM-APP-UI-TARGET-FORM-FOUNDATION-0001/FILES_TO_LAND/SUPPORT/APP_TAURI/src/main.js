import { invoke } from "@tauri-apps/api/core";
import "./styles.css";

const IMPERIUM_TAURI_SHELL = "IMPERIUM_TAURI_SHELL";
const IMPERIUM_APP_PLATFORM = "IMPERIUM_APP_PLATFORM";
const IMPERIUM_APP_UI_TARGET_FORM = "IMPERIUM_APP_UI_TARGET_FORM";
const UI_TARGET_FORM_FOUNDATION = "UI_TARGET_FORM_FOUNDATION";
const ORGAN_HUB_ROOM = "ORGAN_HUB_ROOM";
const PATCH_FORGE_ROOM = "PATCH_FORGE_ROOM";
const MECHANICUS_ROOM = "MECHANICUS_ROOM";
const PATCH_REGISTRY = "PATCH_REGISTRY";
const LANGUAGE_POWER_CODEX = "LANGUAGE_POWER_CODEX";
const AQUARIUM = "AQUARIUM";
const APP_COCKPIT_MERGED_INTO_PLATFORM = "APP_COCKPIT_MERGED_INTO_PLATFORM";
const FPS_LOCK_TARGET = 60;
const RUNTIME_FPS_PROOF = "RUNTIME_FPS_PROOF";
const UX_PROOF_MARKER = "UX_PROOF_MARKER";

let activeRoom = "organ-hub";
let patchPacks = [];
let selectedPatchId = "";
let registeredPatchId = "";
let registeredPatchStatus = "none";
let languagePowers = [];
let aquariumLines = [];
let runtimeFpsProofSent = false;
let frameDeltas = [];
let lastFrame = 0;
let uxActionCount = 0;

const roomList = [
  { id: "organ-hub", label: "Organ Hub", marker: ORGAN_HUB_ROOM, icon: "✦" },
  { id: "patch-forge", label: "Patch Forge", marker: PATCH_FORGE_ROOM, icon: "⚙" },
  { id: "mechanicus", label: "Mechanicus", marker: MECHANICUS_ROOM, icon: "⌬" },
  { id: "astronomicon", label: "Astronomicon", marker: "ASTRONOMICON_ROOM", icon: "✶" },
  { id: "throne", label: "Throne", marker: "THRONE_ROOM", icon: "♛" },
  { id: "eyes", label: "Eyes Room", marker: "EYES_ROOM", icon: "◉" },
  { id: "seed-core", label: "Seed Core", marker: "SEED_CORE_ROOM", icon: "◇" },
];

const knownOrgans = [
  { id: "ASTRONOMICON", title: "Astronomicon", status: "reference implementation", gate: "local crown-aware", note: "intake, patch form, readouts, advisory direction", icon: "✶" },
  { id: "MECHANICUS", title: "Mechanicus", status: "next primary organ", gate: "Gate 1–2 forming", note: "machine reality, toolchains, build/runtime proof", icon: "⌬" },
  { id: "DOCTRINARIUM", title: "Doctrinarium", status: "support law organ", gate: "six-gate canon landed", note: "laws, schemas, operator school", icon: "⚖" },
  { id: "CUSTODES", title: "Custodes", status: "prosecutor", gate: "universal matrix received", note: "external accusation and anti-self-trust", icon: "♜" },
  { id: "THRONE", title: "Throne", status: "special Crown organ", gate: "crown-gate laws received", note: "local success cannot become global fake readiness", icon: "♛" },
  { id: "ADMINISTRATUM", title: "Administratum", status: "deferred to last", gate: "Owner intent fixed", note: "registrar/ledger after organs self-report", icon: "▣" },
];

const fallbackLanguagePowers = [
  {
    language: "Python",
    role: "orchestration, receipts, scans, JSON, quick validators",
    use_when: "glue scripts, WARP helpers, file scans, reports, small validators",
    proof: "python --version; python -m py_compile <file.py>",
    warning: "Python binds orchestration; it does not replace compile proof"
  },
  {
    language: "Rust",
    role: "strict validators, Tauri backend, safety gates, compiled proof",
    use_when: "trust-critical validators, parsers, state machines, app backend",
    proof: "rustc --version; cargo --version; cargo check; cargo test",
    warning: "stronger proof, slower iteration"
  },
  {
    language: "Go",
    role: "small portable CLI, workers, network utilities",
    use_when: "external tools, fast binaries, simple services, portable customer utilities",
    proof: "go version; go test ./...; go build ./...",
    warning: "excellent practical force, less strict than Rust"
  },
  {
    language: "C++",
    role: "deep optimization and native hot paths",
    use_when: "only after profiling proves Rust/Go/TS/Python insufficient",
    proof: "cl or g++; cmake --version; cmake --build <build_dir>",
    warning: "chosen by measured necessity, never prestige"
  },
  {
    language: "TypeScript",
    role: "Tauri frontend, cockpit rooms, visual operator surfaces",
    use_when: "UI, panels, room navigation, graph/app surfaces",
    proof: "node --version; npm --version; npm run build",
    warning: "visual layer renders truth; it cannot prove truth"
  },
  {
    language: "PowerShell",
    role: "Windows host runners and operator workflows",
    use_when: "WARP runners, Windows command sequencing, git/build wrappers",
    proof: "pwsh --version; script exits 0; receipt exists",
    warning: "Windows operator lane with path/quoting discipline"
  },
];

function nowStamp() {
  return new Date().toLocaleTimeString();
}

function markUx(actionName) {
  uxActionCount += 1;
  logAquarium("UX", `${UX_PROOF_MARKER} action=${actionName} count=${uxActionCount}`);
}

function logAquarium(kind, message) {
  const line = `[${nowStamp()}][${kind}] ${message}`;
  aquariumLines = [...aquariumLines.slice(-110), line];
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
  logAquarium("WARN", `No backend command matched: ${names.join(", ")} :: ${String(lastError || "")}`);
  return { ok: false, error: String(lastError || "command not available") };
}

function normalizePatches(result) {
  const raw = Array.isArray(result) ? result :
    Array.isArray(result?.patches) ? result.patches :
    Array.isArray(result?.items) ? result.items :
    Array.isArray(result?.patch_packs) ? result.patch_packs : [];

  return raw.map((item) => {
    if (typeof item === "string") {
      return { patch_id: item, status: "DISCOVERED", runner: "" };
    }
    return {
      patch_id: item.patch_id || item.id || item.name || item.title || "UNKNOWN_PATCH",
      status: item.status || item.state || "DISCOVERED",
      runner: item.runner || item.runner_path || item.run_script || item.has_runner ? "RUNNER" : "",
      path: item.path || item.patch_path || "",
    };
  }).filter((x) => x.patch_id && x.patch_id !== "UNKNOWN_PATCH");
}

async function refreshPatchPacks() {
  markUx("refresh_patch_packs");
  const response = await callAnyCommand([
    "discover_patch_packs",
    "list_patch_packs",
    "get_patch_packs",
    "refresh_patch_registry",
    "list_warp_patch_packs"
  ]);
  if (response.ok) {
    patchPacks = normalizePatches(response.result);
    selectedPatchId = selectedPatchId || patchPacks[0]?.patch_id || "";
    logAquarium("PATCH", `Patch packs visible: ${patchPacks.length}`);
  } else if (patchPacks.length === 0) {
    patchPacks = [
      { patch_id: "PATCH_REGISTRY_BACKEND_PENDING", status: "LOCAL_PLACEHOLDER", runner: "—" }
    ];
    selectedPatchId = patchPacks[0].patch_id;
    logAquarium("PATCH", "Backend patch discovery unavailable; showing placeholder state");
  }
  render();
}

async function registerPatchPack() {
  markUx("register_patch_pack");
  if (!selectedPatchId || selectedPatchId === "PATCH_REGISTRY_BACKEND_PENDING") {
    logAquarium("BLOCKED", "No real patch selected for registration");
    return;
  }
  const response = await callAnyCommand([
    "register_patch_pack",
    "register_warp_patch_pack",
    "register_patch"
  ], { patchId: selectedPatchId, patch_id: selectedPatchId });

  registeredPatchId = selectedPatchId;
  registeredPatchStatus = response.ok ? "backend_registered" : "local_registered_backend_pending";
  logAquarium("PATCH", `Registered patch pack: ${registeredPatchId} (${registeredPatchStatus})`);
  render();
}

async function runRegisteredPatchPack() {
  markUx("run_registered_patch_pack");
  if (!registeredPatchId) {
    logAquarium("BLOCKED", "Patch pack must be registered before run");
    return;
  }
  const response = await callAnyCommand([
    "run_registered_patch_pack",
    "run_registered_patch",
    "run_patch_pack",
    "run_warp_patch_pack"
  ], { patchId: registeredPatchId, patch_id: registeredPatchId });

  if (response.ok) {
    logAquarium("RUN", `Run requested for registered patch: ${registeredPatchId}`);
    if (response.result) logAquarium("RUN", JSON.stringify(response.result).slice(0, 900));
  } else {
    logAquarium("BLOCKED", `Backend runner unavailable for ${registeredPatchId}; no fake execution claimed`);
  }
  render();
}

async function loadLanguagePowers() {
  markUx("load_language_powers");
  const response = await callAnyCommand([
    "load_language_power_codex",
    "load_language_powers",
    "get_language_powers",
    "mechanicus_language_powers"
  ]);
  if (response.ok) {
    const raw = Array.isArray(response.result) ? response.result :
      Array.isArray(response.result?.languages) ? response.result.languages :
      Array.isArray(response.result?.powers) ? response.result.powers : [];
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
  const response = await callAnyCommand([
    "save_aquarium_log",
    "save_app_log",
    "write_app_log"
  ], { body, log: body, content: body });
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
  const response = await callAnyCommand([
    "open_logs",
    "open_app_logs",
    "open_log_folder"
  ]);
  if (!response.ok) {
    logAquarium("INFO", "Open logs backend command unavailable; use SUPPORT/APP_TAURI/logs or app receipts");
  }
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

function renderOrganHub() {
  return `<section class="room-panel organ-hub-panel" data-marker="${ORGAN_HUB_ROOM}">
    <div class="panel-title-row">
      <div>
        <p class="eyebrow">ORGAN HUB</p>
        <h2>Organ Hub</h2>
        <p class="muted">The application remains the main Imperium shell. Operational cockpit powers are rooms inside it, not a replacement.</p>
      </div>
      <div class="level-card">
        <div class="level-sigil">♜</div>
        <strong>LEVEL 5</strong>
        <span>Proof XP 430</span>
        <span>Clean Streak 6</span>
        <span>Global assembled 0</span>
      </div>
    </div>
    <div class="organ-grid">
      ${knownOrgans.map((organ) => `
        <article class="organ-card">
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
  return `<section class="room-panel" data-marker="${PATCH_FORGE_ROOM}">
    <p class="eyebrow">PATCH FORGE / ${PATCH_REGISTRY}</p>
    <h2>Patch Pack Registry</h2>
    <p class="muted">Register WARP patch packs and run registered RUN_*.ps1 through the existing Imperium app. No fake run claim without backend receipt.</p>

    <div class="control-row">
      <select id="patch-select" aria-label="Patch pack selection">
        ${(patchPacks.length ? patchPacks : [{ patch_id: "NO_PATCHES_LOADED", status: "EMPTY", runner: "" }]).map((p) => `
          <option value="${p.patch_id}" ${selectedPatchId === p.patch_id ? "selected" : ""}>${p.patch_id}</option>
        `).join("")}
      </select>
      <button id="refresh-patches">Refresh</button>
      <button id="register-patch">Register</button>
      <button class="danger-soft" id="run-patch">Run registered</button>
    </div>

    <div class="status-strip">
      <span>Selected: <b>${selectedPatchId || "none"}</b></span>
      <span>Registered: <b>${registeredPatchId || "none"}</b></span>
      <span>Status: <b>${registeredPatchStatus}</b></span>
    </div>

    <div class="table-wrap">
      <table>
        <thead><tr><th>Status</th><th>Patch</th><th>Runner</th></tr></thead>
        <tbody>
          ${patchPacks.map((p) => `
            <tr>
              <td>${p.status}</td>
              <td>${p.patch_id}</td>
              <td>${p.runner || "—"}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  </section>`;
}

function renderMechanicus() {
  const powers = languagePowers.length ? languagePowers : fallbackLanguagePowers;
  return `<section class="room-panel" data-marker="${MECHANICUS_ROOM}">
    <p class="eyebrow">MECHANICUS / ${LANGUAGE_POWER_CODEX}</p>
    <h2>Language Power Codex</h2>
    <p class="muted">Python binds orchestration. Mechanicus chooses the minimal sufficient language for the task, proves the toolchain, and refuses prestige-driven language selection.</p>
    <div class="control-row">
      <button id="load-languages">Load language powers</button>
    </div>
    <div class="law-box">
      <strong>Machine Law:</strong>
      <span>A language is available only after Mechanicus proves its toolchain. Compilation proof belongs to the language; Python records and orchestrates.</span>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Language</th><th>Role</th><th>Use when</th><th>Proof</th><th>Warning</th></tr></thead>
        <tbody>
          ${powers.map((p) => `
            <tr>
              <td><b>${p.language}</b></td>
              <td>${p.role}</td>
              <td>${p.use_when}</td>
              <td><code>${p.proof}</code></td>
              <td>${p.warning || ""}</td>
            </tr>
          `).join("")}
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
  if (activeRoom === "patch-forge") return renderPatchForge();
  if (activeRoom === "mechanicus") return renderMechanicus();
  if (activeRoom === "astronomicon") return renderPlaceholderRoom("Astronomicon", "ASTRONOMICON_ROOM", "Reference implementation: intake, patch forms, readouts and operator direction.");
  if (activeRoom === "throne") return renderPlaceholderRoom("Throne", "THRONE_ROOM", "Special Crown organ. Blocks local success from becoming global fake readiness.");
  if (activeRoom === "eyes") return renderPlaceholderRoom("Eyes Room", "EYES_ROOM", "Frozen baseline v0.5.3.1 integration target. No new graph visual work claimed.");
  if (activeRoom === "seed-core") return renderPlaceholderRoom("Seed Core", "SEED_CORE_ROOM", "Future IDE-bound derivative runtime. Not claimed ready.");
  return renderOrganHub();
}

function renderAquarium() {
  return `<section class="aquarium" data-marker="${AQUARIUM}">
    <div class="aquarium-head">
      <div>
        <p class="eyebrow">AQUARIUM</p>
        <h2>UX Proof Log</h2>
      </div>
      <div class="control-row small">
        <button id="copy-aquarium">Copy log</button>
        <button id="clear-aquarium">Clear log</button>
        <button id="save-aquarium">Save log</button>
        <button id="open-logs">Open logs</button>
      </div>
    </div>
    <pre>${aquariumLines.join("\n")}</pre>
  </section>`;
}

function render() {
  const app = document.querySelector("#app");
  app.innerHTML = `
    <main class="app-shell" data-marker="${IMPERIUM_APP_PLATFORM}" data-ui-target="${IMPERIUM_APP_UI_TARGET_FORM}">
      <header class="hero">
        <div class="imperial-crest" aria-hidden="true">♛</div>
        <div class="hero-copy">
          <p class="eyebrow">IMPERIUM TAURI SHELL</p>
          <h1>Imperium App Platform</h1>
          <p>Organ rooms, Patch Forge, Mechanicus powers, Aquarium and future game projection in one application.</p>
        </div>
        <div class="hud">
          <span><i>◎</i> FPS <b id="fps-readout">60</b> / target ${FPS_LOCK_TARGET}</span>
          <span><i>▣</i> Repo E:\\IMPERIUM_REALITY</span>
          <span><i>✥</i> Marker ${IMPERIUM_TAURI_SHELL}</span>
          <span><i>✦</i> App ${APP_COCKPIT_MERGED_INTO_PLATFORM}</span>
        </div>
      </header>

      <div class="layout">
        ${renderRoomNav()}
        <div class="room-stack">
          ${renderActiveRoom()}
          ${renderAquarium()}
        </div>
      </div>
    </main>
  `;

  document.querySelectorAll("[data-room]").forEach((button) => {
    button.addEventListener("click", () => {
      activeRoom = button.getAttribute("data-room");
      markUx(`nav_${activeRoom}`);
    });
  });

  document.querySelector("#patch-select")?.addEventListener("change", (event) => {
    selectedPatchId = event.target.value;
    markUx("select_patch");
  });
  document.querySelector("#refresh-patches")?.addEventListener("click", refreshPatchPacks);
  document.querySelector("#register-patch")?.addEventListener("click", registerPatchPack);
  document.querySelector("#run-patch")?.addEventListener("click", runRegisteredPatchPack);
  document.querySelector("#load-languages")?.addEventListener("click", loadLanguagePowers);
  document.querySelector("#copy-aquarium")?.addEventListener("click", async () => {
    markUx("copy_aquarium_log");
    await navigator.clipboard.writeText(aquariumLines.join("\n"));
    logAquarium("COPY", "Aquarium copied to clipboard");
  });
  document.querySelector("#clear-aquarium")?.addEventListener("click", () => {
    uxActionCount += 1;
    aquariumLines = [`[${nowStamp()}][UX] ${UX_PROOF_MARKER} action=clear_aquarium_log count=${uxActionCount}`];
    render();
  });
  document.querySelector("#save-aquarium")?.addEventListener("click", saveAquariumLog);
  document.querySelector("#open-logs")?.addEventListener("click", openLogs);
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
      const readout = document.querySelector("#fps-readout");
      if (readout) readout.textContent = fps.toFixed(1);

      const warmupFrames = 30;
      const minimumSampleCount = 180;
      if (!runtimeFpsProofSent && frameDeltas.length >= warmupFrames + minimumSampleCount) {
        const samples = frameDeltas.slice(warmupFrames, warmupFrames + minimumSampleCount);
        const fpsSamples = samples.map((ms) => 1000 / ms);
        const averageFps = fpsSamples.reduce((a, b) => a + b, 0) / fpsSamples.length;
        const minFps = Math.min(...fpsSamples);
        const maxFrameMs = Math.max(...samples);
        const slowFrames = samples.filter((ms) => ms > 24).length;
        const payload = {
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
          ui_target_marker: IMPERIUM_APP_UI_TARGET_FORM,
          generated_at: new Date().toISOString()
        };
        recordRuntimeFpsProof(payload);
      }
    }
    lastFrame = timestamp;
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

aquariumLines = [
  `[${nowStamp()}][AUTH] Imperium App Platform awakened`,
  `[${nowStamp()}][STYLE] ${IMPERIUM_APP_UI_TARGET_FORM}: gothic metal / cyber glow / trash-polka accents`,
  `[${nowStamp()}][LAW] UI renders truth; core receipts prove truth`,
  `[${nowStamp()}][UX] ${UX_PROOF_MARKER} action=initial_render count=0`
];

render();
startFpsWatchdog();
refreshPatchPacks();
