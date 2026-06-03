const SAFE_MECHANICUS_ORGAN = "MECHANICUS_AGENT";
const COMMAND_SEQUENCE = ["status", "tools", "identity", "check", "where", "pack", "help", "raw", "screenshot", "clear"];
const BRAIN_LINKS = [
  ["ADMINISTRATUM_AGENT", "OFFICIO_AGENTIS_AGENT"],
  ["OFFICIO_AGENTIS_AGENT", "ASTRONOMICON_AGENT"],
  ["ASTRONOMICON_AGENT", "INQUISITION_AGENT"],
  ["INQUISITION_AGENT", "DOCTRINARIUM_AGENT"],
  ["DOCTRINARIUM_AGENT", "MECHANICUS_AGENT"],
  ["MECHANICUS_AGENT", "STRATEGIUM_AGENT"],
  ["STRATEGIUM_AGENT", "SCHOLA_IMPERIALIS_AGENT"],
  ["SCHOLA_IMPERIALIS_AGENT", "CUSTODES"],
  ["CUSTODES", "THRONE"],
  ["THRONE", "MECHANICUS_AGENT"],
];
const BRAIN_LAYOUT = {
  ADMINISTRATUM_AGENT: { x: 16, y: 26 },
  OFFICIO_AGENTIS_AGENT: { x: 31, y: 14 },
  ASTRONOMICON_AGENT: { x: 50, y: 10 },
  INQUISITION_AGENT: { x: 69, y: 14 },
  DOCTRINARIUM_AGENT: { x: 84, y: 26 },
  STRATEGIUM_AGENT: { x: 84, y: 56 },
  SCHOLA_IMPERIALIS_AGENT: { x: 69, y: 74 },
  CUSTODES: { x: 50, y: 82 },
  THRONE: { x: 31, y: 74 },
  MECHANICUS_AGENT: { x: 16, y: 56 },
};
const MAX_ACTIVITY_EVENTS = 120;
const POLL_INTERVAL_MS = 20000;
const SSE_EVENT_TYPES = [
  "heartbeat",
  "state_snapshot",
  "command_started",
  "command_finished",
  "terminal_entry_added",
  "command_failed",
  "error",
];

const I18N = {
  en: {
    missionLine: "Mission: verify truth anchor, maintain honest lanes, and operate a real live transport.",
    workZoneTitle: "WORK ZONE // CURRENT ACTIVITY",
    workZoneNote: "Live event timeline from SSE and operator commands.",
    commandZoneTitle: "COMMAND ZONE // OPERATOR PALETTE",
    commandZoneNote: "Allowlisted controls only. Unknown commands are blocked by backend.",
    toolRegistryTitle: "TOOL REGISTRY // CAPABILITY OVERVIEW",
    tabOverview: "OVERVIEW",
    tabLive: "LIVE",
    tabEvidence: "EVIDENCE",
    tabReports: "REPORTS",
    tabRaw: "RAW JSON",
    tabActionHistory: "ACTION HISTORY",
    overviewTitle: "SANCTUM OVERVIEW // BRAIN SHELL",
    liveTitle: "LIVE OPERATOR CONSOLE",
    rawStreamTitle: "RAW / TECHNICAL MODE",
    rawModeOn: "RAW MODE ON",
    rawModeOff: "RAW MODE OFF",
    panelIdle: "Panel state: waiting for organ selection.",
    panelOpenedMechanicus: "Mechanicus operator panel opened from brain node click.",
    panelOpenedPlaceholder: "Placeholder organ selected. Operator panel remains Mechanicus-only.",
    panelOpenedLocked: "Locked organ selected. Operator panel remains inaccessible for locked lanes.",
    terminalPrompt: "Command",
    terminalPlaceholder: "status | tools | identity | check | where | pack | help | raw | screenshot | clear",
    terminalRun: "Run",
    terminalClear: "Clear",
    terminalCleared: "Terminal view cleared locally.",
    placeholderFocus: "This organ is placeholder in V0.4.",
    lockedFocus: "This organ is locked in V0.4.",
    viewportMissing: "No screenshot found. Run screenshot command and refresh.",
    reportsSummary: "Reports and paths",
    rawPreview: "Raw JSON Preview",
    actionHistoryTitle: "Executed/Blocked Actions",
    emptyList: "None",
    unknown: "UNKNOWN",
    unproven: "UNPROVEN",
    latestEvidence: "Latest evidence",
    latestReport: "Latest report",
    latestScreenshot: "Latest screenshot",
    latestReceipt: "Latest receipt",
    freshness: "Freshness",
    connected: "Connected",
    placeholders: "Placeholders",
    locked: "Locked",
    warnings: "Warnings",
    errors: "Errors",
    blockers: "Blockers",
    visualStatus: "Visual status",
    renderer: "Renderer",
    commandsCount: "Commands",
    sseStatus: "SSE",
    worktree: "Worktree",
    head: "HEAD",
    status: "status",
    source: "source",
    safety: "safety",
    exitCode: "exit",
    duration: "duration",
    feedIdle: "No live events yet.",
    bottomReport: "LATEST REPORT",
    bottomReceipt: "LATEST RECEIPT",
    bottomEvent: "EVENT SUMMARY",
    bottomHealth: "COMMAND HEALTH",
    unavailable: "Unavailable",
    registered: "Registered",
    available: "Available",
    missing: "Missing",
    counterWarnings: "Warnings",
    counterErrors: "Errors",
    notConnected: "SSE DISABLED",
    fallback: "SSE FALLBACK",
    connectedLabel: "SSE CONNECTED",
    errorLabel: "SSE ERROR",
    eventType: "event",
    commandLabel: "command",
  },
  ru: {
    missionLine: "Миссия: закрепить truth-якорь, сохранить честность линий и держать реальный live-транспорт.",
    workZoneTitle: "WORK ZONE // CURRENT ACTIVITY",
    workZoneNote: "Живая лента событий из SSE и операторских команд.",
    commandZoneTitle: "COMMAND ZONE // OPERATOR PALETTE",
    commandZoneNote: "Только allowlisted-контролы. Неизвестные команды блокируются backend.",
    toolRegistryTitle: "TOOL REGISTRY // CAPABILITY OVERVIEW",
    tabOverview: "OVERVIEW",
    tabLive: "LIVE",
    tabEvidence: "EVIDENCE",
    tabReports: "REPORTS",
    tabRaw: "RAW JSON",
    tabActionHistory: "ACTION HISTORY",
    overviewTitle: "SANCTUM OVERVIEW // BRAIN SHELL",
    liveTitle: "LIVE OPERATOR CONSOLE",
    rawStreamTitle: "RAW / TECHNICAL MODE",
    rawModeOn: "RAW MODE ON",
    rawModeOff: "RAW MODE OFF",
    panelIdle: "Состояние панели: ожидание выбора органа.",
    panelOpenedMechanicus: "Панель Mechanicus открыта по клику на узел мозга.",
    panelOpenedPlaceholder: "Выбран placeholder-орган. Рабочая панель доступна только для Mechanicus.",
    panelOpenedLocked: "Выбран locked-орган. Рабочая панель для locked-линий недоступна.",
    terminalPrompt: "Команда",
    terminalPlaceholder: "status | tools | identity | check | where | pack | help | raw | screenshot | clear",
    terminalRun: "Запуск",
    terminalClear: "Очистить",
    terminalCleared: "Терминальный поток очищен локально.",
    placeholderFocus: "Этот орган в placeholder-режиме V0.4.",
    lockedFocus: "Этот орган заблокирован в V0.4.",
    viewportMissing: "Скриншот не найден. Выполните screenshot и обновите данные.",
    reportsSummary: "Отчеты и пути",
    rawPreview: "Просмотр Raw JSON",
    actionHistoryTitle: "История действий (выполнено/заблокировано)",
    emptyList: "Нет",
    unknown: "UNKNOWN",
    unproven: "UNPROVEN",
    latestEvidence: "Последний evidence",
    latestReport: "Последний отчет",
    latestScreenshot: "Последний скриншот",
    latestReceipt: "Последний receipt",
    freshness: "Свежесть",
    connected: "Подключено",
    placeholders: "Placeholder",
    locked: "Locked",
    warnings: "Предупреждения",
    errors: "Ошибки",
    blockers: "Блокеры",
    visualStatus: "Визуальный статус",
    renderer: "Рендерер",
    commandsCount: "Команд",
    sseStatus: "SSE",
    worktree: "Дерево",
    head: "HEAD",
    status: "статус",
    source: "источник",
    safety: "безопасность",
    exitCode: "код",
    duration: "время",
    feedIdle: "Событий SSE пока нет.",
    bottomReport: "ПОСЛЕДНИЙ ОТЧЕТ",
    bottomReceipt: "ПОСЛЕДНИЙ RECEIPT",
    bottomEvent: "СВОДКА СОБЫТИЙ",
    bottomHealth: "ЗДОРОВЬЕ КОМАНД",
    unavailable: "Недоступно",
    registered: "Зарегистрировано",
    available: "Доступно",
    missing: "Отсутствует",
    counterWarnings: "Warnings",
    counterErrors: "Errors",
    notConnected: "SSE DISABLED",
    fallback: "SSE FALLBACK",
    connectedLabel: "SSE CONNECTED",
    errorLabel: "SSE ERROR",
    eventType: "event",
    commandLabel: "команда",
  },
};

let locale = "ru";
let selectedOrganId = SAFE_MECHANICUS_ORGAN;
let activeTab = "overview";
let stateCache = null;
let actionHistoryCache = [];
let terminalHistoryCache = [];
let actionsCache = [];
let terminalAllowlist = [];
let activityEvents = [];
let refreshTimer = null;
let sse = null;
let sseEverConnected = false;
let sseStatusCode = "fallback";
let rawModeVisible = false;
let panelOpenStateMessage = "";
const eventCounters = {};

const el = {
  mainTitle: document.getElementById("mainTitle"),
  missionLine: document.getElementById("missionLine"),
  topMetrics: document.getElementById("topMetrics"),
  sseStatusPill: document.getElementById("sseStatusPill"),
  langSwitch: document.getElementById("langSwitch"),
  workZoneTitle: document.getElementById("workZoneTitle"),
  workZoneNote: document.getElementById("workZoneNote"),
  activityFeed: document.getElementById("activityFeed"),
  tabOverview: document.getElementById("tabOverview"),
  tabLive: document.getElementById("tabLive"),
  tabEvidence: document.getElementById("tabEvidence"),
  tabReports: document.getElementById("tabReports"),
  tabRaw: document.getElementById("tabRaw"),
  tabActionHistory: document.getElementById("tabActionHistory"),
  tabs: Array.from(document.querySelectorAll(".tab")),
  panels: Array.from(document.querySelectorAll(".tab-panel")),
  overviewOrganTitle: document.getElementById("overviewOrganTitle"),
  brainLinksSvg: document.getElementById("brainLinksSvg"),
  brainCoreZone: document.getElementById("brainCoreZone"),
  organGrid: document.getElementById("organGrid"),
  brainLegend: document.getElementById("brainLegend"),
  truthBlock: document.getElementById("truthBlock"),
  liveHeaderTitle: document.getElementById("liveHeaderTitle"),
  liveHeaderMeta: document.getElementById("liveHeaderMeta"),
  livePanelOpenState: document.getElementById("livePanelOpenState"),
  rawModeToggleBtn: document.getElementById("rawModeToggleBtn"),
  liveColumns: document.getElementById("liveColumns"),
  rawStreamWrap: document.getElementById("rawStreamWrap"),
  liveStatusChips: document.getElementById("liveStatusChips"),
  liveOperatorStream: document.getElementById("liveOperatorStream"),
  rawStreamTitle: document.getElementById("rawStreamTitle"),
  rawTerminalStream: document.getElementById("rawTerminalStream"),
  evidenceViewportHeader: document.getElementById("evidenceViewportHeader"),
  evidenceViewportImage: document.getElementById("evidenceViewportImage"),
  evidenceViewportEmpty: document.getElementById("evidenceViewportEmpty"),
  reportsPanel: document.getElementById("reportsPanel"),
  rawPanel: document.getElementById("rawPanel"),
  actionHistoryPanel: document.getElementById("actionHistoryPanel"),
  commandZoneTitle: document.getElementById("commandZoneTitle"),
  commandZoneNote: document.getElementById("commandZoneNote"),
  commandGrid: document.getElementById("commandGrid"),
  terminalForm: document.getElementById("terminalForm"),
  terminalPromptLabel: document.getElementById("terminalPromptLabel"),
  terminalInput: document.getElementById("terminalInput"),
  terminalRunBtn: document.getElementById("terminalRunBtn"),
  terminalClearBtn: document.getElementById("terminalClearBtn"),
  toolRegistryTitle: document.getElementById("toolRegistryTitle"),
  toolCounters: document.getElementById("toolCounters"),
  toolRows: document.getElementById("toolRows"),
  bottomReport: document.getElementById("bottomReport"),
  bottomReceipt: document.getElementById("bottomReceipt"),
  bottomEventSummary: document.getElementById("bottomEventSummary"),
  bottomCommandHealth: document.getElementById("bottomCommandHealth"),
};

function t(key) {
  return (I18N[locale] && I18N[locale][key]) || key;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function truthValue(value, fallbackKey = "unknown") {
  if (value === null || value === undefined || value === "") {
    return t(fallbackKey);
  }
  return String(value);
}

function shortValue(value, max = 140) {
  const text = truthValue(value);
  return text.length <= max ? text : `${text.slice(0, max - 3)}...`;
}

function setActiveTab(tabId) {
  activeTab = tabId;
  el.tabs.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.tab === tabId);
  });
  el.panels.forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.panel === tabId);
  });
}

function setRawMode(visible) {
  rawModeVisible = Boolean(visible);
  if (el.rawStreamWrap) {
    el.rawStreamWrap.classList.toggle("is-hidden", !rawModeVisible);
  }
  if (el.liveColumns) {
    el.liveColumns.classList.toggle("raw-hidden", !rawModeVisible);
  }
  if (el.rawModeToggleBtn) {
    el.rawModeToggleBtn.textContent = rawModeVisible ? t("rawModeOn") : t("rawModeOff");
  }
}

function setPanelOpenStateByOrgan(organ) {
  if (!organ) {
    panelOpenStateMessage = t("panelIdle");
    return;
  }
  if (organ.id === SAFE_MECHANICUS_ORGAN) {
    panelOpenStateMessage = t("panelOpenedMechanicus");
    setActiveTab("live");
    return;
  }
  if (organ.status === "LOCKED") {
    panelOpenStateMessage = t("panelOpenedLocked");
    return;
  }
  panelOpenStateMessage = t("panelOpenedPlaceholder");
}

function formatTime(timestamp) {
  if (!timestamp) {
    return "";
  }
  const part = String(timestamp).split("T")[1] || String(timestamp);
  return part.replace("Z", "");
}

function localLabel(organ) {
  return locale === "ru" ? organ.label_ru : organ.label_en;
}

function organTruthMode(status) {
  if (status === "CONNECTED") {
    return "REAL";
  }
  if (status === "LOCKED") {
    return "LOCKED";
  }
  return "PLACEHOLDER";
}

function statusClass(status) {
  const value = String(status || "UNKNOWN").toUpperCase();
  if (value === "PASS" || value === "CONNECTED") {
    return "status-pass";
  }
  if (value === "WARN" || value === "PLACEHOLDER") {
    return "status-warn";
  }
  return "status-error";
}

function linkClassByStatus(statusA, statusB) {
  if (statusA === "CONNECTED" || statusB === "CONNECTED") {
    return "real";
  }
  if (statusA === "LOCKED" || statusB === "LOCKED") {
    return "locked";
  }
  return "placeholder";
}

function incrementEventCounter(type) {
  const key = String(type || "unknown");
  eventCounters[key] = (eventCounters[key] || 0) + 1;
}

function pushActivityEvent(event) {
  const normalized = {
    timestamp_utc: event.timestamp_utc || new Date().toISOString(),
    event_type: event.event_type || "unknown",
    source: event.source || "unknown",
    truth_status: event.truth_status || "UNKNOWN",
    action_id: event.action_id || null,
    command: event.command || null,
    details: event.details || {},
  };
  activityEvents.unshift(normalized);
  if (activityEvents.length > MAX_ACTIVITY_EVENTS) {
    activityEvents = activityEvents.slice(0, MAX_ACTIVITY_EVENTS);
  }
}

function hydrateActivityFromTerminalHistory() {
  if (activityEvents.length || !terminalHistoryCache.length) {
    return;
  }
  terminalHistoryCache.slice(0, 40).forEach((row) => {
    pushActivityEvent({
      timestamp_utc: row.finished_at_utc || row.started_at_utc,
      event_type: "terminal_entry_added",
      source: row.source || "terminal_manual",
      truth_status: row.status || "UNKNOWN",
      action_id: row.action_id || null,
      command: row.command || null,
      details: {
        exit_code: row.exit_code,
        duration_ms: row.duration_ms,
        safety: row.safety,
      },
    });
  });
}

function setSseStatus(code) {
  sseStatusCode = code;
  el.sseStatusPill.classList.remove("sse-connected", "sse-fallback", "sse-error", "sse-disabled");
  if (code === "connected") {
    el.sseStatusPill.classList.add("sse-connected");
    el.sseStatusPill.textContent = t("connectedLabel");
    return;
  }
  if (code === "error") {
    el.sseStatusPill.classList.add("sse-error");
    el.sseStatusPill.textContent = t("errorLabel");
    return;
  }
  if (code === "disabled") {
    el.sseStatusPill.classList.add("sse-disabled");
    el.sseStatusPill.textContent = t("notConnected");
    return;
  }
  el.sseStatusPill.classList.add("sse-fallback");
  el.sseStatusPill.textContent = t("fallback");
}

function scheduleRefresh(delayMs = 600) {
  if (refreshTimer) {
    window.clearTimeout(refreshTimer);
  }
  refreshTimer = window.setTimeout(() => {
    refreshAll("sse-event");
  }, delayMs);
}

function handleSsePayload(payload) {
  if (!payload || typeof payload !== "object") {
    return;
  }
  incrementEventCounter(payload.event_type);
  pushActivityEvent(payload);
  renderActivityFeed();
  renderBottomStrip();

  if (
    payload.event_type === "command_finished" ||
    payload.event_type === "command_failed" ||
    payload.event_type === "terminal_entry_added" ||
    payload.event_type === "state_snapshot"
  ) {
    scheduleRefresh();
  }
}

function parseSseEventData(event) {
  try {
    return JSON.parse(event.data);
  } catch (_) {
    return null;
  }
}

function connectSse() {
  if (!window.EventSource) {
    setSseStatus("disabled");
    return;
  }

  if (sse) {
    sse.close();
    sse = null;
  }

  try {
    sse = new EventSource("/api/events");
  } catch (_) {
    setSseStatus("fallback");
    return;
  }

  setSseStatus("fallback");
  sse.onopen = () => {
    sseEverConnected = true;
    setSseStatus("connected");
  };

  sse.onerror = () => {
    setSseStatus(sseEverConnected ? "error" : "fallback");
  };

  SSE_EVENT_TYPES.forEach((eventType) => {
    sse.addEventListener(eventType, (event) => {
      const payload = parseSseEventData(event);
      if (payload) {
        handleSsePayload(payload);
      }
    });
  });
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path}_HTTP_${response.status}`);
  }
  return response.json();
}

async function refreshAll(reason = "poll") {
  try {
    const [state, actionsPayload, actionHistoryPayload, terminalHistoryPayload] = await Promise.all([
      fetchJson("/api/state"),
      fetchJson("/api/actions"),
      fetchJson("/api/actions/history"),
      fetchJson("/api/terminal/history"),
    ]);

    stateCache = state;
    actionsCache = actionsPayload.actions || [];
    actionHistoryCache = actionHistoryPayload.history || [];
    terminalHistoryCache = terminalHistoryPayload.history || [];
    terminalAllowlist = terminalHistoryPayload.allowlist || [];

    if (!(state.organs || []).some((organ) => organ.id === selectedOrganId)) {
      selectedOrganId = SAFE_MECHANICUS_ORGAN;
    }

    hydrateActivityFromTerminalHistory();
    renderAll(reason);
  } catch (error) {
    const text = `${t("eventType")}: ${String(error)}`;
    el.liveHeaderMeta.textContent = text;
    setSseStatus("error");
  }
}

async function runTerminalCommand(commandText) {
  const command = String(commandText || "").trim();
  if (!command) {
    return;
  }

  try {
    await fetch("/api/terminal/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ organ: SAFE_MECHANICUS_ORGAN, command }),
    });
    if (command.toLowerCase() === "clear") {
      terminalHistoryCache = [];
      activityEvents = [];
      el.liveHeaderMeta.textContent = t("terminalCleared");
    }
    await refreshAll("command");
    setActiveTab("live");
  } catch (error) {
    el.liveHeaderMeta.textContent = `${t("eventType")}: ${String(error)}`;
  }
}

function renderStaticLabels() {
  el.missionLine.textContent = t("missionLine");
  el.workZoneTitle.textContent = t("workZoneTitle");
  el.workZoneNote.textContent = t("workZoneNote");
  el.commandZoneTitle.textContent = t("commandZoneTitle");
  el.commandZoneNote.textContent = t("commandZoneNote");
  el.toolRegistryTitle.textContent = t("toolRegistryTitle");
  el.tabOverview.textContent = t("tabOverview");
  el.tabLive.textContent = t("tabLive");
  el.tabEvidence.textContent = t("tabEvidence");
  el.tabReports.textContent = t("tabReports");
  el.tabRaw.textContent = t("tabRaw");
  el.tabActionHistory.textContent = t("tabActionHistory");
  el.overviewOrganTitle.textContent = t("overviewTitle");
  el.liveHeaderTitle.textContent = t("liveTitle");
  el.livePanelOpenState.textContent = panelOpenStateMessage || t("panelIdle");
  el.rawStreamTitle.textContent = t("rawStreamTitle");
  el.terminalPromptLabel.textContent = t("terminalPrompt");
  el.terminalInput.placeholder = t("terminalPlaceholder");
  el.terminalRunBtn.textContent = t("terminalRun");
  el.terminalClearBtn.textContent = t("terminalClear");
  el.langSwitch.textContent = locale === "ru" ? "EN" : "RU";
  setRawMode(rawModeVisible);
  setSseStatus(sseStatusCode);
}

function renderTopBar(state) {
  const globalTruth = state.global_truth || {};
  const metrics = [
    `${t("head")}: ${shortValue(state.repo?.head, 20)}`,
    `${t("worktree")}: ${truthValue(state.repo?.worktree_state)}`,
    `${t("visualStatus")}: ${truthValue(state.viewport?.mode)}`,
    `${t("renderer")}: DOM/CSS`,
    `${t("commandsCount")}: ${terminalAllowlist.length || actionsCache.length || 0}`,
    `${t("warnings")}: ${truthValue(globalTruth.warnings_count, "unknown")}`,
    `${t("errors")}: ${truthValue(globalTruth.errors_count, "unknown")}`,
    `${t("blockers")}: ${truthValue(globalTruth.blockers_count, "unknown")}`,
  ];
  el.topMetrics.innerHTML = metrics.map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("");
}

function renderActivityFeed() {
  if (!activityEvents.length) {
    el.activityFeed.innerHTML = `<div class="feed-empty">${escapeHtml(t("feedIdle"))}</div>`;
    return;
  }

  const rows = activityEvents.slice(0, 60);
  el.activityFeed.innerHTML = rows
    .map((item) => {
      const commandInfo = item.command ? ` :: ${item.command}` : "";
      const title = `${item.event_type}${commandInfo}`;
      const status = truthValue(item.truth_status, "unknown");
      const details = [
        `${t("source")}: ${truthValue(item.source)}`,
        `${t("commandLabel")}: ${truthValue(item.action_id || item.command || "-", "unknown")}`,
        `${t("status")}: ${status}`,
      ];
      if (item.details && typeof item.details === "object") {
        if (item.details.safety) {
          details.push(`${t("safety")}: ${item.details.safety}`);
        }
        if (item.details.exit_code !== null && item.details.exit_code !== undefined) {
          details.push(`${t("exitCode")}: ${item.details.exit_code}`);
        }
        if (item.details.duration_ms !== null && item.details.duration_ms !== undefined) {
          details.push(`${t("duration")}: ${item.details.duration_ms}ms`);
        }
      }
      return `
      <article class="feed-entry">
        <div class="feed-top">
          <span class="feed-title">${escapeHtml(title)}</span>
          <span class="feed-time">${escapeHtml(formatTime(item.timestamp_utc))}</span>
        </div>
        <span class="feed-badge ${escapeHtml(statusClass(status))}">${escapeHtml(status)}</span>
        <div class="feed-details">${escapeHtml(details.join(" | "))}</div>
      </article>`;
    })
    .join("");
}

function renderBrainCore(state) {
  const truth = state.global_truth || {};
  const connected = truth.connected_organs_count ?? t("unknown");
  const placeholders = truth.placeholders_count ?? t("unknown");
  const locked = truth.locked_count ?? t("unknown");
  const active = state.server?.active_organ || SAFE_MECHANICUS_ORGAN;
  el.brainCoreZone.innerHTML = `
    <div class="core-title">NEURAL CORE</div>
    <div class="core-subtitle">${escapeHtml(state.generated_at_utc || "")}</div>
    <div class="core-row">
      <span class="core-chip">${escapeHtml(t("connected"))}: ${escapeHtml(String(connected))}</span>
      <span class="core-chip">${escapeHtml(t("placeholders"))}: ${escapeHtml(String(placeholders))}</span>
      <span class="core-chip">${escapeHtml(t("locked"))}: ${escapeHtml(String(locked))}</span>
    </div>
    <div class="core-subtitle">ACTIVE ANCHOR: ${escapeHtml(active)}</div>
  `;
}

function renderBrainLinks(state) {
  const organMap = {};
  (state.organs || []).forEach((organ) => {
    organMap[organ.id] = organ;
  });
  const centerX = 50;
  const centerY = 48;
  const paths = BRAIN_LINKS.map(([fromId, toId], idx) => {
    const from = BRAIN_LAYOUT[fromId];
    const to = BRAIN_LAYOUT[toId];
    if (!from || !to) {
      return "";
    }
    const statusA = organMap[fromId]?.status || "UNKNOWN";
    const statusB = organMap[toId]?.status || "UNKNOWN";
    const cls = linkClassByStatus(statusA, statusB);
    const x1 = from.x * 10;
    const y1 = from.y * 5.6;
    const x2 = to.x * 10;
    const y2 = to.y * 5.6;
    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;
    const pull = idx % 2 === 0 ? 24 : -24;
    const cx = midX + (centerX * 10 - midX) * 0.13;
    const cy = midY + (centerY * 5.6 - midY) * 0.13 + pull;
    return `<path class="brain-link ${cls}" d="M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}" />`;
  })
    .filter(Boolean)
    .join("");
  el.brainLinksSvg.innerHTML = paths;
}

function renderOrgans(state) {
  const organs = state.organs || [];
  renderBrainCore(state);
  renderBrainLinks(state);
  el.organGrid.innerHTML = organs
    .map((organ) => {
      const active = organ.id === selectedOrganId ? "active" : "";
      const layout = BRAIN_LAYOUT[organ.id] || { x: 50, y: 50 };
      return `
      <article class="organ-card ${active}" data-organ-id="${escapeHtml(organ.id)}" style="--x:${layout.x}%; --y:${layout.y}%;">
        <div class="organ-name">${escapeHtml(localLabel(organ))}</div>
        <div class="organ-id">${escapeHtml(organ.id)}</div>
        <span class="feed-badge ${escapeHtml(statusClass(organ.status))}">${escapeHtml(organ.status)}</span>
        <div class="organ-mode">${escapeHtml(organTruthMode(organ.status))}</div>
      </article>`;
    })
    .join("");

  el.organGrid.querySelectorAll(".organ-card").forEach((card) => {
    card.addEventListener("click", () => {
      const selectedId = card.dataset.organId || SAFE_MECHANICUS_ORGAN;
      selectedOrganId = selectedId;
      const organ = (state.organs || []).find((item) => item.id === selectedId) || null;
      setPanelOpenStateByOrgan(organ);
      if (selectedId === SAFE_MECHANICUS_ORGAN) {
        setRawMode(false);
      }
      renderOrgans(state);
      renderTruth(state);
      renderLivePanel(state);
      renderEvidencePanel(state);
      renderReportsPanel(state);
      renderRawPanel(state);
    });
  });
}

function renderBrainLegend() {
  el.brainLegend.innerHTML = `
    <div>REAL / PLACEHOLDER / LOCKED routing remains truth-bound to backend state. Unknown values are shown as ${escapeHtml(
      t("unknown")
    )}.</div>
  `;
}

function renderTruth(state) {
  const truth = state.global_truth || {};
  const matrix = truth.real_vs_placeholder || {};
  const rows = [
    [t("connected"), truth.connected_organs_count],
    [t("placeholders"), truth.placeholders_count],
    [t("locked"), truth.locked_count],
    [t("warnings"), truth.warnings_count],
    [t("errors"), truth.errors_count],
    [t("blockers"), truth.blockers_count],
    [t("latestEvidence"), shortValue(truth.latest_evidence_path)],
    [t("latestReport"), shortValue(truth.latest_report_path)],
    [t("latestScreenshot"), shortValue(truth.latest_screenshot_path)],
    [t("freshness"), shortValue(truth.freshness_reference)],
    [
      "LANES",
      `real=[${(matrix.real || []).join(", ")}] placeholder=[${(matrix.placeholder || []).join(", ")}] locked=[${(
        matrix.locked || []
      ).join(", ")}]`,
    ],
  ];
  el.truthBlock.innerHTML = rows
    .map(
      ([key, value]) => `
      <div class="truth-item">
        <div class="truth-key">${escapeHtml(String(key))}</div>
        <div class="truth-value">${escapeHtml(truthValue(value))}</div>
      </div>`
    )
    .join("");
}

function renderLivePanel(state) {
  const latest = terminalHistoryCache[0];
  const latestMeta = latest
    ? `${t("status")}: ${latest.status} | ${t("safety")}: ${latest.safety} | ${t("exitCode")}: ${
        latest.exit_code
      } | ${t("duration")}: ${latest.duration_ms}ms`
    : `${t("status")}: ${t("unknown")} | ${t("commandsCount")}: ${terminalAllowlist.length}`;
  el.liveHeaderMeta.textContent = `${latestMeta} | ${t("sseStatus")}: ${el.sseStatusPill.textContent}`;
  el.livePanelOpenState.textContent = panelOpenStateMessage || t("panelIdle");
  setRawMode(rawModeVisible);

  const chips = [
    `${t("head")}: ${shortValue(state.repo?.head, 18)}`,
    `${t("visualStatus")}: ${truthValue(state.viewport?.mode)}`,
    `${t("warnings")}: ${truthValue(state.global_truth?.warnings_count)}`,
    `${t("errors")}: ${truthValue(state.global_truth?.errors_count)}`,
    `${t("blockers")}: ${truthValue(state.global_truth?.blockers_count)}`,
  ];
  el.liveStatusChips.innerHTML = chips.map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("");

  const rows = terminalHistoryCache.slice(0, 32);
  if (!rows.length) {
    el.liveOperatorStream.innerHTML = `<div class="operator-empty">${escapeHtml(t("feedIdle"))}</div>`;
    el.rawTerminalStream.textContent = "";
    return;
  }

  el.liveOperatorStream.innerHTML = rows
    .map((row) => {
      const status = String(row.status || "UNKNOWN").toUpperCase();
      const header = `${row.organ || SAFE_MECHANICUS_ORGAN} :: ${row.command || row.action_id || "-"}`;
      const meta = [
        `${t("source")}: ${row.source || "-"}`,
        `${t("safety")}: ${row.safety || "-"}`,
        `${t("exitCode")}: ${row.exit_code ?? "-"}`,
        `${t("duration")}: ${row.duration_ms ?? 0}ms`,
        formatTime(row.finished_at_utc || row.started_at_utc),
      ].join(" | ");
      const summary = row.stderr_summary || row.stdout_summary || "";
      return `
      <article class="op-entry">
        <div class="op-top">
          <span>${escapeHtml(header)}</span>
          <span class="feed-badge ${escapeHtml(statusClass(status))}">${escapeHtml(status)}</span>
        </div>
        <div class="op-meta">${escapeHtml(meta)}</div>
        <div class="op-meta">${escapeHtml(summary)}</div>
      </article>`;
    })
    .join("");

  const rawLines = rows
    .map((row) => {
      const stamp = formatTime(row.finished_at_utc || row.started_at_utc);
      const command = row.command || row.action_id || "-";
      const status = row.status || "UNKNOWN";
      const out = row.stdout_summary || "";
      const err = row.stderr_summary || "";
      return `[${stamp}] ${status} ${command}\nstdout: ${out}\nstderr: ${err}\n`;
    })
    .join("\n");
  el.rawTerminalStream.textContent = rawLines;
}

function renderEvidencePanel(state) {
  const selected = (state.organs || []).find((organ) => organ.id === selectedOrganId);
  if (!selected) {
    return;
  }
  el.evidenceViewportHeader.textContent = `${selected.id} :: ${selected.status}`;
  if (selected.id !== SAFE_MECHANICUS_ORGAN) {
    el.evidenceViewportImage.style.display = "none";
    el.evidenceViewportEmpty.style.display = "block";
    el.evidenceViewportEmpty.textContent = selected.status === "LOCKED" ? t("lockedFocus") : t("placeholderFocus");
    return;
  }

  const shots = state.mechanicus?.latest_screenshots || [];
  if (!shots.length) {
    el.evidenceViewportImage.style.display = "none";
    el.evidenceViewportEmpty.style.display = "block";
    el.evidenceViewportEmpty.textContent = t("viewportMissing");
    return;
  }

  const url = `/api/mechanicus/screenshot/latest?ts=${encodeURIComponent(state.generated_at_utc || Date.now())}`;
  el.evidenceViewportImage.style.display = "block";
  el.evidenceViewportEmpty.style.display = "none";
  el.evidenceViewportImage.src = url;
  el.evidenceViewportImage.onerror = () => {
    el.evidenceViewportImage.style.display = "none";
    el.evidenceViewportEmpty.style.display = "block";
    el.evidenceViewportEmpty.textContent = t("viewportMissing");
  };
}

function listToHtml(items) {
  if (!items || !items.length) {
    return `<li>${escapeHtml(t("emptyList"))}</li>`;
  }
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderReportsPanel(state) {
  const selected = (state.organs || []).find((organ) => organ.id === selectedOrganId);
  if (!selected || selected.id !== SAFE_MECHANICUS_ORGAN) {
    const text = selected && selected.status === "LOCKED" ? t("lockedFocus") : t("placeholderFocus");
    el.reportsPanel.innerHTML = `<p>${escapeHtml(text)}</p>`;
    return;
  }

  const truth = state.global_truth || {};
  const mechanicus = state.mechanicus || {};
  const reportItems = (mechanicus.latest_reports || [])
    .slice(0, 8)
    .map((item) => `${item.task_id} :: ${item.path_repo_relative || item.path}`);
  const screenshotItems = (mechanicus.latest_screenshots || [])
    .slice(0, 8)
    .map((item) => `${item.file_name} :: ${item.path_repo_relative || item.path}`);
  const receiptItems = (mechanicus.latest_receipts || []).slice(0, 8);

  el.reportsPanel.innerHTML = `
    <h3>${escapeHtml(t("reportsSummary"))}</h3>
    <p><strong>${escapeHtml(t("latestEvidence"))}:</strong> ${escapeHtml(truthValue(truth.latest_evidence_path))}</p>
    <p><strong>${escapeHtml(t("latestReport"))}:</strong> ${escapeHtml(truthValue(truth.latest_report_path))}</p>
    <p><strong>${escapeHtml(t("latestScreenshot"))}:</strong> ${escapeHtml(truthValue(truth.latest_screenshot_path))}</p>
    <p><strong>${escapeHtml("Reports")}</strong></p>
    <ul>${listToHtml(reportItems)}</ul>
    <p><strong>${escapeHtml("Screenshots")}</strong></p>
    <ul>${listToHtml(screenshotItems)}</ul>
    <p><strong>${escapeHtml("Receipts")}</strong></p>
    <ul>${listToHtml(receiptItems)}</ul>
  `;
}

function renderRawPanel(state) {
  const selected = (state.organs || []).find((organ) => organ.id === selectedOrganId);
  const payload =
    selected && selected.id === SAFE_MECHANICUS_ORGAN
      ? {
          server: state.server || {},
          repo: state.repo || {},
          viewport: state.viewport || {},
          global_truth: state.global_truth || {},
          tool_registry: state.mechanicus?.tool_registry || {},
        }
      : { selected_organ: selected || null };
  const raw = JSON.stringify(payload, null, 2);
  el.rawPanel.innerHTML = `
    <h3>${escapeHtml(t("rawPreview"))}</h3>
    <pre>${escapeHtml(raw.length > 18000 ? `${raw.slice(0, 18000)}\n...<truncated>` : raw)}</pre>
  `;
}

function renderActionHistoryPanel() {
  const rows = actionHistoryCache.slice(0, 40);
  if (!rows.length) {
    el.actionHistoryPanel.innerHTML = `<div class="operator-empty">${escapeHtml(t("emptyList"))}</div>`;
    return;
  }
  el.actionHistoryPanel.innerHTML = `
    <h3>${escapeHtml(t("actionHistoryTitle"))}</h3>
    ${rows
      .map((row) => {
        const status = String(row.status || "UNKNOWN").toUpperCase();
        const label = `${row.action_id || "-"} :: ${row.command || "-"}`;
        const meta = [
          `${t("source")}: ${row.source || "-"}`,
          `${t("safety")}: ${row.safety || "-"}`,
          `${t("exitCode")}: ${row.exit_code ?? "-"}`,
          formatTime(row.finished_at_utc || row.started_at_utc),
        ].join(" | ");
        return `
        <div class="history-card">
          <div class="history-top">
            <span>${escapeHtml(label)}</span>
            <span class="feed-badge ${escapeHtml(statusClass(status))}">${escapeHtml(status)}</span>
          </div>
          <div class="history-meta">${escapeHtml(meta)}</div>
        </div>`;
      })
      .join("")}
  `;
}

function commandIsAvailable(command) {
  return terminalAllowlist.includes(command);
}

function renderCommandPalette() {
  el.commandGrid.innerHTML = COMMAND_SEQUENCE.map((command) => {
    const available = commandIsAvailable(command);
    const unavailableMark = available ? "" : ` (${t("unavailable")})`;
    return `
      <button class="command-btn" type="button" data-command="${escapeHtml(command)}" ${available ? "" : "disabled"}>
        ${escapeHtml(command.toUpperCase() + unavailableMark)}
        <span class="command-id">${escapeHtml(command)}</span>
      </button>`;
  }).join("");

  el.commandGrid.querySelectorAll(".command-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const command = button.dataset.command || "";
      await runTerminalCommand(command);
    });
  });
}

function pickCount(counts, keys) {
  if (!counts || typeof counts !== "object") {
    return null;
  }
  for (const key of keys) {
    const value = counts[key];
    if (typeof value === "number") {
      return value;
    }
  }
  return null;
}

function renderToolRegistry(state) {
  const registry = state.mechanicus?.tool_registry || {};
  const counts = registry.counts || {};
  const registered = pickCount(counts, ["total", "registered", "tools_total"]);
  const available = pickCount(counts, ["available", "available_pc", "pc_available", "ok"]);
  const missing = pickCount(counts, ["missing", "missing_pc", "unavailable", "failed"]);
  const warnings = state.global_truth?.warnings_count ?? null;
  const errors = state.global_truth?.errors_count ?? null;
  const rows = [
    [t("registered"), registered],
    [t("available"), available],
    [t("missing"), missing],
    [t("counterWarnings"), warnings],
    [t("counterErrors"), errors],
  ];
  el.toolCounters.innerHTML = rows
    .map(
      ([key, value]) => `
      <div class="counter-card">
        <div class="counter-key">${escapeHtml(String(key))}</div>
        <div class="counter-value">${escapeHtml(truthValue(value))}</div>
      </div>`
    )
    .join("");

  const unavailableRows = registry.top_unavailable_tools || [];
  if (!unavailableRows.length) {
    el.toolRows.innerHTML = `<div class="feed-empty">${escapeHtml(t("emptyList"))}</div>`;
    return;
  }
  el.toolRows.innerHTML = unavailableRows
    .map((row) => {
      const parts = [
        row.tool_id ? `tool_id=${row.tool_id}` : "",
        row.pc_status ? `pc_status=${row.pc_status}` : "",
        row.combined_status ? `combined_status=${row.combined_status}` : "",
      ]
        .filter(Boolean)
        .join(" | ");
      return `<div class="tool-row">${escapeHtml(parts || t("unknown"))}</div>`;
    })
    .join("");
}

function renderBottomCard(node, title, value) {
  node.innerHTML = `
    <div class="bottom-title">${escapeHtml(title)}</div>
    <div class="bottom-value">${escapeHtml(value)}</div>
  `;
}

function summarizeCommandHealth() {
  const counts = { PASS: 0, WARN: 0, ERROR: 0, BLOCK: 0, UNKNOWN: 0 };
  terminalHistoryCache.forEach((row) => {
    const key = String(row.status || "UNKNOWN").toUpperCase();
    counts[key] = (counts[key] || 0) + 1;
  });
  return `PASS=${counts.PASS} WARN=${counts.WARN} ERROR=${counts.ERROR} BLOCK=${counts.BLOCK} UNKNOWN=${counts.UNKNOWN}`;
}

function summarizeEventCounters() {
  const items = Object.keys(eventCounters)
    .sort()
    .map((key) => `${key}=${eventCounters[key]}`);
  if (!items.length) {
    return t("emptyList");
  }
  return items.join(" | ");
}

function renderBottomStrip() {
  const latestReport = stateCache?.global_truth?.latest_report_path || t("unknown");
  const latestReceipt = (stateCache?.mechanicus?.latest_receipts || [])[0] || t("unproven");
  const eventSummary = summarizeEventCounters();
  const commandHealth = summarizeCommandHealth();
  renderBottomCard(el.bottomReport, t("bottomReport"), shortValue(latestReport, 110));
  renderBottomCard(el.bottomReceipt, t("bottomReceipt"), shortValue(latestReceipt, 110));
  renderBottomCard(el.bottomEventSummary, t("bottomEvent"), shortValue(eventSummary, 130));
  renderBottomCard(el.bottomCommandHealth, t("bottomHealth"), shortValue(commandHealth, 130));
}

function renderAll(reason = "refresh") {
  if (!stateCache) {
    return;
  }
  renderStaticLabels();
  renderTopBar(stateCache);
  renderActivityFeed();
  renderOrgans(stateCache);
  renderBrainLegend();
  renderTruth(stateCache);
  renderLivePanel(stateCache);
  renderEvidencePanel(stateCache);
  renderReportsPanel(stateCache);
  renderRawPanel(stateCache);
  renderActionHistoryPanel();
  renderCommandPalette();
  renderToolRegistry(stateCache);
  renderBottomStrip();
  if (reason === "command") {
    setActiveTab("live");
  }
}

function bindEvents() {
  el.langSwitch.addEventListener("click", () => {
    locale = locale === "ru" ? "en" : "ru";
    renderAll("lang");
  });

  el.tabs.forEach((button) => {
    button.addEventListener("click", () => {
      setActiveTab(button.dataset.tab || "overview");
    });
  });

  el.terminalForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const value = el.terminalInput.value;
    el.terminalInput.value = "";
    await runTerminalCommand(value);
  });

  el.terminalClearBtn.addEventListener("click", async () => {
    await runTerminalCommand("clear");
  });

  el.rawModeToggleBtn.addEventListener("click", () => {
    setRawMode(!rawModeVisible);
    setActiveTab("live");
  });
}

function bootstrap() {
  bindEvents();
  panelOpenStateMessage = t("panelIdle");
  renderStaticLabels();
  setRawMode(false);
  setActiveTab("overview");
  connectSse();
  refreshAll("init");
  window.setInterval(() => {
    refreshAll("poll");
  }, POLL_INTERVAL_MS);
}

bootstrap();
