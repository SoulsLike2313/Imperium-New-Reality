# Launch Context Injection Contract V0.1

Status: CANDIDATE_V0_1
Owner organ: ASTRONOMICON
Support organs: OFFICIO_AGENTIS, ADMINISTRATUM, MECHANICUS, INQUISITION

## Purpose

Ensure every Servitor starts from a bounded New Reality launch context instead of relying on ad-hoc memory, parent folders, or Owner correction.

## Required Fields

Launch context must include:

- task_id
- active_root
- route_manifest_path
- registered_task_path
- extracted_taskpack_path
- read_order
- required_organs
- owner_facing_language_contract
- machine_artifact_language_contract
- root_scope_policy
- remote_policy
- caps_to_carry
- expected_start_head when available
- target_contour when available

## Injection Rules

1. Resolve the active root through the New Reality root resolver.
2. Reject Ancient Empire as active runtime root.
3. Load the task route manifest from the registered New Reality task inbox.
4. Load Officio language and final response contracts before any Owner-facing runtime output.
5. Record missing launch fields in the task report before implementation starts.
6. Never use a parent path or Ancient Empire bridge unless a task provides explicit salvage admission and receipt requirements.

## Evidence

Each task must record the launch context status in either preflight_truth_receipt.json or servitor_control_chain_receipt.json.

## Verdict Semantics

- PASS: all required launch context fields are available and rooted in New Reality.
- PASS_WITH_WARNINGS: launch context is usable but carries disclosed caps or missing optional fields.
- BLOCK: active root, task id, route manifest, or scope policy cannot be resolved.

