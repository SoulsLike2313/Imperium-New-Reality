# OFFICIO TASK ADMISSION RULES V0.1

## Purpose

Define mandatory admission checks before Officio starts execution.

## Admission checklist

Required before edits:

1. task id is present;
2. expected starting HEAD is declared;
3. current HEAD matches expected;
4. allowed write paths and forbidden paths are explicit;
5. required gates are listed;
6. `GATE_ACK` verdict is `PASS`;
7. expected reports/receipts are declared;
8. stop conditions are accepted and non-empty.

## Admission verdicts

- `PASS`: all fields present and verifiable.
- `CLARIFY`: information incomplete but recoverable.
- `STOP`: critical truth/safety mismatch.

## Scope rule

If required outputs can be produced within scoped Officio paths, execution may continue.
If outputs force forbidden paths, stop and escalate.
