#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMPLE 1 / 3  —  AI-SCRIPT-FIRST METAOS ORCHESTRATOR (adaptive + polymorphic)

Идея: ядро/IDE оркестрирует ресурсы ДЕТЕРМИНИРОВАННЫМ кодом. LLM (Сервитор)
вызывается только там, где без него нельзя. Это «script-first»: постоянный
ручной труд уходит в органы (код), а Сервитор исполняет ровно задачу.

Как снижаем аппетит системы (по материалам из интернета, см. DOCS):
  * ROUTING + CASCADE: сначала самый дешёвый уровень, эскалация только при низкой
    уверенности. Платим за дорогой модель только когда дешёвая не справилась.
  * TOKEN BUDGET: жёсткий потолок токенов на задачу; превышение — отказ, а не тихий перерасход.
  * PROMPT-CACHE: стабильный префикс (системный промпт/контракт) кэшируется → до -90% цены.
  * STRUCTURED OUTPUT: схема-валидация вместо болтовни; меньше токенов, больше точность.
  * NO EXTRA READS: Сервитор видит только отобранный контекст, не весь репозиторий.

Адаптивность: пороги и уровни меняются по сложности задачи.
Полиморфность: любой backend (локальный, дешёвый, frontier) подключается через
один интерфейс ModelTier.run() — оркестратор не знает, кто там внутри.

Stdlib only. Реальные LLM заменены детерминированными заглушками для демо.
"""
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

BACKEND_MODE = "DETERMINISTIC_STUB_ONLY"
LIVE_LLM_BACKEND_ENABLED = False


# ----------------------------------------------------------------------
# Токен-учёт (грубая оценка ~4 символа/токен; в бою — реальный tokenizer)
# ----------------------------------------------------------------------
def est_tokens(text: str) -> int:
    return max(1, len(text) // 4)


@dataclass
class ModelTier:
    """Полиморфный адаптер любого backend. Цены — условные $/1M токенов."""
    name: str
    price_in: float
    price_out: float
    cache_read_factor: float  # множитель цены для кэш-попадания (напр. 0.1)
    runner: Callable[[str, str], Dict[str, Any]]  # (system, user) -> {answer, confidence}

    def run(self, system: str, user: str, cached_prefix_tokens: int = 0):
        out = self.runner(system, user)
        in_tok = est_tokens(system) + est_tokens(user)
        out_tok = est_tokens(out.get("answer", ""))
        # кэшированный префикс оплачивается дешевле
        billable_in = max(0, in_tok - cached_prefix_tokens)
        cost = (billable_in * self.price_in
                + cached_prefix_tokens * self.price_in * self.cache_read_factor
                + out_tok * self.price_out) / 1_000_000
        return {
            "tier": self.name,
            "answer": out.get("answer", ""),
            "confidence": float(out.get("confidence", 0.0)),
            "in_tokens": in_tok,
            "out_tokens": out_tok,
            "cached_prefix_tokens": cached_prefix_tokens,
            "cost_usd": round(cost, 8),
        }


@dataclass
class TaskContract:
    """Контракт задачи: Сервитор видит ТОЛЬКО это, ничего лишнего."""
    task_id: str
    goal: str
    allowed_context: List[str]      # только отобранные фрагменты, не весь репо
    output_schema: Dict[str, str]   # схема результата (поле -> тип)
    token_budget: int = 4000        # жёсткий потолок
    complexity: str = "auto"        # auto|low|high — управляет адаптивностью


class MetaOSOrchestrator:
    """Детерминированное ядро: решает кодом, LLM исполняет точечно."""

    def __init__(self, tiers: List[ModelTier], confidence_threshold: float = 0.75,
                 chronicle: Optional[Callable[[str, dict], None]] = None):
        # tiers упорядочены от дешёвого к дорогому
        self.tiers = tiers
        self.confidence_threshold = confidence_threshold
        self.chronicle = chronicle or (lambda ev, data: None)

    # --- детерминированный роутер: оценка сложности без LLM ---
    def _route_start_index(self, contract: TaskContract) -> int:
        if contract.complexity == "low":
            return 0
        if contract.complexity == "high":
            return min(1, len(self.tiers) - 1)
        # auto: дешёвая эвристика по длине/ключевым словам
        text = contract.goal + " ".join(contract.allowed_context)
        hard = any(w in text.lower() for w in
                   ("докажи", "архитектур", "рефактор", "рассужд", "prove", "design"))
        return 1 if (hard and len(self.tiers) > 1) else 0

    # --- сборка минимального промпта (no extra reads) ---
    def _build_prompt(self, contract: TaskContract):
        system = (
            "Ты Сервитор Империума. Исполни РОВНО задачу. Не читай лишнего, "
            "не рассуждай вслух, ответ СТРОГО по схеме JSON. "
            "Это стабильный префикс — он кэшируется."
        )
        user = json.dumps({
            "goal": contract.goal,
            "context": contract.allowed_context,
            "schema": contract.output_schema,
        }, ensure_ascii=False)
        return system, user

    def _valid_schema(self, answer: str, schema: Dict[str, str]):
        try:
            obj = json.loads(answer)
        except Exception:
            return False, None
        for k in schema:
            if k not in obj:
                return False, None
        return True, obj

    def run_task(self, contract: TaskContract) -> Dict[str, Any]:
        system, user = self._build_prompt(contract)
        prefix_tokens = est_tokens(system)  # кэшируемый системный префикс
        spent = 0
        attempts = []
        start = self._route_start_index(contract)
        self.chronicle("task_start", {"task_id": contract.task_id,
                                      "start_tier": self.tiers[start].name})

        for idx in range(start, len(self.tiers)):
            tier = self.tiers[idx]
            # кэш работает со второго вызова того же префикса
            cached = prefix_tokens if attempts else 0
            res = tier.run(system, user, cached_prefix_tokens=cached)
            spent += res["in_tokens"] + res["out_tokens"]
            ok, obj = self._valid_schema(res["answer"], contract.output_schema)
            res["schema_ok"] = ok
            attempts.append(res)
            self.chronicle("tier_attempt", {"task_id": contract.task_id, **res})

            # бюджет: жёсткий отказ, а не тихий перерасход
            if spent > contract.token_budget:
                self.chronicle("budget_exceeded",
                               {"task_id": contract.task_id, "spent": spent})
                return self._result(contract, attempts, "BUDGET_EXCEEDED", obj if ok else None)

            # успех: схема ок + уверенность выше порога → НЕ эскалируем
            if ok and res["confidence"] >= self.confidence_threshold:
                return self._result(contract, attempts, "OK", obj)
            # иначе — эскалация на следующий (дороже) уровень

        # все уровни исчерпаны
        last_ok, last_obj = self._valid_schema(attempts[-1]["answer"],
                                               contract.output_schema)
        return self._result(contract, attempts,
                            "OK" if last_ok else "LOW_CONFIDENCE",
                            last_obj if last_ok else None)

    def _result(self, contract, attempts, status, obj):
        total_cost = round(sum(a["cost_usd"] for a in attempts), 8)
        total_tokens = sum(a["in_tokens"] + a["out_tokens"] for a in attempts)
        out = {
            "task_id": contract.task_id,
            "status": status,
            "result": obj,
            "tiers_used": [a["tier"] for a in attempts],
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "attempts": attempts,
            "backend_mode": BACKEND_MODE,
            "live_llm_backend_enabled": LIVE_LLM_BACKEND_ENABLED,
            "cost_measurement_mode": "CANDIDATE_ESTIMATE_NOT_LIVE_BILLING",
        }
        self.chronicle("task_end", {"task_id": contract.task_id,
                                    "status": status, "cost": total_cost,
                                    "tokens": total_tokens})
        return out


# ----------------------------------------------------------------------
# Демо-заглушки моделей (в бою — реальные API)
# ----------------------------------------------------------------------
def _cheap_runner(system, user):
    data = json.loads(user)
    goal = data["goal"].lower()
    # дешёвая модель хороша на простом, не уверена на сложном
    if any(w in goal for w in ("докажи", "архитектур", "design", "prove")):
        return {"answer": json.dumps({"value": "не уверен"}, ensure_ascii=False),
                "confidence": 0.4}
    return {"answer": json.dumps({"value": "42"}, ensure_ascii=False),
            "confidence": 0.95}


def _frontier_runner(system, user):
    return {"answer": json.dumps({"value": "подробный ответ"}, ensure_ascii=False),
            "confidence": 0.92}


def default_tiers():
    return [
        ModelTier("servitor-nano", price_in=0.10, price_out=0.40,
                  cache_read_factor=0.1, runner=_cheap_runner),
        ModelTier("servitor-frontier", price_in=3.00, price_out=15.00,
                  cache_read_factor=0.1, runner=_frontier_runner),
    ]


if __name__ == "__main__":
    orch = MetaOSOrchestrator(default_tiers(),
                              chronicle=lambda ev, d: print("[chron]", ev, d))
    easy = TaskContract("T-1", "сколько будет 6*7?", ["арифметика"],
                        {"value": "string"})
    hard = TaskContract("T-2", "докажи корректность архитектуры", ["модуль X"],
                        {"value": "string"})
    print(json.dumps(orch.run_task(easy), ensure_ascii=False, indent=2))
    print(json.dumps(orch.run_task(hard), ensure_ascii=False, indent=2))
