# Command Shortcuts Catalog V0.1

## Purpose
Short operator-safe command list for known contours. These commands do not expose private keys and do not modify SSH config.

## VM2
- `ssh imperium-vm2`
- `ssh -p 2223 vboxuser2@127.0.0.1`
- `cd /home/vboxuser2/IMPERIUM_WORK/Imperium- && git status --short`
- `cd /home/vboxuser2/IMPERIUM_WORK/Imperium- && git rev-parse HEAD`

## VM3 (registered offline in this scope)
- `ssh imperium-vm3`
- `ssh <vm3-route-if-owner-provided> vboxuser3@<host>`

## VM2 <-> VM3 bounded route proof aliases
- `ssh -o BatchMode=yes imperium-vm3-from-vm2 'echo VM2_TO_VM3_AUTH_OK; hostname; whoami; pwd'`
- `ssh imperium-vm3-from-vm2 \"ssh -o BatchMode=yes imperium-vm2-from-vm3 'echo VM3_TO_VM2_AUTH_OK; hostname; whoami; pwd'\"`
- `scp <local_probe_zip> imperium-vm3-from-vm2:/home/vboxuser3/IMPERIUM_WORK/Imperium-/INBOX/VM2_TO_VM3_PROBES/<TASK_ID>/`
- `ssh imperium-vm3-from-vm2 \"scp <remote_probe_zip> imperium-vm2-from-vm3:/home/vboxuser2/IMPERIUM_WORK/Imperium-/INBOX/VM3_TO_VM2_PROBES/<TASK_ID>/\"`

## PC local
- `cd /d E:\\IMPERIUM && git status --short`
- `cd /d E:\\IMPERIUM && git rev-parse HEAD`

## Guardrails
- Do not store key bodies in scripts/logs.
- Do not run destructive commands in shortcuts.
- Do not claim offline contours are live without explicit proof.
