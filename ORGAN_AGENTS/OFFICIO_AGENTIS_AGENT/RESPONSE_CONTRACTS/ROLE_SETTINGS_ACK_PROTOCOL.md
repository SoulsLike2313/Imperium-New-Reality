# ROLE SETTINGS ACK PROTOCOL

## Purpose
Before serious Officio-controlled work, an agent must be able to acknowledge which role, mode, settings, restrictions, stop conditions, and response contract it received.

## ACK_ROLE Shape
ACK_ROLE:
- agent_id:
- role_name:
- role_family:
- operating_nature:
- default_mode:
- role_profile_path:
- role_profile_hash:
- timestamp_utc:

## ACK_SETTINGS Shape
ACK_SETTINGS:
- agent_id:
- role_name:
- active_mode:
- permissions_ref:
- forbidden_actions_ref:
- stop_conditions_ref:
- evidence_policy_ref:
- response_contract_ref:
- communication_contract_ref:
- bootstrap_execution_directive_ref:
- language_execution_contract_ref:
- role_settings_ack_protocol_ref:
- owner_live_commentary_language_after_officio_ack:
- owner_final_comments_language_after_officio_ack:
- machine_artifact_language:
- violation_codes:
- settings_hash:
- timestamp_utc:

## Failure Rule
If role/settings ACK is required but missing, Servitor must stop with:

VERDICT: BLOCKED_OFFICIO_ACK_MISSING

If role pack authority files are missing, stop with:

VERDICT: BLOCKED_ROLE_PACK_AUTHORITY_MISSING

## Evidence Rule
ACK files should be saved into the task run evidence folder when execution is launched through Officio.

## Anti-crutch Rule
Owner-facing language requirements must be acknowledged from Officio-owned contracts.
Taskpack-only wording is not sufficient authority.
