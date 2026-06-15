# Current Truth Root V0.1 (Foundation)

This folder contains the first bounded foundation for New Generation truth spine:

- `CURRENT_TRUTH_ROOT_V0_1.json`
- `REPORT_STATUS_INDEX_V0_1.json`
- `EVIDENCE_SOURCE_MAP_V0_1.json`

## Scope and claim boundary

This is foundation-only truth indexing for known/proved artifacts.
UNKNOWN zones stay `UNKNOWN`, `MISSING`, `PARTIAL`, or `FOUNDATION_ONLY`.

No production/autonomy/live-organ claims are made.

## Builder

Run:

```bash
python3 IMPERIUM_NEW_GENERATION/TRUTH/TOOLS/build_current_truth_root_v0_1.py \
  --repo-root /home/vboxuser3/IMPERIUM_WORK/Imperium- \
  --task-id TASK-20260522-NEWGEN-CURRENT-TRUTH-ROOT-REPORT-INDEX-VM3-V0_1
```

The builder writes:

- `IMPERIUM_NEW_GENERATION/TRUTH/CURRENT_TRUTH_ROOT_V0_1.json`
- `IMPERIUM_NEW_GENERATION/TRUTH/REPORT_STATUS_INDEX_V0_1.json`
- `IMPERIUM_NEW_GENERATION/TRUTH/EVIDENCE_SOURCE_MAP_V0_1.json`
- build report (task report bundle): `CURRENT_TRUTH_BUILD_REPORT.json`

## Validator

Run:

```bash
python3 IMPERIUM_NEW_GENERATION/TRUTH/TOOLS/validate_current_truth_root_v0_1.py \
  --repo-root /home/vboxuser3/IMPERIUM_WORK/Imperium- \
  --task-id TASK-20260522-NEWGEN-CURRENT-TRUTH-ROOT-REPORT-INDEX-VM3-V0_1
```

Validator output:

- `IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-CURRENT-TRUTH-ROOT-REPORT-INDEX-VM3-V0_1/VALIDATOR_REPORT.json`

## Status model

Allowed report/index statuses:

- `PASS`
- `PASS_WITH_WARN`
- `WARN`
- `BLOCK`
- `UNKNOWN`
- `MISSING`
- `PARTIAL`
- `FOUNDATION_ONLY`
