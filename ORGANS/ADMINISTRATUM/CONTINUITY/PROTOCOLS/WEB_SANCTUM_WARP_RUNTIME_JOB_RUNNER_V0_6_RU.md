# Web Sanctum WARP Runtime + Job Runner v0.6

V0.6 promotes Web Sanctum from static dashboard into an allowlisted operational shell.

Core rules:

- Browser never receives arbitrary shell access.
- Buttons call `action_id` only.
- Local bridge validates action against allowlist and returns `job_id`.
- Long-running tasks are polled through `/api/jobs/<job_id>`.
- Mechanicus owns action metadata.
- Administratum owns receipts and final report bundle.
- Astronomicon owns taskpack admission and active task gate.
- Inquisition/validation blocks dirty promotion.

Visual rule: every patch may add premium atmosphere, but operational clarity wins over decoration.
