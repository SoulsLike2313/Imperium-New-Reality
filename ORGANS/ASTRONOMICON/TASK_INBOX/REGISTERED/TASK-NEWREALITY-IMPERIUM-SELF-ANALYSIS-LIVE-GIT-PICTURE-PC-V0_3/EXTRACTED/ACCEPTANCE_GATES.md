# ACCEPTANCE GATES

## Gate 1: Astronomicon local PC admission

PASS_WITH_WARNINGS is acceptable.
Clean PASS is forbidden for this stage.

Required:

- taskpack is admitted through Astronomicon on PC or an admission blocker is fully reported
- TASK_ROUTE_MANIFEST_TEMPLATE.json is present in the taskpack
- TASK_START_ACK_TEMPLATE.json is present in the taskpack
- current expected task is updated if admission succeeds
- no live success is claimed without registry evidence

## Gate 2: route manifest compatibility

Required:

- TASK_ROUTE_MANIFEST_TEMPLATE.json is present in the taskpack root
- TASK_START_ACK_TEMPLATE.json is present in the taskpack root
- MANIFEST.route_manifest_template points to TASK_ROUTE_MANIFEST_TEMPLATE.json
- MANIFEST.task_start_ack_template points to TASK_START_ACK_TEMPLATE.json
- TASK_ROUTE_MANIFEST_TEMPLATE.organs includes all eight required organs

## Gate 3: organ route

Required:

- MANIFEST.organs includes all eight required organs
- MANIFEST.required_organs mirrors the same eight organs for compatibility
- MANIFEST.organ_route explains each organ responsibility

Required organs:

- DOCTRINARIUM
- OFFICIO_AGENTIS
- ASTRONOMICON
- ADMINISTRATUM
- MECHANICUS
- INQUISITION
- STRATEGIUM
- SCHOLA_IMPERIALIS

## Gate 4: language gate

Required:

- MANIFEST.language_and_encoding_policy is an object
- taskpack_internal_files policy is explicit ENGLISH UTF8
- canonical_repo_artifacts policy is explicit ENGLISH UTF8
- owner facing Russian runtime output is routed through OFFICIO_AGENTIS
- Cyrillic is forbidden inside taskpack internal files
- localization exception is limited to owner facing final summary after Officio role entry

## Gate 5: PC live git truth

Required outputs:

- branch name
- HEAD SHA
- origin/master SHA
- HEAD equals origin/master yes or no
- git status short
- last 10 commits
- dirty state classification

BLOCK if live git truth is claimed without git evidence.

## Gate 6: New Reality full picture

Required outputs:

- IMPERIUM_NEW_REALITY_FULL_PICTURE.md
- imperium_new_reality_full_picture.json
- organ_core_map.json
- zone_inventory.json

These outputs must describe active core, support, reports, quarantine, learning archive, generated artifacts, and unknowns.

## Gate 7: Astronomicon local and route drift analysis

Required output:

- astronomicon_local_pc_registration_and_route_drift_report.md

It must compare:

- local PC registration behavior
- previous VM2 route failure pattern as context only
- config path discovery issue
- required fix for no argument operator workflow

## Gate 8: Mechanicus readiness snapshot

Required output:

- mechanicus_current_readiness_snapshot.md

It must classify capabilities as:

- PROVEN
- CANDIDATE
- MISSING
- BLOCKED

## Gate 9: no destructive action

Required:

- no delete
- no move
- no reset hard
- no git clean
- no push
- no remote route
- no VM2 action
- no VM3 action
- no canon admission
- no rewrite of AGENTS, Constitution, or Emperor Passport

Any violation is BLOCK.

## Gate 10: final package

Required report directory:

REPORTS/TASK-NEWREALITY-IMPERIUM-SELF-ANALYSIS-LIVE-GIT-PICTURE-PC-V0_3/

Required files:

- IMPERIUM_NEW_REALITY_FULL_PICTURE.md
- imperium_new_reality_full_picture.json
- LIVE_GIT_ADDENDUM_PC.md
- organ_core_map.json
- zone_inventory.json
- astronomicon_local_pc_registration_and_route_drift_report.md
- mechanicus_current_readiness_snapshot.md
- passport_constitution_agents_patch_plan.md
- servitor_next_task_recommendation.md
- FINAL_OWNER_SUMMARY_RU.md

Final verdict must be one of:

- PASS_WITH_WARNINGS_READY_FOR_CORE_CLEANUP_PLAN
- BLOCKED_UNTIL_ASTRONOMICON_ADMISSION_REPAIR
- BLOCKED_UNTIL_GIT_STATE_CLARITY
- BLOCKED_UNTIL_OWNER_DECISION
