const STORAGE_LANG_KEY = "importantSixOrganCockpitLang";

const I18N = {
  en: {
    kicker: "IMPERIUM NEW GENERATION",
    title: "Sanctum Organ-Centered Cockpit Skeleton",
    subtitle: "Organs are the product. Actions are secondary.",
    taskLabel: "Task",
    truthStatusLabel: "System Truth",
    blockersLabel: "Blockers",
    blockersValue: "No live backend binding in V0.1",
    routeLabel: "Route Status",
    routeValue: "Organ-centered skeleton admitted",
    seedBadge: "SEED_DATA_NOT_PROVEN",
    organsZoneTitle: "Important Six Organ Shell Panels",
    ownerQueueTitle: "Owner Decision Queue",
    ownerQueueFlow:
      "Detected uncertainty -> Owner Verdict Needed -> receipt -> controlled continuation.",
    evidenceTitle: "Evidence / Receipts / Action History",
    evidenceNote: "Every status claim must map to a concrete path or NOT_PROVEN marker.",
    receiptTimelineTitle: "Receipt Timeline",
    historyTitle: "Recent Controlled Events",
    thTime: "Time",
    thOrgan: "Organ",
    thType: "Type",
    thPath: "Path / Marker",
    roleSummary: "Role / Ownership",
    lastEvidence: "Last Evidence",
    warnings: "Warnings / Blockers",
    pendingCount: "Pending Count",
    openDrawer: "Open Secondary Action Drawer",
    closeDrawer: "Close",
    drawerNote: "Secondary layer only. Actions stay read-only in this skeleton.",
    drawerTitle: "Secondary Action Drawer",
    queueJurisdiction: "Jurisdiction",
    queueDecision: "Needed decision",
    queueReceipt: "Receipt path",
    noWarnings: "NONE",
    noEvidence: "NOT_PROVEN",
    noActions: "No secondary actions mapped.",
    readOnlyStub: "READ_ONLY_STUB",
    status_PASS: "PASS",
    status_PASS_WITH_WARNINGS: "PASS_WITH_WARNINGS",
    status_BLOCKED: "BLOCKED",
    status_NOT_PROVEN: "NOT_PROVEN"
  },
  ru: {
    kicker: "IMPERIUM NEW GENERATION",
    title: "Sanctum: каркас cockpit, центрированный на органах",
    subtitle: "Продукт: органы и доказательства. Действия вторичны.",
    taskLabel: "Задача",
    truthStatusLabel: "Системная истина",
    blockersLabel: "Блокеры",
    blockersValue: "В V0.1 нет live backend binding",
    routeLabel: "Статус маршрута",
    routeValue: "Каркас organ-centered допущен",
    seedBadge: "SEED_DATA_NOT_PROVEN",
    organsZoneTitle: "Шесть орган shell-панелей",
    ownerQueueTitle: "Очередь решений Owner",
    ownerQueueFlow:
      "Неопределенность -> Owner Verdict Needed -> receipt -> контролируемое продолжение.",
    evidenceTitle: "Evidence / Receipts / История действий",
    evidenceNote: "Каждое утверждение статуса должно иметь путь доказательства или NOT_PROVEN.",
    receiptTimelineTitle: "Лента receipt-событий",
    historyTitle: "Недавние контролируемые события",
    thTime: "Время",
    thOrgan: "Орган",
    thType: "Тип",
    thPath: "Путь / Маркер",
    roleSummary: "Роль / Владение",
    lastEvidence: "Последнее доказательство",
    warnings: "Предупреждения / Блокеры",
    pendingCount: "Очередь / Pending",
    openDrawer: "Открыть вторичный action drawer",
    closeDrawer: "Закрыть",
    drawerNote: "Только вторичный слой. В этом каркасе действия read-only.",
    drawerTitle: "Вторичный action drawer",
    queueJurisdiction: "Юрисдикция",
    queueDecision: "Требуемое решение",
    queueReceipt: "Путь receipt",
    noWarnings: "НЕТ",
    noEvidence: "NOT_PROVEN",
    noActions: "Вторичные действия не назначены.",
    readOnlyStub: "READ_ONLY_STUB",
    status_PASS: "PASS",
    status_PASS_WITH_WARNINGS: "PASS_WITH_WARNINGS",
    status_BLOCKED: "BLOCKED",
    status_NOT_PROVEN: "NOT_PROVEN"
  }
};

const SEED_STATE = {
  schema_id: "important_six_organ_cockpit_state_v0_1_seed",
  generated_at_utc: "2026-05-24T15:35:00Z",
  claim_boundary: "READ_ONLY_STATIC_SEED_NOT_PROVEN",
  organs: [
    {
      organ_id: "DOCTRINARIUM",
      name: { en: "Doctrinarium", ru: "Doctrinarium" },
      role_summary: {
        en: "Owns doctrine, gate law interpretation, and read-first discipline.",
        ru: "Владеет доктриной, интерпретацией gate-законов и read-first дисциплиной."
      },
      status: "PASS_WITH_WARNINGS",
      last_evidence_path: "IMPERIUM_NEW_GENERATION/DOCTRINARIUM/DOCTRINES/SANCTUM_COCKPIT_RETHINK_SYNTHESIS_V0_1_EN.pdf",
      warnings: [
        "Doctrine consumed; visual contract still static seed.",
        "No runtime truth binding in this skeleton."
      ],
      pending_count: 1,
      secondary_actions: [
        {
          action_id: "DOC_PREFLIGHT_VISUAL_COCKPIT",
          label: { en: "Run doctrine preflight", ru: "Запустить doctrinarium preflight" },
          mode: "READ_ONLY_STUB"
        }
      ]
    },
    {
      organ_id: "OFFICIO_AGENTIS",
      name: { en: "Officio Agentis", ru: "Officio Agentis" },
      role_summary: {
        en: "Owns role contracts, task admission, and stop-condition discipline.",
        ru: "Владеет role contracts, допуском задач и дисциплиной stop-conditions."
      },
      status: "PASS",
      last_evidence_path: "ORGANS/OFFICIO_AGENTIS/RESPONSE_CONTRACTS/AGENT_GATE_ACK_CONTRACT_V0_1.md",
      warnings: [],
      pending_count: 0,
      secondary_actions: [
        {
          action_id: "OFFICIO_ROLE_ACK_CHECK",
          label: { en: "Role ACK consistency check", ru: "Проверка консистентности role ACK" },
          mode: "READ_ONLY_STUB"
        }
      ]
    },
    {
      organ_id: "ADMINISTRATUM",
      name: { en: "Administratum", ru: "Administratum" },
      role_summary: {
        en: "Owns git truth, path scope, status accounting, and report baselines.",
        ru: "Владеет git-truth, границами путей, учетом статусов и отчетными baseline."
      },
      status: "PASS_WITH_WARNINGS",
      last_evidence_path: "IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-VERIFICATION-SPINE-CONVERGENCE-PC-V0_1/FINAL_REPORT.md",
      warnings: ["Commit/push proof for this new skeleton is pending."],
      pending_count: 2,
      secondary_actions: [
        {
          action_id: "ADMIN_GIT_TRUTH_SNAPSHOT",
          label: { en: "Snapshot git truth", ru: "Снять git truth snapshot" },
          mode: "READ_ONLY_STUB"
        }
      ]
    },
    {
      organ_id: "ASTRONOMICON",
      name: { en: "Astronomicon", ru: "Astronomicon" },
      role_summary: {
        en: "Owns route maps, task transfer intents, and roadmap continuity.",
        ru: "Владеет маршрутами, transfer intents задач и непрерывностью roadmap."
      },
      status: "NOT_PROVEN",
      last_evidence_path: "NOT_PROVEN",
      warnings: ["No live transfer queue wired into this V0.1 static cockpit."],
      pending_count: 1,
      secondary_actions: [
        {
          action_id: "ASTRO_ROUTE_PREVIEW",
          label: { en: "Preview route receipts", ru: "Просмотр route receipts" },
          mode: "READ_ONLY_STUB"
        }
      ]
    },
    {
      organ_id: "MECHANICUS",
      name: { en: "Mechanicus", ru: "Mechanicus" },
      role_summary: {
        en: "Owns tools, validators, checker registration, and script preservation.",
        ru: "Владеет инструментами, валидаторами, регистрацией checker и сохранением скриптов."
      },
      status: "PASS",
      last_evidence_path: "IMPERIUM_NEW_GENERATION/MECHANICUS/ARSENAL/README.md",
      warnings: [],
      pending_count: 0,
      secondary_actions: [
        {
          action_id: "MECH_TOOL_REGISTRY_VIEW",
          label: { en: "View tool registry status", ru: "Просмотр статуса registry инструментов" },
          mode: "READ_ONLY_STUB"
        }
      ]
    },
    {
      organ_id: "INQUISITION",
      name: { en: "Inquisition", ru: "Inquisition" },
      role_summary: {
        en: "Owns anti-fake-green, cleanliness audit, and evidence integrity oversight.",
        ru: "Владеет anti-fake-green, аудитом чистоты и контролем целостности evidence."
      },
      status: "PASS_WITH_WARNINGS",
      last_evidence_path: "IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1/tracked_artifact_hygiene_report.json",
      warnings: ["Current cockpit values are static seed and must not imply production green."],
      pending_count: 1,
      secondary_actions: [
        {
          action_id: "INQ_HYGIENE_SCAN_REVIEW",
          label: { en: "Review hygiene scan summary", ru: "Просмотр сводки hygiene scan" },
          mode: "READ_ONLY_STUB"
        }
      ]
    }
  ],
  owner_decision_queue: [
    {
      queue_id: "ODQ-20260524-001",
      organ: "Administratum",
      jurisdiction: "Commit/Push Admission",
      question: {
        en: "Proceed with commit and push after static validation passes?",
        ru: "Продолжить commit и push после PASS статической валидации?"
      },
      required_decision: "APPROVE | HOLD",
      receipt_path: "NOT_PROVEN",
      status: "OWNER_VERDICT_NEEDED"
    },
    {
      queue_id: "ODQ-20260524-002",
      organ: "Inquisition",
      jurisdiction: "Visual truth claim",
      question: {
        en: "Accept PASS_WITH_WARNINGS if only static seed data is displayed?",
        ru: "Допустить PASS_WITH_WARNINGS, если отображены только static seed данные?"
      },
      required_decision: "ACCEPT | REQUIRE_LIVE_BINDING",
      receipt_path: "NOT_PROVEN",
      status: "OWNER_VERDICT_NEEDED"
    },
    {
      queue_id: "ODQ-20260524-003",
      organ: "Doctrinarium",
      jurisdiction: "Cockpit architecture",
      question: {
        en: "Confirm organ-first screen as canonical direction for NewGen Sanctum.",
        ru: "Подтвердить organ-first экран как каноническое направление NewGen Sanctum."
      },
      required_decision: "CONFIRM_CANON_DIRECTION",
      receipt_path: "IMPERIUM_NEW_GENERATION/DOCTRINARIUM/DOCTRINES/SANCTUM_COCKPIT_RETHINK_SYNTHESIS_V0_1_EN.pdf",
      status: "EVIDENCE_LINKED"
    }
  ],
  evidence_timeline: [
    {
      time_utc: "2026-05-24T05:45:18Z",
      organ: "Inquisition",
      type: "Hygiene report",
      path: "IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-COMMIT-36DF325-CLEANUP-HARDENING-PC-V0_1/tracked_artifact_hygiene_report.json",
      status: "PASS"
    },
    {
      time_utc: "2026-05-24T06:42:20Z",
      organ: "Administratum",
      type: "Read-only smoke",
      path: "IMPERIUM_NEW_GENERATION/REPORTS/TASK-NEWGEN-VERIFICATION-SPINE-CONVERGENCE-PC-V0_1/read_only_smoke_report.json",
      status: "PASS"
    },
    {
      time_utc: "2026-05-24T15:35:00Z",
      organ: "Sanctum",
      type: "Cockpit skeleton",
      path: "IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/important_six_organ_cockpit_v0_1.html",
      status: "PASS_WITH_WARNINGS"
    }
  ],
  history_events: [
    {
      event: {
        en: "Truth check completed at expected HEAD with clean worktree.",
        ru: "Truth check завершен на ожидаемом HEAD при чистом worktree."
      }
    },
    {
      event: {
        en: "Doctrinarium cockpit rethink synthesis consumed before UI edits.",
        ru: "Doctrinarium synthesis по cockpit прочитан до UI-правок."
      }
    },
    {
      event: {
        en: "L2 action dashboard kept secondary; new organ-centered shell added separately.",
        ru: "L2 action dashboard оставлен вторичным; добавлен отдельный organ-centered shell."
      }
    }
  ]
};

function langFromQuery() {
  try {
    const value = new URLSearchParams(window.location.search).get("lang");
    if (value === "en" || value === "ru") return value;
  } catch (error) {
    return null;
  }
  return null;
}

const appState = {
  lang: langFromQuery() || localStorage.getItem(STORAGE_LANG_KEY) || "en",
  drawerOpenForOrganId: null
};

function tr(key) {
  const dict = I18N[appState.lang] || I18N.en;
  return dict[key] || key;
}

function localizedText(value) {
  if (typeof value === "string") return value;
  if (!value || typeof value !== "object") return "";
  return value[appState.lang] || value.en || value.ru || "";
}

function statusClass(status) {
  const normalized = String(status || "").toUpperCase();
  if (normalized === "PASS") return "status-pass";
  if (normalized === "PASS_WITH_WARNINGS") return "status-warn";
  return "status-blocked";
}

function statusLabel(status) {
  const normalized = String(status || "NOT_PROVEN").toUpperCase();
  const key = `status_${normalized}`;
  return tr(key);
}

function applyI18n() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    if (!key) return;
    node.textContent = tr(key);
  });
  document.documentElement.lang = appState.lang;
  document.getElementById("langToggleBtn").textContent = appState.lang === "en" ? "RU" : "EN";
}

function renderOrgans() {
  const organGrid = document.getElementById("organGrid");
  organGrid.innerHTML = "";

  for (const organ of SEED_STATE.organs) {
    const node = document.getElementById("organCardTemplate").content.cloneNode(true);
    node.querySelector(".organ-name").textContent = localizedText(organ.name);

    const statusNode = node.querySelector(".organ-status");
    statusNode.textContent = statusLabel(organ.status);
    statusNode.classList.add(statusClass(organ.status));

    node.querySelector(".organ-role").textContent = localizedText(organ.role_summary);
    node.querySelector(".organ-evidence").textContent =
      organ.last_evidence_path && organ.last_evidence_path !== "NOT_PROVEN" ? organ.last_evidence_path : tr("noEvidence");

    const warningsNode = node.querySelector(".organ-warnings");
    warningsNode.textContent = organ.warnings.length > 0 ? organ.warnings.join("\n") : tr("noWarnings");

    node.querySelector(".organ-pending").textContent = String(organ.pending_count);

    const openDrawerBtn = node.querySelector(".open-drawer-btn");
    openDrawerBtn.addEventListener("click", () => openActionDrawerForOrgan(organ.organ_id));
    organGrid.appendChild(node);
  }
}

function renderOwnerQueue() {
  const queueRoot = document.getElementById("ownerQueueList");
  queueRoot.innerHTML = "";

  for (const item of SEED_STATE.owner_decision_queue) {
    const entry = document.createElement("li");
    const questionText = localizedText(item.question);
    entry.innerHTML = [
      `<strong>${item.queue_id}</strong>`,
      `<div>${item.organ}</div>`,
      `<div>${tr("queueJurisdiction")}: ${item.jurisdiction}</div>`,
      `<div>${questionText}</div>`,
      `<div>${tr("queueDecision")}: ${item.required_decision}</div>`,
      `<div>${tr("queueReceipt")}: ${item.receipt_path}</div>`,
      `<div>${item.status}</div>`
    ].join("");
    queueRoot.appendChild(entry);
  }
}

function renderEvidenceTimeline() {
  const body = document.getElementById("evidenceTableBody");
  body.innerHTML = "";

  for (const row of SEED_STATE.evidence_timeline) {
    const trNode = document.createElement("tr");
    trNode.innerHTML = [
      `<td>${row.time_utc}</td>`,
      `<td>${row.organ}</td>`,
      `<td>${row.type}<br /><span class="${statusClass(row.status)}">${statusLabel(row.status)}</span></td>`,
      `<td>${row.path}</td>`
    ].join("");
    body.appendChild(trNode);
  }
}

function renderHistory() {
  const historyRoot = document.getElementById("historyList");
  historyRoot.innerHTML = "";

  for (const row of SEED_STATE.history_events) {
    const item = document.createElement("li");
    item.textContent = localizedText(row.event);
    historyRoot.appendChild(item);
  }
}

function openActionDrawerForOrgan(organId) {
  const organ = SEED_STATE.organs.find((item) => item.organ_id === organId);
  if (!organ) return;

  appState.drawerOpenForOrganId = organId;
  const drawer = document.getElementById("actionDrawer");
  const title = document.getElementById("drawerTitle");
  const actionsList = document.getElementById("drawerActionsList");

  title.textContent = `${tr("drawerTitle")} / ${localizedText(organ.name)}`;
  actionsList.innerHTML = "";

  if (!organ.secondary_actions || organ.secondary_actions.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = tr("noActions");
    actionsList.appendChild(empty);
  } else {
    for (const action of organ.secondary_actions) {
      const entry = document.createElement("li");
      entry.innerHTML = [
        `<strong>${action.action_id}</strong>`,
        `<div>${localizedText(action.label)}</div>`,
        `<div>${tr("readOnlyStub")}: ${action.mode}</div>`
      ].join("");
      actionsList.appendChild(entry);
    }
  }

  drawer.classList.add("open");
  drawer.setAttribute("aria-hidden", "false");
}

function closeDrawer() {
  appState.drawerOpenForOrganId = null;
  const drawer = document.getElementById("actionDrawer");
  drawer.classList.remove("open");
  drawer.setAttribute("aria-hidden", "true");
}

function bindEvents() {
  document.getElementById("langToggleBtn").addEventListener("click", () => {
    appState.lang = appState.lang === "en" ? "ru" : "en";
    localStorage.setItem(STORAGE_LANG_KEY, appState.lang);
    applyI18n();
    renderOrgans();
    renderOwnerQueue();
    renderEvidenceTimeline();
    renderHistory();
    if (appState.drawerOpenForOrganId) {
      openActionDrawerForOrgan(appState.drawerOpenForOrganId);
    }
  });

  document.getElementById("drawerCloseBtn").addEventListener("click", closeDrawer);
}

function boot() {
  applyI18n();
  bindEvents();
  renderOrgans();
  renderOwnerQueue();
  renderEvidenceTimeline();
  renderHistory();
}

window.addEventListener("DOMContentLoaded", boot);
