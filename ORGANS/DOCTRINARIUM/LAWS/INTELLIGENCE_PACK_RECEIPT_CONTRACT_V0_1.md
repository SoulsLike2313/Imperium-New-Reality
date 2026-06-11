# Doctrinarium Law — Intelligence Pack Receipt Contract v0.1

## Law

An Intelligence Pack is not fully closed by an embedded manifest alone. Final artifact digest must live outside the artifact it hashes.

## Reason

If `MANIFEST.json` inside a ZIP stores the final SHA256 of that same ZIP, the ZIP must be modified to store the hash, which changes the ZIP hash. This is a self-referential digest conflict.

## Required sidecar closure

A closed Intelligence Pack must have:

```text
<pack_id>.zip
<pack_id>.INTELLIGENCE_PACK_MANIFEST.json
<pack_id>.FINAL_SHA256SUMS.txt
<pack_id>.MACHINE_RECEIPT.json
<pack_id>.OWNER_SUMMARY_RU.md
```

## Organ responsibilities

- Mechanicus builds the ZIP and writes sidecar receipt artifacts.
- Inquisition verifies that actual ZIP SHA256 matches all sidecars.
- Data Atlas visualizes receipt health.
- Administratum uses PASS receipt packs as handoff/continuity input.

## Prohibitions

- Do not treat ZIP-only Intelligence Pack as sealed handoff.
- Do not store final ZIP SHA256 inside embedded `MANIFEST.json`.
- Do not copy raw repo dumps when a PASS receipt Intelligence Pack is available.
