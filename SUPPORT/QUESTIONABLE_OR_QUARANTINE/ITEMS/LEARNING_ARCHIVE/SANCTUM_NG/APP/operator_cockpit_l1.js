(() => {
  const I18N = {
    en: {
      title: "Sanctum Operator Cockpit L1",
      subtitle: "Owner power slice: read-only overview with bounded action truth.",
      legacy: "Legacy Shell",
      labels: {
        task: "Active task",
        worker: "Who works",
        contour: "Contour",
        blocker: "Current blocker",
        next: "Next action",
        repo: "Repo clean",
        confidence: "Evidence confidence",
        head: "HEAD",
        sessionMode: "Session mode",
        sessionStatus: "Session status",
        ownerOpen: "Owner open",
        ownerBlocking: "Owner blocking",
        ownerTotal: "Questions total",
        organReq: "Organ requests",
        organResp: "Organ responses",
        changedCount: "Changed files",
        masterSynced: "Master synced"
      },
      headers: {
        gateway: "Focus Gateway Map",
        external: "External Inputs",
        workers: "Workers / Contours",
        assist: "Assistance",
        outputs: "Digital Outputs",
        taskSession: "Task / Session",
        taskSources: "Source refs",
        transfer: "Transfer Routes",
        transferSources: "Source refs",
        evidence: "Evidence / Diff",
        changed: "Changed files",
        reports: "Report refs",
        validators: "Validator refs",
        screenshots: "Screenshots",
        ownerOrgan: "Owner Questions / Organ Dialogue",
        ownerOrganSources: "Source refs",
        continuity: "Continuity + Development Preview",
        continuitySub: "Build Continuity Pack",
        previewSub: "Development Preview",
        actions: "Action Strip",
        lastAction: "Last action result"
      },
      notes: {
        action: "Every active WIRED/DRY_RUN_ONLY action must emit request/result receipts.",
        footerBoundary: "PASS boundary: read-only owner overview only.",
        footerNotProven: "Not proven: live execution, production orchestration, full organ intelligence.",
        previewOnly: "Preview only",
        runAction: "Run action",
        unavailable: "Unavailable",
        running: "Running...",
        apiConnected: "API_CONNECTED",
        apiUnavailable: "API_UNAVAILABLE"
      }
    },
    ru: {
      title: "Sanctum Operator Cockpit L1",
      subtitle: "Срез Owner power: read-only обзор с ограниченной action truth.",
      legacy: "Legacy Shell",
      labels: {
        task: "Активная задача",
        worker: "Кто работает",
        contour: "Контур",
        blocker: "Текущий блокер",
        next: "Следующее действие",
        repo: "Repo чистый",
        confidence: "Уверенность evidence",
        head: "HEAD",
        sessionMode: "Режим сессии",
        sessionStatus: "Статус сессии",
        ownerOpen: "Owner open",
        ownerBlocking: "Owner blocking",
        ownerTotal: "Всего вопросов",
        organReq: "Запросов к органам",
        organResp: "Ответов органов",
        changedCount: "Изменённых файлов",
        masterSynced: "Master synced"
      },
      headers: {
        gateway: "Карта Focus Gateway",
        external: "Внешние входы",
        workers: "Работники / Контуры",
        assist: "Assistance",
        outputs: "Цифровые выходы",
        taskSession: "Task / Session",
        taskSources: "Source refs",
        transfer: "Transfer Routes",
        transferSources: "Source refs",
        evidence: "Evidence / Diff",
        changed: "Изменённые файлы",
        reports: "Ссылки отчётов",
        validators: "Validator refs",
        screenshots: "Скриншоты",
        ownerOrgan: "Owner Questions / Organ Dialogue",
        ownerOrganSources: "Source refs",
        continuity: "Continuity + Development Preview",
        continuitySub: "Build Continuity Pack",
        previewSub: "Development Preview",
        actions: "Action Strip",
        lastAction: "Результат последнего действия"
      },
      notes: {
        action: "Каждое активное WIRED/DRY_RUN_ONLY действие должно иметь request/result receipt.",
        footerBoundary: "Граница PASS: только read-only owner overview.",
        footerNotProven: "Не доказано: live execution, production orchestration, full organ intelligence.",
        previewOnly: "Только превью",
        runAction: "Запустить",
        unavailable: "Недоступно",
        running: "Выполняется...",
        apiConnected: "API_CONNECTED",
        apiUnavailable: "API_UNAVAILABLE"
      }
    }
  };

  const query = new URLSearchParams(window.location.search);
  const langFromQuery = query.get("lang");
  const storedLang = window.localStorage.getItem("operatorCockpitLang");
  const initialLang = langFromQuery === "ru" || langFromQuery === "en"
    ? langFromQuery
    : storedLang === "ru" || storedLang === "en"
      ? storedLang
      : "en";

  const appState = {
    lang: initialLang,
    runtimeConnected: false,
    runtimeActions: {},
    runtimeState: null,
    model: null,
    lastActionResult: null
  };

  function textNode(id, value) {
    const node = document.getElementById(id);
    if (node) {
      node.textContent = value;
    }
  }

  function listNode(id, items, asLinks = false) {
    const node = document.getElementById(id);
    if (!node) {
      return;
    }
    node.innerHTML = "";
    const values = Array.isArray(items) && items.length > 0 ? items : ["-"];
    values.forEach((item) => {
      const li = document.createElement("li");
      if (!asLinks || typeof item !== "string" || item === "-") {
        li.textContent = String(item);
      } else {
        const a = document.createElement("a");
        a.href = resolveEvidenceHref(item);
        a.textContent = item;
        a.target = "_blank";
        a.rel = "noopener";
        li.appendChild(a);
      }
      node.appendChild(li);
    });
  }

  function resolveEvidenceHref(ref) {
    if (typeof ref !== "string") {
      return "#";
    }
    if (/^https?:\/\//i.test(ref)) {
      return ref;
    }
    if (window.location.port === "8787") {
      return `http://127.0.0.1:8765/${ref}`;
    }
    if (ref.startsWith("/")) {
      return ref;
    }
    return `/${ref}`;
  }

  function statusClass(value) {
    return String(value || "unknown").toLowerCase().replace(/[^a-z0-9]+/g, "_");
  }

  function setPill(id, status) {
    const node = document.getElementById(id);
    if (!node) {
      return;
    }
    node.textContent = String(status || "UNKNOWN");
    node.className = `status-pill ${statusClass(status)}`;
  }

  function applyLanguage() {
    const t = I18N[appState.lang];
    document.documentElement.lang = appState.lang;
    textNode("title-text", t.title);
    textNode("subtitle-text", t.subtitle);
    textNode("legacy-link", t.legacy);
    textNode("label-task", t.labels.task);
    textNode("label-worker", t.labels.worker);
    textNode("label-contour", t.labels.contour);
    textNode("label-blocker", t.labels.blocker);
    textNode("label-next", t.labels.next);
    textNode("label-repo", t.labels.repo);
    textNode("label-confidence", t.labels.confidence);
    textNode("label-head", t.labels.head);
    textNode("label-session-mode", t.labels.sessionMode);
    textNode("label-session-status", t.labels.sessionStatus);
    textNode("label-owner-open", t.labels.ownerOpen);
    textNode("label-owner-blocking", t.labels.ownerBlocking);
    textNode("label-owner-total", t.labels.ownerTotal);
    textNode("label-organ-req", t.labels.organReq);
    textNode("label-organ-resp", t.labels.organResp);
    textNode("label-changed-count", t.labels.changedCount);
    textNode("label-master-sync", t.labels.masterSynced);

    textNode("gateway-title", t.headers.gateway);
    textNode("external-title", t.headers.external);
    textNode("workers-title", t.headers.workers);
    textNode("assist-title", t.headers.assist);
    textNode("outputs-title", t.headers.outputs);
    textNode("task-session-title", t.headers.taskSession);
    textNode("task-sources-title", t.headers.taskSources);
    textNode("transfer-title", t.headers.transfer);
    textNode("transfer-sources-title", t.headers.transferSources);
    textNode("evidence-title", t.headers.evidence);
    textNode("changed-title", t.headers.changed);
    textNode("reports-title", t.headers.reports);
    textNode("validators-title", t.headers.validators);
    textNode("screenshots-title", t.headers.screenshots);
    textNode("owner-organ-title", t.headers.ownerOrgan);
    textNode("owner-organ-sources-title", t.headers.ownerOrganSources);
    textNode("continuity-title", t.headers.continuity);
    textNode("continuity-subtitle", t.headers.continuitySub);
    textNode("preview-subtitle", t.headers.previewSub);
    textNode("actions-title", t.headers.actions);
    textNode("last-action-title", t.headers.lastAction);

    textNode("action-note", t.notes.action);
    textNode("footer-boundary", t.notes.footerBoundary);
    textNode("footer-not-proven", t.notes.footerNotProven);

    const toggle = document.getElementById("lang-toggle");
    if (toggle) {
      toggle.textContent = appState.lang === "en" ? "RU" : "EN";
    }
  }

  function fallbackModel() {
    return {
      schema_id: "OPERATOR_COCKPIT_L1_STATE_V0_1",
      task_id: "UNKNOWN",
      generated_at_utc: "UNKNOWN",
      repo: {
        head: "UNKNOWN",
        branch: "UNKNOWN",
        worktree: "UNKNOWN",
        master_synced: false,
        changed_files: []
      },
      five_second_truth: {
        active_task: "UNKNOWN",
        who_is_working: "UNKNOWN",
        contour: "PC",
        current_blocker: "state_unavailable",
        next_action: "run_builder",
        repo_clean: "UNKNOWN",
        evidence_confidence: "LOW"
      },
      focus_gateway: {
        external_inputs: [],
        imperium_core: "IMPERIUM core",
        workers: [],
        assistance_block: "UNKNOWN",
        digital_outputs: []
      },
      panels: {
        task_session: { status: "UNKNOWN", summary: {}, source_refs: [] },
        owner_questions_organ_dialogue: { status: "UNKNOWN", summary: {}, source_refs: [] }
      },
      transfer_routes: {
        pc_vm2: "UNKNOWN",
        pc_vm3: "UNKNOWN",
        vm2_vm3: "UNKNOWN",
        vm3_vm2: "UNKNOWN",
        route_proof_commit: "UNKNOWN",
        source_refs: []
      },
      evidence_diff: {
        changed_files_count: 0,
        changed_files: [],
        report_refs: [],
        validator_refs: [],
        screenshot_refs: [],
        source_refs: []
      },
      continuity: {
        small_mode: "STUB",
        latest_pack_ref: null
      },
      development_preview: {
        status: "PREVIEW_ONLY",
        preview_url: null,
        reason: "state unavailable"
      },
      actions: []
    };
  }

  async function loadGeneratedState() {
    const candidates = [
      "../OPERATOR_COCKPIT/DATA/operator_cockpit_l1_state.generated.json",
      "/IMPERIUM_NEW_GENERATION/SANCTUM_NG/OPERATOR_COCKPIT/DATA/operator_cockpit_l1_state.generated.json"
    ];
    for (const path of candidates) {
      try {
        const res = await fetch(path, { cache: "no-store" });
        if (!res.ok) {
          continue;
        }
        const payload = await res.json();
        if (payload && typeof payload === "object") {
          return payload;
        }
      } catch (_err) {
        // Continue to next candidate.
      }
    }
    return null;
  }

  async function loadRuntimeApi() {
    try {
      const [stateRes, actionsRes] = await Promise.all([
        fetch("/api/state", { cache: "no-store" }),
        fetch("/api/actions", { cache: "no-store" })
      ]);
      if (!stateRes.ok || !actionsRes.ok) {
        throw new Error(`api_status_${stateRes.status}_${actionsRes.status}`);
      }
      const runtimeState = await stateRes.json();
      const runtimeActions = await actionsRes.json();
      appState.runtimeConnected = true;
      appState.runtimeState = runtimeState;
      const map = {};
      const actions = Array.isArray(runtimeActions.actions) ? runtimeActions.actions : [];
      actions.forEach((action) => {
        if (action && typeof action === "object") {
          const key = String(action.action_id || "");
          if (key) {
            map[key] = action;
          }
        }
      });
      appState.runtimeActions = map;
      appState.lastActionResult = runtimeState.latest_action_result || null;
      return true;
    } catch (_err) {
      appState.runtimeConnected = false;
      appState.runtimeActions = {};
      return false;
    }
  }

  function mapStatusFromRuntime(actionItem) {
    const activeStates = new Set(["WIRED", "DRY_RUN_ONLY"]);
    const backendId = actionItem.backend_action_id;
    if (!backendId || typeof backendId !== "string") {
      return actionItem.status;
    }
    const runtimeAction = appState.runtimeActions[backendId];
    if (!runtimeAction || typeof runtimeAction !== "object") {
      return "BLOCKED";
    }
    if (actionItem.status === "DRY_RUN_ONLY") {
      return "DRY_RUN_ONLY";
    }
    const runtimeStatus = String(runtimeAction.status || "UNKNOWN");
    if (runtimeStatus === "WIRED") {
      return actionItem.status;
    }
    if (activeStates.has(actionItem.status)) {
      return "BLOCKED";
    }
    return actionItem.status;
  }

  function normalizeActionList(actions) {
    if (!Array.isArray(actions)) {
      return [];
    }
    return actions
      .filter((item) => item && typeof item === "object")
      .map((item) => {
        const status = mapStatusFromRuntime(item);
        return {
          control_id: String(item.control_id || "unknown"),
          label: String(item.label || "Unknown"),
          status: String(status || "UNKNOWN"),
          backend_action_id: item.backend_action_id ? String(item.backend_action_id) : null,
          request_result_receipt_mode: String(item.request_result_receipt_mode || "UNKNOWN"),
          reason: String(item.reason || "-"),
          evidence_refs: Array.isArray(item.evidence_refs) ? item.evidence_refs : []
        };
      });
  }

  function renderModel() {
    const m = appState.model || fallbackModel();
    const task = m.five_second_truth || {};
    textNode("truth-task", task.active_task || "-");
    textNode("truth-worker", task.who_is_working || "-");
    textNode("truth-contour", task.contour || "-");
    textNode("truth-blocker", task.current_blocker || "-");
    textNode("truth-next", task.next_action || "-");
    textNode("truth-repo-clean", task.repo_clean || "-");
    textNode("truth-confidence", task.evidence_confidence || "-");
    textNode("truth-head", (m.repo || {}).head || "-");

    const warningLamp = document.getElementById("warning-lamp");
    if (warningLamp) {
      const blockerText = String(task.current_blocker || "").toLowerCase();
      const hot = blockerText.includes("block") || blockerText.includes("dirty") || blockerText.includes("owner");
      warningLamp.style.background = hot
        ? "radial-gradient(circle, rgba(255,107,107,0.95), rgba(139,26,26,0.88))"
        : "radial-gradient(circle, rgba(114,209,154,0.95), rgba(28,89,54,0.9))";
      warningLamp.style.boxShadow = hot
        ? "0 0 14px rgba(255, 107, 107, 0.58)"
        : "0 0 14px rgba(114, 209, 154, 0.55)";
    }

    const gateway = m.focus_gateway || {};
    textNode("core-label", gateway.imperium_core || "IMPERIUM CORE");
    textNode("assist-text", gateway.assistance_block || "-");
    listNode("external-list", gateway.external_inputs || []);
    listNode("workers-list", gateway.workers || []);
    listNode("outputs-list", gateway.digital_outputs || []);

    const taskPanel = (m.panels || {}).task_session || {};
    const taskSummary = taskPanel.summary || {};
    setPill("task-session-status", taskPanel.status || "UNKNOWN");
    textNode("session-mode", taskSummary.session_mode || "-");
    textNode("session-status", taskSummary.session_status || taskPanel.status || "-");
    textNode("owner-open", String(taskSummary.owner_open_questions ?? "-"));
    textNode("owner-blocking", String(taskSummary.owner_blocking_questions ?? "-"));
    listNode("task-session-sources", taskPanel.source_refs || [], true);

    const transfer = m.transfer_routes || {};
    const routeStatus = String(transfer.vm2_vm3 || "UNKNOWN").includes("PROVED") ? "PROVED" : "WARN";
    setPill("transfer-status", routeStatus);
    textNode("route-pc-vm2", transfer.pc_vm2 || "-");
    textNode("route-pc-vm3", transfer.pc_vm3 || "-");
    textNode("route-vm2-vm3", transfer.vm2_vm3 || "-");
    textNode("route-vm3-vm2", transfer.vm3_vm2 || "-");
    textNode("route-proof-commit", `route proof commit: ${transfer.route_proof_commit || "-"}`);
    listNode("transfer-sources", transfer.source_refs || [], true);

    const evidence = m.evidence_diff || {};
    const repo = m.repo || {};
    const changed = Array.isArray(evidence.changed_files) ? evidence.changed_files : [];
    textNode("changed-count", String(evidence.changed_files_count ?? changed.length ?? 0));
    textNode("master-synced", repo.master_synced === true ? "YES" : "NO");
    setPill("evidence-status", changed.length > 0 ? "WARN" : "PROVED");
    listNode("changed-files", changed, false);
    listNode("report-refs", evidence.report_refs || [], true);
    listNode("validator-refs", evidence.validator_refs || [], true);
    listNode("screenshot-refs", evidence.screenshot_refs || [], true);

    const ownerPanel = (m.panels || {}).owner_questions_organ_dialogue || {};
    const ownerSummary = ownerPanel.summary || {};
    setPill("owner-organ-status", ownerPanel.status || "FOUNDATION_ONLY");
    textNode("owner-total", String(ownerSummary.owner_question_total ?? "-"));
    textNode("organ-requests", String(ownerSummary.organ_request_count ?? "-"));
    textNode("organ-responses", String(ownerSummary.organ_response_count ?? "-"));
    listNode("owner-organ-sources", ownerPanel.source_refs || [], true);

    const continuity = m.continuity || {};
    const continuityStatus = String(continuity.small_mode || "PREVIEW_ONLY");
    setPill("continuity-status", continuityStatus);
    textNode("continuity-mode", `small mode: ${continuityStatus}`);
    textNode("continuity-latest-pack", `latest pack: ${continuity.latest_pack_ref || "-"}`);
    textNode("continuity-latest-manifest", `manifest: ${continuity.latest_manifest_ref || "-"}`);
    textNode("continuity-latest-result", `result: ${continuity.latest_result_ref || "-"}`);

    const preview = m.development_preview || {};
    textNode("preview-status-line", `status: ${preview.status || "-"}`);
    textNode("preview-reason-line", `reason: ${preview.reason || "-"}`);
    const previewLink = document.getElementById("preview-url");
    if (previewLink) {
      const url = preview.preview_url || "#";
      previewLink.href = url;
      previewLink.textContent = url;
    }

    renderActions(normalizeActionList(m.actions || []));
    renderLastAction();
  }

  function renderActions(actions) {
    const container = document.getElementById("action-cards");
    if (!container) {
      return;
    }
    container.innerHTML = "";
    setPill("action-connection", appState.runtimeConnected ? I18N[appState.lang].notes.apiConnected : I18N[appState.lang].notes.apiUnavailable);
    actions.forEach((action) => {
      const card = document.createElement("article");
      card.className = "action-card";
      const status = action.status;
      const statusPillClass = statusClass(status);
      const canRun = appState.runtimeConnected &&
        (status === "WIRED" || status === "DRY_RUN_ONLY") &&
        typeof action.backend_action_id === "string" &&
        action.backend_action_id.length > 0;

      const title = document.createElement("h3");
      title.textContent = action.label;
      card.appendChild(title);

      const statusLine = document.createElement("p");
      statusLine.innerHTML = `status: <span class="status-pill ${statusPillClass}">${status}</span>`;
      card.appendChild(statusLine);

      const reason = document.createElement("p");
      reason.textContent = action.reason;
      card.appendChild(reason);

      const mode = document.createElement("p");
      mode.textContent = `receipt mode: ${action.request_result_receipt_mode}`;
      card.appendChild(mode);

      const refs = document.createElement("p");
      refs.textContent = `evidence refs: ${action.evidence_refs.length}`;
      card.appendChild(refs);

      const button = document.createElement("button");
      button.type = "button";
      button.className = "action-run";
      if (canRun) {
        button.textContent = I18N[appState.lang].notes.runAction;
      } else if (status === "PREVIEW_ONLY") {
        button.textContent = I18N[appState.lang].notes.previewOnly;
      } else {
        button.textContent = I18N[appState.lang].notes.unavailable;
      }
      button.disabled = !canRun;
      button.addEventListener("click", async () => {
        if (!canRun || !action.backend_action_id) {
          return;
        }
        button.disabled = true;
        button.textContent = I18N[appState.lang].notes.running;
        await runAction(action.backend_action_id);
        renderActions(actions);
      });
      card.appendChild(button);
      container.appendChild(card);
    });
  }

  function renderLastAction() {
    const node = document.getElementById("last-action-json");
    if (!node) {
      return;
    }
    const payload = appState.lastActionResult;
    if (!payload || typeof payload !== "object") {
      node.textContent = "-";
      return;
    }
    node.textContent = JSON.stringify(payload, null, 2);
  }

  async function runAction(actionId) {
    try {
      const res = await fetch(`/api/actions/${encodeURIComponent(actionId)}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          requester: "OPERATOR_COCKPIT_L1",
          input_payload: {
            source: "operator_cockpit_l1",
            requested_at_utc: new Date().toISOString()
          }
        })
      });
      const payload = await res.json();
      appState.lastActionResult = payload && payload.action_result ? payload.action_result : payload;
    } catch (err) {
      appState.lastActionResult = {
        status: "BLOCK",
        output_summary: `action_failed:${String(err)}`
      };
    }
    renderLastAction();
  }

  async function bootstrap() {
    applyLanguage();

    const generated = await loadGeneratedState();
    appState.model = generated && typeof generated === "object" ? generated : fallbackModel();

    await loadRuntimeApi();
    renderModel();

    const focus = query.get("focus");
    if (focus) {
      const node = document.getElementById(focus);
      if (node) {
        node.scrollIntoView({ behavior: "instant", block: "start" });
      }
    }
  }

  const toggle = document.getElementById("lang-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      appState.lang = appState.lang === "en" ? "ru" : "en";
      window.localStorage.setItem("operatorCockpitLang", appState.lang);
      applyLanguage();
      renderModel();
    });
  }

  bootstrap();
})();
