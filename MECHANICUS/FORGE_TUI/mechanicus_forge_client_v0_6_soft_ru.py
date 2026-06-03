from __future__ import annotations

from collections import Counter
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mechanicus_forge_client_v0_5_ru import (
    MechanicusForgeClientV05RU,
    CATEGORY_RU,
    FOLDER_RU,
    STATUS_RU,
    FIELD_RU,
    ru_category,
    ru_folder,
    ru_status,
    short,
)
from mechanicus_forge_client_v0_3 import evidence_metrics, folder_freshness, git_snapshot, status_color


BRASS_SOFT = "#d8b56a"
GOLD = "#e0c27a"
STEEL = "#b9c7d8"
ICE = "#9fd8ff"
VIOLET = "#9e7cff"
PURPLE_GHOST = "#7e5ce6"
BURGUNDY = "#5d1425"
BURGUNDY_LIGHT = "#7a2136"
INK = "#050608"
TEXT = "#dfd7ca"
MUTED = "#9b95a8"
GOOD = "#9bd06b"
WARN = "#e8b35b"
BAD = "#ff6b8d"


class MechanicusForgeClientV06SoftRU(MechanicusForgeClientV05RU):
    CSS_PATH = "forge_client_v0_6.tcss"
    TITLE = "Mechanicus Forge Client V0.6 Soft RU"

    def update_truth_strip(self) -> None:
        git = git_snapshot()
        counts = Counter(card["status"] for card in self.cards)
        metrics = evidence_metrics()

        tiles = Table.grid(expand=True)
        for _ in range(9):
            tiles.add_column(ratio=1)

        def tile(label_ru: str, label_id: str, value: str, color: str = ICE) -> Panel:
            text = Text()
            text.append(label_ru + "\n", style=f"bold {GOLD}")
            text.append(label_id + "\n", style=MUTED)
            text.append(value, style=f"bold {color}")
            return Panel(text, border_style=BURGUNDY_LIGHT, box=box.ROUNDED, padding=(0, 1))

        worktree_color = GOOD if git["worktree"] == "CLEAN" else BAD
        remote_color = GOOD if git["remote_sync"] == "OK" else WARN

        tiles.add_row(
            tile("Всего карт", "TOTAL", str(len(self.cards))),
            tile("Канон", "CANON", str(counts.get("CANON", 0))),
            tile("Песочница", "SANDBOX", str(counts.get("SANDBOX", 0)), GOOD),
            tile("Кандидаты", "CANDIDATE", str(counts.get("CANDIDATE", 0)), WARN),
            tile("Дерево", "WORKTREE", ru_status(git["worktree"]), worktree_color),
            tile("Синхрон", "REMOTE", git["remote_sync"], remote_color),
            tile("Индекс", "EVIDENCE", f"{metrics['records']} записей"),
            tile("Решения", "OWNER", f"{len(self.approvals)} ожидают", WARN if self.approvals else GOOD),
            tile("Head", "GIT", git["head"]),
        )

        title = Text()
        title.append("« ", style=PURPLE_GHOST)
        title.append("Ритуал чтения Омниссии", style=f"bold {GOLD}")
        title.append("  ::  ", style=BURGUNDY_LIGHT)
        title.append("Mechanicus Forge Client V0.6", style=f"bold {ICE}")
        title.append("  ::  ", style=BURGUNDY_LIGHT)
        title.append("Реестр арсенала", style=f"bold {GOLD}")
        title.append(" »", style=PURPLE_GHOST)

        machine = Text()
        machine.append("Дух машины: ", style=f"bold {PURPLE_GHOST}")
        machine.append("стабилен" if git["worktree"] == "CLEAN" else "требует внимания", style=f"bold {GOOD if git['worktree'] == 'CLEAN' else WARN}")
        machine.append("  |  ", style=MUTED)
        machine.append("запись запечатана", style=f"bold {STEEL}")
        machine.append("  |  ", style=MUTED)
        machine.append(f"песочница {counts.get('SANDBOX', 0)}", style=f"bold {GOOD}")
        machine.append("  |  ", style=MUTED)
        machine.append(f"кандидаты {counts.get('CANDIDATE', 0)}", style=f"bold {WARN}")
        machine.append("  |  ", style=MUTED)
        machine.append(f"решения owner {len(self.approvals)}", style=f"bold {WARN if self.approvals else GOOD}")

        whisper = Text()
        whisper.append("Фиолетовый дух машины", style=f"italic {PURPLE_GHOST}")
        whisper.append(" проходит по всем поверхностям интерфейса. Русский индексный слой сохранён рядом с машинным ID.", style=STEEL)

        group = Group(
            Align.center(title),
            Text(""),
            tiles,
            Text(""),
            Align.center(machine),
            Align.center(whisper),
        )

        panel = Panel(
            group,
            subtitle=f"[{ICE}]Внутри агента  |  read-only  |  {git['snapshot']}[/]",
            border_style=BURGUNDY_LIGHT,
            box=box.DOUBLE,
            padding=(0, 1),
        )
        self.query_one("#truth_strip").update(panel)

    def update_category_tree(self) -> None:
        tree = self.query_one("#category_tree")
        tree.clear()
        counts = Counter(card["category"] for card in self.cards)
        root = tree.root
        root.set_label(f"✦ Все категории / ALL ({len(self.cards)})")
        root.data = "ALL"
        for cat, count in sorted(counts.items()):
            label = f"{ru_category(cat)} ({count})"
            node = root.add_leaf(label, data=cat)
            if cat == self.selected_category:
                node.set_label(f"› {label}")
        root.expand()

    def update_folder_tree(self) -> None:
        tree = self.query_one("#folder_tree")
        tree.clear()
        root = tree.root
        root.set_label("✦ Папки Механикуса / свежесть")
        for row in folder_freshness():
            status = "OK" if row["exists"] == "YES" else "MISS"
            glyph = "◦" if status == "OK" else "!"
            root.add_leaf(
                f"{glyph} {ru_folder(row['path'])} | {row['files']} файлов | {status} | {row['fresh']}",
                data=row["path"],
            )
        root.expand()

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
                table.add_row(f"[{status_color(key)}]{ru_status(key)}[/]", f"[{ICE}]{val}[/] [white]({pct:.1f}%)[/]")
        table.add_row(f"[bold {GOLD}]Итого / Total[/]", f"[{ICE}]{total}[/]")
        table.add_row("", "")
        table.add_row(f"[bold {GOLD}]Режим[/]", f"[{STEEL}]только чтение[/]")
        table.add_row(f"[bold {GOLD}]Кузня[/]", f"[{PURPLE_GHOST}]действия запечатаны[/]")

        self.query_one("#status_summary").update(
            Panel(
                table,
                title=f"[bold {GOLD}]Сводка печати реестра[/]",
                subtitle=f"[{ICE}]Выбрано: {ru_category(self.selected_category)}[/]",
                border_style=BURGUNDY_LIGHT,
                box=box.ROUNDED,
            )
        )

    def update_detail(self, card: dict[str, Any]) -> None:
        info = Table.grid(padding=(0, 1))
        info.add_column(style=GOLD)
        info.add_column(style=TEXT)

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
        receipt_table.add_column("time", style=ICE, width=20)
        receipt_table.add_column("file", style=TEXT)
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
        text.append(card["capability_id"] + "\n", style=f"bold {GOLD}")
        text.append(f"{CATEGORY_RU.get(card['category'], card['category'])} / {card['category']}\n\n", style=ICE)
        text.append("Плюс / Value\n", style=f"bold {GOOD}")
        for item in plus[:4]:
            text.append(f"• {item}\n", style=GOOD)
        text.append("\nРиск / Minus\n", style=f"bold {WARN}")
        for item in minus[:4]:
            text.append(f"• {item}\n", style=WARN)

        group = Table.grid(expand=True)
        group.add_row(info)
        group.add_row(Text("\nКвитанции валидации / Validation receipts", style=f"bold {GOLD}"))
        group.add_row(receipt_table)
        group.add_row(text)

        self.query_one("#detail_panel").update(
            Panel(group, title=f"[bold {GOLD}]Деталь возможности[/]", border_style=BURGUNDY_LIGHT, box=box.ROUNDED)
        )

    def update_receipts(self) -> None:
        table = Table(show_header=True, header_style=f"bold {GOLD}", expand=True, box=box.SIMPLE_HEAVY)
        table.add_column("Время", style=ICE, width=20)
        table.add_column("Тип", width=20)
        table.add_column("Субъект", style=TEXT)
        table.add_column("Статус", width=24)
        for receipt in self.receipts[:5]:
            rtype = receipt["file_name"].replace("_validation_receipt.json", "").replace(".json", "")[:20]
            table.add_row(
                receipt["time"],
                rtype,
                str(receipt["subject"])[:48],
                f"[{status_color(receipt['status'])}]{ru_status(receipt['status'])}[/]",
            )
        self.query_one("#receipt_panel").update(
            Panel(table, title=f"[bold {GOLD}]Хранилище квитанций — последняя истина[/]", border_style=BURGUNDY_LIGHT, box=box.ROUNDED)
        )

    def update_actions(self) -> None:
        table = Table.grid(expand=True)
        table.add_column()
        table.add_row(f"[bold {GOLD}]Ритуальные сокеты[/]")
        table.add_row("")
        table.add_row(f"[{STEEL}][ Validate / Валидировать ][/]   [{STEEL}][ Promote / Повысить ][/]")
        table.add_row(f"[{STEEL}][ Export Scope / Выдать scope ][/]   [{STEEL}][ Open Receipt / Открыть receipt ][/]")
        table.add_row(f"[{STEEL}][ Approve Tool / Одобрить tool ][/]   [{STEEL}][ Refresh Index / Обновить индекс ][/]")
        table.add_row("")
        table.add_row(f"[{ICE}]read-only: без записи, установок, сервера.[/]")
        table.add_row(f"[{PURPLE_GHOST}]Кнопки оживут только после Officio + Inquisition + Owner gates.[/]")
        table.add_row("")
        table.add_row(f"[bold {GOLD}]Решения Owner ожидают:[/] [{WARN}]{len(self.approvals)}[/]")
        for item in self.approvals[:5]:
            label = item.get("tool") or item.get("name") or item.get("capability_id") or item.get("question") or str(item)
            table.add_row(f"[{WARN}]• {label}[/]")
        self.query_one("#action_panel").update(
            Panel(table, title=f"[bold {GOLD}]Сокеты действий[/]", border_style=BURGUNDY_LIGHT, box=box.ROUNDED)
        )


if __name__ == "__main__":
    MechanicusForgeClientV06SoftRU().run()
