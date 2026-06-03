from __future__ import annotations

from collections import Counter
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mechanicus_forge_client_v0_6_soft_ru import (
    MechanicusForgeClientV06SoftRU,
    ru_status,
    ru_category,
    ru_folder,
    short,
    CATEGORY_RU,
    FIELD_RU,
)
from mechanicus_forge_client_v0_3 import evidence_metrics, folder_freshness, git_snapshot, status_color


# Palette: steampunk forge, but terminal-safe.
BRASS = "#d0a85a"
GOLD = "#e1c27a"
BRONZE = "#a36b32"
IRON = "#36312b"
DARK_IRON = "#050505"
BURGUNDY = "#5a1222"
BURGUNDY_EDGE = "#8d2440"
ICE = "#a8d8ff"
STEEL = "#b7c0cb"
VIOLET = "#a071ff"
DIM = "#8f8790"
GOOD = "#9ad66b"
WARN = "#e0a340"
BAD = "#ff6384"
WHITE = "#ddd4c6"


MECHANICUS_SIGIL = [
    "      ╭─────⚙─────╮",
    "   ╭──┤  ◐  │  ◑  ├──╮",
    "   │  │  skull/machine │",
    "   │  ╰───╥───╥───╯  │",
    "   ╰──────╨───╨──────╯",
    "       MECHANICUS",
]

IMPERIUM_SIGIL = [
    "      ╭─────☩─────╮",
    "   ╭──╯╲   │   ╱╰──╮",
    "   │  winged aquila  │",
    "   ╰──╮╱   │   ╲╭──╯",
    "      ╰─────┴─────╯",
    "        IMPERIUM",
]


def color_for_status(value: str) -> str:
    s = str(value).upper()
    if s in {"PASS", "OK", "CLEAN", "SANDBOX", "ACTIVE"}:
        return GOOD
    if s in {"CANDIDATE", "PASS_WITH_WARNINGS", "WARN", "PENDING", "OWNER_APPROVAL_REQUIRED"}:
        return WARN
    if s in {"FAIL", "DIRTY", "BLOCKED", "QUARANTINE", "QUARANTINED"}:
        return BAD
    return ICE


def steampunk_panel(renderable, *, title: str = "", subtitle: str = "", heavy: bool = False, pad=(0, 1)) -> Panel:
    return Panel(
        renderable,
        title=f"[bold {GOLD}]{title}[/]" if title else "",
        subtitle=f"[{ICE}]{subtitle}[/]" if subtitle else "",
        border_style=BRONZE if heavy else BURGUNDY_EDGE,
        box=box.DOUBLE if heavy else box.ROUNDED,
        padding=pad,
    )


def brass_tile(label_ru: str, label_id: str, value: str, color: str = ICE) -> Panel:
    text = Text()
    text.append(label_ru + "\n", style=f"bold {GOLD}")
    text.append(label_id + "\n", style=DIM)
    text.append(value, style=f"bold {color}")
    return Panel(
        text,
        border_style=BRONZE,
        box=box.ROUNDED,
        padding=(0, 1),
    )


def small_sigil(lines: list[str], title: str, glow: str = VIOLET) -> Panel:
    body = Text()
    for idx, line in enumerate(lines):
        style = ICE if idx < len(lines) - 1 else f"bold {GOLD}"
        body.append(line + "\n", style=style)
    body.append("  • ", style=BRONZE)
    body.append(title, style=f"bold {glow}")
    body.append(" •", style=BRONZE)
    return steampunk_panel(Align.center(body), title="", heavy=True, pad=(0, 1))


class MechanicusForgeClientV09Steampunk(MechanicusForgeClientV06SoftRU):
    CSS_PATH = "forge_client_v0_9.tcss"
    TITLE = "Mechanicus Forge Client V0.9 Steampunk"

    def on_mount(self) -> None:
        super().on_mount()
        self.selected_category = "TOOLS"
        self.reload_all()

    def update_truth_strip(self) -> None:
        git = git_snapshot()
        counts = Counter(card["status"] for card in self.cards)
        metrics = evidence_metrics()

        tiles = Table.grid(expand=True)
        for _ in range(9):
            tiles.add_column(ratio=1)

        tiles.add_row(
            brass_tile("Всего карт", "TOTAL", str(len(self.cards))),
            brass_tile("Канон", "CANON", str(counts.get("CANON", 0))),
            brass_tile("Песочница", "SANDBOX", str(counts.get("SANDBOX", 0)), GOOD),
            brass_tile("Кандидаты", "CANDIDATE", str(counts.get("CANDIDATE", 0)), WARN),
            brass_tile("Дерево", "WORKTREE", ru_status(git["worktree"]), color_for_status(git["worktree"])),
            brass_tile("Синхрон", "REMOTE", git["remote_sync"], color_for_status(git["remote_sync"])),
            brass_tile("Индекс", "EVIDENCE", f"{metrics['records']} записей", ICE),
            brass_tile("Решения", "OWNER", f"{len(self.approvals)} ожидают", WARN if self.approvals else GOOD),
            brass_tile("Head", "GIT", git["head"], ICE),
        )

        title = Text()
        title.append("╼╼ ", style=BRONZE)
        title.append("MECHANICUS FORGE CLIENT V0.9", style=f"bold {GOLD}")
        title.append("  ::  ", style=BURGUNDY_EDGE)
        title.append("steampunk read-only registry", style=f"bold {ICE}")
        title.append("  ::  ", style=BURGUNDY_EDGE)
        title.append("реестр арсенала", style=f"bold {GOLD}")
        title.append(" ╾╾", style=BRONZE)

        spirit = Text()
        spirit.append("Дух машины: ", style=f"bold {VIOLET}")
        spirit.append("стабилен" if git["worktree"] == "CLEAN" else "требует внимания", style=f"bold {GOOD if git['worktree'] == 'CLEAN' else WARN}")
        spirit.append("  │  ", style=BRONZE)
        spirit.append("read-only", style=f"bold {STEEL}")
        spirit.append("  │  ", style=BRONZE)
        spirit.append("декоративные печати", style=f"bold {BRASS}")
        spirit.append("  │  ", style=BRONZE)
        spirit.append("action sockets sealed", style=f"bold {ICE}")

        note = Text()
        note.append("Цель V0.9: приблизить TUI к forge-console без bitmap/texture dependencies. ", style=STEEL)
        note.append("Печати — terminal-native, настоящие графические гербы будут только в enhanced/web mode.", style=VIOLET)

        middle = Group(
            Align.center(title),
            Text(""),
            tiles,
            Text(""),
            Align.center(spirit),
            Align.center(note),
        )

        grid = Table.grid(expand=True)
        grid.add_column(ratio=2)
        grid.add_column(ratio=8)
        grid.add_column(ratio=2)
        grid.add_row(
            small_sigil(MECHANICUS_SIGIL, "COG / SKULL SEAL"),
            steampunk_panel(
                middle,
                title="Главная машинная панель",
                subtitle=f"Внутри агента | read-only | {git['snapshot']}",
                heavy=True,
            ),
            small_sigil(IMPERIUM_SIGIL, "AQUILA SEAL"),
        )
        self.query_one("#truth_strip").update(grid)

    def update_category_tree(self) -> None:
        tree = self.query_one("#category_tree")
        tree.clear()
        counts = Counter(card["category"] for card in self.cards)
        root = tree.root
        root.set_label(f"◆ Все категории / ALL ({len(self.cards)})")
        root.data = "ALL"
        for cat, count in sorted(counts.items()):
            label = f"{ru_category(cat)} ({count})"
            node = root.add_leaf(label, data=cat)
            if cat == self.selected_category:
                node.set_label(f"◆ {label}")
        root.expand()

    def update_folder_tree(self) -> None:
        tree = self.query_one("#folder_tree")
        tree.clear()
        root = tree.root
        root.set_label("◆ Камеры Механикуса / свежесть")
        for row in folder_freshness():
            status = "OK" if row["exists"] == "YES" else "MISS"
            glyph = "✓" if status == "OK" else "!"
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
                table.add_row(f"[{color_for_status(key)}]{ru_status(key)}[/]", f"[{ICE}]{val}[/] [white]({pct:.1f}%)[/]")
        table.add_row(f"[bold {GOLD}]Итого / Total[/]", f"[{ICE}]{total}[/]")
        table.add_row("", "")
        table.add_row(f"[bold {GOLD}]Режим[/]", f"[{STEEL}]только чтение[/]")
        table.add_row(f"[bold {GOLD}]Кузня[/]", f"[{VIOLET}]действия запечатаны[/]")

        self.query_one("#status_summary").update(
            steampunk_panel(
                table,
                title="Сводка печати реестра",
                subtitle=f"Выбрано: {ru_category(self.selected_category)}",
                heavy=False,
            )
        )

    def update_detail(self, card: dict[str, Any]) -> None:
        info = Table.grid(padding=(0, 1))
        info.add_column(style=GOLD)
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
        receipt_table.add_column("time", style=ICE, width=20)
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
            steampunk_panel(group, title="Деталь возможности", heavy=False)
        )

    def update_receipts(self) -> None:
        table = Table(show_header=True, header_style=f"bold {GOLD}", expand=True, box=box.SIMPLE_HEAVY)
        table.add_column("Время", style=ICE, width=20)
        table.add_column("Тип", width=20)
        table.add_column("Субъект", style=WHITE)
        table.add_column("Статус", width=24)
        for receipt in self.receipts[:5]:
            rtype = receipt["file_name"].replace("_validation_receipt.json", "").replace(".json", "")[:20]
            table.add_row(
                receipt["time"],
                rtype,
                str(receipt["subject"])[:48],
                f"[{color_for_status(receipt['status'])}]{ru_status(receipt['status'])}[/]",
            )
        self.query_one("#receipt_panel").update(
            steampunk_panel(table, title="Хранилище квитанций — последняя истина", heavy=False)
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
        table.add_row(f"[{VIOLET}]Кнопки оживут только после Officio + Inquisition + Owner gates.[/]")
        table.add_row("")
        table.add_row(f"[bold {GOLD}]Решения Owner ожидают:[/] [{WARN}]{len(self.approvals)}[/]")
        for item in self.approvals[:5]:
            label = item.get("tool") or item.get("name") or item.get("capability_id") or item.get("question") or str(item)
            table.add_row(f"[{WARN}]• {label}[/]")
        self.query_one("#action_panel").update(
            steampunk_panel(table, title="Сокеты действий", heavy=False)
        )


if __name__ == "__main__":
    MechanicusForgeClientV09Steampunk().run()
