const I18N = {
  ru: {
    kicker: "IMPERIUM NEW GENERATION",
    title: "Important Six TUI API Dashboard L1",
    subtitle: "Read-only мост: TUI --smoke + query --sample",
    mode: "Режим",
    updated: "Обновлено",
    refresh: "Обновить",
    safe: "БЕЗОПАСНО: только smoke/sample",
    organ: "Орган",
    verdict: "Вердикт",
    tuiCommand: "Команда TUI smoke",
    queryCommand: "Команда query sample",
    tuiOutput: "Вывод TUI",
    queryOutput: "Вывод query",
    loading: "Загрузка снимка...",
    fetchError: "Ошибка загрузки API",
    noData: "Нет данных",
    unknown: "UNKNOWN"
  },
  en: {
    kicker: "IMPERIUM NEW GENERATION",
    title: "Important Six TUI API Dashboard L1",
    subtitle: "Read-only bridge: TUI --smoke + query --sample",
    mode: "Mode",
    updated: "Updated",
    refresh: "Refresh",
    safe: "SAFE: smoke/sample only",
    organ: "Organ",
    verdict: "Verdict",
    tuiCommand: "TUI smoke command",
    queryCommand: "Query sample command",
    tuiOutput: "TUI output",
    queryOutput: "Query output",
    loading: "Loading dashboard state...",
    fetchError: "API fetch failed",
    noData: "No data",
    unknown: "UNKNOWN"
  }
};

const appState = {
  lang: localStorage.getItem("importantSixDashboardLang") || "ru",
  lastPayload: null,
  loading: false
};

function t(key) {
  const dict = I18N[appState.lang] || I18N.ru;
  return dict[key] || key;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function toLocalTime(isoUtc) {
  if (!isoUtc) return "-";
  const date = new Date(isoUtc);
  if (Number.isNaN(date.getTime())) return isoUtc;
  return date.toLocaleString();
}

function statusClass(status) {
  const norm = String(status || "").toUpperCase();
  if (norm === "PASS") return "status-pass";
  if (norm === "WARN") return "status-warn";
  if (norm === "BLOCK") return "status-block";
  return "";
}

function panelOutputText(snapshot, key) {
  const block = snapshot && snapshot[key] ? snapshot[key] : null;
  if (!block) return t("noData");
  const lines = [];
  lines.push(`exit=${block.exit_code} timeout=${block.timed_out}`);
  if (block.parse_error) lines.push(`parse=${block.parse_error}`);
  if (block.stdout) lines.push(block.stdout);
  if (block.stderr) lines.push(`STDERR:\n${block.stderr}`);
  return lines.join("\n\n");
}

function querySummary(snapshot) {
  const query = snapshot && snapshot.query_sample ? snapshot.query_sample : null;
  if (!query || !query.parsed_json) return "";
  const payload = query.parsed_json;
  if (typeof payload !== "object") return "";
  const verdict = payload.verdict ? `verdict=${payload.verdict}` : null;
  const question = payload.question ? `question=${payload.question}` : null;
  return [verdict, question].filter(Boolean).join(" | ");
}

function applyI18nText() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    if (key) node.textContent = t(key);
  });
  const langBtn = document.getElementById("langBtn");
  langBtn.textContent = appState.lang === "ru" ? "EN" : "RU";
  document.documentElement.lang = appState.lang;
}

function renderPanels(payload) {
  const panelsRoot = document.getElementById("panels");
  panelsRoot.innerHTML = "";

  const organsMap = payload && payload.organs ? payload.organs : {};
  const organKeys = Object.keys(organsMap);

  if (!organKeys.length) {
    panelsRoot.innerHTML = `<article class="panel"><pre class="output-pre">${escapeHtml(t("noData"))}</pre></article>`;
    return;
  }

  const template = document.getElementById("panelTemplate");
  organKeys.forEach((organKey, index) => {
    const snapshot = organsMap[organKey];
    const clone = template.content.cloneNode(true);
    const panel = clone.querySelector(".panel");
    panel.dataset.organPanel = organKey;
    panel.style.animationDelay = `${index * 40}ms`;

    const displayName =
      snapshot && snapshot.display_name && snapshot.display_name[appState.lang]
        ? snapshot.display_name[appState.lang]
        : snapshot && snapshot.display_name && snapshot.display_name.en
          ? snapshot.display_name.en
          : organKey;

    const roleText =
      snapshot && snapshot.role && snapshot.role[appState.lang]
        ? snapshot.role[appState.lang]
        : snapshot && snapshot.role && snapshot.role.en
          ? snapshot.role.en
          : "";

    const status = snapshot && snapshot.status ? String(snapshot.status).toUpperCase() : t("unknown");
    const verdict = snapshot && snapshot.verdict ? String(snapshot.verdict).toUpperCase() : t("unknown");

    clone.querySelector(".panel-title").textContent = displayName;
    clone.querySelector(".panel-role").textContent = roleText;
    clone.querySelector(".organ-label").textContent = snapshot.organ_label || organKey.toUpperCase();
    clone.querySelector(".organ-verdict").textContent = `${verdict} / ${status}`;

    const statusPill = clone.querySelector(".status-pill");
    statusPill.textContent = status;
    statusPill.classList.add(statusClass(status));

    const tuiCmd = snapshot && snapshot.source ? snapshot.source.tui_command : "-";
    const queryCmd = snapshot && snapshot.source ? snapshot.source.query_command : "-";
    clone.querySelector(".cmd-tui").textContent = tuiCmd || "-";
    clone.querySelector(".cmd-query").textContent = queryCmd || "-";

    clone.querySelector(".output-tui").textContent = panelOutputText(snapshot, "tui_smoke");
    const queryText = panelOutputText(snapshot, "query_sample");
    const summary = querySummary(snapshot);
    clone.querySelector(".output-query").textContent = summary ? `${summary}\n\n${queryText}` : queryText;

    if (snapshot && snapshot.accent) {
      panel.style.borderColor = snapshot.accent;
      panel.style.boxShadow = `inset 0 0 0 1px #ffffff05, 0 0 0 1px ${snapshot.accent}22`;
    }

    panelsRoot.appendChild(clone);
  });
}

function renderTop(payload) {
  const status = payload || {};
  const count = status.organs ? Object.keys(status.organs).length : 0;

  document.getElementById("modeLabel").textContent = status.mode || "-";
  document.getElementById("updatedAt").textContent = toLocalTime(status.generated_at_utc);
  document.getElementById("organsCount").textContent = `${count} / 6`;
  document.getElementById("boundary").textContent = status.claim_boundary || "-";
}

async function loadDashboardState() {
  if (appState.loading) return;
  appState.loading = true;

  const panelsRoot = document.getElementById("panels");
  panelsRoot.innerHTML = `<article class="panel"><pre class="output-pre">${escapeHtml(t("loading"))}</pre></article>`;

  try {
    const resp = await fetch("/api/dashboard-state", { cache: "no-store" });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const payload = await resp.json();
    appState.lastPayload = payload;
    renderTop(payload);
    renderPanels(payload);
  } catch (error) {
    panelsRoot.innerHTML = `<article class="panel"><pre class="output-pre">${escapeHtml(t("fetchError"))}: ${escapeHtml(error.message)}</pre></article>`;
  } finally {
    appState.loading = false;
  }
}

function toggleLang() {
  appState.lang = appState.lang === "ru" ? "en" : "ru";
  localStorage.setItem("importantSixDashboardLang", appState.lang);
  applyI18nText();
  if (appState.lastPayload) {
    renderTop(appState.lastPayload);
    renderPanels(appState.lastPayload);
  }
}

function bindEvents() {
  document.getElementById("refreshBtn").addEventListener("click", loadDashboardState);
  document.getElementById("langBtn").addEventListener("click", toggleLang);
}

function boot() {
  applyI18nText();
  bindEvents();
  loadDashboardState();
  window.setInterval(loadDashboardState, 60000);
}

window.addEventListener("DOMContentLoaded", boot);
