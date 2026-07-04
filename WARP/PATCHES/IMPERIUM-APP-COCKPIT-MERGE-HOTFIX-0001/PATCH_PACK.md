# PATCH PACK — IMPERIUM-APP-COCKPIT-MERGE-HOTFIX-0001

status: `WARP_CANDIDATE`  
owner: `MECHANICUS + APP_PLATFORM`  
mode: `APP_MERGE_HOTFIX`

## Purpose

Correct the UI direction.

The previous cockpit patch made the app feel like a separate Operational Cockpit. Owner intent is different:

```text
Do not create a separate patch-pack application.
Use the existing Imperium application.
Patch Pack Registry and Mechanicus Language Codex are rooms inside the app.
```

## Fix

This patch restores the primary shell to:

```text
Imperium App Platform
```

and embeds operational cockpit powers as rooms:

- Organ Hub;
- Patch Forge / Patch Pack Registry;
- Mechanicus / Language Power Codex;
- Aquarium;
- future Astronomicon, Throne, Eyes Room and Seed Core rooms.

## Law

```text
Operational power does not replace the app.
Operational power is integrated into the app as a room, panel or capability.
```

## Not claimed

- final app UX;
- AAA polish;
- full Patch Pack security model;
- full Mechanicus language proof system;
- packaged exe;
- updater lane.
