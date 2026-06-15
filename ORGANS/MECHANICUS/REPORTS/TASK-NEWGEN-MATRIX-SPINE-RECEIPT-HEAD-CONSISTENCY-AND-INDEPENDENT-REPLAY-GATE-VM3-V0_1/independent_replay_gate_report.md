# Independent Replay Gate Report

- Independent replay typing enforced:
  - `INQUISITOR`
  - `SPECULUM`
  - `SEPARATE_REPLAY_RUNNER`
  - `NONE`
- Clean PASS is forbidden when replay status is `NONE`.
- Mandatory cap is enforced:
  - `CAP_NO_INDEPENDENT_REPLAY`
- Efficiency scorer consumes replay gate and keeps verdict at `PASS_WITH_WARNINGS` when replay is missing.
- Negative fixtures NF20/NF21 are detected (`true`).
