# IMPERIAL IDE Launcher / Sanctum Operator Home V0.3

H-patch: continuity hardening + Sanctum UX seed.

## What changed

Part 1 — continuity repair:

- H-contour path and main repo path are now explicit in continuity output.
- Logos Prime boot protocol is written as owner-visible RU docs.
- H-safe command flow is included so new chats do not apply H patches in main.
- Continuity pack builder schema is upgraded to `administratum.continuity_pack.v0_3`.
- Previous failure modes are recorded so they are not repeated.

Part 2 — operator UX seed:

- Launcher becomes `Imperial Sanctum Operator Home V0.3`.
- New surfaces: Sanctum, Task Intake, Mechanicus, Departments.
- Header shows contour/branch/head and a 60fps target FPS readout.
- Flow diagram now represents the task lifecycle state machine.
- Right visual shows Core + IDE + Addons + Departments as observable machine state.
- Buttons include Copy H Flow and Open Protocols.

## Safety

- no real servitor execution;
- no live LLM backend;
- no unsafe shell;
- no auto commit/push;
- no live trading/order placement;
- station routes remain read-only or explicitly safe.

## Smoke

```powershell
python .\ORGANS\ADMINISTRATUM\CONTINUITY\continuity_pack_builder.py --smoke
python .\ORGANS\IMPERIAL_IDE\LAUNCHER\imperial_launcher.py --smoke
```

## Visual

```powershell
python .\ORGANS\IMPERIAL_IDE\LAUNCHER\imperial_launcher.py
```

This is not the final top-level UI. It is the first corrected H-safe foundation for the future Sanctum where task registration, agent visibility, evidence, client/freelance flow, Mechanicus standards, and departments become pleasant to operate.
