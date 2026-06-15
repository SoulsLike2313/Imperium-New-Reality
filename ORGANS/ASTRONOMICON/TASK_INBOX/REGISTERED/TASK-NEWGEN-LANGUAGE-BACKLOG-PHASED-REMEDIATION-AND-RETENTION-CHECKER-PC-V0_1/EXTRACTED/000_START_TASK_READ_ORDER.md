# START HERE - Language Backlog Phased Remediation and Retention Checker

Task: `TASK-NEWGEN-LANGUAGE-BACKLOG-PHASED-REMEDIATION-AND-RETENTION-CHECKER-PC-V0_1`

Preferred start mode:
1. Register this ZIP through Astronomicon intake.
2. Start Servitor with:

```text
TASK_ID: TASK-NEWGEN-LANGUAGE-BACKLOG-PHASED-REMEDIATION-AND-RETENTION-CHECKER-PC-V0_1
start task
```

Expected starting HEAD: `23727b55020775827aa0473f72e9132830004f6c`

This taskpack is English-only and UTF-8 without BOM.

Prime rule:
This is a small, controlled remediation and checker task. Do not perform a broad repository rewrite.

Mission:
- select a small safe P0 or P1 slice from the existing legacy language backlog;
- remediate only deterministic, low-risk cases with before and after evidence;
- produce backlog delta receipts;
- implement a retention checker for Astronomicon registered taskpack payloads;
- apply the checker to current registered taskpacks and produce an inventory delta;
- repeat independent language replay after changes;
- preserve strict scope and global scope semantics;
- commit and push admitted canonical changes.

No visual IDE. No WARP. No second micro-pilot. No VM3 execution. No freelance or trading execution.
