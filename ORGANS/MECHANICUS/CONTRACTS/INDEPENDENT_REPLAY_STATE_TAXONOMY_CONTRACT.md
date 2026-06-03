# Independent Replay State Taxonomy Contract

Status: `CANDIDATE_V0_1`
Owner organ: `Mechanicus`

## Rule

Independent replay claims must use explicit states, not vague wording.

## Required states

- `NONE`
- `PRIOR_REPLAY_EXISTS`
- `SEPARATE_REPLAY_RUNNER_FOR_TARGET`
- `INQUISITOR_REPLAY_FOR_TARGET`
- `SPECULUM_REPLAY_FOR_TARGET`
- `EXTERNAL_REPLAY_ACCEPTED`
- `STALE_REPLAY_ONLY`

## Consistency checks

- If state is current-target replay (`SEPARATE_*`, `INQUISITOR_*`, `SPECULUM_*`, `EXTERNAL_*`), then `replay_head` must equal `target_head`.
- If replay exists but for older target, use `STALE_REPLAY_ONLY` or `PRIOR_REPLAY_EXISTS`, never current-target states.
- If state is `NONE`, replay evidence fields must be empty.

## Cap interaction

- Mismatch triggers `CAP_STALE_REPLAY_USED_AS_CURRENT`.
- Ambiguous state triggers `CAP_REPLAY_STATE_AMBIGUOUS`.
