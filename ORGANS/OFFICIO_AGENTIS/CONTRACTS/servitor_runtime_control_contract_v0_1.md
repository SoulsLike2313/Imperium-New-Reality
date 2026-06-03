# Servitor Runtime Control Contract V0.1

Status: CANDIDATE_V0_1
Owner organ: OFFICIO_AGENTIS
Support organs: ASTRONOMICON, DOCTRINARIUM, ADMINISTRATUM, MECHANICUS, INQUISITION, SPECULUM, SCHOLA_IMPERIALIS

## Purpose

Define a model-agnostic runtime control chain for any Servitor agent used inside New Reality.

The controlled agent may be Codex, Claude, Qwen, Kimi, Gemini, a local LLM, or a future CLI/API agent. Control must be issued by organs and recorded in receipts. Owner chat corrections are not a valid runtime control layer.

## Required Runtime Inputs

Every admitted Servitor run must receive:

1. Astronomicon launch context with task id, root, route manifest, read order, target contour, and caps.
2. Officio role and response contract with owner-facing runtime language and final response format.
3. Doctrinarium non-negotiable laws and forbidden claim boundaries.
4. Administratum current truth and evidence boundary.
5. Mechanicus tool and validator capability map.
6. Inquisition compliance and no-fake-green matrix.
7. Speculum architecture review hook when the task changes control surfaces.
8. Schola lesson capture hook for reusable failures and fixtures.

## Owner-Facing Runtime Language

Owner-facing live progress and final responses are Russian unless a task-specific Officio language contract says otherwise.

Machine artifacts, schemas, scripts, filenames, receipts, and canonical repo documents are English-safe UTF-8 without BOM.

## Manual Correction Rule

If Owner has to correct runtime behavior, language, scope, or final format manually, the run must record:

- drift_detected: true
- correction_source: OWNER_MANUAL_INTERVENTION
- agent_control_failure: true
- next_control_fix: a concrete organ-side correction

The task may still continue, but the failure must appear in the task report, claim ledger, and red-team verdict.

## Receipt Requirements

Each task that uses this contract must produce a servitor_control_chain_receipt.json containing:

- control_contract_issued_by_officio
- launch_context_injected_by_astronomicon
- doctrinarium_law_read
- inquisition_compliance_check_run
- observed_owner_facing_language
- required_owner_facing_language
- drift_detected
- correction_source
- agent_control_failure
- next_control_fix

## Verdict Semantics

- PASS: organ-issued control succeeded and no manual Owner correction was needed.
- PASS_WITH_WARNINGS: control artifacts exist but a disclosed drift or capability gap remains.
- BLOCK: required control artifacts are missing or a manual correction was hidden.

