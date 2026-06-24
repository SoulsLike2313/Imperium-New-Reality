/* IMPERIUM GRAPH VIEWER — app.js (v0_2)
   Renders imperium.graph.v0_1 snapshots from ../graph_snapshot.json.
   7 canonical views (V0 Outline + V1..V6) per IMPERIUM_GRAPH doctrine.
   URL filters: ?v=V2&organ=&since=&focus=&depth=&search=&pins=a,b,c
   Annotations: localStorage 'imperium.graph.annotations.v1' (client-only).
   AAA pass: LOD labels, hover tooltips, mini-map, history, pin/bundle,
             multi-format LLM context export, organ-grouped V1, strict V3. */

(function () {
  'use strict';

  const SCHEMA = 'imperium.graph.v0_1';
  const SNAPSHOT_URL = '../graph_snapshot.json';
  const ANNOTATION_KEY = 'imperium.graph.annotations.v1';
  const VIEW_IDS = ['V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'];
  const DEFAULT_VIEW = 'V1';
  const DEFAULT_DEPTH = 2;

  const NODE_TYPES = ['organ', 'sub_organ', 'doctrine', 'agent', 'task', 'land', 'receipt', 'sentinel', 'thread'];
  const EDGE_TYPES = ['parent_of', 'owns', 'declares_base', 'lands_after', 'ratifies', 'gates', 'produces', 'references', 'monitors', 'succeeds'];

  // ---- State ---------------------------------------------------------------
  const state = {
    graph: null,
    cy: null,
    mini: null,
    view: DEFAULT_VIEW,
    filters: { organ: '', since: '', focus: '', depth: DEFAULT_DEPTH, search: '', annotatedOnly: false },
    selected: null,
    pins: new Set(),       // pinned node ids (multi-select bundle)
    history: [],           // selection history (back stack)
    annotations: loadAnnotations(),
  };

  // ---- Utility -------------------------------------------------------------
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  function toast(msg, ms) {
    const t = $('#toast');
    t.textContent = msg;
    t.classList.remove('hidden');
    clearTimeout(toast._h);
    toast._h = setTimeout(() => t.classList.add('hidden'), ms || 1800);
  }
  function loadAnnotations() {
    try { return JSON.parse(localStorage.getItem(ANNOTATION_KEY) || '{}'); } catch (e) { return {}; }
  }
  function saveAnnotations() {
    try { localStorage.setItem(ANNOTATION_KEY, JSON.stringify(state.annotations)); return true; }
    catch (e) { return false; }
  }

  function parseUrlFilters() {
    const p = new URLSearchParams(window.location.search);
    const v = p.get('v');
    if (v && VIEW_IDS.indexOf(v) !== -1) state.view = v;
    state.filters.organ  = p.get('organ')  || '';
    state.filters.since  = p.get('since')  || '';
    state.filters.focus  = p.get('focus')  || '';
    state.filters.depth  = parseInt(p.get('depth') || DEFAULT_DEPTH, 10);
    state.filters.search = p.get('search') || '';
    state.filters.annotatedOnly = p.get('anno') === '1';
    const pinsParam = p.get('pins');
    if (pinsParam) pinsParam.split(',').filter(Boolean).forEach((id) => state.pins.add(id));
  }
  function writeUrlFilters() {
    const p = new URLSearchParams();
    p.set('v', state.view);
    if (state.filters.organ)  p.set('organ',  state.filters.organ);
    if (state.filters.since)  p.set('since',  state.filters.since);
    if (state.filters.focus)  p.set('focus',  state.filters.focus);
    if (state.filters.depth !== DEFAULT_DEPTH) p.set('depth', String(state.filters.depth));
    if (state.filters.search) p.set('search', state.filters.search);
    if (state.filters.annotatedOnly) p.set('anno', '1');
    if (state.pins.size) p.set('pins', Array.from(state.pins).join(','));
    window.history.replaceState(null, '', window.location.pathname + '?' + p.toString());
  }

  // ---- Style ---------------------------------------------------------------
  function cyStyle() {
    const c = getComputedStyle(document.documentElement);
    const v = (n) => c.getPropertyValue(n).trim();
    const palette = {};
    NODE_TYPES.forEach((t) => { palette[t] = v('--n-' + t); });
    const mark = v('--c-mark');
    const edgeDefault = v('--e-default');
    const text = v('--c-text-vivid');

    const typed = NODE_TYPES.map((t) => ({
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
          'font-size': 10,
          'font-family': 'JetBrains Mono, ui-monospace, monospace',
          'text-valign': 'bottom',
          'text-margin-y': 6,
          'text-outline-color': '#07061a',
          'text-outline-width': 2.5,
          'text-opacity': 1,
          'width': 14, 'height': 14,
          'border-width': 1,
          'border-color': '#1c1a3c',
          'transition-property': 'background-color, border-color, border-width, opacity',
          'transition-duration': 200,
        },
      },
      { selector: 'node[type = "organ"]',    style: { width: 42, height: 42, 'font-size': 13, 'font-weight': 'bold' } },
      { selector: 'node[type = "sub_organ"]',style: { width: 22, height: 22 } },
      { selector: 'node[type = "doctrine"]', style: { width: 20, height: 20, shape: 'diamond' } },
      { selector: 'node[type = "sentinel"]', style: { shape: 'triangle', width: 20, height: 20 } },
      { selector: 'node[type = "land"]',     style: { shape: 'rectangle', width: 11, height: 11 } },
      { selector: 'node[type = "receipt"]',  style: { shape: 'tag', width: 14, height: 9 } },
      { selector: 'node[type = "task"]',     style: { shape: 'round-rectangle', width: 18, height: 11 } },
      ...typed,
      // organ-cluster compound parents (V1 grouping)
      {
        selector: 'node.organ-group',
        style: {
          'background-color': 'rgba(180, 168, 255, 0.04)',
          'background-opacity': 1,
          'border-color': 'rgba(180, 168, 255, 0.22)',
          'border-width': 1,
          'shape': 'round-rectangle',
          'label': 'data(label)',
          'color': 'rgba(216, 212, 255, 0.55)',
          'font-size': 12,
          'text-valign': 'top',
          'text-halign': 'center',
          'text-margin-y': -4,
          'text-outline-width': 0,
          'padding': 16,
        },
      },
      // annotation ring (yellow MARK)
      {
        selector: 'node.has-annotation',
        style: {
          'border-color': mark,
          'border-width': 2,
          'border-opacity': 0.85,
        },
      },
      // pinned
      {
        selector: 'node.pinned',
        style: {
          'border-color': mark,
          'border-width': 3,
          'overlay-color': mark,
          'overlay-opacity': 0.18,
          'overlay-padding': 4,
        },
      },
      // selected
      {
        selector: 'node:selected',
        style: {
          'border-color': mark,
          'border-width': 3,
          'background-blacken': -0.12,
        },
      },
      // faded by search miss
      { selector: 'node.faded', style: { opacity: 0.12, 'text-opacity': 0 } },
      // LOD: label hidden when zoomed-out or type minor
      { selector: 'node.label-off', style: { 'text-opacity': 0 } },
      {
        selector: 'edge',
        style: {
          'width': 1,
          'line-color': edgeDefault,
          'target-arrow-color': edgeDefault,
          'target-arrow-shape': 'triangle-backcurve',
          'curve-style': 'bezier',
          'opacity': 0.55,
          'arrow-scale': 0.7,
          'transition-property': 'opacity, width, line-color',
          'transition-duration': 200,
        },
      },
      { selector: 'edge[type = "lands_after"]',
        style: { 'line-color': mark, 'target-arrow-color': mark, 'width': 1.8, 'opacity': 0.85 } },
      { selector: 'edge[type = "declares_base"]', style: { 'line-style': 'dashed' } },
      { selector: 'edge[type = "ratifies"]', style: { 'line-style': 'dotted', 'width': 1.4 } },
      { selector: 'edge.faded', style: { opacity: 0.06 } },
      { selector: 'edge.highlighted', style: { 'line-color': mark, 'target-arrow-color': mark, opacity: 0.95, width: 2 } },
    ];
  }

  // ---- View filters --------------------------------------------------------
  function isAfter(node, sinceISO) {
    if (!sinceISO) return true;
    const t = node.created_at || node.committed_at || node.verified_at || node.last_seen;
    return !t || t >= sinceISO;
  }
  function byOrgan(n, organ) {
    if (!organ) return true;
    if (n.organ === organ) return true;
    if (n.type === 'organ' && (n.id === 'organ:' + organ || n.label === organ)) return true;
    return false;
  }

  function applyView(view, graph, filters) {
    let nodes = graph.nodes.slice();
    let edges = graph.edges.slice();
    const f = filters;

    switch (view) {
      case 'V1':
        nodes = nodes.filter((n) => byOrgan(n, f.organ) && isAfter(n, f.since));
        break;
      case 'V2':
        nodes = nodes.filter((n) => byOrgan(n, f.organ)
          && ['organ', 'sub_organ', 'sentinel', 'agent', 'doctrine'].indexOf(n.type) !== -1);
        break;
      case 'V3': {
        // STRICT: only nodes incident to at least one lands_after edge
        const inChain = new Set();
        graph.edges.forEach((e) => {
          if (e.type === 'lands_after') { inChain.add(e.src); inChain.add(e.dst); }
        });
        nodes = nodes.filter((n) => inChain.has(n.id) && byOrgan(n, f.organ) && isAfter(n, f.since));
        break;
      }
      case 'V4':
        nodes = nodes.filter((n) => byOrgan(n, f.organ) && isAfter(n, f.since));
        break;
      case 'V5': {
        const sentinels = new Set(graph.nodes.filter((n) => n.type === 'sentinel').map((n) => n.id));
        const monitored = new Set();
        graph.edges.forEach((e) => {
          if (e.type === 'monitors' && sentinels.has(e.src)) monitored.add(e.dst);
        });
        nodes = nodes.filter((n) => (n.type === 'sentinel' || monitored.has(n.id)) && byOrgan(n, f.organ));
        break;
      }
      case 'V6':
        nodes = nodes.filter((n) => n.type === 'doctrine' && byOrgan(n, f.organ));
        break;
      default:
        break;
    }

    // Focus BFS
    if (f.focus) {
      const adj = new Map();
      graph.edges.forEach((e) => {
        if (!adj.has(e.src)) adj.set(e.src, []);
        if (!adj.has(e.dst)) adj.set(e.dst, []);
        adj.get(e.src).push(e.dst); adj.get(e.dst).push(e.src);
      });
      const visited = new Set(), q = [[f.focus, 0]];
      while (q.length) {
        const [id, d] = q.shift();
        if (visited.has(id)) continue;
        visited.add(id);
        if (d < f.depth) (adj.get(id) || []).forEach((n) => { if (!visited.has(n)) q.push([n, d + 1]); });
      }
      nodes = nodes.filter((n) => visited.has(n.id));
    }

    // Annotated-only filter
    if (f.annotatedOnly) {
      nodes = nodes.filter((n) => state.annotations[n.id]);
    }

    const ids = new Set(nodes.map((n) => n.id));
    edges = edges.filter((e) => ids.has(e.src) && ids.has(e.dst));
    return { nodes, edges };
  }

  function buildOrganGroups(filtered) {
    // For V1: wrap each node with .organ attribute in a compound parent
    // "group:<ORGAN>". Untagged nodes stay top-level.
    const groups = new Set();
    filtered.nodes.forEach((n) => { if (n.organ) groups.add(n.organ); });
    const groupNodes = Array.from(groups).map((g) => ({
      data: { id: 'group:' + g, label: g, type: 'organ-group' },
      classes: 'organ-group',
    }));
    const wrapped = filtered.nodes.map((n) => {
      const el = nodeElement(n);
      if (n.organ && groups.has(n.organ)) el.data.parent = 'group:' + n.organ;
      return el;
    });
    return [...groupNodes, ...wrapped];
  }

  function preferredLayout(view, nodeCount) {
    switch (view) {
      case 'V1':
        // Organ-grouped V1: use cose with compound bounds; smaller graphs OK with circle
        return { name: 'cose', animate: false, idealEdgeLength: 70, nodeRepulsion: 18000,
                 nestingFactor: 1.2, gravity: 0.15, numIter: 1200, randomize: false, padding: 30 };
      case 'V2': return { name: 'circle', animate: false, padding: 30 };
      case 'V3': return { name: 'breadthfirst', directed: true, spacingFactor: 1.5, animate: false, padding: 30 };
      case 'V4': return { name: 'breadthfirst', directed: true, spacingFactor: 1.7, animate: false, padding: 30 };
      case 'V5': return { name: 'concentric', minNodeSpacing: 40, animate: false, padding: 30,
                          concentric: (n) => n.data('type') === 'sentinel' ? 10 : 1 };
      case 'V6': return { name: 'concentric', minNodeSpacing: 35, animate: false, padding: 30 };
      default:   return { name: 'cose', animate: false };
    }
  }

  // ---- Element helpers -----------------------------------------------------
  function nodeElement(n) {
    const hasAnno = !!state.annotations[n.id];
    const cls = [];
    if (hasAnno) cls.push('has-annotation');
    if (state.pins.has(n.id)) cls.push('pinned');
    return {
      group: 'nodes',
      data: Object.assign({}, n, {
        id: n.id,
        label: n.label || n.title || n.task_id || (n.id.split(':').pop()) || n.id,
      }),
      classes: cls.join(' '),
    };
  }
  function edgeElement(e, i) {
    return {
      group: 'edges',
      data: Object.assign({}, e, {
        id: 'e' + i + ':' + e.type + ':' + e.src + '->' + e.dst,
        source: e.src, target: e.dst,
      }),
    };
  }

  // ---- Render --------------------------------------------------------------
  function render() {
    const filtered = applyView(state.view, state.graph, state.filters);
    let elements;
    if (state.view === 'V1') {
      elements = [
        ...buildOrganGroups(filtered),
        ...filtered.edges.map(edgeElement),
      ];
    } else {
      elements = [
        ...filtered.nodes.map(nodeElement),
        ...filtered.edges.map(edgeElement),
      ];
    }

    if (!state.cy) {
      state.cy = cytoscape({
        container: $('#cy'),
        elements,
        style: cyStyle(),
        layout: preferredLayout(state.view, filtered.nodes.length),
        wheelSensitivity: 0.2,
        minZoom: 0.04,
        maxZoom: 4.5,
      });
      wireCanvas();
    } else {
      state.cy.elements().remove();
      state.cy.add(elements);
      state.cy.layout(preferredLayout(state.view, filtered.nodes.length)).run();
    }
    applyLodLabels();
    applySearchHighlight();
    updateCounts(filtered);
    refreshMinimap(elements);
    refreshSelectionBundle();
  }

  function applyLodLabels() {
    if (!state.cy) return;
    const z = state.cy.zoom();
    const total = state.cy.nodes(':childless').length;
    // strategy: when graph is dense AND zoomed out, hide labels for minor types
    const dense = total > 80;
    const veryDense = total > 200;
    state.cy.nodes(':childless').forEach((n) => {
      const t = n.data('type');
      let show = true;
      if (veryDense && z < 1.2) show = (t === 'organ' || t === 'sub_organ');
      else if (dense && z < 0.8) show = (t === 'organ' || t === 'sub_organ' || t === 'doctrine');
      else if (z < 0.45) show = (t === 'organ');
      n.toggleClass('label-off', !show);
    });
  }

  function applySearchHighlight() {
    if (!state.cy) return;
    const q = (state.filters.search || '').toLowerCase().trim();
    state.cy.elements().removeClass('faded');
    if (!q) return;
    const matches = state.cy.nodes(':childless').filter((n) => {
      const d = n.data();
      return (d.label && d.label.toLowerCase().indexOf(q) !== -1)
          || (d.id && d.id.toLowerCase().indexOf(q) !== -1)
          || (d.task_id && d.task_id.toLowerCase().indexOf(q) !== -1);
    });
    if (!matches.length) return;
    const matchIds = new Set(matches.map((n) => n.id()));
    state.cy.nodes(':childless').forEach((n) => { if (!matchIds.has(n.id())) n.addClass('faded'); });
    state.cy.edges().forEach((e) => {
      if (!matchIds.has(e.source().id()) && !matchIds.has(e.target().id())) e.addClass('faded');
    });
  }

  function updateCounts(filtered) {
    const byType = {};
    NODE_TYPES.forEach((t) => byType[t] = 0);
    filtered.nodes.forEach((n) => { if (byType.hasOwnProperty(n.type)) byType[n.type]++; });
    const lines = ['<strong>' + filtered.nodes.length + '</strong> nodes / <strong>' + filtered.edges.length + '</strong> edges'];
    NODE_TYPES.forEach((t) => { if (byType[t]) lines.push(t + ': ' + byType[t]); });
    const annoCount = Object.keys(state.annotations).length;
    if (annoCount) lines.push('<span style="color:var(--c-mark)">✱ ' + annoCount + ' annotated</span>');
    $('#counts').innerHTML = lines.join('<br>');
  }

  // ---- Hover tooltip + canvas events ---------------------------------------
  function wireCanvas() {
    let hoverNode = null;
    state.cy.on('mouseover', 'node', (evt) => {
      const n = evt.target;
      if (n.hasClass('organ-group')) return;
      hoverNode = n.id();
      showTooltip(n, evt.originalEvent);
    });
    state.cy.on('mousemove', (evt) => {
      if (!hoverNode) return;
      moveTooltip(evt.originalEvent);
    });
    state.cy.on('mouseout', 'node', () => { hoverNode = null; hideTooltip(); });
    state.cy.on('tap', 'node', (evt) => {
      const n = evt.target;
      if (n.hasClass('organ-group')) return;
      const shift = evt.originalEvent && evt.originalEvent.shiftKey;
      if (shift) togglePin(n.id());
      else selectNode(n);
    });
    state.cy.on('tap', (evt) => { if (evt.target === state.cy) deselect(); });
    state.cy.on('zoom pan', () => { applyLodLabels(); updateMinimapViewport(); });
  }

  function showTooltip(node, mouseEv) {
    const d = node.data();
    const t = $('#hover-tooltip');
    const anno = state.annotations[d.id];
    let html =
      '<div class="tt-type">' + escape(d.type) + (anno ? ' · ✱ annotated' : '') + '</div>' +
      '<div class="tt-label">' + escape(d.label || d.id) + '</div>' +
      '<div class="tt-id">' + escape(d.id) + '</div>';
    if (d.organ && d.type !== 'organ') html += '<div class="tt-id">organ: ' + escape(d.organ) + '</div>';
    if (anno) html += '<div class="tt-anno">' + escape(anno.slice(0, 280)) + (anno.length > 280 ? '…' : '') + '</div>';
    t.innerHTML = html;
    t.classList.remove('hidden');
    moveTooltip(mouseEv);
  }
  function moveTooltip(mouseEv) {
    if (!mouseEv) return;
    const t = $('#hover-tooltip');
    const x = mouseEv.clientX + 14;
    const y = mouseEv.clientY + 14;
    const w = t.offsetWidth, h = t.offsetHeight;
    const maxX = window.innerWidth - w - 12;
    const maxY = window.innerHeight - h - 12;
    t.style.left = Math.min(x, maxX) + 'px';
    t.style.top = Math.min(y, maxY) + 'px';
  }
  function hideTooltip() { $('#hover-tooltip').classList.add('hidden'); }
  function escape(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

  // ---- Selection / sidebar -------------------------------------------------
  function selectNode(node, pushHistory) {
    const prev = state.selected;
    state.selected = node.id();
    if (pushHistory !== false && prev && prev !== node.id()) state.history.push(prev);
    const d = node.data();
    $('#sidebar').classList.remove('hidden');
    $('#sb-type').textContent = d.type;
    $('#sb-id').textContent = d.id;
    $('#sb-label').textContent = d.label || d.id;
    renderBreadcrumb(d);
    const dl = $('#sb-props');
    dl.innerHTML = '';
    const keys = Object.keys(d).filter((k) => ['id','label','type','source','target'].indexOf(k) === -1).sort();
    keys.forEach((k) => {
      const dt = document.createElement('dt'); dt.textContent = k;
      const dd = document.createElement('dd');
      const v = d[k]; dd.textContent = (typeof v === 'object') ? JSON.stringify(v) : String(v);
      dl.appendChild(dt); dl.appendChild(dd);
    });
    $('#sb-anno').value = state.annotations[d.id] || '';
    $('#sb-anno-status').textContent = state.annotations[d.id] ? '✱ saved' : '';
    renderNeighborhood(node);
  }
  function renderBreadcrumb(d) {
    const el = $('#sb-breadcrumb');
    el.innerHTML = '';
    const parts = [];
    if (d.organ) parts.push(d.organ);
    if (d.sub_organ) parts.push(d.sub_organ);
    if (d.type !== 'organ' && d.type !== 'sub_organ') parts.push(d.type);
    if (!parts.length) { el.style.display = 'none'; return; }
    el.style.display = '';
    el.innerHTML = parts.map((p) => '<span class="crumb">' + escape(p) + '</span>').join(' › ');
  }
  function deselect() {
    state.selected = null;
    $('#sidebar').classList.add('hidden');
  }
  function renderNeighborhood(node) {
    const ul = $('#sb-neighbors');
    ul.innerHTML = '';
    const seen = new Set();
    node.connectedEdges().forEach((e) => {
      const other = e.source().id() === node.id() ? e.target() : e.source();
      if (other.hasClass('organ-group')) return;
      const key = e.data('type') + ':' + other.id();
      if (seen.has(key)) return;
      seen.add(key);
      const li = document.createElement('li');
      const dir = e.source().id() === node.id() ? '→' : '←';
      li.innerHTML = '<span class="edge-label">' + escape(dir + ' ' + e.data('type')) + '</span> ' + escape(other.data('label') || other.id());
      li.addEventListener('click', () => selectNode(other));
      ul.appendChild(li);
    });
  }
  function goBack() {
    if (!state.history.length) return toast('no history');
    const prev = state.history.pop();
    const n = state.cy.getElementById(prev);
    if (n && n.length) selectNode(n, false);
    else toast('previous node not in current view');
  }
  function togglePin(id) {
    if (state.pins.has(id)) {
      state.pins.delete(id);
      toast('unpinned');
    } else {
      state.pins.add(id);
      toast('pinned (' + state.pins.size + ' total)');
    }
    const node = state.cy.getElementById(id);
    if (node) node.toggleClass('pinned');
    refreshSelectionBundle();
    writeUrlFilters();
  }
  function clearPins() {
    state.pins.forEach((id) => {
      const n = state.cy.getElementById(id);
      if (n) n.removeClass('pinned');
    });
    state.pins.clear();
    refreshSelectionBundle();
    writeUrlFilters();
    toast('pins cleared');
  }
  function refreshSelectionBundle() {
    const el = $('#selection-bundle');
    if (!state.pins.size) { el.classList.add('hidden'); return; }
    el.classList.remove('hidden');
    $('#selection-count').textContent = state.pins.size;
  }

  // ---- Mini-map ------------------------------------------------------------
  function refreshMinimap(elements) {
    if (!state.cy) return;
    if (!state.mini) {
      state.mini = cytoscape({
        container: $('#minimap-cy'),
        elements: cloneElementsForMini(elements),
        style: miniStyle(),
        layout: { name: 'preset' },
        userZoomingEnabled: false,
        userPanningEnabled: false,
        boxSelectionEnabled: false,
        autoungrabify: true,
      });
      $('#minimap').addEventListener('mousedown', miniDragStart);
    } else {
      state.mini.elements().remove();
      state.mini.add(cloneElementsForMini(elements));
    }
    // sync positions from main cy after layout
    setTimeout(() => {
      if (!state.cy || !state.mini) return;
      state.cy.nodes(':childless').forEach((n) => {
        const m = state.mini.getElementById(n.id());
        if (m && m.length) m.position(n.position());
      });
      state.mini.fit(undefined, 8);
      updateMinimapViewport();
    }, 200);
  }
  function cloneElementsForMini(elements) {
    return elements.filter((el) => !(el.classes && el.classes.indexOf('organ-group') !== -1))
      .map((el) => ({ group: el.group, data: Object.assign({}, el.data) }));
  }
  function miniStyle() {
    const c = getComputedStyle(document.documentElement);
    return [
      { selector: 'node', style: {
          'background-color': c.getPropertyValue('--n-organ').trim(),
          'width': 6, 'height': 6, 'label': '', 'border-width': 0,
      }},
      ...NODE_TYPES.map((t) => ({
        selector: 'node[type = "' + t + '"]',
        style: { 'background-color': c.getPropertyValue('--n-' + t).trim() },
      })),
      { selector: 'node[type = "organ"]', style: { width: 10, height: 10 } },
      { selector: 'edge', style: {
          'width': 0.5, 'curve-style': 'haystack',
          'line-color': c.getPropertyValue('--e-default').trim(), 'opacity': 0.35,
      }},
      { selector: 'edge[type = "lands_after"]', style: {
          'line-color': c.getPropertyValue('--c-mark').trim(), 'opacity': 0.8, 'width': 0.8,
      }},
    ];
  }
  function updateMinimapViewport() {
    if (!state.cy || !state.mini) return;
    const main = state.cy;
    const mini = state.mini;
    const ext = main.extent();
    const miniExt = mini.extent();
    const miniW = mini.width(), miniH = mini.height();
    const sx = miniW / (miniExt.w || 1), sy = miniH / (miniExt.h || 1);
    const x1 = (ext.x1 - miniExt.x1) * sx, y1 = (ext.y1 - miniExt.y1) * sy;
    const w = ext.w * sx, h = ext.h * sy;
    const vp = $('#minimap-viewport');
    vp.style.left = Math.max(0, x1) + 'px';
    vp.style.top = Math.max(0, y1) + 'px';
    vp.style.width = Math.min(miniW, w) + 'px';
    vp.style.height = Math.min(miniH, h) + 'px';
  }
  function miniDragStart(ev) {
    if (ev.target.id === 'minimap-viewport') return;
    panToMiniPoint(ev);
    const move = (e) => panToMiniPoint(e);
    const up = () => {
      window.removeEventListener('mousemove', move);
      window.removeEventListener('mouseup', up);
    };
    window.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
  }
  function panToMiniPoint(ev) {
    if (!state.cy || !state.mini) return;
    const rect = $('#minimap').getBoundingClientRect();
    const mx = ev.clientX - rect.left;
    const my = ev.clientY - rect.top;
    const mini = state.mini;
    const miniExt = mini.extent();
    const miniW = mini.width(), miniH = mini.height();
    const sx = (miniExt.w || 1) / miniW, sy = (miniExt.h || 1) / miniH;
    const targetX = miniExt.x1 + mx * sx;
    const targetY = miniExt.y1 + my * sy;
    const main = state.cy;
    const z = main.zoom();
    main.pan({
      x: main.width() / 2 - targetX * z,
      y: main.height() / 2 - targetY * z,
    });
  }

  // ---- Toolbar wiring ------------------------------------------------------
  function wireToolbar() {
    $$('#view-picker .view-btn').forEach((btn) => {
      btn.addEventListener('click', () => switchView(btn.dataset.view));
    });
    $('#btn-apply').addEventListener('click', () => {
      state.filters.organ  = $('#f-organ').value;
      state.filters.since  = $('#f-since').value;
      state.filters.focus  = $('#f-focus').value.trim();
      state.filters.depth  = parseInt($('#f-depth').value || DEFAULT_DEPTH, 10);
      state.filters.search = $('#f-search').value.trim();
      state.filters.annotatedOnly = $('#f-annotated-only').checked;
      writeUrlFilters();
      render();
    });
    $('#btn-reset').addEventListener('click', () => {
      state.filters = { organ: '', since: '', focus: '', depth: DEFAULT_DEPTH, search: '', annotatedOnly: false };
      $('#f-organ').value = ''; $('#f-since').value = ''; $('#f-focus').value = '';
      $('#f-depth').value = DEFAULT_DEPTH; $('#f-search').value = '';
      $('#f-annotated-only').checked = false;
      writeUrlFilters(); render();
    });
    $('#btn-fit').addEventListener('click', () => { if (state.cy) state.cy.fit(null, 40); });
    $('#btn-back').addEventListener('click', goBack);
    $('#btn-pin').addEventListener('click', () => { if (state.selected) togglePin(state.selected); else toast('no selection'); });
    $('#btn-clear-pins').addEventListener('click', clearPins);

    // Export
    $('#btn-export-png').addEventListener('click', () => exportImage('png'));
    $('#btn-export-svg').addEventListener('click', () => exportImage('svg'));
    $('#btn-export-json').addEventListener('click', exportFiltered);
    $('#btn-export-annotations').addEventListener('click', exportAnnotations);
    $('#btn-import-annotations').addEventListener('click', () => $('#file-import-annotations').click());
    $('#file-import-annotations').addEventListener('change', importAnnotations);

    // LLM
    $('#btn-open-llm').addEventListener('click', openLlmOverlay);
    $('#sb-llm-short').addEventListener('click', () => quickLlmCopy('selection', 0));
    $('#sb-llm-medium').addEventListener('click', () => quickLlmCopy('selection', 1));
    $('#sb-llm-full').addEventListener('click', () => quickLlmCopy('selection', 2));
    $('#llm-copy').addEventListener('click', () => { copyText($('#llm-text').value); toast('LLM context copied'); });
    $('#llm-download').addEventListener('click', () => downloadText($('#llm-text').value, 'imperium-llm-context.md'));
    $('#llm-regen').addEventListener('click', regenerateLlmText);
    $('#llm-close').addEventListener('click', () => closeOverlay('#llm-overlay'));
    ['llm-scope', 'llm-depth', 'llm-format', 'llm-include-annos'].forEach((id) => {
      $('#' + id).addEventListener('change', regenerateLlmText);
    });

    // Outline
    $('#outline-copy').addEventListener('click', () => { copyText($('#outline-text').value); toast('Outline copied'); });
    $('#outline-download').addEventListener('click', () => downloadText($('#outline-text').value, 'imperium-outline.md'));
    $('#outline-close').addEventListener('click', () => closeOverlay('#outline-overlay'));
    $('#outline-detail').addEventListener('change', regenerateOutline);

    // Sidebar
    $('#sb-close').addEventListener('click', deselect);
    $('#sb-anno-save').addEventListener('click', saveCurrentAnnotation);
    $('#sb-anno').addEventListener('blur', saveCurrentAnnotation);
    $('#sb-anno-clear').addEventListener('click', () => {
      if (!state.selected) return;
      delete state.annotations[state.selected];
      saveAnnotations();
      $('#sb-anno').value = '';
      $('#sb-anno-status').textContent = 'cleared';
      const node = state.cy.getElementById(state.selected);
      if (node) node.removeClass('has-annotation');
      updateCounts(applyView(state.view, state.graph, state.filters));
    });

    // Help
    $('#btn-help').addEventListener('click', () => toggleOverlay('#kbd-overlay'));
    $('#kbd-close').addEventListener('click', () => closeOverlay('#kbd-overlay'));

    // Keyboard shortcuts
    document.addEventListener('keydown', onKeydown);
  }

  function saveCurrentAnnotation() {
    if (!state.selected) return;
    const val = $('#sb-anno').value;
    const node = state.cy.getElementById(state.selected);
    if (val.trim()) {
      state.annotations[state.selected] = val;
      if (node) node.addClass('has-annotation');
      $('#sb-anno-status').textContent = saveAnnotations() ? '✱ saved' : 'storage full';
    } else if (state.annotations[state.selected]) {
      delete state.annotations[state.selected];
      saveAnnotations();
      if (node) node.removeClass('has-annotation');
      $('#sb-anno-status').textContent = '';
    }
    updateCounts(applyView(state.view, state.graph, state.filters));
  }

  function switchView(v) {
    state.view = v;
    $$('#view-picker .view-btn').forEach((b) => b.classList.toggle('active', b.dataset.view === v));
    writeUrlFilters();
    if (v === 'V0') {
      regenerateOutline();
      openOverlay('#outline-overlay');
    } else {
      closeOverlay('#outline-overlay');
      render();
    }
  }

  function onKeydown(ev) {
    if (ev.target && (ev.target.tagName === 'INPUT' || ev.target.tagName === 'TEXTAREA' || ev.target.tagName === 'SELECT')) {
      if (ev.key === 'Escape') ev.target.blur();
      return;
    }
    if (ev.key === '?') { toggleOverlay('#kbd-overlay'); ev.preventDefault(); }
    else if (ev.key === '/') { $('#f-search').focus(); ev.preventDefault(); }
    else if (ev.key === 'Escape') {
      $$('.overlay').forEach((o) => o.classList.add('hidden'));
      deselect();
    }
    else if (/^[0-6]$/.test(ev.key)) switchView('V' + ev.key);
    else if (ev.key === 'b') goBack();
    else if (ev.key === 'p') { if (state.selected) togglePin(state.selected); }
    else if (ev.key === 'c') openLlmOverlay();
    else if (ev.key === 'f') { if (state.cy) state.cy.fit(null, 40); }
    else if (ev.key === 'o') switchView('V0');
  }

  // ---- Export: image / json ------------------------------------------------
  function exportImage(format) {
    if (!state.cy) return;
    let blob, name;
    if (format === 'svg' && state.cy.svg) {
      const svg = state.cy.svg({ full: true, bg: '#07061a' });
      blob = new Blob([svg], { type: 'image/svg+xml' });
      name = 'imperium-graph-' + state.view + '.svg';
    } else {
      const dataUrl = state.cy.png({ full: true, bg: '#07061a', scale: 2 });
      blob = dataUrlToBlob(dataUrl);
      name = 'imperium-graph-' + state.view + '.png';
    }
    downloadBlob(blob, name);
  }
  function exportFiltered() {
    const f = applyView(state.view, state.graph, state.filters);
    const payload = {
      schema: SCHEMA,
      generator: 'imperium.graph.viewer.v0_2',
      view: state.view,
      filters: state.filters,
      pins: Array.from(state.pins),
      source_snapshot: state.graph.generated_at,
      counts: { nodes: f.nodes.length, edges: f.edges.length },
      nodes: f.nodes,
      edges: f.edges,
    };
    downloadBlob(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }),
                 'imperium-graph-' + state.view + '.json');
  }
  function exportAnnotations() {
    const payload = {
      schema: 'imperium.graph.annotations.v1',
      exported_at: new Date().toISOString(),
      annotations: state.annotations,
    };
    downloadText(JSON.stringify(payload, null, 2), 'imperium-annotations.json');
    toast('annotations exported (' + Object.keys(state.annotations).length + ')');
  }
  function importAnnotations(ev) {
    const file = ev.target.files[0];
    if (!file) return;
    const r = new FileReader();
    r.onload = () => {
      try {
        const data = JSON.parse(r.result);
        const annos = data.annotations || data;
        if (typeof annos !== 'object') throw new Error('invalid format');
        Object.assign(state.annotations, annos);
        saveAnnotations();
        toast('imported ' + Object.keys(annos).length + ' annotations');
        render();
      } catch (e) { toast('import failed: ' + e.message, 3000); }
    };
    r.readAsText(file);
    ev.target.value = '';
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
    const a = document.createElement('a'); a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function downloadText(text, name) {
    downloadBlob(new Blob([text], { type: 'text/plain;charset=utf-8' }), name);
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
    } else fallbackCopy(text);
  }
  function fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.left = '-9999px';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
  }

  // ---- V0 Outline (markdown tree) ------------------------------------------
  function regenerateOutline() {
    const detail = $('#outline-detail').value;
    const md = buildOutlineMarkdown(detail === 'full');
    $('#outline-text').value = md;
    $('#outline-footer').textContent = md.split('\n').length + ' lines · ' + md.length + ' chars · source: ' + (state.graph.generated_at || 'n/a');
  }
  function buildOutlineMarkdown(full) {
    const g = state.graph;
    const lines = [];
    lines.push('# Imperium Graph Outline');
    lines.push('');
    lines.push('- schema: `' + g.schema + '`');
    lines.push('- generated_at: `' + (g.generated_at || 'n/a') + '`');
    lines.push('- counts: **' + (g.counts ? g.counts.nodes : g.nodes.length) + ' nodes / ' + (g.counts ? g.counts.edges : g.edges.length) + ' edges**');
    lines.push('- generator: `' + (g.generator || 'unknown') + '`');
    lines.push('');

    // Index nodes by id, group by organ
    const byId = new Map(); g.nodes.forEach((n) => byId.set(n.id, n));
    const organs = g.nodes.filter((n) => n.type === 'organ');
    const byOrganMap = new Map();
    g.nodes.forEach((n) => {
      const key = n.organ || (n.type === 'organ' ? (n.label || n.id) : '_unorganed');
      if (!byOrganMap.has(key)) byOrganMap.set(key, []);
      byOrganMap.get(key).push(n);
    });

    // Provenance chain
    const chainEdges = g.edges.filter((e) => e.type === 'lands_after');
    if (chainEdges.length) {
      lines.push('## Provenance chain (lands_after)');
      lines.push('');
      // Topo-ish: A lands_after B means A succeeded B. Print B → A in declared order.
      chainEdges.slice().reverse().forEach((e) => {
        const a = byId.get(e.src), b = byId.get(e.dst);
        const aL = a ? (a.label || a.id) : e.src;
        const bL = b ? (b.label || b.id) : e.dst;
        lines.push('- `' + bL + '` → `' + aL + '`');
      });
      lines.push('');
    }

    // Organs section
    lines.push('## Organs');
    lines.push('');
    const organKeys = Array.from(byOrganMap.keys()).sort((a, b) => {
      if (a === '_unorganed') return 1;
      if (b === '_unorganed') return -1;
      return a.localeCompare(b);
    });
    organKeys.forEach((k) => {
      const members = byOrganMap.get(k);
      const head = members.find((n) => n.type === 'organ');
      const title = head ? (head.label || head.id) : k;
      lines.push('### ' + title);
      // breakdown by type
      const byType = {};
      members.forEach((n) => { byType[n.type] = (byType[n.type] || 0) + 1; });
      const types = Object.keys(byType).sort();
      lines.push('counts: ' + types.map((t) => t + ': ' + byType[t]).join(' · '));
      if (full) {
        types.forEach((t) => {
          if (t === 'organ') return; // the organ itself is the heading
          const items = members.filter((m) => m.type === t).sort((a, b) => (a.label || a.id).localeCompare(b.label || b.id));
          lines.push('');
          lines.push('- **' + t + '** (' + items.length + ')');
          items.forEach((m) => {
            const ann = state.annotations[m.id];
            const label = m.label || m.id;
            const meta = [];
            if (m.id !== label) meta.push('`' + m.id + '`');
            if (m.declared_base) meta.push('base=' + m.declared_base.slice(0, 8));
            if (m.committed_at) meta.push('at=' + m.committed_at);
            lines.push('    - ' + label + (meta.length ? ' — ' + meta.join(' · ') : '') + (ann ? ' ✱' : ''));
            if (ann) lines.push('        > ' + ann.replace(/\n/g, '\n        > '));
          });
        });
      }
      lines.push('');
    });

    // Annotations summary
    const annKeys = Object.keys(state.annotations);
    if (annKeys.length) {
      lines.push('## Annotations (' + annKeys.length + ')');
      lines.push('');
      annKeys.sort().forEach((id) => {
        const n = byId.get(id);
        const label = n ? (n.label || id) : id;
        lines.push('- `' + label + '` (' + (n ? n.type : 'missing') + ')');
        lines.push('    > ' + state.annotations[id].replace(/\n/g, '\n    > '));
      });
      lines.push('');
    }

    return lines.join('\n');
  }

  // ---- LLM context export --------------------------------------------------
  function openLlmOverlay() {
    regenerateLlmText();
    openOverlay('#llm-overlay');
  }
  function quickLlmCopy(scope, depth) {
    $('#llm-scope').value = scope;
    $('#llm-depth').value = String(depth);
    regenerateLlmText();
    copyText($('#llm-text').value);
    toast('LLM context (' + scope + ', depth=' + depth + ') copied');
  }
  function regenerateLlmText() {
    const scope = $('#llm-scope').value;
    const depth = parseInt($('#llm-depth').value, 10);
    const format = $('#llm-format').value;
    const includeAnnos = $('#llm-include-annos').checked;
    const ctx = buildLlmContext(scope, depth, format, includeAnnos);
    $('#llm-text').value = ctx;
    $('#llm-footer').textContent = ctx.split('\n').length + ' lines · ' + ctx.length + ' chars (~' + Math.round(ctx.length / 4) + ' tokens est.)';
  }
  function buildLlmContext(scope, depth, format, includeAnnos) {
    const g = state.graph;
    const byId = new Map(); g.nodes.forEach((n) => byId.set(n.id, n));
    const adj = new Map();
    g.edges.forEach((e) => {
      if (!adj.has(e.src)) adj.set(e.src, []);
      if (!adj.has(e.dst)) adj.set(e.dst, []);
      adj.get(e.src).push({ to: e.dst, type: e.type, dir: 'out' });
      adj.get(e.dst).push({ to: e.src, type: e.type, dir: 'in' });
    });

    let seedIds = [];
    if (scope === 'selection') {
      if (state.pins.size) seedIds = Array.from(state.pins);
      else if (state.selected) seedIds = [state.selected];
    } else if (scope === 'view') {
      const f = applyView(state.view, g, state.filters);
      seedIds = f.nodes.map((n) => n.id);
    } else if (scope === 'organ') {
      const organ = state.filters.organ || (state.selected && byId.get(state.selected) && byId.get(state.selected).organ);
      if (organ) seedIds = g.nodes.filter((n) => n.organ === organ || (n.type === 'organ' && n.label === organ)).map((n) => n.id);
      else seedIds = g.nodes.filter((n) => n.type === 'organ').map((n) => n.id);
    } else if (scope === 'all') {
      seedIds = g.nodes.map((n) => n.id);
    }
    if (!seedIds.length) return '(empty — no selection / pinned nodes / matching scope)';

    // BFS expand seeds by depth
    const visited = new Set();
    const q = seedIds.map((id) => [id, 0]);
    while (q.length) {
      const [id, d] = q.shift();
      if (visited.has(id)) continue;
      visited.add(id);
      if (d < depth) (adj.get(id) || []).forEach((nb) => { if (!visited.has(nb.to)) q.push([nb.to, d + 1]); });
    }
    const nodes = Array.from(visited).map((id) => byId.get(id)).filter(Boolean);
    const edges = g.edges.filter((e) => visited.has(e.src) && visited.has(e.dst));

    // Supported formats: 'markdown' (default), 'json', 'prompt'.
    if (format === 'json') {
      const payload = {
        schema: SCHEMA,
        scope, depth, source_snapshot: g.generated_at,
        seed_ids: seedIds, counts: { nodes: nodes.length, edges: edges.length },
        nodes,
        edges: edges.map((e) => ({ src: e.src, dst: e.dst, type: e.type })),
        annotations: includeAnnos ? Object.fromEntries(Object.entries(state.annotations).filter(([id]) => visited.has(id))) : undefined,
      };
      return JSON.stringify(payload, null, 2);
    }

    // Markdown
    const lines = [];
    if (format === 'prompt') {  // 'prompt' = markdown + system header for Codex/Grok/Claude
      lines.push('You are reviewing a subgraph of the Imperium repository\'s causal graph (schema imperium.graph.v0_1).');
      lines.push('Below: ' + nodes.length + ' nodes, ' + edges.length + ' edges, scope=' + scope + ', BFS depth=' + depth + ' from ' + seedIds.length + ' seed(s).');
      lines.push('Node types: ' + NODE_TYPES.join(', '));
      lines.push('Edge types: ' + EDGE_TYPES.join(', '));
      lines.push('Seeds (focus of this context): ' + seedIds.map((id) => '`' + id + '`').join(', '));
      lines.push('');
      lines.push('---');
      lines.push('');
    }
    lines.push('# Imperium graph context');
    lines.push('');
    lines.push('- scope: `' + scope + '`');
    lines.push('- depth: `' + depth + '`');
    lines.push('- seeds: ' + seedIds.map((id) => '`' + id + '`').join(', '));
    lines.push('- source_snapshot: `' + (g.generated_at || 'n/a') + '`');
    lines.push('- counts: **' + nodes.length + ' nodes / ' + edges.length + ' edges**');
    lines.push('');

    // Group nodes by type
    const byType = {};
    nodes.forEach((n) => { (byType[n.type] = byType[n.type] || []).push(n); });
    NODE_TYPES.forEach((t) => {
      if (!byType[t]) return;
      lines.push('## ' + t + ' (' + byType[t].length + ')');
      lines.push('');
      byType[t].sort((a, b) => (a.label || a.id).localeCompare(b.label || b.id)).forEach((n) => {
        const label = n.label || n.id;
        const meta = [];
        if (n.id !== label) meta.push('id=`' + n.id + '`');
        if (n.organ) meta.push('organ=' + n.organ);
        if (n.declared_base) meta.push('base=' + n.declared_base.slice(0, 8));
        if (n.committed_at) meta.push('at=' + n.committed_at);
        if (n.verified_at) meta.push('verified=' + n.verified_at);
        const isSeed = seedIds.indexOf(n.id) !== -1 ? ' ●' : '';
        lines.push('- **' + label + '**' + isSeed + (meta.length ? ' — ' + meta.join(' · ') : ''));
        if (includeAnnos && state.annotations[n.id]) {
          lines.push('    > [annotation] ' + state.annotations[n.id].replace(/\n/g, '\n    > '));
        }
      });
      lines.push('');
    });

    // Edges
    if (edges.length) {
      lines.push('## edges (' + edges.length + ')');
      lines.push('');
      edges.slice().sort((a, b) => a.type.localeCompare(b.type)).forEach((e) => {
        const aN = byId.get(e.src), bN = byId.get(e.dst);
        const aL = aN ? (aN.label || aN.id) : e.src;
        const bL = bN ? (bN.label || bN.id) : e.dst;
        lines.push('- `' + e.type + '`: ' + aL + ' → ' + bL);
      });
      lines.push('');
    }

    return lines.join('\n');
  }

  // ---- Overlays ------------------------------------------------------------
  function openOverlay(sel) { $(sel).classList.remove('hidden'); }
  function closeOverlay(sel) { $(sel).classList.add('hidden'); }
  function toggleOverlay(sel) { $(sel).classList.toggle('hidden'); }

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
    $('#f-annotated-only').checked = state.filters.annotatedOnly;
    $$('#view-picker .view-btn').forEach((b) => b.classList.toggle('active', b.dataset.view === state.view));
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
    if (state.view === 'V0') { regenerateOutline(); openOverlay('#outline-overlay'); render(); }
    else render();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bootstrap);
  else bootstrap();

  // Diagnostics surface
  window.__IMPERIUM_VIEWER__ = {
    schema: SCHEMA, snapshotUrl: SNAPSHOT_URL,
    annotationKey: ANNOTATION_KEY,
    viewIds: VIEW_IDS, nodeTypes: NODE_TYPES, edgeTypes: EDGE_TYPES,
    state, applyView, buildLlmContext, buildOutlineMarkdown, parseUrlFilters,
  };
})();
