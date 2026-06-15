# TASK SPEC

Task ID: `TASK-NEWGEN-ADMINISTRATUM-CONTINUITY-PACK-SKILL-AND-LOGOS-HANDOFF-BRIDGE-PC-V0_1`

Title: Administratum Continuity Pack Skill and Logos-Prime handoff bridge.

Target contour: `PC`.

Start message: `start task`.

## Purpose

Build the first Administratum-owned Continuity Pack Skill. The Owner needs a stable mechanism that prepares a new Logos-Prime or new chat with the current IMPERIUM state without manual reconstruction, stale context, private-data leaks or huge unbounded dumps.

This is a Skill, not merely a launcher. It is an operational hand of Administratum. The future IDE may call it as a UI action, but IDE must not become the truth source.

## Operational note

This task should be registered through the Astronomicon Taskpack Registration Skill on PC contour. The Owner wants to open Astronomicon TUI, choose Register Taskpack, select this ZIP, choose PC, and see how the registration happens inside the Skill.

## Required implementation scope

Create or harden an Administratum Skill package under an appropriate Administratum-owned path, preferably:

`IMPERIUM_NEW_GENERATION/ORGANS/ADMINISTRATUM/SKILLS/CONTINUITY_PACK_SKILL/`

The Skill must be able to build a controlled continuity pack for Logos-Prime handoff.

## Required behavior

The Skill must collect:

- current git truth;
- HEAD, branch, remote sync status and worktree state;
- latest accepted task chain;
- current expected task and latest Astronomicon task links if available;
- active caps and warnings;
- important receipts/report paths;
- organ state summary stubs where reliable;
- source index;
- private-data exclusion receipt;
- stale-context audit;
- Russian Owner-facing handoff summary routed through Officio;
- English machine-readable handoff summary for internal artifacts;
- SHA256 checks and final continuity ZIP receipt.

## Required constraints

Do not dump the whole repository. Do not collect secrets. Do not include private files from external local/private context areas unless explicitly whitelisted, and for this task no private collection is required. Prefer indexes, receipts and summaries over raw bulk.

## Required learning

Record this as an Administratum Skill. Register that Astronomicon owns taskpack registration, while Administratum owns continuity/handoff packs. Record IDE as a future caller only.
