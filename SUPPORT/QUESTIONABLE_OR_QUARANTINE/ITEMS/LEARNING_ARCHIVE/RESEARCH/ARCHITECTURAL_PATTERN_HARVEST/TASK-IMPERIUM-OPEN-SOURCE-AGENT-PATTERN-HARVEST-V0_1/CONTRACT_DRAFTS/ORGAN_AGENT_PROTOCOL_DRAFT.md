# Organ-Agent Protocol Draft

## Purpose

Define the minimum shape of a local IMPERIUM Organ-Agent.

## Required folders

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

## Required identity fields

```json
{
  "agent_id": "ADMINISTRATUM_AGENT",
  "organ": "ADMINISTRATUM",
  "version": "V1",
  "status": "DRAFT_OR_IMPLEMENTED",
  "role": "memory_archive_inventory_provenance_routing",
  "authority": [],
  "limits": [],
  "may_read": [],
  "may_write": [],
  "must_not_write": [],
  "must_not_do": [],
  "tool_access_policy": "ALLOWLIST_ONLY",
  "memory_scope": "AGENT_OWNED",
  "receipt_required": true
}
```

## Agent lifecycle

1. `AGENT_START`
2. `INPUT_ACCEPTANCE_CHECK`
3. `ROUTE_OR_SKILL_SELECTED`
4. `SKILL_START`
5. `SKILL_FINISH`
6. `CHECKPOINT_WRITTEN`
7. `REPORT_WRITTEN`
8. `RECEIPT_WRITTEN`
9. `AGENT_STOP`
