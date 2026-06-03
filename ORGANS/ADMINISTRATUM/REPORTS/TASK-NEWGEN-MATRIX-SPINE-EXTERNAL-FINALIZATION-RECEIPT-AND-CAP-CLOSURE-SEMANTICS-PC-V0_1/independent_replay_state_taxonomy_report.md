# Independent Replay State Taxonomy Report

Task: $taskId

## Delivered

- New Mechanicus matrix: INDEPENDENT_REPLAY_STATE_TAXONOMY_MATRIX.
- New Mechanicus contract: INDEPENDENT_REPLAY_STATE_TAXONOMY_CONTRACT.md.
- New schema: independent_replay_state_schema.json.

## Replay states

- NONE
- PRIOR_REPLAY_EXISTS
- SEPARATE_REPLAY_RUNNER_FOR_TARGET
- INQUISITOR_REPLAY_FOR_TARGET
- SPECULUM_REPLAY_FOR_TARGET
- EXTERNAL_REPLAY_ACCEPTED
- STALE_REPLAY_ONLY

## Surviving-cap clarity

- Older-target replay must be represented as STALE_REPLAY_ONLY/PRIOR_REPLAY_EXISTS.
- Current-target replay states require exact target/replay head match.
- Mismatch triggers CAP_STALE_REPLAY_USED_AS_CURRENT.
