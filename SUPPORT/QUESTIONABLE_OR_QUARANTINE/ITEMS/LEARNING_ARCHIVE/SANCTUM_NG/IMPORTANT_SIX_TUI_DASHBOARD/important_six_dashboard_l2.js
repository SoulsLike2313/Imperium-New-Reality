const I18N = {
  ru: {
    kicker: "IMPERIUM NEW GENERATION",
    title: "Important Six Dashboard L2 Control Action Surface",
    subtitle: "Безопасные кнопки L2: allowlisted actions, receipts, owner intent, diff gate.",
    mode: "Режим",
    updated: "Обновлено",
    refresh: "Обновить",
    groups: "Группы действий",
    diffPanel: "Diff / Approval",
    ownerIntentPanel: "Owner Intent / Questions",
    resultPanel: "Результат действия",
    historyPanel: "История действий",
    decision: "Решение",
    noteRu: "Комментарий RU",
    organ: "Орган",
    severity: "Серьёзность",
    question: "Вопрос",
    requiredDecision: "Требуемое решение",
    decisionOptional: "Решение (опционально)",
    run: "Запустить",
    lastResult: "Last",
    loading: "Загрузка...",
    loadingActions: "Загрузка групп действий...",
    error: "Ошибка",
    noData: "Нет данных"
  },
  en: {
    kicker: "IMPERIUM NEW GENERATION",
    title: "Important Six Dashboard L2 Control Action Surface",
    subtitle: "Safe L2 buttons: allowlisted actions, receipts, owner intent, diff gate.",
    mode: "Mode",
    updated: "Updated",
    refresh: "Refresh",
    groups: "Action Groups",
    diffPanel: "Diff / Approval",
    ownerIntentPanel: "Owner Intent / Questions",
    resultPanel: "Action Result",
    historyPanel: "Action History",
    decision: "Decision",
    noteRu: "RU Note",
    organ: "Organ",
    severity: "Severity",
    question: "Question",
    requiredDecision: "Required Decision",
    decisionOptional: "Decision (optional)",
    run: "Run",
    lastResult: "Last",
    loading: "Loading...",
    loadingActions: "Loading action groups...",
    error: "Error",
    noData: "No data"
  }
};

const GROUP_I18N = {
  "Administratum": { ru: "Administratum / Администратум", en: "Administratum" },
  "Transfer Zone": { ru: "Transfer Zone / Трансфер", en: "Transfer Zone" },
  "Mechanicus": { ru: "Mechanicus / Механикус", en: "Mechanicus" },
  "Inquisition": { ru: "Inquisition / Инквизиция", en: "Inquisition" },
  "Astronomicon": { ru: "Astronomicon / Астрономикон", en: "Astronomicon" },
  "Diff / Approval": { ru: "Diff / Одобрение", en: "Diff / Approval" },
  "Owner Intent / Questions": { ru: "Owner Intent / Вопросы", en: "Owner Intent / Questions" }
};

const appState = {
  lang: localStorage.getItem("importantSixL2Lang") || "ru",
  actionsPayload: null,
  loading: false,
  running: new Set()
};

function t(key) {
  const dict = I18N[appState.lang] || I18N.ru;
  return dict[key] || key;
}

function groupLabel(groupName) {
  const value = GROUP_I18N[groupName];
  if (!value) return groupName;
  return value[appState.lang] || value.ru || groupName;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function pretty(value) {
  if (value === null || value === undefined) return t("noData");
  if (typeof value === "string") return value;
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return String(value);
  }
}

function toLocal(isoUtc) {
  if (!isoUtc) return "-";
  const date = new Date(isoUtc);
  if (Number.isNaN(date.getTime())) return isoUtc;
  return date.toLocaleString();
}

function setBox(boxId, payload) {
  const node = document.getElementById(boxId);
  node.textContent = pretty(payload);
}

function applyI18n() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.getAttribute("data-i18n");
    if (key) node.textContent = t(key);
  });
  const langBtn = document.getElementById("langBtn");
  langBtn.textContent = appState.lang === "ru" ? "EN" : "RU";
  document.documentElement.lang = appState.lang;
}

async function apiGet(path) {
  const resp = await fetch(path, { cache: "no-store" });
  const text = await resp.text();
  let parsed;
  try {
    parsed = text ? JSON.parse(text) : {};
  } catch (error) {
    throw new Error(`Invalid JSON response from ${path}`);
  }
  if (!resp.ok) {
    const detail = parsed && parsed.detail ? parsed.detail : JSON.stringify(parsed);
    throw new Error(`HTTP ${resp.status}: ${detail}`);
  }
  return parsed;
}

async function apiPost(path, payload) {
  const resp = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {})
  });
  const text = await resp.text();
  let parsed;
  try {
    parsed = text ? JSON.parse(text) : {};
  } catch (error) {
    throw new Error(`Invalid JSON response from ${path}`);
  }
  if (!resp.ok) {
    const detail = parsed && parsed.detail ? parsed.detail : JSON.stringify(parsed);
    throw new Error(`HTTP ${resp.status}: ${detail}`);
  }
  return parsed;
}

function safetyClassTag(safetyClass) {
  const cls = String(safetyClass || "").toUpperCase();
  if (cls.includes("READ")) return "read";
  if (cls.includes("DRY")) return "dry";
  return "write";
}

function normalizeStatus(statusValue) {
  const status = String(statusValue || "").toUpperCase();
  if (status === "PASS" || status === "OK") return "PASS";
  if (status === "PASS_WITH_WARNINGS" || status === "WARN" || status === "WARNING" || status === "PARTIAL") {
    return "PASS_WITH_WARNINGS";
  }
  if (status === "FAIL" || status === "FAILED" || status === "ERROR") return "FAIL";
  if (status === "BLOCKED" || status === "BLOCK") return "BLOCKED";
  return "BLOCKED";
}

function buildPayloadForAction(actionId) {
  if (actionId === "OWNER_RECORD_DIFF_DECISION") {
    return {
      decision: document.getElementById("diffDecisionSelect").value,
      note_ru: document.getElementById("diffNoteInput").value.trim(),
      author: "OWNER"
    };
  }
  if (actionId === "OWNER_RECORD_NOTE_OR_DECISION") {
    return {
      organ: document.getElementById("ownerOrganInput").value.trim() || "OFFICIO_AGENTIS",
      severity: document.getElementById("ownerSeveritySelect").value,
      question: document.getElementById("ownerQuestionInput").value.trim(),
      required_decision: document.getElementById("ownerRequiredDecisionInput").value.trim() || "OWNER_REVIEW",
      decision: document.getElementById("ownerDecisionInput").value.trim(),
      note_ru: document.getElementById("ownerNoteInput").value.trim()
    };
  }
  return {};
}

async function runAction(actionId) {
  if (appState.running.has(actionId)) return;
  appState.running.add(actionId);
  renderGroups(appState.actionsPayload);
  setBox("resultBox", `${t("loading")} ${actionId} ...`);
  try {
    const payload = buildPayloadForAction(actionId);
    const result = await apiPost(`/api/actions/${actionId}/run`, payload);
    setBox("resultBox", result);
  } catch (error) {
    setBox("resultBox", { status: "BLOCKED", error: String(error) });
  } finally {
    appState.running.delete(actionId);
    await refreshPanels();
    await loadActions();
  }
}

async function loadLastResult(actionId) {
  setBox("resultBox", `${t("loading")} ${actionId} ...`);
  try {
    const payload = await apiGet(`/api/actions/${actionId}/last-result`);
    setBox("resultBox", payload);
  } catch (error) {
    setBox("resultBox", { status: "BLOCKED", error: String(error) });
  }
}

function renderGroups(payload) {
  const root = document.getElementById("groupsRoot");
  root.innerHTML = "";

  if (!payload || !payload.groups) {
    root.innerHTML = `<article class="group-card"><pre class="json-box">${escapeHtml(t("loadingActions"))}</pre></article>`;
    return;
  }

  const groups = payload.groups;
  const groupNames = Object.keys(groups);
  const actionCount = payload.actions_count || 0;
  document.getElementById("actionCount").textContent = `actions=${actionCount}`;

  let passLike = 0;
  let warnLike = 0;
  let blockLike = 0;

  groupNames.forEach((groupName) => {
    const groupActions = groups[groupName];
    const groupNode = document.getElementById("groupTemplate").content.cloneNode(true);
    const groupCard = groupNode.querySelector(".group-card");
    groupCard.querySelector(".group-title").textContent = groupLabel(groupName);
    const actionsRoot = groupCard.querySelector(".actions-list");

    groupActions.forEach((action) => {
      const actionNode = document.getElementById("actionTemplate").content.cloneNode(true);
      const actionCard = actionNode.querySelector(".action-item");
      const title = appState.lang === "ru" ? action.label_ru : action.action_id;
      actionCard.querySelector(".action-title").textContent = title;
      actionCard.querySelector(".action-desc").textContent = action.description || "";
      actionCard.querySelector(".action-id").textContent = action.action_id;

      const safety = String(action.safety_class || "");
      const safetyNode = actionCard.querySelector(".safety-tag");
      safetyNode.textContent = safety;
      safetyNode.classList.add(safetyClassTag(safety));

      const last = action.last_result;
      const status = last && last.status ? normalizeStatus(last.status) : "UNKNOWN";
      const summary = last && last.summary ? String(last.summary) : "-";
      actionCard.querySelector(".action-last").textContent = `${status}: ${summary}`;
      if (status === "PASS") passLike += 1;
      else if (status === "PASS_WITH_WARNINGS") warnLike += 1;
      else if (status === "FAIL" || status === "BLOCKED") blockLike += 1;

      const runBtn = actionCard.querySelector(".run-btn");
      runBtn.disabled = appState.running.has(action.action_id);
      runBtn.addEventListener("click", () => runAction(action.action_id));

      const lastBtn = actionCard.querySelector(".last-btn");
      lastBtn.addEventListener("click", () => loadLastResult(action.action_id));

      actionsRoot.appendChild(actionNode);
    });
    root.appendChild(groupNode);
  });

  document.getElementById("statusHint").textContent = `PASS=${passLike} PASS_WITH_WARNINGS=${warnLike} FAIL_OR_BLOCKED=${blockLike}`;
}

async function loadActions() {
  if (appState.loading) return;
  appState.loading = true;
  try {
    const payload = await apiGet("/api/actions");
    appState.actionsPayload = payload;
    renderGroups(payload);
  } catch (error) {
    appState.actionsPayload = null;
    renderGroups(null);
    setBox("resultBox", { status: "BLOCKED", error: String(error) });
  } finally {
    appState.loading = false;
  }
}

async function refreshPanels() {
  try {
    const statusPayload = await apiGet("/api/status");
    document.getElementById("modeLabel").textContent = statusPayload.mode || "-";
    document.getElementById("updatedAt").textContent = toLocal(statusPayload.generated_at_utc);
  } catch (error) {
    document.getElementById("modeLabel").textContent = "ERROR";
    document.getElementById("updatedAt").textContent = String(error);
  }

  try {
    const diffPayload = await apiGet("/api/diff/status");
    setBox("diffStatusBox", diffPayload);
  } catch (error) {
    setBox("diffStatusBox", { status: "BLOCKED", error: String(error) });
  }

  try {
    const ownerPayload = await apiGet("/api/owner-questions");
    setBox("ownerQuestionsBox", ownerPayload);
  } catch (error) {
    setBox("ownerQuestionsBox", { status: "BLOCKED", error: String(error) });
  }

  try {
    const historyPayload = await apiGet("/api/action-history?limit=60");
    setBox("historyBox", historyPayload);
  } catch (error) {
    setBox("historyBox", { status: "BLOCKED", error: String(error) });
  }
}

function toggleLanguage() {
  appState.lang = appState.lang === "ru" ? "en" : "ru";
  localStorage.setItem("importantSixL2Lang", appState.lang);
  applyI18n();
  renderGroups(appState.actionsPayload);
}

function bindEvents() {
  document.getElementById("refreshBtn").addEventListener("click", async () => {
    await refreshPanels();
    await loadActions();
  });
  document.getElementById("langBtn").addEventListener("click", toggleLanguage);
}

async function boot() {
  applyI18n();
  bindEvents();
  setBox("resultBox", t("loading"));
  await refreshPanels();
  await loadActions();
  window.setInterval(async () => {
    await refreshPanels();
    await loadActions();
  }, 90000);
}

window.addEventListener("DOMContentLoaded", boot);
