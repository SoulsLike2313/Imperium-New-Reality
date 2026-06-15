# OUTPUT REQUIREMENTS

## Output root

REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-WORKBENCH-WARP-METAOS-INTEGRATION-PC-V0_2/

## Bundled input archives

Taskpack must include:

- SOURCE_BUNDLES/IMPERIAL_IDE_WORKBENCH_V0_1.zip
- SOURCE_BUNDLES/IMPERIUM_WARP_ZONE_V0_1.zip
- SOURCE_BUNDLES/IMPERIUM_METAOS_ORCHESTRATION_V0_1.zip

## Required repository outputs

Workbench destination:

- ORGANS/IMPERIAL_IDE/WORKBENCH/

WARP destination:

- ORGANS/IMPERIAL_IDE/WARP/

MetaOS destination:

- ORGANS/IMPERIAL_IDE/METAOS/

Required launchers:

- ORGANS/IMPERIAL_IDE/run_imperial_workbench.ps1
- ORGANS/IMPERIAL_IDE/run_warp_zone.ps1
- ORGANS/IMPERIAL_IDE/run_metaos_smoke.ps1

Required docs:

- ORGANS/IMPERIAL_IDE/DOCS/WORKBENCH_WARP_METAOS_USER_GUIDE_RU.md
- ORGANS/IMPERIAL_IDE/DOCS/WORKBENCH_WARP_METAOS_OPERATOR_FLOW.md
- ORGANS/IMPERIAL_IDE/DOCS/WARP_METAOS_RELEASE_GATE_MODEL.md
- ORGANS/IMPERIAL_IDE/DOCS/NEXT_REAL_EXECUTION_AND_LLM_GATE_PLAN.md

Required bridge files, if safe:

- ORGANS/MECHANICUS/IDE_BRIDGE/workbench_bridge_adapter.py
- ORGANS/MECHANICUS/IDE_BRIDGE/warp_bridge_adapter.py
- ORGANS/MECHANICUS/IDE_BRIDGE/metaos_bridge_adapter.py
- ORGANS/MECHANICUS/IDE_BRIDGE/workbench_warp_metaos_bridge_policy.json

Required Administratum files, if safe:

- ORGANS/ADMINISTRATUM/BUNDLE_GATES/README.md
- ORGANS/ADMINISTRATUM/BUNDLE_GATES/administratum_bundle_gate_adapter.py
- ORGANS/ADMINISTRATUM/BUNDLE_GATES/bundle_gate_policy.json

## Required report outputs

Report files under REPORTS/TASK-NEWREALITY-IMPERIAL-IDE-WORKBENCH-WARP-METAOS-INTEGRATION-PC-V0_2/:

- source_bundle_inventory.json
- workbench_candidate_import_receipt.json
- warp_candidate_import_receipt.json
- metaos_candidate_import_receipt.json
- workbench_normalization_receipt.json
- warp_normalization_receipt.json
- metaos_normalization_receipt.json
- workbench_smoke_receipt.json
- warp_smoke_receipt.json
- metaos_smoke_receipt.json
- mechanicus_triple_bridge_receipt.json
- administratum_bundle_gate_receipt.json
- servitor_runtime_integration_receipt.json
- launcher_integration_receipt.json
- runtime_gitignore_receipt.json
- safety_gate_receipt.json
- validation_receipt.json
- git_diff_scope_receipt.json
- git_commit_push_receipt.json
- continuity_pack.json
- FINAL_OWNER_SUMMARY_RU.md

## Required source_bundle_inventory.json fields

Must include:

- task_id;
- workbench_zip_path;
- workbench_sha256;
- workbench_file_count;
- workbench_top_level_files;
- warp_zip_path;
- warp_sha256;
- warp_file_count;
- warp_top_level_files;
- metaos_zip_path;
- metaos_sha256;
- metaos_file_count;
- metaos_top_level_files;
- timestamp.

## Required import receipt fields

Each import receipt must include:

- task_id;
- source_zip_path;
- source_sha256;
- destination_root;
- extracted_file_count;
- overwritten_files;
- skipped_files;
- conflict_resolution;
- status;
- timestamp.

## Required safety_gate_receipt.json fields

Must include:

- allow_real_enabled;
- unsafe_shell_available;
- real_servitor_execution_enabled;
- live_llm_backend_enabled;
- runtime_paths_staged;
- vm2_action;
- vm3_action;
- destructive_cleanup;
- result.

## Required git_commit_push_receipt.json fields

Must include:

- task_id;
- commit_sha;
- origin_master_sha;
- head_equals_origin_master_after_push;
- git_status_after_push;
- pushed_files_summary;
- validation_summary;
- timestamp.

## Final owner summary

FINAL_OWNER_SUMMARY_RU.md is Russian owner-facing output and must be short.

It must state:

- where Workbench was integrated;
- where WARP was integrated;
- where MetaOS was integrated;
- how to launch Workbench;
- how to launch WARP;
- how to launch MetaOS smoke;
- what is live and what is sample or candidate;
- what remains blocked for safety;
- whether push completed;
- next recommended task.

It must not claim full IDE completion.
It must not claim real servitor execution.
It must not claim unrestricted tool execution.
It must not claim live LLM backend is enabled.
