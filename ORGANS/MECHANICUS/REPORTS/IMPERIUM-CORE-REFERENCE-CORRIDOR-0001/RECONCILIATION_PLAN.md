# Targeted Reconciliation Plan

This is a focused implementation map for the audit backlog supplied by the Owner. It is not a replacement audit.

| Finding | Existing component to reuse | Component to isolate | New module | Expected change zones | Acceptance proof |
|---|---|---|---|---|---|
| M01/M02 authority and Great Nine conflict | Root governance order; Owner-locked terms; Throne active canon matrix | Unamended Constitution wording; eight-organ intake list | Canon source adapter + supersession proposal | taskpack, report, organ ledger | conflict remains visible; exactly nine operational rows plus Throne |
| M04 root resolver | Git CLI and Astronomicon git-first idea | hardcoded/marker-walk resolvers | `root_resolver.py` | Mechanicus package | nested cwd succeeds; outside Git fails closed; Reality root recorded |
| M05 task truth | Astronomicon taskpack path and immutable Owner input | current_expected_task and IDE state files | atomic `task_store.py` | report runtime state | one transaction, versioned transitions, restart recovery, stale-base block |
| M07/M08 tool truth | Mechanicus command policy/schema concepts | three legacy registries and hardcoded actions | `registry.py` + typed `executor.py` | Mechanicus package, Tauri bridge | one runtime registry, default deny, actual-effect/write-scope proof |
| M09/M11 unsafe runners | Tauri shell presentation only | direct `RUN_*.ps1` discovery/execution and old runners | fixed-action corridor bridge | APP_TAURI | unsafe command absent from invoke surface and frontend |
| M10/M12/M13 WARP semantics | Git worktree support and legacy WARP metadata vocabulary | copytree, tracked patch/intake/archive semantics | `warp_manager.py` | Mechanicus package | exact HEAD + Git metadata; lifecycle and disposable rollback/destroy proofs |
| M14 evidence | Evidence vault hashing and post-work organ schema | incomplete legacy receipt shapes | evidence envelope/store/validator | Mechanicus package and report | required proof tuple, tamper detection, JSON+MD pairs |
| M15 UI/backend parity | Existing Vite/Tauri application | JS truth arrays and substring parity test | backend snapshot + generic renderer | APP_TAURI | every panel/action comes from backend; semantic parity gate |
| M17 end-to-end proof | Existing build lanes and Git truth commands | synthetic corridor claims | real diagnostic corridor | WARP report/evidence | demo execution receipt and 20 localized negative scenarios |

Decision priority: verifiability, result quality, Core safety, Owner control, learnability, capability growth, speed, then visual polish.
