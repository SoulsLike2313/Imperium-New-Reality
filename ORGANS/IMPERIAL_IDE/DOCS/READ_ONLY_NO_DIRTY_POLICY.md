# Read-only No-dirty Policy

Status: CANDIDATE_V0_1

Read-only Imperial IDE commands must not modify tracked repository files.

## Read-only commands

help, station, agents, agent-status, taskpack-manager, taskpack-inspect, dirty-classifier, safety, git-closure, reports-latest, receipts-latest, show-summary, show-json, full-json, launch-card, handoff-card, daily-ops, operator-board, next-action, task-flow, lifecycle.

## Allowed writes

- explicit smoke commands may write validation/report receipts;
- explicit build/register commands may write ignored runtime/generated taskpack paths;
- post-push inspection must not rewrite committed reports;
- shell receipts must show mutates_repo.

The no_dirty_guard smoke compares tracked diff fingerprints before and after the read-only command set.
