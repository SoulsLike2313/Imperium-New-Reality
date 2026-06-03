# OFFICIO ROLE ACK BLOCK TEMPLATE V0.1

```text
GATE_ACK:
- task_id: <TASK-ID>
- current_head: <GIT-HEAD>
- gatepack_path: <PATH-TO-TASKPACK-OR-DOSSIER>
- gatepack_sha256: <SHA256>
- read_gates: [GATE-U00, GATE-U01, GATE-U02, GATE-U04, GATE-U05, GATE-U08, GATE-U09]
- accepted_stop_conditions:
  - unclear task scope
  - unrelated dirty tree
  - missing required input
  - forbidden scope expansion
  - destructive action risk
  - fake green risk
- scope_boundary: <ALLOWED PATHS ONLY>
- touched_paths: <EXPECTED PATHS>
- forbidden_paths: <FORBIDDEN PATHS>
- expected_receipts: <REPORT/RECEIPT LIST>
- repo_recon_required: true/false
- script_absorption_required: true/false
- clarification_needed: true/false
- verdict: PASS | STOP | CLARIFY
```
