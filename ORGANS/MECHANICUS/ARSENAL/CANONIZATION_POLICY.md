# Mechanicus Arsenal Canonization Policy V0.1

Status: CANDIDATE_V0_1
Owner organ: MECHANICUS

## Purpose

Store Skill, API, and tool candidates without uncontrolled installs or fake canon claims.

## Candidate States

- CANDIDATE
- SANDBOX_READY
- SANDBOX_TESTED
- ADMITTED
- CANON
- QUARANTINE
- REJECTED_FOR_NOW

## Candidate Storage

Candidates are stored under:

- ORGANS/MECHANICUS/ARSENAL/SKILL_CANDIDATES/
- ORGANS/MECHANICUS/ARSENAL/API_CANDIDATES/
- ORGANS/MECHANICUS/ARSENAL/TOOL_CANDIDATES/

## Required Card Fields

Each candidate card must include:

- candidate_id
- name
- type
- category
- owner_organ
- purpose
- first_safe_use_case
- risk
- admission_mode
- install_status
- receipt_requirements
- canon_after_successful_cycles

## Canon Rule

A candidate can become canon only after 10 successful task cycles with receipts.

## Install Rule

This storage does not grant install permission. Installs require explicit Mechanicus admission, owner-approved scope, rollback plan, and validation receipts.

