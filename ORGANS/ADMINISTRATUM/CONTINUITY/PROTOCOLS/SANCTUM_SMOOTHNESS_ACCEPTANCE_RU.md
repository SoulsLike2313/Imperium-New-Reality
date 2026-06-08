# SANCTUM SMOOTHNESS ACCEPTANCE RU

v0.3 showed 32-42 FPS and a heavy purple header artifact. v0.4 focuses on smoother daily use.

## Acceptance

- Header has no big blocky purple scanline artifact.
- Visual Quality modes are available: Performance, Balanced, Cinematic.
- Default Performance mode reduces redraw pressure.
- FPS is measured owner-visibly; target remains 60 FPS, actual depends on host machine/Tkinter.
- Smoothness work must not enable unsafe execution, live LLM, or trading execution.

## V0.4.2 FPS governor hotfix

During H review v0.4 still showed about 32 FPS in Performance. The immediate task is not to commit v0.4 yet, but to fix the same H task in place.

V0.4.2 acceptance:

- Performance mode throttles heavy redraws instead of redrawing header/flow/right canvases every frame.
- A 60Hz lightweight loop remains active, while full visual recomposition is budgeted.
- If measured FPS remains below 50, ultra-light Performance budget is entered automatically.
- This hotfix is visual/UX only and must not enable real execution, live LLM, unsafe shell, or live trading.
