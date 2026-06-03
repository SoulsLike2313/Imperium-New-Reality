const I18N = {
  en: {
    title: "IMPERIUM Agent IDE Projection",
    subtitle: "Local-only dashboard on shared truth view model",
    overview: "Overview",
    organs: "Organs",
    atlas: "File Atlas",
    languageGate: "Officio Language Gate",
    painMap: "Owner Pain Map",
    routes: "Routes",
    reportsReceipts: "Reports / Receipts",
    blockFoundation: "Block Foundation",
    privacyNote: "PRIVATE/LOCAL data is projection-restricted by policy.",
    refresh: "Refresh",
  },
  ru: {
    title: "IMPERIUM Agent IDE Проекция",
    subtitle: "Локальный dashboard на общем truth view model",
    overview: "Обзор",
    organs: "Органы",
    atlas: "Атлас файлов",
    languageGate: "Officio Language Gate",
    painMap: "Карта болей Owner",
    routes: "Маршруты",
    reportsReceipts: "Отчёты / Квитанции",
    blockFoundation: "Block Foundation",
    privacyNote: "PRIVATE/LOCAL данные в проекции показываются только в summary-режиме.",
    refresh: "Обновить",
  },
};

let lang = "en";

function t(key) {
  return (I18N[lang] || I18N.en)[key] || key;
}

function pretty(obj) {
  return JSON.stringify(obj, null, 2);
}

function setLanguage(next) {
  lang = next;
  document.documentElement.lang = lang;
  document.getElementById("title").textContent = t("title");
  document.getElementById("subtitle").textContent = t("subtitle");
  document.getElementById("privacyNote").textContent = t("privacyNote");
  document.getElementById("refreshBtn").textContent = t("refresh");
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.getAttribute("data-i18n"));
  });
  document.getElementById("langBtn").textContent = lang === "en" ? "RU" : "EN";
}

async function loadProjection() {
  const [dashboardRes, blockRes] = await Promise.all([
    fetch("/api/view-model", { cache: "no-store" }),
    fetch("/api/block-view-model", { cache: "no-store" }),
  ]);
  const dashboard = await dashboardRes.json();
  const block = await blockRes.json();

  const overview = {
    task_id: dashboard.task_id,
    generated_at_utc: dashboard.generated_at_utc,
    current_head: dashboard.truth?.git?.head || "UNKNOWN",
    branch: dashboard.truth?.git?.branch || "UNKNOWN",
    organ_count: Array.isArray(dashboard.organs) ? dashboard.organs.length : 0,
    unknown_file_kind_count: dashboard.atlas_summary?.unknown_file_kind_count ?? 0,
    required_route_alias: dashboard.truth?.required_route_alias || "imperium-vm3",
    restricted_projection_count: dashboard.projection_guard?.private_local_restricted_count ?? 0,
    warnings_count: Array.isArray(dashboard.warnings) ? dashboard.warnings.length : 0,
    self_validator_status: dashboard.self_validator_surface?.status || "UNPROVEN",
  };
  document.getElementById("overviewBox").textContent = pretty(overview);

  const organsGrid = document.getElementById("organsGrid");
  organsGrid.innerHTML = "";
  (dashboard.organs || []).forEach((organ) => {
    const tile = document.createElement("div");
    tile.className = "organ-pill";
    tile.textContent = `${organ.organ}: ${organ.file_count} (${organ.status})`;
    organsGrid.appendChild(tile);
  });

  const atlasSummary = {
    ...dashboard.atlas_summary,
    classification_counts: dashboard.classification_counts || {},
  };
  document.getElementById("atlasBox").textContent = pretty(atlasSummary);

  const languageGate = dashboard.language_gate_surface || {};
  document.getElementById("languageGateBox").textContent = pretty(languageGate);

  const painList = document.getElementById("painList");
  painList.innerHTML = "";
  const pains = dashboard.owner_pain_surface?.pain_items || [];
  if (!pains.length) {
    const empty = document.createElement("div");
    empty.className = "pain-item";
    empty.textContent = "NO_PAIN_ITEMS";
    painList.appendChild(empty);
  } else {
    pains.forEach((pain) => {
      const item = document.createElement("div");
      item.className = "pain-item";
      item.textContent = `${pain.pain_id} | ${pain.severity} | ${pain.current_status}`;
      painList.appendChild(item);
    });
  }

  const routes = {
    required_alias: dashboard.route_surface?.required_alias || "imperium-vm3",
    imperium_vm3_visible: dashboard.route_surface?.imperium_vm3_visible ?? false,
    canonical_commands_file: dashboard.route_surface?.canonical_commands_file || "",
  };
  document.getElementById("routesBox").textContent = pretty(routes);

  document.getElementById("reportsBox").textContent = pretty(dashboard.report_receipt_summary || {});
  document.getElementById("blockBox").textContent = pretty({
    preview: dashboard.block_foundation_preview || {},
    warnings: block.warnings || [],
  });

  document.getElementById("statusNote").textContent = `head: ${overview.current_head} | alias: ${routes.required_alias} | unknown: ${overview.unknown_file_kind_count}`;
}

document.getElementById("langBtn").addEventListener("click", () => {
  setLanguage(lang === "en" ? "ru" : "en");
});

document.getElementById("refreshBtn").addEventListener("click", () => {
  loadProjection().catch((err) => {
    document.getElementById("statusNote").textContent = String(err);
  });
});

setLanguage(lang);
loadProjection().catch((err) => {
  document.getElementById("statusNote").textContent = String(err);
});
