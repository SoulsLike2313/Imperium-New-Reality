# PATCH PACK — IMPERIUM-APP-PLATFORM-UI-POLISH-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + APP_PLATFORM`  
mode: `UI_POLISH_HOTFIX`

## Purpose

Make the existing Imperium App Platform usable after the cockpit merge.

The app currently renders as nearly unstyled HTML because the frontend does not import `styles.css`.

## Fix

- Ensure `SUPPORT/APP_TAURI/src/main.js` imports `./styles.css`.
- Replace `SUPPORT/APP_TAURI/src/styles.css` with a usable room-based skin.
- Preserve the existing app platform and room architecture.
- Do not claim final AAA visual system.

## Style

Victorian Gothic + cyberpunk glow, but lightweight enough for the current Tauri WebView 60 FPS proof path.

## Not claimed

- final AAA polish;
- game projection;
- packaged exe;
- updater lane;
- final design;
- visual work for Eyes graph.
