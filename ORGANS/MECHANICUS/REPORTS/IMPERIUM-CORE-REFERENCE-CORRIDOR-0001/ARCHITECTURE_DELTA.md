# Architecture Delta

- Added one task-local `CORE_REFERENCE_CORRIDOR` package under Mechanicus.
- Added Git-derived root context, atomic task transaction, one capability registry, typed executor, exact-HEAD WARP manager, evidence/checkpoint stores, organ ledger and Owner gate.
- Replaced APP_TAURI's legacy cockpit entry with a generic backend snapshot renderer and two fixed bridge commands.
- Removed the direct `RUN_*.ps1` Tauri execution surface.
- Kept legacy registries, patch stores and WARP implementations read-only for migration; no deletion or hidden promotion occurred.
