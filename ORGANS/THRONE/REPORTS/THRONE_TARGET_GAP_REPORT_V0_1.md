# THRONE TARGET GAP REPORT V0.1

task_id: `THRONE-TARGET-GAP-VALIDATOR-0001`  
validator_id: `throne_target_gap_validator.v0_1`  
verdict: `PASS_MEASURED`  
mode: `MEASURE_ONLY`  
validation_model: `TARGET_V1_VS_CURRENT_REALITY`  
generated_at_utc: `2026-06-29T18:03:18Z`

## Global scores

- core_readiness_score: `67.55`
- throne_readiness_score: `97.0`
- great_nine_readiness_score: `51.69`
- lowest_organ_readiness_score: `38.65`

## Organ readiness, lowest first

- `OFFICIO_AGENTIS`: `38.65` — gaps: missing README.md, missing MANIFEST.json, missing FUNCTIONS.md, no schema evidence, no validator evidence
- `SCHOLA_IMPERIALIS`: `39.58` — gaps: missing README.md, missing MANIFEST.json, missing FUNCTIONS.md, no schema evidence, no validator evidence
- `CUSTODES`: `43.44` — gaps: missing README.md, missing MANIFEST.json, missing FUNCTIONS.md, no schema evidence, no validator evidence, has quarantine residents
- `DOCTRINARIUM`: `50.52` — gaps: missing README.md, missing MANIFEST.json, missing FUNCTIONS.md, no validator evidence, has negative-example residents
- `INQUISITION`: `51.77` — gaps: missing README.md, missing MANIFEST.json, missing FUNCTIONS.md, no validator evidence, has quarantine residents, has negative-example residents
- `STRATEGIUM`: `55.31` — gaps: missing README.md, missing MANIFEST.json, missing FUNCTIONS.md, no validator evidence, has quarantine residents, has negative-example residents
- `ADMINISTRATUM`: `58.44` — gaps: missing README.md, missing MANIFEST.json, missing FUNCTIONS.md, no validator evidence, has quarantine residents, has negative-example residents
- `MECHANICUS`: `60.31` — gaps: missing MANIFEST.json, missing FUNCTIONS.md, no validator evidence, has quarantine residents, has negative-example residents
- `ASTRONOMICON`: `67.19` — gaps: missing README.md, missing MANIFEST.json, missing FUNCTIONS.md, has quarantine residents, has negative-example residents
- `THRONE`: `97.0` — gaps: has WARP-status residents, has negative-example residents

## Next attention areas

10. **Great Nine README passports** — Missing README: ASTRONOMICON, ADMINISTRATUM, DOCTRINARIUM, INQUISITION, CUSTODES, STRATEGIUM, SCHOLA_IMPERIALIS, OFFICIO_AGENTIS → `ORGAN-README-PASSPORT-STAMP-0001`
20. **Great Nine manifests** — Missing MANIFEST: ASTRONOMICON, ADMINISTRATUM, DOCTRINARIUM, MECHANICUS, INQUISITION, CUSTODES, STRATEGIUM, SCHOLA_IMPERIALIS, OFFICIO_AGENTIS → `ORGAN-MANIFEST-STAMP-0001`
40. **Custodes trust layer** — Custodes readiness is low; organ validator trust cannot be audited deeply yet. → `CUSTODES-TRUST-LAYER-0001`
50. **Schema-validator coverage** — Schema count exceeds validator count; declaration/evidence gap is visible. → `SCHEMA-VALIDATOR-COVERAGE-0001`
60. **Lowest organ readiness: OFFICIO_AGENTIS** — OFFICIO_AGENTIS readiness is 38.65%. → `OFFICIO_AGENTIS-GAP-CLOSURE-0001`

## Checks

- `PASS` — required_inputs_exist
- `PASS` — input_json_parse
- `PASS` — census_has_residents
- `PASS` — scoring_matrix_has_weights
- `PASS` — target_matrix_exists_and_mentions_target
- `PASS` — fake_green_guard_not_all_100

## Warnings

- Core readiness below target v1; this is expected and measured.

## Errors

- none

## Outputs

- `ORGANS/THRONE/RECEIPTS/throne_target_gap_receipt.json`
- `ORGANS/THRONE/REPORTS/THRONE_ORGAN_READINESS_TABLE_V0_1.csv`
- `ORGANS/THRONE/REPORTS/THRONE_NEXT_ATTENTION_AREAS_V0_1.json`

## Meaning

This report does not claim Imperium v1 is achieved.

It proves the Throne can compare a target v1 form against current Reality and produce a measured gap map.
