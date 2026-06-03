# Mechanicus Scope Packs Index RU (V0.1)

Назначение: быстрый доступ будущего Servitor/local-agent к разрешенным capability-срезам по типам задач.

| Scope ID | Файл | CANON | SANDBOX | CANDIDATE | OWNER_DECISION | FORBIDDEN |
|---|---|---:|---:|---:|---:|---:|
| code_quality_task | scope_code_quality_task_v0_1.json | 2 | 14 | 1 | 12 | 1 |
| controlled_tool_provision_task | scope_controlled_tool_provision_task_v0_1.json | 2 | 14 | 3 | 12 | 0 |
| evidence_search_task | scope_evidence_search_task_v0_1.json | 0 | 8 | 4 | 12 | 0 |
| json_schema_validation_task | scope_json_schema_validation_task_v0_1.json | 3 | 6 | 5 | 12 | 0 |
| mechanicus_tool_validation_task | scope_mechanicus_tool_validation_task_v0_1.json | 3 | 5 | 11 | 12 | 0 |
| repo_hygiene_task | scope_repo_hygiene_task_v0_1.json | 1 | 5 | 12 | 12 | 0 |
| taskpack_generation_task | scope_taskpack_generation_task_v0_1.json | 1 | 3 | 13 | 12 | 0 |
| visual_readiness_task | scope_visual_readiness_task_v0_1.json | 0 | 2 | 13 | 12 | 2 |

## Важные правила
- `visual_readiness_task` = только readiness; без запуска визуальных прототипов.
- `controlled_tool_provision_task` = только Owner-approved install lane; silent install запрещен.
- `evidence_search_task` = только bounded поиск по индексу Mechanicus, без private context.
- Во всех scope действует запрет на LLM/cloud activation без отдельного Owner gate.
