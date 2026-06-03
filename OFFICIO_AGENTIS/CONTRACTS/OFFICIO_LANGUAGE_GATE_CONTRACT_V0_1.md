# OFFICIO LANGUAGE GATE CONTRACT V0.1

## Purpose

Define mandatory language discipline for Owner-facing communication in Officio-governed tasks.

## Mandatory language

- Owner-facing live progress, interim comments, and final Owner response must be Russian.
- Technical artifacts remain English-safe (paths, code, JSON keys, schemas, exact command output).

## Required acknowledgements

Before substantive work, agent must explicitly acknowledge:

- `ROLE_ACK`
- `LANGUAGE_ACK`
- `SCOPE_ACK`
- `STOP_CONDITIONS_ACK`
- `FORBIDDEN_ACTIONS_ACK`

## Allowed technical English fields

- code snippets;
- file paths;
- JSON/JSONL keys;
- schema field names;
- package/tool names;
- exact command output.

## Violation policy

If Owner-facing language drifts into long English commentary:

1. Correct course immediately in the next owner-facing message.
2. Continue in Russian.
3. Record `OFFICIO_LANGUAGE_VIOLATION_WARN` in reports.
4. Mark repeated violations as `violation` and recommend follow-up hardening.

## PASS boundary

This contract defines first-pass policy discipline only.
It does not claim full NLP-grade language enforcement.
