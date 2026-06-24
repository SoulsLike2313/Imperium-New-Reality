# IMPERIUM_GRAPH — Codebook of the Living Map

**Status:** doctrinal v0.1
**Issued by:** NOTION_OPUS
**Ratified by:** Uttkarsh, session thread `384ec8a8-2409-80fc-b98b-00a9ffec9701`
**Issued at:** 2026-06-24
**Lands at:** `ORGANS/DOCTRINARIUM/IMPERIUM_GRAPH.md`
**Visual code:** governed by `ORGANS/DOCTRINARIUM/EYES_V2.md` v0.2 (ratified earlier this session)
**Roadmap slot:** GRAPH-SPEC (Tier 1 of 3 for Imperium operational graph surface)

---

## 0. Premise

The Imperium is not a folder tree. It is a graph of organs, agents, doctrines,
tasks, lands and signals — with causal relationships between them. A folder tree
shows the **filing**; the graph shows the **living state**.

This codebook defines that graph as a first-class object of the empire:
its node types, edge types, view types, visual mapping, composition rules,
transmission contracts and annotation contract. Downstream tools
(`GRAPH-INDEXER-0001` indexer, `GRAPH-VIEWER-0001` HTML/Cytoscape viewer)
implement this canon — they do not invent it.

The graph wears EYES_V2: violet ground, yellow as mark, cosmic volume, gaze
inward by default. It does not look like a corporate dashboard. It looks
like a monument with its windows lit.

---

## 1. NODE_TYPES

Nine canonical node types in v0.1. Each is a kind of *thing the empire knows about*.

```
organ         : ORGANS/<NAME>/                 (canon organ root)
sub_organ     : ORGANS/<NAME>/<SUBSECTION>/    (e.g. INQUISITION/TOOLS)
doctrine      : *.md in ORGANS/DOCTRINARIUM/   (ratified law)
agent         : configured agent (Boris, Notion-Opus, autofill, sentinel, ...)
task          : pack/patch ever issued (TASK_MANIFEST.json bearing a task_id)
land          : commit on master where a task settled (commit_sha + task_id)
receipt       : Inquisition gate verdict for a land (verdict, deny_reasons, mode)
sentinel      : a live signal source (stagnation, loop, tails, daily/session caps)
thread        : owner conversation session (carries decisions, ratifications)
```

Each node carries minimum metadata:

```
id           : stable URL-safe slug (organ:INQUISITION, task:EYES-V2-CODEBOOK-0001, ...)
type         : one of the nine above
name         : human label
home_path    : repo-relative path or N/A
created_at   : ISO date if known
last_touch   : ISO date
status       : enum per type (see §2)
health       : ok | warn | alert | unknown   (drives yellow accent, see §5)
links_in     : count of incoming edges (computed)
links_out    : count of outgoing edges (computed)
focus_weight : 0..1, controls z-depth in cosmic-volume layout
```

---

## 2. STATUS_VOCABULARY (per node type)

```
organ        : canon | extra | hold       (canon = REQUIRED_9, extra = KNOWN_EXTRA, hold = migration leftover)
doctrine     : draft | ratified | superseded
agent        : online | dormant | retired
task         : built | landed | reverted | failed
land         : current | superseded | reverted
receipt      : allow | deny | crash
sentinel     : ok | warn | alert
thread       : open | closed
```

---

## 3. EDGE_TYPES

```
parent_of        organ → sub_organ, sub_organ → doctrine, agent → task
owns             organ → agent | organ → doctrine
declares_base    task  → land            (the parent SHA the task targeted)
lands_after      land  → land            (master succession)
ratifies         thread → doctrine        (owner approval moment)
gates            agent → task            (Inquisition gating a pack)
produces         task  → receipt
references       doctrine → doctrine     (canon cross-link)
monitors         sentinel → organ | sentinel → thread
succeeds         doctrine → doctrine     (versioning chain)
```

Edges carry minimum metadata: `type`, `from`, `to`, `since` (ISO), optional `weight`.

---

## 4. VIEW_TYPES (v1 canon — six views)

```
V1  overview                  every node, force-directed, clustered by organ
V2  organ_drilldown <ORGAN>    one organ + its sub_organs + doctrines + agents + recent tasks
V3  provenance_chain <land>    a land + declares_base → parent land + ... walked back N steps
V4  time_slice <since>         only nodes with last_touch >= since
V5  sentinel_pulse             only sentinels in warn|alert + their monitored targets
V6  doctrine_map               only doctrine nodes + references/succeeds edges
```

Each view is **derived** — it is a filter over the same underlying graph snapshot,
not a separate dataset.

---

## 5. VISUAL_MAPPING (EYES_V2 → graph)

### 5.1 Ground (TONAL_FIELD)

```
background     : radial gradient, center HSL(265, 35%, 14%), edges HSL(245, 40%, 6%)
fog overlay    : optional canvas-noise, opacity <=10%
no daylight    : enforced (mean luminance of canvas chrome <= 60/255)
```

### 5.2 Node color per type (within violet field)

```
organ        : HSL(255, 55%, 55%)   solid disk, ring 2px brighter
sub_organ    : HSL(255, 35%, 45%)   solid disk
doctrine     : HSL(275, 60%, 60%)   hexagon
agent        : HSL(245, 50%, 60%)   square with rounded corners
task         : HSL(285, 40%, 50%)   smaller disk, outline only
land         : HSL(295, 50%, 55%)   diamond
receipt      : HSL(220, 25%, 50%)   tiny dot near its land
sentinel     : HSL(310, 45%, 60%)   triangle
thread       : HSL(240, 30%, 40%)   pill, low opacity
```

### 5.3 Yellow as MARK (accent discipline)

The yellow stroke is reserved — it marks **live state** only:

```
active_task       : node currently in progress           → yellow ring 2px
sentinel_alert    : sentinel in alert (not warn)         → yellow fill stroke pulse
owner_focus       : node touched by owner in last 24h    → yellow underline glyph
ratified_today    : doctrine ratified within 24h         → yellow corner notch
```

Total yellow pixel area target: **5..10% of viewport** (EYES_V2 §2). Viewer
must degrade gracefully — if more than 10 nodes would carry yellow simultaneously,
rank by `focus_weight` and apply yellow only to top-N until budget is met.

### 5.4 Edge styles

```
parent_of        solid     opacity 0.6
owns             solid     opacity 0.5
declares_base    dashed    opacity 0.8   — the causal spine
lands_after      solid     opacity 0.9   — master succession, brightest
ratifies         dotted    opacity 0.7
gates            dashed    opacity 0.4
produces         dotted    opacity 0.3
references       dotted    opacity 0.5
monitors         dashed    opacity 0.4
succeeds         dotted    opacity 0.6
```

No arrowheads on `parent_of` and `owns` (structural). Arrowheads ON for
causal edges (`declares_base`, `lands_after`, `ratifies`, `succeeds`).

### 5.5 COSMIC_VOLUME via z-depth

```
z_layer 3 (front)  : nodes with active yellow mark
z_layer 2          : nodes with last_touch <= 7d
z_layer 1          : everything else
z_layer 0 (back)   : doctrines (the canon recedes into the field)
```

Front layers crisp; back layers blurred 1–2px and desaturated 20%. This is the
"window not sticker" rule (EYES_V2 §4).

### 5.6 FORBIDDEN in graph rendering

- bright theme / white background — ever
- two competing accent colors
- decorative emoji in nodes
- frontal labels covering > 40% of any node disk (EYES_V2 §7.5 spirit applied to UI)
- straight 90° right-angle edges (use bezier or smooth haystack)

---

## 6. COMPOSITION_RULES

Views compose via a single filter object:

```
filter = {
  view        : V1..V6,
  organs      : ["INQUISITION", "DOCTRINARIUM", ...]   (subset, default = all),
  types       : ["task", "land", ...]                  (subset, default = all),
  since       : ISO date                               (last_touch >= since),
  status      : { task: ["landed"], sentinel: ["alert"] },
  focus_node  : node_id                                (highlight + 1-hop neighbours up to depth N),
  depth       : 1..3                                   (only with focus_node),
  search      : "substring"                            (case-insensitive over name + id)
}
```

All filters are AND-combined. Empty arrays = no constraint. The viewer must
support pinning a named composition (save current filter as `view_name`).

---

## 7. TRANSMISSION_CONTRACTS

### 7.1 URL schema

```
https://<host>/viewer/?v=V2&organ=INQUISITION&since=2026-06-20&focus=land:158f4397&depth=2
```

All filter keys above map to URL query params. Opening the URL must reconstruct
the exact view.

### 7.2 Snapshot exports (frozen)

```
png         : viewer canvas, 2x DPR, includes legend strip on left edge
svg         : vector, no rasterization, EYES_V2 colors preserved
canvas      : Obsidian Canvas .canvas JSON, one card per visible node,
              card colors mapped from §5.2, edges as canvas edges
```

The Canvas export is the empire's **contemplative artifact**: a frozen
composed view ready to live inside a Doctrinarium note. Live exploration
happens in the HTML viewer; meditation on a composed view happens in Canvas.

### 7.3 Forbidden in transmission

- exporting without the legend
- snapshot resolution below 1920×1080 (PNG)
- canvas export that drops yellow marks (live state must survive freezing)

---

## 8. ANNOTATION_CONTRACT

```
storage_key   : "imperium.graph.annotations.v1"
storage_where : browser localStorage of the viewer (per device)
format        : { node_id: { note: string, bookmarked: bool, tags: [string], updated_at: ISO } }
repo_write    : forbidden by default (interaction mode = annotate, not edit)
portability   : viewer must expose "Export annotations" → .json file the owner may
                place at SUPPORT/annotations/<device>.json if they choose.
                Viewer auto-loads any SUPPORT/annotations/*.json on init, merged client-side.
```

Annotations never enter master through the viewer itself. If owner ever
imports an annotation file into the repo, it lands as a normal patch pack
through the Inquisition gate, like everything else.

---

## 9. INDEXER_CONTRACT (handoff to Tier 2)

`GRAPH-INDEXER-0001` must produce a single artifact:

```
path     : SUPPORT/graph_snapshot.json
schema   : { nodes: [Node], edges: [Edge], generated_at: ISO, master_sha: string, version: "imperium.graph.v0_1" }
source   : walked from repo root, never from external state
rules    : every node and edge in the snapshot must be derivable from repo content alone
           (no live network calls, no inferred ghosts)
e3       : indexer must ship E3 tests verifying schema, derivability, idempotency
```

---

## 10. VIEWER_CONTRACT (handoff to Tier 3)

`GRAPH-VIEWER-0001` must:

```
stack         : HTML + Cytoscape.js (graph engine) + CSS, no build step
files         : SUPPORT/viewer/{index.html, app.js, styles.css, cytoscape.min.js}
input         : SUPPORT/graph_snapshot.json (Tier 2 output)
host          : GitHub Pages from SUPPORT/viewer/ (owner-enabled)
offline       : index.html must open from disk without internet
performance   : >= 30 FPS pan/zoom with up to 500 nodes
accessibility : keyboard nav for focus+depth filters
self_check    : visible footer with snapshot master_sha + generated_at;
                load fails loud if snapshot version != imperium.graph.v0_1
```

---

## 11. VERSIONING

```
v0.1  initial canon, this document, 2026-06-24
```

Future versions land via the gate. No silent updates.

---

## 12. SIGNATURE

```
issued_by              : NOTION_OPUS
ratified_by_owner      : Uttkarsh
session_thread         : 384ec8a8-2409-80fc-b98b-00a9ffec9701
visual_code            : ORGANS/DOCTRINARIUM/EYES_V2.md v0.2
master_tip_at_issuance : 158f4397
```
