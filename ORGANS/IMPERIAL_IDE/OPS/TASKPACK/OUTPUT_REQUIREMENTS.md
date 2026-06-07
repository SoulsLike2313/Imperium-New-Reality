# OUTPUT_REQUIREMENTS

Финальный отчёт владельцу ОБЯЗАН содержать строки:

1. task_id
2. result_summary
3. artifacts
4. evidence_level (минимум E3)
5. metrics
6. tokens_used
7. cost_usd

Дополнительно:
- receipts (список выпущенных ресивов)
- next_task_recommendation
- доказательства выполнения: command / exit_code / output_digest

Правила:
- Нет PASS без receipts.
- UTF-8 без BOM, валидный JSON.
- evidence_level ниже E3 => отчёт HELD.
