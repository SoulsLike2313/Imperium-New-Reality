# Migration Map

| Old path/role | Risk | New replacement | Adapter/removal precondition | Status |
|---|---|---|---|---|
| heuristic root resolvers | stale/hardcoded root | `CORE_REFERENCE_CORRIDOR/root_resolver.py` | read-only compatibility only; remove after consumers migrate | LEGACY_READ_ONLY |
| Astronomicon/IDE current-state files | contradictory current task | atomic corridor `TASK_STATE.json` | generate views after Owner admission | LEGACY_READ_ONLY |
| three Mechanicus registries | competing authority/effect drift | task-local `CAPABILITY_REGISTRY.json` | migrate consumers and validate parity | LEGACY_READ_ONLY |
| hardcoded Tauri actions | UI/backend drift | registry-backed snapshot actions | semantic parity required | DEPRECATED_UNSAFE |
| direct Tauri patch runner | arbitrary Reality mutation | fixed corridor bridge -> typed executor | no re-enable without new Owner task | QUARANTINED |
| copytree WARP | no Git metadata/exact HEAD | `warp_manager.py` Git worktree | migrate runtime callers | DEPRECATED_UNSAFE |
| tracked `WARP/PATCHES` and intake/archive meanings | mixed semantics | external managed runtime WARP | retain as non-executable legacy stores | LEGACY_READ_ONLY |
| old `RUN_*.ps1` patch runners | direct Reality write/removal | no replacement execution authority | per-runner migration and owner approval | QUARANTINED |
| incomplete receipt formats | missing proof tuple | `evidence.py` envelope | independent validator and hash migration | LEGACY_READ_ONLY |
