# Candidate-модель капсул Сервиторов

Капсула в текущей интеграции является одноразовой dry-run моделью. Она может
показать орган, задачу, очередь и receipt, но не запускает внешнюю команду.

Безопасный smoke:

```powershell
python ORGANS/IMPERIAL_IDE/WORKBENCH/SERVITORS/servitor_capsule.py `
  --capsule CAP-ALPHA --once --task smoke
```

Ограничения текущей задачи:

- `--allow-real` всегда возвращает `BLOCKED`;
- запуск без `--once` всегда возвращает `BLOCKED`;
- persistent supervisor не запускает процессы;
- queue/result paths должны находиться только в ignored runtime;
- production и autonomous execution не заявлены.
