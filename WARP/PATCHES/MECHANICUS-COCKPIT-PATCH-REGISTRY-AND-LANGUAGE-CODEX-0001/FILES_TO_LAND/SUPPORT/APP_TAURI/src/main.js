// IMPERIUM_TAURI_COCKPIT_PATCH_REGISTRY_UI
// IMPERIUM_TAURI_MECHANICUS_LANGUAGE_CODEX_UI
import { invoke } from "@tauri-apps/api/core";
import "./styles.css";

const IMPERIUM_TAURI_SHELL = "IMPERIUM_TAURI_SHELL";
const FPS_LOCK_TARGET = 60;
let runtimeFpsProofSent = false;
let frameDeltas = [];
let lastFrame = performance.now();
let patchPacks = [];

function el(id) { return document.getElementById(id); }
function now() { return new Date().toLocaleTimeString(); }
function log(line, kind = "INFO") {
  const aquarium = el("aquarium");
  if (!aquarium) return;
  aquarium.textContent += `[${now()}][${kind}] ${line}\n`;
  aquarium.scrollTop = aquarium.scrollHeight;
}

function selectedPatchId() {
  const sel = el("patchSelect");
  return sel && sel.value ? sel.value : null;
}

function renderPatchPacks(items) {
  patchPacks = items || [];
  const select = el("patchSelect");
  const table = el("patchTable");
  if (!select || !table) return;
  select.innerHTML = "";
  for (const p of patchPacks) {
    const option = document.createElement("option");
    option.value = p.patch_id;
    option.textContent = `${p.registered ? "✓" : "·"} ${p.patch_id}`;
    select.appendChild(option);
  }
  table.innerHTML = patchPacks.slice(0, 20).map(p => `
    <tr>
      <td>${p.registered ? "REGISTERED" : "DISCOVERED"}</td>
      <td>${p.patch_id}</td>
      <td>${p.has_runner ? "RUNNER" : "NO RUNNER"}</td>
    </tr>`).join("");
}

async function refreshPatchPacks() {
  log("Refreshing WARP/PATCHES registry...", "ACTION");
  const result = await invoke("list_patch_packs");
  renderPatchPacks(result.patch_packs || []);
  el("repoRoot").textContent = result.repo_root || "unknown";
  log(`Patch packs visible: ${(result.patch_packs || []).length}`, "PASS");
}

async function registerSelectedPatchPack() {
  const id = selectedPatchId();
  if (!id) { log("No patch selected", "WARN"); return; }
  log(`Registering patch pack: ${id}`, "ACTION");
  const result = await invoke("register_patch_pack", { patchId: id });
  log(`${result.verdict}: ${result.patch_id}`, result.verdict.startsWith("PASS") ? "PASS" : "FAIL");
  await refreshPatchPacks();
}

async function runSelectedPatchPack() {
  const id = selectedPatchId();
  if (!id) { log("No patch selected", "WARN"); return; }
  if (!confirm(`Run registered patch pack from cockpit?\n\n${id}\n\nThis executes its RUN_*.ps1 through pwsh.`)) {
    log(`Run cancelled by Owner: ${id}`, "WARN");
    return;
  }
  el("runPatchBtn").disabled = true;
  log(`Running registered patch pack: ${id}`, "ACTION");
  try {
    const result = await invoke("run_registered_patch_pack", { patchId: id });
    log(`${result.verdict}: exit ${result.exit_code}`, result.verdict.startsWith("PASS") ? "PASS" : "FAIL");
    log(`Receipt: ${result.receipt}`, "RECEIPT");
  } catch (err) {
    log(`Patch run failed: ${err}`, "FAIL");
  } finally {
    el("runPatchBtn").disabled = false;
  }
}

async function loadLanguageCodex() {
  log("Loading Mechanicus language power codex...", "ACTION");
  const matrix = await invoke("get_mechanicus_language_codex");
  const table = el("languageTable");
  table.innerHTML = (matrix.languages || []).map(lang => `
    <tr>
      <td>${lang.language}</td>
      <td>${lang.primary_role}</td>
      <td>${lang.use_when.join("; ")}</td>
      <td>${lang.proof_commands.join(" | ")}</td>
    </tr>`).join("");
  log(`Language codex loaded: ${(matrix.languages || []).length} powers`, "PASS");
}

function setupUi() {
  document.body.innerHTML = `
    <main class="shell">
      <section class="hero card">
        <div>
          <div class="eyebrow">IMPERIUM TAURI SHELL</div>
          <h1>Operational Cockpit</h1>
          <p>Patch Pack registry, controlled WARP runner and Mechanicus language power codex.</p>
        </div>
        <div class="statusBox">
          <div>FPS <span id="fpsValue">0</span> / target 60</div>
          <div>Repo <span id="repoRoot">unknown</span></div>
          <div>Marker ${IMPERIUM_TAURI_SHELL}</div>
        </div>
      </section>

      <section class="grid">
        <section class="card panel">
          <h2>Patch Pack Registry</h2>
          <p class="muted">Register WARP patch packs and run registered RUN_*.ps1 from the cockpit.</p>
          <div class="row">
            <select id="patchSelect"></select>
          </div>
          <div class="buttonRow">
            <button id="refreshPatchesBtn">Refresh</button>
            <button id="registerPatchBtn">Register</button>
            <button id="runPatchBtn" class="danger">Run registered</button>
          </div>
          <table>
            <thead><tr><th>Status</th><th>Patch</th><th>Runner</th></tr></thead>
            <tbody id="patchTable"></tbody>
          </table>
        </section>

        <section class="card panel">
          <h2>Mechanicus Language Codex</h2>
          <p class="muted">Python binds, Rust judges, Go ships, C++ descends only when optimization demands it.</p>
          <div class="buttonRow"><button id="loadLanguagesBtn">Load language powers</button></div>
          <table>
            <thead><tr><th>Language</th><th>Role</th><th>Use when</th><th>Proof</th></tr></thead>
            <tbody id="languageTable"></tbody>
          </table>
        </section>
      </section>

      <section class="card panel">
        <h2>Aquarium</h2>
        <pre id="aquarium"></pre>
        <div class="buttonRow">
          <button id="copyLogBtn">Copy</button>
          <button id="clearLogBtn">Clear</button>
        </div>
      </section>
    </main>
  `;

  el("refreshPatchesBtn").addEventListener("click", () => refreshPatchPacks().catch(e => log(String(e), "FAIL")));
  el("registerPatchBtn").addEventListener("click", () => registerSelectedPatchPack().catch(e => log(String(e), "FAIL")));
  el("runPatchBtn").addEventListener("click", () => runSelectedPatchPack());
  el("loadLanguagesBtn").addEventListener("click", () => loadLanguageCodex().catch(e => log(String(e), "FAIL")));
  el("copyLogBtn").addEventListener("click", () => navigator.clipboard.writeText(el("aquarium").textContent || ""));
  el("clearLogBtn").addEventListener("click", () => { el("aquarium").textContent = ""; });
  log("Cockpit loaded. Refresh patch packs to begin.", "AUTH");
}

function fpsLoop(ts) {
  const delta = ts - lastFrame;
  lastFrame = ts;
  if (delta > 0 && delta < 1000) {
    frameDeltas.push(delta);
    if (frameDeltas.length > 240) frameDeltas.shift();
    const fps = 1000 / delta;
    if (el("fpsValue")) el("fpsValue").textContent = fps.toFixed(1);
  }
  maybeRecordRuntimeFpsProof();
  requestAnimationFrame(fpsLoop);
}

async function maybeRecordRuntimeFpsProof() {
  if (runtimeFpsProofSent || frameDeltas.length < 210) return;
  const samples = frameDeltas.slice(30);
  const fpsValues = samples.map(ms => 1000 / ms);
  const average = fpsValues.reduce((a,b) => a+b, 0) / fpsValues.length;
  const slow = samples.filter(ms => ms > 24).length;
  const payload = {
    proof_type: "RUNTIME_FPS_PROOF",
    target_fps: FPS_LOCK_TARGET,
    average_fps: average,
    min_fps: Math.min(...fpsValues),
    max_frame_ms: Math.max(...samples),
    sample_count: samples.length,
    slow_frame_count: slow,
    slow_frame_ratio: slow / samples.length,
    reduce_motion_mode: false,
    user_agent: navigator.userAgent
  };
  runtimeFpsProofSent = true;
  try {
    const result = await invoke("record_runtime_fps_proof", { payload });
    log(`RUNTIME_FPS_PROOF_RECEIPT: ${result.receipt}`, "PASS");
    log(`RUNTIME_FPS_AVG: ${average.toFixed(2)} / target ${FPS_LOCK_TARGET}`, "PASS");
  } catch (err) {
    log(`RUNTIME_FPS_PROOF_FAILED: ${err}`, "FAIL");
  }
}

setupUi();
refreshPatchPacks().catch(e => log(String(e), "FAIL"));
requestAnimationFrame(fpsLoop);
