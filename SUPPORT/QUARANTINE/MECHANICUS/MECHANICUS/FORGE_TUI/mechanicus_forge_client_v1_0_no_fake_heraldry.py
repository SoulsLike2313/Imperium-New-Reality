from __future__ import annotations

from collections import Counter

from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mechanicus_forge_client_v0_6_soft_ru import (
    MechanicusForgeClientV06SoftRU,
    GOLD,
    STEEL,
    ICE,
    PURPLE_GHOST,
    BURGUNDY_LIGHT,
    GOOD,
    WARN,
    BAD,
    MUTED,
    ru_status,
)
from mechanicus_forge_client_v0_3 import evidence_metrics, git_snapshot


class MechanicusForgeClientV10NoFakeHeraldry(MechanicusForgeClientV06SoftRU):
    CSS_PATH = "forge_client_v1_0.tcss"
    TITLE = "Mechanicus Forge Client V1.0"

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

        def tile(label_ru: str, label_id: str, value: str, color: str = ICE) -> Panel:
            text = Text()
            text.append(label_ru + "\n", style=f"bold {GOLD}")
            text.append(label_id + "\n", style=MUTED)
            text.append(value, style=f"bold {color}")
            return Panel(text, border_style=BURGUNDY_LIGHT, box=box.ROUNDED, padding=(0, 1))

        tiles.add_row(
            tile("Всего карт", "TOTAL", str(len(self.cards))),
            tile("Канон", "CANON", str(counts.get("CANON", 0))),
            tile("Песочница", "SANDBOX", str(counts.get("SANDBOX", 0)), GOOD),
            tile("Кандидаты", "CANDIDATE", str(counts.get("CANDIDATE", 0)), WARN),
            tile("Дерево", "WORKTREE", ru_status(git["worktree"]), GOOD if git["worktree"] == "CLEAN" else BAD),
            tile("Синхрон", "REMOTE", git["remote_sync"], GOOD if git["remote_sync"] == "OK" else WARN),
            tile("Индекс", "EVIDENCE", f"{metrics['records']} записей", ICE),
            tile("Решения", "OWNER", f"{len(self.approvals)} ожидают", WARN if self.approvals else GOOD),
            tile("Head", "GIT", git["head"], ICE),
        )

        title = Text()
        title.append("⚙ ", style=PURPLE_GHOST)
        title.append("Mechanicus Forge Client V1.0", style=f"bold {GOLD}")
        title.append("  ::  ", style=BURGUNDY_LIGHT)
        title.append("честный read-only TUI без фейковых гербов", style=f"bold {ICE}")
        title.append("  ::  ", style=BURGUNDY_LIGHT)
        title.append("реестр арсенала", style=f"bold {GOLD}")
        title.append(" ☩", style=PURPLE_GHOST)

        machine = Text()
        machine.append("Дух машины: ", style=f"bold {PURPLE_GHOST}")
        machine.append("стабилен" if git["worktree"] == "CLEAN" else "требует внимания", style=f"bold {GOOD if git['worktree'] == 'CLEAN' else WARN}")
        machine.append("  │  ", style=BURGUNDY_LIGHT)
        machine.append("read-only", style=f"bold {STEEL}")
        machine.append("  │  ", style=BURGUNDY_LIGHT)
        machine.append(f"песочница {counts.get('SANDBOX', 0)}", style=f"bold {GOOD}")
        machine.append("  │  ", style=BURGUNDY_LIGHT)
        machine.append(f"кандидаты {counts.get('CANDIDATE', 0)}", style=f"bold {WARN}")
        machine.append("  │  ", style=BURGUNDY_LIGHT)
        machine.append(f"решения owner {len(self.approvals)}", style=f"bold {WARN if self.approvals else GOOD}")

        no_fake = Text()
        no_fake.append("Геральдика отключена в чистом TUI: ", style=f"bold {GOLD}")
        no_fake.append("плохие pseudo-heraldry рисунки удалены. ", style=STEEL)
        no_fake.append("Настоящие гербы — только future enhanced/web/image-capable mode поверх той же truth-модели.", style=PURPLE_GHOST)

        badge_line = Table.grid(expand=True)
        badge_line.add_column(ratio=1)
        badge_line.add_column(ratio=5)
        badge_line.add_column(ratio=1)
        badge_line.add_row(
            Panel(Text("⚙\nMECHANICUS", style=f"bold {ICE}", justify="center"), border_style=BURGUNDY_LIGHT, box=box.ROUNDED),
            Align.center(title),
            Panel(Text("☩\nIMPERIUM", style=f"bold {ICE}", justify="center"), border_style=BURGUNDY_LIGHT, box=box.ROUNDED),
        )

        group = Group(
            badge_line,
            Text(""),
            tiles,
            Text(""),
            Align.center(machine),
            Align.center(no_fake),
        )

        panel = Panel(
            group,
            title=f"[bold {GOLD}]Главная машинная панель[/]",
            subtitle=f"[{ICE}]Внутри агента | read-only | {git['snapshot']}[/]",
            border_style=BURGUNDY_LIGHT,
            box=box.DOUBLE,
            padding=(0, 1),
        )

        self.query_one("#truth_strip").update(panel)


if __name__ == "__main__":
    MechanicusForgeClientV10NoFakeHeraldry().run()
