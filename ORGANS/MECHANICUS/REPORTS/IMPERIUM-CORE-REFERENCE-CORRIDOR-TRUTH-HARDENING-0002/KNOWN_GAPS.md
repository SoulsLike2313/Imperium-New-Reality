# Known Gaps

- Historical finalized receipts under `IMPERIUM-CORE-REFERENCE-CORRIDOR-0001` are not current Phase 1 proof and have not yet been reconciled.
- The Phase 1 fixture validates all organ record shapes and verdict rules; it does not claim that all actual organs are operational.
- Actual organ rows without current organ-specific evidence remain `NOT_PROVEN`.
- Phase 2 negative scenarios are observation-derived and checkpointed; Phase 3 reran the full backend regression but did not reinterpret the historical Phase 2 receipts.
- Phase 3 closes the real Rust Tauri invoke surface to the two canonical corridor commands; the unregistered legacy Rust helper implementations remain private source debt and are not Tauri-reachable.
- The Thin IDE makes no runtime FPS performance claim; its regression check proves only that the removed `record_runtime_fps_proof` mutation route remains fail closed.
- Phase 4 hardens the Rust-to-Python bridge with registry-pinned interpreter admission, exact process inputs, minimal environment, Windows process-tree termination, and bound receipts.
- Real diff, live UI proof, final claim reconciliation, and independent disk audit remain unexecuted.
- Campaign verdict is `TRUTH_HARDENING_PARTIAL_NOT_READY`; no land is authorized or performed.
