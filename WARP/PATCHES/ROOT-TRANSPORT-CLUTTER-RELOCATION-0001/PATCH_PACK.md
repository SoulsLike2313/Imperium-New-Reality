# PATCH PACK — ROOT-TRANSPORT-CLUTTER-RELOCATION-0001

status: `WARP_CANDIDATE`  
mode: `HYGIENE_RELOCATION`  
primary_organ: `MECHANICUS`  
supporting_organs: `ADMINISTRATUM`, `THRONE`

## Purpose

Relocate root-level transport clutter out of repo root while preserving provenance.

This is patch 3/6 of the hygiene/control series.

## Why

External audits confirmed that Reality root is readable but noisy.

The root currently contains many transport-only artifacts:

```text
APPLY_*.ps1
*_FILE_MANIFEST_SHA256.json
```

These are useful, but they are not conceptual root files. They should live in a canonical transport zone.

## Canonical destinations

```text
SUPPORT/TRANSPORT/APPLY_SCRIPTS/
SUPPORT/TRANSPORT/FILE_MANIFESTS/
```

## New indexes

```text
SUPPORT/TRANSPORT/ROOT_TRANSPORT_INDEX_V0_1.json
SUPPORT/TRANSPORT/ROOT_TRANSPORT_INDEX_V0_1.md
ORGANS/ADMINISTRATUM/REGISTRY/ROOT_TRANSPORT_RELOCATION_REGISTRY_V0_1.json
```

## Validator

```text
ORGANS/MECHANICUS/VALIDATORS/validate_root_transport_hygiene.py
```

It proves:

```text
root has no APPLY_*.ps1
root has no *_FILE_MANIFEST_SHA256.json
all relocated files exist
all SHA256 hashes match before/after
all relocated files are indexed
WARP/PATCHES remains present
no provenance is lost
```

## Important note

This patch may relocate its own extracted root-level files:

```text
APPLY_ROOT_TRANSPORT_CLUTTER_RELOCATION_0001.ps1
ROOT_TRANSPORT_CLUTTER_RELOCATION_0001_FILE_MANIFEST_SHA256.json
```

That is intended.

The durable patch provenance remains in:

```text
WARP/PATCHES/ROOT-TRANSPORT-CLUTTER-RELOCATION-0001/
SUPPORT/TRANSPORT/
```

## Expected verdict

```text
PASS_ROOT_TRANSPORT_HYGIENE
```
