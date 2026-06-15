# Post-Patch Research Register v0.9.3 — Evidence Vault Batch Pack Plan

## Что зарегистрировано

- OCI Image Layout как ориентир content-addressed layout: blobs + refs + manifests.
- SLSA provenance как ориентир для будущих execution receipts.
- in-toto attestations как ориентир для проверяемых claims о том, какие шаги были выполнены, кем и в каком порядке.

## Что берём в Imperium

- План упаковки должен отделяться от исполнения.
- Execution patch должен иметь manifest/receipt/proof.
- Source deletion не может следовать из preview/plan автоматически.
