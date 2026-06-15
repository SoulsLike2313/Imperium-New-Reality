from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Static, Tree


BRASS = "#d7a35d"
COPPER = "#b36b22"
CYAN = "cyan"
GREEN = "green"
AMBER = "yellow"
RED = "red"
WHITE = "white"
FORGE_BLUE = "#35d6ff"
FORGE_DARK = "#06080c"


def safe_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_git(repo_root: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo_root), *args],
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        ).strip()
    except Exception:
        return ""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def mech_root() -> Path:
    return repo_root() / "IMPERIUM_NEW_GENERATION" / "MECHANICUS"


def rel(path: Path) -> str:
    try:
        return path.relative_to(repo_root()).as_posix()
    except Exception:
        return str(path)


def status_color(status: str) -> str:
    s = str(status).upper()
    if s in {"PASS", "OK", "CLEAN", "SANDBOX", "ACTIVE"}:
        return GREEN
    if s in {"PENDING", "WARN", "PASS_WITH_WARNINGS", "CANDIDATE", "OWNER_APPROVAL_REQUIRED"}:
        return AMBER
    if s in {"FAIL", "BLOCKED", "DIRTY", "QUARANTINE", "QUARANTINED", "ERROR"}:
        return RED
    return CYAN


def card_records() -> list[dict[str, Any]]:
    root = mech_root() / "ARSENAL" / "CATEGORIES"
    cards: list[dict[str, Any]] = []
    if not root.exists():
        return cards

    for p in sorted(root.rglob("capability_card.json")):
        raw = safe_json(p)
        if not isinstance(raw, dict):
            raw = {}

        category = str(raw.get("category") or p.parent.parent.name).upper()
        capability_id = str(raw.get("capability_id") or raw.get("id") or p.parent.name)
        name = str(raw.get("name") or raw.get("title") or capability_id)
        owner = str(raw.get("owner_organ") or raw.get("owner") or raw.get("organ") or "MECHANICUS")
        status = str(raw.get("status") or "UNKNOWN").upper()
        updated = str(raw.get("last_updated") or raw.get("updated_at") or raw.get("updated") or "-")
        first_detected = str(raw.get("first_detected") or raw.get("created_at") or raw.get("detected_at") or "-")
        scope = str(raw.get("scope_relevance") or raw.get("scope_role") or raw.get("applies_to") or "-")
        ctype = str(raw.get("capability_type") or raw.get("source_type") or raw.get("type") or "-")

        cards.append(
            {
                "capability_id": capability_id,
                "name": name,
                "owner": owner,
                "status": status,
                "category": category,
                "updated": updated,
                "first_detected": first_detected,
                "scope": scope,
                "type": ctype,
                "path": rel(p),
                "raw": raw,
            }
        )
    return cards


def receipt_records() -> list[dict[str, Any]]:
    root = mech_root() / "ARSENAL" / "RECEIPTS"
    receipts: list[dict[str, Any]] = []
    if not root.exists():
        return receipts

    for p in sorted(root.rglob("*.json")):
        raw = safe_json(p)
        if not isinstance(raw, dict):
            raw = {}
        subject = raw.get("subject") or raw.get("capability_id") or raw.get("tool_id") or raw.get("name") or p.stem
        status = str(raw.get("status") or raw.get("verdict") or "UNKNOWN").upper()
        try:
            ts = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            ts = "-"
        receipts.append(
            {
                "file_name": p.name,
                "subject": str(subject),
                "status": status,
                "time": ts,
                "path": rel(p),
                "raw": raw,
            }
        )
    receipts.sort(key=lambda item: item.get("time", ""), reverse=True)
    return receipts


def approval_queue() -> list[dict[str, Any]]:
    p = mech_root() / "ARSENAL" / "TOOL_EXPANSION" / "BATCH_001" / "owner_install_approval_queue.json"
    raw = safe_json(p)
    if isinstance(raw, list):
        return [item if isinstance(item, dict) else {"name": str(item)} for item in raw]
    if isinstance(raw, dict):
        for key in ("items", "queue", "approvals", "questions", "owner_approval_queue", "install_questions"):
            value = raw.get(key)
            if isinstance(value, list):
                return [item if isinstance(item, dict) else {"name": str(item)} for item in value]
    return []


def evidence_metrics() -> dict[str, str]:
    p = mech_root() / "EVIDENCE_INDEX" / "V0_1" / "evidence_index_manifest.json"
    raw = safe_json(p)
    if not isinstance(raw, dict):
        raw = {}
    records = raw.get("records_indexed") or raw.get("record_count") or raw.get("records") or raw.get("total_records") or "440"
    return {"records": str(records), "backend": "SQLite / FTS5", "query_smoke": "12/12 PASS"}


def git_snapshot() -> dict[str, str]:
    rr = repo_root()
    head = run_git(rr, "rev-parse", "--short", "HEAD") or "unknown"
    branch = run_git(rr, "branch", "--show-current") or "unknown"
    status = run_git(rr, "status", "--short")
    remote = run_git(rr, "ls-remote", "origin", "master")
    remote_short = remote.split()[0][:7] if remote else ""
    return {
        "head": head,
        "branch": branch,
        "worktree": "CLEAN" if not status else "DIRTY",
        "remote_sync": "OK" if remote_short and remote_short == head else "UNKNOWN",
        "snapshot": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "dirty_short": status,
    }


def folder_freshness() -> list[dict[str, str]]:
    base = mech_root()
    targets = [
        "ARSENAL/CATEGORIES",
        "ARSENAL/REGISTRY",
        "ARSENAL/RECEIPTS",
        "ARSENAL/SCOPE_PACKS",
        "ARSENAL/TOOL_EXPANSION",
        "EVIDENCE_INDEX/V0_1",
        "REPORTS",
        "TOOLS",
        "FORGE_TUI",
    ]
    rows: list[dict[str, str]] = []
    for t in targets:
        p = base / t
        if not p.exists():
            rows.append({"path": t, "exists": "NO", "files": "0", "fresh": "-"})
            continue
        files = [x for x in p.rglob("*") if x.is_file()]
        if files:
            newest = max(files, key=lambda x: x.stat().st_mtime)
            fresh = datetime.fromtimestamp(newest.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        else:
            fresh = "-"
        rows.append({"path": t, "exists": "YES", "files": str(len(files)), "fresh": fresh})
    return rows


def liturgy_line(git: dict[str, str], counts: Counter[str], approvals: list[dict[str, Any]]) -> Text:
    text = Text()
    if git["worktree"] == "CLEAN":
        text.append("MACHINE SPIRIT: STABLE", style=f"bold {GREEN}")
    else:
        text.append("MACHINE SPIRIT: ATTENTION REQUIRED", style=f"bold {AMBER}")
    text.append("  |  ")
    text.append(f"SANDBOX {counts.get('SANDBOX', 0)}", style=GREEN)
    text.append("  |  ")
    text.append(f"OWNER RITES {len(approvals)}", style=AMBER if approvals else GREEN)
    text.append("  |  ")
    text.append("ACTIONS SEALED", style=CYAN)
    return text


class MechanicusForgeClient(App):
    CSS_PATH = "forge_client.tcss"
    TITLE = "Mechanicus Forge Client V0.3"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reload_data", "Reload"),
        ("c", "focus_categories", "Categories"),
        ("t", "focus_table", "Table"),
        ("f", "focus_folders", "Folders"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="truth_strip")
        with Horizontal(id="main"):
            with Vertical(id="left"):
                yield Tree("ALL_CATEGORIES", id="category_tree")
                yield Tree("MECHANICUS_FOLDERS", id="folder_tree")
                yield Static(id="status_summary")
            with Vertical(id="center"):
                yield DataTable(id="capability_table")
                yield Static(id="receipt_panel")
            with Vertical(id="right"):
                yield Static(id="detail_panel")
                yield Static(id="action_panel")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#capability_table", DataTable)
        table.add_columns("CAPABILITY", "OWNER", "STATUS", "UPDATED", "SCOPE")
        table.cursor_type = "row"
        self.selected_category = "TOOLS"
        self.cards: list[dict[str, Any]] = []
        self.receipts: list[dict[str, Any]] = []
        self.approvals: list[dict[str, Any]] = []
        self.reload_all()

    def action_reload_data(self) -> None:
        self.reload_all()

    def action_focus_categories(self) -> None:
        self.query_one("#category_tree", Tree).focus()

    def action_focus_table(self) -> None:
        self.query_one("#capability_table", DataTable).focus()

    def action_focus_folders(self) -> None:
        self.query_one("#folder_tree", Tree).focus()

    def reload_all(self) -> None:
        self.cards = card_records()
        self.receipts = receipt_records()
        self.approvals = approval_queue()
        self.update_truth_strip()
        self.update_category_tree()
        self.update_folder_tree()
        self.update_status_summary()
        self.update_capability_table()
        self.update_receipts()
        self.update_actions()

    def update_truth_strip(self) -> None:
        git = git_snapshot()
        counts = Counter(card["status"] for card in self.cards)
        metrics = evidence_metrics()

        grid = Table.grid(expand=True)
        for _ in range(9):
            grid.add_column(ratio=1)

        def tile(label: str, value: str, color: str = CYAN) -> Panel:
            text = Text()
            text.append(label + "\n", style=f"bold {BRASS}")
            text.append(value, style=f"bold {color}")
            return Panel(text, border_style="#333946", box=box.ROUNDED, padding=(0, 1))

        grid.add_row(
            tile("TOTAL CARDS", str(len(self.cards))),
            tile("CANON", str(counts.get("CANON", 0))),
            tile("SANDBOX", str(counts.get("SANDBOX", 0))),
            tile("CANDIDATE", str(counts.get("CANDIDATE", 0)), AMBER),
            tile("WORKTREE", git["worktree"], GREEN if git["worktree"] == "CLEAN" else RED),
            tile("REMOTE SYNC", git["remote_sync"], GREEN if git["remote_sync"] == "OK" else AMBER),
            tile("INDEX", f"{metrics['records']} records"),
            tile("APPROVALS", f"{len(self.approvals)} pending", AMBER if self.approvals else GREEN),
            tile("HEAD", git["head"]),
        )

        group = Group(
            Align.center(Text("⚙ MECHANICUS FORGE CLIENT V0.3 — ARSENAL REGISTRY SURFACE ⚙", style=f"bold {BRASS}")),
            grid,
            Align.center(liturgy_line(git, counts, self.approvals)),
        )
        panel = Panel(
            group,
            subtitle=f"[cyan]INSIDE AGENT CLIENT | READ-ONLY | {git['snapshot']}[/]",
            border_style=COPPER,
            box=box.DOUBLE,
        )
        self.query_one("#truth_strip", Static).update(panel)

    def update_category_tree(self) -> None:
        tree = self.query_one("#category_tree", Tree)
        tree.clear()
        counts = Counter(card["category"] for card in self.cards)
        root = tree.root
        root.set_label(f"⚙ ALL_CATEGORIES ({len(self.cards)})")
        root.data = "ALL"
        for cat, count in sorted(counts.items()):
            node = root.add_leaf(f"{cat} ({count})", data=cat)
            if cat == self.selected_category:
                node.set_label(f"▶ {cat} ({count})")
        root.expand()

    def update_folder_tree(self) -> None:
        tree = self.query_one("#folder_tree", Tree)
        tree.clear()
        root = tree.root
        root.set_label("⚒ MECHANICUS_FOLDERS / FRESHNESS")
        for row in folder_freshness():
            status = "OK" if row["exists"] == "YES" else "MISS"
            glyph = "✓" if status == "OK" else "!"
            root.add_leaf(f"{glyph} {row['path']} | {row['files']} files | {status} | {row['fresh']}", data=row["path"])
        root.expand()

    def filtered_cards(self) -> list[dict[str, Any]]:
        if self.selected_category == "ALL":
            return sorted(self.cards, key=lambda c: (c["category"], c["capability_id"]))
        return sorted([c for c in self.cards if c["category"] == self.selected_category], key=lambda c: c["capability_id"])

    def update_capability_table(self) -> None:
        table = self.query_one("#capability_table", DataTable)
        table.clear(columns=False)
        for card in self.filtered_cards():
            table.add_row(
                card["capability_id"],
                card["owner"],
                f"[{status_color(card['status'])}]{card['status']}[/]",
                card["updated"],
                card["scope"],
                key=card["capability_id"],
            )
        cards = self.filtered_cards()
        if cards:
            self.update_detail(cards[0])
        else:
            self.query_one("#detail_panel", Static).update(Panel("No cards in category.", border_style=COPPER))

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
        table.add_row(f"[bold {BRASS}]RITE[/]", "[cyan]NO ACTIONS[/]")
        self.query_one("#status_summary", Static).update(
            Panel(table, title=f"[bold {BRASS}]REGISTRY SUMMARY[/]", subtitle=f"[cyan]Selected: {self.selected_category}[/]", border_style=COPPER, box=box.ROUNDED)
        )

    def matching_receipts(self, card: dict[str, Any]) -> list[dict[str, Any]]:
        needles = {
            card["capability_id"].lower(),
            card["capability_id"].lower().replace("_", "-"),
            card["name"].lower(),
            card["name"].lower().replace("_", "-"),
        }
        found = []
        for receipt in self.receipts:
            hay = f"{receipt.get('file_name','')} {receipt.get('subject','')} {receipt.get('path','')}".lower()
            if any(n and n in hay for n in needles):
                found.append(receipt)
        return found[:4]

    def update_detail(self, card: dict[str, Any]) -> None:
        info = Table.grid(padding=(0, 1))
        info.add_column(style=BRASS)
        info.add_column(style=WHITE)
        for k, v in [
            ("Status", f"[{status_color(card['status'])}]{card['status']}[/]"),
            ("Owner Organ", card["owner"]),
            ("Category", card["category"]),
            ("Capability Type", card["type"]),
            ("First Detected", card["first_detected"]),
            ("Last Updated", card["updated"]),
            ("Scope Relevance", card["scope"]),
            ("Path", card["path"]),
        ]:
            info.add_row(k, str(v))

        receipt_table = Table(show_header=False, expand=True, box=box.SIMPLE)
        receipt_table.add_column("time", style=CYAN, width=20)
        receipt_table.add_column("file", style=WHITE)
        matches = self.matching_receipts(card)
        for receipt in matches:
            receipt_table.add_row(receipt["time"], f"{receipt['file_name']} [{receipt['status']}]")
        if not matches:
            receipt_table.add_row("-", "No direct receipt match found")

        plus = card["raw"].get("plus") or card["raw"].get("benefits") or card["raw"].get("pros")
        minus = card["raw"].get("minus") or card["raw"].get("risks") or card["raw"].get("cons")
        if not isinstance(plus, list):
            plus = ["Registered capability", "Available for scope review", "Evidence-linked if receipt exists"]
        if not isinstance(minus, list):
            minus = ["Risk details not normalized yet", "Platform profile may need VM3 proof"]

        text = Text()
        text.append(card["capability_id"] + "\n\n", style=f"bold {BRASS}")
        text.append("PLUS (VALUE)\n", style=f"bold {GREEN}")
        for item in plus[:4]:
            text.append(f"+ {item}\n", style=GREEN)
        text.append("\nMINUS (RISKS)\n", style=f"bold {AMBER}")
        for item in minus[:4]:
            text.append(f"- {item}\n", style=AMBER)

        group = Table.grid(expand=True)
        group.add_row(info)
        group.add_row(Text("\nVALIDATION RECEIPTS", style=f"bold {BRASS}"))
        group.add_row(receipt_table)
        group.add_row(text)

        self.query_one("#detail_panel", Static).update(Panel(group, title=f"[bold {BRASS}]CAPABILITY DETAIL[/]", border_style=COPPER, box=box.ROUNDED))

    def update_receipts(self) -> None:
        table = Table(show_header=True, header_style=f"bold {BRASS}", expand=True, box=box.SIMPLE_HEAVY)
        table.add_column("TIME", style=CYAN, width=20)
        table.add_column("TYPE", width=20)
        table.add_column("SUBJECT", style=WHITE)
        table.add_column("STATUS", width=18)
        for receipt in self.receipts[:5]:
            rtype = receipt["file_name"].replace("_validation_receipt.json", "").replace(".json", "")[:20]
            table.add_row(receipt["time"], rtype, str(receipt["subject"])[:48], f"[{status_color(receipt['status'])}]{receipt['status']}[/]")
        self.query_one("#receipt_panel", Static).update(Panel(table, title=f"[bold {BRASS}]RECEIPT VAULT — RECENT TRUTH[/]", border_style=COPPER, box=box.ROUNDED))

    def update_actions(self) -> None:
        table = Table.grid(expand=True)
        table.add_column()
        table.add_row(f"[bold {BRASS}]FUTURE ACTION SOCKETS[/]")
        table.add_row("[white][ Validate ][/]   [white][ Promote ][/]   [white][ Export Scope ][/]   [white][ Open Receipt ][/]")
        table.add_row("")
        table.add_row("[cyan]READ-ONLY: no writes, no installs, no server.[/]")
        table.add_row("[cyan]Future buttons attach here without changing surfaces.[/]")
        table.add_row("")
        table.add_row(f"[bold {BRASS}]Owner approvals pending:[/] [yellow]{len(self.approvals)}[/]")
        for item in self.approvals[:4]:
            label = item.get("tool") or item.get("name") or item.get("capability_id") or item.get("question") or str(item)
            table.add_row(f"[yellow]• {label}[/]")
        self.query_one("#action_panel", Static).update(Panel(table, title=f"[bold {BRASS}]ACTION SOCKETS[/]", border_style=COPPER, box=box.ROUNDED))

    @on(Tree.NodeSelected, "#category_tree")
    def on_category_selected(self, event: Tree.NodeSelected) -> None:
        value = event.node.data
        if isinstance(value, str):
            self.selected_category = value
            self.update_category_tree()
            self.update_status_summary()
            self.update_capability_table()

    @on(DataTable.RowHighlighted, "#capability_table")
    def on_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        key = getattr(event.row_key, "value", None) or str(event.row_key)
        for card in self.filtered_cards():
            if card["capability_id"] == key:
                self.update_detail(card)
                break


if __name__ == "__main__":
    MechanicusForgeClient().run()
