# TASK_INBOX — Stage2 Canonical Intake

Canonical taskpack intake belongs to Astronomicon.

Layout:
- `TASK_INBOX/REGISTERED/<TASK_ID>/TASKPACK.zip`
- `TASK_INBOX/REGISTERED/<TASK_ID>/EXTRACTED/**`
- `TASK_INBOX/REGISTERED/<TASK_ID>/TASKPACK_ADMISSION_RECEIPT.json`
- `TASK_INBOX/REGISTERED/<TASK_ID>/TASK_ROUTE_MANIFEST.json`
- `TASK_INBOX/REGISTERED/<TASK_ID>/TASK_START_ACK_TEMPLATE.json`

Rules:
- Owner may provide only `task_id` + `start task` after registration.
- Resolver must map `task_id` through Astronomicon registry.
- Root `_TASKPACK_INBOX` (if present) is temporary local staging only; it is not canonical task truth.
- No clean PASS claims; Stage2 remains `PASS_WITH_WARNINGS` until real-use pilot and independent review.
