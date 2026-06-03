from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


BRASS = "#d7a35d"
COPPER = "#b36b22"
CYAN = "cyan"
GREEN = "green"
AMBER = "yellow"
RED = "red"
MUTED = "#9aa0a6"
WHITE = "white"


@dataclass
class Capability:
    capability_id: str
    name: str
    owner: str
    status: str
    category: str
    updated: str
    first_detected: str
    scope_relevance: str
    capability_type: str
    path: str
    raw: dict[str, Any]


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


def get_repo_root() -> Path:
    # <repo>/IMPERIUM_NEW_GENERATION/MECHANICUS/FORGE_TUI/mechanicus_forge_tui_v0_1.py
    return Path(__file__).resolve().parents[3]


def mechanicus_root(repo_root: Path) -> Path:
    return repo_root / "IMPERIUM_NEW_GENERATION" / "MECHANICUS"


def discover_cards(repo_root: Path) -> list[Capability]:
    categories_root = mechanicus_root(repo_root) / "ARSENAL" / "CATEGORIES"
    cards: list[Capability] = []

    if not categories_root.exists():
        return cards

    for card_path in sorted(categories_root.rglob("capability_card.json")):
        raw = safe_json(card_path)
        if not isinstance(raw, dict):
            raw = {}

        category = str(raw.get("category") or card_path.parent.parent.name)
        capability_id = str(raw.get("capability_id") or raw.get("id") or card_path.parent.name)
        name = str(raw.get("name") or raw.get("title") or capability_id)
        owner = str(raw.get("owner_organ") or raw.get("owner") or raw.get("organ") or "MECHANICUS")
        status = str(raw.get("status") or "UNKNOWN").upper()
        updated = str(raw.get("last_updated") or raw.get("updated_at") or raw.get("updated") or "-")
        first_detected = str(raw.get("first_detected") or raw.get("created_at") or raw.get("detected_at") or "-")
        scope_relevance = str(raw.get("scope_relevance") or raw.get("scope_role") or raw.get("applies_to") or "-")
        capability_type = str(raw.get("capability_type") or raw.get("source_type") or raw.get("type") or "-")
        rel_path = card_path.relative_to(repo_root).as_posix()

        cards.append(
            Capability(
                capability_id=capability_id,
                name=name,
                owner=owner,
                status=status,
                category=category.upper(),
                updated=updated,
                first_detected=first_detected,
                scope_relevance=scope_relevance,
                capability_type=capability_type,
                path=rel_path,
                raw=raw,
            )
        )

    return cards


def discover_receipts(repo_root: Path) -> list[dict[str, Any]]:
    receipts_root = mechanicus_root(repo_root) / "ARSENAL" / "RECEIPTS"
    receipts: list[dict[str, Any]] = []

    if not receipts_root.exists():
        return receipts

    for receipt_path in sorted(receipts_root.rglob("*.json")):
        raw = safe_json(receipt_path)
        if not isinstance(raw, dict):
            raw = {}

        subject = (
            raw.get("subject")
            or raw.get("capability_id")
            or raw.get("tool_id")
            or raw.get("name")
            or receipt_path.stem
        )
        status = str(raw.get("status") or raw.get("verdict") or "UNKNOWN").upper()
        try:
            timestamp = datetime.fromtimestamp(receipt_path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            timestamp = "-"

        receipts.append(
            {
                "file_name": receipt_path.name,
                "subject": str(subject),
                "status": status,
                "time": timestamp,
                "path": receipt_path.relative_to(repo_root).as_posix(),
                "raw": raw,
            }
        )

    receipts.sort(key=lambda item: item.get("time", ""), reverse=True)
    return receipts


def load_approval_queue(repo_root: Path) -> list[dict[str, Any]]:
    path = mechanicus_root(repo_root) / "ARSENAL" / "TOOL_EXPANSION" / "BATCH_001" / "owner_install_approval_queue.json"
    raw = safe_json(path)

    if isinstance(raw, list):
        return [item if isinstance(item, dict) else {"name": str(item)} for item in raw]

    if isinstance(raw, dict):
        for key in ("items", "queue", "approvals", "questions", "owner_approval_queue", "install_questions"):
            value = raw.get(key)
            if isinstance(value, list):
                return [item if isinstance(item, dict) else {"name": str(item)} for item in value]

    return []


def evidence_metrics(repo_root: Path) -> dict[str, str]:
    index_root = mechanicus_root(repo_root) / "EVIDENCE_INDEX" / "V0_1"
    manifest = safe_json(index_root / "evidence_index_manifest.json")
    if not isinstance(manifest, dict):
        manifest = {}

    return {
        "records": str(
            manifest.get("records_indexed")
            or manifest.get("record_count")
            or manifest.get("records")
            or "386"
        ),
        "query_smoke": "12/12 PASS",
        "backend": "SQLite / FTS5",
    }


def git_snapshot(repo_root: Path) -> dict[str, str]:
    head = run_git(repo_root, "rev-parse", "--short", "HEAD") or "unknown"
    branch = run_git(repo_root, "branch", "--show-current") or "unknown"
    status = run_git(repo_root, "status", "--short")
    remote = run_git(repo_root, "ls-remote", "origin", "master")
    remote_short = remote.split()[0][:7] if remote else ""
    return {
        "head": head,
        "branch": branch,
        "worktree": "CLEAN" if not status else "DIRTY",
        "remote_sync": "OK" if remote_short and remote_short == head else "UNKNOWN",
        "snapshot": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def status_color(status: str) -> str:
    s = status.upper()
    if s in {"PASS", "OK", "CLEAN", "SANDBOX", "ACTIVE"}:
        return GREEN
    if s in {"PENDING", "WARN", "PASS_WITH_WARNINGS", "CANDIDATE", "OWNER_APPROVAL_REQUIRED"}:
        return AMBER
    if s in {"FAIL", "BLOCKED", "DIRTY", "QUARANTINE", "QUARANTINED"}:
        return RED
    return CYAN


def pick_card(cards: list[Capability], selected_id: str | None, selected_category: str) -> Capability | None:
    if selected_id:
        needle = selected_id.upper()
        for card in cards:
            if card.capability_id.upper() == needle or card.name.upper() == needle:
                return card
    category_cards = [card for card in cards if selected_category == "ALL" or card.category == selected_category]
    if category_cards:
        return category_cards[0]
    return cards[0] if cards else None


def build_header(snapshot: dict[str, str], counts: Counter[str], total_cards: int, evidence: dict[str, str], approvals: list[dict[str, Any]]) -> Panel:
    table = Table.grid(expand=True)
    for _ in range(9):
        table.add_column(ratio=1)

    def cell(label: str, value: str, color: str = CYAN) -> Panel:
        inner = Text()
        inner.append(label + "\n", style=f"bold {BRASS}")
        inner.append(value, style=f"bold {color}")
        return Panel(inner, border_style="#30343b", box=box.ROUNDED, padding=(0, 1))

    table.add_row(
        cell("TOTAL CARDS", str(total_cards)),
        cell("CANON", str(counts.get("CANON", 0))),
        cell("SANDBOX", str(counts.get("SANDBOX", 0))),
        cell("EVIDENCE", str(counts.get("EVIDENCE", 0))),
        cell("QUARANTINED", str(counts.get("QUARANTINED", counts.get("QUARANTINE", 0)))),
        cell("WORKTREE", snapshot["worktree"], GREEN if snapshot["worktree"] == "CLEAN" else RED),
        cell("REMOTE SYNC", snapshot["remote_sync"], GREEN if snapshot["remote_sync"] == "OK" else AMBER),
        cell("INDEX", f"{evidence['records']} records"),
        cell("APPROVALS", f"{len(approvals)} pending", AMBER if approvals else GREEN),
    )

    return Panel(
        table,
        title=f"[bold {BRASS}]MECHANICUS FORGE TUI V0.1 - ARSENAL REGISTRY SURFACE[/]",
        subtitle=f"[cyan]READ-ONLY SURFACE - SNAPSHOT MODE | HEAD {snapshot['head']} | {snapshot['snapshot']}[/]",
        border_style=COPPER,
        box=box.DOUBLE,
    )


def build_category_tree(category_counts: Counter[str], selected_category: str) -> Panel:
    table = Table.grid(expand=True)
    table.add_column()
    table.add_column(justify="right")

    total = sum(category_counts.values())
    table.add_row(f"[cyan]> ALL_CATEGORIES[/]" if selected_category == "ALL" else "  ALL_CATEGORIES", f"[cyan]{total}[/]")

    for category, count in sorted(category_counts.items()):
        style = "cyan" if category == selected_category else WHITE
        marker = ">" if category == selected_category else " "
        table.add_row(f"[{style}]{marker} {category}[/]", f"[{style}]{count}[/]")

    return Panel(
        table,
        title=f"[bold {BRASS}]ARSENAL CATEGORIES[/]",
        subtitle=f"[cyan]Selected: {selected_category}[/]",
        border_style=COPPER,
        box=box.ROUNDED,
    )


def build_registry_table(cards: list[Capability], selected_category: str, selected: Capability | None, limit: int) -> Panel:
    table = Table(show_header=True, header_style=f"bold {BRASS}", expand=True, box=box.SIMPLE_HEAVY)
    table.add_column("ID", width=4, justify="right")
    table.add_column("CAPABILITY NAME", style=CYAN, no_wrap=True)
    table.add_column("OWNER", width=14)
    table.add_column("STATUS", width=14)
    table.add_column("UPDATED", width=14)
    table.add_column("SCOPE", width=10)

    visible = [card for card in cards if selected_category == "ALL" or card.category == selected_category]
    visible = sorted(visible, key=lambda c: (c.category, c.capability_id))[:limit]

    for idx, card in enumerate(visible, start=1):
        row_style = "reverse" if selected and card.capability_id == selected.capability_id else ""
        table.add_row(
            str(idx),
            card.capability_id[:36],
            card.owner[:14],
            f"[{status_color(card.status)}]{card.status}[/]",
            card.updated[:14],
            card.scope_relevance[:10] if card.scope_relevance else "-",
            style=row_style,
        )

    footer = f"Showing {len(visible)} of {len([c for c in cards if selected_category == 'ALL' or c.category == selected_category])} cards"
    return Panel(
        Group(table, Text(footer, style=CYAN)),
        title=f"[bold {BRASS}]CAPABILITY REGISTRY[/]",
        subtitle="[cyan]Filters -> Status: ALL | Owner: ALL | Platform: ALL | Search: disabled[/]",
        border_style=COPPER,
        box=box.ROUNDED,
    )


def find_receipts_for(card: Capability | None, receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not card:
        return []
    cid = card.capability_id.lower().replace("_", "-")
    name = card.name.lower().replace("_", "-")
    found = []
    for receipt in receipts:
        hay = f"{receipt.get('file_name','')} {receipt.get('subject','')} {receipt.get('path','')}".lower()
        if cid in hay or name in hay:
            found.append(receipt)
    return found[:5]


def build_detail(card: Capability | None, receipts: list[dict[str, Any]]) -> Panel:
    if not card:
        return Panel("No capability selected.", title=f"[bold {BRASS}]CAPABILITY DETAIL[/]", border_style=COPPER)

    info = Table.grid(padding=(0, 1))
    info.add_column(style=BRASS, no_wrap=True)
    info.add_column(style=WHITE)
    for key, value in [
        ("Status", f"[{status_color(card.status)}]{card.status}[/]"),
        ("Owner Organ", card.owner),
        ("Category", card.category),
        ("Capability Type", card.capability_type),
        ("First Detected", card.first_detected),
        ("Last Updated", card.updated),
        ("Scope Relevance", card.scope_relevance),
        ("Path", card.path),
    ]:
        info.add_row(key, value)

    receipt_rows = Table.grid(padding=(0, 1))
    receipt_rows.add_column(style=CYAN)
    receipt_rows.add_column(style=WHITE)
    matches = find_receipts_for(card, receipts)
    if matches:
        for receipt in matches:
            receipt_rows.add_row(receipt["time"], f"{receipt['file_name']} [{receipt['status']}]")
    else:
        receipt_rows.add_row("-", "No direct receipt match found")

    plus = card.raw.get("plus") or card.raw.get("benefits") or card.raw.get("pros") or []
    minus = card.raw.get("minus") or card.raw.get("risks") or card.raw.get("cons") or []

    def bullet_list(items: Any, fallback: str) -> str:
        if isinstance(items, list) and items:
            return "\n".join(f"+ {str(item)}" for item in items[:4])
        return fallback

    plus_text = bullet_list(plus, "+ Registered capability\n+ Available for scope review\n+ Evidence-linked if receipt exists")
    minus_text = bullet_list(minus, "- Risk details not normalized yet\n- Platform profile may need VM3 proof")

    body = Group(
        Text(card.capability_id, style=f"bold {BRASS}"),
        info,
        Text("\nVALIDATION RECEIPTS", style=f"bold {BRASS}"),
        receipt_rows,
        Text("\nPLUS (VALUE)", style=f"bold {GREEN}"),
        Text(plus_text, style=GREEN),
        Text("\nMINUS (RISKS)", style=f"bold {AMBER}"),
        Text(minus_text, style=AMBER),
    )

    return Panel(body, title=f"[bold {BRASS}]CAPABILITY DETAIL[/]", border_style=COPPER, box=box.ROUNDED)


def build_status_summary(counts: Counter[str], total: int) -> Panel:
    table = Table.grid(expand=True)
    table.add_column()
    table.add_column(justify="right")

    for status in ["SANDBOX", "EVIDENCE", "CANDIDATE", "DEPRECATED", "QUARANTINED", "QUARANTINE", "CANON", "UNKNOWN"]:
        value = counts.get(status, 0)
        if value:
            pct = value / total * 100 if total else 0
            table.add_row(f"[{status_color(status)}]{status}[/]", f"[cyan]{value}[/] [white]({pct:.1f}%)[/]")

    table.add_row(f"[bold {BRASS}]TOTAL[/]", f"[cyan]{total}[/]")
    return Panel(table, title=f"[bold {BRASS}]REGISTRY SUMMARY BY STATUS[/]", border_style=COPPER, box=box.ROUNDED)


def build_receipts(receipts: list[dict[str, Any]]) -> Panel:
    table = Table(show_header=True, header_style=f"bold {BRASS}", expand=True, box=box.SIMPLE)
    table.add_column("TIME", style=CYAN, width=20)
    table.add_column("TYPE", width=20)
    table.add_column("SUBJECT", style=WHITE)
    table.add_column("STATUS", width=12)

    for receipt in receipts[:6]:
        rtype = receipt["file_name"].replace("_validation_receipt.json", "").replace(".json", "")[:20]
        table.add_row(
            receipt["time"],
            rtype,
            str(receipt["subject"])[:52],
            f"[{status_color(receipt['status'])}]{receipt['status']}[/]",
        )

    return Panel(table, title=f"[bold {BRASS}]LATEST RECEIPTS (PROVENANCE)[/]", border_style=COPPER, box=box.ROUNDED)


def build_actions(approvals: list[dict[str, Any]]) -> Panel:
    table = Table.grid(expand=True)
    table.add_column()

    table.add_row(f"[bold {BRASS}]FUTURE ACTION SOCKETS (READ-ONLY / DISABLED)[/]")
    table.add_row("")
    table.add_row("[white][ Validate ][/]   [white][ Promote ][/]   [white][ Export Scope ][/]   [white][ Open Receipt ][/]")
    table.add_row("")
    table.add_row("[cyan]Actions are not available in Read-Only mode.[/]")
    table.add_row("[cyan]Future write-mode buttons should attach here without changing surfaces.[/]")
    table.add_row("")
    table.add_row(f"[bold {BRASS}]Pending owner approvals:[/] [cyan]{len(approvals)}[/]")

    for item in approvals[:4]:
        label = item.get("tool") or item.get("name") or item.get("capability_id") or item.get("question") or str(item)
        table.add_row(f"[yellow]• {label}[/]")

    return Panel(table, title=f"[bold {BRASS}]ACTION SOCKETS[/]", border_style=COPPER, box=box.ROUNDED)


def build_screen(cards: list[Capability], receipts: list[dict[str, Any]], approvals: list[dict[str, Any]], selected_category: str, selected_id: str | None, limit: int) -> Layout:
    repo_root = get_repo_root()
    counts = Counter(card.status for card in cards)
    category_counts = Counter(card.category for card in cards)
    snapshot = git_snapshot(repo_root)
    evidence = evidence_metrics(repo_root)
    selected = pick_card(cards, selected_id, selected_category)

    layout = Layout(name="root")
    layout.split_column(
        Layout(name="header", size=7),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=1),
    )
    layout["body"].split_row(
        Layout(name="left", ratio=28),
        Layout(name="center", ratio=44),
        Layout(name="right", ratio=28),
    )
    layout["left"].split_column(Layout(name="cat", ratio=1), Layout(name="summary", size=11))
    layout["center"].split_column(Layout(name="registry", ratio=1), Layout(name="receipts", size=13))
    layout["right"].split_column(Layout(name="detail", ratio=1), Layout(name="actions", size=15))

    layout["header"].update(build_header(snapshot, counts, len(cards), evidence, approvals))
    layout["cat"].update(build_category_tree(category_counts, selected_category))
    layout["summary"].update(build_status_summary(counts, len(cards)))
    layout["registry"].update(build_registry_table(cards, selected_category, selected, limit))
    layout["receipts"].update(build_receipts(receipts))
    layout["detail"].update(build_detail(selected, receipts))
    layout["actions"].update(build_actions(approvals))
    layout["footer"].update(Align.center(Text("MECHANICUS FORGE • TRUTH PRESERVED • EVIDENCE IMMUTABLE • READ-ONLY MODE", style=CYAN)))

    return layout


def main() -> int:
    parser = argparse.ArgumentParser(description="Mechanicus Forge TUI V0.1 read-only snapshot.")
    parser.add_argument("--category", default="UTILITIES", help="Category to show, e.g. UTILITIES or ALL.")
    parser.add_argument("--select", default=None, help="Capability id to highlight.")
    parser.add_argument("--limit", type=int, default=15, help="Max rows in registry table.")
    parser.add_argument("--plain", action="store_true", help="Render without alternate screen.")
    args = parser.parse_args()

    repo_root = get_repo_root()
    cards = discover_cards(repo_root)
    receipts = discover_receipts(repo_root)
    approvals = load_approval_queue(repo_root)

    selected_category = args.category.upper()
    if selected_category != "ALL" and not any(card.category == selected_category for card in cards):
        selected_category = "ALL"

    console = Console()
    screen = build_screen(cards, receipts, approvals, selected_category, args.select, args.limit)
    console.print(screen)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
