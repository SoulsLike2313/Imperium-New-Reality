#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Imperium Evidence Vault Batch Pack Plan v0.1

Trinity Plus read-only planner for turning an owner-reviewed hygiene batch
preview into an Evidence Vault pack execution plan.

Important safety contract:
- Does NOT copy files.
- Does NOT move files.
- Does NOT delete source.
- Does NOT create a Vault pack.
- Writes only plan/proof artifacts to --out-root.
A later patch may execute the plan only after explicit owner acceptance.
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
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SURFACE = "INQUISITION_EVIDENCE_VAULT_BATCH_PACK_PLAN_V0_1"
VERSION = "0.1.1"
SCHEMA = "imperium.evidence_vault_batch_pack_plan.v0_1"
DEFAULT_BATCH_ID = "BATCH_001_REPORTS_LEGACY_PACK_TO_VAULT_PLAN"

RUNTIME_PARTS = {"__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
RUNTIME_SUFFIXES = (".pyc", ".pyo", ".trace.zip", ".har")
SOURCE_DELETE_FORBIDDEN = True


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
        "plan_id", "candidate_id", "path", "size_bytes", "sha256", "hash_status",
        "extension", "top_dir", "source_lane", "source_severity", "planned_action",
        "vault_relpath", "owner_gate_required", "source_delete_allowed"
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for row in rows:
            wr.writerow({c: row.get(c, "") for c in cols})


def rel_top_dir(path: str, depth: int = 2) -> str:
    parts = path.replace("\\", "/").split("/")
    if len(parts) <= depth:
        return path.replace("\\", "/")
    return "/".join(parts[:depth])


def is_runtime_or_local(path: str) -> bool:
    lower = path.lower().replace("\\", "/")
    parts = set(lower.split("/"))
    if parts & {p.lower() for p in RUNTIME_PARTS}:
        return True
    return lower.endswith(RUNTIME_SUFFIXES) or lower.startswith(".imperium_patch_backups/") or lower.startswith("_local_handoff/")


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


def candidate_ok(row: Dict[str, Any], repo: Path) -> Tuple[bool, str]:
    path = str(row.get("path", "")).replace("\\", "/")
    if not path:
        return False, "missing path"
    if row.get("organ") != "REPORTS_LEGACY":
        return False, "not REPORTS_LEGACY"
    if row.get("lane") != "PACK_TO_VAULT_CANDIDATE":
        return False, "not PACK_TO_VAULT_CANDIDATE"
    if is_runtime_or_local(path):
        return False, "runtime/local marker"
    full = repo / path
    if not full.exists() or not full.is_file():
        return False, "missing source file"
    if not path.startswith("REPORTS/"):
        return False, "outside REPORTS/"
    return True, "high-confidence reports legacy pack-to-vault candidate"


def vault_relpath_for(path: str) -> str:
    # Preserve source relative path under source/ so later execution is reversible and auditable.
    return "source/" + path.replace("\\", "/")


def build_sqlite(path: Path, plan: Dict[str, Any], rows: List[Dict[str, Any]]) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    con.execute("create table manifest(key text primary key, value text)")
    for k, v in plan.items():
        if k in {"candidates_sample", "outputs"}:
            continue
        con.execute("insert into manifest(key,value) values(?,?)", (str(k), json.dumps(v, ensure_ascii=False)))
    con.execute("""create table pack_plan_items(
        candidate_id text primary key,
        path text,
        size_bytes integer,
        sha256 text,
        hash_status text,
        extension text,
        top_dir text,
        source_lane text,
        source_severity text,
        planned_action text,
        vault_relpath text,
        owner_gate_required integer,
        source_delete_allowed integer
    )""")
    for r in rows:
        con.execute("insert into pack_plan_items values(?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            r["candidate_id"], r["path"], int(r["size_bytes"]), r.get("sha256",""),
            r.get("hash_status",""), r.get("extension",""), r.get("top_dir",""),
            r.get("source_lane",""), r.get("source_severity",""), r.get("planned_action",""),
            r.get("vault_relpath",""), 1 if r.get("owner_gate_required") else 0,
            1 if r.get("source_delete_allowed") else 0,
        ))
    con.execute("create table top_dirs(top_dir text primary key, count integer, bytes integer)")
    for top, count, size in top_dirs(rows):
        con.execute("insert into top_dirs values(?,?,?)", (top, int(count), int(size)))
    con.execute("create table extension_counts(extension text primary key, count integer, bytes integer)")
    for ext, count, size in ext_counts(rows):
        con.execute("insert into extension_counts values(?,?,?)", (ext, int(count), int(size)))
    con.commit()
    con.close()


def top_dirs(rows: List[Dict[str, Any]]) -> List[Tuple[str, int, int]]:
    c: Counter[str] = Counter()
    b: Counter[str] = Counter()
    for r in rows:
        key = str(r.get("top_dir", ""))
        c[key] += 1
        b[key] += int(r.get("size_bytes", 0) or 0)
    return sorted([(k, c[k], b[k]) for k in c], key=lambda x: (x[1], x[2]), reverse=True)


def ext_counts(rows: List[Dict[str, Any]]) -> List[Tuple[str, int, int]]:
    c: Counter[str] = Counter()
    b: Counter[str] = Counter()
    for r in rows:
        key = str(r.get("extension", "<none>"))
        c[key] += 1
        b[key] += int(r.get("size_bytes", 0) or 0)
    return sorted([(k, c[k], b[k]) for k in c], key=lambda x: (x[1], x[2]), reverse=True)


def bar(value: float, width: int = 34) -> str:
    value = max(0.0, min(1.0, value))
    fill = int(round(value * width))
    return "█" * fill + "░" * (width - fill)


def human_bytes(n: int) -> str:
    n = int(n or 0)
    units = ["B", "KB", "MB", "GB"]
    x = float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            return f"{x:.1f} {u}" if u != "B" else f"{n} B"
        x /= 1024
    return f"{n} B"




def resolve_repo_files_total(preview: Dict[str, Any], repo: Path) -> int:
    """Return a stable denominator for repo-share percentages.

    Batch preview v0.9.2 stores repo total as classification_files_total, while
    older/alternative reports may expose repo_files_total or files_total.  The
    previous v0.9.3 planner only checked repo_files_total/files_total, which
    collapsed to 1 when consuming the real v0.9.2 preview and rendered
    200400.0% instead of 22.4% in the owner dashboard.
    """
    for key in (
        "repo_files_total",
        "files_total",
        "classification_files_total",
        "source_files_total",
        "repo_total",
    ):
        value = preview.get(key)
        try:
            n = int(value or 0)
        except Exception:
            n = 0
        if n > 0:
            return n
    try:
        out = subprocess.check_output(["git", "-C", str(repo), "ls-files"], text=True, errors="replace")
        n = len([line for line in out.splitlines() if line.strip()])
        if n > 0:
            return n
    except Exception:
        pass
    return 0


def ratio_percent(numerator: int, denominator: int) -> Tuple[float, float]:
    denominator = int(denominator or 0)
    if denominator <= 0:
        return 0.0, 0.0
    ratio = max(0.0, min(1.0, float(numerator or 0) / float(denominator)))
    return ratio, ratio * 100.0

def build_terminal(plan: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    total_repo = int(plan.get("repo_files_total", 0) or 0)
    selected = int(plan.get("planned_candidates_total", 0) or 0)
    pct = float(plan.get("repo_share_ratio", 0.0) or 0.0)
    if not pct:
        pct, _ = ratio_percent(selected, total_repo)
    lines = []
    lines.append("=" * 78)
    lines.append("IMPERIUM TRINITY PLUS — EVIDENCE VAULT BATCH 001 PACK PLAN")
    lines.append("ИМПЕРИУМ TRINITY PLUS — ПЛАН УПАКОВКИ BATCH 001 В EVIDENCE VAULT")
    lines.append("=" * 78)
    lines.append(f"Patch / Патч       : {plan['patch_id']}")
    lines.append(f"Source / HEAD      : {plan['source_head_short']} / {plan['source_branch']}")
    lines.append(f"Mode / Режим       : {plan['mode']}")
    lines.append(f"Candidates         : {selected} / {plan.get('candidate_pool_total')} ({pct*100:.1f}% repo)")
    lines.append(f"Bytes / Объём      : {human_bytes(plan.get('planned_bytes_total', 0))}")
    lines.append("")
    lines.append("OWNER GATE / ГЕЙТ ВЛАДЕЛЬЦА")
    lines.append("- This plan DOES NOT copy, move, pack or delete source.")
    lines.append("- Этот план НЕ копирует, НЕ перемещает, НЕ упаковывает и НЕ удаляет source.")
    lines.append("- Next patch may execute COPY/PACK to Vault only after explicit owner approval.")
    lines.append("")
    lines.append("READINESS / ГОТОВНОСТЬ")
    steps = [
        ("PASS", 1.0, "Batch preview exists / batch preview построен"),
        ("PASS", 1.0, "Pack plan generated / план упаковки создан"),
        ("PASS", 1.0, "Manifest preview + SQLite proof / manifest preview + SQLite proof"),
        ("OWNER_GATE_REQUIRED", 0.0, "Actual Vault packing / реальная упаковка в Vault"),
        ("BLOCKED", 0.0, "Source deletion / удаление source"),
    ]
    for status, p, label in steps:
        lines.append(f"{status:<20} {bar(p, 24)} {p*100:5.1f}%  {label}")
    lines.append("")
    lines.append("TOP FOLDERS / ГЛАВНЫЕ ПАПКИ")
    denom = max(1, selected)
    for top, count, size in top_dirs(rows)[:12]:
        lines.append(f"{top:<62} {count:5d} {bar(count/denom, 12)} {human_bytes(size):>10}")
    lines.append("")
    lines.append("OUTPUTS")
    for key, value in plan.get("outputs", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) + "\n"


def html_bar(pct: float) -> str:
    pct = max(0.0, min(100.0, pct))
    return f'<div class="bar"><span style="width:{pct:.2f}%"></span></div><span class="pct">{pct:.1f}%</span>'


def build_dashboard(plan: Dict[str, Any], rows: List[Dict[str, Any]], path: Path) -> None:
    selected = int(plan.get("planned_candidates_total", 0) or 0)
    repo_total = int(plan.get("repo_files_total", 0) or 0)
    repo_share = float(plan.get("repo_share_percent", 0.0) or 0.0)
    if not repo_share:
        _, repo_share = ratio_percent(selected, repo_total)
    top = top_dirs(rows)[:25]
    sample = rows[:75]
    css = """
    :root{--bg:#0d1117;--panel:#151b24;--panel2:#1b2230;--line:#2b3445;--text:#f2f7ff;--muted:#b8c7e6;--accent:#8bd5ff;--accent2:#dab6ff;--warn:#ffd166;}
    *{box-sizing:border-box} body{margin:0;padding:24px;background:var(--bg);color:var(--text);font-family:Segoe UI,Arial,sans-serif} h1,h2{margin:0 0 14px} .muted{color:var(--muted)}
    .top{display:flex;justify-content:space-between;gap:12px;align-items:start;border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}
    .lang button{background:#20283a;color:var(--text);border:1px solid #36435c;border-radius:8px;padding:8px 12px;margin-left:6px;cursor:pointer}.lang button.active{border-color:var(--accent);box-shadow:0 0 0 2px rgba(139,213,255,.2)}
    .grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}.label{text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-size:13px}.big{font-size:34px;font-weight:800;margin-top:10px}
    .owner{background:linear-gradient(135deg,#17212c,#21172f);border:1px solid var(--line);border-radius:12px;margin:18px 0;padding:20px}
    table{width:100%;border-collapse:collapse;background:var(--panel);border-radius:12px;overflow:hidden;margin:12px 0 28px}th{background:#20283a;color:#cfe2ff;text-align:left}td,th{border-bottom:1px solid var(--line);padding:11px 12px;vertical-align:top}code{font-family:Consolas,monospace;color:#dbeafe}
    .bar{display:inline-block;width:220px;height:11px;background:#30384b;border-radius:99px;overflow:hidden;margin-right:10px}.bar span{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2))}.pct{color:#cfe2ff}.pill{display:inline-block;border:1px solid #2f8ed8;color:#8bd5ff;border-radius:999px;padding:3px 8px;font-size:12px}
    .gate{border-left:4px solid var(--accent);background:#111827;padding:14px 18px;margin-top:22px}.ru .enOnly{display:none}.en .ruOnly{display:none}
    @media(max-width:900px){.grid{grid-template-columns:1fr}.bar{width:120px}}
    """
    def tr_top(topdir, count, size):
        share = count / max(1, selected) * 100
        return f"<tr><td><code>{html.escape(topdir)}</code></td><td>{count}</td><td>{human_bytes(size)}</td><td>{html_bar(share)}</td></tr>"
    def tr_sample(r):
        return "<tr><td><code>{}</code></td><td>{}</td><td>{}</td><td><code>{}</code></td></tr>".format(
            html.escape(str(r.get("candidate_id",""))),
            html.escape(str(r.get("source_severity",""))),
            human_bytes(int(r.get("size_bytes",0) or 0)),
            html.escape(str(r.get("path",""))),
        )
    html_doc = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Imperium Evidence Vault Batch Plan</title><style>{css}</style></head>
<body class="ru">
<div class="top"><div>
<h1><span class="ruOnly">Imperium Trinity Plus — План упаковки Batch 001</span><span class="enOnly">Imperium Trinity Plus — Batch 001 Pack Plan</span></h1>
<div class="muted">{html.escape(plan['patch_id'])} · {html.escape(plan['generated_at_utc'])}</div>
</div><div class="lang"><button onclick="document.body.className='ru';this.classList.add('active');this.nextElementSibling.classList.remove('active')" class="active">RU</button><button onclick="document.body.className='en';this.classList.add('active');this.previousElementSibling.classList.remove('active')">EN</button></div></div>
<div class="grid">
  <div class="card"><div class="label ruOnly">Кандидатов</div><div class="label enOnly">Candidates</div><div class="big">{selected}</div><div class="muted">REPORTS_LEGACY / PACK_TO_VAULT</div></div>
  <div class="card"><div class="label ruOnly">Доля репо</div><div class="label enOnly">Repo share</div><div class="big">{repo_share:.1f}%</div>{html_bar(repo_share)}</div>
  <div class="card"><div class="label">Source HEAD</div><div class="big">{html.escape(plan['source_head_short'])}</div><div class="muted">{html.escape(plan['source_branch'])}</div></div>
  <div class="card"><div class="label ruOnly">Режим</div><div class="label enOnly">Mode</div><div class="big">plan</div><div class="muted">no copy / no move / no delete</div></div>
</div>
<div class="owner">
<div class="label">Owner Gate</div>
<h2 class="ruOnly">Этот патч НЕ упаковывает и НЕ чистит source. Он строит план упаковки в Evidence Vault.</h2>
<h2 class="enOnly">This patch does NOT pack or clean source. It builds an Evidence Vault pack plan.</h2>
<p class="ruOnly">Следующий execution-патч сможет копировать/упаковывать выбранные high-confidence candidates только после явного owner approval. Удаление source отдельным gate запрещено.</p>
<p class="enOnly">A later execution patch may copy/pack selected high-confidence candidates only after explicit owner approval. Source deletion remains blocked without a separate gate.</p>
</div>
<h2 class="ruOnly">Готовность Batch 001</h2><h2 class="enOnly">Batch 001 readiness</h2>
<table><tr><th>Status</th><th>Progress</th><th class="ruOnly">Шаг</th><th class="enOnly">Step</th><th>Evidence</th></tr>
<tr><td><span class="pill">PASS</span></td><td>{html_bar(100)}</td><td class="ruOnly">Batch preview найден</td><td class="enOnly">Batch preview loaded</td><td>{plan.get('candidate_pool_total')} preview candidates</td></tr>
<tr><td><span class="pill">PASS</span></td><td>{html_bar(100)}</td><td class="ruOnly">Pack plan построен</td><td class="enOnly">Pack plan generated</td><td>{selected} planned candidates</td></tr>
<tr><td><span class="pill">OWNER_GATE_REQUIRED</span></td><td>{html_bar(0)}</td><td class="ruOnly">Упаковка в Evidence Vault</td><td class="enOnly">Evidence Vault packing</td><td>not executed by this plan</td></tr>
<tr><td><span class="pill">BLOCKED</span></td><td>{html_bar(0)}</td><td class="ruOnly">Удаление source</td><td class="enOnly">Source deletion</td><td>explicitly out of scope</td></tr>
</table>
<h2 class="ruOnly">Главные папки плана</h2><h2 class="enOnly">Top planned folders</h2>
<table><tr><th>Folder</th><th>Count</th><th>Bytes</th><th>Share</th></tr>
{''.join(tr_top(*x) for x in top)}
</table>
<h2 class="ruOnly">Первые кандидаты плана</h2><h2 class="enOnly">First plan candidates</h2>
<table><tr><th>ID</th><th>Severity</th><th>Bytes</th><th>Path</th></tr>
{''.join(tr_sample(r) for r in sample)}
</table>
<div class="gate"><b>Owner gate:</b> <span class="ruOnly">план разрешает ревью и подготовку execution patch, но НЕ автоматическую упаковку, перемещение или удаление.</span><span class="enOnly">this plan authorizes review and execution-patch preparation, but NOT automatic packing, moving or deletion.</span></div>
</body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_doc, encoding="utf-8")


def build_markdown(plan: Dict[str, Any], rows: List[Dict[str, Any]], lang: str) -> str:
    total = int(plan.get("planned_candidates_total", 0) or 0)
    b = human_bytes(int(plan.get("planned_bytes_total", 0) or 0))
    if lang == "ru":
        title = "# Evidence Vault Batch 001 — план упаковки\n"
        body = [
            title,
            f"- Статус: `{plan['status']}`",
            f"- Режим: `{plan['mode']}`",
            f"- Кандидатов в плане: **{total}**",
            f"- Общий объём: **{b}**",
            f"- Source HEAD: `{plan['source_head_short']}`",
            "",
            "## Owner gate",
            "Этот план НЕ копирует, НЕ перемещает, НЕ упаковывает и НЕ удаляет source.",
            "Следующий execution patch может работать только после явного owner approval.",
            "",
            "## Следующий допустимый шаг",
            "Подготовить execution patch для copy/pack выбранных candidates в Evidence Vault. Удаление source остаётся запрещено отдельным gate.",
        ]
    else:
        body = [
            "# Evidence Vault Batch 001 — Pack Plan\n",
            f"- Status: `{plan['status']}`",
            f"- Mode: `{plan['mode']}`",
            f"- Planned candidates: **{total}**",
            f"- Total bytes: **{b}**",
            f"- Source HEAD: `{plan['source_head_short']}`",
            "",
            "## Owner gate",
            "This plan does NOT copy, move, pack or delete source.",
            "A later execution patch may run only after explicit owner approval.",
            "",
            "## Next allowed step",
            "Prepare an execution patch for copy/pack of selected candidates into Evidence Vault. Source deletion remains blocked by a separate gate.",
        ]
    return "\n".join(body) + "\n"


def build(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    out_root = Path(args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    preview = load_json(Path(args.batch_preview))
    candidates = load_jsonl(Path(args.candidates_jsonl))

    pool_total = len(candidates)
    planned_rows: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    max_candidates = int(args.max_candidates or 0)
    for row in candidates:
        ok, reason = candidate_ok(row, repo)
        if not ok:
            rejected.append({"path": row.get("path", ""), "reason": reason})
            continue
        if max_candidates and len(planned_rows) >= max_candidates:
            rejected.append({"path": row.get("path", ""), "reason": "over max candidates cap"})
            continue
        rel = str(row["path"]).replace("\\", "/")
        full = repo / rel
        size = full.stat().st_size
        digest, hash_status = sha256_file(full, max_hash_file_bytes=int(args.max_hash_file_bytes))
        plan_item = {
            "plan_id": args.batch_id,
            "candidate_id": row.get("candidate_id", f"{args.batch_id}-{len(planned_rows)+1:05d}"),
            "path": rel,
            "size_bytes": size,
            "sha256": digest,
            "hash_status": hash_status,
            "extension": Path(rel).suffix.lower() or "<none>",
            "top_dir": rel_top_dir(rel, 2),
            "source_lane": row.get("lane", ""),
            "source_severity": row.get("severity", ""),
            "planned_action": "COPY_OR_PACK_TO_EVIDENCE_VAULT_AFTER_OWNER_APPROVAL",
            "vault_relpath": vault_relpath_for(rel),
            "owner_gate_required": True,
            "source_delete_allowed": False,
            "reason": reason,
        }
        planned_rows.append(plan_item)

    total_bytes = sum(int(r["size_bytes"]) for r in planned_rows)
    generated = utc_now()
    now = datetime.now(timezone.utc)
    vault_pack_root_preview = str(Path(args.vault_root) / "packs" / f"{now.year:04d}" / f"{now.month:02d}" / args.batch_id)
    head = git_head(repo)
    repo_files_total = resolve_repo_files_total(preview, repo)
    repo_share_ratio, repo_share_percent = ratio_percent(len(planned_rows), repo_files_total)

    plan = {
        "schema": SCHEMA,
        "surface": SURFACE,
        "version": VERSION,
        "status": "PASS_EVIDENCE_VAULT_BATCH_PACK_PLAN_BUILT",
        "generated_at_utc": generated,
        "repo": str(repo),
        "source_head": head,
        "source_head_short": head[:12],
        "source_branch": git_branch(repo),
        "patch_id": args.patch_id,
        "batch_id": args.batch_id,
        "mode": "read_only_pack_plan_no_copy_no_delete",
        "repo_files_total": repo_files_total,
        "repo_share_ratio": repo_share_ratio,
        "repo_share_percent": repo_share_percent,
        "repo_share_percent_display": f"{repo_share_percent:.1f}%",
        "candidate_pool_total": pool_total,
        "planned_candidates_total": len(planned_rows),
        "rejected_candidates_total": len(rejected),
        "planned_bytes_total": total_bytes,
        "planned_bytes_human": human_bytes(total_bytes),
        "vault_root": str(Path(args.vault_root)),
        "vault_pack_root_preview": vault_pack_root_preview,
        "source_delete_allowed": False,
        "copy_pack_allowed_by_this_plan": False,
        "owner_gate_required_before_execution": True,
        "high_confidence_rule": "REPORTS_LEGACY + PACK_TO_VAULT_CANDIDATE + existing REPORTS/* file + no runtime/local marker",
        "trinity_plus": {
            "data_atlas": "Evidence Vault Batch Plan card and proof expose planned pack scope.",
            "organ_logic": "Inquisition planner converts Batch Preview candidates into a copy/pack plan.",
            "architecture_spine": "Execution requires owner gate; source deletion remains blocked.",
            "plus_visual_proof": "HTML/terminal/markdown/machine proof shows the plan and what is not executed."
        },
        "outputs": {
            "plan": str(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_PLAN.json"),
            "manifest_preview_jsonl": str(out_root / "EVIDENCE_VAULT_BATCH_001_FILE_MANIFEST_PREVIEW.jsonl"),
            "manifest_preview_csv": str(out_root / "EVIDENCE_VAULT_BATCH_001_FILE_MANIFEST_PREVIEW.csv"),
            "sha256sums_preview": str(out_root / "EVIDENCE_VAULT_BATCH_001_SHA256SUMS_PREVIEW.txt"),
            "risk_summary": str(out_root / "EVIDENCE_VAULT_BATCH_001_RISK_SUMMARY.json"),
            "owner_gate_ru": str(out_root / "EVIDENCE_VAULT_BATCH_001_OWNER_GATE_RU.md"),
            "owner_gate_en": str(out_root / "EVIDENCE_VAULT_BATCH_001_OWNER_GATE_EN.md"),
            "sqlite_index": str(out_root / "EVIDENCE_VAULT_BATCH_001_PACK_PLAN.sqlite"),
            "dashboard": str(out_root / "EVIDENCE_VAULT_BATCH_001_VISUAL_PROOF_DASHBOARD.html"),
            "terminal": str(out_root / "EVIDENCE_VAULT_BATCH_001_VISUAL_PROOF_TERMINAL_RU_EN.txt"),
            "machine_proof": str(out_root / "EVIDENCE_VAULT_BATCH_001_VISUAL_PROOF_MACHINE.json"),
        },
        "recommended_next_action_ru": "Owner review: approve pack execution in a later patch; this plan does not pack, move or delete source.",
    }

    write_json(Path(plan["outputs"]["plan"]), plan)
    write_jsonl(Path(plan["outputs"]["manifest_preview_jsonl"]), planned_rows)
    write_csv(Path(plan["outputs"]["manifest_preview_csv"]), planned_rows)
    sha_lines = []
    for r in planned_rows:
        if r.get("sha256"):
            sha_lines.append(f"{r['sha256']}  {r['path']}")
        else:
            sha_lines.append(f"{r['hash_status']}  {r['path']}")
    Path(plan["outputs"]["sha256sums_preview"]).write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    write_json(Path(plan["outputs"]["risk_summary"]), {
        "batch_id": args.batch_id,
        "planned_candidates_total": len(planned_rows),
        "planned_bytes_total": total_bytes,
        "planned_bytes_human": human_bytes(total_bytes),
        "rejected_candidates_total": len(rejected),
        "extension_counts": [{"extension": e, "count": c, "bytes": b} for e, c, b in ext_counts(planned_rows)],
        "top_dirs": [{"top_dir": t, "count": c, "bytes": b} for t, c, b in top_dirs(planned_rows)],
        "owner_gate_required": True,
        "source_delete_allowed": False,
        "rejected_sample": rejected[:50],
    })
    Path(plan["outputs"]["owner_gate_ru"]).write_text(build_markdown(plan, planned_rows, "ru"), encoding="utf-8")
    Path(plan["outputs"]["owner_gate_en"]).write_text(build_markdown(plan, planned_rows, "en"), encoding="utf-8")
    terminal = build_terminal(plan, planned_rows)
    Path(plan["outputs"]["terminal"]).write_text(terminal, encoding="utf-8")
    build_dashboard(plan, planned_rows, Path(plan["outputs"]["dashboard"]))
    write_json(Path(plan["outputs"]["machine_proof"]), {"plan": plan, "top_dirs": top_dirs(planned_rows)[:20], "sample": planned_rows[:75]})
    build_sqlite(Path(plan["outputs"]["sqlite_index"]), plan, planned_rows)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return plan


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build an owner-gated Evidence Vault pack plan from Batch 001 preview.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--batch-preview", required=True)
    ap.add_argument("--candidates-jsonl", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--vault-root", default=r"E:\IMPERIUM_EVIDENCE_VAULT")
    ap.add_argument("--patch-id", default="V0_9_3-EVIDENCE-VAULT-BATCH-001-PACK-PLAN")
    ap.add_argument("--batch-id", default=DEFAULT_BATCH_ID)
    ap.add_argument("--max-candidates", type=int, default=0, help="0 means all high-confidence candidates")
    ap.add_argument("--max-hash-file-bytes", type=int, default=50 * 1024 * 1024)
    args = ap.parse_args(argv)
    build(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
