# IMPERIUM Native Contract Recommendations

## Contract 1 — Organ-Agent Protocol

Each Organ-Agent must have:

```text
AGENT_MANIFEST.json
ROLE_CONTRACT.md
POLICIES/
BRAIN_NODE/
SKILLS/
MEMORY/
INBOX/
OUTBOX/
STATE/
RECEIPTS/
REPORTS/
TESTS/
TOOLS/
RUNS/
```

Required machine fields:

```json
{
  "agent_id": "ADMINISTRATUM_AGENT",
  "organ": "ADMINISTRATUM",
  "status": "BASE_IMPLEMENTED_V0_1",
  "authority": [],
  "may_read": [],
  "may_write": [],
  "must_not_do": [],
  "tool_access": [],
  "memory_scope": "agent_owned",
  "runtime_output_policy": "RUNS_LAYER_ONLY",
  "receipt_required": true
}
```

## Contract 2 — Skill Bundle Protocol

Every script/tool/ability must be represented as a skill bundle.

Required files:

```text
skill_manifest.json
input_schema.json
output_schema.json
side_effects.md
run.py
README.md
tests/
receipts/
```

## Contract 3 — Route/Checkpoint Protocol

Every task route must be resumable and inspectable.

Required checkpoint fields:

```json
{
  "route_id": "ROUTE-...",
  "checkpoint_id": "CHK-...",
  "agent_id": "ADMINISTRATUM_AGENT",
  "step_id": "classify_repo",
  "input_refs": [],
  "output_refs": [],
  "verdict": "PASS",
  "resume_policy": "RESUME_FROM_THIS_CHECKPOINT",
  "owner_approval_required": false
}
```

## Contract 4 — Tool State Protocol

Tools must have state separate from agent memory:

```json
{
  "tool_id": "python_rich",
  "installed": false,
  "introduced_now": false,
  "verified": false,
  "owner_approved": false,
  "canon_status": "NOT_CANON",
  "sandbox_status": "REFERENCE_ONLY",
  "last_receipt": null
}
```

## Contract 5 — Permission/Admission Protocol

Before risky actions:

- Custodes validates path/scope.
- Inquisition validates fake-green risk.
- Mechanicus validates tool/script state.
- Owner approval required for deletion, canon promotion, cross-zone merge, external tool install.

## Contract 6 — Stress-Test Protocol

Every Organ-Agent needs stress tests:

- accept good input
- reject bad input
- block forbidden scope
- refuse direct canon mutation
- write receipt
- preserve clean tree
- respect output budget
- classify runtime correctly
- route to other organs correctly

## Contract 7 — CLI Visual Comfort Contract

Every CLI agent command should support:

```text
--plain-json
--pretty
--no-color
--compact
--verbose
```

Visual mode should show:

```text
[AGENT] [RUN] [STATUS]
Scope
Input
Checks
Actions
Outputs
Receipts
Warnings
Next action
```

Rule: presentation must never overwrite truth. JSON/JSONL reports are authoritative.
