# Task Spec — TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5

## Role

You are PC Servitor for IMPERIUM.

## Repo

Default repo: `E:\IMPERIUM`

## Machine scope

PC only. VM2 is forbidden unless Owner explicitly says VM2.

## Strategic scope

This task belongs to **IMPERIUM_NEW_GENERATION only**.

The goal is to build the New Generation form first. Later, old main repo data and test-version data may be mined/absorbed through explicit gates. This task must not merge or contaminate old main organs.

## Starting evidence

Owner reports:
- V0_3 output bundle/report path was under old/main `ORGANS\MECHANICUS\REPORTS`, which is wrong.
- LIVE UI became bad: too raw, too terminal-like, poor resolution behavior.
- Clicking Mechanicus in the brain view does not open the expected organ operator panel.
- Owner wants a panel like `ASSETS/target_reference_mechanicus_operator_console.png`.

## Allowed source scope

Allowed:
- `IMPERIUM_NEW_GENERATION/**`

Allowed report/evidence scope:
- `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5/**`

Read-only reference allowed:
- previous reports under `IMPERIUM_NEW_GENERATION/REPORTS/**`
- taskpack assets
- uploaded/packaged prior evidence
- Git history

Forbidden write scope:
- `ORGANS/**`
- `SANCTUM/**` outside New Generation
- `IMPERIUM_TEST_VERSION/**`
- root-level source/config files unless explicitly needed and justified in BLOCK/WARN report
- laptop paths
- VM2 paths

## Required repair steps

### Phase 0 — Scope contamination audit

1. Run:
   - `git rev-parse HEAD`
   - `git status --short`
   - `git log -1 --oneline`
2. Identify any V0_3/V0_4 artifacts under forbidden paths, especially:
   - `ORGANS/MECHANICUS/REPORTS/TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3`
   - `ORGANS/MECHANICUS/REPORTS/TASK-20260520-SANCTUM-MECHANICUS-PANEL-REPAIR-RESPONSIVE-SSE-PC-V0_4`
3. Produce `scope_contamination_audit.md/json` under the New Generation report folder.
4. If wrong-scope files are uncommitted task artifacts:
   - copy any useful evidence into `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5/MIGRATED_PRIOR_EVIDENCE/`
   - restore/remove wrong-scope uncommitted task artifacts
   - record exact action
5. If wrong-scope files are already committed:
   - do not silently rewrite history
   - prepare a corrective commit only if safe and task-only
   - otherwise mark WARN and provide exact manual owner decision options.

### Phase 1 — New Generation report root

Create:
`E:\IMPERIUM\IMPERIUM_NEW_GENERATION\REPORTS\TASK-20260520-NEWGEN-SANCTUM-SCOPE-REPAIR-MECHANICUS-PANEL-PC-V0_5\`

All reports, screenshots, receipts, logs and proof from this task go there.

### Phase 2 — Mechanicus click interaction

Implement/repair this behavior:

- In Sanctum brain/overview, the **Mechanicus node/card is clickable**.
- Clicking it opens a **Mechanicus operator panel**.
- Opening can be:
  - route/view switch inside Sanctum,
  - right-side panel,
  - modal/docked panel,
  - or full operator workspace.
- But it must be visually and functionally obvious that Mechanicus was selected and its panel was born/opened.
- The panel must show:
  - top status/header
  - work zone/current activity
  - command zone/operator palette
  - tool registry/capabilities
  - latest report/receipt
  - event summary
  - raw/technical mode toggle
  - SSE/live connection state

BLOCK if clicking Mechanicus does nothing.

### Phase 3 — Responsive layout repair

The UI must be usable on:
- 1366x768 viewport
- 1600x900 viewport
- 1920x1080 viewport

Requirements:
- no giant horizontal scroll for the whole page
- no critical controls below inaccessible fold at 1366x768
- operator panel uses CSS grid/flex responsibly
- left/right panels collapse or stack on smaller width
- text is readable, not microscopic
- raw logs are contained in scrollable technical panes only
- main operator view must not be dominated by raw ASCII output

### Phase 4 — Operator panel form

Target direction:
- `ASSETS/target_reference_mechanicus_operator_console.png`
- original IMPERIUM/Mechanicus-inspired style
- dark metallic / red-cyan-amber-green semantics
- large readable top status strip
- left work zone
- right command zone
- lower tool registry / receipts / events
- no copied IP, no paid assets

Important:
- The goal is not to copy the reference pixel-by-pixel.
- The goal is to create the same **operator function and readability**.

### Phase 5 — SSE/live truth

Use existing SSE work if valid, but keep truth labels honest.

Required:
- show `SSE CONNECTED`, `SSE FALLBACK`, `SSE ERROR`, or `SSE DISABLED`
- if browser falls back, do not call it SSE PASS
- event stream proof must show heartbeat + state snapshot + command event
- operator panel must visibly update after a command without full page reload if SSE is connected

### Phase 6 — Raw terminal demotion

Raw terminal output must remain available under:
- RAW
- technical view
- expandable drawer
- or diagnostics tab

BLOCK if raw ASCII terminal remains the primary LIVE experience.

### Phase 7 — Evidence

Capture screenshots:
1. overview before clicking Mechanicus
2. Mechanicus node hover/selected state
3. operator panel after clicking Mechanicus at 1366x768
4. operator panel after running `status`
5. operator panel after running `tools`
6. SSE/live state visible
7. raw technical mode
8. responsive 1920x1080
9. action history / evidence tab

Also produce JSON/MD reports:
- `scope_contamination_audit.json/md`
- `ui_interaction_proof.json/md`
- `responsive_layout_proof.json/md`
- `sse_live_status_proof.json/md`
- `validation_report.json/md`
- `FINAL_RECEIPT.json`
- `OWNER_REPORT_RU.md`

### Phase 8 — Commit

Commit/push only if:
- final git status is clean after commit
- no forbidden path writes remain
- task report is under New Generation
- screenshots/evidence exist
- Mechanicus click opens panel

If forbidden writes remain or UI interaction fails, do not fake PASS.
