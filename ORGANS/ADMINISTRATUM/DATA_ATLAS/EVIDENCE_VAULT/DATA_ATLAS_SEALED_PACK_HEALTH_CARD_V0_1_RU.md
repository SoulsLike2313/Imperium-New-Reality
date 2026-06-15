# Data Atlas / Sealed Pack Health Card V0.1

Patch: `v0.8.9.2`

Цель: Data Atlas должен показывать sealed evidence pack как одну проверяемую сущность, а не как набор случайных файлов.

## Поля карточки

- `patch_id`
- `evidence_pack_id`
- `pack_path`
- `manifest_path`
- `machine_index_path`
- `owner_summary_path`
- `sha256sums_path`
- `raw_buffer_deleted`
- `sealer_report_root`
- `report_location_safe`
- `health_status`

## Health states

- `PASS_SEALED_PACK_HEALTH` — pack и sidecar-файлы существуют, SHA256 совпадает, raw buffer закрыт по manifest.
- `PASS_WITH_BUFFER_RETAINED` — pack валиден, но raw buffer оставлен намеренно.
- `FAIL_SEALED_PACK_HEALTH` — отсутствует sidecar или hash не совпадает.

## Coupling

- Mechanicus пишет canonical sidecars.
- Inquisition проверяет output-root contract и sealed pack health.
- Data Atlas показывает owner-readable карточку состояния.

Правило: если Data Atlas не может показать health sealed pack без распаковки ZIP, evidence storage ещё недостаточно архитектурен.
