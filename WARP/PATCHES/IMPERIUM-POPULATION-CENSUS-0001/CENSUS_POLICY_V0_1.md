# CENSUS POLICY V0.1

The Imperium population census is a measurement layer, not a cleaning layer.

The census must not delete, move, rewrite, quarantine, or auto-fix files. It only observes, classifies, hashes, counts, and reports.

## Scan scope

The first census scans the repository working tree, excluding `.git/`, common runtime caches, and generated output files of this census pack to avoid recursive self-reference.

Unknown is not failure. Unknown is measurement.

## Required gap map

The first gap map must surface unknown roots, unknown owners, unknown classes, schemas without obvious validators, validators without obvious receipts, receipts without obvious reports, WARP packs, organs without basic passport files, and decode warnings.
