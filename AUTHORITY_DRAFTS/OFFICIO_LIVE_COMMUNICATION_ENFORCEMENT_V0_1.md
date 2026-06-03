# OFFICIO LIVE COMMUNICATION ENFORCEMENT V0.1

## Status
Draft authority for New Generation bounded tasks.
This draft does not override canonical AGENTS or ORGANS law.

## Core binding
- Taskpack is not role authority.
- Officio owns role and communication settings.
- Each new Servitor/Codex chat must reacquire Officio role/communication ACK.

## Language split
- Owner-facing live progress commentary: Russian by default.
- Final owner-facing summary/comments: Russian.
- Technical artifacts remain English:
  - code
  - JSON keys
  - schemas
  - filenames and paths
  - commands
  - raw logs

## Violation handling
- Any English owner-facing live commentary violation must be self-corrected immediately.
- Self-correction must be recorded as `OFFICIO_LIVE_LANGUAGE_SELF_CORRECTION`.
- Sanctum NG should expose current communication compliance state as explicit gate data.

## Sanctum integration requirement
Truth state/UI should expose:
- `LIVE_LANGUAGE_COMPLIANCE`
- `FINAL_REPORT_LANGUAGE`
- `TECHNICAL_ARTIFACT_LANGUAGE`
- `AUTHORITY_SOURCE`
- `STATUS`
- `KNOWN_LIMITATION`

## Safety limit
This is a foundation enforcement layer.
It does not claim runtime hard-block automation for every shell/chat surface.
