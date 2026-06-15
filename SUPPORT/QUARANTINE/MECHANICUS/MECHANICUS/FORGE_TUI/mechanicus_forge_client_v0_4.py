from __future__ import annotations

from collections import Counter

from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mechanicus_forge_client_v0_3 import (
    MechanicusForgeClient,
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


class MechanicusForgeClientV04(MechanicusForgeClient):
    CSS_PATH = "forge_client_v0_4.tcss"
    TITLE = "Mechanicus Forge Client V0.4"

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

        def tile(label: str, value: str, color: str = CYAN) -> Panel:
            text = Text()
            text.append(label + "\n", style=f"bold {BRASS}")
            text.append(value, style=f"bold {color}")
            return Panel(text, border_style="#51402d", box=box.ROUNDED, padding=(0, 1))

        tiles.add_row(
            tile("TOTAL CARDS", str(len(self.cards))),
            tile("CANON", str(counts.get("CANON", 0))),
            tile("SANDBOX", str(counts.get("SANDBOX", 0)), GREEN),
            tile("CANDIDATE", str(counts.get("CANDIDATE", 0)), AMBER),
            tile("WORKTREE", git["worktree"], GREEN if git["worktree"] == "CLEAN" else RED),
            tile("REMOTE SYNC", git["remote_sync"], GREEN if git["remote_sync"] == "OK" else AMBER),
            tile("EVIDENCE INDEX", f"{metrics['records']} records"),
            tile("OWNER RITES", f"{len(self.approvals)} pending", AMBER if self.approvals else GREEN),
            tile("HEAD", git["head"]),
        )

        sigil = Text()
        sigil.append("<< ", style=COPPER)
        sigil.append("OMNISSIAH READ-ONLY RITE", style=f"bold {BRASS}")
        sigil.append(" :: ", style=COPPER)
        sigil.append("MECHANICUS FORGE CLIENT V0.4", style=f"bold {CYAN}")
        sigil.append(" :: ", style=COPPER)
        sigil.append("ARSENAL REGISTRY SURFACE", style=f"bold {BRASS}")
        sigil.append(" >>", style=COPPER)

        machine_spirit = Text()
        if git["worktree"] == "CLEAN":
            machine_spirit.append("MACHINE SPIRIT: STABLE", style=f"bold {GREEN}")
        else:
            machine_spirit.append("MACHINE SPIRIT: ATTENTION REQUIRED", style=f"bold {AMBER}")
        machine_spirit.append("  |  ")
        machine_spirit.append("NO WRITE RITES", style=f"bold {CYAN}")
        machine_spirit.append("  |  ")
        machine_spirit.append(f"SANDBOX {counts.get('SANDBOX', 0)}", style=f"bold {GREEN}")
        machine_spirit.append("  |  ")
        machine_spirit.append(f"CANDIDATE {counts.get('CANDIDATE', 0)}", style=f"bold {AMBER}")
        machine_spirit.append("  |  ")
        machine_spirit.append(f"OWNER APPROVALS {len(self.approvals)}", style=f"bold {AMBER if self.approvals else GREEN}")

        group = Group(
            Align.center(sigil),
            Text(""),
            tiles,
            Text(""),
            Align.center(machine_spirit),
            Align.center(Text("All surfaces are modular. Action sockets are sealed until future write-mode gates.", style=CYAN)),
        )

        panel = Panel(
            group,
            subtitle=f"[cyan]INSIDE AGENT CLIENT | READ-ONLY | {git['snapshot']}[/]",
            border_style=COPPER,
            box=box.DOUBLE,
            padding=(0, 1),
        )
        self.query_one("#truth_strip").update(panel)

    def update_folder_tree(self) -> None:
        tree = self.query_one("#folder_tree")
        tree.clear()
        root = tree.root
        root.set_label("++ FORGE CHAMBERS / FRESHNESS ++")
        for row in folder_freshness():
            status = "OK" if row["exists"] == "YES" else "MISS"
            glyph = "[OK]" if status == "OK" else "[!!]"
            root.add_leaf(f"{glyph} {row['path']} | {row['files']} files | {status} | {row['fresh']}", data=row["path"])
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
                table.add_row(f"[{status_color(key)}]{key}[/]", f"[cyan]{val}[/] [white]({pct:.1f}%)[/]")

        table.add_row(f"[bold {BRASS}]TOTAL[/]", f"[cyan]{total}[/]")
        table.add_row("", "")
        table.add_row(f"[bold {BRASS}]RITE[/]", "[cyan]READ ONLY[/]")
        table.add_row(f"[bold {BRASS}]FORGE[/]", "[cyan]ACTIONS SEALED[/]")

        self.query_one("#status_summary").update(
            Panel(
                table,
                title=f"[bold {BRASS}]REGISTRY SEAL SUMMARY[/]",
                subtitle=f"[cyan]Selected chamber: {self.selected_category}[/]",
                border_style=COPPER,
                box=box.DOUBLE,
            )
        )

    def update_actions(self) -> None:
        table = Table.grid(expand=True)
        table.add_column()
        table.add_row(f"[bold {BRASS}]SEALED ACTION SOCKETS[/]")
        table.add_row("")
        table.add_row("[white][ Validate ][/]   [white][ Promote ][/]   [white][ Export Scope ][/]   [white][ Open Receipt ][/]")
        table.add_row("[white][ Approve Tool ][/]   [white][ Refresh Index ][/]   [white][ Open Chamber ][/]")
        table.add_row("")
        table.add_row("[cyan]READ-ONLY RITE: no writes, no installs, no server.[/]")
        table.add_row("[cyan]Buttons will awaken only after Officio + Inquisition + Owner gates.[/]")
        table.add_row("")
        table.add_row(f"[bold {BRASS}]Owner approval rites pending:[/] [yellow]{len(self.approvals)}[/]")
        for item in self.approvals[:5]:
            label = item.get("tool") or item.get("name") or item.get("capability_id") or item.get("question") or str(item)
            table.add_row(f"[yellow]• {label}[/]")
        self.query_one("#action_panel").update(
            Panel(table, title=f"[bold {BRASS}]RITE SOCKETS[/]", border_style=COPPER, box=box.DOUBLE)
        )


if __name__ == "__main__":
    MechanicusForgeClientV04().run()
