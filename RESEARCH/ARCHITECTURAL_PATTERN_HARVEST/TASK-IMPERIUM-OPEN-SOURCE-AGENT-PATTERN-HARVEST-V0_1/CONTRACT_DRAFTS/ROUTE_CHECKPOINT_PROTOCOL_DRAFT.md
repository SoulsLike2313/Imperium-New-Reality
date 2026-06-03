# Route / Checkpoint Protocol Draft

## Purpose

Make every multi-step agent route resumable, auditable, and inspectable.

## Route sheet

```json
{
  "route_id": "ROUTE-...",
  "task_id": "TASK-...",
  "created_at": "ISO-8601",
  "owner": "OWNER_OR_SERVITOR",
  "agents": [],
  "allowed_scope": [],
  "denied_scope": [],
  "expected_outputs": [],
  "approval_points": []
}
```

## Required behavior

- Write checkpoint after every meaningful step.
- Owner approval is a first-class checkpoint.
- Failed step must say whether route can resume.
- Runtime checkpoints stay in `RUNS/`.
