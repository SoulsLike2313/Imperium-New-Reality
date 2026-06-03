# SERVITOR_LLM_FOCUS_MATRIX

Status: CANDIDATE_NOT_CANON
Owner organ: OFFICIO_AGENTIS
Support organs: ASTRONOMICON, MECHANICUS, INQUISITION

| criterion_id | owner_organ | evidence_required | pass_logic | warn_logic | block_logic | score_or_delta | cap_mapping | remediation_path | forced_improvement |
|---|---|---|---|---|---|---|---|---|---|
| SF-01_ROLE_ENTRY_ACK_PRESENT | OFFICIO_AGENTIS | ghost_evolve_entry_ack.json | role, contour, head, sources, readiness recorded | one field missing and warned | no role entry ack | +20 | CAP_STAGE1_WITH_WARNINGS_ONLY | emit full role entry ack | prevents unguided execution |
| SF-02_TASK_FOCUS_PACKET_BUILT | ASTRONOMICON | context pack json + summary | focus packet generated pre-implementation | packet generated late | no packet | +25 | CAP_TASK_CONTEXT_BUILDER_MISSING | run builder first and store receipt | improves deterministic startup |
| SF-03_CAPABILITY_SPLIT_DECLARED | MECHANICUS | capability_split_receipt.json | all actions mapped to split classes | partial mapping | no split receipt | +20 | CAP_TOOL_SURFACE_CONTRACT_MISSING | classify actions and add evidence | avoids reasoning-as-capability drift |
| SF-04_FAKE_GREEN_ATTACKED | INQUISITION | hard_red_team_verdict.json | explicit downgrade logic exists | manual checks only | no red-team output | +20 | CAP_STAGE1_WITH_WARNINGS_ONLY | run closure gate and attach caps | keeps verdict honest |
| SF-05_OWNER_LANGUAGE_LANE_RESPECTED | OFFICIO_AGENTIS | final_owner_summary_ru.md + english machine artifacts | ru only in owner-facing lane | minor drift in report prose | cyrillic in machine policy artifacts | +15 | CAP_OWNER_LANGUAGE_NOT_ROUTED_THROUGH_OFFICIO | isolate ru output to final summary lane | prevents language policy drift |
