# Live Registration Promotion Runbook

Status: CANDIDATE_V0_1

## Flow

1. Dry-run taskpack is built and validated.
2. Taskpack Manager shows the candidate taskpack.
3. live-registration-promote shows current expected task impact.
4. Safety and scope checks are shown.
5. Owner must provide the exact confirmation token: CONFIRM_LIVE_REGISTRATION.
6. Only local PC Astronomicon registration is allowed.
7. Promotion receipt records result.

## Default

Smoke and UI preview never auto-promote. Without the confirmation token, the result is PROMOTION_AVAILABLE or PROMOTION_BLOCKED only.
