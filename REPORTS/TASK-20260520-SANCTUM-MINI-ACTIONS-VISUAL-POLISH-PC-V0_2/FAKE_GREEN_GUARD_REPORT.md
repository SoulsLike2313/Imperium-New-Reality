# FAKE_GREEN_GUARD_REPORT

- task_id: TASK-20260520-SANCTUM-MINI-ACTIONS-VISUAL-POLISH-PC-V0_2
- generated_at_utc: 2026-05-20T05:49:50.3890521Z

## Truth checks from API state sample

- active_organ: MECHANICUS_AGENT
- Mechanicus status: CONNECTED
- connected_organs_count: 1
- placeholders_count: 7
- locked_count: 2
- real organs: MECHANICUS_AGENT
- placeholder organs: ADMINISTRATUM_AGENT, OFFICIO_AGENTIS_AGENT, ASTRONOMICON_AGENT, INQUISITION_AGENT, DOCTRINARIUM_AGENT, STRATEGIUM_AGENT, SCHOLA_IMPERIALIS_AGENT
- locked organs: CUSTODES, THRONE

## Verdict

PASS: only MECHANICUS_AGENT is real/connected. Placeholder and locked organs remain explicit. No fake green escalation detected.
