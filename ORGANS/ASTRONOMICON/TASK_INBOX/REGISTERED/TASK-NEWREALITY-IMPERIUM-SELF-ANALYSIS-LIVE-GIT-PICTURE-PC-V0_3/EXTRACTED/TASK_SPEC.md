# TASK SPEC

## Task ID

TASK-NEWREALITY-IMPERIUM-SELF-ANALYSIS-LIVE-GIT-PICTURE-PC-V0_3

## Mode

READ_ONLY_SELF_ANALYSIS_WITH_REPORT_OUTPUTS.

This task is for the PC contour only.

This task must not perform cleanup, deletion, file moves, canon admission, remote route execution, VM2 execution, VM3 execution, live transfer, WARP activation, or production execution.

## Mission

Produce a full live picture of Imperium New Reality from the PC git workspace.

The Servitor must analyze the current New Reality repository as it exists on PC, not an extracted archive, not VM2, not VM3, and not the Ancient repository.

The report must make the system easier to read, clean, and operate through Imperium itself.

## Required self-analysis scope

1. Record the live git state of New Reality on PC.
2. Produce a top level repository map.
3. Produce an organ map for all active organ directories.
4. Separate active core, reports, support, quarantine, learning archive, candidate, generated, and unknown zones.
5. Identify high level dirt without performing cleanup.
6. Identify duplicate and versioning risk classes without deleting files.
7. Analyze Astronomicon task entry and local PC registration state.
8. Analyze why VM2 remote route was attempted and why future PC tasks should not depend on VM2.
9. Analyze Astronomicon route config discovery drift as a repair topic, not as a blocker for this PC task.
10. Analyze Mechanicus readiness as a script first local tool organ.
11. Identify which Mechanicus capabilities are proven, candidate, or missing.
12. Prepare patch plan only for Emperor Passport, Constitution, and AGENTS.md.
13. Recommend the next safe Servitor taskpack.

## PC only boundary

Active execution contour is PC.

Allowed:

- local PC Astronomicon registration
- local PC read only git and inventory commands
- local PC report output under allowed report path
- read only analysis of New Reality files

Forbidden:

- SSH to VM2 or VM3
- remote route execution
- remote sync
- copying taskpack to VM2 or VM3
- treating VM2 state as required evidence
- cleaning VM2
- using Ancient repository as active truth

## New Reality boundary

Active truth is Imperium New Reality only.

Ancient repository may be mentioned only as read only historical context if already referenced by the task context. It must not be used as active truth and must not be copied into New Reality.

## Required live commands

The Servitor should run read only commands such as:

- git status --short
- git status -sb
- git rev-parse HEAD
- git rev-parse origin/master
- git log --oneline --decorate -10
- git ls-files
- git ls-files -o --exclude-standard
- git status --porcelain=v1 --ignored
- PowerShell or Python inventory without following symlink directories

Every command used as evidence must be recorded in a command receipt.

## Required findings

The report must explicitly answer:

1. What is the current shape of New Reality on PC?
2. What is active core?
3. What is support?
4. What is quarantine or learning archive?
5. What is report or evidence history?
6. What is generated or runtime residue?
7. Which parts are safe to read but not safe to treat as canon?
8. Which Astronomicon local PC registration pieces work?
9. Which Astronomicon route config pieces are drifting?
10. What should be fixed so Astronomicon works without manual route config arguments later?
11. What is Mechanicus ready to do now?
12. What must Mechanicus become next?
13. Which next task should Owner approve?

## Stop conditions

Stop and report BLOCK if:

- repo root cannot be resolved
- git status cannot be read
- HEAD cannot be resolved
- any required action would become destructive
- any action would require remote execution
- any action would require canon admission
- any action would require rewriting core documents
