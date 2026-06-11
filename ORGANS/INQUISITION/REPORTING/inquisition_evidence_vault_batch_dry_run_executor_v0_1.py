#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Imperium Evidence Vault Batch 001 Dry-Run Executor v0.1

Trinity Plus read-only execution rehearsal for Batch 001.

Safety contract:
- Does NOT copy source files.
- Does NOT move source files.
- Does NOT delete source files.
- Does NOT create an Evidence Vault pack.
- Does NOT write into the Evidence Vault by default.
- Writes dry-run reports/proofs only to --out-root.

Purpose:
Answer the owner question: "If I approve the next execution patch, will the
Evidence Vault packing run have the required source files and stable hashes?"
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import sqlite3
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

SURFACE = "INQUISITION_EVIDENCE_VAULT_BATCH_DRY_RUN_EXECUTOR_V0_1"
VERSION = "0.1.1"
SCHEMA = "imperium.evidence_vault_batch_dry_run.v0_1"
DEFAULT_BATCH_ID = "BATCH_001_REPORTS_LEGACY_PACK_TO_VAULT_DRY_RUN"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(repo: Path, args: Sequence[str], *, ok_empty: bool = False) -> str:
    cp = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if cp.returncode != 0:
        if ok_empty:
            return ""
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or f"git {' '.join(args)} failed")
    return cp.stdout


def git_head(repo: Path) -> str:
    return run_git(repo, ["rev-parse", "HEAD"]).strip()


def git_branch(repo: Path) -> str:
    return run_git(repo, ["branch", "--show-current"], ok_empty=True).strip() or "DETACHED"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    cols = [
        "dry_run_id", "candidate_id", "source_path", "exists", "is_file",
        "size_bytes_planned", "size_bytes_actual", "sha256_plan", "sha256_actual",
        "hash_status", "hash_match", "extension", "top_dir", "vault_relpath",
        "would_stage_to", "planned_action", "owner_gate_required", "source_delete_allowed"
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for row in rows:
            wr.writerow({c: row.get(c, "") for c in cols})


def sha256_file(path: Path, *, max_hash_file_bytes: int) -> Tuple[str, str]:
    try:
        size = path.stat().st_size
    except OSError:
        return "", "MISSING"
    if size > max_hash_file_bytes:
        return "", f"SKIPPED_OVERSIZE>{max_hash_file_bytes}"
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest(), "FULL_SHA256"


def human_bytes(n: int) -> str:
    n = int(n or 0)
    units = ["B", "KB", "MB", "GB", "TB"]
    v = float(n)
    for u in units:
        if v < 1024 or u == units[-1]:
            if u == "B":
                return f"{int(v)} B"
            return f"{v:.1f} {u}"
        v /= 1024
    return f"{n} B"


def rel_top_dir(path: str, depth: int = 2) -> str:
    parts = path.replace("\\", "/").split("/")
    if len(parts) <= depth:
        return path.replace("\\", "/")
    return "/".join(parts[:depth])


def safe_pct(num: float, den: float) -> float:
    if not den:
        return 0.0
    return max(0.0, min(100.0, (num / den) * 100.0))


def bar_text(percent: float, width: int = 34) -> str:
    ratio = max(0.0, min(1.0, percent / 100.0))
    fill = int(round(ratio * width))
    return "█" * fill + "░" * (width - fill)


def summarize_top_dirs(rows: List[Dict[str, Any]]) -> List[Tuple[str, int, int]]:
    c: Counter[str] = Counter()
    b: Counter[str] = Counter()
    for r in rows:
        key = str(r.get("top_dir", ""))
        c[key] += 1
        b[key] += int(r.get("size_bytes_actual") or r.get("size_bytes_planned") or 0)
    return sorted([(k, c[k], b[k]) for k in c], key=lambda x: (x[1], x[2]), reverse=True)


def summarize_ext(rows: List[Dict[str, Any]]) -> List[Tuple[str, int, int]]:
    c: Counter[str] = Counter()
    b: Counter[str] = Counter()
    for r in rows:
        key = str(r.get("extension") or "<none>")
        c[key] += 1
        b[key] += int(r.get("size_bytes_actual") or r.get("size_bytes_planned") or 0)
    return sorted([(k, c[k], b[k]) for k in c], key=lambda x: (x[1], x[2]), reverse=True)


def build_sqlite(path: Path, report: Dict[str, Any], rows: List[Dict[str, Any]]) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    con.execute("create table manifest(key text primary key, value text)")
    for k, v in report.items():
        if k in {"outputs", "samples"}:
            continue
        con.execute("insert into manifest(key,value) values(?,?)", (str(k), json.dumps(v, ensure_ascii=False)))
    # SQLite treats EXISTS as a keyword in DDL contexts on some builds;
    # keep the SQL column explicit as exists_on_disk while preserving the JSON key "exists".
    con.execute("""create table dry_run_items(
        dry_run_id text primary key,
        candidate_id text,
        source_path text,
        exists_on_disk integer,
        is_file integer,
        size_bytes_planned integer,
        size_bytes_actual integer,
        sha256_plan text,
        sha256_actual text,
        hash_status text,
        hash_match integer,
        extension text,
        top_dir text,
        vault_relpath text,
        would_stage_to text,
        planned_action text,
        owner_gate_required integer,
        source_delete_allowed integer
    )""")
    for r in rows:
        con.execute("insert into dry_run_items values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            r["dry_run_id"], r.get("candidate_id", ""), r.get("source_path", ""),
            1 if r.get("exists") else 0, 1 if r.get("is_file") else 0,
            int(r.get("size_bytes_planned") or 0), int(r.get("size_bytes_actual") or 0),
            r.get("sha256_plan", ""), r.get("sha256_actual", ""), r.get("hash_status", ""),
            1 if r.get("hash_match") else 0, r.get("extension", ""), r.get("top_dir", ""),
            r.get("vault_relpath", ""), r.get("would_stage_to", ""), r.get("planned_action", ""),
            1 if r.get("owner_gate_required") else 0,
            1 if r.get("source_delete_allowed") else 0,
        ))
    con.execute("create table top_dirs(top_dir text primary key, count integer, bytes integer)")
    for top, count, size in summarize_top_dirs(rows):
        con.execute("insert into top_dirs values(?,?,?)", (top, int(count), int(size)))
    con.execute("create table extension_counts(extension text primary key, count integer, bytes integer)")
    for ext, count, size in summarize_ext(rows):
        con.execute("insert into extension_counts values(?,?,?)", (ext, int(count), int(size)))
    con.execute("create table risk_counts(risk text primary key, count integer)")
    risks = Counter()
    for r in rows:
        if not r.get("exists"):
            risks["MISSING_SOURCE"] += 1
        elif not r.get("is_file"):
            risks["NOT_FILE"] += 1
        elif r.get("hash_status") != "FULL_SHA256":
            risks[str(r.get("hash_status") or "HASH_NOT_FULL")] += 1
        elif r.get("sha256_plan") and r.get("sha256_actual") and r.get("sha256_plan") != r.get("sha256_actual"):
            risks["SHA256_MISMATCH"] += 1
        else:
            risks["READY"] += 1
    for risk, count in risks.items():
        con.execute("insert into risk_counts values(?,?)", (risk, int(count)))
    con.commit(); con.close()


def html_bar(percent: float) -> str:
    percent = max(0.0, min(100.0, percent))
    return f'<div class="bar"><span style="width:{percent:.2f}%"></span></div><span class="pct">{percent:.1f}%</span>'


def html_dashboard(report: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    candidate_total = int(report["planned_candidates_total"])
    existing_total = int(report["checks"]["existing_files_total"])
    missing_total = int(report["checks"]["missing_files_total"])
    hash_match_total = int(report["checks"]["hash_match_total"])
    ready_percent = safe_pct(hash_match_total, candidate_total)
    exist_percent = safe_pct(existing_total, candidate_total)
    total_bytes = int(report["checks"].get("total_bytes_actual", 0))
    top_dirs = summarize_top_dirs(rows)[:25]
    sample = rows[:80]
    css = """
    :root{--bg:#0d1117;--panel:#151b24;--line:#2b3445;--text:#f2f7ff;--muted:#b8c7e6;--accent:#8bd5ff;--accent2:#dab6ff;--warn:#ffd166;--danger:#ff7b72;--ok:#7ee787;}
    *{box-sizing:border-box} body{margin:0;padding:24px;background:var(--bg);color:var(--text);font-family:Segoe UI,Arial,sans-serif} h1,h2{margin:0 0 14px}.muted{color:var(--muted)}
    .top{display:flex;justify-content:space-between;gap:12px;align-items:start;border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}
    .lang button{background:#20283a;color:var(--text);border:1px solid #36435c;border-radius:8px;padding:8px 12px;margin-left:6px;cursor:pointer}.lang button.active{border-color:var(--accent);box-shadow:0 0 0 2px rgba(139,213,255,.2)}
    .grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}.label{text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-size:13px}.big{font-size:34px;font-weight:800;margin-top:10px}
    .owner{background:linear-gradient(135deg,#17212c,#21172f);border:1px solid var(--line);border-radius:12px;margin:18px 0;padding:20px}
    table{width:100%;border-collapse:collapse;background:var(--panel);border-radius:12px;overflow:hidden;margin:12px 0 28px}th{background:#20283a;color:#cfe2ff;text-align:left}td,th{border-bottom:1px solid var(--line);padding:11px 12px;vertical-align:top}code{font-family:Consolas,monospace;color:#dbeafe}
    .bar{display:inline-block;width:220px;height:11px;background:#30384b;border-radius:99px;overflow:hidden;margin-right:10px}.bar span{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2))}.pct{color:#cfe2ff}.pill{display:inline-block;border:1px solid #2f8ed8;color:#8bd5ff;border-radius:999px;padding:3px 8px;font-size:12px}.ok{color:var(--ok)}.warn{color:var(--warn)}.danger{color:var(--danger)}
    .gate{border-left:4px solid var(--accent);background:#111827;padding:14px 18px;margin-top:22px}.ru .enOnly{display:none}.en .ruOnly{display:none}
    @media(max-width:900px){.grid{grid-template-columns:1fr}.bar{width:120px}}
    """
    top_rows = []
    for top, count, size in top_dirs:
        top_rows.append(f"<tr><td><code>{html.escape(top)}</code></td><td>{count}</td><td>{human_bytes(size)}</td><td>{html_bar(safe_pct(count, candidate_total))}</td></tr>")
    sample_rows = []
    for r in sample:
        status_cls = "ok" if r.get("hash_match") else ("danger" if not r.get("exists") else "warn")
        status = "READY" if r.get("hash_match") else r.get("hash_status", "CHECK")
        sample_rows.append(
            f"<tr><td><code>{html.escape(str(r.get('dry_run_id','')))}</code></td>"
            f"<td class='{status_cls}'>{html.escape(str(status))}</td><td>{human_bytes(int(r.get('size_bytes_actual') or 0))}</td>"
            f"<td><code>{html.escape(str(r.get('source_path','')))}</code></td></tr>"
        )
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Imperium Evidence Vault Batch Dry Run</title><style>{css}</style></head>
<body class="ru">
<div class="top"><div>
<h1><span class="ruOnly">Imperium Trinity Plus — Dry-run упаковки Batch 001</span><span class="enOnly">Imperium Trinity Plus — Batch 001 Packing Dry Run</span></h1>
<div class="muted">{html.escape(report['patch_id'])} · {html.escape(report['generated_at_utc'])}</div>
</div><div class="lang"><button onclick="document.body.className='ru';this.classList.add('active');this.nextElementSibling.classList.remove('active')" class="active">RU</button><button onclick="document.body.className='en';this.classList.add('active');this.previousElementSibling.classList.remove('active')">EN</button></div></div>
<div class="grid">
  <div class="card"><div class="label ruOnly">Кандидатов</div><div class="label enOnly">Candidates</div><div class="big">{candidate_total}</div><div class="muted">Batch 001 / REPORTS_LEGACY</div></div>
  <div class="card"><div class="label ruOnly">Файлы найдены</div><div class="label enOnly">Files found</div><div class="big">{existing_total}</div>{html_bar(exist_percent)}</div>
  <div class="card"><div class="label ruOnly">Объём</div><div class="label enOnly">Bytes</div><div class="big">{human_bytes(total_bytes)}</div><div class="muted">actual readable source bytes</div></div>
  <div class="card"><div class="label ruOnly">Режим</div><div class="label enOnly">Mode</div><div class="big">dry-run</div><div class="muted">no copy / no move / no delete / no pack</div></div>
</div>
<div class="owner">
<div class="label">Owner Gate</div>
<h2 class="ruOnly">Этот патч НЕ упаковывает source. Он проверяет готовность будущего execution-патча.</h2>
<h2 class="enOnly">This patch does NOT pack source. It verifies readiness for a future execution patch.</h2>
<p class="ruOnly">Dry-run считает наличие файлов, размеры и SHA256. Копирование в Evidence Vault, создание ZIP и удаление source остаются запрещены без отдельного owner gate.</p>
<p class="enOnly">The dry run checks file presence, sizes and SHA256. Evidence Vault copy, ZIP creation and source deletion remain blocked without a separate owner gate.</p>
</div>
<h2 class="ruOnly">Готовность к execution</h2><h2 class="enOnly">Execution readiness</h2>
<table><tr><th>Status</th><th>Progress</th><th class="ruOnly">Шаг</th><th class="enOnly">Step</th><th>Evidence</th></tr>
<tr><td><span class="pill">PASS</span></td><td>{html_bar(100)}</td><td class="ruOnly">Pack plan загружен</td><td class="enOnly">Pack plan loaded</td><td>{candidate_total} planned candidates</td></tr>
<tr><td><span class="pill">{'PASS' if missing_total == 0 else 'WARN'}</span></td><td>{html_bar(exist_percent)}</td><td class="ruOnly">Source-файлы существуют</td><td class="enOnly">Source files exist</td><td>existing={existing_total}; missing={missing_total}</td></tr>
<tr><td><span class="pill">{'PASS' if hash_match_total == existing_total and missing_total == 0 else 'WARN'}</span></td><td>{html_bar(ready_percent)}</td><td class="ruOnly">SHA256 рассчитаны</td><td class="enOnly">SHA256 computed</td><td>hash_match={hash_match_total}; total={candidate_total}</td></tr>
<tr><td><span class="pill">OWNER_GATE_REQUIRED</span></td><td>{html_bar(0)}</td><td class="ruOnly">Упаковка в Evidence Vault</td><td class="enOnly">Evidence Vault packing</td><td>not executed by this dry run</td></tr>
<tr><td><span class="pill">BLOCKED</span></td><td>{html_bar(0)}</td><td class="ruOnly">Удаление source</td><td class="enOnly">Source deletion</td><td>explicitly out of scope</td></tr>
</table>
<h2 class="ruOnly">Главные папки dry-run</h2><h2 class="enOnly">Top dry-run folders</h2>
<table><tr><th>Folder</th><th>Count</th><th>Bytes</th><th>Share</th></tr>{''.join(top_rows)}</table>
<h2 class="ruOnly">Первые проверенные кандидаты</h2><h2 class="enOnly">First checked candidates</h2>
<table><tr><th>ID</th><th>Status</th><th>Bytes</th><th>Path</th></tr>{''.join(sample_rows)}</table>
<div class="gate"><b>Owner gate:</b> <span class="ruOnly">dry-run разрешает подготовку execution patch, но НЕ автоматическую упаковку, перемещение или удаление.</span><span class="enOnly">dry run authorizes execution-patch preparation, but NOT automatic packing, moving or deletion.</span></div>
</body></html>"""


def terminal_proof(report: Dict[str, Any]) -> str:
    total = int(report["planned_candidates_total"])
    checks = report["checks"]
    exist_pct = safe_pct(int(checks["existing_files_total"]), total)
    hash_pct = safe_pct(int(checks["hash_match_total"]), total)
    lines = []
    lines.append("=" * 78)
    lines.append("IMPERIUM TRINITY PLUS — EVIDENCE VAULT BATCH 001 DRY-RUN")
    lines.append("=" * 78)
    lines.append(f"Patch      : {report['patch_id']}")
    lines.append(f"Source     : {report['source_head_short']} / {report['source_branch']}")
    lines.append(f"Mode       : {report['mode']} (no copy / no move / no delete / no pack)")
    lines.append("")
    lines.append("COUNTERS")
    lines.append(f"Candidates         : {total}")
    lines.append(f"Existing files     : {checks['existing_files_total']} [{bar_text(exist_pct)}] {exist_pct:5.1f}%")
    lines.append(f"Missing files      : {checks['missing_files_total']}")
    lines.append(f"SHA256 matched     : {checks['hash_match_total']} [{bar_text(hash_pct)}] {hash_pct:5.1f}%")
    lines.append(f"Actual bytes       : {human_bytes(int(checks.get('total_bytes_actual', 0)))}")
    lines.append("")
    lines.append("OWNER DECISION")
    lines.append("PASS means the execution patch can be prepared. It does NOT authorize source deletion.")
    lines.append("PASS означает, что можно готовить execution patch. Это НЕ разрешает удаление source.")
    return "\n".join(lines) + "\n"


def build(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    out = Path(args.out_root).resolve()
    out.mkdir(parents=True, exist_ok=True)
    plan_path = Path(args.pack_plan).resolve()
    manifest_path = Path(args.file_manifest_jsonl).resolve()
    vault_root = Path(args.vault_root)

    plan = load_json(plan_path)
    source_rows = load_jsonl(manifest_path)
    head = git_head(repo)
    branch = git_branch(repo)
    batch_id = args.batch_id or DEFAULT_BATCH_ID
    patch_id = args.patch_id
    planned_stage_root = vault_root / "buffer" / "dry-run" / f"{batch_id}_{head[:12]}"

    rows: List[Dict[str, Any]] = []
    total_bytes_actual = 0
    total_bytes_planned = 0
    missing_total = 0
    existing_total = 0
    is_file_total = 0
    hash_match_total = 0
    hash_mismatch_total = 0
    skipped_hash_total = 0

    for idx, src in enumerate(source_rows, start=1):
        rel = str(src.get("path") or src.get("source_path") or "").replace("\\", "/")
        candidate_id = str(src.get("candidate_id") or src.get("plan_id") or f"{batch_id}-{idx:05d}")
        full = repo / rel
        exists = full.exists()
        is_file = full.is_file() if exists else False
        size_planned = int(src.get("size_bytes") or src.get("size_bytes_planned") or 0)
        total_bytes_planned += size_planned
        size_actual = int(full.stat().st_size) if is_file else 0
        total_bytes_actual += size_actual
        if exists:
            existing_total += 1
        else:
            missing_total += 1
        if is_file:
            is_file_total += 1
        sha_actual, hash_status = ("", "MISSING")
        if is_file:
            sha_actual, hash_status = sha256_file(full, max_hash_file_bytes=args.max_hash_file_bytes)
        if hash_status.startswith("SKIPPED"):
            skipped_hash_total += 1
        sha_plan = str(src.get("sha256") or src.get("sha256_plan") or "")
        hash_match = bool(sha_actual and (not sha_plan or sha_actual == sha_plan))
        if hash_match:
            hash_match_total += 1
        elif sha_plan and sha_actual and sha_plan != sha_actual:
            hash_mismatch_total += 1
        vault_relpath = str(src.get("vault_relpath") or ("source/" + rel))
        dry_id = f"{batch_id}-{idx:05d}"
        rows.append({
            "dry_run_id": dry_id,
            "candidate_id": candidate_id,
            "source_path": rel,
            "exists": exists,
            "is_file": is_file,
            "size_bytes_planned": size_planned,
            "size_bytes_actual": size_actual,
            "sha256_plan": sha_plan,
            "sha256_actual": sha_actual,
            "hash_status": hash_status,
            "hash_match": hash_match,
            "extension": Path(rel).suffix.lower() or "<none>",
            "top_dir": src.get("top_dir") or rel_top_dir(rel, 2),
            "vault_relpath": vault_relpath,
            "would_stage_to": str(planned_stage_root / vault_relpath.replace("/", os.sep)),
            "planned_action": "DRY_RUN_VERIFY_AND_STAGE_PREVIEW_ONLY",
            "owner_gate_required": True,
            "source_delete_allowed": False,
        })

    ready = missing_total == 0 and hash_mismatch_total == 0 and skipped_hash_total == 0 and hash_match_total == len(rows)
    report = {
        "schema": SCHEMA,
        "surface": SURFACE,
        "version": VERSION,
        "status": "PASS_EVIDENCE_VAULT_BATCH_DRY_RUN_READY" if ready else "WARN_EVIDENCE_VAULT_BATCH_DRY_RUN_REVIEW_REQUIRED",
        "generated_at_utc": utc_now(),
        "repo": str(repo),
        "source_head": head,
        "source_head_short": head[:12],
        "source_branch": branch,
        "patch_id": patch_id,
        "batch_id": batch_id,
        "mode": "read_only_dry_run_no_copy_no_move_no_delete_no_pack",
        "source_pack_plan": str(plan_path),
        "source_file_manifest_jsonl": str(manifest_path),
        "vault_root": str(vault_root),
        "planned_stage_root": str(planned_stage_root),
        "planned_candidates_total": len(rows),
        "checks": {
            "existing_files_total": existing_total,
            "missing_files_total": missing_total,
            "is_file_total": is_file_total,
            "hash_match_total": hash_match_total,
            "hash_mismatch_total": hash_mismatch_total,
            "hash_skipped_total": skipped_hash_total,
            "total_bytes_planned": total_bytes_planned,
            "total_bytes_actual": total_bytes_actual,
            "source_delete_allowed": False,
            "copy_executed": False,
            "move_executed": False,
            "pack_created": False,
            "vault_write_executed": False,
        },
        "owner_gate": "Dry-run permits execution-patch preparation only; no source deletion/copy/pack is authorized.",
        "recommended_next_action_ru": "Если dry-run PASS, подготовить owner-gated execution patch для копирования/упаковки в Evidence Vault. Source deletion отдельно запрещён.",
        "source_plan_digest": {
            "plan_status": plan.get("status"),
            "plan_surface": plan.get("surface"),
            "plan_patch_id": plan.get("patch_id"),
            "plan_batch_id": plan.get("batch_id"),
            "plan_candidates_total": plan.get("planned_candidates_total") or plan.get("candidates_total"),
        },
    }

    outputs = {
        "report": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_REPORT.json",
        "checks_jsonl": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_FILE_CHECKS.jsonl",
        "checks_csv": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_FILE_CHECKS.csv",
        "sha256sums": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_SHA256SUMS.txt",
        "staging_preview": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_STAGING_LAYOUT_PREVIEW.json",
        "risk_summary": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_RISK_SUMMARY.json",
        "sqlite": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN.sqlite",
        "owner_gate_ru": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_OWNER_GATE_RU.md",
        "owner_gate_en": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_OWNER_GATE_EN.md",
        "dashboard": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_VISUAL_PROOF_DASHBOARD.html",
        "terminal": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_VISUAL_PROOF_TERMINAL_RU_EN.txt",
        "machine": out / "EVIDENCE_VAULT_BATCH_001_DRY_RUN_VISUAL_PROOF_MACHINE.json",
    }
    report["outputs"] = {k: str(v) for k, v in outputs.items()}
    report["samples"] = {"first_items": rows[:25], "top_dirs": summarize_top_dirs(rows)[:25]}

    write_json(outputs["report"], report)
    write_jsonl(outputs["checks_jsonl"], rows)
    write_csv(outputs["checks_csv"], rows)
    sums = []
    for r in rows:
        if r.get("sha256_actual"):
            sums.append(f"{r['sha256_actual']}  {r['source_path']}")
    outputs["sha256sums"].write_text("\n".join(sums) + ("\n" if sums else ""), encoding="utf-8")
    staging = {
        "status": "DRY_RUN_STAGING_LAYOUT_PREVIEW_ONLY",
        "planned_stage_root": str(planned_stage_root),
        "would_create_directories_total": len(set(str(Path(r["vault_relpath"]).parent).replace("\\", "/") for r in rows)),
        "would_stage_files_total": len(rows),
        "would_stage_bytes_total": total_bytes_actual,
        "vault_write_executed": False,
        "source_delete_allowed": False,
        "examples": [{"source": r["source_path"], "would_stage_to": r["would_stage_to"]} for r in rows[:20]],
    }
    write_json(outputs["staging_preview"], staging)
    risks = {
        "missing_files_total": missing_total,
        "hash_mismatch_total": hash_mismatch_total,
        "hash_skipped_total": skipped_hash_total,
        "ready_files_total": hash_match_total,
        "blocking_for_execution": [
            x for x, n in [("MISSING_SOURCE", missing_total), ("SHA256_MISMATCH", hash_mismatch_total), ("HASH_SKIPPED", skipped_hash_total)] if n
        ],
    }
    write_json(outputs["risk_summary"], risks)
    build_sqlite(outputs["sqlite"], report, rows)
    outputs["owner_gate_ru"].write_text(
        "# Owner Gate — Evidence Vault Batch 001 Dry-run\n\n"
        "Этот dry-run НЕ копирует, НЕ перемещает, НЕ удаляет и НЕ создаёт Vault pack.\n\n"
        f"- Кандидатов: {len(rows)}\n"
        f"- Найдено файлов: {existing_total}\n"
        f"- Missing: {missing_total}\n"
        f"- SHA256 match: {hash_match_total}\n"
        f"- Объём: {human_bytes(total_bytes_actual)}\n\n"
        "Если статус PASS, следующий патч может быть execution-патчем копирования/упаковки в Evidence Vault. Удаление source остаётся запрещено отдельным gate.\n",
        encoding="utf-8",
    )
    outputs["owner_gate_en"].write_text(
        "# Owner Gate — Evidence Vault Batch 001 Dry-run\n\n"
        "This dry-run does NOT copy, move, delete, or create a Vault pack.\n\n"
        f"- Candidates: {len(rows)}\n"
        f"- Existing files: {existing_total}\n"
        f"- Missing: {missing_total}\n"
        f"- SHA256 match: {hash_match_total}\n"
        f"- Bytes: {human_bytes(total_bytes_actual)}\n\n"
        "If PASS, a later patch may execute copy/packing into Evidence Vault. Source deletion remains blocked by a separate gate.\n",
        encoding="utf-8",
    )
    outputs["dashboard"].write_text(html_dashboard(report, rows), encoding="utf-8")
    outputs["terminal"].write_text(terminal_proof(report), encoding="utf-8")
    write_json(outputs["machine"], report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Evidence Vault Batch 001 dry-run executor")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pack-plan", required=True)
    ap.add_argument("--file-manifest-jsonl", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--vault-root", default="E:\\IMPERIUM_EVIDENCE_VAULT")
    ap.add_argument("--patch-id", default="SMOKE-V0_9_4-EVIDENCE-VAULT-BATCH-001-DRY-RUN")
    ap.add_argument("--batch-id", default=DEFAULT_BATCH_ID)
    ap.add_argument("--max-hash-file-bytes", type=int, default=512 * 1024 * 1024)
    args = ap.parse_args(argv)
    build(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
