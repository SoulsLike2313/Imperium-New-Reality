# Servitor Execution Contract V0.1

Role: `VM3_SERVITOR`  
Scope: `IMPERIUM_NEW_GENERATION only`

## Mandatory Boot Order

Before edits:

1. Read `IMPERIUM_NEW_GENERATION/AGENTS.md`.
2. Run Doctrinarium preflight:

```bash
python3 IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TOOLS/doctrinarium_preflight_v0_1.py --task-type <task_type>
```

3. Read Officio contracts in `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/`.
4. Read taskpack ZIP for concrete scope.
5. Generate Officio boot ack:

```bash
python3 IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/TOOLS/officio_boot_ack_v0_1.py \
  --task-id <task_id> \
  --task-type <task_type> \
  --taskpack-path <taskpack_zip_path> \
  --preflight-json <preflight_output_json_path> \
  --output <officio_role_contract_ack_json_path>
```

6. Report applicable laws/gates/role/scope in Russian.
7. Only then begin scoped edits.

## Mandatory Execution Discipline

- One task = one chat.
- Target context budget = 256k.
- Taskpack is not full memory carrier.
- No fake green.
- No generic PASS.
- Every critical claim must have evidence reference.

## STOP Conditions

Stop and wait if:

1. Git truth mismatch.
2. Worktree dirty before admission and unsafe to clean.
3. Doctrinarium preflight is missing or failed.
4. Officio contract files are missing or invalid.
5. Organ route requests `Owner Verdict Needed`.
6. Scope requires forbidden paths.
