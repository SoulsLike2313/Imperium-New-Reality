# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-IMPERIUM-SELF-ANALYSIS-LIVE-GIT-PICTURE-PC-V0_3/

## Required machine readable files

### imperium_new_reality_full_picture.json

Must include:

- generated_at
- hostname
- repo_root
- branch
- head_sha
- origin_master_sha
- head_equals_origin_master
- git_status_short
- top_level_entries
- zone_counts
- organ_count
- report_count
- support_count
- quarantine_count
- symlink_inventory
- file_type_counts
- risks
- next_recommended_task

### organ_core_map.json

Must include one record per organ directory with:

- organ_id
- path
- file_count
- known_contract_files
- known_tool_files
- known_report_files
- current_status
- risks
- next_required_action

### zone_inventory.json

Must include:

- active_core
- support
- reports
- quarantine
- learning_archive
- generated_or_runtime
- unknown
- candidate_to_canon

## Required human readable files

### IMPERIUM_NEW_REALITY_FULL_PICTURE.md

Must explain the current New Reality system shape in a form useful for Owner and Logos Prime.

### LIVE_GIT_ADDENDUM_PC.md

Must include PC git evidence and dirty state.

### astronomicon_local_pc_registration_and_route_drift_report.md

Must explain PC local registration status and route config drift as a repair issue.

It must recommend a fix that makes the skill discover its route config without manual arguments later.

### mechanicus_current_readiness_snapshot.md

Must explain current Mechanicus readiness and what is required to move toward script first local tool control.

### passport_constitution_agents_patch_plan.md

Must propose patches only. It must not overwrite files.

### servitor_next_task_recommendation.md

Must propose the next taskpack and why it should be next.

### FINAL_OWNER_SUMMARY_RU.md

This is the only required owner facing Russian output.

It is allowed only after Officio role entry and must not be used as proof of technical completion.
