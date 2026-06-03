const I18N = {
  en: {
    brandSub: "Mechanicus Holder V0.2",
    actionsTitle: "Owner Actions",
    organTitle: "Organs",
    truthTitle: "Global Truth",
    logTitle: "Micro Log",
    tabOverview: "Overview",
    tabPaths: "Paths",
    tabReceipts: "Receipts",
    tabRaw: "Raw JSON",
    server: "Server",
    apiHealth: "API",
    repoHead: "HEAD",
    worktree: "Worktree",
    active: "Active",
    lastRefresh: "Last refresh",
    quality: "Quality",
    missing: "MISSING",
    actionRunning: "Action running...",
    actionDone: "Action result",
    actionHistory: "Recent actions",
    viewportTitle: "Active organ viewport",
    viewportMissing:
      "No screenshot found. Mechanicus visual capture is missing. Use screenshot action and refresh.",
    placeholderFocus: "This organ is placeholder in V0.2. Visual viewport is reserved for connected organ data.",
    lockedFocus: "This organ is locked in V0.2.",
    identity: "Identity",
    toolRegistry: "Tool registry",
    warnings: "Warnings",
    errors: "Errors",
    blockers: "Blockers",
    reports: "Latest reports",
    screenshots: "Latest screenshots",
    receipts: "Latest receipts",
    commands: "Available commands",
    latestEvidence: "Latest evidence",
    latestReport: "Latest report",
    latestScreenshot: "Latest screenshot",
    emptyList: "None",
    connectedCount: "Connected",
    placeholderCount: "Placeholders",
    lockedCount: "Locked",
    warningsCount: "Warnings",
    errorsCount: "Errors",
    blockersCount: "Blockers",
    freshness: "Freshness reference",
    realPlaceholder: "Real vs placeholder",
    fakeGreenNote:
      "Truth mode: Mechanicus only is connected. Other organs are explicit placeholders/locked.",
    fetchError: "API fetch failed",
  },
  ru: {
    brandSub: "Mechanicus Holder V0.2",
    actionsTitle: "Действия владельца",
    organTitle: "Органы",
    truthTitle: "Блок истины",
    logTitle: "Микро-лог",
    tabOverview: "Обзор",
    tabPaths: "Пути",
    tabReceipts: "Квитанции",
    tabRaw: "Raw JSON",
    server: "Сервер",
    apiHealth: "API",
    repoHead: "HEAD",
    worktree: "Дерево",
    active: "Активный",
    lastRefresh: "Обновление",
    quality: "Качество",
    missing: "ОТСУТСТВУЕТ",
    actionRunning: "Выполнение действия...",
    actionDone: "Результат действия",
    actionHistory: "Недавние действия",
    viewportTitle: "Visual viewport активного органа",
    viewportMissing:
      "Скриншот не найден. Для Mechanicus нет актуального visual-capture. Запустите screenshot action и обновите состояние.",
    placeholderFocus:
      "Этот орган в режиме placeholder в V0.2. Главный visual viewport резервируется под подключённый орган.",
    lockedFocus: "Этот орган заблокирован в V0.2.",
    identity: "Идентичность",
    toolRegistry: "Реестр инструментов",
    warnings: "Предупреждения",
    errors: "Ошибки",
    blockers: "Блокеры",
    reports: "Последние отчёты",
    screenshots: "Последние скриншоты",
    receipts: "Последние квитанции",
    commands: "Доступные команды",
    latestEvidence: "Последний evidence",
    latestReport: "Последний отчёт",
    latestScreenshot: "Последний скриншот",
    emptyList: "Нет",
    connectedCount: "Подключено",
    placeholderCount: "Placeholder",
    lockedCount: "Locked",
    warningsCount: "Предупреждения",
    errorsCount: "Ошибки",
    blockersCount: "Блокеры",
    freshness: "Референс свежести",
    realPlaceholder: "Реальные данные vs placeholder",
    fakeGreenNote:
      "Режим истины: подключён только Mechanicus. Остальные органы явно помечены как placeholder/locked.",
    fetchError: "Ошибка запроса API",
  },
};

let locale = "ru";
let selectedOrganId = "MECHANICUS_AGENT";
let secondaryTab = "overview";
let stateCache = null;
let actionsCache = [];
let historyCache = [];

const el = {
  brandSub: document.getElementById("brandSub"),
  actionsTitle: document.getElementById("actionsTitle"),
  organTitle: document.getElementById("organTitle"),
  truthTitle: document.getElementById("truthTitle"),
  logTitle: document.getElementById("logTitle"),
  tabOverview: document.getElementById("tabOverview"),
  tabPaths: document.getElementById("tabPaths"),
  tabReceipts: document.getElementById("tabReceipts"),
  tabRaw: document.getElementById("tabRaw"),
  headerMetrics: document.getElementById("headerMetrics"),
  actionList: document.getElementById("actionList"),
  actionOutput: document.getElementById("actionOutput"),
  actionHistory: document.getElementById("actionHistory"),
  organGrid: document.getElementById("organGrid"),
  viewportHeader: document.getElementById("viewportHeader"),
  viewportImage: document.getElementById("viewportImage"),
  viewportEmpty: document.getElementById("viewportEmpty"),
  organDetails: document.getElementById("organDetails"),
  truthBlock: document.getElementById("truthBlock"),
  microLog: document.getElementById("microLog"),
  langSwitch: document.getElementById("langSwitch"),
  secondaryTabs: Array.from(document.querySelectorAll(".secondary-tab")),
};

function t(key) {
  return (I18N[locale] && I18N[locale][key]) || key;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function localLabel(organ) {
  return locale === "ru" ? organ.label_ru : organ.label_en;
}

function shortValue(value) {
  if (!value) {
    return t("missing");
  }
  const text = String(value);
  return text.length > 120 ? `${text.slice(0, 117)}...` : text;
}

function listToHtml(items, emptyText) {
  if (!items || !items.length) {
    return `<li>${escapeHtml(emptyText)}</li>`;
  }
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderStaticLabels() {
  el.brandSub.textContent = t("brandSub");
  el.actionsTitle.textContent = t("actionsTitle");
  el.organTitle.textContent = t("organTitle");
  el.truthTitle.textContent = t("truthTitle");
  el.logTitle.textContent = t("logTitle");
  el.tabOverview.textContent = t("tabOverview");
  el.tabPaths.textContent = t("tabPaths");
  el.tabReceipts.textContent = t("tabReceipts");
  el.tabRaw.textContent = t("tabRaw");
  el.langSwitch.textContent = locale === "ru" ? "EN" : "RU";
}

function renderHeader(state) {
  const chips = [
    `${t("server")}: ${state.server.status}`,
    `${t("apiHealth")}: ${state.server.api_status}`,
    `${t("repoHead")}: ${state.repo.head.slice(0, 12)}`,
    `${t("worktree")}: ${state.repo.worktree_state}`,
    `${t("active")}: ${state.server.active_organ}`,
    `${t("quality")}: ${state.server.connection_quality}`,
    `${t("lastRefresh")}: ${state.generated_at_utc}`,
  ];
  el.headerMetrics.innerHTML = chips
    .map((chip) => `<span class="metric-chip">${escapeHtml(chip)}</span>`)
    .join("");
}

function renderActions() {
  el.actionList.innerHTML = actionsCache
    .map((action) => {
      const title = locale === "ru" ? action.title_ru : action.title_en;
      return `<button class="action-btn" type="button" data-action-id="${escapeHtml(action.action_id)}">${escapeHtml(title)}</button>`;
    })
    .join("");

  el.actionList.querySelectorAll(".action-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const actionId = button.dataset.actionId;
      await runAction(actionId || "");
    });
  });
}

function renderActionHistory() {
  const rows = historyCache.slice(0, 8);
  if (!rows.length) {
    el.actionHistory.textContent = `${t("actionHistory")}\n- ${t("emptyList")}`;
    return;
  }
  el.actionHistory.innerHTML = rows
    .map((row) => {
      const line1 = `${row.action_id} :: ${row.status}`;
      const line2 = row.command_or_path || "";
      const line3 = row.finished_at_utc || row.started_at_utc || "";
      return `
      <div class="history-row">
        <div>${escapeHtml(line1)}</div>
        <div>${escapeHtml(shortValue(line2))}</div>
        <div>${escapeHtml(line3)}</div>
      </div>
    `;
    })
    .join("");
}

async function runAction(actionId) {
  if (!actionId) {
    return;
  }
  el.actionOutput.textContent = `${t("actionRunning")}\n${actionId}`;
  try {
    const response = await fetch("/api/actions/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action_id: actionId }),
    });
    const payload = await response.json();
    const lines = [
      `${t("actionDone")}: ${payload.action_id}`,
      `status=${payload.status} exit_code=${payload.exit_code}`,
      `safety=${payload.safety}`,
      `cmd/path=${payload.command_or_path || t("missing")}`,
      `stdout=${payload.stdout_summary || ""}`,
      `stderr=${payload.stderr_summary || ""}`,
      `started=${payload.started_at_utc || ""}`,
      `finished=${payload.finished_at_utc || ""}`,
    ];
    el.actionOutput.textContent = lines.join("\n");
    await refreshAll();
  } catch (error) {
    el.actionOutput.textContent = `${t("fetchError")}: ${String(error)}`;
  }
}

function renderOrgans(state) {
  const organs = state.organs || [];
  el.organGrid.innerHTML = organs
    .map((organ) => {
      const isActive = organ.id === selectedOrganId;
      return `
      <article class="organ-card ${isActive ? "active" : ""}" data-organ-id="${escapeHtml(organ.id)}">
        <h3>${escapeHtml(localLabel(organ))}</h3>
        <span class="status-badge status-${escapeHtml(organ.status)}">${escapeHtml(organ.status)}</span>
      </article>
    `;
    })
    .join("");

  el.organGrid.querySelectorAll(".organ-card").forEach((card) => {
    card.addEventListener("click", () => {
      selectedOrganId = card.dataset.organId || "MECHANICUS_AGENT";
      renderViewport(state);
      renderOrgans(state);
      renderSecondary(state);
    });
  });
}

function renderViewport(state) {
  const selected = (state.organs || []).find((organ) => organ.id === selectedOrganId);
  if (!selected) {
    return;
  }

  el.viewportHeader.textContent = `${t("viewportTitle")} :: ${localLabel(selected)} :: ${selected.status}`;
  if (selected.id !== "MECHANICUS_AGENT") {
    el.viewportImage.style.display = "none";
    el.viewportEmpty.style.display = "block";
    el.viewportEmpty.textContent = selected.status === "LOCKED" ? t("lockedFocus") : t("placeholderFocus");
    return;
  }

  const shots = state.mechanicus?.latest_screenshots || [];
  if (!shots.length) {
    el.viewportImage.style.display = "none";
    el.viewportEmpty.style.display = "block";
    el.viewportEmpty.textContent = t("viewportMissing");
    return;
  }

  const url = `/api/mechanicus/screenshot/latest?ts=${encodeURIComponent(state.generated_at_utc)}`;
  el.viewportImage.style.display = "block";
  el.viewportEmpty.style.display = "none";
  el.viewportImage.src = url;
  el.viewportImage.onerror = () => {
    el.viewportImage.style.display = "none";
    el.viewportEmpty.style.display = "block";
    el.viewportEmpty.textContent = t("viewportMissing");
  };
}

function renderSecondary(state) {
  const organs = state.organs || [];
  const selected = organs.find((organ) => organ.id === selectedOrganId) || organs[0];
  if (!selected) {
    el.organDetails.innerHTML = "";
    return;
  }

  if (selected.id !== "MECHANICUS_AGENT") {
    const text = selected.status === "LOCKED" ? t("lockedFocus") : t("placeholderFocus");
    el.organDetails.innerHTML = `
      <h3 class="detail-title">${escapeHtml(localLabel(selected))}</h3>
      <p class="detail-row">${escapeHtml(text)}</p>
    `;
    return;
  }

  const mechanicus = state.mechanicus || {};
  const toolSummary = mechanicus.tool_registry || {};
  const counts = toolSummary.counts || {};
  const reportItems = (mechanicus.latest_reports || []).slice(0, 6).map((item) => {
    return `${item.task_id} :: ${item.path_repo_relative || item.path}`;
  });
  const screenshotItems = (mechanicus.latest_screenshots || []).slice(0, 6).map((item) => {
    return `${item.file_name} :: ${item.path_repo_relative || item.path}`;
  });
  const receiptItems = (mechanicus.latest_receipts || []).slice(0, 8);
  const commandItems = (mechanicus.commands || []).map((command) => {
    const name = locale === "ru" ? command.title_ru : command.title_en;
    return `${name} => ${command.value}`;
  });

  if (secondaryTab === "paths") {
    const truth = state.global_truth || {};
    el.organDetails.innerHTML = `
      <h3 class="detail-title">Mechanicus :: ${escapeHtml(t("tabPaths"))}</h3>
      <p class="detail-row"><strong>${escapeHtml(t("latestEvidence"))}:</strong> ${escapeHtml(
        truth.latest_evidence_path || t("missing")
      )}</p>
      <p class="detail-row"><strong>${escapeHtml(t("latestReport"))}:</strong> ${escapeHtml(
        truth.latest_report_path || t("missing")
      )}</p>
      <p class="detail-row"><strong>${escapeHtml(t("latestScreenshot"))}:</strong> ${escapeHtml(
        truth.latest_screenshot_path || t("missing")
      )}</p>
      <p class="detail-row"><strong>${escapeHtml(t("reports"))}</strong></p>
      <ul class="detail-list">${listToHtml(reportItems, t("emptyList"))}</ul>
      <p class="detail-row"><strong>${escapeHtml(t("screenshots"))}</strong></p>
      <ul class="detail-list">${listToHtml(screenshotItems, t("emptyList"))}</ul>
    `;
    return;
  }

  if (secondaryTab === "receipts") {
    el.organDetails.innerHTML = `
      <h3 class="detail-title">Mechanicus :: ${escapeHtml(t("tabReceipts"))}</h3>
      <p class="detail-row"><strong>${escapeHtml(t("warnings"))}:</strong> ${(mechanicus.warnings || []).length}</p>
      <p class="detail-row"><strong>${escapeHtml(t("errors"))}:</strong> ${(mechanicus.errors || []).length}</p>
      <p class="detail-row"><strong>${escapeHtml(t("blockers"))}:</strong> ${(mechanicus.blocks || []).length}</p>
      <ul class="detail-list">${listToHtml(receiptItems, t("emptyList"))}</ul>
    `;
    return;
  }

  if (secondaryTab === "raw") {
    const raw = JSON.stringify(mechanicus, null, 2);
    el.organDetails.innerHTML = `
      <h3 class="detail-title">Mechanicus :: ${escapeHtml(t("tabRaw"))}</h3>
      <pre>${escapeHtml(raw.length > 10000 ? `${raw.slice(0, 10000)}\n...<truncated>` : raw)}</pre>
    `;
    return;
  }

  el.organDetails.innerHTML = `
    <h3 class="detail-title">Mechanicus :: ${escapeHtml(t("tabOverview"))}</h3>
    <p class="detail-row"><strong>${escapeHtml(t("identity"))}:</strong> ${escapeHtml(
      mechanicus.identity?.display_name || "Mechanicus"
    )}</p>
    <p class="detail-row"><strong>${escapeHtml(t("toolRegistry"))}:</strong> ${escapeHtml(
      `tools_total=${counts.tools_total ?? "?"}, available_both=${counts.available_both ?? "?"}, known_not_installed=${counts.known_not_installed ?? "?"}`
    )}</p>
    <p class="detail-row"><strong>${escapeHtml(t("warnings"))}:</strong> ${(mechanicus.warnings || []).length}</p>
    <p class="detail-row"><strong>${escapeHtml(t("errors"))}:</strong> ${(mechanicus.errors || []).length}</p>
    <p class="detail-row"><strong>${escapeHtml(t("blockers"))}:</strong> ${(mechanicus.blocks || []).length}</p>
    <p class="detail-row"><strong>${escapeHtml(t("commands"))}</strong></p>
    <ul class="detail-list">${listToHtml(commandItems, t("emptyList"))}</ul>
  `;
}

function renderTruth(state) {
  const truth = state.global_truth || {};
  const matrix = truth.real_vs_placeholder || {};
  const rows = [
    [t("connectedCount"), truth.connected_organs_count],
    [t("placeholderCount"), truth.placeholders_count],
    [t("lockedCount"), truth.locked_count],
    [t("warningsCount"), truth.warnings_count],
    [t("errorsCount"), truth.errors_count],
    [t("blockersCount"), truth.blockers_count],
    [t("latestEvidence"), shortValue(truth.latest_evidence_path)],
    [t("latestReport"), shortValue(truth.latest_report_path)],
    [t("latestScreenshot"), shortValue(truth.latest_screenshot_path)],
    [t("freshness"), shortValue(truth.freshness_reference)],
    [
      t("realPlaceholder"),
      `real=[${(matrix.real || []).join(", ")}], placeholder=[${(matrix.placeholder || []).join(
        ", "
      )}], locked=[${(matrix.locked || []).join(", ")}]`,
    ],
    ["NOTE", t("fakeGreenNote")],
  ];

  el.truthBlock.innerHTML = rows
    .map(
      ([key, value]) => `
      <div class="truth-item">
        <div class="truth-key">${escapeHtml(String(key))}</div>
        <div class="truth-value">${escapeHtml(String(value ?? t("missing")))}</div>
      </div>
    `
    )
    .join("");
}

function renderLog(state) {
  const rows = (state.micro_log || []).slice(-18).reverse();
  el.microLog.innerHTML = rows
    .map((row) => {
      const time = (row.timestamp_utc || "").split("T")[1] || row.timestamp_utc || "";
      return `
      <div class="log-row">
        <span>${escapeHtml(time.replace("Z", ""))}</span>
        <span class="log-status ${escapeHtml(row.status || "UNKNOWN")}">${escapeHtml(row.status || "UNKNOWN")}</span>
        <span>${escapeHtml(row.message || "")}</span>
      </div>
    `;
    })
    .join("");
}

function renderAll(state) {
  renderStaticLabels();
  renderHeader(state);
  renderActions();
  renderActionHistory();
  renderOrgans(state);
  renderViewport(state);
  renderSecondary(state);
  renderTruth(state);
  renderLog(state);
}

async function fetchState() {
  const response = await fetch("/api/state", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`STATE_HTTP_${response.status}`);
  }
  return response.json();
}

async function fetchActions() {
  const response = await fetch("/api/actions", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`ACTIONS_HTTP_${response.status}`);
  }
  const payload = await response.json();
  return payload.actions || [];
}

async function fetchHistory() {
  const response = await fetch("/api/actions/history", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`HISTORY_HTTP_${response.status}`);
  }
  const payload = await response.json();
  return payload.history || [];
}

async function refreshAll() {
  try {
    const [state, actions, history] = await Promise.all([fetchState(), fetchActions(), fetchHistory()]);
    stateCache = state;
    actionsCache = actions;
    historyCache = history;
    renderAll(stateCache);
  } catch (error) {
    el.actionOutput.textContent = `${t("fetchError")}: ${String(error)}`;
  }
}

el.langSwitch.addEventListener("click", () => {
  locale = locale === "ru" ? "en" : "ru";
  if (stateCache) {
    renderAll(stateCache);
  } else {
    renderStaticLabels();
  }
});

el.secondaryTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    secondaryTab = tab.dataset.tabId || "overview";
    el.secondaryTabs.forEach((other) => other.classList.remove("is-active"));
    tab.classList.add("is-active");
    if (stateCache) {
      renderSecondary(stateCache);
    }
  });
});

renderStaticLabels();
refreshAll();
setInterval(refreshAll, 20000);

