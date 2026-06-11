# Post Patch Research Register v0.9.6

Тема: receipt verification и Data Atlas registration для Evidence Vault Batch 001.

Ориентиры:

- OCI Image Layout: pack folder должен мыслиться как layout с manifest/index/content-addressed payload.
- SLSA provenance: registration должен отвечать где, когда и как произведён artifact.
- in-toto attestations: verification report должен быть проверяемым claim о выполненном шаге.

Решение сейчас: не внедрять внешние зависимости; сохранить lightweight JSON/SQLite/HTML proof, но выравнивать лексику и поля под manifest/provenance/attestation mindset.
