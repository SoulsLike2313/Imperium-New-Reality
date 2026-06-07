# Финальное резюме владельцу

Задача: TASK-NEWREALITY-IMPERIAL-IDE-WORKBENCH-WARP-METAOS-INTEGRATION-PC-V0_2

## Результат

`PASS_WITH_WARNINGS` до validated push.

## Где интегрировано

- Workbench: `ORGANS/IMPERIAL_IDE/WORKBENCH/` — active surface candidate.
- WARP: `ORGANS/IMPERIAL_IDE/WARP/` — active hot zone, runtime изолирован и игнорируется Git.
- MetaOS: `ORGANS/IMPERIAL_IDE/METAOS/` — active orchestration candidate на deterministic stubs.

## Как запускать

```powershell
& .\ORGANS\IMPERIAL_IDE\run_imperial_workbench.ps1 -Surface smoke
& .\ORGANS\IMPERIAL_IDE\run_warp_zone.ps1 -Command smoke
& .\ORGANS\IMPERIAL_IDE\run_metaos_smoke.ps1
```

## Что заблокировано

Full IDE completion, real servitor execution, unrestricted tool execution, live LLM backend и WARP promotion to kernel не включены.

Push receipt будет обновлён после validated push.
