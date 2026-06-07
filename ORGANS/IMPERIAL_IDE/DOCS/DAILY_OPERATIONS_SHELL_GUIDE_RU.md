# Daily Operations Shell Guide

Status: CANDIDATE_V0_1

## Open

Commands:

- python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py daily-ops
- python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py operator-board
- python ORGANS/IMPERIAL_IDE/WORKBENCH/TUI/imperial_tui.py

## Board

- system truth: root, branch, HEAD, origin/master;
- current task and current expected task;
- real 12-agent roster summary;
- latest generated taskpack;
- launch card and handoff card;
- lifecycle, safety, dirty state, git closure;
- next recommended action.

task-flow shows the daily sequence: start day, inspect system, create task, build taskpack, validate, dry-run register, review promotion, copy launch/handoff, watch lifecycle, inspect reports/receipts, close task, prepare next task.

Live registration and real execution do not run automatically.
