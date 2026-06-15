# SSH Alias Policy V0.1

## Naming Convention
- Alias format: `imperium-<contour>[-purpose]`.
- Reserved aliases in this foundation:
  - `imperium-vm2`
  - `imperium-vm3`
  - `imperium-throne-core`
  - `imperium-pc-local`

## Mandatory Rules
- Alias registry in repo is documentation truth, not proof of installation.
- Any alias marked offline must not be represented as live.
- Host/user/port info can be stored.
- Private key material cannot be stored.
- Key paths are local references only (example: `%USERPROFILE%\\.ssh\\imperium_pc_to_vm2_ed25519_20260418`).

## Safety Clauses
- `~/.ssh/config` is out of scope for this task.
- No automation in this slice writes or mutates user SSH configuration.
- Any future auto-config helper must require Owner gate and explicit rollback contract.
