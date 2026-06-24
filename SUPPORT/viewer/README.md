# Imperium Graph Viewer — v0_2

AAA-pass over v0_1: 7 canonical views (V0 Outline + V1…V6 graph), LOD
labels, hover tooltips, organ-grouped V1 layout, strict V3 `lands_after`
chain, mini-map, history back, pin / multi-selection bundle, annotated
ring overlay, auto-save annotations, JSON import/export of annotations,
and a full LLM context exporter (scope + depth + format).

Lives at `SUPPORT/viewer/`, reads `SUPPORT/graph_snapshot.json` via
relative path. Zero runtime CDN dependency — Cytoscape.js 3.30.4 is
vendored in this folder.

## Views (V0…V6)

| ID | Name              | Output         | Use |
|----|-------------------|----------------|-----|
| V0 | **Outline** *(new)* | markdown text | LLM friendly tree of the whole graph |
| V1 | Overview          | cose, grouped by organ | Whole graph with visual clusters |
| V2 | Organ Drilldown   | circle         | Single organ + sub_organs + sentinels |
| V3 | Provenance Chain  | breadthfirst   | Strict `lands_after` chain (no orphans) |
| V4 | Time Slice        | breadthfirst   | Nodes after `?since=` |
| V5 | Sentinel Pulse    | concentric     | Sentinels + monitored entities |
| V6 | Doctrine Map      | concentric     | Doctrines + references |

## URL filters

```
index.html?v=V2&organ=MECHANICUS&since=2026-06-01&focus=organ:MECHANICUS&depth=3&search=indexer&anno=1&pins=task:A,land:B
```

All params optional. Round-trips state to the URL so any selection is a
bookmark.

## Annotations

- Click any node → textarea in sidebar.
- **Auto-save** on blur (clicking away). Manual Save button also there.
- Yellow ring **✱ has-annotation** overlay drawn on annotated nodes.
- Filter `✱ only annotated` (or `?anno=1`) shows only your marks.
- Hover tooltip shows annotation snippet without opening sidebar.
- Download all annotations as JSON (`⬇ Annotations`).
- Import back from JSON (`⬆ Annotations`).
- Local-only: `localStorage['imperium.graph.annotations.v1']`.

## LLM context export

**`⧫ Copy as LLM context`** button (or `c` key) opens the export modal.

Four **scopes**:
- `selection` — just pinned nodes (or current selection) + N-hop neighborhood
- `view`      — whatever's currently visible (view + filters)
- `organ`     — one organ's whole subgraph
- `all`       — the entire graph

Three **formats**:
- `markdown outline` — grouped by node type, sorted, with metadata
- `json subgraph`    — raw nodes + edges + annotations
- `prompt-ready`     — markdown + a system-style header explaining schema and edges (drop straight into Codex / Grok / Claude)

**Depth** slider 0..4 sets BFS expansion from seeds.

Quick buttons in node sidebar:
- `short`  — just this node
- `medium` — +1 hop neighborhood
- `full`   — +2 hops

Footer shows live `lines · chars · ~tokens` estimate.

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `?` | show / hide help |
| `/` | focus search |
| `0`…`6` | switch to view V0…V6 |
| `Esc` | close any overlay / sidebar |
| `b` | back — previous selected node |
| `p` | pin / unpin selected |
| `c` | copy as LLM context |
| `f` | fit graph to canvas |
| `o` | open Outline (V0) |
| `shift+click` | multi-select / pin node |

## Mini-map

Live overview in bottom-right. Yellow MARK rectangle = current viewport.
Drag inside the mini-map to pan the main canvas.

## LOD labels

When graph is dense (>80 nodes) and you're zoomed out, minor labels hide
automatically. Zoom in to reveal them. Tooltips always work on hover.

## Files

- `index.html` — layout (topbar + controls + canvas + mini-map + sidebar + overlays)
- `app.js` — viewer logic (~1100 lines)
- `styles.css` — EYES_V2 v0.2 + frosted glass
- `cytoscape.min.js` — vendored Cytoscape.js 3.30.4
- `.nojekyll` — GitHub Pages: disable Jekyll

## Refreshing the snapshot

Any new land that touches the repo:

```powershell
python3 ORGANS/MECHANICUS/TOOLS/imperium_graph_indexer_v0_1.py --repo-root .
git add SUPPORT/graph_snapshot.json
git commit -m "refresh graph snapshot"
git push
```

Viewer reads `../graph_snapshot.json` so it reflects on next refresh.
