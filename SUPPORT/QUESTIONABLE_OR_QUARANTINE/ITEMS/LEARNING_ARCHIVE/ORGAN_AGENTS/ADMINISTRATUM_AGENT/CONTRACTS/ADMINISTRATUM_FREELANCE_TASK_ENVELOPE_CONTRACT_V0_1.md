# ADMINISTRATUM FREELANCE TASK ENVELOPE CONTRACT V0.1

## Purpose

Define the scoped task envelope Administratum-Agent may accept for freelance/client work.

Administratum does not implement the client solution. It performs intake, context mapping, evidence packaging, privacy classification, and handoff routing.

## Required Envelope

The canonical machine envelope is:

```json
{
  "task_id": "FREELANCE-TASK-...",
  "client_goal": "...",
  "assigned_organ": "ADMINISTRATUM_AGENT",
  "administratum_scope": ["intake", "context_map", "evidence_pack", "handoff"],
  "input_refs": [],
  "privacy_level": "public",
  "allowed_actions": [],
  "forbidden_actions": [],
  "deliverables_required": [],
  "acceptance_criteria": [],
  "evidence_required": [],
  "handoff_target": "MECHANICUS_AGENT",
  "owner_decision_required": false
}
```

## Output Duties

Administratum freelance output must include:

- intake summary;
- input reference map;
- privacy classification;
- evidence package references;
- deliverable and handoff checklist;
- limitations;
- next organ recommendation.

## Safety Rules

- No private payload content export by default.
- Metadata references are allowed when payload content is restricted.
- Forbidden actions or outside-scope edits must return `BLOCKED`.
- Default exchange packages are markdown/json and must not include PDF.
