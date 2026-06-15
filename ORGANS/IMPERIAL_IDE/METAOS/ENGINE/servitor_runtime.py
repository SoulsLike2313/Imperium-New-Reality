#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMPLE 2 / 3  —  THIN SERVITOR RUNTIME (исполняет ТОЛЬКО задачу)

Принцип «thin agent» (Anthropic/Praetorian): токены — это ~80% разброса
качества. Чем меньше мусора в контексте — тем точнее и дешевле.

Органы живут в ядре/IDE и держат постоянный труд (правила, ретрай, отбор
контекста, валидация). Сервитор — одноразовый исполнитель:
  * видит только ContextWindow, собранный органом (не весь репо);
  * не пишет лишних рецептов/файлов — только декларированные артефакты;
  * отчитывается органам структурно (Report), органы пишут ЛЕТОПИСЬ дела.

Stdlib only.
"""
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def est_tokens(text: str) -> int:
    return max(1, len(text) // 4)


@dataclass
class ContextWindow:
    """Отобранный органом контекст. Сервитор НЕ видит ничего кроме этого."""
    pinned: List[str] = field(default_factory=list)   # кэшируемый стабильный префикс
    relevant: List[str] = field(default_factory=list) # только релевантные фрагменты
    max_tokens: int = 2000

    def materialize(self) -> str:
        body = "\n".join(self.pinned + self.relevant)
        # жёсткая обрезка по бюджету (lost-in-the-middle → режем хвост)
        while est_tokens(body) > self.max_tokens and self.relevant:
            self.relevant.pop()
            body = "\n".join(self.pinned + self.relevant)
        return body


@dataclass
class Report:
    """Структурный отчёт Сервитора органу. Только факты — никакой «воды»."""
    task_id: str
    organ: str
    status: str                 # done|partial|failed
    artifacts: List[str]        # декларированные выходы (пути/иды)
    metrics: Dict[str, Any]
    evidence_level: str         # E1..E6 (см. WARP-доктрину)
    tokens_used: int
    cost_usd: float
    notes: str = ""

    def to_dict(self):
        return self.__dict__.copy()


class Organ:
    """Орган ядра: держит постоянный труд и пишет ЛЕТОПИСЬ."""

    def __init__(self, name: str):
        self.name = name
        self.chronicle: List[Dict[str, Any]] = []  # летопись дела (append-only)

    # орган САМ отбирает контекст — Сервитор не тратит лимиты на чтение
    def select_context(self, full_repo: Dict[str, str], goal: str,
                       max_tokens: int = 2000) -> ContextWindow:
        pinned = ["# КОНТРАКТ ОРГАНА: исполни только задачу, ответ по схеме."]
        kw = set(re_words(goal))
        scored = []
        for path, text in full_repo.items():
            score = len(kw & set(re_words(path + " " + text[:400])))
            if score > 0:
                scored.append((score, path, text))
        scored.sort(reverse=True)
        relevant = [f"## {p}\n{t[:600]}" for _, p, t in scored[:3]]  # топ-3
        return ContextWindow(pinned=pinned, relevant=relevant, max_tokens=max_tokens)

    def record(self, report: Report):
        self.chronicle.append({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "organ": self.name,
            "task_id": report.task_id,
            "status": report.status,
            "evidence_level": report.evidence_level,
            "metrics": report.metrics,
            "artifacts": report.artifacts,
            "tokens_used": report.tokens_used,
            "cost_usd": report.cost_usd,
        })


def re_words(s: str) -> List[str]:
    import re
    return [w for w in re.findall(r"[\w\u0400-\u04FF]+", s.lower()) if len(w) > 2]


class Servitor:
    """Одноразовый исполнитель. Никакого состояния между задачами."""

    def __init__(self, runner=None):
        # runner(system, user) -> {answer, confidence}; дефолт — заглушка
        self.runner = runner or _demo_runner

    def execute(self, organ: Organ, task_id: str, goal: str,
                output_schema: Dict[str, str], window: ContextWindow) -> Report:
        system = "\n".join(window.pinned)
        user = json.dumps({"goal": goal,
                           "context": window.relevant,
                           "schema": output_schema}, ensure_ascii=False)
        out = self.runner(system, user)
        answer = out.get("answer", "")
        conf = float(out.get("confidence", 0.0))
        tokens = est_tokens(system) + est_tokens(user) + est_tokens(answer)

        # Сервитор НЕ плодит лишних рецептов: артефакт только если схема валидна
        ok = self._schema_ok(answer, output_schema)
        artifacts = [f"artifact://{task_id}/result.json"] if ok else []
        status = "done" if (ok and conf >= 0.7) else ("partial" if ok else "failed")
        evidence = "E3" if ok and conf >= 0.7 else "E2"

        report = Report(task_id=task_id, organ=organ.name, status=status,
                        artifacts=artifacts,
                        metrics={"confidence": conf, "schema_ok": ok},
                        evidence_level=evidence, tokens_used=tokens,
                        cost_usd=round(tokens * 1e-6, 8),
                        notes="" if ok else "schema invalid")
        organ.record(report)
        return report

    @staticmethod
    def _schema_ok(answer: str, schema: Dict[str, str]) -> bool:
        try:
            obj = json.loads(answer)
        except Exception:
            return False
        return all(k in obj for k in schema)


def _demo_runner(system, user):
    data = json.loads(user)
    return {"answer": json.dumps({"value": "готово", "goal": data["goal"]},
                                 ensure_ascii=False),
            "confidence": 0.88}


if __name__ == "__main__":
    repo = {
        "KERNEL/core.py": "def boot(): pass  # ядро",
        "ORGANS/MECHANICUS/bridge.py": "# бридж к CLI, real_execution_blocked",
        "DOCS/notes.md": "нерелевантный шум " * 50,
    }
    mechanicus = Organ("MECHANICUS")
    win = mechanicus.select_context(repo, "почини бридж к CLI в mechanicus")
    print("context tokens:", est_tokens(win.materialize()))
    serv = Servitor()
    rep = serv.execute(mechanicus, "T-7", "почини бридж к CLI",
                       {"value": "string"}, win)
    print(json.dumps(rep.to_dict(), ensure_ascii=False, indent=2))
    print("--- ЛЕТОПИСЬ ОРГАНА ---")
    print(json.dumps(mechanicus.chronicle, ensure_ascii=False, indent=2))
