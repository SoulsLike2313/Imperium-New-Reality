# TASK SPEC

## Task ID

H-TASK-NEWREALITY-H-TUI-DAILY-OPS-VISUAL-POLISH-AND-HANDY-WORKFLOW-V0-2-PC-V0_1

## Class

HANDY_IMPERIUM_H manual chat-driven patch task.

## Title

H TUI Daily Ops Visual Polish and Handy Workflow V0.2

## Intent

Improve Imperial IDE H-contour daily operations UX through manual chat-driven patch workflow: polish Dashboard, Daily Ops, Agent Roster, Taskpack Manager, Launch/Handoff Card, Dirty/Git Closure readability, and make Handy task registration practical for future manual patches.

## Target

Work only in Imperium H contour: E:\IMPERIUM_NEW_GENERATION_NEW_REALITY_H

## Workflow

1. Gather evidence ZIP from the H contour.
2. Review files in chat.
3. Produce PATCH-H ZIP with APPLY_PATCH.ps1 and ROLLBACK_PATCH.ps1.
4. Apply patch in H contour only.
5. Owner manually tests.
6. If accepted, Owner commits with IMPERIUM_H author identity.
7. Mainline receives the work only by reviewed cherry-pick.

## Files to read

- AGENTS.md
- ORGANS/IMPERIAL_IDE/WORKBENCH/TUI
- ORGANS/IMPERIAL_IDE/STATION
- ORGANS/IMPERIAL_IDE/SHELL
- ORGANS/IMPERIAL_IDE/AGENTS
- ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL
- ORGANS/ASTRONOMICON/TASK_REGISTRY
- ORGANS/ASTRONOMICON/TASK_INBOX

## Files to patch

- ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py
- ORGANS/IMPERIAL_IDE/STATION/daily_ops_shell.py
- ORGANS/IMPERIAL_IDE/STATION/operator_next_action.py
- ORGANS/IMPERIAL_IDE/STATION/taskpack_manager.py
- ORGANS/IMPERIAL_IDE/STATION/dirty_classifier.py
- ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py
- ORGANS/ASTRONOMICON/SKILLS/TASKPACK_REGISTRATION_SKILL/astronomicon_taskpack_registration_skill_v0_1.py
