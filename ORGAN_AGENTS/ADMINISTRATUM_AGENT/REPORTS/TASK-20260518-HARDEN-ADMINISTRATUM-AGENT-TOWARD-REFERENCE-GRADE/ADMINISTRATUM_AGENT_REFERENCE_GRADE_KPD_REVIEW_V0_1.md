# KPD Review V0.1

## Positive KPD impact
- Increased action density: one runner now covers context, continuity, CU, KPD, and shell flows.
- Evidence quality improved via command receipts + output hashes + metrics.
- Operator usability improved via shell and readable panel rendering without sacrificing JSON authority.

## Cost/risk observations
- Full repository inventory in continuity/check-all can be expensive on large trees.
- Bounded max-files controls were added to keep runtime predictable.

## Waste analysis
- Initial continuity run exceeded timeout before bounded scan control existed.
- This was corrected by introducing explicit inventory scan limits and warning semantics.

## Preservation decisions
- Runtime evidence preserved under RUNS folders.
- CU persistent state was moved out of implicit runtime writes; default now uses RUNS-local evidence to protect tree purity.

## Next KPD uplift opportunities
- Add cached inventory delta mode.
- Add route quality regression fixtures and historical scoring calibration.
- Add shell profile presets for compact high-frequency operations.
