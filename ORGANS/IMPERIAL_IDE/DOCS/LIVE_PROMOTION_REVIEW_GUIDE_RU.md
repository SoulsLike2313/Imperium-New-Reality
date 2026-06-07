# Live Promotion Review Guide

Status: CANDIDATE_V0_1

Open review:

- python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py live-registration-promote
- python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py live-registration-promote TASKPACK_ID

Default state: LIVE_NOT_RUN.

Review shows candidate taskpack, canon current expected task, expected impact on current_expected_task.json, safety checks, dirty state checks, and required confirmation.

Live registration runs only with explicit manual token:

python ORGANS/IMPERIAL_IDE/SHELL/imperial_ide_cli.py live-registration-promote LIVE TASKPACK_ID

Smoke and normal review do not run live promotion.
