# INDEPENDENT_REPLAY_STATE_TAXONOMY_MATRIX

Status: `CANDIDATE_NOT_CANON`
Owner organ: `Mechanicus`
Support organs: Inquisition, Administratum

## Purpose

Defines explicit replay state taxonomy to prevent vague "replay exists" claims.

## Replay states

- `NONE`
- `PRIOR_REPLAY_EXISTS`
- `SEPARATE_REPLAY_RUNNER_FOR_TARGET`
- `INQUISITOR_REPLAY_FOR_TARGET`
- `SPECULUM_REPLAY_FOR_TARGET`
- `EXTERNAL_REPLAY_ACCEPTED`
- `STALE_REPLAY_ONLY`

## PASS criteria

- State reflects target-vs-replay head truth.
- Current-target replay states require `replay_head == target_head`.
- `STALE_REPLAY_ONLY` is used when replay exists but not for current target.

## WARN criteria

- Replay exists but only for older target.
- Replay is pending for strict certifier loop.

## BLOCK criteria

- State claims current-target replay while heads mismatch.
- State `NONE` while replay evidence fields are populated.

## Fake-green flags

- `REPLAY_STATE_AMBIGUOUS`
- `STALE_REPLAY_USED_AS_CURRENT`
- `REPLAY_CLAIM_WITHOUT_RECEIPT`

## Evidence requirements

- replay state receipt
- replay receipt path
- checker output
