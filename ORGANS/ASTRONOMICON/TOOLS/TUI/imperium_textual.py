#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IMPERIUM :: Rich/Textual backend — максимальная красота TUI.

Опционален. Требует:  pip install \"textual>=0.50\" rich
Если пакеты не установлены — используйте curses-вариант (throne_tui.py);
лаунчер imperium.ps1 переключается автоматически.

Данные общие: imperium_tui_core.Backend (git, паки, валидация, цикл, рецепты).
Запуск:   python imperium_textual.py [--config PATH] [--selftest]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imperium_tui_core as core  # noqa: E402

# ---- мягкий импорт textual/rich -------------------------------------------
TEXTUAL_OK = True
IMPORT_ERR = None
try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, VerticalScroll, Vertical
    from textual.screen import ModalScreen
    from textual.widgets import (
        Static, Footer, Header, ListView, ListItem, Label, Input, Select, Button,
    )
    from rich.table import Table
    from rich.text import Text
    from rich.panel import Panel
    from rich import box
except Exception as _e:  # pragma: no cover
    TEXTUAL_OK = False
    IMPORT_ERR = _e

try:
    from textual.widgets import Sparkline  # type: ignore
    HAS_SPARK = True
except Exception:
    HAS_SPARK = False

GOLD = "#d4af37"
CRIMSON = "#7a0d0d"
INK = "#0b0b0b"


# ---- Rich-рендеры панелей (используются внутри Static) ---------------------
def _reality_renderable(be):
    gh = be.git_head()
    t = Table.grid(padding=(0, 1))
    t.add_column(justify="right", style="bold " + GOLD, no_wrap=True)
    t.add_column(style="white")
    t.add_row("reality", str(be.reality() or "-"))
    t.add_row("trunk", str(be.trunk()))
    if gh:
        state = gh.get("state", "?")
        col = "green" if state == "clean" else "yellow"
        t.add_row("HEAD", "%s [%s]%s[/]" % (gh.get("sha", "?"), col, state))
        if gh.get("subject"):
            t.add_row("посл.", gh["subject"][:54])
    else:
        t.add_row("HEAD", "[dim](нет git)[/]")
    return Panel(t, title="�​ СОСТОЯНИЕ РЕАЛЬНОСТИ", title_align="left",
                 border_style=GOLD, box=box.ROUNDED)


def _organs_renderable(be):
    counts = be.organ_status()
    t = Table(expand=True, box=box.SIMPLE, show_edge=False,
              header_style="bold " + GOLD, pad_edge=False)
    t.add_column("Орган", no_wrap=True)
    t.add_column("Паков", justify="right", width=6)
    t.add_column("", ratio=1)
    for o, n in counts.items():
        bar = ("█" * min(n, 10)) if n else ""
        t.add_row(o, ("[green]%d[/]" % n) if n else "[dim]·[/]",
                  "[%s]%s[/]" % (CRIMSON, bar))
    return Panel(t, title="⚙ ОРГАНЫ", title_align="left",
                 border_style=GOLD, box=box.ROUNDED)


def _receipts_renderable(be):
    rec = [os.path.basename(x) for x in be.list_receipts(10)]
    if rec:
        body = Text("\n".join(rec), style="white")
    else:
        body = Text("(пусто)", style="dim")
    return Panel(body, title="🧾 ПОСЛЕДНИЕ РЕЦЕПТЫ", title_align="left",
                 border_style=GOLD, box=box.ROUNDED)


if TEXTUAL_OK:

    class ResultScreen(ModalScreen):
        """Модальный экран с прокручиваемым результатом."""

        BINDINGS = [("escape", "dismiss", "Закрыть"), ("q", "dismiss", "Закрыть")]

        def __init__(self, title, lines, ok=True):
            super().__init__()
            self._title = title
            self._lines = lines
            self._ok = ok

        def compose(self) -> ComposeResult:
            border = "green" if self._ok else "red"
            with VerticalScroll(id="dialog"):
                yield Static(Panel(Text("\n".join(self._lines)),
                                   title=self._title, title_align="left",
                                   border_style=border, box=box.ROUNDED))
                yield Button("Закрыть", id="close", variant="primary")

        def on_button_pressed(self, event) -> None:
            self.dismiss(None)

        def action_dismiss(self) -> None:
            self.dismiss(None)

    class PickScreen(ModalScreen):
        """Модальный выбор из списка (label,value)."""

        BINDINGS = [("escape", "cancel", "Отмена"), ("q", "cancel", "Отмена")]

        def __init__(self, title, options):
            super().__init__()
            self._title = title
            self._options = options

        def compose(self) -> ComposeResult:
            with Vertical(id="picker"):
                yield Static(Text(self._title, style="bold " + GOLD))
                yield ListView(
                    *[ListItem(Label(lbl), id="opt_%d" % i)
                      for i, (lbl, _v) in enumerate(self._options)],
                    id="picklist",
                )

        def on_list_view_selected(self, event) -> None:
            try:
                i = int((event.item.id or "opt_-1").split("_")[1])
            except Exception:
                i = -1
            if 0 <= i < len(self._options):
                self.dismiss(self._options[i][1])

        def action_cancel(self) -> None:
            self.dismiss(None)

    class NewPackScreen(ModalScreen):
        """Рич-форма создания таск-пака в одном окне."""

        BINDINGS = [("escape", "cancel", "Отмена")]

        def __init__(self, organ):
            super().__init__()
            self.organ = organ

        def compose(self) -> ComposeResult:
            with Vertical(id="form"):
                yield Static(Text("Новый таск-пак :: %s" % self.organ,
                                  style="bold " + GOLD))
                yield Label("Task ID")
                yield Input(value=self.organ[:6] + "-", id="task_id")
                yield Label("Заголовок")
                yield Input(placeholder="коротко и по делу", id="title")
                yield Label("Интент (>=8 символов)")
                yield Input(placeholder="зачем этот пак", id="intent")
                yield Label("Тип изменения")
                yield Select([(c, c) for c in core.CHANGE_KINDS],
                             value=core.CHANGE_KINDS[0], allow_blank=False,
                             id="change_kind")
                yield Label("Кем подан")
                yield Select([(c, c) for c in core.SUBMITTERS],
                             value=core.SUBMITTERS[0], allow_blank=False,
                             id="submitted_by")
                with Horizontal(id="form_buttons"):
                    yield Button("Создать", id="submit", variant="success")
                    yield Button("Отмена", id="cancel", variant="error")

        def on_button_pressed(self, event) -> None:
            if event.button.id == "cancel":
                self.dismiss(None)
                return
            data = {
                "task_id": self.query_one("#task_id", Input).value.strip(),
                "title": self.query_one("#title", Input).value.strip(),
                "intent": self.query_one("#intent", Input).value.strip(),
                "change_kind": self.query_one("#change_kind", Select).value,
                "submitted_by": self.query_one("#submitted_by", Select).value,
            }
            self.dismiss(data)

        def action_cancel(self) -> None:
            self.dismiss(None)

    class ImperiumApp(App):
        """Имперский лаунчер на Textual — truecolor, живые панели, формы."""

        CSS = """
        Screen { background: """ + INK + """; }
        #banner { color: """ + GOLD + """; text-align: center; height: auto;
                  padding: 0 1; text-style: bold; }
        #titlebar { background: """ + CRIMSON + """; color: """ + GOLD + """;
                    text-style: bold; padding: 0 1; height: 1; }
        #body { height: 1fr; }
        #nav { width: 34; border: round """ + GOLD + """; background: $panel;
               padding: 0 1; }
        #nav > ListItem { padding: 0 1; }
        #nav > ListItem.--highlight { background: """ + GOLD + """; color: black;
                                      text-style: bold; }
        #panels { width: 1fr; padding: 0 1; }
        #panels > Static { height: auto; margin-bottom: 1; }
        #spark { height: 3; border: round """ + GOLD + """; }
        #dialog { align: center middle; padding: 2 4; }
        #picker, #form { width: 70; padding: 1 2; border: round """ + GOLD + """;
                         background: $panel; }
        #form Input, #form Select { margin-bottom: 1; }
        #form_buttons { height: auto; padding-top: 1; }
        #form_buttons Button { margin-right: 2; }
        """

        BINDINGS = [
            ("q", "quit", "Выход"),
            ("n", "new_pack", "Новый пак"),
            ("v", "validate", "Валидация"),
            ("c", "run_cycle", "Цикл (dry)"),
            ("p", "toggle_permit", "Permit"),
            ("d", "drill", "Орган"),
            ("b", "to_throne", "К Трону"),
            ("r", "do_refresh", "Обновить"),
        ]

        def __init__(self, be):
            super().__init__()
            self.be = be
            self.permit = "DENIED"
            self.current_organ = None  # None = Трон

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield Static("\n".join(self.be.banner()), id="banner")
            yield Static("", id="titlebar")
            with Horizontal(id="body"):
                yield ListView(
                    ListItem(Label("Войти в орган →"), id="nav_drill"),
                    ListItem(Label("Новый таск-пак →"), id="nav_new"),
                    ListItem(Label("Валидировать пак"), id="nav_validate"),
                    ListItem(Label("Throne permit: DENIED", id="permit_label"),
                             id="nav_permit"),
                    ListItem(Label("Полный цикл (dry)"), id="nav_cycle"),
                    ListItem(Label("Рецепты"), id="nav_receipts"),
                    id="nav",
                )
                with VerticalScroll(id="panels"):
                    yield Static(id="reality")
                    yield Static(id="organs")
                    if HAS_SPARK:
                        yield Sparkline([0], summary_function=max, id="spark")
                    yield Static(id="receipts")
            yield Footer()

        def on_mount(self) -> None:
            self.title = "IMPERIUM"
            self.sub_title = "Throne"
            self.do_refresh()
            # fade-in баннера (анимация)
            try:
                banner = self.query_one("#banner", Static)
                banner.styles.opacity = 0.0
                banner.styles.animate("opacity", value=1.0, duration=1.2)
            except Exception:
                pass
            self.set_interval(2.0, self.do_refresh)

        # ---- данные ----
        def do_refresh(self) -> None:
            try:
                self.query_one("#reality", Static).update(_reality_renderable(self.be))
                self.query_one("#organs", Static).update(_organs_renderable(self.be))
                self.query_one("#receipts", Static).update(_receipts_renderable(self.be))
                scope = ("ORGAN :: %s" % self.current_organ) if self.current_organ \
                    else "THRONE :: пульт оркестрации"
                self.query_one("#titlebar", Static).update(
                    "%s    permit=%s" % (scope, self.permit))
                self.sub_title = self.current_organ or "Throne"
                if HAS_SPARK:
                    counts = list(self.be.organ_status().values()) or [0]
                    self.query_one("#spark", Sparkline).data = counts
            except Exception:
                pass

        # ---- навигация ----
        def on_list_view_selected(self, event) -> None:
            key = (getattr(event.item, "id", "") or "")
            disp = {
                "nav_drill": self.action_drill,
                "nav_new": self.action_new_pack,
                "nav_validate": self.action_validate,
                "nav_permit": self.action_toggle_permit,
                "nav_cycle": self.action_run_cycle,
                "nav_receipts": self.action_receipts,
            }.get(key)
            if disp:
                disp()

        # ---- действия ----
        def action_to_throne(self) -> None:
            self.current_organ = None
            self.do_refresh()

        def action_toggle_permit(self) -> None:
            self.permit = "GRANTED" if self.permit == "DENIED" else "DENIED"
            try:
                self.query_one("#permit_label", Label).update(
                    "Throne permit: %s" % self.permit)
            except Exception:
                pass
            self.do_refresh()

        def action_drill(self) -> None:
            opts = [(o, o) for o in core.CANON_ORGANS]

            def after(organ):
                if organ:
                    self.current_organ = organ
                    self.do_refresh()
            self.push_screen(PickScreen("В какой орган?", opts), after)

        def _resolve_organ(self, then):
            if self.current_organ:
                then(self.current_organ)
            else:
                self.push_screen(
                    PickScreen("В какой орган?", [(o, o) for o in core.CANON_ORGANS]),
                    lambda o: then(o) if o else None)

        def action_new_pack(self) -> None:
            def with_organ(organ):
                def after_form(data):
                    if not data or not data.get("task_id"):
                        return
                    d, err = self.be.new_task_pack(
                        organ, data["task_id"], data["title"] or data["task_id"],
                        data["intent"], data["change_kind"] or "PATCH",
                        data["submitted_by"] or "OWNER_MANUAL")
                    if err:
                        self.push_screen(ResultScreen("Новый пак", ["Ошибка: " + err], ok=False))
                        return
                    v, reasons, _r = self.be.validate(d)
                    lines = ["Создан: %s" % d, "", "Автовалидация: %s" % v] + (
                        ["[%s] %s — %s" % (x["gate"], x["code"], x["message"]) for x in reasons]
                        or ["ворота чисты"])
                    lines += ["", "Дальше: положи файлы в files/, заполни payload,",
                              "передай сервитору (Codex/Grok) и верни на валидацию."]
                    self.push_screen(ResultScreen("Новый таск-пак", lines, ok=("OK" in v or "ADMIT" in v)))
                    self.do_refresh()
                self.push_screen(NewPackScreen(organ), after_form)
            self._resolve_organ(with_organ)

        def _pick_pack(self, title, then):
            packs = self.be.list_packs(self.current_organ) if self.current_organ \
                else self.be.list_packs()
            if not packs:
                self.push_screen(ResultScreen(title, ["Паков не найдено"], ok=False))
                return
            opts = [("%s :: %s" % (p["task_id"], p.get("title") or ""), p["dir"])
                    for p in packs]
            self.push_screen(PickScreen(title, opts), lambda d: then(d) if d else None)

        def action_validate(self) -> None:
            def run(pack_dir):
                v, reasons, _r = self.be.validate(pack_dir)
                lines = ["Вердикт: %s" % v, ""] + (
                    ["[%s] %s — %s" % (x["gate"], x["code"], x["message"]) for x in reasons]
                    or ["ворота чисты"])
                self.push_screen(ResultScreen("Валидация", lines,
                                              ok=("OK" in v or "ADMIT" in v)))
            self._pick_pack("Какой пак валидировать?", run)

        def action_run_cycle(self) -> None:
            def run(pack_dir):
                verdict, receipt = self.be.run_cycle(
                    pack_dir, apply=False, throne_permit=self.permit)
                stages = receipt.get("stages", []) if isinstance(receipt, dict) else []
                lines = ["Вердикт: %s" % verdict, "permit=%s · режим=DRYRUN" % self.permit, ""]
                for s in stages:
                    if isinstance(s, dict):
                        lines.append("%-12s %s" % (s.get("stage", "?"), s.get("status", "")))
                    else:
                        lines.append(str(s))
                self.push_screen(ResultScreen("Полный цикл (dry-run)", lines,
                                              ok=("OK" in verdict)))
            self._pick_pack("Прогнать цикл (dry) для пака:", run)

        def action_receipts(self) -> None:
            rec = [os.path.basename(x) for x in self.be.list_receipts(40)]
            self.push_screen(ResultScreen("Рецепты", rec or ["(пусто)"]))


def run(config_path=None):
    if not TEXTUAL_OK:
        print("[IMPERIUM] textual/rich не установлены — нужен:")
        print('    pip install "textual>=0.50" rich')
        print("Причина:", IMPORT_ERR)
        print("Пока используйте curses-вариант:  python throne_tui.py")
        return 2
    be = core.Backend(config_path)
    ImperiumApp(be).run()
    return 0


def selftest(config_path=None):
    print("== IMPERIUM Textual selftest ==")
    print("textual  :", "OK" if TEXTUAL_OK else ("НЕТ (%s)" % IMPORT_ERR))
    print("sparkline:", "OK" if HAS_SPARK else "нет (необязательно)")
    be = core.Backend(config_path)
    gh = be.git_head()
    print("reality  :", be.reality())
    print("git HEAD :", ("%s (%s)" % (gh["sha"], gh["state"])) if gh else "(нет git)")
    print("органы   :", sum(be.organ_status().values()), "паков всего")
    return 0 if TEXTUAL_OK else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    config_path = None
    if "--config" in argv:
        i = argv.index("--config")
        if i + 1 < len(argv):
            config_path = argv[i + 1]
    if "--selftest" in argv:
        return selftest(config_path)
    return run(config_path)


if __name__ == "__main__":
    raise SystemExit(main())
