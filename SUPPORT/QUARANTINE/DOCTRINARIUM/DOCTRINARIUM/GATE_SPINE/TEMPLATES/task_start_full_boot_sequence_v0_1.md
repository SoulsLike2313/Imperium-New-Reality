# Full Boot Sequence Template V0.1

Use this start block in future NewGen taskpacks and task-start messages.

## Before Any Edits

1. Read `IMPERIUM_NEW_GENERATION/AGENTS.md`.
2. Run Doctrinarium preflight:

```bash
python3 IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TOOLS/doctrinarium_preflight_v0_1.py --task-type <task_type> --output <preflight_json_path>
```

3. Read Officio boot contracts:
   - `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/officio_role_contract_v0_1.json`
   - `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/servitor_execution_contract_v0_1.md`
   - `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/owner_facing_language_contract_v0_1.md`
   - `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/final_response_contract_v0_1.md`

4. Read taskpack ZIP (concrete task scope only).

5. Generate Officio ack:

```bash
python3 IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/TOOLS/officio_boot_ack_v0_1.py \
  --task-id <task_id> \
  --task-type <task_type> \
  --taskpack-path <taskpack_zip_path> \
  --preflight-json <preflight_json_path> \
  --output <officio_role_contract_ack_path>
```

6. Report in Russian before editing:
   - task id;
   - repo path + HEAD;
   - required declarations;
   - active gates;
   - forbidden patterns;
   - role/scope;
   - PASS/FAIL criteria;
   - not-proven boundary.

7. Only then begin scoped edits.

## Mandatory Runtime Rules

- Owner-facing live commentary: Russian.
- Code/JSON/paths/logs/schemas: English allowed.
- If organ route returns `Owner Verdict Needed`, STOP and wait.
- No generic PASS. No fake green.
