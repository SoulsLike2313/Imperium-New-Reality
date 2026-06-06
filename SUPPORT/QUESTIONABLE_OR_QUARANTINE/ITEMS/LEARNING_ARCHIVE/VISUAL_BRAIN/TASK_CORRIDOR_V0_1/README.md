# NewGen Visual Brain Task Corridor V0.1

## Purpose
This lab is a static, read-only corridor visual surface for New Generation artifacts.

It renders generated state from:
- `data/visual_brain_task_corridor_state.generated.json`

## Truth Boundaries
- `READ_ONLY_LAB`
- `FOUNDATION_ONLY`
- `NO LIVE BACKEND`
- `NO LIVE AUTONOMOUS ORGAN DIALOGUE PROVEN`
- green/proved states require evidence references

## How To Build Data
From `E:\IMPERIUM`:

```powershell
python IMPERIUM_NEW_GENERATION\TOOLS\VISUAL_BRAIN\build_visual_brain_task_corridor_v0_1.py
```

## How To Open
Open locally:

`E:\IMPERIUM\IMPERIUM_NEW_GENERATION\VISUAL_BRAIN\TASK_CORRIDOR_V0_1\index.html`

## Interaction Surface
- click node card to inspect truth/evidence details;
- click evidence star to inspect evidence reference;
- toggle reduced motion;
- switch compact/detail view.

No action in this lab triggers backend execution.
