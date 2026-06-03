# MECHANICUS Servitor Contract V0.1

## Input Contract

Servitor query must include:
- `task_id`
- `question`
- optional `mode`

## Output Contract

Return `newgen_organ_verdict_v0_1` with:
- capability/gate status;
- required tool actions;
- forbidden unsafe tool operations;
- evidence refs for tool health.

## BLOCK Conditions

- mandatory TUI capability (`rich`) missing and cannot be verified/installed;
- required registry/receipt output missing for capability acquisition path;
- destructive tool action attempted out of scope.

## WARN Conditions

- capability available but metadata/receipt set is partial.

## Not-Proven Boundary

- full production-grade tool admission framework;
- full autonomic remediation.
