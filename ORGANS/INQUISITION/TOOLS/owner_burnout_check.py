#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""owner_burnout_check.py — Anti-Stagnation Sentinel.

Organ-owner: Inquisitorium.
Источник истины: _CORE/OWNER_PROFILE.md (грань VI, раздел IV).

ВАЖНО: этот страж ловит СТАГНАЦИЮ и ОТКРЫТЫЕ ХВОСТЫ,
А НЕ ПЕРЕРАБОТКУ. Owner от работы не выгорает — его истощает
«болото без видимых изменений».

Каденция: 2 сессии x 4ч + 1ч перерыв, ~8ч/день, предупреждать ~каждые 4ч.

Usage:
    python3 owner_burnout_check.py --state session_state.json
    python3 owner_burnout_check.py            # демо-режим на встроенных данных

State JSON schema (все поля необязательны, есть разумные дефолты):
{
    "session_minutes": 250,            # минут в текущей сессии без перерыва
    "daily_minutes": 500,              # минут за день всего
    "minutes_since_last_warning": 245, # когда последний раз предупреждали
    "minutes_since_visible_progress": 95,  # СТАГНАЦИЯ: когда был последний видимый результат
    "open_questions": ["q1", "q2"],   # ХВОСТЫ: незакрытые вопросы
    "loop_repeats": 1                  # сколько раз подряд крутимся вокруг одного
}

Exit codes: 0 = OK, 1 = WARN, 2 = ALERT.
"""
import argparse
import json
import sys

# --- Канонические пороги (из OWNER_PROFILE.md) ---
SESSION_LIMIT_MIN = 4 * 60          # 240
BREAK_HINT_MIN = 60
DAILY_IDEAL_MIN = 8 * 60            # 480
WARN_EVERY_MIN = 4 * 60             # 240

# Стагнация — главный триггер. Без видимых изменений долго = тревога.
STAGNATION_WARN_MIN = 60            # час без видимого результата → WARN
STAGNATION_ALERT_MIN = 120          # два часа → ALERT («топчемся»)
LOOP_ALERT_REPEATS = 3              # три круга вокруг одного → ALERT
TAILS_WARN = 3                      # хвостов накопилось

DEMO_STATE = {
    "session_minutes": 250,
    "daily_minutes": 500,
    "minutes_since_last_warning": 245,
    "minutes_since_visible_progress": 95,
    "open_questions": ["EYES V2 reference board", "warp branch cleanup"],
    "loop_repeats": 1,
}


def analyze(state):
    """Возвращает (severity, messages). severity: 0 OK / 1 WARN / 2 ALERT."""
    messages = []
    severity = 0

    def bump(level):
        nonlocal severity
        severity = max(severity, level)

    spm = state.get("minutes_since_visible_progress", 0) or 0
    loops = state.get("loop_repeats", 0) or 0
    tails = len(state.get("open_questions", []) or [])
    sess = state.get("session_minutes", 0) or 0
    daily = state.get("daily_minutes", 0) or 0
    since_warn = state.get("minutes_since_last_warning", 0) or 0

    # 1) СТАГНАЦИЯ — главный сигнал
    if spm >= STAGNATION_ALERT_MIN:
        bump(2)
        messages.append(
            f"[ALERT] Стагнация: {spm} мин без видимых изменений. "
            "Мы топчемся на месте — сменить угол/разбить задачу/закрыть мелкое."
        )
    elif spm >= STAGNATION_WARN_MIN:
        bump(1)
        messages.append(
            f"[WARN] {spm} мин без видимого результата. Нужен осязаемый шаг."
        )

    # 2) Петля — кружим вокруг одного
    if loops >= LOOP_ALERT_REPEATS:
        bump(2)
        messages.append(
            f"[ALERT] {loops} круга вокруг одного — это болото. Нужен другой подход."
        )

    # 3) Хвосты — незакрытые вопросы
    if tails >= TAILS_WARN:
        bump(1)
        messages.append(
            f"[WARN] Открытых хвостов: {tails}. Закрываем без остатка: "
            + ", ".join(state.get("open_questions", []))
        )

    # 4) Каденция — мягкое напоминание (НЕ про переработку, а про ритм)
    if since_warn >= WARN_EVERY_MIN:
        bump(max(severity, 1) if severity else 1)
        messages.append(
            f"[WARN] Прошло ~{since_warn} мин с последней сверки. "
            "Пора подбить итог сессии и решить про перерыв."
        )
    if sess >= SESSION_LIMIT_MIN:
        messages.append(
            f"[INFO] Сессия {sess} мин (лимит блока {SESSION_LIMIT_MIN}). "
            f"Рекомендуется перерыв ~{BREAK_HINT_MIN} мин — но это выбор Owner-а."
        )
    if daily >= DAILY_IDEAL_MIN:
        messages.append(
            f"[INFO] За день {daily} мин (идеал {DAILY_IDEAL_MIN}). Работа — не проблема; "
            "следим только за тем, чтобы не было хвостов."
        )

    if severity == 0 and not messages:
        messages.append("[OK] Движение есть, хвостов нет. Свет Astronomican ровный.")
    return severity, messages


def main():
    parser = argparse.ArgumentParser(description="Owner anti-stagnation sentinel")
    parser.add_argument("--state", help="Путь к JSON с состоянием сессии")
    args = parser.parse_args()

    if args.state:
        with open(args.state, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = DEMO_STATE
        print("(демо-режим: встроенные данные)\n")

    severity, messages = analyze(state)
    for m in messages:
        print(m)
    sys.exit(severity)


if __name__ == "__main__":
    main()
