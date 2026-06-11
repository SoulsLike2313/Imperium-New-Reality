#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imperium Patch Visual Proof v0.1

Owner-facing visual proof generator for Trinity Plus patch packs.
Reads a repo hygiene classification report and emits:
- terminal-friendly visual proof text
- owner markdown summary
- static HTML dashboard
- machine JSON receipt

No source mutation. Writes only to the provided out-root.
"""
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

SURFACE = "MECHANICUS_PATCH_VISUAL_PROOF_V0_1"
VERSION = "0.1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bar(value: int, total: int, width: int = 34) -> str:
    if total <= 0:
        return "[" + " " * width + "] 0%"
    filled = max(0, min(width, round(width * value / total)))
    pct = round(100 * value / total, 1)
    return "[" + "#" * filled + "." * (width - filled) + f"] {pct:>5}%"


def top_items(mapping: Dict[str, Any], limit: int = 8) -> List[Tuple[str, int]]:
    rows: List[Tuple[str, int]] = []
    for k, v in mapping.items():
        try:
            rows.append((str(k), int(v)))
        except Exception:
            continue
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[:limit]


def terminal_proof(report: Dict[str, Any], patch_id: str) -> str:
    files_total = int(report.get("files_total", 0) or 0)
    action_required = int(report.get("action_required_total", 0) or 0)
    lane_counts = report.get("lane_counts", {}) or {}
    severity_counts = report.get("severity_counts", {}) or {}
    organ_review_counts = report.get("organ_review_counts", {}) or {}
    outputs = report.get("outputs", {}) or {}

    lines: List[str] = []
    lines.append("=" * 78)
    lines.append("IMPERIUM TRINITY PLUS VISUAL PROOF")
    lines.append("=" * 78)
    lines.append(f"Surface    : {SURFACE} v{VERSION}")
    lines.append(f"Patch      : {patch_id}")
    lines.append(f"Source     : {report.get('source_head_short', 'UNKNOWN')} / {report.get('source_branch', 'UNKNOWN')}")
    lines.append(f"Generated  : {utc_now()}")
    lines.append("")
    lines.append("WHAT CHANGED / WHAT WORKS")
    lines.append("- Repo hygiene classifier produced a machine report, owner board, lane queue and SQLite index.")
    lines.append("- Classification is read-only: no source file is moved or deleted.")
    lines.append("- Owner can now inspect lanes before approving pack/move/delete actions.")
    lines.append("")
    lines.append("COUNTERS")
    lines.append(f"Files scanned       : {files_total}")
    lines.append(f"Action required     : {action_required} {bar(action_required, files_total)}")
    lines.append("")
    lines.append("LANES")
    for lane, count in top_items(lane_counts, limit=12):
        lines.append(f"{lane:<30} {count:>7} {bar(count, files_total)}")
    lines.append("")
    lines.append("SEVERITY")
    for sev, count in top_items(severity_counts, limit=8):
        lines.append(f"{sev:<30} {count:>7} {bar(count, files_total)}")
    lines.append("")
    lines.append("TOP REVIEW ORGANS")
    for organ, count in top_items(organ_review_counts, limit=10):
        lines.append(f"{organ:<30} {count:>7} {bar(count, max(action_required, 1))}")
    lines.append("")
    lines.append("OUTPUTS")
    for k in ["report", "owner_board", "lane_queue", "lane_counts", "sqlite_index"]:
        if k in outputs:
            lines.append(f"{k:<18}: {outputs[k]}")
    lines.append("")
    lines.append("OWNER DECISION")
    lines.append("PASS means: start owner-reviewed hygiene lanes. It does NOT authorize automatic source deletion.")
    lines.append("=" * 78)
    return "\n".join(lines) + "\n"


def owner_markdown(report: Dict[str, Any], machine: Dict[str, Any]) -> str:
    files_total = int(report.get("files_total", 0) or 0)
    action_required = int(report.get("action_required_total", 0) or 0)
    lane_counts = report.get("lane_counts", {}) or {}
    organ_review_counts = report.get("organ_review_counts", {}) or {}
    lines: List[str] = []
    lines.append(f"# Trinity Plus Visual Proof — {machine['patch_id']}")
    lines.append("")
    lines.append("## Что реально появилось")
    lines.append("")
    lines.append("- Inquisition repo hygiene classifier выполнил read-only классификацию репозитория.")
    lines.append("- Сформированы machine report, owner board, lane queue, lane counts и SQLite index.")
    lines.append("- Visual proof surface показывает владельцу счётчики и lanes без удаления source.")
    lines.append("")
    lines.append("## Итоговые счётчики")
    lines.append("")
    lines.append(f"- Files scanned: `{files_total}`")
    lines.append(f"- Action required: `{action_required}`")
    lines.append("")
    lines.append("## Lanes")
    lines.append("")
    for lane, count in top_items(lane_counts, limit=12):
        lines.append(f"- `{lane}`: `{count}`")
    lines.append("")
    lines.append("## Top review organs")
    lines.append("")
    for organ, count in top_items(organ_review_counts, limit=10):
        lines.append(f"- `{organ}`: `{count}`")
    lines.append("")
    lines.append("## Правило")
    lines.append("")
    lines.append("Trinity Plus patch считается закрытым только если владелец получил смотровую: terminal proof, owner dashboard/report или web dashboard. Этот proof не заменяет smoke, а показывает, что smoke дал живой, читаемый результат.")
    lines.append("")
    return "\n".join(lines) + "\n"


def html_dashboard(report: Dict[str, Any], machine: Dict[str, Any]) -> str:
    files_total = int(report.get("files_total", 0) or 0)
    action_required = int(report.get("action_required_total", 0) or 0)
    lane_counts = report.get("lane_counts", {}) or {}
    organ_review_counts = report.get("organ_review_counts", {}) or {}

    def card(title: str, value: Any, subtitle: str = "") -> str:
        return f"<div class='card'><div class='title'>{html.escape(title)}</div><div class='value'>{html.escape(str(value))}</div><div class='subtitle'>{html.escape(subtitle)}</div></div>"

    lane_rows = "".join(
        f"<tr><td>{html.escape(k)}</td><td>{v}</td><td><div class='bar'><span style='width:{0 if files_total == 0 else min(100, 100 * int(v) / files_total):.2f}%'></span></div></td></tr>"
        for k, v in top_items(lane_counts, limit=12)
    )
    organ_rows = "".join(
        f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>"
        for k, v in top_items(organ_review_counts, limit=12)
    )

    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Imperium Trinity Plus Visual Proof</title>
<style>
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; background: #101218; color: #eef1f5; }}
header {{ border-bottom: 1px solid #303646; padding-bottom: 16px; margin-bottom: 22px; }}
h1 {{ margin: 0; font-size: 28px; }}
small {{ color: #aab2c5; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 18px 0; }}
.card {{ background: #171b24; border: 1px solid #303646; border-radius: 12px; padding: 16px; }}
.title {{ color: #aab2c5; font-size: 13px; text-transform: uppercase; letter-spacing: .06em; }}
.value {{ font-size: 30px; font-weight: 700; margin-top: 8px; }}
.subtitle {{ color: #aab2c5; margin-top: 6px; }}
table {{ width: 100%; border-collapse: collapse; background: #171b24; border-radius: 12px; overflow: hidden; margin-bottom: 22px; }}
th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #303646; }}
th {{ color: #aab2c5; background: #202636; }}
.bar {{ background: #303646; height: 10px; border-radius: 99px; overflow: hidden; }}
.bar span {{ display: block; height: 100%; background: #8dd6ff; }}
.notice {{ border-left: 4px solid #8dd6ff; padding: 12px 14px; background: #171b24; margin-top: 16px; }}
</style>
</head>
<body>
<header>
<h1>Imperium Trinity Plus Visual Proof</h1>
<small>{html.escape(machine['patch_id'])} · {html.escape(machine['generated_at_utc'])}</small>
</header>
<div class="grid">
{card('Files scanned', files_total)}
{card('Action required', action_required, 'classification lanes requiring review')}
{card('Source head', report.get('source_head_short', 'UNKNOWN'))}
{card('Mode', report.get('mode', 'read_only'))}
</div>
<h2>Lane board</h2>
<table><tr><th>Lane</th><th>Count</th><th>Share</th></tr>{lane_rows}</table>
<h2>Top review organs</h2>
<table><tr><th>Organ</th><th>Review count</th></tr>{organ_rows}</table>
<div class="notice"><b>Owner gate:</b> this proof authorizes review, not automatic cleanup. No source deletion is performed by the classifier.</div>
</body>
</html>
"""


def build(args: argparse.Namespace) -> Dict[str, Any]:
    report_path = Path(args.classification_report)
    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    report = read_json(report_path)
    patch_id = args.patch_id or report.get("patch_id") or "UNKNOWN-PATCH"

    machine = {
        "schema": "imperium.trinity_plus_visual_proof.v0_1",
        "surface": SURFACE,
        "version": VERSION,
        "status": "PASS_TRINITY_PLUS_VISUAL_PROOF_BUILT",
        "generated_at_utc": utc_now(),
        "patch_id": patch_id,
        "classification_report": str(report_path),
        "source_head_short": report.get("source_head_short"),
        "files_total": report.get("files_total"),
        "action_required_total": report.get("action_required_total"),
        "lane_counts": report.get("lane_counts", {}),
        "organ_review_counts": report.get("organ_review_counts", {}),
        "proof_outputs": {
            "terminal": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_TERMINAL.txt"),
            "owner_markdown": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_RU.md"),
            "html_dashboard": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_DASHBOARD.html"),
            "machine": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_MACHINE.json"),
        },
        "owner_gate": "Visual proof shows changed/worked state; it does not authorize automatic source deletion.",
    }

    terminal = terminal_proof(report, patch_id)
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_TERMINAL.txt").write_text(terminal, encoding="utf-8")
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_RU.md").write_text(owner_markdown(report, machine), encoding="utf-8")
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_DASHBOARD.html").write_text(html_dashboard(report, machine), encoding="utf-8")
    write_json(out_root / "TRINITY_PLUS_VISUAL_PROOF_MACHINE.json", machine)

    print(terminal)
    print(json.dumps({k: v for k, v in machine.items() if k not in {"lane_counts", "organ_review_counts"}}, ensure_ascii=False, indent=2))
    return machine


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build owner-facing Trinity Plus visual proof from a classification report.")
    ap.add_argument("--classification-report", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--patch-id", default="")
    args = ap.parse_args(argv)
    build(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
