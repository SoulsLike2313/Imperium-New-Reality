# CONTEXT_PACK_ECONOMY_MATRIX

Status: CANDIDATE_NOT_CANON
Owner organ: ASTRONOMICON
Support organs: MECHANICUS, INQUISITION

| criterion_id | owner_organ | evidence_required | pass_logic | warn_logic | block_logic | score_or_delta | cap_mapping | remediation_path | forced_improvement |
|---|---|---|---|---|---|---|---|---|---|
| CE-01_MANDATORY_ONLY_DEFAULT | ASTRONOMICON | context pack json | mandatory list is separated from optional list | optional list present but unclear | no mandatory/optional split | +25 | CAP_TASK_CONTEXT_BUILDER_MISSING | enforce split in builder output | avoids broad read by default |
| CE-02_DIGEST_FIRST_LOADING | OFFICIO_AGENTIS | organ digest paths in pack | all active organs include digest entry | one organ missing digest | most organs missing digest | +20 | CAP_ORGAN_BLOCK_PASSPORTS_MISSING | create missing digest files | faster orientation and less noise |
| CE-03_DUPLICATE_READ_FIRST_CHECK | MECHANICUS | bloat detector receipt | no duplicate read-first entries | duplicates flagged with warning | duplicates ignored while pass claimed | +20 | CAP_CONTEXT_BLOAT_DETECTOR_MISSING | deduplicate and rerun detector | prevents circular loading |
| CE-04_PROTECTED_ZONE_VISIBLE | INQUISITION | protected_zones list in pack | protected zones for each required organ exist | partial protected zones | protected zones absent | +20 | CAP_PROTECTED_ZONE_CONTRACT_MISSING | add zone declarations in passports | prevents unsafe edits |
| CE-05_EXPECTED_OUTPUT_DECLARED | ADMINISTRATUM | expected_outputs list | outputs and receipts declared | outputs partial | outputs absent | +15 | CAP_PENDING_COMMIT_PUSH_FIELDS_LEFT_OPEN | restore output contract from taskpack | improves closure reliability |
