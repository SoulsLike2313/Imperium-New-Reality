# Mandatory Doctrinarium Task-Start Block (V0.1)

Use this block before any edits in future NewGen task start messages.

```text
DOCTRINARIUM_READ_FIRST_ACK:
- task_id: <TASK_ID>
- task_type: <core_task|visual_cockpit|tool_acquisition|continuity|repo_hygiene|organ_directive|freelance_external>
- preflight_command: python3 IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TOOLS/doctrinarium_preflight_v0_1.py --task-type <task_type>
- declaration_index: IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/declaration_index_v0_1.json
- gate_registry: IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/gate_registry_v0_1.json
- required_declarations:
  - <path_1>
  - <path_2>
- active_gates:
  - <GATE_ID_1>
  - <GATE_ID_2>
- forbidden_patterns:
  - <FP-XXX>
- pass_criteria:
  - <criterion>
- fail_criteria:
  - <criterion>
- evidence_required:
  - <artifact_or_path>
- not_proven_boundary:
  - full organ intelligence
  - automatic enforcement across all taskpacks
  - final visual quality
  - production autonomy
- verdict_boundary: PASS_FOR_<SLICE>_ONLY
```

If this block is missing, task cannot claim PASS.
