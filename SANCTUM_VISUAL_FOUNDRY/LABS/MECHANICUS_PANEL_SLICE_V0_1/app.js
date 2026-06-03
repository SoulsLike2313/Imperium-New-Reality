const TOOL_SNAPSHOT = [
  { tool_id: "git", owner_organ: "ADMINISTRATUM_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_BOTH" },
  { tool_id: "node", owner_organ: "MECHANICUS_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_PC" },
  { tool_id: "npm", owner_organ: "MECHANICUS_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_PC" },
  { tool_id: "ripgrep", owner_organ: "INQUISITION_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_BOTH" },
  { tool_id: "ruff", owner_organ: "MECHANICUS_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "AVAILABLE_VM2" },
  { tool_id: "pytest", owner_organ: "MECHANICUS_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_PC" },
  { tool_id: "jsonschema", owner_organ: "DOCTRINARIUM_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "AVAILABLE_VM2" },
  { tool_id: "jq", owner_organ: "ADMINISTRATUM_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_BOTH" },
  { tool_id: "yq", owner_organ: "ADMINISTRATUM_AGENT", pc_status: "AVAILABLE_PC", combined_status: "AVAILABLE_BOTH" },
  { tool_id: "gitleaks", owner_organ: "INQUISITION_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "KNOWN_NOT_INSTALLED" },
  { tool_id: "semgrep", owner_organ: "INQUISITION_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "KNOWN_NOT_INSTALLED" },
  { tool_id: "bandit", owner_organ: "INQUISITION_AGENT", pc_status: "NOT_FOUND_ON_PC", combined_status: "KNOWN_NOT_INSTALLED" }
];

const COMMANDS = [
  { cmd: "status", detail: "Show organ status and health", key: "F1" },
  { cmd: "tools", detail: "List tool registry and capabilities", key: "F2" },
  { cmd: "identity", detail: "Show organ identity and mission", key: "F3" },
  { cmd: "check", detail: "Run validations and integrity checks", key: "F4" },
  { cmd: "where", detail: "Show paths and active worktree", key: "F5" },
  { cmd: "help", detail: "Show admitted command lanes", key: "F6" },
  { cmd: "raw", detail: "Open explicit raw detail lane", key: "F7" },
  { cmd: "screenshot", detail: "Capture visual evidence lane", key: "F8" },
  { cmd: "clear", detail: "Reset command output lane", key: "ESC" }
];

const ACTIVITY_BY_STATE = {
  idle: [
    ["12:54:01", "G", "Registry sync", "Tool index loaded from snapshot", "IDLE"],
    ["12:54:03", "T", "Truth lane", "Backend source remains CANDIDATE", "UNKNOWN"],
    ["12:54:05", "S", "SSE", "Live stream is intentionally STUB", "STUB"],
    ["12:54:08", "C", "Command zone", "Allowlist is ready, no active dispatch", "IDLE"]
  ],
  active: [
    ["12:56:10", "W", "where", "Mechanicus path summary validated", "ACTIVE"],
    ["12:56:15", "S", "status", "Visual slice state transitioned to ACTIVE", "ACTIVE"],
    ["12:56:17", "T", "tools", "Registry counters refreshed", "ACTIVE"],
    ["12:56:21", "R", "raw", "Diagnostic lane returned bounded output", "ACTIVE"]
  ],
  warn: [
    ["12:58:02", "A", "allowlist", "One requested command is not admitted", "WARN"],
    ["12:58:05", "B", "backend", "State source is candidate, not real", "WARN"],
    ["12:58:08", "E", "evidence", "Latest report path unresolved", "UNKNOWN"],
    ["12:58:11", "S", "transport", "SSE remains STUB in this isolated lab", "STUB"]
  ],
  blocked: [
    ["13:01:44", "X", "git status", "Blocked: command not in allowlist", "BLOCKED"],
    ["13:01:46", "L", "privileged lane", "LOCKED command class requires owner gate", "LOCKED"],
    ["13:01:49", "T", "truth", "No fake PASS emitted under blocked state", "OK"],
    ["13:01:52", "S", "safety", "Scope boundary preserved", "OK"]
  ],
  unknown: [
    ["13:05:14", "?", "state source", "No fresh runtime payload", "UNKNOWN"],
    ["13:05:18", "?", "activity", "Last signal timestamp unavailable", "UNKNOWN"],
    ["13:05:22", "?", "evidence", "Latest receipt unresolved", "UNKNOWN"],
    ["13:05:28", "I", "operator", "Fallback static mode enabled", "IDLE"]
  ]
};

const PRESSURE_CHANNELS = [
  { id: "ARC-01", base: 0.55, speed: 0.75, phase: 0.1 },
  { id: "ARC-02", base: 0.62, speed: 0.63, phase: 0.7 },
  { id: "ARC-03", base: 0.41, speed: 0.9, phase: 1.2 },
  { id: "ARC-04", base: 0.7, speed: 0.52, phase: 1.8 },
  { id: "ARC-05", base: 0.48, speed: 1.05, phase: 2.4 },
  { id: "ARC-06", base: 0.58, speed: 0.82, phase: 2.9 }
];

const body = document.body;
const shell = document.querySelector(".slice-shell");
const statePill = document.getElementById("statePill");
const activityList = document.getElementById("activityList");
const commandGrid = document.getElementById("commandGrid");
const toolRows = document.getElementById("toolRows");
const motionToggle = document.getElementById("motionToggle");
const pressureBars = document.getElementById("pressureBars");
const neuroCanvas = document.getElementById("neuroCanvas");

const metricFps = document.getElementById("metricFps");
const metricMotion = document.getElementById("metricMotion");

const reduceMotionMedia = window.matchMedia("(prefers-reduced-motion: reduce)");

let manualReducedMotion = false;
let reducedMotion = reduceMotionMedia.matches;
let pressureNodes = [];

const tilt = {
  targetX: 0,
  targetY: 0,
  currentX: 0,
  currentY: 0
};

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function stateClassName(state) {
  return `state-${state.toLowerCase()}`;
}

function chipClass(status) {
  const normalized = status.toLowerCase();
  if (normalized === "active" || normalized === "ok") return "chip-active";
  if (normalized === "idle") return "chip-idle";
  if (normalized === "warn") return "chip-warn";
  if (normalized === "blocked" || normalized === "error" || normalized === "locked") return "chip-blocked";
  if (normalized === "stub") return "chip-warn";
  return "chip-unknown";
}

function renderCommands() {
  commandGrid.innerHTML = "";
  for (const row of COMMANDS) {
    const card = document.createElement("article");
    card.className = "command-card";
    card.innerHTML = [
      `<strong>${row.cmd}</strong>`,
      `<small>${row.detail}</small>`,
      `<span class="keycap">${row.key}</span>`
    ].join("");
    commandGrid.appendChild(card);
  }
  document.getElementById("metricCmds").textContent = String(COMMANDS.length);
}

function renderTools() {
  const declaredRegisteredCount = 20;
  const snapshotRowsCount = TOOL_SNAPSHOT.length;
  const available = TOOL_SNAPSHOT.filter((tool) => tool.pc_status === "AVAILABLE_PC").length;
  const warnings = TOOL_SNAPSHOT.filter((tool) => tool.pc_status !== "AVAILABLE_PC").length;
  const errors = TOOL_SNAPSHOT.filter((tool) => tool.combined_status === "KNOWN_NOT_INSTALLED").length;

  document.getElementById("countRegistered").textContent = `${declaredRegisteredCount} (rows:${snapshotRowsCount})`;
  document.getElementById("countAvailable").textContent = String(available);
  document.getElementById("countWarnings").textContent = String(warnings);
  document.getElementById("countErrors").textContent = String(errors);

  toolRows.innerHTML = "";
  for (const row of TOOL_SNAPSHOT) {
    const tr = document.createElement("tr");
    tr.innerHTML = [
      `<td>${row.tool_id}</td>`,
      `<td>${row.owner_organ}</td>`,
      `<td>${row.pc_status}</td>`,
      `<td>${row.combined_status}</td>`
    ].join("");
    toolRows.appendChild(tr);
  }
}

function renderActivity(state) {
  activityList.innerHTML = "";
  const entries = ACTIVITY_BY_STATE[state] ?? ACTIVITY_BY_STATE.unknown;
  let warnCount = 0;
  let blockedCount = 0;

  for (const [time, glyph, item, detail, status] of entries) {
    const lowered = status.toLowerCase();
    if (lowered === "warn" || lowered === "stub" || lowered === "unknown") warnCount += 1;
    if (lowered === "blocked" || lowered === "locked") blockedCount += 1;

    const li = document.createElement("li");
    li.innerHTML = [
      `<span class="time-tag">${time}</span>`,
      `<span class="item-glyph">${glyph}</span>`,
      `<div><p class="item-title">${item}</p><p class="item-detail">${detail}</p></div>`,
      `<span class="state-chip ${chipClass(status)}">${status}</span>`
    ].join("");
    activityList.appendChild(li);
  }

  document.getElementById("metricWarn").textContent = String(warnCount);
  document.getElementById("metricBlock").textContent = String(blockedCount);
}

function setState(nextState) {
  body.classList.remove("state-idle", "state-active", "state-warn", "state-blocked", "state-unknown");
  body.classList.add(stateClassName(nextState));
  statePill.textContent = `STATE: ${nextState.toUpperCase()}`;
  renderActivity(nextState);
}

function setupStateButtons() {
  for (const button of document.querySelectorAll("[data-state]")) {
    button.addEventListener("click", () => setState(button.dataset.state || "unknown"));
  }
}

function renderPressureBars() {
  if (!pressureBars) return;
  pressureBars.innerHTML = "";
  pressureNodes = [];

  for (const channel of PRESSURE_CHANNELS) {
    const card = document.createElement("article");
    card.className = "pressure-bar";
    const label = document.createElement("span");
    label.className = "pressure-label";
    label.textContent = channel.id;

    const track = document.createElement("span");
    track.className = "pressure-track";
    const fill = document.createElement("span");
    fill.className = "pressure-fill";
    fill.style.setProperty("--pressure-scale", String(channel.base));
    track.appendChild(fill);

    const value = document.createElement("span");
    value.className = "pressure-value";
    value.textContent = `${Math.round(channel.base * 100)}%`;

    card.append(label, track, value);
    pressureBars.appendChild(card);
    pressureNodes.push({ ...channel, fill, value });
  }
}

function applyReducedMotion() {
  reducedMotion = manualReducedMotion || reduceMotionMedia.matches;
  body.classList.toggle("reduced-motion", reducedMotion);
  motionToggle.textContent = `Reduced Motion: ${reducedMotion ? "ON" : "OFF"}`;
  metricMotion.textContent = reducedMotion ? "REDUCED" : "RUN";
}

function setupReducedMotionToggle() {
  motionToggle.addEventListener("click", () => {
    manualReducedMotion = !manualReducedMotion;
    applyReducedMotion();
    neuroEngine.setReducedMotion(reducedMotion);
  });

  reduceMotionMedia.addEventListener("change", () => {
    applyReducedMotion();
    neuroEngine.setReducedMotion(reducedMotion);
  });
}

function updatePressureBars(timeSeconds) {
  for (const channel of pressureNodes) {
    let scale = channel.base;
    if (!reducedMotion) {
      const wave = Math.sin((timeSeconds * channel.speed) + channel.phase);
      const micro = Math.sin((timeSeconds * channel.speed * 2.8) + (channel.phase * 0.5));
      scale = clamp(channel.base + (wave * 0.17) + (micro * 0.05), 0.12, 0.98);
    }
    channel.fill.style.setProperty("--pressure-scale", scale.toFixed(3));
    channel.value.textContent = `${Math.round(scale * 100)}%`;
  }
}

function updateTilt(deltaSeconds) {
  if (!shell) return;
  if (reducedMotion) {
    tilt.targetX = 0;
    tilt.targetY = 0;
  }
  const smoothing = clamp(deltaSeconds * 8.5, 0.08, 0.28);
  tilt.currentX += (tilt.targetX - tilt.currentX) * smoothing;
  tilt.currentY += (tilt.targetY - tilt.currentY) * smoothing;
  document.documentElement.style.setProperty("--tilt-x", `${tilt.currentX.toFixed(3)}deg`);
  document.documentElement.style.setProperty("--tilt-y", `${tilt.currentY.toFixed(3)}deg`);
}

class NeuroFieldEngine {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas ? canvas.getContext("2d", { alpha: true }) : null;
    this.width = 0;
    this.height = 0;
    this.nodes = [];
    this.pointer = { x: 0, y: 0, active: false };
    this.running = false;
    this.reduced = false;
    this.lastFrame = 0;
    this.rafId = 0;
    this.time = 0;
    this.fps = 0;
    this.fpsCounter = 0;
    this.fpsAccumulator = 0;
    this.handleResize = this.resize.bind(this);
  }

  setReducedMotion(flag) {
    this.reduced = flag;
    if (flag && this.ctx) {
      this.ctx.clearRect(0, 0, this.width, this.height);
      metricFps.textContent = "--";
    }
  }

  setPointer(x, y, active) {
    this.pointer.x = x;
    this.pointer.y = y;
    this.pointer.active = active;
  }

  resize() {
    if (!this.canvas || !this.ctx) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(window.innerWidth, 320);
    const height = Math.max(window.innerHeight, 240);
    this.canvas.width = Math.round(width * dpr);
    this.canvas.height = Math.round(height * dpr);
    this.canvas.style.width = `${width}px`;
    this.canvas.style.height = `${height}px`;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.width = width;
    this.height = height;
    this.buildNodes();
  }

  buildNodes() {
    const density = clamp((this.width * this.height) / 26000, 46, 110);
    const nodeCount = Math.round(density);
    const next = [];
    for (let i = 0; i < nodeCount; i += 1) {
      const speed = 0.34 + (Math.random() * 0.78);
      const angle = Math.random() * Math.PI * 2;
      next.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 0.8 + (Math.random() * 1.55),
        phase: Math.random() * Math.PI * 2
      });
    }
    this.nodes = next;
  }

  start() {
    if (!this.ctx || this.running) return;
    this.running = true;
    this.resize();
    window.addEventListener("resize", this.handleResize);
    this.rafId = window.requestAnimationFrame((t) => this.loop(t));
  }

  stop() {
    this.running = false;
    window.removeEventListener("resize", this.handleResize);
    window.cancelAnimationFrame(this.rafId);
  }

  loop(timestamp) {
    if (!this.running) return;
    if (!this.lastFrame) this.lastFrame = timestamp;
    const deltaSeconds = Math.min((timestamp - this.lastFrame) / 1000, 0.034);
    this.lastFrame = timestamp;
    this.time += deltaSeconds;

    updateTilt(deltaSeconds);
    updatePressureBars(this.time);

    if (!this.reduced) {
      this.updateNodes(deltaSeconds);
      this.drawFrame();
      this.fpsCounter += 1;
      this.fpsAccumulator += deltaSeconds;
      if (this.fpsAccumulator >= 0.6) {
        this.fps = Math.round(this.fpsCounter / this.fpsAccumulator);
        metricFps.textContent = String(this.fps);
        this.fpsCounter = 0;
        this.fpsAccumulator = 0;
      }
    }

    this.rafId = window.requestAnimationFrame((t) => this.loop(t));
  }

  updateNodes(deltaSeconds) {
    const influenceRadius = 160;
    const influenceRadiusSquared = influenceRadius * influenceRadius;

    for (const node of this.nodes) {
      if (this.pointer.active) {
        const dx = this.pointer.x - node.x;
        const dy = this.pointer.y - node.y;
        const d2 = (dx * dx) + (dy * dy);
        if (d2 < influenceRadiusSquared && d2 > 1) {
          const pull = 0.018 * (1 - (d2 / influenceRadiusSquared));
          const inv = 1 / Math.sqrt(d2);
          node.vx += dx * inv * pull;
          node.vy += dy * inv * pull;
        }
      }

      node.x += node.vx * deltaSeconds * 60;
      node.y += node.vy * deltaSeconds * 60;

      if (node.x < 0 || node.x > this.width) {
        node.vx *= -1;
        node.x = clamp(node.x, 0, this.width);
      }

      if (node.y < 0 || node.y > this.height) {
        node.vy *= -1;
        node.y = clamp(node.y, 0, this.height);
      }

      node.vx *= 0.998;
      node.vy *= 0.998;
      node.phase += deltaSeconds;
    }
  }

  drawFrame() {
    if (!this.ctx) return;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);
    ctx.fillStyle = "rgba(3, 8, 15, 0.22)";
    ctx.fillRect(0, 0, this.width, this.height);

    const maxDistance = 138;
    const maxDistanceSquared = maxDistance * maxDistance;

    for (let i = 0; i < this.nodes.length; i += 1) {
      const a = this.nodes[i];
      for (let j = i + 1; j < this.nodes.length; j += 1) {
        const b = this.nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const d2 = (dx * dx) + (dy * dy);
        if (d2 > maxDistanceSquared) continue;

        const ratio = 1 - (d2 / maxDistanceSquared);
        ctx.strokeStyle = `rgba(98, 214, 255, ${0.03 + (ratio * 0.22)})`;
        ctx.lineWidth = 0.6 + (ratio * 0.8);
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
    }

    for (const node of this.nodes) {
      const glow = 0.45 + (Math.sin(node.phase * 2.2) * 0.25);
      ctx.fillStyle = `rgba(113, 224, 255, ${glow})`;
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
      ctx.fill();
    }

    if (this.pointer.active) {
      const gradient = ctx.createRadialGradient(
        this.pointer.x,
        this.pointer.y,
        12,
        this.pointer.x,
        this.pointer.y,
        150
      );
      gradient.addColorStop(0, "rgba(98, 214, 255, 0.2)");
      gradient.addColorStop(1, "rgba(98, 214, 255, 0)");
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(this.pointer.x, this.pointer.y, 150, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

const neuroEngine = new NeuroFieldEngine(neuroCanvas);

function setupPointerTracking() {
  window.addEventListener("pointermove", (event) => {
    const { innerWidth, innerHeight } = window;
    const xRatio = clamp(event.clientX / innerWidth, 0, 1);
    const yRatio = clamp(event.clientY / innerHeight, 0, 1);

    if (!reducedMotion) {
      tilt.targetX = clamp((0.5 - yRatio) * 2.8, -2.8, 2.8);
      tilt.targetY = clamp((xRatio - 0.5) * 4.2, -4.2, 4.2);
      neuroEngine.setPointer(event.clientX, event.clientY, true);
    }
  }, { passive: true });

  window.addEventListener("pointerleave", () => {
    tilt.targetX = 0;
    tilt.targetY = 0;
    neuroEngine.setPointer(0, 0, false);
  }, { passive: true });
}

renderCommands();
renderTools();
renderPressureBars();
renderActivity("active");
setupStateButtons();
setupPointerTracking();
applyReducedMotion();
setupReducedMotionToggle();
neuroEngine.setReducedMotion(reducedMotion);
neuroEngine.start();
