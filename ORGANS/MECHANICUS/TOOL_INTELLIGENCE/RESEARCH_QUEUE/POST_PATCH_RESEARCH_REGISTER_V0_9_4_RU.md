# Post Patch Research Register — v0.9.4

Patch: Evidence Vault Batch 001 Dry-run Executor.

## Что зарегистрировать через Mechanicus

- dry-run executor как отдельный capability, не как packer;
- output contract: report + file checks + sha256 preview + staging layout preview + SQLite + visual proof;
- запрет на source mutation и Vault pack creation без execution gate.

## Архитектурные ориентиры

- OCI image layout: вдохновение для manifest/index/blobs layout и content-addressed pack мышления.
- SLSA provenance: вдохновение для описания, где, когда и как produced artifact создаётся.
- in-toto attestations/link metadata: вдохновение для проверяемых claims по шагам supply chain.

## Следующий вопрос

После dry-run PASS подготовить execution patch, который копирует/упаковывает selected candidates в Evidence Vault, но всё ещё не удаляет source.
