#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRATED SMOKE — весь конвейер MetaOS в одном прогоне:

  ROUTING/CASCADE (ядро решает кодом)
    -> SERVITOR исполняет только задачу на отобранном контексте
      -> ОРГАНЫ пишут ЛЕТОПИСЬ
        -> АДМИНИСТРАТУМ собирает BUNDLE и РЕШАЕТ: RELEASED | HELD

Доказывает два исхода:
  SCENARIO 1: неполный отчёт → Сервитор НЕ ОТПУЩЕН (HELD), выданы missing_lines
  SCENARIO 2: Сервитор дозаполняет строки → RELEASED

exit=0 только если оба сценария отработали как ожидается.
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ENGINE"))

from metaos_orchestrator import MetaOSOrchestrator, TaskContract, default_tiers  # noqa
from servitor_runtime import Organ, Servitor  # noqa
from administratum_bundle_gate import Administratum  # noqa


def main():
    failures = []

    # --- 1. ЯДРО РОУТИТ (детерминированно) ---
    orch = MetaOSOrchestrator(default_tiers())
    easy = orch.run_task(TaskContract("T-1", "сколько 6*7?", ["арифметика"],
                                      {"value": "string"}))
    hard = orch.run_task(TaskContract("T-2", "докажи архитектуру", ["модуль X"],
                                      {"value": "string"}))
    print("[route] easy tiers:", easy["tiers_used"], "cost:", easy["total_cost_usd"])
    print("[route] hard tiers:", hard["tiers_used"], "cost:", hard["total_cost_usd"])
    # простая задача НЕ должна эскалировать на дорогой уровень
    if easy["tiers_used"] != ["servitor-nano"]:
        failures.append("easy task escalated (should stay on nano)")
    if "servitor-frontier" not in hard["tiers_used"]:
        failures.append("hard task did not escalate to frontier")
    if hard["total_cost_usd"] <= easy["total_cost_usd"]:
        failures.append("hard task not more expensive than easy")

    # --- 2. SERVITOR исполняет, ОРГАН пишет ЛЕТОПИСЬ ---
    repo = {
        "KERNEL/core.py": "def boot(): pass",
        "ORGANS/ASTRONOMICON/routes.py": "# маршруты и карта",
        "DOCS/noise.md": "шум " * 80,
    }
    astro = Organ("ASTRONOMICON")
    serv = Servitor()
    win = astro.select_context(repo, "собрать карту маршрутов")
    rep = serv.execute(astro, "T-9", "собрать карту маршрутов",
                       {"value": "string"}, win)
    print("[servitor] status:", rep.status, "evidence:", rep.evidence_level)
    if not astro.chronicle:
        failures.append("organ chronicle empty")

    # --- 3. ADMINISTRATUM GATE ---
    adm = Administratum()

    # SCENARIO 1: пустая летопись (отчёт неполный) → HELD
    empty_organ = {"ASTRONOMICON": [{"task_id": "T-9", "artifacts": [],
                                     "tokens_used": 50, "cost_usd": 0.00005,
                                     "evidence_level": "E2", "metrics": {}}]}
    d1 = adm.release_or_hold("T-9", "собрать карту маршрутов", empty_organ)
    print("[gate] SCENARIO 1:", d1.verdict, "missing:", len(d1.missing_lines))
    if d1.released or not d1.missing_lines:
        failures.append("scenario1 should be HELD with missing lines")

    # SCENARIO 2: полный бандл (Сервитор дозаполнил) → RELEASED
    full_organ = {"ASTRONOMICON": [{"task_id": "T-9",
                                    "artifacts": ["artifact://T-9/routes.json"],
                                    "tokens_used": 1200, "cost_usd": 0.0012,
                                    "evidence_level": "E3",
                                    "metrics": {"routes": 12, "confidence": 0.9}}]}
    bundle = adm.build_bundle("T-9", "собрать карту маршрутов", full_organ)
    bundle["result_summary"] = "Построены 12 маршрутов"  # дозаполненная строка
    d2 = adm.review(bundle)
    print("[gate] SCENARIO 2:", d2.verdict, "missing:", len(d2.missing_lines))
    if not d2.released:
        failures.append(f"scenario2 should be RELEASED, missing={d2.missing_lines}")

    print("-" * 50)
    if failures:
        print("SMOKE RESULT: FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print("SMOKE RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
