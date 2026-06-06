# Shell Contract

- CLI is non-interactive and deterministic.
- Every file output path must be printed.
- Non-zero exit on blocked state.
- Human summary plus JSON evidence path in stdout.

Forbidden:

- hidden side-effects in repo root
- writing runtime noise into tracked folders
- PASS claims without emitted artifacts

