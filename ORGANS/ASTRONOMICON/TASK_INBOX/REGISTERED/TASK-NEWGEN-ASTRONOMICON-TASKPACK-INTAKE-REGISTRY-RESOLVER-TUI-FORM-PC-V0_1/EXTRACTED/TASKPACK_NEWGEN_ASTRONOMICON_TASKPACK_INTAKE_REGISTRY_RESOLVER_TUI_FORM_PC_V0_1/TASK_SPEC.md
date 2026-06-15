# Task Spec — Astronomicon Taskpack Intake, Registry, Resolver, and Minimal TUI Form

Task ID: `TASK-NEWGEN-ASTRONOMICON-TASKPACK-INTAKE-REGISTRY-RESOLVER-TUI-FORM-PC-V0_1`

## Background

Stage 1 created 8-organ task participation form and a synthetic task-entry proof.

Latest known chain:
- Stage 1 bundle commit: `620f11d402fd3aa3c330ac37108e1e4104c15f52`
- Stage 1 finalization/continuity head: `f10c55079274035df89ac076df2bc8cd82916a51`
- Stage 0 P0 remediation head: `f68fac35d04ec917238bec97edee738191d8c72e`

Merged Logos verdict after Stage 1:
- `PASS_WITH_WARNINGS`
- all 8 organs have Stage 1 task-participation packets;
- Astronomicon task entry corridor exists in synthetic form;
- next task must harden resolver behavior and owner-facing intake flow.

Owner requested the next form:

> Open Astronomicon TUI, provide a taskpack ZIP in an intake window/form, and Astronomicon should unpack/register it as the next expected task.

## Goal

Create the first usable Astronomicon intake corridor.

This task must make the taskpack ZIP become an official Astronomicon task entry, instead of a loose ZIP passed directly in chat.

## Owner workflow target

V0.1 workflow:

1. Owner has a taskpack ZIP.
2. Owner opens/runs Astronomicon TUI/form.
3. Owner enters/pastes ZIP path.
4. Tool validates the taskpack.
5. Tool extracts taskpack to canonical registered task path.
6. Tool reads `MANIFEST.json` and required task files.
7. Tool creates admission receipt.
8. Tool updates task registry.
9. Tool writes `current_expected_task.json`.
10. Owner copies `task_id`.
11. Owner gives Servitor: `TASK_ID: <task_id>` and `start task`.
12. Servitor resolves task ID through Astronomicon.

## Canonical paths

Prefer this structure, unless repo already has better equivalent:

```text
IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/
  TASK_INBOX/
    REGISTERED/
      <TASK_ID>/
        TASKPACK.zip
        EXTRACTED/
        TASKPACK_ADMISSION_RECEIPT.json
        TASK_ROUTE_MANIFEST.json
        TASK_START_ACK_TEMPLATE.json
  TASK_REGISTRY/
    task_registry.json
    current_expected_task.json
  TASK_ENTRY_CORRIDOR/
    TASKPACK_INTAKE_CONTRACT.md
    TASKPACK_INTAKE_CONTRACT.json
    TASKPACK_ADMISSION_CONTRACT.json
    TASK_ID_RESOLVER_CONTRACT.json
    TASK_ROUTE_MANIFEST_TEMPLATE.json
    TASK_START_ACK_TEMPLATE.json
  TOOLS/
    astronomicon_taskpack_intake_v0_1.py
    astronomicon_task_id_resolver_v0_1.py
    astronomicon_task_entry_tui_v0_1.py
```

## Root `_TASKPACK_INBOX` policy

If root `_TASKPACK_INBOX` exists:

- do not delete it blindly;
- classify it as local temporary staging unless Astronomicon explicitly registers it;
- add policy: root `_TASKPACK_INBOX` is not canonical task truth;
- canonical task inbox belongs to Astronomicon;
- if useful, the TUI may accept ZIPs from that folder as input source but must register them into Astronomicon.

## Required intake validation

Taskpack admission must check:

- ZIP exists;
- ZIP is readable;
- SHA256 computed;
- `MANIFEST.json` exists;
- `task_id` exists;
- `TASK_SPEC.md` exists or equivalent;
- `ACCEPTANCE_GATES.md` exists or equivalent;
- `OUTPUT_REQUIREMENTS.md` exists or equivalent;
- task_id is not duplicate in registry;
- extracted path is safe and stays under Astronomicon registered task root;
- route manifest can be created;
- 8-organ read route can be attached.

Admission verdicts:
- `ADMISSION_PASS`
- `ADMISSION_PASS_WITH_WARNINGS`
- `ADMISSION_BLOCK`

## Required resolver behavior

Resolver must support:

- resolve by exact `task_id`;
- return registered path;
- return taskpack ZIP path;
- return extracted path;
- return route manifest path;
- return current expected task;
- detect missing task;
- detect duplicate task;
- detect registry corruption;
- produce resolver receipt.

## Required minimal TUI/form

Create a minimal owner-facing TUI/form.

It can be stdlib-only text interface, not final visual IDE.

Must support at least:

- show current expected task;
- register taskpack by ZIP path;
- print task_id after admission;
- show admission verdict;
- show registered path;
- show resolver status;
- show simple next instruction for Owner:
  `Give Servitor: TASK_ID: <task_id> and start task`

Do not build rich visual IDE.
Do not build React/Tauri/HTML UI here.

## Required fixtures

Create synthetic fixtures for:

Positive:
1. valid taskpack ZIP registers successfully;
2. expected task is updated;
3. resolver finds task_id;
4. start ACK can reference all 8 organ participation packets.

Negative:
1. missing ZIP;
2. unreadable/bad ZIP;
3. missing MANIFEST;
4. missing task_id;
5. duplicate task_id;
6. missing TASK_SPEC;
7. missing route manifest template;
8. unsafe extraction path attempt;
9. registry task exists but extracted artifact missing;
10. organ read-first ACK missing.

## Required reports/receipts

Recommended report root:

`IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/REPORTS/TASK-NEWGEN-ASTRONOMICON-TASKPACK-INTAKE-REGISTRY-RESOLVER-TUI-FORM-PC-V0_1/`

Required:
- `ghost_evolve_entry_ack.json`
- `repo_truth_probe.json`
- `taskpack_intake_implementation_report.md`
- `taskpack_admission_fixture_report.md`
- `task_id_resolver_fixture_report.md`
- `minimal_tui_form_report.md`
- `current_expected_task_registration_receipt.json`
- `TASKPACK_ADMISSION_RECEIPT.example.json`
- `TASK_ROUTE_MANIFEST.example.json`
- `TASK_START_ACK.example.json`
- `GHOST_EVOLVE_STAGE2_LEARNING_BACKLOG.json`
- `GHOST_EVOLVE_STAGE2_LEARNING_BACKLOG.md`
- `NEXT_PIPELINE_HANDOFF.json`
- `efficiency_delta_receipt.json`
- `hard_red_team_verdict.json`
- `final_owner_summary_ru.md`
- `commit_push_receipt.json`

## Ghost_Evolve teaching requirement

Every encountered gap must become one of:

- Astronomicon route improvement;
- Matrix update candidate;
- Inquisition cap candidate;
- Mechanicus checker/tool need;
- Administratum receipt/history need;
- Officio task-start language/role need;
- Schola lesson;
- Strategium roadmap note.

If learning backlog is missing, task cannot pass.

## Allowed scope

Prefer:
- `IMPERIUM_NEW_GENERATION/ORGANS/ASTRONOMICON/**`
- `IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/**` for receipts/continuity only
- `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/**` for tool registration/checker references only
- `IMPERIUM_NEW_GENERATION/ORGANS/INQUISITION/**` for caps/red-team references only
- `IMPERIUM_NEW_GENERATION/ORGANS/SCHOLA_IMPERIALIS/**` for lessons only
- `IMPERIUM_NEW_GENERATION/ORGANS/STRATEGIUM/**` for roadmap note only
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/**` for route/cap matrix updates only
- task-specific reports/receipts

Avoid `AGENTS.md` unless absolutely necessary.

Forbidden:
- final visual IDE implementation;
- WARP activation;
- real runtime/freelance claim;
- broad unrelated UI/backend edits;
- mass legacy receipt migration;
- deleting old evidence without receipt;
- private/secrets;
- Throne/Custodes scope.

## Commit/push

PC Servitor must commit and push admitted diffs.
If commit/push is blocked, produce BLOCK report and do not fake success.
