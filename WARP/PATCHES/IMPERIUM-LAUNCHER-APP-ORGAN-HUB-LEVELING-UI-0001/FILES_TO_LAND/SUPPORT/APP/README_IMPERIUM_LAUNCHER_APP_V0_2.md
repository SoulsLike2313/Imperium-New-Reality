# Imperium Launcher App V0.2 — Organ Hub / Leveling UI

patch_id: `IMPERIUM-LAUNCHER-APP-ORGAN-HUB-LEVELING-UI-0001`

## What changed

The app no longer exposes all functions directly on the main screen.

It now behaves like an Imperium/Solo-leveling-like system interface:

```text
Main screen:
  organ hub
  level / proof XP
  clean execution streak
  proof reasons

Organ room:
  functions appear only after entering an organ

Pack Forge:
  registration request buttons for Patch Pack and Task Pack
```

## Run

```powershell
pwsh SUPPORT/APP/imperium_launcher.ps1
```

Double-click entry remains:

```text
SUPPORT/APP/LAUNCH_IMPERIUM_APP.cmd
```

Self-test:

```powershell
pwsh SUPPORT/APP/imperium_launcher.ps1 -SelfTest
```

## XP / leveling rule

XP is calculated from proof, not aesthetics:

```text
+100 Astronomicon chain ok
+100 Crown-aware overlay integrated
+selected crown-aware scores
+honesty boundary bonuses
+clean execution streak bonus
```

## Pack registration boundary

The buttons:

```text
Регистрация Patch Pack
Регистрация Task Pack
```

create app-level request drafts under:

```text
SUPPORT/APP/REGISTRY/PACK_REQUESTS/
SUPPORT/APP/RECEIPTS/
```

They do **not** claim canonical Astronomicon/Administratum final registration yet.

## Not claimed

```text
canonical final Patch Pack registration
canonical final Task Pack registration
packaged exe installer
full IDE visual abstraction
Great Nine assembled
Core v1 ready
Throne self-validation
```
