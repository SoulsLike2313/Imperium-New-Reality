#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Imperium Patch Visual Proof v0.2

Owner-facing Trinity Plus visual proof generator.

Reads a repo hygiene classification report and emits bilingual proof surfaces:
- bilingual terminal proof text
- Russian markdown summary
- English markdown summary
- bilingual markdown summary
- static bilingual HTML dashboard with RU/EN toggle
- machine JSON receipt with roadmap/progress metrics

Optional Rich terminal rendering is supported when the `rich` package is installed.
No source mutation. Writes only to the provided out-root.
"""
from __future__ import annotations

import argparse
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

SURFACE = "MECHANICUS_PATCH_VISUAL_PROOF_V0_1"
VERSION = "0.2.0"


RU = {
    "title": "Imperium Trinity Plus — Смотровая патча",
    "what_changed": "Что реально изменилось / что работает",
    "counters": "Счётчики",
    "lanes": "Линии действий",
    "severity": "Серьёзность",
    "top_review_organs": "Главные зоны ревью",
    "roadmap": "Движение по плану",
    "overall_goal": "Общая цель",
    "owner_gate": "Owner gate: смотровая разрешает ревью и планирование, но НЕ разрешает автоматическое удаление source.",
    "files_scanned": "Файлов просканировано",
    "action_required": "Требуют действия",
    "source_head": "Source HEAD",
    "mode": "Режим",
    "progress_note": "Процент — операторский индикатор близости, не юридическое разрешение на cleanup.",
    "changed_bullets": [
        "Инквизиция построила read-only классификацию репозитория.",
        "Созданы machine report, owner board, lane queue, lane counts и SQLite index.",
        "Смотровая показывает lanes, прогресс и следующие owner-gated действия без удаления source.",
    ],
    "roadmap_steps": {
        "visibility": "Видимость: репо просканировано, lanes построены",
        "trinity_plus": "Trinity Plus proof: владелец видит живую смотровую",
        "source_clarity": "Source clarity: доля KEEP_SOURCE относительно всех файлов",
        "passporting": "Паспортизация: tool-like source получает Mechanicus passports",
        "vault_migration": "Evidence Vault: pack-to-vault candidates обработаны",
        "fixture_manifest": "Fixture exceptions: source fixtures снабжены manifest",
        "owner_gate_cleanup": "Owner-gated cleanup: перемещения/удаления только после разрешения",
        "clean_transfer": "Clean transfer: перенос в main без H-мусора",
    },
    "lanes_ru": {
        "KEEP_SOURCE": "Оставить в source",
        "PACK_TO_VAULT_CANDIDATE": "Кандидат на упаковку в Vault",
        "PASSPORT_REQUIRED": "Нужен паспорт Mechanicus",
        "FIXTURE_MANIFEST_REQUIRED": "Нужен fixture/source manifest",
        "OWNER_REVIEW_MOVE": "Нужно решение владельца о переносе",
        "SAFE_RUNTIME_DELETE": "Safe-delete только после owner gate",
    },
}

EN = {
    "title": "Imperium Trinity Plus — Patch Visual Proof",
    "what_changed": "What changed / what works",
    "counters": "Counters",
    "lanes": "Action lanes",
    "severity": "Severity",
    "top_review_organs": "Top review zones",
    "roadmap": "Roadmap progress",
    "overall_goal": "Overall goal",
    "owner_gate": "Owner gate: this proof authorizes review and planning, NOT automatic source deletion.",
    "files_scanned": "Files scanned",
    "action_required": "Action required",
    "source_head": "Source HEAD",
    "mode": "Mode",
    "progress_note": "Percentages are operator indicators, not cleanup authorization.",
    "changed_bullets": [
        "Inquisition produced a read-only repository hygiene classification.",
        "Machine report, owner board, lane queue, lane counts and SQLite index were created.",
        "The visual proof shows lanes, progress and next owner-gated actions without deleting source.",
    ],
    "roadmap_steps": {
        "visibility": "Visibility: repo scanned and lanes built",
        "trinity_plus": "Trinity Plus proof: owner sees a live proof surface",
        "source_clarity": "Source clarity: KEEP_SOURCE share across all files",
        "passporting": "Passporting: tool-like source receives Mechanicus passports",
        "vault_migration": "Evidence Vault: pack-to-vault candidates processed",
        "fixture_manifest": "Fixture exceptions: source fixtures get manifests",
        "owner_gate_cleanup": "Owner-gated cleanup: moves/deletes only after approval",
        "clean_transfer": "Clean transfer: move to main without H-local debris",
    },
    "lanes_ru": {},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def pct(value: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return round(max(0.0, min(100.0, 100.0 * value / total)), 1)


def clamp_pct(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 1)


def bar(value: float, total: float = 100.0, width: int = 34) -> str:
    percent = pct(value, total) if total != 100.0 else clamp_pct(value)
    filled = max(0, min(width, round(width * percent / 100.0)))
    return "[" + "#" * filled + "." * (width - filled) + f"] {percent:>5.1f}%"


def top_items(mapping: Dict[str, Any], limit: int = 8) -> List[Tuple[str, int]]:
    rows: List[Tuple[str, int]] = []
    for k, v in (mapping or {}).items():
        try:
            rows.append((str(k), int(v)))
        except Exception:
            continue
    rows.sort(key=lambda x: x[1], reverse=True)
    return rows[:limit]


def lane_label(lane: str, lang: str) -> str:
    if lang == "ru":
        return RU["lanes_ru"].get(lane, lane)
    return lane


def compute_progress(report: Dict[str, Any]) -> Dict[str, Any]:
    files_total = as_int(report.get("files_total"))
    lane_counts = report.get("lane_counts", {}) or {}
    keep_source = as_int(lane_counts.get("KEEP_SOURCE"))
    passport_required = as_int(lane_counts.get("PASSPORT_REQUIRED"))
    pack_to_vault = as_int(lane_counts.get("PACK_TO_VAULT_CANDIDATE"))
    fixture_required = as_int(lane_counts.get("FIXTURE_MANIFEST_REQUIRED"))
    action_required = as_int(report.get("action_required_total"))
    registered_tools = as_int(report.get("registered_tool_paths_total"))

    passport_total_estimate = registered_tools + passport_required
    passport_coverage = pct(registered_tools, passport_total_estimate) if passport_total_estimate else 100.0
    source_clarity = pct(keep_source, files_total)
    needs_action_share = pct(action_required, files_total)

    steps = [
        {
            "id": "visibility",
            "status": "PASS",
            "percent": 100.0,
            "evidence": f"{files_total} files scanned; {len(lane_counts)} lanes counted",
            "ru": RU["roadmap_steps"]["visibility"],
            "en": EN["roadmap_steps"]["visibility"],
        },
        {
            "id": "trinity_plus",
            "status": "PASS",
            "percent": 100.0,
            "evidence": "terminal + markdown + HTML + machine proof generated",
            "ru": RU["roadmap_steps"]["trinity_plus"],
            "en": EN["roadmap_steps"]["trinity_plus"],
        },
        {
            "id": "source_clarity",
            "status": "IN_PROGRESS",
            "percent": source_clarity,
            "evidence": f"KEEP_SOURCE={keep_source}/{files_total}; action_required={action_required}",
            "ru": RU["roadmap_steps"]["source_clarity"],
            "en": EN["roadmap_steps"]["source_clarity"],
        },
        {
            "id": "passporting",
            "status": "IN_PROGRESS",
            "percent": passport_coverage,
            "evidence": f"registered_tool_paths={registered_tools}; passport_required={passport_required}",
            "ru": RU["roadmap_steps"]["passporting"],
            "en": EN["roadmap_steps"]["passporting"],
        },
        {
            "id": "vault_migration",
            "status": "OWNER_GATE_REQUIRED",
            "percent": 0.0 if pack_to_vault else 100.0,
            "evidence": f"pack_to_vault_candidates={pack_to_vault}; no automatic packing in this proof",
            "ru": RU["roadmap_steps"]["vault_migration"],
            "en": EN["roadmap_steps"]["vault_migration"],
        },
        {
            "id": "fixture_manifest",
            "status": "OWNER_GATE_REQUIRED",
            "percent": 0.0 if fixture_required else 100.0,
            "evidence": f"fixture_manifest_required={fixture_required}; no automatic source exception created here",
            "ru": RU["roadmap_steps"]["fixture_manifest"],
            "en": EN["roadmap_steps"]["fixture_manifest"],
        },
        {
            "id": "owner_gate_cleanup",
            "status": "NOT_STARTED",
            "percent": 0.0,
            "evidence": "classifier is read-only; cleanup requires explicit owner gate",
            "ru": RU["roadmap_steps"]["owner_gate_cleanup"],
            "en": EN["roadmap_steps"]["owner_gate_cleanup"],
        },
        {
            "id": "clean_transfer",
            "status": "NOT_STARTED",
            "percent": 0.0,
            "evidence": "H-contour continues; main transfer intentionally not done",
            "ru": RU["roadmap_steps"]["clean_transfer"],
            "en": EN["roadmap_steps"]["clean_transfer"],
        },
    ]

    weights = {
        "visibility": 0.18,
        "trinity_plus": 0.12,
        "source_clarity": 0.20,
        "passporting": 0.14,
        "vault_migration": 0.16,
        "fixture_manifest": 0.10,
        "owner_gate_cleanup": 0.06,
        "clean_transfer": 0.04,
    }
    overall = 0.0
    for step in steps:
        overall += float(step["percent"]) * weights.get(str(step["id"]), 0.0)

    return {
        "overall_goal_id": "clean_passported_indexed_repo",
        "overall_goal_ru": "Чистое, паспортированное, индексируемое repo без неуправляемой evidence/runtime грязи",
        "overall_goal_en": "Clean, passported, queryable repository without unmanaged evidence/runtime debris",
        "overall_progress_percent": clamp_pct(overall),
        "source_clarity_percent": source_clarity,
        "needs_action_share_percent": needs_action_share,
        "passport_coverage_estimate_percent": passport_coverage,
        "pack_to_vault_candidates": pack_to_vault,
        "fixture_manifest_required": fixture_required,
        "action_required_total": action_required,
        "roadmap_steps": steps,
        "progress_warning_ru": "Это операторская шкала движения по плану, а не разрешение на автоматическую чистку.",
        "progress_warning_en": "This is an operator roadmap score, not authorization for automatic cleanup.",
    }


def localized_summary_lines(report: Dict[str, Any], progress: Dict[str, Any], lang: str) -> List[str]:
    L = RU if lang == "ru" else EN
    files_total = as_int(report.get("files_total"))
    action_required = as_int(report.get("action_required_total"))
    lane_counts = report.get("lane_counts", {}) or {}
    severity_counts = report.get("severity_counts", {}) or {}
    organ_review_counts = report.get("organ_review_counts", {}) or {}

    lines: List[str] = []
    lines.append("=" * 86)
    lines.append(L["title"].upper())
    lines.append("=" * 86)
    lines.append(f"Surface    : {SURFACE} v{VERSION}")
    lines.append(f"Patch      : {report.get('patch_id', 'UNKNOWN')}")
    lines.append(f"Source     : {report.get('source_head_short', 'UNKNOWN')} / {report.get('source_branch', 'UNKNOWN')}")
    lines.append(f"Generated  : {utc_now()}")
    lines.append("")
    lines.append(L["what_changed"].upper())
    for bullet in L["changed_bullets"]:
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append(L["overall_goal"].upper())
    lines.append(progress["overall_goal_ru"] if lang == "ru" else progress["overall_goal_en"])
    lines.append(f"{progress['overall_progress_percent']:>5.1f}% {bar(progress['overall_progress_percent'])}")
    lines.append(L["progress_note"])
    lines.append("")
    lines.append(L["counters"].upper())
    lines.append(f"{L['files_scanned']:<28}: {files_total}")
    lines.append(f"{L['action_required']:<28}: {action_required} {bar(action_required, files_total)}")
    lines.append(f"{L['source_head']:<28}: {report.get('source_head_short', 'UNKNOWN')}")
    lines.append(f"{L['mode']:<28}: {report.get('mode', 'UNKNOWN')}")
    lines.append("")
    lines.append(L["roadmap"].upper())
    for step in progress["roadmap_steps"]:
        label = step["ru"] if lang == "ru" else step["en"]
        lines.append(f"{step['status']:<20} {step['percent']:>5.1f}% {bar(step['percent'])}  {label}")
        lines.append(f"{'':<20}       evidence: {step['evidence']}")
    lines.append("")
    lines.append(L["lanes"].upper())
    for lane, count in top_items(lane_counts, limit=12):
        label = lane_label(lane, lang)
        lines.append(f"{label:<38} {count:>7} {bar(count, files_total)}  [{lane}]")
    lines.append("")
    lines.append(L["severity"].upper())
    for sev, count in top_items(severity_counts, limit=8):
        lines.append(f"{sev:<38} {count:>7} {bar(count, files_total)}")
    lines.append("")
    lines.append(L["top_review_organs"].upper())
    for organ, count in top_items(organ_review_counts, limit=12):
        lines.append(f"{organ:<38} {count:>7} {bar(count, max(action_required, 1))}")
    lines.append("")
    lines.append(L["owner_gate"])
    lines.append("=" * 86)
    return lines


def terminal_proof(report: Dict[str, Any], progress: Dict[str, Any], language: str) -> str:
    sections: List[str] = []
    if language in {"ru", "both"}:
        sections.extend(localized_summary_lines(report, progress, "ru"))
    if language == "both":
        sections.append("\n")
    if language in {"en", "both"}:
        sections.extend(localized_summary_lines(report, progress, "en"))
    return "\n".join(sections) + "\n"


def markdown_summary(report: Dict[str, Any], progress: Dict[str, Any], lang: str) -> str:
    L = RU if lang == "ru" else EN
    files_total = as_int(report.get("files_total"))
    action_required = as_int(report.get("action_required_total"))
    lane_counts = report.get("lane_counts", {}) or {}
    organ_review_counts = report.get("organ_review_counts", {}) or {}

    title = "Смотровая Trinity Plus" if lang == "ru" else "Trinity Plus Visual Proof"
    lines = [f"# {title} — {report.get('patch_id', 'UNKNOWN')}", ""]
    lines.append(f"**{L['overall_goal']}:** {progress['overall_goal_ru'] if lang == 'ru' else progress['overall_goal_en']}")
    lines.append("")
    lines.append(f"**Progress:** `{progress['overall_progress_percent']}%`")
    lines.append("")
    lines.append("## " + L["what_changed"])
    lines.append("")
    for bullet in L["changed_bullets"]:
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("## " + L["counters"])
    lines.append("")
    lines.append(f"- {L['files_scanned']}: `{files_total}`")
    lines.append(f"- {L['action_required']}: `{action_required}`")
    lines.append(f"- {L['source_head']}: `{report.get('source_head_short', 'UNKNOWN')}`")
    lines.append("")
    lines.append("## " + L["roadmap"])
    lines.append("")
    lines.append("| Status | Progress | Step | Evidence |")
    lines.append("|---|---:|---|---|")
    for step in progress["roadmap_steps"]:
        label = step["ru"] if lang == "ru" else step["en"]
        lines.append(f"| `{step['status']}` | `{step['percent']}%` | {label} | {step['evidence']} |")
    lines.append("")
    lines.append("## " + L["lanes"])
    lines.append("")
    lines.append("| Lane | Count |")
    lines.append("|---|---:|")
    for lane, count in top_items(lane_counts, limit=12):
        label = lane_label(lane, lang)
        lines.append(f"| `{lane}` — {label} | `{count}` |")
    lines.append("")
    lines.append("## " + L["top_review_organs"])
    lines.append("")
    lines.append("| Organ | Review count |")
    lines.append("|---|---:|")
    for organ, count in top_items(organ_review_counts, limit=12):
        lines.append(f"| `{organ}` | `{count}` |")
    lines.append("")
    lines.append("> " + L["owner_gate"])
    lines.append("")
    return "\n".join(lines)


def html_dashboard(report: Dict[str, Any], progress: Dict[str, Any]) -> str:
    files_total = as_int(report.get("files_total"))
    action_required = as_int(report.get("action_required_total"))
    lane_counts = report.get("lane_counts", {}) or {}
    organ_review_counts = report.get("organ_review_counts", {}) or {}

    def h(x: Any) -> str:
        return html.escape(str(x))

    def card(ru: str, en: str, value: Any, subtitle_ru: str = "", subtitle_en: str = "") -> str:
        return (
            "<div class='card'>"
            f"<div class='title ru'>{h(ru)}</div><div class='title en'>{h(en)}</div>"
            f"<div class='value'>{h(value)}</div>"
            f"<div class='subtitle ru'>{h(subtitle_ru)}</div><div class='subtitle en'>{h(subtitle_en)}</div>"
            "</div>"
        )

    def progress_bar(percent: float) -> str:
        percent = clamp_pct(percent)
        return f"<div class='bar'><span style='width:{percent:.2f}%'></span></div><span class='pct'>{percent:.1f}%</span>"

    roadmap_rows = "".join(
        "<tr>"
        f"<td><span class='badge'>{h(step['status'])}</span></td>"
        f"<td>{progress_bar(float(step['percent']))}</td>"
        f"<td><span class='ru'>{h(step['ru'])}</span><span class='en'>{h(step['en'])}</span></td>"
        f"<td>{h(step['evidence'])}</td>"
        "</tr>"
        for step in progress["roadmap_steps"]
    )
    lane_rows = "".join(
        "<tr>"
        f"<td><b>{h(lane)}</b><br><span class='ru muted'>{h(lane_label(lane, 'ru'))}</span><span class='en muted'>{h(lane)}</span></td>"
        f"<td>{count}</td>"
        f"<td>{progress_bar(pct(count, files_total))}</td>"
        "</tr>"
        for lane, count in top_items(lane_counts, limit=12)
    )
    organ_rows = "".join(
        f"<tr><td>{h(organ)}</td><td>{count}</td><td>{progress_bar(pct(count, max(action_required, 1)))}</td></tr>"
        for organ, count in top_items(organ_review_counts, limit=12)
    )

    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Imperium Trinity Plus Visual Proof — Bilingual Roadmap</title>
<style>
:root {{ --bg:#101218; --panel:#171b24; --panel2:#202636; --border:#303646; --text:#eef1f5; --muted:#aab2c5; --accent:#8dd6ff; --accent2:#d9b8ff; --warn:#ffd166; }}
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; background: var(--bg); color: var(--text); }}
header {{ border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 22px; display:flex; justify-content:space-between; gap:16px; align-items:flex-start; }}
h1 {{ margin:0; font-size:30px; }}
small, .muted {{ color:var(--muted); }}
button {{ background:var(--panel2); color:var(--text); border:1px solid var(--border); border-radius:10px; padding:8px 12px; cursor:pointer; }}
button.active {{ border-color:var(--accent); box-shadow:0 0 0 1px var(--accent) inset; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin:18px 0; }}
.card {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; padding:16px; }}
.title {{ color:var(--muted); font-size:13px; text-transform:uppercase; letter-spacing:.06em; }}
.value {{ font-size:30px; font-weight:700; margin-top:8px; }}
.subtitle {{ color:var(--muted); margin-top:6px; }}
.goal {{ border:1px solid var(--border); background:linear-gradient(135deg, rgba(141,214,255,.12), rgba(217,184,255,.08)); border-radius:14px; padding:18px; margin:18px 0; }}
.goal .big {{ font-size:34px; font-weight:800; margin:8px 0; }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); border-radius:12px; overflow:hidden; margin-bottom:22px; }}
th,td {{ text-align:left; padding:10px 12px; border-bottom:1px solid var(--border); vertical-align:top; }}
th {{ color:var(--muted); background:var(--panel2); }}
.bar {{ display:inline-block; width:220px; max-width:38vw; background:#303646; height:10px; border-radius:99px; overflow:hidden; vertical-align:middle; margin-right:8px; }}
.bar span {{ display:block; height:100%; background:linear-gradient(90deg,var(--accent),var(--accent2)); }}
.pct {{ color:var(--muted); font-variant-numeric: tabular-nums; }}
.badge {{ display:inline-block; border:1px solid var(--border); border-radius:999px; padding:3px 8px; color:var(--accent); background:#111722; font-size:12px; }}
.notice {{ border-left:4px solid var(--accent); padding:12px 14px; background:var(--panel); margin-top:16px; }}
.en {{ display:none; }}
body.lang-en .en {{ display:initial; }} body.lang-en .ru {{ display:none; }}
body.lang-ru .ru {{ display:initial; }} body.lang-ru .en {{ display:none; }}
</style>
<script>
function setLang(lang) {{
  document.body.className = 'lang-' + lang;
  document.getElementById('btn-ru').classList.toggle('active', lang === 'ru');
  document.getElementById('btn-en').classList.toggle('active', lang === 'en');
}}
</script>
</head>
<body class="lang-ru">
<header>
  <div>
    <h1><span class="ru">Imperium Trinity Plus — Смотровая патча</span><span class="en">Imperium Trinity Plus — Patch Visual Proof</span></h1>
    <small>{h(report.get('patch_id','UNKNOWN'))} · {h(utc_now())}</small>
  </div>
  <div><button id="btn-ru" class="active" onclick="setLang('ru')">RU</button> <button id="btn-en" onclick="setLang('en')">EN</button></div>
</header>
<div class="grid">
{card('Файлов просканировано','Files scanned',files_total)}
{card('Требуют действия','Action required',action_required,'classification lanes requiring review','classification lanes requiring review')}
{card('Source HEAD','Source HEAD',report.get('source_head_short','UNKNOWN'))}
{card('Режим','Mode',report.get('mode','UNKNOWN'))}
</div>
<section class="goal">
  <div class="title ru">Общая цель</div><div class="title en">Overall goal</div>
  <div class="ru">{h(progress['overall_goal_ru'])}</div><div class="en">{h(progress['overall_goal_en'])}</div>
  <div class="big">{progress['overall_progress_percent']:.1f}%</div>
  {progress_bar(progress['overall_progress_percent'])}
  <p class="muted ru">{h(progress['progress_warning_ru'])}</p><p class="muted en">{h(progress['progress_warning_en'])}</p>
</section>
<h2><span class="ru">Движение по плану</span><span class="en">Roadmap progress</span></h2>
<table><tr><th>Status</th><th>Progress</th><th><span class="ru">Шаг</span><span class="en">Step</span></th><th>Evidence</th></tr>{roadmap_rows}</table>
<h2><span class="ru">Линии действий</span><span class="en">Action lanes</span></h2>
<table><tr><th>Lane</th><th>Count</th><th>Share</th></tr>{lane_rows}</table>
<h2><span class="ru">Главные зоны ревью</span><span class="en">Top review zones</span></h2>
<table><tr><th>Organ</th><th>Review count</th><th>Share</th></tr>{organ_rows}</table>
<div class="notice"><b>Owner gate:</b> <span class="ru">смотровая разрешает ревью и планирование, но НЕ автоматическое удаление source.</span><span class="en">this proof authorizes review and planning, NOT automatic source deletion.</span></div>
</body>
</html>
"""


def maybe_print_rich(report: Dict[str, Any], progress: Dict[str, Any], language: str) -> bool:
    try:
        from rich.console import Console  # type: ignore
        from rich.panel import Panel  # type: ignore
        from rich.table import Table  # type: ignore
        from rich.progress_bar import ProgressBar  # type: ignore
    except Exception:
        return False

    console = Console()
    title = "Imperium Trinity Plus — Смотровая / Visual Proof" if language == "both" else (RU["title"] if language == "ru" else EN["title"])
    console.print(Panel.fit(
        f"[bold]Patch:[/bold] {report.get('patch_id','UNKNOWN')}\n"
        f"[bold]Source:[/bold] {report.get('source_head_short','UNKNOWN')} / {report.get('source_branch','UNKNOWN')}\n"
        f"[bold]Overall:[/bold] {progress['overall_progress_percent']}%",
        title=title,
        border_style="cyan",
    ))

    table = Table(title="Roadmap / Дорожная карта")
    table.add_column("Status")
    table.add_column("%", justify="right")
    table.add_column("Step")
    table.add_column("Evidence")
    for step in progress["roadmap_steps"]:
        label = step["ru"] if language == "ru" else step["en"] if language == "en" else f"{step['ru']} / {step['en']}"
        table.add_row(str(step["status"]), f"{step['percent']}%", label, str(step["evidence"]))
    console.print(table)
    return True


def build(args: argparse.Namespace) -> Dict[str, Any]:
    report_path = Path(args.classification_report)
    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    report = read_json(report_path)
    patch_id = args.patch_id or report.get("patch_id") or "UNKNOWN-PATCH"
    report["patch_id"] = patch_id
    progress = compute_progress(report)

    machine = {
        "schema": "imperium.trinity_plus_visual_proof.v0_2",
        "surface": SURFACE,
        "version": VERSION,
        "status": "PASS_TRINITY_PLUS_VISUAL_PROOF_BUILT",
        "generated_at_utc": utc_now(),
        "patch_id": patch_id,
        "language_modes": ["ru", "en", "both"],
        "classification_report": str(report_path),
        "source_head_short": report.get("source_head_short"),
        "source_branch": report.get("source_branch"),
        "files_total": report.get("files_total"),
        "action_required_total": report.get("action_required_total"),
        "lane_counts": report.get("lane_counts", {}),
        "organ_review_counts": report.get("organ_review_counts", {}),
        "progress": progress,
        "proof_outputs": {
            "terminal_bilingual": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_TERMINAL_BILINGUAL.txt"),
            "terminal_legacy": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_TERMINAL.txt"),
            "owner_markdown_ru": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_RU.md"),
            "owner_markdown_en": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_EN.md"),
            "owner_markdown_bilingual": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_BILINGUAL.md"),
            "html_dashboard": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_DASHBOARD.html"),
            "machine": str(out_root / "TRINITY_PLUS_VISUAL_PROOF_MACHINE.json"),
        },
        "owner_gate": "Visual proof shows changed/worked state and roadmap progress; it does not authorize automatic source deletion.",
    }

    terminal = terminal_proof(report, progress, args.language)
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_TERMINAL_BILINGUAL.txt").write_text(terminal, encoding="utf-8")
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_TERMINAL.txt").write_text(terminal, encoding="utf-8")
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_RU.md").write_text(markdown_summary(report, progress, "ru"), encoding="utf-8")
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_EN.md").write_text(markdown_summary(report, progress, "en"), encoding="utf-8")
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_BILINGUAL.md").write_text(
        markdown_summary(report, progress, "ru") + "\n---\n\n" + markdown_summary(report, progress, "en"),
        encoding="utf-8",
    )
    (out_root / "TRINITY_PLUS_VISUAL_PROOF_DASHBOARD.html").write_text(html_dashboard(report, progress), encoding="utf-8")
    write_json(out_root / "TRINITY_PLUS_VISUAL_PROOF_MACHINE.json", machine)

    printed_rich = False
    if args.rich in {"auto", "always"}:
        printed_rich = maybe_print_rich(report, progress, args.language)
        if args.rich == "always" and not printed_rich:
            raise SystemExit("Rich requested with --rich always, but the rich package is not installed.")
    if not printed_rich:
        print(terminal)
    print(json.dumps({k: v for k, v in machine.items() if k not in {"lane_counts", "organ_review_counts"}}, ensure_ascii=False, indent=2))
    return machine


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build bilingual owner-facing Trinity Plus visual proof from a classification report.")
    ap.add_argument("--classification-report", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--patch-id", default="")
    ap.add_argument("--language", choices=["ru", "en", "both"], default="both")
    ap.add_argument("--rich", choices=["auto", "always", "never"], default="auto")
    args = ap.parse_args(argv)
    build(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
