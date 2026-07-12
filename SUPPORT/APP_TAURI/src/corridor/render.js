function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function safeToken(value) {
  return String(value ?? "").replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 48);
}

function renderValue(value) {
  if (value === null || value === undefined || value === "") {
    return '<span class="corridor-empty">—</span>';
  }
  if (typeof value === "object") {
    return `<pre>${escapeHtml(JSON.stringify(value, null, 2))}</pre>`;
  }
  return `<span>${escapeHtml(value)}</span>`;
}

function renderFields(fields) {
  if (!Array.isArray(fields) || fields.length === 0) return "";
  return `<dl class="corridor-fields">${fields.map((field) => {
    const tone = field?.tone ? ` tone-${safeToken(field.tone)}` : "";
    return `<div class="corridor-field${tone}">
      <dt>${escapeHtml(field?.label ?? field?.name ?? "")}</dt>
      <dd>${renderValue(field?.value)}</dd>
      ${field?.detail ? `<small>${escapeHtml(field.detail)}</small>` : ""}
    </div>`;
  }).join("")}</dl>`;
}

function renderCard(card) {
  const tone = card?.tone ? ` tone-${safeToken(card.tone)}` : "";
  return `<article class="corridor-card${tone}" data-card-id="${escapeHtml(card.id)}">
    <header>
      <h3>${escapeHtml(card?.title ?? "")}</h3>
      ${card?.status ? `<span class="corridor-status">${escapeHtml(card.status)}</span>` : ""}
    </header>
    ${card?.summary ? `<p>${escapeHtml(card.summary)}</p>` : ""}
    ${renderFields(card?.fields)}
    ${card?.data !== undefined ? `<div class="corridor-card-data">${renderValue(card.data)}</div>` : ""}
    ${Array.isArray(card?.items) ? `<ul class="corridor-items">${card.items.map((item) => `<li>${renderValue(item)}</li>`).join("")}</ul>` : ""}
  </article>`;
}

function renderOptions(field, current) {
  if (!Array.isArray(field.options)) return "";
  return field.options.map((option) => {
    const value = typeof option === "object" ? option.value : option;
    const label = typeof option === "object" ? option.label : option;
    const selected = String(value) === String(current) ? " selected" : "";
    return `<option value="${escapeHtml(value)}"${selected}>${escapeHtml(label)}</option>`;
  }).join("");
}

function renderInput(field) {
  const name = escapeHtml(field?.name ?? "");
  const label = escapeHtml(field?.label ?? field?.name ?? "");
  const current = field?.value ?? field?.default ?? "";
  const required = field?.required === true ? " required" : "";
  const placeholder = field?.placeholder ? ` placeholder="${escapeHtml(field.placeholder)}"` : "";
  const inputType = field?.type ?? "text";

  if (Array.isArray(field?.options)) {
    return `<label><span>${label}</span><select name="${name}"${required}>${renderOptions(field, current)}</select></label>`;
  }
  if (inputType === "textarea" || inputType === "json") {
    const encoded = inputType === "json" && typeof current === "object" ? JSON.stringify(current, null, 2) : current;
    return `<label><span>${label}</span><textarea name="${name}" data-value-type="${escapeHtml(inputType)}"${required}${placeholder}>${escapeHtml(encoded)}</textarea></label>`;
  }
  if (inputType === "boolean" || inputType === "checkbox") {
    return `<label class="corridor-checkbox"><input name="${name}" type="checkbox" data-value-type="boolean"${current === true ? " checked" : ""}${required}><span>${label}</span></label>`;
  }
  const allowedType = ["text", "number", "date", "datetime-local"].includes(inputType) ? inputType : "text";
  return `<label><span>${label}</span><input name="${name}" type="${allowedType}" value="${escapeHtml(current)}" data-value-type="${escapeHtml(inputType)}"${required}${placeholder}></label>`;
}

function actionFields(action) {
  const schema = action?.payload_schema;
  return Array.isArray(schema?.fields) ? schema.fields : [];
}

function renderAction(action, busy, pendingActionId) {
  const fields = actionFields(action);
  const disabled = action.enabled !== true || busy;
  const waiting = busy && pendingActionId === action.id;
  const tone = action.tone ? ` tone-${safeToken(action.tone)}` : "";
  const confirmation = typeof action.confirmation === "string"
    ? action.confirmation
    : action.confirmation === true ? action.label : "";
  return `<form class="corridor-action${tone}" data-action-id="${escapeHtml(action.id)}"${confirmation ? ` data-confirmation="${escapeHtml(confirmation)}"` : ""}>
    ${fields.length ? `<div class="corridor-action-fields">${fields.map(renderInput).join("")}</div>` : ""}
    <button type="submit"${disabled ? " disabled" : ""}>${escapeHtml(waiting ? (action.pending_label ?? action.label) : action.label)}</button>
    ${action.reason ? `<small>${escapeHtml(action.reason)}</small>` : ""}
  </form>`;
}

function renderPanel(panel, busy, pendingActionId) {
  const tone = panel.tone ? ` tone-${safeToken(panel.tone)}` : "";
  return `<section class="corridor-panel${tone}" id="panel-${escapeHtml(panel.id)}" data-panel-id="${escapeHtml(panel.id)}">
    <header class="corridor-panel-head">
      <div>
        <p class="corridor-kicker">${escapeHtml(panel.marker ?? panel.id)}</p>
        <h2>${escapeHtml(panel.title)}</h2>
      </div>
      ${panel.status ? `<span class="corridor-status">${escapeHtml(panel.status)}</span>` : ""}
    </header>
    ${panel.summary ? `<p class="corridor-summary">${escapeHtml(panel.summary)}</p>` : ""}
    <div class="corridor-cards">${panel.cards.map(renderCard).join("")}</div>
    ${panel.actions.length ? `<div class="corridor-actions">${panel.actions.map((action) => renderAction(action, busy, pendingActionId)).join("")}</div>` : ""}
  </section>`;
}

function renderHeaderFields(snapshot) {
  if (!Array.isArray(snapshot.header_fields)) return "";
  return `<div class="corridor-head-fields">${snapshot.header_fields.map((field) => `<div>
    <span>${escapeHtml(field?.label ?? field?.name ?? "")}</span>
    ${renderValue(field?.value)}
  </div>`).join("")}</div>`;
}

function renderNotices(notices) {
  if (!Array.isArray(notices) || notices.length === 0) return "";
  return `<aside class="corridor-notices" aria-label="Backend notices">${notices.map((notice) => {
    const tone = notice?.tone ? ` tone-${safeToken(notice.tone)}` : "";
    return `<div class="corridor-notice${tone}"><strong>${escapeHtml(notice?.title ?? "")}</strong><span>${escapeHtml(notice?.message ?? notice)}</span></div>`;
  }).join("")}</aside>`;
}

export function renderCorridorMarkup(snapshot, { busy = false, pendingActionId = null } = {}) {
  const title = snapshot.title ?? snapshot.contract_id;
  return `<div class="corridor-shell" data-contract-id="${escapeHtml(snapshot.contract_id)}">
    <header class="corridor-hero">
      <div class="corridor-sigil" aria-hidden="true">◈</div>
      <div>
        <p class="corridor-kicker">AUTHORITATIVE SAFE EXECUTION SPINE</p>
        <h1>${escapeHtml(title)}</h1>
        ${snapshot.subtitle ? `<p>${escapeHtml(snapshot.subtitle)}</p>` : ""}
      </div>
      ${renderHeaderFields(snapshot)}
    </header>
    ${renderNotices(snapshot.notices)}
    <nav class="corridor-nav" aria-label="Corridor panels">
      ${snapshot.panels.map((panel) => `<a href="#panel-${escapeHtml(panel.id)}" data-panel-link="${escapeHtml(panel.id)}">${escapeHtml(panel.title)}</a>`).join("")}
    </nav>
    <main class="corridor-grid">${snapshot.panels.map((panel) => renderPanel(panel, busy, pendingActionId)).join("")}</main>
  </div>`;
}

export function renderCorridor(root, view) {
  if (!root) return;
  if (!view.snapshot) {
    root.innerHTML = `<main class="corridor-boot" aria-live="polite">
      <div class="corridor-sigil" aria-hidden="true">◈</div>
      <p>${view.error ? escapeHtml(view.error) : "Loading backend corridor contract…"}</p>
    </main>`;
    return;
  }
  root.innerHTML = `${view.error ? `<div class="corridor-bridge-error" role="alert">${escapeHtml(view.error)}</div>` : ""}${renderCorridorMarkup(view.snapshot, view)}`;
}

function formPayload(form) {
  const payload = {};
  for (const element of form.elements) {
    if (!element.name || element.type === "submit") continue;
    const valueType = element.dataset.valueType;
    if (valueType === "boolean") {
      payload[element.name] = element.checked;
    } else if (valueType === "number") {
      const parsed = Number(element.value);
      if (!Number.isFinite(parsed)) throw new Error(`${element.name} must be a number`);
      payload[element.name] = parsed;
    } else if (valueType === "json") {
      payload[element.name] = JSON.parse(element.value);
    } else {
      payload[element.name] = element.value;
    }
  }
  return payload;
}

export function bindCorridorActions(root, onAction) {
  root?.querySelectorAll("form[data-action-id]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      if (button?.disabled) return;
      const confirmation = form.dataset.confirmation;
      if (confirmation && !window.confirm(confirmation)) return;
      await onAction(form.dataset.actionId, formPayload(form));
    });
  });
}
