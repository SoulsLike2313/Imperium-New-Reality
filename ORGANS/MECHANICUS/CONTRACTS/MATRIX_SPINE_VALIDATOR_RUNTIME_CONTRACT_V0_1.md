# Matrix Spine Validator Runtime Contract V0.1

Owner organ: `Mechanicus`
Support organs: `Inquisition`, `Administratum`, `Officio Agentis`
Status: `CANDIDATE_RUNTIME_READY`

## Runtime promise
When replayed through the provided runner scripts, the validator must:
1. scan Matrix Spine and organ matrix JSON files;
2. enforce metadata/status/owner checks;
3. verify required READ_FIRST packet and schema/template presence;
4. execute manifest-driven negative fixtures and prove expected failures are detected;
5. produce compact machine and human receipts;
6. support a synthetic `start task` corridor proof (entry ACK -> validation -> capability split -> red-team -> closure);
7. enforce typed corridor terms (`synthetic_corridor`, `real_runtime_corridor`, `warp_corridor`) and deny untyped `runtime corridor` claim;
8. enforce head consistency fields (`base/implementation/proof/closure_bundle/remote`) and independent replay gate;
9. block clean PASS without independent replay;
10. require claim ledger for closure and enforce excluded runtime-output hash/policy metadata.

## Replay commands
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
- `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.sh`
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_efficiency_delta.sh`

## Required outputs
- `matrix_spine_validation_receipt.json`
- `matrix_spine_validation_report.md`
- `matrix_spine_validation_failures.jsonl`
- `matrix_spine_validation_summary.json`
- `synthetic_corridor_receipt.json`
- `synthetic_runtime_corridor_report.md`
- `efficiency_delta_receipt.json`
- `final_closure_verifier_receipt.json`
- `NEXT_PIPELINE_HANDOFF.json`

## Boundaries
- This validator does not grant canon admission.
- Synthetic corridor proof does not grant real WARP runtime admission.
- PASS claims must still pass Inquisition red-team gate and efficiency delta evidence.
- Efficiency score must consume red-team caps, independent replay caps, and synthetic delta cap before verdict.
