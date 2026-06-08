const VERSION = "0.8.1";
const SURFACE = "WEB_SANCTUM_STAGE_LOOP_POLISH_AND_COPY_CONTOUR_V0_8_1";
const STAGES = ["task_admitted", "work_started", "implementation", "validation", "report_bundle", "owner_review", "promotion_ready"];

let snapshot = null;
let quality = "Performance";
let bridgeMode = "probing";
let paletteOpen = false;
let jobs = [];
let currentJobId = null;
let currentJobRaw = null;
let currentJobTab = "summary";
let jobFilter = "all";

window.__SANCTUM_READY = false;
const $ = (id) => document.getElementById(id);

function setText(id, text) {
  const element = $(id);
  if (element) element.textContent = text ?? "";
}

function toast(message) {
  const element = $("toast");
  if (!element) return;
  element.textContent = message;
  element.classList.add("show");
  setTimeout(() => element.classList.remove("show"), 2600);
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const raw = await response.text();
  try {
    return JSON.parse(raw);
  } catch {
    return { status: response.ok ? "PASS" : "FAIL", raw };
  }
}

function stageStatus(stageId) {
  const stages = snapshot?.stage_ledger?.stages || [];
  return stages.find((item) => item.stage_id === stageId)?.status || "PENDING";
}

function renderStageRail() {
  const rail = $("stageRail");
  if (!rail) return;
  rail.innerHTML = "";
  STAGES.forEach((stageId) => {
    const status = stageStatus(stageId);
    const node = document.createElement("div");
    node.className = `stage-step ${status.toLowerCase()}`;
    node.innerHTML = `<span>${status}</span><b>${stageId.replaceAll("_", " ")}</b>`;
    rail.appendChild(node);
  });
}
function evidenceRequirements(stageId) {
  const gates = snapshot?.stage_ledger?.gate_requirements || {};
  return gates[stageId] || [];
}

function renderStageControl() {
  const ledger = snapshot?.stage_ledger || {};
  const current = ledger.current_stage || snapshot?.warp?.current_stage || "task_intake";
  setText("stageCurrent", current);
  const stages = ledger.stages || [];
  const row = stages.find((item) => item.stage_id === current) || {};
  setText("stageVerdict", row.status || "PENDING");
  const req = $("stageRequired");
  if (req) {
    const items = evidenceRequirements(current);
    req.innerHTML = (items.length ? items : ["stage marker or gate receipt required"]).map((item) => `<li>${item}</li>`).join("");
  }
  setText("stageGateVerdict", row.gate_verdict || row.status || "NOT_RUN");
  setText("stageBlockers", (row.blockers || []).join(" · ") || "no blockers recorded");
  const timeline = $("stageTimeline");
  if (timeline) {
    timeline.innerHTML = "";
    STAGES.forEach((stageId) => {
      const status = stageStatus(stageId);
      const evidence = (stages.find((item) => item.stage_id === stageId)?.evidence || []).length;
      const card = document.createElement("article");
      card.className = `stage-card ${status.toLowerCase()}`;
      card.innerHTML = `<span>${status}</span><b>${stageId.replaceAll("_", " ")}</b><small>${evidence} evidence marks</small>`;
      timeline.appendChild(card);
    });
  }
}

function renderPromotion(result) {
  if (!result) return;
  const preview = result.promotion_preview || result.preview || result;
  const route = preview.promotion_route || "UNKNOWN_ROUTE";
  setText("promotionCandidate", preview.status || result.status || "UNKNOWN");
  setText("promotionBlocked", preview.blocked ? "BLOCKED" : "not blocked by preview");
  setText("promotionRoute", route.replaceAll("_", " "));
  setText("promotionMessage", preview.suggested_commit_message || "IMPERIUM_H: promote accepted WARP stage loop");
  const warnings = (preview.warnings || []).join("\n") || "no route warnings";
  setText("promotionTrace", `${warnings}\n\n${JSON.stringify(preview, null, 2)}`);
}


function renderContour() {
  const contour = snapshot?.contour || {};
  const task = snapshot?.task || {};
  const warp = snapshot?.warp || {};
  const progress = warp.stage_progress || { done: 0, total: 6 };
  const currentStage = snapshot?.stage_ledger?.current_stage || warp.current_stage || "task_intake";

  setText("contour", `${contour.current_contour || "MAIN_OR_UNKNOWN"} · ${quality} · branch:${contour.branch || "unknown"} · head:${(contour.head || "unknown").slice(0, 10)}`);
  setText("stateText", snapshot?.status || "UNKNOWN");
  setText("contourText", contour.current_contour || "read-only surface");
  setText("taskText", task.id || "NO_ACTIVE_TASK");
  setText("warpText", warp.mode || "NO_WARP_SELECTED");
  setText("stageText", `${progress.done || 0} / ${progress.total || 6}`);
  setText("currentStageText", currentStage);
  setText("nextText", task.next_action || "Register taskpack, then start work");
  setText("jobText", jobs.length ? `${jobs[0].status} · ${jobs[0].action}` : "idle");
  setText("jobPill", `jobs: ${jobs.length}`);

  setText("warpModeSeal", warp.mode || "NO_WARP_SELECTED");
  setText("warpId", warp.warp_id || "none");
  setText("warpPath", warp.path || "none");
  setText("warpBase", warp.base_head || "unknown");
  setText("warpBranch", warp.branch || contour.branch || "unknown");
  setText("warpStrategy", warp.strategy || "unknown");
  setText("warpDirty", `${warp.dirty_status || "unknown"}${Number.isFinite(warp.dirty_count) ? ` (${warp.dirty_count})` : ""}`);
  setText("warpActiveTask", task.id || "NO_ACTIVE_TASK");
  setText("warpStage", currentStage);
  setText("warpRuntimePath", warp.runtime_path || snapshot?.runtime_paths?.run_dir || "not created");

  const operator = $("operatorText");
  if (operator) operator.textContent = JSON.stringify(snapshot, null, 2);
  const warpStatus = $("warpStatus");
  if (warpStatus) warpStatus.textContent = JSON.stringify({ warp, task, stage_ledger: snapshot?.stage_ledger, runtime_paths: snapshot?.runtime_paths }, null, 2);
  renderStageRail();
}

function renderFlow() {
  const labels = ["INTAKE", "TASKPACK", "ASTRA GATE", "WARP", "JOB", "WORK", "STAGE PASS", "VALIDATE", "REPORT", "OWNER"];
  const root = $("flowNodes");
  if (!root) return;
  root.innerHTML = "";
  const current = snapshot?.warp?.current_stage || "task_intake";
  const active = current === "work_started" ? 5 : current === "validation" ? 7 : current === "report_bundle" ? 8 : snapshot?.warp?.path ? 3 : 1;
  labels.forEach((label, index) => {
    const node = document.createElement("div");
    node.className = `node${index === active ? " active" : ""}`;
    node.innerHTML = `<div class="dot"></div><label>${label}</label>`;
    root.appendChild(node);
  });
}

function renderOrbit() {
  const root = $("orbit");
  if (!root) return;
  root.innerHTML = "";
  const names = ["MECHANICUS", "ASTRONOMICON", "ADMINISTRATUM", "INQUISITION", "STRATEGIUM", "OFFICIO", "FREELANCE", "TRADING"];
  const coords = [[65, 18], [75, 44], [66, 72], [42, 80], [20, 64], [18, 30], [42, 16], [50, 50]];
  names.forEach((name, index) => {
    const element = document.createElement("div");
    element.className = "orb";
    element.textContent = name;
    element.style.left = `${coords[index][0]}%`;
    element.style.top = `${coords[index][1]}%`;
    root.appendChild(element);
  });
}

function showPage(page) {
  document.querySelectorAll(".page").forEach((element) => element.classList.remove("active"));
  $(`page-${page}`)?.classList.add("active");
  document.querySelectorAll("[data-page]").forEach((button) => button.classList.toggle("active", button.dataset.page === page));
}

function jobClass(status) {
  return String(status || "unknown").toLowerCase().replace(/[^a-z0-9_-]/g, "");
}

function summarizeJob(job) {
  const result = job?.result || {};
  const execution = result.execution || result.result?.execution || {};
  const duration = result.duration_sec || execution.duration_sec || result.result?.duration_sec || "";
  const reason = result.reason || result.verdict || result.message || result.status || job?.summary || "";
  return { duration, reason };
}

function renderJobs() {
  const list = $("jobList");
  if (!list) return;
  list.innerHTML = "";
  const filtered = (jobs || []).filter((job) => jobFilter === "all" || jobClass(job.status) === jobFilter);
  if (!filtered.length) {
    list.innerHTML = '<div class="job empty">No jobs match this filter.</div>';
    return;
  }
  filtered.forEach((job) => {
    const card = document.createElement("button");
    const summary = summarizeJob(job);
    card.className = `job-card${job.job_id === currentJobId ? " active" : ""}`;
    card.dataset.jobId = job.job_id;
    card.innerHTML = `<span class="job-status ${jobClass(job.status)}">${job.status}</span><b>${job.action}</b><small>${job.job_id}</small><time>${job.updated_at_utc || job.created_at_utc}${summary.duration ? ` · ${summary.duration}s` : ""}</time><small>${summary.reason || "allowlisted action"}</small>`;
    card.onclick = () => loadJob(job.job_id);
    list.appendChild(card);
  });
}

function jobResult(job) {
  return job?.result || {};
}

function executionOf(job) {
  const result = jobResult(job);
  return result.execution || result.result?.execution || result.result || result;
}

function artifactList(job) {
  const result = jobResult(job);
  const artifacts = [];
  for (const key of ["receipt", "stage_ledger", "task_template_zip", "report_bundle_zip", "manifest_path", "output_root", "runtime_state_path"]) {
    if (result[key]) artifacts.push(`${key}: ${result[key]}`);
  }
  if (result.runtime_paths) Object.entries(result.runtime_paths).forEach(([key, value]) => value && artifacts.push(`${key}: ${value}`));
  if (result.evidence_outputs) artifacts.push(`evidence: ${(result.evidence_outputs || []).join(", ")}`);
  if (job?.evidence_outputs) artifacts.push(`expected: ${job.evidence_outputs.join(", ")}`);
  return artifacts.length ? artifacts.join("\n") : "No artifact paths reported.";
}

function renderJobDetail(tab = currentJobTab) {
  currentJobTab = tab;
  if (!currentJobRaw) {
    setText("jobSummary", "No job selected.");
    setText("jobTrace", "No job selected.");
    return;
  }
  const job = currentJobRaw;
  const result = jobResult(job);
  const execution = executionOf(job);
  const summary = [
    `Action: ${job.action}`,
    `Status: ${job.status}`,
    `Job: ${job.job_id}`,
    `Created: ${job.created_at_utc}`,
    `Updated: ${job.updated_at_utc}`,
    result.reason ? `Reason: ${result.reason}` : "",
    result.verdict ? `Verdict: ${result.verdict}` : "",
    execution.duration_sec ? `Duration: ${execution.duration_sec}s` : "",
  ].filter(Boolean).join("\n");
  setText("jobSummary", summary);
  let trace = summary;
  if (tab === "stdout") trace = execution.stdout || result.stdout || "No stdout captured.";
  if (tab === "stderr") trace = execution.stderr || result.stderr || "No stderr captured.";
  if (tab === "artifacts") trace = artifactList(job);
  if (tab === "raw") trace = JSON.stringify(job, null, 2);
  if (tab === "summary") trace = summary;
  setText("jobTrace", trace);
  document.querySelectorAll("[data-job-tab]").forEach((button) => button.classList.toggle("active", button.dataset.jobTab === tab));
}

function renderAdmission(result) {
  if (!result) return;
  const receipt = result.receipt || {};
  setText("admissionVerdict", result.verdict || result.status || "UNKNOWN");
  setText("admissionTaskId", result.task_id || "none");
  setText("admissionPath", result.registered_path || "none");
  setText("admissionCaps", typeof result.caps === "string" ? result.caps : JSON.stringify(result.caps || {}));
  setText("admissionWarnings", (result.warnings || []).join(" · ") || "none");
  setText("admissionReceipt", receipt.receipt_path || receipt.admission_receipt_path || "embedded in job result");
  setText("registrationTrace", JSON.stringify(result, null, 2));
}

function routeJobResult(job) {
  const traceMap = {
    register_taskpack_pc: "registrationTrace",
    validate_warp: "validationTrace",
    build_report_bundle: "reportTrace",
    mechanicus_register_tool: "mechanicusTrace",
    mechanicus_list_tools: "mechanicusTrace",
    run_playwright: "playwrightTrace",
    run_playwright_screenshots: "playwrightTrace",
    runtime_hygiene_scan: "hygieneTrace",
    node_probe: "hygieneTrace",
    stage_start_current: "stageTrace",
    stage_submit_evidence: "stageTrace",
    stage_run_gate: "stageTrace",
    stage_close_stage: "stageTrace",
    promotion_preview: "promotionTrace",
  };
  const target = traceMap[job.action];
  if (target) setText(target, JSON.stringify(job.result || job, null, 2));
  if (job.action === "register_taskpack_pc") renderAdmission(job.result);
  if (job.action === "promotion_preview") renderPromotion(job.result);
}

async function refreshJobs() {
  const data = await api("/api/jobs");
  jobs = data.jobs || [];
  renderJobs();
  renderContour();
}

async function loadJob(id) {
  currentJobId = id;
  const data = await api(`/api/jobs/${id}`);
  currentJobRaw = data;
  renderJobDetail(currentJobTab || "summary");
  routeJobResult(data);
  renderJobs();
  if (data.status === "RUNNING") {
    setTimeout(() => loadJob(id), 750);
  } else {
    await refreshSnapshot(false);
  }
}

async function refreshSnapshot(includeJobs = true) {
  snapshot = await api("/api/snapshot");
  if (includeJobs) await refreshJobs();
  renderContour();
  renderFlow();
  renderOrbit();
  renderStageControl();
  window.__SANCTUM_READY = true;
}

async function detectBridge() {
  const health = await api("/api/health");
  bridgeMode = health.actions_enabled ? "actions" : "read-only";
  setText("bridgePill", `bridge: ${bridgeMode} · jobs:${health.job_runner ? "yes" : "no"}`);
}

async function sendAction(actionId, sourceButton = null) {
  const body = { action: actionId };
  if (actionId === "register_taskpack_pc") body.zip_path = $("taskZipPath")?.value || "";
  document.body.classList.add("action-running");
  sourceButton?.classList.add("busy");
  toast(`dispatching: ${actionId}`);
  try {
    const data = await api("/api/action", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    if (data.status === "BLOCKED") {
      toast(data.message || data.reason || "blocked");
      return data;
    }
    if (data.job_id) {
      currentJobId = data.job_id;
      toast(`job accepted: ${actionId}`);
      await refreshJobs();
      loadJob(data.job_id);
      showPage(actionId === "register_taskpack_pc" ? "register" : actionId.startsWith("stage_") ? "stage" : actionId === "promotion_preview" ? "promotion" : "jobs");
      return data;
    }
    toast(`${actionId}: ${data.status || "done"}`);
    return data;
  } finally {
    setTimeout(() => {
      document.body.classList.remove("action-running");
      sourceButton?.classList.remove("busy");
    }, 650);
  }
}

function paletteItems() {
  return [
    { label: "Go Sanctum", page: "sanctum" },
    { label: "Go WARP", page: "warp" },
    { label: "Go Task Register", page: "register" },
    { label: "Go Jobs", page: "jobs" },
    { label: "Go Stage Control", page: "stage" },
    { label: "Go Runtime Hygiene", page: "hygiene" },
    { label: "Go Validation", page: "validation" },
    { label: "Go Reports", page: "reports" },
    { label: "Go Promotion Preview", page: "promotion" },
    { label: "Create WARP", action: "create_warp" },
    { label: "Start Work", action: "start_work" },
    { label: "Build Report Bundle", action: "build_report_bundle" },
    { label: "Run Stage Gate", action: "stage_run_gate" },
    { label: "Promotion Preview", action: "promotion_preview" },
    { label: "Scan Runtime Hygiene", action: "runtime_hygiene_scan" },
    { label: "Probe This Node", action: "node_probe" },
  ];
}

function renderPalette() {
  const query = ($("paletteSearch")?.value || "").toLowerCase();
  const list = $("paletteList");
  if (!list) return;
  list.innerHTML = "";
  paletteItems().filter((item) => item.label.toLowerCase().includes(query)).forEach((item, index) => {
    const button = document.createElement("button");
    button.className = "paletteItem";
    button.textContent = item.label;
    button.onclick = () => {
      if (item.page) showPage(item.page);
      if (item.action) sendAction(item.action);
      closePalette();
    };
    if (index === 0) button.dataset.first = "true";
    list.appendChild(button);
  });
}

function openPalette() {
  paletteOpen = true;
  $("commandPalette")?.classList.remove("hidden");
  const search = $("paletteSearch");
  if (search) {
    search.value = "";
    search.focus();
  }
  renderPalette();
}

function closePalette() {
  paletteOpen = false;
  $("commandPalette")?.classList.add("hidden");
}

function copyText(text, message) {
  navigator.clipboard?.writeText(text).then(() => toast(message));
}

function bind() {
  document.querySelectorAll("[data-page]").forEach((button) => button.addEventListener("click", () => showPage(button.dataset.page)));
  document.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => sendAction(button.dataset.action, button)));
  $("qualityButton")?.addEventListener("click", () => {
    quality = quality === "Performance" ? "Balanced" : quality === "Balanced" ? "Cinematic" : "Performance";
    setText("qualityButton", `Quality: ${quality}`);
    document.body.dataset.quality = quality.toLowerCase();
    renderContour();
  });
  $("paletteButton")?.addEventListener("click", openPalette);
  $("copySnapshot")?.addEventListener("click", () => copyText(JSON.stringify(snapshot, null, 2), "snapshot copied"));
  $("copyWarpPath")?.addEventListener("click", () => copyText(snapshot?.warp?.path || "", "WARP path copied"));
  $("refreshJobs")?.addEventListener("click", refreshJobs);
  $("jobFilter")?.addEventListener("change", (event) => { jobFilter = event.target.value || "all"; renderJobs(); });
  document.querySelectorAll("[data-job-tab]").forEach((button) => button.addEventListener("click", () => renderJobDetail(button.dataset.jobTab)));
  $("paletteSearch")?.addEventListener("input", renderPalette);
  $("paletteSearch")?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      $("paletteList")?.querySelector(".paletteItem")?.click();
    }
    if (event.key === "Escape") closePalette();
  });
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      openPalette();
    }
    if (paletteOpen && event.key === "Escape") closePalette();
  });
}

async function boot() {
  bind();
  await detectBridge();
  await refreshSnapshot();
  setInterval(refreshJobs, 2500);
}

boot().catch((error) => {
  console.error(error);
  toast("boot failed");
  window.__SANCTUM_READY = true;
});
