# IMPERIUM-APP-DAILY-USE-REGISTRATION-WORKFLOW-0001

Purpose: establish the daily-use two-phase registration workflow for the Tauri app.

This patch does not perform the visual refactor. It creates the UI-refit candidate pack and upgrades registration so Astronomicon + Mechanicus can analyze that candidate first.

Changes:
- Tauri backend recognizes `CANDIDATE_INTAKE_PACK` vs `POLISHED_EXECUTION_PACK`.
- Candidate packs are blocked from app launch.
- Astronomicon can return `REGISTERABLE_CANDIDATE_PACK`.
- Mechanicus can return `MECHANICUS_ANALYZES_CANDIDATE_REQUIRES_POLISHED_PACK`.
- App Astronomicon room shows Candidate → Polished Pack → Launch Gate workflow.
- Adds `IMPERIUM-APP-DAILY-USE-UI-REFIT-CANDIDATE-0001` as the next complex registration target.

No real execution is enabled.
