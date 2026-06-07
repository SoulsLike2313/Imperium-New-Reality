#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMPLE 3 / 3  —  ADMINISTRATUM BUNDLE-REPORT GATE

В конце работы Администратум собирает BUNDLE REPORT из летописей органов.
Если бандл НЕДОСТАТОЧЕН по форме (не заполнены обязательные строки,
нет доказательств нужного уровня) — Сервитор НЕ ОТПУСКАЕТСЯ.
Ему возвращается список ИМЕННО тех строк, которые надо дозаполнить.

Это аналог строгого structured-output гейта: без валидной формы — нет выпуска.

Stdlib only.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


# Обязательная форма бандл-репорта («строки», которые обязан заполнить Сервитор)
REQUIRED_FIELDS: Dict[str, str] = {
    "task_id":        "идентификатор задачи",
    "goal":           "цель задачи",
    "result_summary": "что именно сделано",
    "artifacts":      "список выходных артефактов",
    "evidence_level": "уровень доказательств E1..E6",
    "metrics":        "измеримые метрики",
    "tokens_used":    "потрачено токенов",
    "cost_usd":       "стоимость",
}
MIN_EVIDENCE = "E3"  # ниже этого — не выпускаем
EVIDENCE_ORDER = ["E1", "E2", "E3", "E4", "E5", "E6"]


@dataclass
class GateDecision:
    released: bool
    verdict: str                      # RELEASED | HELD
    missing_lines: List[str]          # что именно дозаполнить
    reasons: List[str]
    bundle: Dict[str, Any]

    def to_dict(self):
        d = self.__dict__.copy()
        return d


class Administratum:
    """Сборщик бандл-репорта и строгий гейт выпуска."""

    def __init__(self, required=None, min_evidence=MIN_EVIDENCE):
        self.required = required or REQUIRED_FIELDS
        self.min_evidence = min_evidence

    def build_bundle(self, task_id: str, goal: str,
                     organ_chronicles: Dict[str, List[dict]]) -> Dict[str, Any]:
        """Собирает бандл из летописей органов по этой задаче."""
        entries = []
        for organ, chron in organ_chronicles.items():
            for e in chron:
                if e.get("task_id") == task_id:
                    entries.append(e)
        artifacts, tokens, cost = [], 0, 0.0
        best_ev = "E1"
        metrics = {}
        for e in entries:
            artifacts += e.get("artifacts", [])
            tokens += e.get("tokens_used", 0)
            cost += e.get("cost_usd", 0.0)
            metrics.update(e.get("metrics", {}))
            ev = e.get("evidence_level", "E1")
            if EVIDENCE_ORDER.index(ev) > EVIDENCE_ORDER.index(best_ev):
                best_ev = ev
        return {
            "task_id": task_id,
            "goal": goal,
            "result_summary": "" if not entries else f"органов: {len(organ_chronicles)}, записей: {len(entries)}",
            "artifacts": artifacts,
            "evidence_level": best_ev,
            "metrics": metrics,
            "tokens_used": tokens,
            "cost_usd": round(cost, 8),
        }

    def review(self, bundle: Dict[str, Any]) -> GateDecision:
        missing, reasons = [], []
        # 1) обязательные строки заполнены?
        for field_name, desc in self.required.items():
            val = bundle.get(field_name, None)
            empty = val in (None, "", [], {}, 0) and field_name not in ("tokens_used", "cost_usd")
            if field_name not in bundle:
                missing.append(f"{field_name} ({desc})")
                reasons.append(f"отсутствует поле '{field_name}'")
            elif empty:
                missing.append(f"{field_name} ({desc})")
                reasons.append(f"пустое поле '{field_name}'")
        # 2) уровень доказательств достаточен?
        ev = bundle.get("evidence_level", "E1")
        if ev in EVIDENCE_ORDER and EVIDENCE_ORDER.index(ev) < EVIDENCE_ORDER.index(self.min_evidence):
            reasons.append(f"уровень доказательств {ev} < минимума {self.min_evidence}")
            missing.append(f"evidence_level (поднять до {self.min_evidence}: реальный прогон/реплей)")
        # 3) артефакты при успехе?
        if not bundle.get("artifacts"):
            reasons.append("нет артефактов выполнения")
            missing.append("artifacts (хотя бы один выходной артефакт)")

        released = not missing
        return GateDecision(
            released=released,
            verdict="RELEASED" if released else "HELD",
            missing_lines=missing,
            reasons=reasons,
            bundle=bundle,
        )

    def release_or_hold(self, task_id, goal, organ_chronicles) -> GateDecision:
        bundle = self.build_bundle(task_id, goal, organ_chronicles)
        return self.review(bundle)


if __name__ == "__main__":
    # СЦЕНАРИЙ A: неполный бандл → HELD (Сервитор не отпущен)
    bad = {
        "ASTRONOMICON": [{"task_id": "T-9", "artifacts": [], "tokens_used": 100,
                          "cost_usd": 0.0001, "evidence_level": "E2",
                          "metrics": {"confidence": 0.5}}],
    }
    adm = Administratum()
    dec = adm.release_or_hold("T-9", "собрать карту маршрутов", bad)
    print("SCENARIO A:", dec.verdict)
    print(json.dumps(dec.to_dict(), ensure_ascii=False, indent=2))

    # СЦЕНАРИЙ B: полный бандл → RELEASED
    good = {
        "ASTRONOMICON": [{"task_id": "T-9",
                          "artifacts": ["artifact://T-9/routes.json"],
                          "tokens_used": 1200, "cost_usd": 0.0012,
                          "evidence_level": "E3",
                          "metrics": {"confidence": 0.9, "routes": 12}}],
    }
    dec2 = adm.release_or_hold("T-9", "собрать карту маршрутов", good)
    # result_summary заполним (в реальности — Сервитор дозаполняет по missing_lines)
    dec2.bundle["result_summary"] = "Построены 12 маршрутов"
    dec2 = adm.review(dec2.bundle)
    print("SCENARIO B:", dec2.verdict)
    print(json.dumps(dec2.to_dict(), ensure_ascii=False, indent=2))
