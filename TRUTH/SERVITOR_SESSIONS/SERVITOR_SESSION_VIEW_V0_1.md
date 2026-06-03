# SERVITOR_SESSION_VIEW_V0_1

## Purpose

Foundation-only read-only model for Sanctum NG that shows:

- task/session identity;
- run/rerun timeline from existing artifacts;
- organ dialogue references;
- action layer status references;
- evidence references;
- acceptance semantics and limitations.

## Scope

This view is strictly read-only and artifact-backed.

It does **not** claim:

- live autonomous execution;
- production readiness;
- live organ intelligence.

## Canonical artifacts

- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/DATA/servitor_session_view_state.generated.json`
- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/servitor_session_view_state.schema.json`
- `IMPERIUM_NEW_GENERATION/SANCTUM_NG/CONTRACTS/servitor_session_timeline_event.schema.json`
- `IMPERIUM_NEW_GENERATION/TRUTH/SERVITOR_SESSIONS/SERVITOR_SESSION_STATUS_RULES_V0_1.json`
- `IMPERIUM_NEW_GENERATION/TRUTH/SERVITOR_SESSIONS/SERVITOR_SESSION_VIEW_REGISTRY_V0_1.json`

## No-fake-green rule

`PASS_STRICT` is forbidden unless event/report has explicit evidence reference.
