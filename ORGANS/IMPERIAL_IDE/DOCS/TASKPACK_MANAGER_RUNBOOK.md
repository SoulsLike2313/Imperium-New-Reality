# Taskpack Manager Runbook

Status: CANDIDATE_V0_1

## Commands

- taskpack-manager: list generated station taskpacks.
- taskpack-list: alias for the same list view.
- taskpack-inspect [TASK_ID]: inspect one generated taskpack, or latest when omitted.
- validate-taskpack [TASK_ID]: validate required root files for a generated taskpack.

## Required evidence

The manager shows ZIP path, SHA256, extracted root files, validation status, dry-run registration status, and live promotion availability.

## Safety

The manager does not auto-register live taskpacks. Live registration remains behind live-registration-promote with explicit owner confirmation.
