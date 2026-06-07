# Taskpack Manager Runbook

Status: CANDIDATE_V0_1

## Commands

- taskpack-manager: list generated station taskpacks.
- taskpacks: short alias for the generated taskpack list.
- taskpack-list: alias for the same list view.
- taskpack-inspect [TASK_ID]: inspect one generated taskpack, or latest when omitted.
- taskpack-validate [TASK_ID]: validate required root files for the latest or selected generated taskpack.
- taskpack-open [TASK_ID]: print a copy-ready command for opening the taskpack folder.
- taskpack-copy-path [TASK_ID]: print a copy-ready command for copying the TASKPACK.zip path.
- validate-taskpack [TASK_ID]: compatibility command; when omitted it may build and validate a sample taskpack.

## Required evidence

The manager shows ZIP path, SHA256, extracted root files, validation status, dry-run registration status, and live promotion availability.

## Safety

The manager does not auto-register live taskpacks. Live registration remains behind live-registration-promote with explicit owner confirmation.
