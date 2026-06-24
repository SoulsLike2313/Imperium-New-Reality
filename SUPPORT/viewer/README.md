# Imperium Graph Viewer

Static HTML/JS/CSS viewer for `imperium.graph.v0_1` snapshots.
Lives at `SUPPORT/viewer/`, reads `SUPPORT/graph_snapshot.json` via relative path.

## Files

- `index.html` — layout (topbar, controls, canvas, sidebar, botbar)
- `app.js` — viewer logic, 6 views, URL filters, annotations, export
- `styles.css` — EYES_V2 v0.2 palette (tonal violet + yellow MARK)
- `cytoscape.min.js` — vendored Cytoscape.js 3.30.4 (graph rendering)
- `.nojekyll` — disables Jekyll on GitHub Pages

## Views

| ID | Name | Focus |
|----|------|-------|
| V1 | Overview | All nodes, light filter, default layout |
| V2 | Organ Drilldown | One organ + sub_organs + sentinels + agents + doctrines |
| V3 | Provenance Chain | lands + tasks + receipts, lands_after spine highlighted |
| V4 | Time Slice | Nodes after `?since=YYYY-MM-DD` |
| V5 | Sentinel Pulse | Sentinels + monitored entities |
| V6 | Doctrine Map | Doctrines + references between them |

## URL filters

```
index.html?v=V2&organ=MECHANICUS&since=2026-06-01&focus=organ:MECHANICUS&depth=3&search=indexer
```

All params optional. Default view is V1.

## Annotations

Per-node notes saved in `localStorage` under key `imperium.graph.annotations.v1`.
Client-only; never leaves the browser; not sync'd with the repo.

## GitHub Pages

After the first push including this viewer + `SUPPORT/graph_snapshot.json`:

1. Repo Settings → Pages
2. Source: `master` branch, root `/` folder
3. Wait ~1 min for the first deploy
4. Open `https://soulslike2313.github.io/Imperium-New-Reality/SUPPORT/viewer/`

## Refreshing the snapshot

After any new land:

```powershell
python3 ORGANS/MECHANICUS/TOOLS/imperium_graph_indexer_v0_1.py --repo-root .
git add SUPPORT/graph_snapshot.json
git commit -m "refresh graph snapshot"
git push
```

The viewer reads `../graph_snapshot.json` so a new snapshot reflects in the
viewer on the next page refresh.
