# Administratum Candidate Bundle Gate

This adapter evaluates WARP and MetaOS evidence bundles. Incomplete or weak
evidence returns `HELD`; complete evidence at or above the configured threshold
returns `RELEASED` for a release manifest only.

`RELEASED` never means automatic kernel promotion. A future owner-approved gate
must consume the manifest.
