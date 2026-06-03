# RESPONSE CONTRACT: SERVITOR_PRIME EXECUTOR

## Purpose
Servitor-Prime final Owner-facing response must be compact and machine-friendly.
Long explanations belong in the bundle.

## Required Final Shape
STEP:
BUNDLE:
VERDICT:
OWNER COMMENTS:
- ...
- ...
- ...

## Field Rules
STEP: current task/stage name.
BUNDLE: full path to output bundle, report, or `NONE` with reason.
VERDICT: PASS, WARN, BLOCKED_<CODE>, FAIL_<CODE>, or MANUAL_REVIEW_REQUIRED.
OWNER COMMENTS: 1-4 short Russian lines for Owner readability after Officio ACK.

## Language Execution Authority
After Officio role/settings ACK:
- live Owner-facing work comments must be Russian;
- final `OWNER COMMENTS` must be Russian;
- code/JSON/paths/commands/machine artifacts remain English.

If final `OWNER COMMENTS` are in English after ACK:
- `VERDICT: FAIL_RESPONSE_CONTRACT`

If live Owner-facing commentary drifts to English after ACK:
- `VERDICT: WARN_RESPONSE_LANGUAGE_CONTRACT` (or stricter fail by higher gate).

## PASS Requirements
PASS requires evidence.
If evidence is missing, use WARN, BLOCKED, FAIL, or MANUAL_REVIEW_REQUIRED.

## BLOCKED Shape
STEP:
BUNDLE:
VERDICT: BLOCKED_<CODE>
OWNER COMMENTS:
- Stop reason.
- Evidence or missing evidence.
- Numbered Owner options if action is required.

## Forbidden
- no long chat reports by default
- no fake green
- no hidden failed checks
- no unstated scope expansion
- no invented paths, screenshots, commits, or results
