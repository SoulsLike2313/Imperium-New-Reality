# BLOCK_MATURITY_MATRIX

Status: CANDIDATE_NOT_CANON
Owner organ: STRATEGIUM
Support organs: DOCTRINARIUM, MECHANICUS, INQUISITION

| criterion_id | owner_organ | evidence_required | pass_logic | warn_logic | block_logic | score_or_delta | cap_mapping | remediation_path | forced_improvement |
|---|---|---|---|---|---|---|---|---|---|
| BM-01_BLOCK_MANIFEST_COMPLETE | DOCTRINARIUM | block manifest json + schema check | all required fields present | optional refs missing only | required identity/zone fields missing | +20 | CAP_BLOCK_STANDARD_MISSING | fill missing fields and revalidate | prevents fuzzy block definitions |
| BM-02_ZONE_BOUNDARY_EXPLICIT | INQUISITION | protected/editable/runtime declarations | all zones explicit and non-empty | one zone weakly documented | protected zone missing | +20 | CAP_PROTECTED_ZONE_CONTRACT_MISSING | declare zones in passports + manifest | prevents accidental high-risk edits |
| BM-03_CONTEXT_BUDGET_ENFORCED | MECHANICUS | builder + bloat detector receipts | within file and character budget | near budget with warning | no budget values or major overflow | +20 | CAP_CONTEXT_PACK_SCHEMA_MISSING | set budget and rerun detector | reduces context waste |
| BM-04_IMPROVEMENT_LOOP_PRESENT | SCHOLA_IMPERIALIS | improvement request files + learning rules | structured improvement loop exists | loop exists but missing evidence references | no improvement request contract | +20 | CAP_GHOST_EVOLVE_BLOCK_LEARNING_MISSING | adopt request schema and learning rules | converts pain into reusable upgrades |
| BM-05_RED_TEAM_DOWNGRADE_READY | INQUISITION | hard_red_team_verdict + claim ledger | downgrade path explicit | red-team manual only | no red-team verdict | +20 | CAP_STAGE1_WITH_WARNINGS_ONLY | run closure gate and record verdict | blocks fake-green closure |
