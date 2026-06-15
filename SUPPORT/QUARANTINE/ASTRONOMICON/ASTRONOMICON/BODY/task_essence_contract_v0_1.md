# Task Essence Contract V0.1

A task essence must define the minimum truth required before execution.

Required fields:
- `task_id`
- `task_summary`
- `primary_organ`
- `support_organs`
- `out_of_scope`
- `success_criteria`
- `risks_and_gates`
- `stop_conditions`

Rules:
- Essence must be execution-oriented, not prose-only.
- Scope boundary must explicitly reject unrelated expansion.
- Gate references must be concrete and auditable.
- Success criteria must be testable with receipts.

Verdict policy:
- `PASS`: all required fields present and non-empty.
- `WARN`: minor ambiguity but bounded and explicitly marked.
- `BLOCK`: missing required fields, no scope boundary, or fake success shape.
