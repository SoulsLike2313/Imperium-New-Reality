# ADMINISTRATUM OSS ADMISSION CONTRACT V0.1

## Purpose
Control optional OSS usage without unsafe implicit dependency drift.

## Lifecycle states
- candidate
- admitted_if_available
- sandbox_candidate
- future_candidate
- rejected

## Mandatory record fields
- tool id
- purpose
- scope
- risk
- fallback
- admission status
- detection method
- availability snapshot

## Hard rules
- No auto-install in operational tasks.
- No silent hard dependency introduction.
- Detection only unless Owner explicitly approves installation.
