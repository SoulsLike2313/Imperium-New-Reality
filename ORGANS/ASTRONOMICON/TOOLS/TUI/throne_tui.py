#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Throne-TUI v0_4 — личный имперский лаунчер / верховная оркестрация.

Трон — единая точка входа:
  · сводка по всем 9 органам
  · «провалиться» в любой орган (его СОБСТВЕННЫЙ TUI) — проверка/данные/формы
  · новый таск-пак в любой орган
  · верховный permit (только Трон) → полный цикл
  · состояние реальности (git) · рецепты

Запуск:  python throne_tui.py   |   python throne_tui.py --selftest
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imperium_tui_core as core  # noqa: E402
import organ_tui  # noqa: E402


def _board(be):
    counts = be.organ_status()
    return ["%-20s %s" % (o, ("%d пак(ов)" % n) if n else "-") for o, n in counts.items()]


def _panels(be):
    """Живые панели домашнего экрана Трона."""
    gh = be.git_head()
    counts = be.organ_status()
    real = ["reality: " + (be.reality() or "-"),
            "trunk:   " + be.trunk(),
            "HEAD:    " + (("%s (%s)" % (gh["sha"], gh["state"])) if gh else "(нет git)")]
    if gh and gh.get("subject"):
        real.append("посл.:   " + gh["subject"][:42])
    organs = ["%-18s %s" % (o, ("%d пак" % n) if n else "-") for o, n in counts.items()]
    rec = [os.path.basename(x) for x in be.list_receipts(6)] or ["(пусто)"]
    return [("СОСТОЯНИЕ РЕАЛЬНОСТИ", real),
            ("ОРГАНЫ — паков в очереди", organs),
            ("ПОСЛЕДНИЕ РЕЦЕПТЫ", rec)]


def _pick_organ(ui, title="В какой орган?"):
    return ui.menu(title, [(x, x) for x in core.CANON_ORGANS])


def throne_loop(ui, be):
    permit = {"v": "DENIED"}
    while True:
        menu = [("Войти в орган →", "drill"),
                ("Новый таск-пак →", "new"),
                ("Валидировать любой пак", "validate"),
                ("Throne permit: %s" % permit["v"], "permit"),
                ("Полный цикл (требует GRANTED)", "cycle"),
                ("Состояние реальности (детально)", "state"),
                ("Рецепты", "receipts"),
                ("Выход", "exit")]
        ch = ui.dashboard("THRONE :: пульт оркестрации", menu, _panels(be))
        if ch in (None, "exit"):
            return
        if ch == "board":
            ui.text("Сводка по органам", _board(be))
        elif ch == "permit":
            permit["v"] = "GRANTED" if permit["v"] == "DENIED" else "DENIED"
        elif ch == "drill":
            o = _pick_organ(ui)
            if o:
                organ_tui.organ_loop(ui, be, o, permit["v"])
        elif ch == "new":
            o = _pick_organ(ui, "Новый пак — в какой орган?")
            if o:
                organ_tui.new_pack_form(ui, be, o)
        elif ch == "state":
            gh = be.git_head()
            lines = ["reality: %s" % be.reality()]
            lines.append("git HEAD: %s" % ("%s (%s) — %s" % (gh["sha"], gh["state"], gh["subject"]) if gh else "(нет git)"))
            lines.append("trunk: %s" % be.trunk())
            lines += ["", "Органы:"] + _board(be)
            ui.text("Состояние реальности", lines)
        elif ch == "receipts":
            ui.text("Рецепты", be.list_receipts() or ["(пусто)"])
        elif ch in ("validate", "cycle"):
            packs = be.list_packs()
            if not packs:
                ui.text("THRONE", ["Нет паков в inbox. Создай через 'Новый таск-пак'."])
                continue
            sel = ui.menu("Выбери пак", [("%s [%s]" % (p["task_id"], p["target_organ"]), p) for p in packs])
            if not sel:
                continue
            if ch == "validate":
                v, reasons, _r = be.validate(sel["dir"])
                lines = ["VERDICT: %s" % v, ""] + (["[%s] %s %s" % (x["gate"], x["code"], x["message"]) for x in reasons] or ["ворота чисты"])
                ui.text("Валидация :: %s" % sel["task_id"], lines)
            else:
                if permit["v"] != "GRANTED":
                    ui.text("Цикл", ["Полный цикл требует Throne permit = GRANTED.",
                                    "Сейчас: %s. Выдай permit в меню." % permit["v"]])
                    continue
                verdict, receipt = be.run_cycle(sel["dir"], apply=True, throne_permit=permit["v"])
                lines = ["CYCLE_VERDICT: %s" % verdict, "permit=%s" % permit["v"], ""]
                for st in receipt.get("stages", []):
                    lines.append("[%-10s] %-8s %s" % (st["stage"], st["status"], st.get("detail") or ""))
                if receipt.get("land_sha"):
                    lines += ["", "land_sha: %s" % receipt["land_sha"]]
                ui.text("Цикл :: %s" % sel["task_id"], lines)


def run(be):
    core.run_app(lambda ui: throne_loop(ui, be), be.banner())


def selftest(be):
    print("== THRONE-TUI selftest ==")
    print("reality :", be.reality())
    print("inbox   :", be.inbox())
    print("gate/cycle:", "OK" if be.gate else "MISSING", "/", "OK" if be.cycle else "MISSING")
    print("curses  :", "OK" if core.curses_available() else "NO (текстовый режим)")
    gh = be.git_head()
    print("git HEAD:", ("%s (%s)" % (gh["sha"], gh["state"])) if gh else "(нет git)")
    print("-- сводка по органам --")
    for ln in _board(be):
        print("  ", ln)
    packs = be.list_packs()
    if packs:
        v1, _ = be.run_cycle(packs[0]["dir"], apply=False, throne_permit="DENIED")
        v2, _ = be.run_cycle(packs[0]["dir"], apply=False, throne_permit="GRANTED")
        print("-- permit-gate: DENIED ->", v1, "| GRANTED ->", v2)
    return 0 if (be.gate and be.cycle) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    be = core.Backend(a.config)
    if a.selftest:
        return selftest(be)
    run(be)
    return 0


if __name__ == "__main__":
    sys.exit(main())
