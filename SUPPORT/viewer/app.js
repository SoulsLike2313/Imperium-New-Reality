/* IMPERIUM GRAPH VIEWER — app.js (v0_1)
   Renders imperium.graph.v0_1 snapshots from ../graph_snapshot.json.
   6 canonical views (V1..V6) per ORGANS/DOCTRINARIUM/IMPERIUM_GRAPH.md.
   URL filters: ?v=V2&organ=&since=&focus=&depth=
   Annotations: localStorage key 'imperium.graph.annotations.v1' (local only).
   No network calls beyond the snapshot fetch. EYES_V2 palette applied. */

(function () {
  'use strict';

  const SCHEMA = 'imperium.graph.v0_1';
  const SNAPSHOT_URL = '../graph_snapshot.json';
  const ANNOTATION_KEY = 'imperium.graph.annotations.v1';
  const VIEW_IDS = ['V1', 'V2', 'V3', 'V4', 'V5', 'V6'];
  const DEFAULT_VIEW = 'V1';
  const DEFAULT_DEPTH = 2;

  const NODE_TYPES = [
    'organ', 'sub_organ', 'doctrine', 'agent', 'task',
    'land', 'receipt', 'sentinel', 'thread',
  ];
  const EDGE_TYPES = [
    'parent_of', 'owns', 'declares_base', 'lands_after', 'ratifies',
    'gates', 'produces', 'references', 'monitors', 'succeeds',
  ];

  // ---- State ---------------------------------------------------------------
  const state = {
    graph: null,         // raw snapshot
    cy: null,            // cytoscape instance
    view: DEFAULT_VIEW,
    filters: { organ: '', since: '', focus: '', depth: DEFAULT_DEPTH, search: '' },
    selected: null,
    annotations: loadAnnotations(),
  };

  // ---- Utility -------------------------------------------------------------
  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return Array.from(document.querySelectorAll(sel)); }

  function loadAnnotations() {
    try {
      const raw = localStorage.getItem(ANNOTATION_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  }
  function saveAnnotations() {
    try {
      localStorage.setItem(ANNOTATION_KEY, JSON.stringify(state.annotations));
      return true;
    } catch (e) { return false; }
  }

  function parseUrlFilters() {
    const params = new URLSearchParams(window.location.search);
    const v = params.get('v');
    if (v && VIEW_IDS.indexOf(v) !== -1) state.view = v;
    state.filters.organ  = params.get('organ')  || '';
    state.filters.since  = params.get('since')  || '';
    state.filters.focus  = params.get('focus')  || '';
    state.filters.depth  = parseInt(params.get('depth') || DEFAULT_DEPTH, 10);
    state.filters.search = params.get('search') || '';
  }
  function writeUrlFilters() {
    const params = new URLSearchParams();
    params.set('v', state.view);
    if (state.filters.organ)  params.set('organ',  state.filters.organ);
    if (state.filters.since)  params.set('since',  state.filters.since);
    if (state.filters.focus)  params.set('focus',  state.filters.focus);
    if (state.filters.depth !== DEFAULT_DEPTH) params.set('depth', String(state.filters.depth));
    if (state.filters.search) params.set('search', state.filters.search);
    const next = window.location.pathname + '?' + params.toString();
    window.history.replaceState(null, '', next);
  }

  // ---- Style ---------------------------------------------------------------
  // EYES_V2-aligned: all node fills within violet hue 240..290. Sole accent is
  // yellow MARK on (a) selected node, (b) lands_after edges (chain spine).
  function cytoscapeStyle() {
    const c = getComputedStyle(document.documentElement);
    const cssVar = (n) => c.getPropertyValue(n).trim();
    const palette = {
      organ:     cssVar('--n-organ'),
      sub_organ: cssVar('--n-sub_organ'),
      doctrine:  cssVar('--n-doctrine'),
      agent:     cssVar('--n-agent'),
      task:      cssVar('--n-task'),
      land:      cssVar('--n-land'),
      receipt:   cssVar('--n-receipt'),
      sentinel:  cssVar('--n-sentinel'),
      thread:    cssVar('--n-thread'),
    };
    const mark = cssVar('--c-mark');
    const edgeDefault = cssVar('--e-default');
    const text = cssVar('--c-text');

    const nodeSelectors = NODE_TYPES.map((t) => ({
      selector: 'node[type = "' + t + '"]',
      style: { 'background-color': palette[t] },
    }));

    return [
      {
        selector: 'node',
        style: {
          'background-color': palette.organ,
          'label': 'data(label)',
          'color': text,
          'font-size': 9,
          'font-family': 'JetBrains Mono, Cascadia Mono, monospace',
          'text-valign': 'bottom',
          'text-margin-y': 6,
          'text-outline-color': '#0a0814',
          'text-outline-width': 2,
          'width': 14, 'height': 14,
          'border-width': 1,
          'border-color': '#1c1a3c',
        },
      },
      { selector: 'node[type = "organ"]',    style: { width: 26, height: 26, 'font-size': 11 } },
      { selector: 'node[type = "doctrine"]', style: { width: 20, height: 20, shape: 'diamond' } },
      { selector: 'node[type = "sentinel"]', style: { shape: 'triangle', width: 18, height: 18 } },
      { selector: 'node[type = "land"]',     style: { shape: 'rectangle', width: 10, height: 10 } },
      { selector: 'node[type = "receipt"]',  style: { shape: 'tag', width: 12, height: 8 } },
      { selector: 'node[type = "task"]',     style: { shape: 'round-rectangle', width: 16, height: 10 } },
      ...nodeSelectors,
      {
        selector: 'node:selected',
        style: {
          'border-color': mark,
          'border-width': 3,
          'background-blacken': -0.1,
        },
      },
      {
        selector: 'node.faded',
        style: { opacity: 0.18 },
      },
      {
        selector: 'edge',
        style: {
          'width': 1,
          'line-color': edgeDefault,
          'target-arrow-color': edgeDefault,
          'target-arrow-shape': 'triangle-backcurve',
          'curve-style': 'bezier',
          'opacity': 0.65,
          'arrow-scale': 0.7,
        },
      },
      {
        selector: 'edge[type = "lands_after"]',
        style: { 'line-color': mark, 'target-arrow-color': mark, 'width': 1.6, 'opacity': 0.85 },
      },
      {
        selector: 'edge[type = "declares_base"]',
        style: { 'line-style': 'dashed' },
      },
      {
        selector: 'edge[type = "ratifies"]',
        style: { 'line-style': 'dotted', 'width': 1.4 },
      },
      {
        selector: 'edge.faded',
        style: { 'opacity': 0.08 },
      },
    ];
  }

  // ---- View filters --------------------------------------------------------
  // Each view returns the subset of nodes & edges to render.
  function applyView(view, graph, filters) {
    let nodes = graph.nodes.slice();
    let edges = graph.edges.slice();
    const sinceISO = filters.since;

    function isAfter(node) {
      if (!sinceISO) return true;
      const t = node.created_at || node.committed_at || node.verified_at || node.last_seen;
      if (!t) return true; // keep undated nodes
      return t >= sinceISO;
    }

    function byOrgan(n) {
      if (!filters.organ) return true;
      if (n.organ === filters.organ) return true;
      if (n.type === 'organ' && n.id === 'organ:' + filters.organ) return true;
      return false;
    }

    switch (view) {
      case 'V1': // Overview — keep all, light filter
        nodes = nodes.filter((n) => byOrgan(n) && isAfter(n));
        break;
      case 'V2': // Organ drilldown — organ + sub_organ + sentinels + receipts
        nodes = nodes.filter((n) => byOrgan(n)
          && ['organ', 'sub_organ', 'sentinel', 'agent', 'doctrine'].indexOf(n.type) !== -1);
        break;
      case 'V3': // Provenance chain — lands + receipts + tasks, lands_after spine
        nodes = nodes.filter((n) => byOrgan(n)
          && ['land', 'task', 'receipt'].indexOf(n.type) !== -1
          && isAfter(n));
        break;
      case 'V4': // Time slice — only nodes after `since`
        nodes = nodes.filter((n) => byOrgan(n) && isAfter(n));
        break;
      case 'V5': // Sentinel pulse — sentinels + monitored
        const sentinelIds = new Set(
          graph.nodes.filter((n) => n.type === 'sentinel').map((n) => n.id)
        );
        const monitoredIds = new Set();
        graph.edges.forEach((e) => {
          if (e.type === 'monitors' && sentinelIds.has(e.src)) monitoredIds.add(e.dst);
        });
        nodes = nodes.filter((n) =>
          (n.type === 'sentinel' || monitoredIds.has(n.id)) && byOrgan(n));
        break;
      case 'V6': // Doctrine map — doctrines + references
        nodes = nodes.filter((n) => n.type === 'doctrine' && byOrgan(n));
        break;
      default:
        break;
    }

    // Focus node + depth: BFS expand from focus id to N hops
    if (filters.focus) {
      const focusId = filters.focus;
      const adjacency = new Map();
      graph.edges.forEach((e) => {
        if (!adjacency.has(e.src)) adjacency.set(e.src, []);
        if (!adjacency.has(e.dst)) adjacency.set(e.dst, []);
        adjacency.get(e.src).push(e.dst);
        adjacency.get(e.dst).push(e.src);
      });
      const visited = new Set();
      const queue = [[focusId, 0]];
      while (queue.length) {
        const [id, d] = queue.shift();
        if (visited.has(id)) continue;
        visited.add(id);
        if (d < filters.depth) {
          (adjacency.get(id) || []).forEach((nbr) => {
            if (!visited.has(nbr)) queue.push([nbr, d + 1]);
          });
        }
      }
      nodes = nodes.filter((n) => visited.has(n.id));
    }

    // Restrict edges to endpoints in the filtered node set
    const nodeIds = new Set(nodes.map((n) => n.id));
    edges = edges.filter((e) => nodeIds.has(e.src) && nodeIds.has(e.dst));
    return { nodes: nodes, edges: edges };
  }

  function preferredLayout(view) {
    switch (view) {
      case 'V3': return { name: 'breadthfirst', directed: true, spacingFactor: 1.4, animate: false };
      case 'V4': return { name: 'breadthfirst', directed: true, spacingFactor: 1.6, animate: false };
      case 'V6': return { name: 'concentric', minNodeSpacing: 30, animate: false };
      case 'V5': return { name: 'concentric', minNodeSpacing: 40, animate: false };
      case 'V2': return { name: 'circle', animate: false };
      default:   return { name: 'cose', animate: false, idealEdgeLength: 60, nodeRepulsion: 8000 };
    }
  }

  // ---- Render --------------------------------------------------------------
  function nodeToElement(n) {
    return {
      group: 'nodes',
      data: Object.assign({}, n, {
        id: n.id,
        label: n.label || n.title || n.task_id || n.id.split(':').pop() || n.id,
      }),
    };
  }
  function edgeToElement(e, i) {
    return {
      group: 'edges',
      data: Object.assign({}, e, {
        id: 'e' + i + ':' + e.type + ':' + e.src + '->' + e.dst,
        source: e.src,
        target: e.dst,
      }),
    };
  }

  function render() {
    const filtered = applyView(state.view, state.graph, state.filters);
    const elements = [
      ...filtered.nodes.map(nodeToElement),
      ...filtered.edges.map(edgeToElement),
    ];
    if (!state.cy) {
      state.cy = cytoscape({
        container: $('#cy'),
        elements: elements,
        style: cytoscapeStyle(),
        layout: preferredLayout(state.view),
        wheelSensitivity: 0.2,
        minZoom: 0.05,
        maxZoom: 4,
      });
      state.cy.on('tap', 'node', (evt) => selectNode(evt.target));
      state.cy.on('tap', (evt) => {
        if (evt.target === state.cy) deselect();
      });
    } else {
      state.cy.elements().remove();
      state.cy.add(elements);
      state.cy.layout(preferredLayout(state.view)).run();
    }
    applySearchHighlight();
    updateCounts(filtered);
  }

  function applySearchHighlight() {
    if (!state.cy) return;
    const q = (state.filters.search || '').toLowerCase().trim();
    state.cy.elements().removeClass('faded');
    if (!q) return;
    const matches = state.cy.nodes().filter((n) => {
      const d = n.data();
      return (d.label && d.label.toLowerCase().indexOf(q) !== -1)
          || (d.id && d.id.toLowerCase().indexOf(q) !== -1)
          || (d.task_id && d.task_id.toLowerCase().indexOf(q) !== -1);
    });
    if (matches.length === 0) return;
    const matchSet = new Set(matches.map((n) => n.id()));
    state.cy.nodes().forEach((n) => { if (!matchSet.has(n.id())) n.addClass('faded'); });
    state.cy.edges().forEach((e) => {
      if (!matchSet.has(e.source().id()) && !matchSet.has(e.target().id())) e.addClass('faded');
    });
  }

  function updateCounts(filtered) {
    const byType = {};
    NODE_TYPES.forEach((t) => byType[t] = 0);
    filtered.nodes.forEach((n) => { if (byType.hasOwnProperty(n.type)) byType[n.type]++; });
    const lines = [];
    lines.push('<strong>' + filtered.nodes.length + '</strong> nodes / <strong>' + filtered.edges.length + '</strong> edges');
    NODE_TYPES.forEach((t) => {
      if (byType[t]) lines.push(t + ': ' + byType[t]);
    });
    $('#counts').innerHTML = lines.join('<br>');
  }

  // ---- Sidebar -------------------------------------------------------------
  function selectNode(node) {
    state.selected = node.id();
    const d = node.data();
    $('#sidebar').classList.remove('hidden');
    $('#sb-type').textContent = d.type;
    $('#sb-id').textContent = d.id;
    $('#sb-label').textContent = d.label || d.id;
    const dl = $('#sb-props');
    dl.innerHTML = '';
    const keys = Object.keys(d).filter((k) =>
      ['id', 'label', 'type', 'source', 'target'].indexOf(k) === -1);
    keys.sort();
    keys.forEach((k) => {
      const dt = document.createElement('dt'); dt.textContent = k;
      const dd = document.createElement('dd');
      const v = d[k];
      dd.textContent = (typeof v === 'object') ? JSON.stringify(v) : String(v);
      dl.appendChild(dt); dl.appendChild(dd);
    });
    $('#sb-anno').value = state.annotations[d.id] || '';
    $('#sb-anno-status').textContent = '';
    renderNeighborhood(node);
  }
  function deselect() {
    state.selected = null;
    $('#sidebar').classList.add('hidden');
  }
  function renderNeighborhood(node) {
    const ul = $('#sb-neighbors');
    ul.innerHTML = '';
    const edges = node.connectedEdges();
    const seen = new Set();
    edges.forEach((e) => {
      const other = e.source().id() === node.id() ? e.target() : e.source();
      const key = e.data('type') + ':' + other.id();
      if (seen.has(key)) return;
      seen.add(key);
      const li = document.createElement('li');
      const direction = e.source().id() === node.id() ? '→' : '←';
      li.innerHTML = '<span class="edge-label">' + direction + ' ' + e.data('type') + '</span> ' + (other.data('label') || other.id());
      li.addEventListener('click', () => selectNode(other));
      ul.appendChild(li);
    });
  }

  // ---- Toolbar wiring ------------------------------------------------------
  function wireToolbar() {
    $$('#view-picker .view-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        $$('#view-picker .view-btn').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        state.view = btn.dataset.view;
        writeUrlFilters();
        render();
      });
    });
    $('#btn-apply').addEventListener('click', () => {
      state.filters.organ  = $('#f-organ').value;
      state.filters.since  = $('#f-since').value;
      state.filters.focus  = $('#f-focus').value.trim();
      state.filters.depth  = parseInt($('#f-depth').value || DEFAULT_DEPTH, 10);
      state.filters.search = $('#f-search').value.trim();
      writeUrlFilters();
      render();
    });
    $('#btn-reset').addEventListener('click', () => {
      state.filters = { organ: '', since: '', focus: '', depth: DEFAULT_DEPTH, search: '' };
      $('#f-organ').value = '';
      $('#f-since').value = '';
      $('#f-focus').value = '';
      $('#f-depth').value = DEFAULT_DEPTH;
      $('#f-search').value = '';
      writeUrlFilters();
      render();
    });
    $('#btn-fit').addEventListener('click', () => { if (state.cy) state.cy.fit(null, 40); });

    // Export
    $('#btn-export-png').addEventListener('click', () => exportImage('png'));
    $('#btn-export-svg').addEventListener('click', () => exportImage('svg'));
    $('#btn-export-json').addEventListener('click', exportFiltered);

    // Sidebar
    $('#sb-close').addEventListener('click', deselect);
    $('#sb-anno-save').addEventListener('click', () => {
      if (!state.selected) return;
      state.annotations[state.selected] = $('#sb-anno').value;
      const ok = saveAnnotations();
      $('#sb-anno-status').textContent = ok ? 'saved locally' : 'storage full';
    });
    $('#sb-anno-clear').addEventListener('click', () => {
      if (!state.selected) return;
      delete state.annotations[state.selected];
      saveAnnotations();
      $('#sb-anno').value = '';
      $('#sb-anno-status').textContent = 'cleared';
    });
  }

  function exportImage(format) {
    if (!state.cy) return;
    let blob, name;
    if (format === 'png') {
      const dataUrl = state.cy.png({ full: true, bg: '#0a0814', scale: 2 });
      blob = dataUrlToBlob(dataUrl);
      name = 'imperium-graph-' + state.view + '.png';
    } else if (format === 'svg' && state.cy.svg) {
      const svg = state.cy.svg({ full: true, bg: '#0a0814' });
      blob = new Blob([svg], { type: 'image/svg+xml' });
      name = 'imperium-graph-' + state.view + '.svg';
    } else {
      // svg plugin not loaded; fall back to png
      const dataUrl = state.cy.png({ full: true, bg: '#0a0814', scale: 2 });
      blob = dataUrlToBlob(dataUrl);
      name = 'imperium-graph-' + state.view + '.png';
    }
    downloadBlob(blob, name);
  }
  function exportFiltered() {
    const filtered = applyView(state.view, state.graph, state.filters);
    const payload = {
      schema: SCHEMA,
      generator: 'imperium.graph.viewer.v0_1',
      view: state.view,
      filters: state.filters,
      source_snapshot: state.graph.generated_at,
      counts: {
        nodes: filtered.nodes.length,
        edges: filtered.edges.length,
      },
      nodes: filtered.nodes,
      edges: filtered.edges,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    downloadBlob(blob, 'imperium-graph-' + state.view + '.json');
  }
  function dataUrlToBlob(dataUrl) {
    const parts = dataUrl.split(',');
    const byteStr = atob(parts[1]);
    const mime = parts[0].match(/data:(.*?);/)[1];
    const arr = new Uint8Array(byteStr.length);
    for (let i = 0; i < byteStr.length; i++) arr[i] = byteStr.charCodeAt(i);
    return new Blob([arr], { type: mime });
  }
  function downloadBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  // ---- Legend & organ list -------------------------------------------------
  function buildLegend() {
    const c = getComputedStyle(document.documentElement);
    const ul = $('#legend');
    NODE_TYPES.forEach((t) => {
      const li = document.createElement('li');
      const sw = document.createElement('span');
      sw.className = 'legend-swatch';
      sw.style.background = c.getPropertyValue('--n-' + t).trim();
      li.appendChild(sw);
      li.appendChild(document.createTextNode(t));
      ul.appendChild(li);
    });
  }
  function populateOrganSelect() {
    const sel = $('#f-organ');
    const organs = state.graph.nodes
      .filter((n) => n.type === 'organ')
      .map((n) => n.label || n.id.replace(/^organ:/, ''))
      .sort();
    organs.forEach((o) => {
      const opt = document.createElement('option');
      opt.value = o; opt.textContent = o;
      sel.appendChild(opt);
    });
    if (state.filters.organ) sel.value = state.filters.organ;
  }
  function syncFormFromState() {
    $('#f-organ').value  = state.filters.organ;
    $('#f-since').value  = state.filters.since;
    $('#f-focus').value  = state.filters.focus;
    $('#f-depth').value  = state.filters.depth;
    $('#f-search').value = state.filters.search;
    $$('#view-picker .view-btn').forEach((b) => {
      b.classList.toggle('active', b.dataset.view === state.view);
    });
  }

  // ---- Bootstrap -----------------------------------------------------------
  async function bootstrap() {
    parseUrlFilters();
    wireToolbar();
    buildLegend();

    let graph;
    try {
      const r = await fetch(SNAPSHOT_URL, { cache: 'no-store' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      graph = await r.json();
    } catch (err) {
      $('#snapshot-stamp').textContent = 'snapshot unreachable: ' + err.message;
      $('#counts').innerHTML = '<em style="color:var(--c-mark)">graph_snapshot.json not found at ' + SNAPSHOT_URL + '</em>';
      return;
    }
    if (!graph || graph.schema !== SCHEMA) {
      $('#snapshot-stamp').textContent = 'schema mismatch: expected ' + SCHEMA;
      return;
    }
    state.graph = graph;
    $('#snapshot-stamp').textContent = 'snapshot ' + (graph.generated_at || 'unknown')
      + '  ·  ' + (graph.counts && graph.counts.nodes) + ' / ' + (graph.counts && graph.counts.edges);
    populateOrganSelect();
    syncFormFromState();
    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap);
  } else {
    bootstrap();
  }

  // Expose for diagnostics + E3 introspection (never used by HTML directly)
  window.__IMPERIUM_VIEWER__ = {
    schema: SCHEMA,
    snapshotUrl: SNAPSHOT_URL,
    annotationKey: ANNOTATION_KEY,
    viewIds: VIEW_IDS,
    nodeTypes: NODE_TYPES,
    edgeTypes: EDGE_TYPES,
    state: state,
    applyView: applyView,
    parseUrlFilters: parseUrlFilters,
  };
})();
