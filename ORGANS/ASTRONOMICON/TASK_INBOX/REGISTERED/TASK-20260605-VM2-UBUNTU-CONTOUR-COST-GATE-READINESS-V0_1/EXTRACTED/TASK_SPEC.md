# TASK-20260605-VM2-UBUNTU-CONTOUR-COST-GATE-READINESS-V0_1

## Mission

Introduce VM2 Ubuntu contour into active New Reality work in a controlled, cheap, and evidence-heavy way.

This is a micro task, not a broad feature wave. The Servitor must verify that VM2 is synced, compatible with the PC/Windows operator route over SSH, and able to participate in the standard Astronomicon-to-Administratum task flow.

The task must also introduce the first Strategium cost gate foundation so future tasks become cheaper and measurable.

## Required role entry

1. Read the registered Astronomicon task.
2. Read OFFICIO_AGENTIS task participation first.
3. Enter Servitor role through OFFICIO.
4. After OFFICIO role entry, owner-facing live and final responses must be Russian.
5. Machine artifacts must remain ENGLISH UTF8 NO_BOM.

## Work zones

Allowed root: New Reality repository on VM2 Ubuntu.

Expected VM2 root may be: `$HOME/IMPERIUM_NEW_GENERATION_NEW_REALITY`. If the actual root differs, record it with evidence and do not fake pass.

Allowed paths:

- ORGANS/STRATEGIUM/COST_GATE/
- ORGANS/MECHANICUS/TOOL_REGISTRY/ or existing Mechanicus accepted registry path
- ORGANS/ADMINISTRATUM/POST_WORK_BUNDLE/ only for compatibility/readme hooks if needed
- REPORTS/TASK-20260605-VM2-UBUNTU-CONTOUR-COST-GATE-READINESS-V0_1/
- ORGANS/ASTRONOMICON/TASK_INBOX/REGISTERED/TASK-20260605-VM2-UBUNTU-CONTOUR-COST-GATE-READINESS-V0_1/ only as registered task evidence

## Work items

### A. VM2 contour readiness proof

Create a VM2 readiness receipt in the report folder. It must record:

- operating system family and version;
- hostname;
- shell;
- repo root;
- python version;
- git version;
- local HEAD;
- origin/master HEAD;
- clean or dirty worktree status before work;
- whether local HEAD equals origin/master at start;
- whether the New Reality root contains Astronomicon task entry corridor;
- whether the Post-Work Bundle V0.2 assets exist;
- whether the 9-organ ring assets exist.

### B. Windows PC to Ubuntu VM2 compatibility note

Create a compatibility note and receipt explaining how PC/Windows operator path maps to VM2 Ubuntu path. Include:

- PC command route: SSH from PC to VM2;
- VM2 repo root path;
- path separator rules;
- line ending risk;
- UTF8 NO_BOM rule;
- executable bit or shebang risk for scripts;
- PowerShell versus bash command difference;
- no Ancient Empire access rule.

### C. Strategium cost gate v0.1 micro foundation

Create a minimal Strategium cost gate zone with:

- TASK_BUDGET_CONTRACT_V0_1.md
- task_budget_card.schema.json
- task_cost_receipt.schema.json
- kpd_delta_receipt.schema.json
- TEMPLATES/TASK_BUDGET_CARD_TEMPLATE.json
- TEMPLATES/TASK_COST_RECEIPT_TEMPLATE.json
- TEMPLATES/KPD_DELTA_RECEIPT_TEMPLATE.json
- strategium_task_cost_checker_v0_1.py

The checker may be small, but it must run and validate at least one positive fixture and one negative fixture.

Cost receipt fields must include:

- task_id;
- budget_class_planned;
- actual_cost_class;
- files_changed_count;
- commands_run_count or UNKNOWN_WITH_REASON;
- validators_run_count or UNKNOWN_WITH_REASON;
- wall_time_minutes or UNKNOWN_WITH_REASON;
- token_usage or UNKNOWN_WITH_REASON;
- owner_intervention_count or UNKNOWN_WITH_REASON;
- scope_expansion_count;
- kpd_verdict;
- next_task_budget_recommendation.

### D. Mechanicus registration

If a new checker script is added, create or update a Mechanicus tool card for it. The tool card must include command, inputs, outputs, owner organ, validator route, and risk/status.

### E. Post-work bundle

Produce a report bundle index for this task using the existing Administratum post-work bundle conventions. If V0.2 checker exists, run it or explain precisely why it cannot run on VM2.

## Enhanced Ghost Evolve

The Servitor must teach organs strongly but cheaply. Do not add broad theory. Convert each useful lesson into a compact organ-owned artifact. If a discovered rule cannot be implemented in this task, create a Schola learning receipt and a next-route card.

## Hard stop conditions

Stop and report BLOCK if:

- VM2 repo is not synced with origin/master at start and cannot be safely synced;
- worktree is dirty before work and dirty state is not explained;
- task tries to expand into WARP, IDE, or major bundle redesign;
- any required machine artifact would need Cyrillic text;
- cost gate grows beyond micro scope.
