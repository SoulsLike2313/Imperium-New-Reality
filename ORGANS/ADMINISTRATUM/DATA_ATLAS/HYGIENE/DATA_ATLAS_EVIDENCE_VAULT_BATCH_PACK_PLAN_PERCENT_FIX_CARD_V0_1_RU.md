# Data Atlas — Evidence Vault Batch Pack Plan Percent Fix v0.1

Исправляет owner-facing метрику `Repo share` в смотровой Evidence Vault Batch 001 Pack Plan.

До FIX1 реальный v0.9.2 preview отдавал общее число файлов как `classification_files_total`, а v0.9.3 planner искал только `repo_files_total/files_total`. При fallback-denominator=1 смотровая показывала `200400.0%` вместо примерно `22.4%`.

FIX1 закрепляет правило: owner-facing percentages должны иметь явный denominator, а machine proof должен хранить ratio и percent отдельно.
