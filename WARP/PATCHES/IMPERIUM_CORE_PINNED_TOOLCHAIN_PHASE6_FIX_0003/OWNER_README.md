# IMPERIUM_CORE_PINNED_TOOLCHAIN_PHASE6_FIX_0003

This patch does not weaken Phase 4 by restoring `PATH`.

It admits two exact host dependencies through the canonical capability registry:

- `CORE_GIT`
- `CORE_PWSH`

The Rust bridge checks their absolute paths and SHA-256 values, passes them through a minimal environment, and Python verifies the hashes again immediately before use.

The patch is designed to run on top of the currently applied Phase 6 `FIX_0002` worktree state. It does not commit, push, merge, or land.

Flow:

1. Run `RUN_...ps1`.
2. Start the application with `npm run tauri:dev`.
3. Click **Run Diagnostic** once, then **Refresh** once, then close the app.
4. Run `VERIFY_...ps1`.

On any installation/test failure, the runner restores only its own changes and leaves the prior Phase 6 FIX_0002 state intact.
