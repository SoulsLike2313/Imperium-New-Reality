# Strategium Task Budget Contract V0.1

Status: `CANDIDATE_V0_1`
Owner organ: `STRATEGIUM`

## Purpose

This contract creates a small, replayable budget gate for New Reality tasks. It does not claim production costing. It records planned budget, measured or explicitly unknown cost fields, scope expansion count, KPD verdict, and the next task budget recommendation.

## Required Task Budget Card

Each task budget card must include:

- `task_id`
- `budget_class_planned`
- `max_files_changed_target`
- `stop_if_scope_expands`
- `planned_scope`
- `required_receipts`
- `unknown_measurement_policy`
- `next_task_budget_recommendation`

## Required Task Cost Receipt

Each task cost receipt must include:

- `task_id`
- `budget_class_planned`
- `actual_cost_class`
- `files_changed_count`
- `commands_run_count` or `UNKNOWN_WITH_REASON`
- `validators_run_count` or `UNKNOWN_WITH_REASON`
- `wall_time_minutes` or `UNKNOWN_WITH_REASON`
- `token_usage` or `UNKNOWN_WITH_REASON`
- `owner_intervention_count` or `UNKNOWN_WITH_REASON`
- `scope_expansion_count`
- `kpd_verdict`
- `next_task_budget_recommendation`

If measured cost exceeds the planned budget class, the receipt must include `overrun_reason`.

## Required KPD Delta Receipt

Each KPD delta receipt must include a before/after summary, compact evidence paths, a verdict, and a next route. KPD values may stay qualitative in V0.1.

## Unknown Values

Unknown values are allowed only when represented as:

```json
{
  "status": "UNKNOWN_WITH_REASON",
  "reason": "Concrete reason."
}
```

Fake numeric values are forbidden.

## Boundary

This gate is a micro foundation. It does not create WARP costing, IDE telemetry, global production readiness, billing readiness, or full resource accounting.
