import { invoke } from "@tauri-apps/api/core";

// IMPERIUM_TAURI_SHELL
// Frontend identity marker required by Imperium Tauri foundation validator.
// RUNTIME_FPS_PROOF: this shell records local WebView FPS proof through the Rust bridge.
const IMPERIUM_TAURI_SHELL = "IMPERIUM_TAURI_SHELL";

const FPS_LOCK_TARGET = 60;
const FPS_SOFT_WARNING = 55;
const FPS_HARD_FAIL = 50;
const FRAME_BUDGET_MS = 16.67;
const RUNTIME_FPS_PROOF_MIN_SAMPLES = 180;
const RUNTIME_FPS_PROOF_WARMUP_FRAMES = 30;

const organs = [
  { id: "ASTRONOMICON", title: "ASTRONOMICON", subtitle: "CROWN-CONFIRMED 1/10", actions: ["status", "astronomicon-advice", "astronomicon-redblue", "astronomicon-hardening", "score-refresh-guidance"] },
  { id: "CUSTODES", title: "CUSTODES", subtitle: "Прокурорская проверка Астрономикона", actions: ["custodes-audit", "custodes-readout"] },
  { id: "THRONE", title: "THRONE", subtitle: "Crown order / anti-self-deception", actions: ["throne-crown-order", "throne-readout"] },
  { id: "PACK_FORGE", title: "PACK FORGE", subtitle: "Patch Pack / Task Pack request drafts", actions: ["register-patch-pack", "register-task-pack"] },
  { id: "EYES_ROOM", title: "EYES ROOM", subtitle: "Eyes 0.5.3.1 integration contract", actions: ["eyes-contract", "eyes-notes", "eyes-context-level", "eyes-screenshot-sweep"] },
  { id: "SEED_CORE", title: "SEED CORE", subtitle: "draft lineage / IDE-bound initialization contract", actions: ["seed-contract", "seed-status"] },
];

const actionLabels = {
  "status": "Статус Империума",
  "astronomicon-advice": "Астрономикон: органный совет",
  "astronomicon-redblue": "Астрономикон: Red/Blue статус",
  "astronomicon-hardening": "Астрономикон: hardening",
  "score-refresh-guidance": "Подсказка обновления цифр",
  "custodes-audit": "Кустодес: прокурорская проверка",
  "custodes-readout": "Кустодес: последний docket",
  "throne-crown-order": "Трон: Crown order",
  "throne-readout": "Трон: Crown verdict",
  "register-patch-pack": "Регистрация Patch Pack request",
  "register-task-pack": "Регистрация Task Pack request",
  "eyes-contract": "Eyes: показать contract",
  "eyes-notes": "Eyes: заметки зон",
  "eyes-context-level": "Eyes: уровни контекста",
  "eyes-screenshot-sweep": "Eyes: screenshot sweep plan",
  "seed-contract": "Seed Core: contract",
  "seed-status": "Seed Core: status"
};

let state = {};
let activeOrgan = organs[0];
let fpsSamples = [];
let frameDeltas = [];
let lastFrame = performance.now();
let reduceMotionMode = false;
let runtimeFpsProofSent = false;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function log(message, level = "info") {
  const box = document.querySelector("#aquarium-log");
  if (!box) return;
  const line = el("div", `log-line ${level}`);
  const now = new Date().toLocaleTimeString("ru-RU");
  line.textContent = `[${now}][${level.toUpperCase()}] ${message}`;
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
}

function setReduceMotion(on) {
  reduceMotionMode = on;
  document.body.classList.toggle("reduce-motion", on);
}

async function recordRuntimeFpsProof() {
  if (runtimeFpsProofSent) return;
  if (frameDeltas.length < RUNTIME_FPS_PROOF_MIN_SAMPLES + RUNTIME_FPS_PROOF_WARMUP_FRAMES) return;

  runtimeFpsProofSent = true;

  const measuredDeltas = frameDeltas.slice(RUNTIME_FPS_PROOF_WARMUP_FRAMES);
  const measuredFps = measuredDeltas.map((d) => 1000 / Math.max(d, 1));
  const averageFps = measuredFps.reduce((a, b) => a + b, 0) / measuredFps.length;
  const minFps = Math.min(...measuredFps);
  const maxFrameMs = Math.max(...measuredDeltas);
  const slowFrames = measuredDeltas.filter((d) => d > 24.0).length;
  const slowFrameRatio = slowFrames / measuredDeltas.length;

  const payload = {
    proof_id: "RUNTIME_FPS_PROOF",
    app_marker: IMPERIUM_TAURI_SHELL,
    target_fps: FPS_LOCK_TARGET,
    average_fps: averageFps,
    min_fps: minFps,
    max_frame_ms: maxFrameMs,
    sample_count: measuredDeltas.length,
    warmup_frames: RUNTIME_FPS_PROOF_WARMUP_FRAMES,
    slow_frame_ms: 24.0,
    slow_frame_count: slowFrames,
    slow_frame_ratio: slowFrameRatio,
    reduce_motion_mode: reduceMotionMode,
    user_agent: navigator.userAgent,
    generated_at_client_iso: new Date().toISOString()
  };

  try {
    const receipt = await invoke("record_runtime_fps_proof", { payload });
    log(`RUNTIME_FPS_PROOF_RECEIPT: ${receipt.receipt}`, receipt.fps_lock_proven ? "pass" : "error");
    log(`RUNTIME_FPS_AVG: ${averageFps.toFixed(2)} / target ${FPS_LOCK_TARGET}`, receipt.fps_lock_proven ? "pass" : "error");
  } catch (err) {
    log(`RUNTIME_FPS_PROOF_FAILED: ${err}`, "error");
  }
}

function startFpsWatchdog() {
  const chip = document.querySelector("#fps-chip");

  const tick = (now) => {
    const delta = now - lastFrame;
    lastFrame = now;
    const fps = 1000 / Math.max(delta, 1);
    fpsSamples.push(fps);
    frameDeltas.push(delta);
    if (fpsSamples.length > 180) fpsSamples.shift();
    if (frameDeltas.length > 360) frameDeltas.shift();

    const avg = fpsSamples.reduce((a, b) => a + b, 0) / fpsSamples.length;
    chip.textContent = `FPS ${avg.toFixed(1)} / target ${FPS_LOCK_TARGET}`;
    chip.classList.toggle("warn", avg < FPS_SOFT_WARNING && avg >= FPS_HARD_FAIL);
    chip.classList.toggle("fail", avg < FPS_HARD_FAIL);

    if (avg < FPS_SOFT_WARNING && fpsSamples.length >= 120) {
      setReduceMotion(true);
    }

    recordRuntimeFpsProof();
    requestAnimationFrame(tick);
  };

  requestAnimationFrame(tick);

  if ("PerformanceObserver" in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > FRAME_BUDGET_MS * 3) {
            log(`Long task detected: ${entry.duration.toFixed(1)}ms`, "error");
          }
        }
      });
      observer.observe({ entryTypes: ["longtask"] });
    } catch {
      // Some WebViews may not support longtask. FPS watchdog remains active.
    }
  }
}

function renderShell() {
  document.querySelector("#app").innerHTML = `
    <main class="imperium-shell">
      <header class="app-header">
        <div class="brand">IMPERIUM</div>
        <div class="level-hud">
          <div class="level-row">
            <strong id="level-label">LEVEL --</strong>
            <span id="xp-label">Proof XP: --</span>
            <span id="streak-label">Стрик: --</span>
          </div>
          <div class="xp-track"><div class="xp-fill" id="xp-fill"></div></div>
        </div>
        <div class="fps-chip" id="fps-chip">FPS -- / target ${FPS_LOCK_TARGET}</div>
      </header>
      <section class="main-layout">
        <aside class="panel organ-hub" data-room="ORGAN_HUB">
          <div class="panel-title">ORGAN_HUB</div>
          <div class="organ-list" id="organ-list"></div>
        </aside>
        <section class="panel room">
          <div class="room-head">
            <div>
              <div class="room-title" id="room-title">ASTRONOMICON</div>
              <div class="room-subtitle" id="room-subtitle">CROWN-CONFIRMED 1/10</div>
            </div>
            <div class="energy-river" aria-label="elemental energy flow"></div>
          </div>
          <div class="room-actions" id="room-actions"></div>
          <div class="room-body">
            <div class="telemetry-grid" id="telemetry"></div>
            <div class="telemetry-grid" id="room-panel"></div>
          </div>
        </section>
        <aside class="panel aquarium" data-stream="AQUARIUM_STREAM">
          <div class="panel-title">AQUARIUM</div>
          <div id="aquarium-log" class="log-box"></div>
          <div class="log-controls">
            <button class="action-btn" id="copy-log">Копировать</button>
            <button class="action-btn" id="clear-log">Очистить</button>
            <button class="action-btn" id="refresh-state">Обновить state</button>
          </div>
        </aside>
      </section>
    </main>
  `;

  document.querySelector("#copy-log").addEventListener("click", async () => {
    await navigator.clipboard.writeText(document.querySelector("#aquarium-log").innerText);
    log("Aquarium copied to clipboard.", "pass");
  });
  document.querySelector("#clear-log").addEventListener("click", () => {
    document.querySelector("#aquarium-log").innerHTML = "";
  });
  document.querySelector("#refresh-state").addEventListener("click", refreshImperiumState);

  renderOrgans();
  openOrgan("ASTRONOMICON");
}

function renderOrgans() {
  const list = document.querySelector("#organ-list");
  list.innerHTML = "";
  for (const organ of organs) {
    const card = el("div", "organ-card");
    card.dataset.organ = organ.id;
    card.innerHTML = `
      <div class="organ-id">${organ.title}</div>
      <div class="organ-state">${organ.subtitle}</div>
    `;
    card.addEventListener("click", () => openOrgan(organ.id));
    list.appendChild(card);
  }
}

function openOrgan(id) {
  activeOrgan = organs.find((x) => x.id === id) || organs[0];
  document.querySelectorAll(".organ-card").forEach((x) => x.classList.toggle("active", x.dataset.organ === activeOrgan.id));
  document.querySelector("#room-title").textContent = activeOrgan.title;
  document.querySelector("#room-subtitle").textContent = activeOrgan.subtitle;

  const actions = document.querySelector("#room-actions");
  actions.innerHTML = "";
  for (const actionId of activeOrgan.actions) {
    const btn = el("button", "action-btn", actionLabels[actionId] || actionId);
    btn.addEventListener("click", () => routeAction(actionId));
    actions.appendChild(btn);
  }

  renderTelemetry();
  renderRoomPanel();
  log(`Entered organ room: ${activeOrgan.id}`, "auth");
}

function metric(label, value) {
  const card = el("div", "metric-card");
  card.innerHTML = `<div class="metric-label">${label}</div><div class="metric-value">${value ?? "—"}</div>`;
  return card;
}

function renderTelemetry() {
  const grid = document.querySelector("#telemetry");
  grid.innerHTML = "";
  const c = state?.crown_aware_scores || {};
  grid.appendChild(metric("CROWN_AWARE_OVERLAY", state?.stage_integration_mode || "—"));
  grid.appendChild(metric("Red Team", c.red_team_score));
  grid.appendChild(metric("Blue Team", c.blue_team_score));
  grid.appendChild(metric("Custodes", c.custodes_organ_validators_score));
  grid.appendChild(metric("Throne", c.throne_organ_validators_score));
  grid.appendChild(metric("Assembled", c.organ_assembled_score ?? state?.current_scores?.organ_assembled_score));
}

function renderRoomPanel() {
  const panel = document.querySelector("#room-panel");
  panel.innerHTML = "";

  if (activeOrgan.id === "EYES_ROOM") {
    panel.appendChild(metric("EYES ROOM", "contract-only"));
    panel.appendChild(metric("Baseline", "v0.5.3.1"));
    panel.appendChild(metric("Notes", "planned"));
    panel.appendChild(metric("Context levels", "planned"));
    panel.appendChild(metric("Screenshot sweep", "planned"));
    return;
  }

  if (activeOrgan.id === "SEED_CORE") {
    panel.appendChild(metric("SEED_CORE", "draft contract"));
    panel.appendChild(metric("IDE binding", "future"));
    panel.appendChild(metric("Patch inheritance", "future"));
    panel.appendChild(metric("Function preservation", "future"));
    return;
  }

  if (activeOrgan.id === "PACK_FORGE") {
    panel.appendChild(metric("Patch Pack request", "available"));
    panel.appendChild(metric("Task Pack request", "available"));
    panel.appendChild(metric("Canonical registrar", "future"));
    return;
  }

  panel.appendChild(metric("Organ", activeOrgan.title));
  panel.appendChild(metric("Action count", activeOrgan.actions.length));
  panel.appendChild(metric("Aquarium", "visible"));
}

async function refreshImperiumState() {
  try {
    state = await invoke("read_imperium_state");
    renderTelemetry();
    renderRoomPanel();
    const xp = state?.proof_xp || 0;
    const level = Math.floor(xp / 100) + 1;
    document.querySelector("#level-label").textContent = `LEVEL ${level}`;
    document.querySelector("#xp-label").textContent = `Proof XP: ${xp}`;
    document.querySelector("#streak-label").textContent = `Стрик: ${state?.clean_streak ?? 0}`;
    document.querySelector("#xp-fill").style.width = `${xp % 100}%`;
    log("Imperium state refreshed.", "pass");
  } catch (err) {
    log(`State refresh failed: ${err}`, "error");
  }
}

async function routeAction(actionId) {
  if (actionId === "register-patch-pack") return createPackRequest("PATCH_PACK");
  if (actionId === "register-task-pack") return createPackRequest("TASK_PACK");
  if (actionId.startsWith("eyes-")) return openEyesRoom(actionId);
  if (actionId.startsWith("seed-")) return openSeedCore(actionId);
  return runImperiumAction(actionId);
}

async function runImperiumAction(actionId) {
  log(`RUN_ACTION: ${actionId}`, "auth");
  try {
    const result = await invoke("run_imperium_action", { actionId });
    log(result.stdout || "(no stdout)", result.exit_code === 0 ? "pass" : "error");
    if (result.stderr) log(result.stderr, "error");
    log(`ACTION_EXIT_CODE: ${result.exit_code}`, result.exit_code === 0 ? "pass" : "error");
    await refreshImperiumState();
  } catch (err) {
    log(`ACTION_FAILED: ${err}`, "error");
  }
}

async function createPackRequest(kind) {
  const packId = prompt(`${kind}: Pack ID`);
  if (!packId) return;
  const title = prompt(`${kind}: Название`, packId) || packId;
  try {
    const result = await invoke("create_pack_request", { kind, packId, title, targetOrgan: "ASTRONOMICON" });
    log(`PACK_REQUEST_CREATED: ${result.request}`, "pass");
    log(`PACK_REQUEST_RECEIPT: ${result.receipt}`, "pass");
  } catch (err) {
    log(`PACK_REQUEST_FAILED: ${err}`, "error");
  }
}

async function openEyesRoom(actionId) {
  log(`EYES_ROOM action: ${actionId}`, "auth");
  try {
    const contract = await invoke("read_eyes_contract");
    log(JSON.stringify(contract, null, 2), "auth");
  } catch (err) {
    log(`EYES_ROOM contract read failed: ${err}`, "error");
  }
}

async function openSeedCore(actionId) {
  log(`SEED_CORE action: ${actionId}`, "auth");
  try {
    const contract = await invoke("read_seed_core_contract");
    log(JSON.stringify(contract, null, 2), "auth");
  } catch (err) {
    log(`SEED_CORE contract read failed: ${err}`, "error");
  }
}

renderShell();
log(`Shell marker: ${IMPERIUM_TAURI_SHELL}`, "auth");
startFpsWatchdog();
refreshImperiumState();
