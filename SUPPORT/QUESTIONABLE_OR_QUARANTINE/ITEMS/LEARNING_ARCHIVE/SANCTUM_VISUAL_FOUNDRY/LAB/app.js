const I18N = {
  en: {
    eyebrow: "VISUAL FOUNDRY // BRAIN FORGE ITERATION",
    title: "MECHANICUS OPERATOR COCKPIT // SECOND-MIND DOMINION",
    mission:
      "The brain field now drives the scene mass, while the right cockpit exposes active organ operations without promoting raw output.",
    brainSectorTitle: "NEURAL DOMINION // ORGAN TOPOLOGY",
    brainSectorNote: "Select an organ node to route context into the cockpit panel.",
    brainPulseState: "pulse lattice: stable",
    workReportTitle: "WORK REPORT // LIVE OPERATOR TRACK",
    cockpitTitle: "MECHANICUS COCKPIT PANEL",
    cockpitNote: "Forge operations and holograph controls are grouped as cockpit modules.",
    toolsTitle: "APPROVED TOOLS BUS",
    contourTitle: "CONTOUR / READINESS GRID",
    actionTitle: "SANCTUM-LAYER ACTION SWITCHBOARD",
    rawModeTitle: "RAW TECHNICAL MODE (SECONDARY)",
    rawOn: "RAW ON",
    rawOff: "RAW OFF",
    scope: "scope",
    branch: "branch",
    head: "head",
    visual: "visual",
    state: "state",
    footerReport: "LATEST REPORT",
    footerReceipt: "LATEST RECEIPT",
    footerEvent: "EVENT SUMMARY",
    footerHealth: "COCKPIT HEALTH",
    runAction: "Run",
    actionNote: "Operator action prepared for controlled flow.",
    active: "active"
  },
  ru: {
    eyebrow: "VISUAL FOUNDRY // BRAIN FORGE ITERATION",
    title: "MECHANICUS OPERATOR COCKPIT // SECOND-MIND DOMINION",
    mission:
      "Brain field теперь доминирует по визуальной массе, а правый cockpit держит операционный контекст без вывода raw в главный режим.",
    brainSectorTitle: "NEURAL DOMINION // ORGAN TOPOLOGY",
    brainSectorNote: "Выберите organ node, чтобы передать контекст в правую cockpit-панель.",
    brainPulseState: "pulse lattice: stable",
    workReportTitle: "WORK REPORT // LIVE OPERATOR TRACK",
    cockpitTitle: "MECHANICUS COCKPIT PANEL",
    cockpitNote: "Forge операции и holograph-контролы сгруппированы как cockpit-модули.",
    toolsTitle: "APPROVED TOOLS BUS",
    contourTitle: "CONTOUR / READINESS GRID",
    actionTitle: "SANCTUM-LAYER ACTION SWITCHBOARD",
    rawModeTitle: "RAW TECHNICAL MODE (SECONDARY)",
    rawOn: "RAW ON",
    rawOff: "RAW OFF",
    scope: "scope",
    branch: "ветка",
    head: "head",
    visual: "visual",
    state: "статус",
    footerReport: "ПОСЛЕДНИЙ ОТЧЕТ",
    footerReceipt: "ПОСЛЕДНИЙ RECEIPT",
    footerEvent: "СВОДКА СОБЫТИЙ",
    footerHealth: "ЗДОРОВЬЕ COCKPIT",
    runAction: "Запуск",
    actionNote: "Operator-действие подготовлено для контролируемого потока.",
    active: "active"
  }
};

const ORGANS = [
  { id: "MECHANICUS", title: "MECHANICUS", hint: "forge tooling", x: 15, y: 56 },
  { id: "ADMINISTRATUM", title: "ADMINISTRATUM", hint: "receipt truth", x: 16, y: 22 },
  { id: "OFFICIO", title: "OFFICIO", hint: "agent control", x: 40, y: 11 },
  { id: "INQUISITION", title: "INQUISITION", hint: "gate audits", x: 66, y: 19 },
  { id: "DOCTRINARIUM", title: "DOCTRINARIUM", hint: "contracts", x: 80, y: 42 },
  { id: "STRATEGIUM", title: "STRATEGIUM", hint: "plans", x: 70, y: 64 },
  { id: "CUSTODES", title: "CUSTODES", hint: "guard locks", x: 44, y: 77 }
];

const TOOLS = {
  MECHANICUS: [
    ["git", "ok"],
    ["node", "ok"],
    ["npm", "ok"],
    ["playwright", "warn"],
    ["jsonschema", "warn"],
    ["token_lint", "ok"]
  ],
  ADMINISTRATUM: [
    ["receipt_checker", "ok"],
    ["scope_map", "ok"],
    ["delta_digest", "warn"]
  ],
  OFFICIO: [
    ["role_ack", "ok"],
    ["observer_trace", "warn"],
    ["task_router", "ok"]
  ],
  INQUISITION: [
    ["gate_audit", "ok"],
    ["fake_green_scan", "ok"],
    ["perf_strike", "warn"]
  ],
  DOCTRINARIUM: [
    ["contract_lint", "ok"],
    ["token_diff", "ok"],
    ["style_budget", "warn"]
  ],
  STRATEGIUM: [
    ["timeline_planner", "ok"],
    ["risk_projection", "warn"],
    ["rollback_lane", "ok"]
  ],
  CUSTODES: [
    ["boundary_lock", "ok"],
    ["owner_gate", "ok"],
    ["threat_watch", "warn"]
  ]
};

const CONTOUR = {
  MECHANICUS: [
    ["Windows readiness", "ok"],
    ["Ubuntu parity", "warn"],
    ["Contour verification", "ok"],
    ["Forge holograph cohesion", "ok"]
  ],
  ADMINISTRATUM: [
    ["Path truth", "ok"],
    ["Receipt binding", "ok"],
    ["Output budget", "ok"]
  ],
  OFFICIO: [
    ["Role admission", "ok"],
    ["Stop conditions", "ok"],
    ["Control density", "warn"]
  ],
  INQUISITION: [
    ["Gate compliance", "ok"],
    ["No fake green", "ok"],
    ["Alert channel", "warn"]
  ],
  DOCTRINARIUM: [
    ["Contract integrity", "ok"],
    ["Token layer explicit", "ok"],
    ["Style drift", "warn"]
  ],
  STRATEGIUM: [
    ["Roadmap lock", "ok"],
    ["Impact map", "warn"],
    ["Execution lane", "ok"]
  ],
  CUSTODES: [
    ["Boundary lock", "ok"],
    ["Escalation channel", "warn"],
    ["Guard truth", "ok"]
  ]
};

const ACTIONS = [
  "send_prompt_to_vm",
  "fetch_bundle",
  "build_continuity",
  "run_audit",
  "dirty_state_inspection",
  "contour_verification"
];

const WORK_BASE = [
  ["18:58", "Brain forge iteration armed", "neural dominion mass increased for operator-first focus"],
  ["19:02", "Token layer v0.2", "explicit JSON/CSS token layer wired into LAB"],
  ["19:06", "Cockpit refit", "right panel converted from flat cards to cockpit modules"],
  ["19:11", "Proof runner", "screenshots include brain focus and cockpit focus"],
  ["19:15", "Scope lock", "all writes contained in IMPERIUM_NEW_GENERATION"]
];

const FOOTER = [
  ["footerReport", "validation_report.json"],
  ["footerReceipt", "FINAL_RECEIPT.json"],
  ["footerEvent", "WARN=2 ERROR=0 BLOCK=0"],
  ["footerHealth", "RAW SECONDARY / BRAIN DOMINANT"]
];

let locale = "ru";
let rawVisible = false;
let activeOrgan = "MECHANICUS";
const workFeed = [...WORK_BASE];

const el = {
  truthEyebrow: document.getElementById("truthEyebrow"),
  mainTitle: document.getElementById("mainTitle"),
  missionLine: document.getElementById("missionLine"),
  truthChipRow: document.getElementById("truthChipRow"),
  langSwitch: document.getElementById("langSwitch"),
  rawToggle: document.getElementById("rawToggle"),
  brainSectorTitle: document.getElementById("brainSectorTitle"),
  brainSectorNote: document.getElementById("brainSectorNote"),
  brainPulseState: document.getElementById("brainPulseState"),
  neuralLinks: document.getElementById("neuralLinks"),
  organNodes: document.getElementById("organNodes"),
  workReportTitle: document.getElementById("workReportTitle"),
  workFeed: document.getElementById("workFeed"),
  cockpitTitle: document.getElementById("cockpitTitle"),
  activeOrganTag: document.getElementById("activeOrganTag"),
  cockpitNote: document.getElementById("cockpitNote"),
  toolsTitle: document.getElementById("toolsTitle"),
  contourTitle: document.getElementById("contourTitle"),
  actionTitle: document.getElementById("actionTitle"),
  toolsList: document.getElementById("toolsList"),
  contourList: document.getElementById("contourList"),
  actionGrid: document.getElementById("actionGrid"),
  rawMode: document.getElementById("rawMode"),
  rawModeTitle: document.getElementById("rawModeTitle"),
  rawPayload: document.getElementById("rawPayload"),
  footerStrip: document.getElementById("footerStrip")
};

function t(key) {
  return I18N[locale][key] ?? key;
}

function stateClass(value) {
  if (value === "ok") return "ok";
  if (value === "warn") return "warn";
  return "error";
}

function renderTruthStrip() {
  const chips = [
    [t("scope"), "IMPERIUM_NEW_GENERATION", "ok"],
    [t("branch"), "master", "ok"],
    [t("head"), "66ebf5b0", "warn"],
    [t("visual"), "brain_forge_iter_v0_1", "ok"]
  ];
  el.truthChipRow.innerHTML = "";
  chips.forEach(([k, v, s]) => {
    const chip = document.createElement("div");
    chip.className = `truth-chip ${s}`;
    chip.textContent = `${k}: ${v}`;
    el.truthChipRow.appendChild(chip);
  });
}

function renderNeuralLinks() {
  const center = { x: 700, y: 440 };
  const points = ORGANS.map((o) => ({
    x: (o.x / 100) * 1400,
    y: (o.y / 100) * 880
  }));

  const lines = points
    .map((p) => `<line class="neural-link" x1="${center.x}" y1="${center.y}" x2="${p.x}" y2="${p.y}"></line>`)
    .join("");

  el.neuralLinks.innerHTML = `${lines}`;
}

function renderOrganNodes() {
  el.organNodes.innerHTML = "";
  ORGANS.forEach((organ) => {
    const node = document.createElement("button");
    node.type = "button";
    node.className = `organ-node ${organ.id === activeOrgan ? "is-active" : ""}`;
    node.style.left = `${organ.x}%`;
    node.style.top = `${organ.y}%`;
    node.innerHTML = `<strong>${organ.title}</strong><span>${organ.hint}</span>`;
    node.addEventListener("click", () => {
      activeOrgan = organ.id;
      renderOrganNodes();
      renderCockpit();
    });
    el.organNodes.appendChild(node);
  });
}

function renderWorkFeed() {
  el.workFeed.innerHTML = "";
  workFeed.forEach((item) => {
    const card = document.createElement("article");
    card.className = "feed-item";
    card.innerHTML = `
      <div class="feed-head"><strong>${item[0]}</strong><span>${activeOrgan}</span></div>
      <div class="feed-body">${item[1]}: ${item[2]}</div>
    `;
    el.workFeed.appendChild(card);
  });
}

function renderModuleRows(target, rows) {
  target.innerHTML = "";
  rows.forEach(([name, state]) => {
    const row = document.createElement("div");
    row.className = "module-row";
    row.innerHTML = `<span>${name}</span><span class="state-badge ${stateClass(state)}">${state.toUpperCase()}</span>`;
    target.appendChild(row);
  });
}

function renderActions() {
  el.actionGrid.innerHTML = "";
  ACTIONS.forEach((action) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "action-btn";
    btn.innerHTML = `<strong>${action}</strong><span>${t("actionNote")}</span>`;
    btn.addEventListener("click", () => {
      workFeed.unshift([
        new Date().toLocaleTimeString(locale === "ru" ? "ru-RU" : "en-US", {
          hour: "2-digit",
          minute: "2-digit"
        }),
        `${t("runAction")}: ${action}`,
        `${activeOrgan} cockpit module refreshed`
      ]);
      workFeed.splice(5);
      renderWorkFeed();
    });
    el.actionGrid.appendChild(btn);
  });
}

function renderRawPayload() {
  const payload = {
    active_organ: activeOrgan,
    scope: "IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/**",
    raw_mode: rawVisible ? "visible_secondary" : "hidden_secondary",
    token_layer: {
      json: "TOKENS/design_tokens_mechanicus_console_v0_2.json",
      css: "TOKENS/design_tokens_mechanicus_console_v0_2.css"
    },
    proof_targets: ["1366x768", "1920x1080", "brain_focus", "right_panel_focus", "raw_secondary"]
  };
  el.rawPayload.textContent = JSON.stringify(payload, null, 2);
}

function renderCockpit() {
  el.activeOrganTag.textContent = `${t("state")}: ${t("active")} // ${activeOrgan}`;
  renderModuleRows(el.toolsList, TOOLS[activeOrgan] ?? []);
  renderModuleRows(el.contourList, CONTOUR[activeOrgan] ?? []);
  renderRawPayload();
}

function renderFooter() {
  el.footerStrip.innerHTML = "";
  FOOTER.forEach(([k, v]) => {
    const card = document.createElement("div");
    card.className = "footer-card";
    card.innerHTML = `<span class="k">${t(k)}</span><span class="v">${v}</span>`;
    el.footerStrip.appendChild(card);
  });
}

function renderText() {
  el.truthEyebrow.textContent = t("eyebrow");
  el.mainTitle.textContent = t("title");
  el.missionLine.textContent = t("mission");
  el.brainSectorTitle.textContent = t("brainSectorTitle");
  el.brainSectorNote.textContent = t("brainSectorNote");
  el.brainPulseState.textContent = t("brainPulseState");
  el.workReportTitle.textContent = t("workReportTitle");
  el.cockpitTitle.textContent = `${t("cockpitTitle")} // ${activeOrgan}`;
  el.cockpitNote.textContent = t("cockpitNote");
  el.toolsTitle.textContent = t("toolsTitle");
  el.contourTitle.textContent = t("contourTitle");
  el.actionTitle.textContent = t("actionTitle");
  el.rawModeTitle.textContent = t("rawModeTitle");
  el.langSwitch.textContent = locale === "ru" ? "EN" : "RU";
  el.rawToggle.textContent = rawVisible ? t("rawOn") : t("rawOff");
}

function setRawMode(next) {
  rawVisible = next;
  el.rawMode.classList.toggle("is-hidden", !rawVisible);
  el.rawToggle.textContent = rawVisible ? t("rawOn") : t("rawOff");
  renderRawPayload();
}

function renderAll() {
  renderText();
  renderTruthStrip();
  renderNeuralLinks();
  renderOrganNodes();
  renderWorkFeed();
  renderActions();
  renderCockpit();
  renderFooter();
}

el.langSwitch.addEventListener("click", () => {
  locale = locale === "ru" ? "en" : "ru";
  renderAll();
});

el.rawToggle.addEventListener("click", () => setRawMode(!rawVisible));

setRawMode(false);
renderAll();
