# Final Report — TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1

## Verdict

`WARN_PARTIAL_ROUTE_PROOF_WITH_VM2_TO_VM3_BLOCKED`

## Claim boundary

- `PASS_FOR_PC_TO_VM2_WITH_WARN_PARTIAL_PC_TO_VM3_AND_BLOCKED_VM2_TO_VM3_ROUTE_ONLY`
- No production orchestration claim.
- No global all-routes-live claim.

## Proved

- route: `PC_TO_VM2`
- status: `PROVED`
- evidence refs:
  - `INBOX/VM2_TASKPACKS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/PC_TO_VM2_DELIVERY_EVIDENCE.json`
  - `INBOX/VM2_TASKPACKS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/TASKPACK_TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1.zip`
- validator/smoke refs:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/transfer_route_proof_validator_report.json`
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/transfer_route_proof_smoke_report.json`

## Recovered / partial

- route: `PC_TO_VM3`
- status: `WARN_PARTIAL`
- reason: VM3 salvage reports confirm bounded proof history, but referenced raw request/result and VM3 inbox paths are not fully available on VM2.
- evidence refs:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-PC-TO-VM3-VM3-V0_1/transfer_route_proof_action_report.json`
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-PC-TO-VM3-VM3-V0_1/transfer_route_proof_validator_report.json`
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-PC-TO-VM3-VM3-V0_1/vm3_interrupted_handoff.json`

## Blocked route

- route: `VM2_TO_VM3`
- status: `BLOCKED_ROUTE_UNAVAILABLE`
- reason: `ssh -o BatchMode=yes imperium-vm3` failed (`Could not resolve hostname imperium-vm3`).
- evidence refs:
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/ACTION_LOGS/vm2_to_vm3_ssh_g.txt`
  - `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/ACTION_LOGS/vm2_to_vm3_probe_run.json`

## Not proven

- production orchestration
- arbitrary remote execution
- global all-routes-live transfer

## Not run

- VM2->VM3 remote file copy/hash proof commands (`scp` and remote `sha256sum`) were not run because SSH alias resolution failed before bounded probe copy stage.

## Evidence

- summary: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/route_proof_recovery_summary.json`
- request records: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/action_requests/`
- result records: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/action_results/`
- runner ledger: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/ledgers/transfer_action_runner_ledger.jsonl`
- transfer ledger: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/ledger/transfer_action_ledger.jsonl`
- UI/state: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/DATA/TRANSFER_CONSOLE_VIEW_STATE.generated.json`
- validator: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/transfer_route_proof_validator_report.json`
- smoke: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/transfer_route_proof_smoke_report.json`

## Context Source Mix

- taskpack: `48%`
- repo/registries: `30%`
- organ packets/contracts: `5%`
- Owner input: `12%`
- Servitor inference: `5%`
- details file: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/context_source_mix.json`

## KPD / next-task improvement

- details file: `IMPERIUM_NEW_GENERATION/SANCTUM_NG/TRANSFER_CONSOLE/REPORTS/TASK-20260523-NEWGEN-SANCTUM-TRANSFER-ROUTE-PROOF-RECOVERY-VM2-V0_1/kpd_next_task_improvement.md`

## Closure

- final head: `RECORDED_IN_FINAL_OWNER_MESSAGE`
- remote head: `RECORDED_IN_FINAL_OWNER_MESSAGE`
- worktree clean: `RECORDED_IN_FINAL_OWNER_MESSAGE`
