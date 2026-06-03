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
    VIOLET,
    PURPLE_GHOST,
    BURGUNDY_LIGHT,
    GOOD,
    WARN,
    BAD,
    MUTED,
    ru_status,
)
from mechanicus_forge_client_v0_3 import evidence_metrics, git_snapshot


MECH_HERALDRY = r"""
        ╔═╦═╗
     ╔══╣◉║◉╠══╗
     ║╔═╩═╬═╩═╗║
  ╔══╬╣  ╔╩╗  ╠╬══╗
  ║  ║║ ╔╣ ╠╗ ║║  ║
  ╚══╬╣ ╚╣ ╠╝ ╠╬══╝
     ║╚═╗╚╦╝╔═╝║
     ╚══╝ ║ ╚══╝
          ║
     ⚙ МЕХАНИКУС ⚙
"""

IMPERIUM_HERALDRY = r"""
        ╔═╗   ╔═╗
     ╔══╣╬╚═══╝╬╠══╗
     ║╔═╩╗ ╔═╗ ╔╩═╗║
  ╔══╣║  ╚═╣ ╠═╝  ║╠══╗
  ║  ║║  ╔═╣ ╠═╗  ║║  ║
  ╚══╣║ ╔╝ ║ ║ ╚╗ ║╠══╝
     ║╚═╝  ║ ║  ╚═╝║
     ╚═════╝ ╚═════╝
         ☩ ИМПЕРИУМ ☩
"""


class MechanicusForgeClientV07Heraldry(MechanicusForgeClientV06SoftRU):
    CSS_PATH = "forge_client_v0_7.tcss"
    TITLE = "Mechanicus Forge Client V0.7 Heraldry"

    def update_truth_strip(self) -> None:
        git = git_snapshot()
        counts = Counter(card["status"] for card in self.cards)
        metrics = evidence_metrics()

        def tile(label_ru: str, label_id: str, value: str, color: str = ICE) -> Panel:
            text = Text()
            text.append(label_ru + "\n", style=f"bold {GOLD}")
            text.append(label_id + "\n", style=MUTED)
            text.append(value, style=f"bold {color}")
            return Panel(text, border_style=BURGUNDY_LIGHT, box=box.ROUNDED, padding=(0, 1))

        tiles = Table.grid(expand=True)
        for _ in range(9):
            tiles.add_column(ratio=1)

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
        title.append("Mechanicus Forge Client V0.7", style=f"bold {ICE}")
        title.append("  ::  ", style=BURGUNDY_LIGHT)
        title.append("Реестр арсенала", style=f"bold {GOLD}")
        title.append("  ::  ", style=BURGUNDY_LIGHT)
        title.append("Геральдический слой", style=f"bold {STEEL}")
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
        whisper.append("ANSI / block-art heraldry", style=f"italic {PURPLE_GHOST}")
        whisper.append(" встроена в верхний strip как отдельные модульные поверхности.", style=STEEL)

        center_group = Group(
            Align.center(title),
            Text(""),
            tiles,
            Text(""),
            Align.center(machine),
            Align.center(whisper),
        )

        left_panel = Panel(
            Text(MECH_HERALDRY, style=ICE, justify="center"),
            title=f"[bold {GOLD}]Герб Механикус[/]",
            border_style=BURGUNDY_LIGHT,
            box=box.ROUNDED,
            padding=(0, 1),
        )

        center_panel = Panel(
            center_group,
            title=f"[bold {GOLD}]Главный ритуальный strip[/]",
            subtitle=f"[{ICE}]Внутри агента  |  read-only  |  {git['snapshot']}[/]",
            border_style=BURGUNDY_LIGHT,
            box=box.DOUBLE,
            padding=(0, 1),
        )

        right_panel = Panel(
            Text(IMPERIUM_HERALDRY, style=ICE, justify="center"),
            title=f"[bold {GOLD}]Герб Империума[/]",
            border_style=BURGUNDY_LIGHT,
            box=box.ROUNDED,
            padding=(0, 1),
        )

        layout = Table.grid(expand=True)
        layout.add_column(ratio=2)
        layout.add_column(ratio=7)
        layout.add_column(ratio=2)
        layout.add_row(left_panel, center_panel, right_panel)

        self.query_one("#truth_strip").update(layout)


if __name__ == "__main__":
    MechanicusForgeClientV07Heraldry().run()
