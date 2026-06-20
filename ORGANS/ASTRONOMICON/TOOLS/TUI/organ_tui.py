#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Organ-TUI v0_4 — консоль одного органа (curses или текстовый fallback).

Базовые формы (универсальны для всех 9 органов):
  паки в очереди · новый таск-пак · валидация · цикл dry/apply · последние данные · рецепты
Запуск:  python organ_tui.py MECHANICUS  [--throne-permit GRANTED] [--selftest]
Permit остаётся за Троном (по умолчанию DENIED).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imperium_tui_core as core  # noqa: E402


def _organ_panels(be, organ, permit):
    """Живые панели домашнего экрана органа."""
    gh = be.git_head()
    packs = be.list_packs(organ)
    info = ["орган:   " + organ,
            "permit:  " + permit,
            "HEAD:    " + (("%s (%s)" % (gh["sha"], gh["state"])) if gh else "(нет git)"),
            "каталог: " + (be.organ_dir(organ) or "-")]
    pk = ["%s [%s] %s" % (p["task_id"], p["change_kind"] or "-", p["title"]) for p in packs] or ["(паков нет)"]
    rec = [os.path.basename(x) for x in be.list_receipts(5)] or ["(пусто)"]
    return [("ОРГАН", info), ("ПАКИ В ОЧЕРЕДИ", pk), ("ПОСЛЕДНИЕ РЕЦЕПТЫ", rec)]


def _pack_lines(be, organ):
    packs = be.list_packs(organ)
    if not packs:
        return ["(паков для этого органа нет)"]
    return ["%-22s %-7s %-12s %s" % (p["task_id"], p["change_kind"] or "-",
                                     p["submitted_by"] or "-", p["title"]) for p in packs]


def new_pack_form(ui, be, organ):
    """Базовая форма создания таск-пака для органа (+ автовалидация)."""
    fields = [
        {"key": "task_id", "label": "Task ID", "type": "text", "default": organ[:6] + "-"},
        {"key": "title", "label": "Заголовок", "type": "text", "default": ""},
        {"key": "intent", "label": "Интент (>=8)", "type": "text", "default": ""},
        {"key": "change_kind", "label": "Тип изменения", "type": "choice", "choices": core.CHANGE_KINDS, "default": core.CHANGE_KINDS[0]},
        {"key": "submitted_by", "label": "Кем подан", "type": "choice", "choices": core.SUBMITTERS, "default": core.SUBMITTERS[0]},
    ]
    res = ui.form("Новый таск-пак :: %s" % organ, fields)
    if not res or not (res.get("task_id") or "").strip():
        return
    task_id = res["task_id"].strip()
    title = res.get("title") or task_id
    intent = res.get("intent", "")
    ck = res.get("change_kind") or "PATCH"
    sb = res.get("submitted_by") or "OWNER_MANUAL"
    d, err = be.new_task_pack(organ, task_id, title, intent, ck, sb)
    if err:
        ui.text("Новый пак", ["Ошибка: " + err])
        return
    v, reasons, _r = be.validate(d)
    lines = ["Создан: %s" % d, "",
             "Автовалидация: %s" % v] + \
            (["[%s] %s %s" % (x["gate"], x["code"], x["message"]) for x in reasons] or ["ворота чисты"])
    lines += ["", "Дальше: положи файлы в files/, заполни payload,",
              "передай сервитору (Codex/Grok) и верни на валидацию."]
    ui.text("Новый таск-пак :: %s" % organ, lines)


def _cycle_view(ui, be, sel, apply, throne_permit):
    verdict, receipt = be.run_cycle(sel["dir"], apply=apply, throne_permit=throne_permit)
    lines = ["CYCLE_VERDICT: %s" % verdict, "permit=%s  apply=%s" % (throne_permit, apply), ""]
    for st in receipt.get("stages", []):
        lines.append("[%-10s] %-8s %s" % (st["stage"], st["status"], st.get("detail") or ""))
    if receipt.get("land_sha"):
        lines += ["", "land_sha: %s" % receipt["land_sha"]]
    ui.text("Цикл :: %s" % sel["task_id"], lines)


def organ_loop(ui, be, organ, throne_permit):
    while True:
        packs = be.list_packs(organ)
        menu = [("Паки в очереди (%d)" % len(packs), "packs"),
                ("Новый таск-пак", "new"),
                ("Валидировать пак", "validate"),
                ("Цикл (dry-run)", "dry"),
                ("Цикл (APPLY)", "apply"),
                ("Последние данные", "data"),
                ("Рецепты", "receipts"),
                ("← Назад/выход", "exit")]
        ch = ui.dashboard("ORGAN :: %s" % organ, menu, _organ_panels(be, organ, throne_permit))
        if ch in (None, "exit"):
            return
        if ch == "packs":
            ui.text("%s :: паки" % organ, _pack_lines(be, organ))
        elif ch == "new":
            new_pack_form(ui, be, organ)
        elif ch == "data":
            ui.text("%s :: данные" % organ, be.request_data(organ))
        elif ch == "receipts":
            ui.text("Рецепты", be.list_receipts() or ["(пусто)"])
        elif ch in ("validate", "dry", "apply"):
            if not packs:
                ui.text(organ, ["Нет паков для действия. Создай через 'Новый таск-пак'."])
                continue
            sel = ui.menu("Выбери пак", [(p["task_id"] + " — " + p["title"], p) for p in packs])
            if not sel:
                continue
            if ch == "validate":
                v, reasons, _r = be.validate(sel["dir"])
                lines = ["VERDICT: %s" % v, ""] + (["[%s] %s %s" % (x["gate"], x["code"], x["message"]) for x in reasons] or ["ворота чисты"])
                ui.text("Валидация :: %s" % sel["task_id"], lines)
            elif ch == "apply" and throne_permit != "GRANTED":
                ui.text("Цикл :: %s" % sel["task_id"],
                        ["APPLY требует throne_permit=GRANTED.",
                         "Сейчас permit=%s — разрешён только dry-run." % throne_permit,
                         "", "Permit выдаёт Трон."])
            else:
                _cycle_view(ui, be, sel, apply=(ch == "apply"), throne_permit=throne_permit)


def run(organ, be, throne_permit):
    core.run_app(lambda ui: organ_loop(ui, be, organ, throne_permit), be.banner())


def selftest(organ, be, throne_permit):
    print("== ORGAN-TUI selftest :: %s ==" % organ)
    print("reality :", be.reality())
    print("inbox   :", be.inbox())
    print("gate    :", "OK" if be.gate else "MISSING")
    print("cycle   :", "OK" if be.cycle else "MISSING")
    print("curses  :", "OK" if core.curses_available() else "NO (текстовый режим)")
    packs = be.list_packs(organ)
    print("packs   : %d" % len(packs))
    for p in packs:
        v, reasons, _r = be.validate(p["dir"])
        print("  -", p["task_id"], "|", p["change_kind"], "|", p["submitted_by"], "-> validate", v, "(%d)" % len(reasons))
    return 0 if (be.gate and be.cycle) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("organ", choices=core.CANON_ORGANS)
    ap.add_argument("--config")
    ap.add_argument("--throne-permit", default="DENIED")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    be = core.Backend(a.config)
    if a.selftest:
        return selftest(a.organ, be, a.throne_permit)
    run(a.organ, be, a.throne_permit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
