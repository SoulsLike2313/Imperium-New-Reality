from __future__ import annotations

from collections import Counter
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from textual import on
from textual.widgets import DataTable

from mechanicus_forge_client_v0_4 import MechanicusForgeClientV04
from mechanicus_forge_client_v0_3 import (
    AMBER,
    BRASS,
    COPPER,
    CYAN,
    GREEN,
    RED,
    WHITE,
    evidence_metrics,
    folder_freshness,
    git_snapshot,
    status_color,
)


CATEGORY_RU = {
    "ALGORITHMS": "АЛГОРИТМЫ",
    "CLOUD_LLM_ADAPTERS": "ОБЛАЧНЫЕ_LLM_АДАПТЕРЫ",
    "CODE_QUALITY": "КАЧЕСТВО_КОДА",
    "DATABASES": "БАЗЫ_ДАННЫХ",
    "EXAMPLES": "ПРИМЕРЫ",
    "LANGUAGES": "ЯЗЫКИ",
    "LOCAL_LLM": "ЛОКАЛЬНЫЕ_LLM",
    "PLAYBOOKS": "ПЛЕЙБУКИ",
    "PROMPTING_PATTERNS": "ПРОМПТ_ШАБЛОНЫ",
    "REFERENCE_CODE": "ЭТАЛОННЫЙ_КОД",
    "SEARCH_INDEXING": "ПОИСК_ИНДЕКСЫ",
    "TOOLS": "ИНСТРУМЕНТЫ",
    "UI_FRAMEWORKS": "UI_ФРЕЙМВОРКИ",
    "UTILITIES": "УТИЛИТЫ",
    "VISUAL_TESTING": "ВИЗУАЛЬНЫЕ_ТЕСТЫ",
    "QUARANTINE": "КАРАНТИН",
}

STATUS_RU = {
    "SANDBOX": "ПЕСОЧНИЦА",
    "CANDIDATE": "КАНДИДАТ",
    "CANON": "КАНОН",
    "EVIDENCE": "ДОКАЗАНО",
    "PASS": "ПРОЙДЕНО",
    "PASS_WITH_WARNINGS": "ПРОЙДЕНО_С_WARN",
    "FAIL": "ПРОВАЛ",
    "WARN": "ПРЕДУПРЕЖДЕНИЕ",
    "BLOCKED": "БЛОК",
    "QUARANTINE": "КАРАНТИН",
    "QUARANTINED": "КАРАНТИН",
    "UNKNOWN": "НЕИЗВЕСТНО",
    "CLEAN": "ЧИСТО",
    "DIRTY": "ГРЯЗНО",
    "OK": "OK",
}

FOLDER_RU = {
    "ARSENAL/CATEGORIES": "КАТЕГОРИИ_АРСЕНАЛА",
    "ARSENAL/REGISTRY": "РЕЕСТР_АРСЕНАЛА",
    "ARSENAL/RECEIPTS": "КВИТАНЦИИ",
    "ARSENAL/SCOPE_PACKS": "ПАКЕТЫ_SCOPE",
    "ARSENAL/TOOL_EXPANSION": "РАСШИРЕНИЕ_ИНСТРУМЕНТОВ",
    "EVIDENCE_INDEX/V0_1": "ИНДЕКС_ДОКАЗАТЕЛЬСТВ",
    "REPORTS": "ОТЧЁТЫ",
    "TOOLS": "СКРИПТЫ_МЕХАНИКУС",
    "FORGE_TUI": "КЛИЕНТ_КУЗНИ",
}

FIELD_RU = {
    "Status": "Статус",
    "Owner Organ": "Орган-владелец",
    "Category": "Категория",
    "Capability Type": "Тип возможности",
    "First Detected": "Первое обнаружение",
    "Last Updated": "Последнее обновление",
    "Scope Relevance": "Связь со scope",
    "Path": "Путь",
}


def ru_category(category: str) -> str:
    raw = str(category).upper()
    return f"{CATEGORY_RU.get(raw, raw)} / {raw}"


def ru_status(status: str) -> str:
    raw = str(status).upper()
    return f"{STATUS_RU.get(raw, raw)} / {raw}"


def ru_folder(path: str) -> str:
    raw = str(path)
    return f"{FOLDER_RU.get(raw, raw)} / {raw}"


def short(text: str, limit: int = 54) -> str:
    text = str(text)
    if len(text) <= limit:
        return text
    return text[: max(1, limit - 1)] + "…"


class MechanicusForgeClientV05RU(MechanicusForgeClientV04):
    CSS_PATH = "forge_client_v0_5.tcss"
    TITLE = "Mechanicus Forge Client V0.5 RU"

    def on_mount(self) -> None:
        table = self.query_one("#capability_table", DataTable)
        table.clear(columns=True)
        table.add_columns("ВОЗМОЖНОСТЬ", "ВЛАДЕЛЕЦ", "СТАТУС", "ОБНОВЛЕНО", "SCOPE")
        table.cursor_type = "row"
        self.selected_category = "TOOLS"
        self.cards = []
        self.receipts = []
        self.approvals = []
        self.reload_all()

    def update_truth_strip(self) -> None:
        git = git_snapshot()
        counts = Counter(card["status"] for card in self.cards)
        metrics = evidence_metrics()

        tiles = Table.grid(expand=True)
        for _ in range(9):
            tiles.add_column(ratio=1)

        def tile(label_ru: str, label_id: str, value: str, color: str = CYAN) -> Panel:
            text = Text()
            text.append(label_ru + "\n", style=f"bold {BRASS}")
            text.append(label_id + "\n", style="#8f98a3")
            text.append(value, style=f"bold {color}")
            return Panel(text, border_style="#51402d", box=box.ROUNDED, padding=(0, 1))

        tiles.add_row(
            tile("ВСЕГО КАРТ", "TOTAL", str(len(self.cards))),
            tile("КАНОН", "CANON", str(counts.get("CANON", 0))),
            tile("ПЕСОЧНИЦА", "SANDBOX", str(counts.get("SANDBOX", 0)), GREEN),
            tile("КАНДИДАТЫ", "CANDIDATE", str(counts.get("CANDIDATE", 0)), AMBER),
            tile("ДЕРЕВО", "WORKTREE", ru_status(git["worktree"]), GREEN if git["worktree"] == "CLEAN" else RED),
            tile("СИНХРОН", "REMOTE", git["remote_sync"], GREEN if git["remote_sync"] == "OK" else AMBER),
            tile("ИНДЕКС", "EVIDENCE", f"{metrics['records']} записей"),
            tile("РЕШЕНИЯ", "OWNER", f"{len(self.approvals)} ожидают", AMBER if self.approvals else GREEN),
            tile("HEAD", "GIT", git["head"]),
        )

        sigil = Text()
        sigil.append("<< ", style=COPPER)
        sigil.append("РИТУАЛ ЧТЕНИЯ ОМНИССИИ", style=f"bold {BRASS}")
        sigil.append(" :: ", style=COPPER)
        sigil.append("MECHANICUS FORGE CLIENT V0.5 RU", style=f"bold {CYAN}")
        sigil.append(" :: ", style=COPPER)
        sigil.append("РЕЕСТР АРСЕНАЛА", style=f"bold {BRASS}")
        sigil.append(" >>", style=COPPER)

        machine = Text()
        machine.append("ДУХ МАШИНЫ: ", style=f"bold {BRASS}")
        machine.append("СТАБИЛЕН" if git["worktree"] == "CLEAN" else "ТРЕБУЕТ ВНИМАНИЯ", style=f"bold {GREEN if git['worktree'] == 'CLEAN' else AMBER}")
        machine.append("  |  ")
        machine.append("ЗАПИСЬ ЗАПЕЧАТАНА", style=f"bold {CYAN}")
        machine.append("  |  ")
        machine.append(f"ПЕСОЧНИЦА {counts.get('SANDBOX', 0)}", style=f"bold {GREEN}")
        machine.append("  |  ")
        machine.append(f"КАНДИДАТЫ {counts.get('CANDIDATE', 0)}", style=f"bold {AMBER}")
        machine.append("  |  ")
        machine.append(f"РЕШЕНИЯ OWNER {len(self.approvals)}", style=f"bold {AMBER if self.approvals else GREEN}")

        group = Group(
            Align.center(sigil),
            Text(""),
            tiles,
            Text(""),
            Align.center(machine),
            Align.center(Text("Русский индексный слой: рядом с понятным названием всегда сохранён машинный ID.", style=CYAN)),
        )

        panel = Panel(
            group,
            subtitle=f"[cyan]ВНУТРИ АГЕНТА | READ-ONLY | {git['snapshot']}[/]",
            border_style=COPPER,
            box=box.DOUBLE,
            padding=(0, 1),
        )
        self.query_one("#truth_strip").update(panel)

    def update_category_tree(self) -> None:
        tree = self.query_one("#category_tree")
        tree.clear()
        counts = Counter(card["category"] for card in self.cards)
        root = tree.root
        root.set_label(f"⚙ ВСЕ КАТЕГОРИИ / ALL ({len(self.cards)})")
        root.data = "ALL"
        for cat, count in sorted(counts.items()):
            label = f"{ru_category(cat)} ({count})"
            node = root.add_leaf(label, data=cat)
            if cat == self.selected_category:
                node.set_label(f"▶ {label}")
        root.expand()

    def update_folder_tree(self) -> None:
        tree = self.query_one("#folder_tree")
        tree.clear()
        root = tree.root
        root.set_label("++ ПАПКИ МЕХАНИКУСА / СВЕЖЕСТЬ ++")
        for row in folder_freshness():
            status = "OK" if row["exists"] == "YES" else "MISS"
            glyph = "[OK]" if status == "OK" else "[!!]"
            root.add_leaf(
                f"{glyph} {ru_folder(row['path'])} | {row['files']} файлов | {status} | {row['fresh']}",
                data=row["path"],
            )
        root.expand()

    def update_capability_table(self) -> None:
        table = self.query_one("#capability_table", DataTable)
        table.clear(columns=False)
        for card in self.filtered_cards():
            table.add_row(
                card["capability_id"],
                card["owner"],
                f"[{status_color(card['status'])}]{ru_status(card['status'])}[/]",
                card["updated"],
                card["scope"],
                key=card["capability_id"],
            )
        cards = self.filtered_cards()
        if cards:
            self.update_detail(cards[0])
        else:
            self.query_one("#detail_panel").update(Panel("В категории нет карточек.", border_style=COPPER))

    def update_status_summary(self) -> None:
        counts = Counter(card["status"] for card in self.cards)
        table = Table.grid(expand=True)
        table.add_column()
        table.add_column(justify="right")
        total = len(self.cards)

        for key in ["SANDBOX", "CANDIDATE", "EVIDENCE", "PASS_WITH_WARNINGS", "QUARANTINE", "QUARANTINED", "CANON", "UNKNOWN"]:
            val = counts.get(key, 0)
            if val:
                pct = (val / total * 100) if total else 0
                table.add_row(f"[{status_color(key)}]{ru_status(key)}[/]", f"[cyan]{val}[/] [white]({pct:.1f}%)[/]")

        table.add_row(f"[bold {BRASS}]ИТОГО / TOTAL[/]", f"[cyan]{total}[/]")
        table.add_row("", "")
        table.add_row(f"[bold {BRASS}]РЕЖИМ[/]", "[cyan]ТОЛЬКО ЧТЕНИЕ[/]")
        table.add_row(f"[bold {BRASS}]КУЗНЯ[/]", "[cyan]ДЕЙСТВИЯ ЗАПЕЧАТАНЫ[/]")

        self.query_one("#status_summary").update(
            Panel(
                table,
                title=f"[bold {BRASS}]СВОДКА ПЕЧАТИ РЕЕСТРА[/]",
                subtitle=f"[cyan]Выбрано: {ru_category(self.selected_category)}[/]",
                border_style=COPPER,
                box=box.DOUBLE,
            )
        )

    def update_detail(self, card: dict[str, Any]) -> None:
        info = Table.grid(padding=(0, 1))
        info.add_column(style=BRASS)
        info.add_column(style=WHITE)

        rows = [
            ("Status", ru_status(card["status"])),
            ("Owner Organ", card["owner"]),
            ("Category", ru_category(card["category"])),
            ("Capability Type", card["type"]),
            ("First Detected", card["first_detected"]),
            ("Last Updated", card["updated"]),
            ("Scope Relevance", card["scope"]),
            ("Path", card["path"]),
        ]
        for key, value in rows:
            info.add_row(FIELD_RU.get(key, key), str(value))

        receipt_table = Table(show_header=False, expand=True, box=box.SIMPLE)
        receipt_table.add_column("time", style=CYAN, width=20)
        receipt_table.add_column("file", style=WHITE)
        matches = self.matching_receipts(card)
        for receipt in matches:
            receipt_table.add_row(receipt["time"], f"{short(receipt['file_name'], 46)} [{ru_status(receipt['status'])}]")
        if not matches:
            receipt_table.add_row("-", "Прямая квитанция не найдена")

        plus = card["raw"].get("plus") or card["raw"].get("benefits") or card["raw"].get("pros")
        minus = card["raw"].get("minus") or card["raw"].get("risks") or card["raw"].get("cons")
        if not isinstance(plus, list):
            plus = ["Зарегистрированная возможность", "Доступно для scope-review", "Связано с evidence, если есть receipt"]
        if not isinstance(minus, list):
            minus = ["Риски ещё не нормализованы", "Профиль платформы требует будущей VM3-проверки"]

        text = Text()
        text.append(card["capability_id"] + "\n", style=f"bold {BRASS}")
        text.append(f"{CATEGORY_RU.get(card['category'], card['category'])} / {card['category']}\n\n", style=CYAN)
        text.append("ПЛЮС / VALUE\n", style=f"bold {GREEN}")
        for item in plus[:4]:
            text.append(f"+ {item}\n", style=GREEN)
        text.append("\nРИСК / MINUS\n", style=f"bold {AMBER}")
        for item in minus[:4]:
            text.append(f"- {item}\n", style=AMBER)

        group = Table.grid(expand=True)
        group.add_row(info)
        group.add_row(Text("\nКВИТАНЦИИ ВАЛИДАЦИИ / VALIDATION RECEIPTS", style=f"bold {BRASS}"))
        group.add_row(receipt_table)
        group.add_row(text)

        self.query_one("#detail_panel").update(
            Panel(group, title=f"[bold {BRASS}]ДЕТАЛЬ ВОЗМОЖНОСТИ[/]", border_style=COPPER, box=box.ROUNDED)
        )

    def update_receipts(self) -> None:
        table = Table(show_header=True, header_style=f"bold {BRASS}", expand=True, box=box.SIMPLE_HEAVY)
        table.add_column("ВРЕМЯ", style=CYAN, width=20)
        table.add_column("ТИП", width=20)
        table.add_column("СУБЪЕКТ", style=WHITE)
        table.add_column("СТАТУС", width=22)
        for receipt in self.receipts[:5]:
            rtype = receipt["file_name"].replace("_validation_receipt.json", "").replace(".json", "")[:20]
            table.add_row(
                receipt["time"],
                rtype,
                str(receipt["subject"])[:48],
                f"[{status_color(receipt['status'])}]{ru_status(receipt['status'])}[/]",
            )
        self.query_one("#receipt_panel").update(
            Panel(table, title=f"[bold {BRASS}]ХРАНИЛИЩЕ КВИТАНЦИЙ — ПОСЛЕДНЯЯ ИСТИНА[/]", border_style=COPPER, box=box.ROUNDED)
        )

    def update_actions(self) -> None:
        table = Table.grid(expand=True)
        table.add_column()
        table.add_row(f"[bold {BRASS}]ЗАПЕЧАТАННЫЕ ACTION SOCKETS[/]")
        table.add_row("")
        table.add_row("[white][ Validate / Валидировать ][/]   [white][ Promote / Повысить ][/]")
        table.add_row("[white][ Export Scope / Выдать scope ][/]   [white][ Open Receipt / Открыть receipt ][/]")
        table.add_row("[white][ Approve Tool / Одобрить tool ][/]   [white][ Refresh Index / Обновить индекс ][/]")
        table.add_row("")
        table.add_row("[cyan]READ-ONLY: без записи, установок, сервера.[/]")
        table.add_row("[cyan]Кнопки оживут только после Officio + Inquisition + Owner gates.[/]")
        table.add_row("")
        table.add_row(f"[bold {BRASS}]Решения Owner ожидают:[/] [yellow]{len(self.approvals)}[/]")
        for item in self.approvals[:5]:
            label = item.get("tool") or item.get("name") or item.get("capability_id") or item.get("question") or str(item)
            table.add_row(f"[yellow]• {label}[/]")
        self.query_one("#action_panel").update(
            Panel(table, title=f"[bold {BRASS}]РИТУАЛЬНЫЕ СОКЕТЫ[/]", border_style=COPPER, box=box.DOUBLE)
        )


if __name__ == "__main__":
    MechanicusForgeClientV05RU().run()
