# Useful Patterns for IMPERIUM

## 1. Skill Bundle Protocol from MCP

MCP shows the value of separating the agent host from external capabilities. IMPERIUM should not adopt MCP as host now, but every local script/tool should become a Skill Bundle with:

- `skill_id`
- owner organ
- purpose
- input schema
- output schema
- allowed paths
- side effects
- receipts
- tests
- risk level
- Custodes admission status
- Mechanicus verification status

## 2. Route/Checkpoint Protocol from LangGraph

LangGraph's persistence pattern maps directly to IMPERIUM route checkpoints:

- route starts with route sheet
- every organ step writes checkpoint
- every checkpoint can be inspected
- execution can pause for Owner approval
- failed step resumes from last clean checkpoint
- route can be replayed for audit

## 3. Organ-Agent Protocol from Claude Code subagents

Claude Code subagents suggest a simple but powerful pattern: agent identity is a file, tool access is explicit, memory scope is configured, and visual identity helps the operator. IMPERIUM should implement:

- `AGENT_MANIFEST.json`
- `ROLE_CONTRACT.md`
- `TOOL_ADMISSION.json`
- `MEMORY_POLICY.md`
- `CLI_VISUAL_IDENTITY.json`
- `STATE/current_status.json`

## 4. Event Hooks and Receipts

Hooks reveal agent lifecycle points. IMPERIUM should write:

- `AGENT_START`
- `AGENT_ACCEPTED_TASK`
- `AGENT_REJECTED_TASK`
- `SKILL_STARTED`
- `SKILL_FINISHED`
- `CHECKPOINT_WRITTEN`
- `AGENT_STOP`

Each event should go to JSONL ledger and summary receipts.

## 5. Agent-Computer Interface from SWE-agent

The interface matters. Agents should not receive raw unlimited shell. They should use narrow commands:

- status
- inventory
- classify-path
- detect-dirty-runtime
- build-summary
- route
- validate

Each command has typed args, output path, and receipt.

## 6. Trajectory/Trace Pattern

Every route session should be inspectable later. Final answer is not enough. Store compact traces and Owner-readable summaries.

## 7. Workspace Permission Boundary from OpenHands

OpenHands reinforces the need for real workspace action, but IMPERIUM must constrain it:

- allowed paths
- denied paths
- write mode
- rollback plan
- dirty-state report
- owner confirmation for risky writes

## 8. SOP Pipeline from MetaGPT

SOPs are useful if they are real contracts, not theatrical roles. Organ handoffs need structured artifacts.

## 9. Flow vs Crew from CrewAI

Sanctum should be the route/flow controller. Organ-Agent groups are invoked by route cards, not free chat.

## 10. Typed Async Event Bus from AutoGen

Async agent work is useful later, but needs typed messages, run IDs, route IDs, sequence numbers, and conflict rules.

## 11. CLI Visual Comfort

Owner-facing CLI should be readable and pleasant:

- colored panels
- status badges
- short tables
- progress sections
- no white-wall flood
- machine files still JSON/JSONL
- no pretty fake green
