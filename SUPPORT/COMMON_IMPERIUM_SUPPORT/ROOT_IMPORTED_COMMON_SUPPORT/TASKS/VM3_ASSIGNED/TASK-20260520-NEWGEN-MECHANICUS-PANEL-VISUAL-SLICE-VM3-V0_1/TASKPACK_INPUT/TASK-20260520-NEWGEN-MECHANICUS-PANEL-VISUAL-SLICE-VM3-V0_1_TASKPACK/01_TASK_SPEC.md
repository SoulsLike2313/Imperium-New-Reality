# Task specification

## Task ID

`TASK-20260520-NEWGEN-MECHANICUS-PANEL-VISUAL-SLICE-VM3-V0_1`

## Objective

Implement one isolated visual lab slice for:

`SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL`

using the hardened topology, owner visual contract, and included asset references.

## Output locations

### Implementation root

`IMPERIUM_NEW_GENERATION/SANCTUM_VISUAL_FOUNDRY/LABS/MECHANICUS_PANEL_SLICE_V0_1/`

### Task artifacts root

`IMPERIUM_NEW_GENERATION/TASKS/VM3_ASSIGNED/TASK-20260520-NEWGEN-MECHANICUS-PANEL-VISUAL-SLICE-VM3-V0_1/`

## Required implementation outputs

Create at minimum:

- `index.html`
- `styles.css`
- `app.js`
- `README.md`
- `SCREENSHOTS/`
- `REPORTS/`
- `RECEIPTS/`

## Required visual behavior

The slice must include five zones:

1. **Header / Identity**
2. **Current Activity / Work Zone**
3. **Command / Operator Palette**
4. **Tool Registry / Capability Overview**
5. **Footer / Evidence / Mission Focus**

## Truth discipline

- Unknown data must show as `UNKNOWN`.
- Stub sections must show as `STUB`.
- Locked sections must show as `LOCKED`.
- Real/current values may only be shown if grounded by existing repo data.
- Do not claim integrated SSE if this slice is static or mock-backed.

## Implementation constraints

- Prefer plain HTML/CSS/JS.
- No external CDN dependencies.
- No framework tax unless already present and clearly justified.
- Cheap motion only.
- Reduced-motion fallback required.
- No global app rewrite.
- This is an isolated lab.

## Evidence requirements

Produce:
- before/after screenshots;
- one full screenshot;
- 2-4 detail crops;
- owner report in RU;
- implementation report in EN;
- final receipt JSON;
- list of source files used for truth grounding;
- list of visual assets used.

## Optional but good

If easy and safe, include:
- one small state toggle demo (`idle`, `active`, `warn`, `blocked`, `unknown`);
- one reduced-motion toggle;
- one token file or compact visual constants file.
