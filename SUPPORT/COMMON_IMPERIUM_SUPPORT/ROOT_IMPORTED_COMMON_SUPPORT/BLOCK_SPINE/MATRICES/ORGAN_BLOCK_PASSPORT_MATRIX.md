# ORGAN_BLOCK_PASSPORT_MATRIX

Status: CANDIDATE_NOT_CANON
Owner organ: OFFICIO_AGENTIS
Support organs: ASTRONOMICON, INQUISITION

| criterion_id | owner_organ | evidence_required | pass_logic | warn_logic | block_logic | score_or_delta | cap_mapping | remediation_path | forced_improvement |
|---|---|---|---|---|---|---|---|---|---|
| OP-01_ALL_ACTIVE_ORGANS_HAVE_PASSPORT | ASTRONOMICON | 8 passport json files | all 8 organs have passport skeletons | one organ missing non-critical field | one or more passport files missing | +30 | CAP_ORGAN_BLOCK_PASSPORTS_MISSING | create missing files from template | ensures route completeness |
| OP-02_READ_FIRST_COMPACT_PRESENT | OFFICIO_AGENTIS | read_first_compact files | compact read-first exists per organ | file exists but too broad | compact file missing | +20 | CAP_ORGAN_FILE_DECORATIVE_NOT_USED | add compact read-first with mandatory paths | lowers startup overhead |
| OP-03_CONTEXT_DIGEST_PRESENT | MECHANICUS | context digest files | digest present and concise | digest verbose but usable | digest missing | +20 | CAP_CONTEXT_PACK_SCHEMA_MISSING | create digest and rerun builder | enables context pack automation |
| OP-04_IMPROVEMENT_REQUEST_LANE_DEFINED | SCHOLA_IMPERIALIS | improvement refs in passport | improvement lane declared | lane declared without ownership | no improvement lane | +15 | CAP_GHOST_EVOLVE_BLOCK_LEARNING_MISSING | map to request schema | converts issues into backlog |
| OP-05_PROTECTED_ZONES_DECLARED | INQUISITION | protected_zones fields | protected zones defined per organ | zones too broad | no protected zones | +15 | CAP_PROTECTED_ZONE_CONTRACT_MISSING | define precise protected zones | protects critical authority files |
