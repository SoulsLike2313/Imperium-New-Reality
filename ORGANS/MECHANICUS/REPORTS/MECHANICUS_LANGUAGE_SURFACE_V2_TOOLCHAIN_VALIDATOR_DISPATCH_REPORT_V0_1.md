# MECHANICUS LANGUAGE SURFACE V2 TOOLCHAIN VALIDATOR DISPATCH REPORT V0.1

task_id: `MECHANICUS-LANGUAGE-SURFACE-V2-TOOLCHAIN-VALIDATOR-DISPATCH-0001`  
validator_id: `mechanicus_language_surface_v2_toolchain_validator_dispatch_validator.v0_1`  
verdict: `PASS_MECHANICUS_LANGUAGE_SURFACE_V2_TOOLCHAIN_VALIDATOR_DISPATCH_READY`  
generated_at_utc: `2026-07-04T19:00:49Z`

## Meaning

Mechanicus separates raw language mass from source-runtime code and governance evidence. It also establishes first toolchain and baseline language validation dispatch.

## Source-runtime language surface preview

- `Python` — files: `375`, total: `97406`, code: `83584`
- `JSON` — files: `336`, total: `91698`, code: `91687`
- `PowerShell` — files: `49`, total: `2783`, code: `2370`
- `JavaScript` — files: `6`, total: `1730`, code: `1592`
- `CSS` — files: `4`, total: `1385`, code: `1204`
- `YAML` — files: `2`, total: `1219`, code: `960`
- `TypeScript` — files: `10`, total: `498`, code: `447`
- `Rust` — files: `5`, total: `306`, code: `281`
- `HTML` — files: `3`, total: `275`, code: `260`
- `Text` — files: `5`, total: `58`, code: `55`

## Boundary

```text
This is not a 100% clean verdict.
This is baseline measurement and validation-debt discovery.
```

## Checks

- `PASS` — surface_matrix_exists_and_has_laws
- `PASS` — toolchain_matrix_exists_and_has_laws
- `PASS` — custodes_matrix_exists_and_has_laws
- `PASS` — throne_matrix_exists_and_has_laws
- `PASS` — surface_tool_exists
- `PASS` — probe_tool_exists
- `PASS` — dispatch_tool_exists
- `PASS` — language_surface_v2_tool_runs
- `PASS` — surface_v2_splits_source_from_evidence
- `PASS` — toolchain_probe_runs
- `PASS` — language_validation_dispatch_runs
- `PASS` — dispatch_does_not_claim_100_clean

## Warnings

- Optional toolchains/builds missing or failed; recorded as debt, not 100% clean failure.
- Validation baseline contains debt; expected for first baseline.

## Errors

- none
