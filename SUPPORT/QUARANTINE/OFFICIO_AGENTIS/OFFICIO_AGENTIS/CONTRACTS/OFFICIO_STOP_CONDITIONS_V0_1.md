# OFFICIO STOP CONDITIONS V0.1

## Purpose

Codify reusable stop conditions for Officio execution discipline.

## Mandatory stop conditions

Stop and escalate when any condition is true:

- git truth mismatch;
- unrelated dirty worktree at admission;
- missing required task inputs/contracts;
- required forbidden path touch;
- destructive action required without Owner gate;
- install/network/cloud activation required outside approval;
- fake-green risk (evidence missing for PASS claim);
- unresolved organ ownership conflict.

## Stop response contract

When stop is triggered:

1. record stop reason;
2. record known evidence paths;
3. mark verdict `STOP` or `BLOCKED`;
4. request Owner decision only for true blockers.
