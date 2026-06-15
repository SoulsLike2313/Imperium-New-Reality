# Post Patch Research Register v0.9.5 — Evidence Vault Pack Execution

## Что регистрируем через Mechanicus

- Execution tool как write-capable Evidence Vault tool.
- Owner token contract.
- Receipt/provenance surface для будущей проверки.
- Pack folder layout как стабильный storage contract.

## Внешние архитектурные ориентиры

- OCI Image Layout: content-addressed blobs, references/indexes and portable filesystem/archive layouts.
- SLSA provenance: artifact integrity and provenance claims for produced artifacts.
- in-toto attestation: verifiable claims about how an artifact was produced.

## Doctrine update

Execution is not cleanup. Copy/pack/seal is allowed only with owner token; source deletion remains a separate future gate.
