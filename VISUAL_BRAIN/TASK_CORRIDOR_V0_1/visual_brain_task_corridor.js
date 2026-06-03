(function () {
  const DATA_PATH = "./data/visual_brain_task_corridor_state.generated.json";

  const state = {
    data: null,
    motionReduced: false,
    compactView: false,
  };

  function normalizeStatus(status, evidenceRef) {
    const value = String(status || "STUB").trim().toUpperCase();
    if (value === "PROVED_BY_RECEIPT" && !String(evidenceRef || "").trim()) {
      return "PARTIAL";
    }
    return value;
  }

  function statusClass(status) {
    return `status-${String(status || "").toLowerCase()}`;
  }

  function createNodeButton(node) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "node-btn";
    const status = normalizeStatus(node.status, node.evidence_ref);
    btn.innerHTML = `
      <div class="node-label">${node.label}</div>
      <div class="node-kind">${node.kind}</div>
      <span class="status-pill ${statusClass(status)}">${status}</span>
    `;
    btn.addEventListener("click", () => renderNodeDetail(node));
    return btn;
  }

  function createEvidenceButton(evidence) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "evidence-btn";
    btn.innerHTML = `
      <div class="node-label">${evidence.evidence_id}</div>
      <div class="node-kind">${evidence.kind}</div>
      <span class="status-pill ${statusClass(evidence.status)}">${evidence.status}</span>
    `;
    btn.addEventListener("click", () => renderEvidenceDetail(evidence));
    return btn;
  }

  function createRailItem(step) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "rail-item";
    const status = normalizeStatus(step.status, step.evidence_ref);
    item.innerHTML = `
      <div class="node-label">${step.label}</div>
      <div class="node-kind">${step.details || ""}</div>
      <span class="status-pill ${statusClass(status)}">${status}</span>
    `;
    item.addEventListener("click", () => {
      renderNodeDetail({
        label: step.label,
        kind: "RUN_RAIL",
        status,
        evidence_ref: step.evidence_ref,
        notes: [step.details || "No details"],
      });
    });
    return item;
  }

  function renderTruthMarkers(data) {
    const container = document.getElementById("truth-markers");
    container.innerHTML = "";
    const warnings = Array.isArray(data.warnings) ? data.warnings : [];
    warnings.forEach((marker) => {
      const el = document.createElement("span");
      el.className = "badge";
      el.textContent = marker;
      container.appendChild(el);
    });
  }

  function renderNodes(data) {
    const spineContainer = document.getElementById("spine-nodes");
    const organContainer = document.getElementById("organ-ring");
    spineContainer.innerHTML = "";
    organContainer.innerHTML = "";

    const allNodes = Array.isArray(data.nodes) ? data.nodes : [];
    const organKinds = new Set([
      "officio_agentis",
      "doctrinarium",
      "administratum",
      "mechanicus",
      "inquisition",
      "strategium",
      "schola_imperialis",
    ]);
    const spineOrder = [
      "owner_intent",
      "astronomicon",
      "servitor_core",
      "evidence_binder",
      "owner_verdict_gate",
    ];

    spineOrder.forEach((id) => {
      const node = allNodes.find((n) => n.node_id === id);
      if (node) {
        spineContainer.appendChild(createNodeButton(node));
      }
    });

    allNodes
      .filter((node) => organKinds.has(node.node_id))
      .forEach((node) => organContainer.appendChild(createNodeButton(node)));
  }

  function renderRunRail(data) {
    const container = document.getElementById("run-rail");
    container.innerHTML = "";
    const steps = Array.isArray(data.run_rail) ? data.run_rail : [];
    steps.forEach((step) => container.appendChild(createRailItem(step)));
  }

  function renderEvidence(data) {
    const container = document.getElementById("evidence-stars");
    container.innerHTML = "";
    const evidence = Array.isArray(data.evidence_constellation) ? data.evidence_constellation : [];
    evidence.forEach((item) => container.appendChild(createEvidenceButton(item)));
  }

  function renderNodeDetail(node) {
    const panel = document.getElementById("node-detail");
    const notes = Array.isArray(node.notes) ? node.notes : [];
    panel.innerHTML = `
      <p class="headline">${node.label}</p>
      <p><strong>Kind:</strong> ${node.kind}</p>
      <p><strong>Status:</strong> ${normalizeStatus(node.status, node.evidence_ref)}</p>
      <p><strong>Evidence ref:</strong> ${node.evidence_ref || "NONE"}</p>
      <p><strong>Notes:</strong> ${notes.join(" | ") || "No notes."}</p>
    `;
  }

  function renderEvidenceDetail(item) {
    const panel = document.getElementById("evidence-detail");
    const linked = Array.isArray(item.linked_nodes) ? item.linked_nodes.join(", ") : "none";
    panel.innerHTML = `
      <p class="headline">${item.evidence_id}</p>
      <p><strong>Kind:</strong> ${item.kind}</p>
      <p><strong>Status:</strong> ${item.status}</p>
      <p><strong>Path/Note:</strong> ${item.path_or_note}</p>
      <p><strong>Linked nodes:</strong> ${linked || "none"}</p>
    `;
  }

  function setMotionLabel() {
    const btn = document.getElementById("toggle-motion");
    btn.textContent = `Reduced Motion: ${state.motionReduced ? "On" : "Off"}`;
  }

  function bindControls() {
    const motionBtn = document.getElementById("toggle-motion");
    const viewBtn = document.getElementById("toggle-view");

    motionBtn.addEventListener("click", () => {
      state.motionReduced = !state.motionReduced;
      document.body.classList.toggle("motion-reduced", state.motionReduced);
      document.body.classList.toggle("motion-enabled", !state.motionReduced);
      setMotionLabel();
    });

    viewBtn.addEventListener("click", () => {
      state.compactView = !state.compactView;
      document.body.classList.toggle("view-compact", state.compactView);
      document.body.classList.toggle("view-detailed", !state.compactView);
      viewBtn.textContent = state.compactView ? "Switch Detailed View" : "Switch Compact View";
    });
  }

  async function bootstrap() {
    bindControls();
    setMotionLabel();

    try {
      const res = await fetch(DATA_PATH, { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      state.data = data;
      renderTruthMarkers(data);
      renderNodes(data);
      renderRunRail(data);
      renderEvidence(data);
    } catch (err) {
      const marker = document.getElementById("truth-markers");
      marker.innerHTML = '<span class="badge">MISSING_INPUT_WARN:visual_state_data</span>';
      renderNodeDetail({
        label: "Visual State Data",
        kind: "SYSTEM",
        status: "MISSING_INPUT_WARN",
        evidence_ref: "",
        notes: [`Failed to load ${DATA_PATH}: ${String(err)}`],
      });
    }
  }

  bootstrap();
})();
