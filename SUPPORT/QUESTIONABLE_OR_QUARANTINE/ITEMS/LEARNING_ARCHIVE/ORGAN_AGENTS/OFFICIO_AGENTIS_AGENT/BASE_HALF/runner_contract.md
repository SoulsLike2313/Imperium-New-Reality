# Runner Contract

The runner is the only supported command entrypoint for V0.1.

## Required Commands

- `status`
- `role-get --agent <SERVITOR|LOGOS_PRIME|LOGOS_SPECULUM>`
- `settings-get --agent <...> --mode <EXECUTOR|AUDITOR|ARCHITECT|REPAIRER>`
- `requirements-compile --task-pack <path>`
- `pack-build-role --agent <...>`
- `compliance-check --matrix <path> [--evidence <path>]`
- `check-all`

## Receipt Rule

Every command must emit a structured receipt path.

