# ASTRONOMICON Servitor Contract V0.1

## Input Contract

Servitor query must include:
- `task_id`
- `question`
- optional `mode`

## Output Contract

Return `newgen_organ_verdict_v0_1` with:
- verdict and applied gates;
- required task registration/stage actions;
- forbidden bypass actions;
- evidence requirements;
- explicit not-proven boundary.

## BLOCK Conditions

- task not registered/classified;
- stage route absent or contradictory;
- pass/fail criteria absent;
- active/archive transition ignored.

## WARN Conditions

- route exists but remains partial and explicitly bounded.

## Not-Proven Boundary

- live owner route editor button;
- full automatic stage generator;
- production autonomy.

