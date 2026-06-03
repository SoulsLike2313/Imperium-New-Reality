# AGENTS.md - IMPERIUM Agent Bootloader V0.2

## Purpose

This is the first file every agent must read before editing anything in this repository.

This file is a bootloader and router. It does not duplicate all doctrine. It tells the agent:
- what truth checks to run first;
- what gates are mandatory;
- what files to read by task class;
- what shortcuts are forbidden;
- how to report, preserve tools, and stop safely.

IMPERIUM is not a normal repository. It is an operating body made of organs, gates, scripts, receipts, dashboards, and future agent profiles. An agent must not work as an isolated chatbot. It must work as a bounded unit inside IMPERIUM.

## Universal First Truth Check

Before editing anything:

```powershell
cd E:\IMPERIUM
git status --short
git rev-parse --show-toplevel
git rev-parse HEAD
git branch --show-current
git ls-remote origin refs/heads/master
```

STOP if:
- repo root is not `E:\IMPERIUM`;
- branch is not the expected branch;
- HEAD does not match the task-required starting HEAD;
- worktree is dirty before work unless the task explicitly begins with dirty-state classification;
- required orientation/gate files are missing.

## Universal Admission Rules

No agent is admitted to work unless it has:
1. task id;
2. required starting HEAD;
3. allowed write paths;
4. forbidden paths;
5. required gates;
6. GATE_ACK before edits;
7. report/receipt/action-card requirements;
8. STOP conditions.

Missing GATE_ACK means the work is not admitted.

## Mandatory Gate Families

Always consider these gates:
- `GATE-U00-GIT-TRUTH`
- `GATE-U01-ROLE-ACK`
- `GATE-U02-SCOPE-BOUNDARY`
- `GATE-U04-EVIDENCE-RECEIPT`
- `GATE-U05-STOP-CONDITIONS`
- `GATE-U08-REPO-PURITY`
- `GATE-U09-NO-FAKE-GREEN`
- `GATE-U12-REPORT-OUTPUT-BUDGET`
- `GATE-U13-PYTHON-TYPE-SAFETY`
- `GATE-U14-WHOLE-REPO-SCOPE-RECON`
- `GATE-U15-OPERATIONALITY-IMPACT`
- `GATE-U16-BILINGUAL-UI`
- `GATE-U17-DELIVERABLE-PACKAGE`
- `GATE-U18-AGENT-FACTORY-COMPLIANCE`
- `GATE-U19-SCRIPT-ARTIFACT-PRESERVATION`
- `GATE-U20-AGENT-KPD-SELF-REVIEW`
- `GATE-U21-COMMAND-CHUNKING`

Read canonical gate details from:
- `ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json`
- `ORGANS/DOCTRINARIUM/GATES/UNIVERSAL_GATE_LAWS_V0_1.md`
- `ORGANS/DOCTRINARIUM/GATES/BASE_MANDATORY_GATES_V0_1.md`

## Task-Class Reading Routes

### Any task
Read:
- `AGENTS.md`
- `ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json`
- `ORGANS/DOCTRINARIUM/GATES/UNIVERSAL_GATE_LAWS_V0_1.md`
- `ORGANS/OFFICIO_AGENTIS/RESPONSE_CONTRACTS/AGENT_GATE_ACK_CONTRACT_V0_1.md`

### Whole-repo / roadmap / planning task
Read:
- `ORGANS/ASTRONOMICON/ROADMAPS/IMPERIUM_OPERATIONALITY_70_WHOLE_REPO_FUSION_ROADMAP_V0_1.md`
- `ORGANS/ADMINISTRATUM/READINESS/OPERATIONALITY_70_READINESS_MATRIX_V0_1.md`
- orientation PDFs under `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/SECOND_BRAIN_V07_VISUAL_SYSTEM_20260517/`

### Script / tool task
Read:
- `ORGANS/MECHANICUS/SCRIPTORIUM/PYTHON_TYPE_SAFETY/SCRIPT_TYPE_SAFETY_POLICY_V0_1.md`
- `ORGANS/MECHANICUS/SCRIPTORIUM/SCRIPT_ARTIFACT_PRESERVATION_POLICY_V0_1.md`
- `ORGANS/MECHANICUS/SCRIPTORIUM/TEMP_SCRIPT_BUFFER_POLICY_V0_1.md`
- `ORGANS/MECHANICUS/SCRIPTORIUM/COMMAND_DISCIPLINE/COMMAND_CHUNKING_DISCIPLINE_V0_1.md`

### Big-model / Codex / Kiro / high-reasoning task
Read:
- `ORGANS/OFFICIO_AGENTIS/AGENT_SETTINGS/BIG_MODEL_AGENT_OPERATING_RULES_V0_1.md`
- `ORGANS/OFFICIO_AGENTIS/RESPONSE_CONTRACTS/AGENT_KPD_SELF_REVIEW_CONTRACT_V0_1.md`
- `ORGANS/INQUISITION/GATE_AUDITS/AGENT_EXECUTION_INQUISITION_AUDIT_RULES_V0_1.md`

### Local executor task
Read:
- `ORGANS/OFFICIO_AGENTIS/AGENT_SETTINGS/LOCAL_EXECUTOR_AGENT_RULES_V0_1.md`

### Runtime / browser / performance task
Read:
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/FULL_RUNTIME_AUDIT_SAFETY_CONTRACT_V0_1.md`
- `ORGANS/INQUISITION/GATE_AUDITS/FULL_RUNTIME_AUDIT_SAFETY_RULES_V0_1.md`
- `ORGANS/DOCTRINARIUM/GATES/REPORT_OUTPUT_BUDGET_V0_1.md`

### Visual / UI / dashboard task
Read:
- `ORGANS/SANCTUM/CONTROL_CENTER/CONTROL_CENTER_MVP_REQUIREMENTS_V0_1.md`
- `ORGANS/SANCTUM/CONTROL_CENTER/BILINGUAL_UI_POLICY_V0_1.md`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/VISUAL_LAYER_CONTRACT_V0_1.md`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/PERFORMANCE_BUDGET_V0_1.json`

### Freelance / delivery task
Read:
- `ORGANS/ASTRONOMICON/FREELANCE_CORRIDOR/FREELANCE_CORRIDOR_MVP_CONTRACT_V0_1.md`
- `ORGANS/MECHANICUS/DELIVERABLE_FACTORY/DELIVERABLE_FACTORY_MVP_CONTRACT_V0_1.md`

### Agent-factory task
Read:
- `ORGANS/OFFICIO_AGENTIS/AGENT_FACTORY/AGENT_FACTORY_FOUNDATION_CONCEPT_V0_1.md`
- `ORGANS/DOCTRINARIUM/GATES/AGENT_FACTORY_COMPLIANCE_GATE_V0_1.md`

## Command Discipline

Do not use huge monolithic PowerShell or shell command blocks.

Large work must be split into compact phases:
1. create core docs;
2. validate;
3. create gates/registry updates;
4. validate;
5. create reports/receipts/action cards;
6. validate JSON/JSONL/report budget;
7. inspect diff/status;
8. commit/push only if clean.

If a command-length limit or partial dirty start appears, STOP and recover through quarantine or explicit cleanup.

## Tool Preservation

If you create a script, helper, parser, checker, runner, temporary generator, or useful command file:
- do not silently delete it;
- preserve it in a controlled buffer or register why it is unsafe/useless;
- include it in the tool/artifact preservation manifest;
- recommend absorb/rewrite/negative-sample/discard-after-review.

## Big Model KPD Review

Large reasoning agents must include KPD self-review:
- what was wasteful;
- what tools were missing;
- what generated tools should be preserved;
- what narrower future agent profile would improve execution;
- what context pack would increase useful action density.

Small local executors may skip deep reflection unless the task explicitly requires it.

## Owner-Facing Language and Encoding

Canonical machine artifacts should be English / UTF-8 safe by default.
Owner-facing action cards, summaries, and live chat may be Russian.
Dashboards and applications must support both Russian and English.
No mojibake is acceptable.

## Mandatory Final Response

For normal task completion:
1. step name;
2. full path to reports/receipts/action card;
3. verdict;
4. short Russian Owner comment;
5. next allowed task.

For auto-push task:
1. step name;
2. verdict;
3. new commit hash;
4. GitHub commit URL;
5. worktree clean yes/no and remote sync yes/no;
6. micro-summary and next allowed task.

## Never Claim

Do not claim:
- Control Center implemented if only requirements exist;
- Agent Factory implemented if only concept exists;
- runtime baseline valid if CSS/JS/assets/API failed;
- visual build admitted before truth/performance gates pass;
- freelance corridor ready before delivery package path exists;
- strict type safety complete without evidence;
- PASS without receipt.

## When Unsure

STOP. Report:
- what is unclear;
- what you read;
- what paths are affected;
- what options exist;
- what Owner decision is needed.
