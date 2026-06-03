# Task Volume Control V0.1

## Purpose

Task volume controls execution density before implementation starts.
Scope tells where an agent may edit.
Volume tells how much can be executed safely and accurately in one pass.

## Required size classes

- SMALL: 1 organ, 1-10 files, low evidence volume, one-pass execution.
- MEDIUM: 1-2 organs, 10-30 files, one pass with strong final report.
- LARGE: 3-5 organs or 30-80 files, staged execution required.
- MEGA: 6+ organs or mixed shell/audit/sweep/report planes, phased execution required.

## Required fields

A task volume control JSON must include:
- task_id
- task_size_class
- context_budget_class
- organ_count
- expected_file_touch_class
- expected_command_count_class
- expected_evidence_volume_class
- accuracy_risk
- checkpoint_required
- checkpoint_cadence
- split_required_if
- continuation_protocol_required
- recommended_execution_phases

## Enforcement rules

- LARGE and MEGA tasks must set `checkpoint_required=true`.
- LARGE and MEGA tasks must include at least 2 execution phases.
- MEGA tasks should include an explicit split rule and continuation protocol.
- If uncertainty remains, verdict must become `SPLIT_REQUIRED` or `BLOCKED`, not fake green.

## Context budget classes

- LOW: compact context, low entropy, stable requirements.
- MEDIUM: moderate context and dependencies.
- HIGH: many files/organs or evolving constraints.
- EXTREME: cross-organ control/system work with high ambiguity risk.

## Recommended cadence

- SMALL: END_ONLY
- MEDIUM: END_ONLY or MILESTONE
- LARGE: PER_STAGE
- MEGA: PER_STAGE with explicit owner decision points
