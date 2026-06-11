#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Imperium Hygiene Batch Planner v0.1

Read-only owner-gated batch preview planner.
It consumes Repo Hygiene Classification outputs and builds a proposed Batch 001
preview for owner review. It never moves, deletes, copies to Vault, or rewrites
source files. Execution requires a later explicit owner gate.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

SURFACE = "INQUISITION_HYGIENE_BATCH_PLANNER_V0_1"
VERSION = "0.1.0"
SCHEMA = "imperium.owner_gated_hygiene_batch_preview.v0_1"
DEFAULT_BATCH_ID = "BATCH_001_REPORTS_LEGACY_PACK_TO_VAULT_PREVIEW"


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
        "batch_id", "candidate_id", "lane", "severity", "organ", "file_kind",
        "size_bytes", "extension", "path", "recommended_action", "reasons"
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for row in rows:
            wr.writerow({
                "batch_id": row.get("batch_id", ""),
                "candidate_id": row.get("candidate_id", ""),
                "lane": row.get("lane", ""),
                "severity": row.get("severity", ""),
                "organ": row.get("organ", ""),
                "file_kind": row.get("file_kind", ""),
                "size_bytes": row.get("size_bytes", 0),
                "extension": row.get("extension", ""),
                "path": row.get("path", ""),
                "recommended_action": row.get("recommended_action", ""),
                "reasons": "; ".join(row.get("reasons", [])),
            })


def rel_top_dir(path: str, depth: int = 2) -> str:
    parts = path.split("/")
    if len(parts) <= depth:
        return path
    return "/".join(parts[:depth])


def bar(value: float, width: int = 32) -> str:
    value = max(0.0, min(1.0, value))
    fill = int(round(value * width))
    return "█" * fill + "░" * (width - fill)


def size_of(repo: Path, rel: str) -> int:
    try:
        p = repo / rel
        return p.stat().st_size if p.exists() and p.is_file() else 0
    except OSError:
        return 0


def enrich_candidates(repo: Path, rows: List[Dict[str, Any]], batch_id: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i, row in enumerate(rows, start=1):
        path = str(row.get("path", "")).replace("\\", "/")
        ext = Path(path).suffix.lower() or "<none>"
        size = size_of(repo, path)
        item = dict(row)
        item.update({
            "batch_id": batch_id,
            "candidate_id": f"{batch_id}-{i:05d}",
            "size_bytes": size,
            "extension": ext,
            "top_dir": rel_top_dir(path, 2),
            "owner_gate_required": True,
            "execution_allowed_by_this_preview": False,
            "planned_action": "COPY_OR_PACK_TO_EVIDENCE_VAULT_ONLY_AFTER_OWNER_APPROVAL",
        })
        out.append(item)
    return out


def build_sqlite(path: Path, preview: Dict[str, Any], candidates: List[Dict[str, Any]], ext_counts: Dict[str, int], top_dirs: List[Tuple[str, int, int]]) -> None:
    if path.exists():
        path.unlink()
    con = sqlite3.connect(str(path))
    try:
        con.execute("CREATE TABLE manifest(key TEXT PRIMARY KEY, value TEXT)")
        con.execute("""
            CREATE TABLE candidates(
              candidate_id TEXT PRIMARY KEY,
              path TEXT,
              lane TEXT,
              severity TEXT,
              organ TEXT,
              file_kind TEXT,
              extension TEXT,
              size_bytes INTEGER,
              top_dir TEXT,
              planned_action TEXT,
              owner_gate_required INTEGER
            )
        """)
        con.execute("CREATE TABLE extension_counts(extension TEXT PRIMARY KEY, count INTEGER)")
        con.execute("CREATE TABLE top_dirs(top_dir TEXT PRIMARY KEY, count INTEGER, size_bytes INTEGER)")
        for k, v in preview.items():
            if k in {"candidates_sample", "outputs"}:
                continue
            con.execute("INSERT INTO manifest(key,value) VALUES (?,?)", (k, json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)))
        for c in candidates:
            con.execute("""
                INSERT INTO candidates(candidate_id,path,lane,severity,organ,file_kind,extension,size_bytes,top_dir,planned_action,owner_gate_required)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                c["candidate_id"], c["path"], c["lane"], c["severity"], c["organ"], c["file_kind"],
                c["extension"], int(c.get("size_bytes", 0)), c["top_dir"], c["planned_action"], 1 if c.get("owner_gate_required") else 0
            ))
        for ext, count in sorted(ext_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            con.execute("INSERT INTO extension_counts(extension,count) VALUES (?,?)", (ext, count))
        for name, count, size in top_dirs:
            con.execute("INSERT INTO top_dirs(top_dir,count,size_bytes) VALUES (?,?,?)", (name, count, size))
        con.commit()
    finally:
        con.close()


def html_bar(percent: float) -> str:
    p = max(0.0, min(100.0, percent))
    return f"<div class='bar'><span style='width:{p:.1f}%'></span></div><span class='pct'>{p:.1f}%</span>"


def build_dashboard(preview: Dict[str, Any], candidates: List[Dict[str, Any]], top_dirs: List[Tuple[str, int, int]], path: Path, lang_default: str = "ru") -> None:
    total_files = max(int(preview.get("classification_files_total") or 1), 1)
    candidate_total = int(preview.get("candidate_total") or 0)
    candidate_share = candidate_total / total_files * 100.0
    top = candidates[:50]
    rows_candidates = "\n".join(
        f"<tr><td>{html.escape(c['candidate_id'])}</td><td>{html.escape(c['severity'])}</td><td>{c.get('size_bytes',0)}</td><td><code>{html.escape(c['path'])}</code></td></tr>"
        for c in top
    )
    rows_dirs = "\n".join(
        f"<tr><td><code>{html.escape(name)}</code></td><td>{count}</td><td>{size}</td><td>{html_bar((count/max(candidate_total,1))*100)}</td></tr>"
        for name, count, size in top_dirs[:20]
    )
    risk_rows = "\n".join(
        f"<tr><td>{html.escape(k)}</td><td>{v}</td><td>{html_bar((v/max(candidate_total,1))*100)}</td></tr>"
        for k, v in sorted(preview.get("severity_counts", {}).items(), key=lambda kv: (-kv[1], kv[0]))
    )
    style = """
    body{font-family:Inter,Segoe UI,Arial,sans-serif;background:#0d1117;color:#f0f6fc;margin:0;padding:24px;}
    .top{display:flex;justify-content:space-between;gap:16px;align-items:center}.lang button{background:#1f2937;color:#dbeafe;border:1px solid #334155;border-radius:8px;padding:8px 12px;margin-left:8px;cursor:pointer}.lang button.active{border-color:#7dd3fc;box-shadow:0 0 0 2px #164e63 inset}.grid{display:grid;grid-template-columns:repeat(4,minmax(180px,1fr));gap:14px;margin:20px 0}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:18px}.label{color:#bfdbfe;text-transform:uppercase;letter-spacing:.06em;font-size:13px}.big{font-size:30px;font-weight:800;margin-top:10px}.accent{background:linear-gradient(135deg,#16202d,#1f1b2e)}h1,h2{margin:10px 0 14px}.section{margin:26px 0}.bar{display:inline-block;width:220px;height:11px;background:#2d3748;border-radius:99px;vertical-align:middle;overflow:hidden}.bar span{display:block;height:100%;background:linear-gradient(90deg,#7dd3fc,#d8b4fe)}.pct{margin-left:10px;color:#bfdbfe}.badge{border:1px solid #1f6feb;color:#7dd3fc;border-radius:999px;padding:3px 8px;font-size:12px}table{width:100%;border-collapse:collapse;background:#161b22;border-radius:12px;overflow:hidden}th,td{border-bottom:1px solid #30363d;padding:10px;text-align:left}th{background:#1f2937;color:#bfdbfe}code{color:#e0f2fe}.gate{border-left:4px solid #7dd3fc;background:#111827;padding:14px 16px;margin-top:22px}.en{display:none}body.en-mode .ru{display:none}body.en-mode .en{display:block}body.en-mode span.en{display:inline}body.en-mode td.en,body.en-mode th.en{display:table-cell}body.en-mode .ru-inline{display:none}.small{color:#bfdbfe;font-size:14px}.warn{color:#fcd34d}.ok{color:#86efac}@media(max-width:900px){.grid{grid-template-columns:1fr}}
    """
    script = """
    function setLang(l){document.body.classList.toggle('en-mode',l==='en');document.getElementById('btn-ru').classList.toggle('active',l==='ru');document.getElementById('btn-en').classList.toggle('active',l==='en');}
    """
    body_class = "en-mode" if lang_default == "en" else ""
    html_text = f"""<!doctype html><html lang='ru'><head><meta charset='utf-8'><title>Imperium Batch 001 Preview</title><style>{style}</style></head><body class='{body_class}'>
    <div class='top'><div><h1><span class='ru'>Imperium Trinity Plus — Batch 001 Preview</span><span class='en'>Imperium Trinity Plus — Batch 001 Preview</span></h1><div class='small'>{html.escape(preview['patch_id'])} · {html.escape(preview['generated_at_utc'])}</div></div><div class='lang'><button id='btn-ru' class='active' onclick="setLang('ru')">RU</button><button id='btn-en' onclick="setLang('en')">EN</button></div></div>
    <div class='grid'>
      <div class='card'><div class='label ru'>Кандидатов</div><div class='label en'>Candidates</div><div class='big'>{candidate_total}</div><div class='small'>REPORTS_LEGACY / PACK_TO_VAULT</div></div>
      <div class='card'><div class='label ru'>Доля репо</div><div class='label en'>Repo share</div><div class='big'>{candidate_share:.1f}%</div>{html_bar(candidate_share)}</div>
      <div class='card'><div class='label'>SOURCE HEAD</div><div class='big'>{html.escape(preview['source_head_short'])}</div><div class='small'>{html.escape(preview['source_branch'])}</div></div>
      <div class='card'><div class='label ru'>Режим</div><div class='label en'>Mode</div><div class='big'>preview</div><div class='small warn'>no move / no delete / no pack</div></div>
    </div>
    <div class='card accent'><div class='label ru'>Owner gate</div><div class='label en'>Owner gate</div><h2 class='ru'>Этот патч НЕ чистит source. Он показывает первый batch для ревью.</h2><h2 class='en'>This patch does NOT clean source. It shows the first batch for review.</h2><p class='ru'>После одобрения следующий патч сможет копировать/упаковывать high-confidence candidates в Evidence Vault. Удаление source отдельно запрещено без нового owner gate.</p><p class='en'>After approval, a later patch may copy/package high-confidence candidates into Evidence Vault. Source deletion remains prohibited without a separate owner gate.</p></div>
    <div class='section'><h2 class='ru'>Готовность Batch 001</h2><h2 class='en'>Batch 001 readiness</h2><table><tr><th>Status</th><th>Progress</th><th class='ru'>Шаг</th><th class='en'>Step</th><th>Evidence</th></tr>
      <tr><td><span class='badge ok'>PASS</span></td><td>{html_bar(100)}</td><td class='ru'>Кандидаты найдены</td><td class='en'>Candidates discovered</td><td>{candidate_total} candidates selected from classification queue</td></tr>
      <tr><td><span class='badge ok'>PASS</span></td><td>{html_bar(100)}</td><td class='ru'>Смотровая создана</td><td class='en'>Visual proof generated</td><td>HTML + terminal + markdown + machine proof</td></tr>
      <tr><td><span class='badge'>OWNER_GATE_REQUIRED</span></td><td>{html_bar(0)}</td><td class='ru'>Упаковка в Evidence Vault</td><td class='en'>Evidence Vault packaging</td><td>not executed by this preview</td></tr>
      <tr><td><span class='badge'>BLOCKED</span></td><td>{html_bar(0)}</td><td class='ru'>Удаление source</td><td class='en'>Source deletion</td><td>explicitly out of scope</td></tr>
    </table></div>
    <div class='section'><h2 class='ru'>Top folders</h2><h2 class='en'>Top folders</h2><table><tr><th>Folder</th><th>Count</th><th>Bytes</th><th>Share</th></tr>{rows_dirs}</table></div>
    <div class='section'><h2 class='ru'>Риск</h2><h2 class='en'>Risk</h2><table><tr><th>Severity</th><th>Count</th><th>Share</th></tr>{risk_rows}</table></div>
    <div class='section'><h2 class='ru'>Первые кандидаты</h2><h2 class='en'>First candidates</h2><table><tr><th>ID</th><th>Severity</th><th>Bytes</th><th>Path</th></tr>{rows_candidates}</table></div>
    <div class='gate'><b>Owner gate:</b> <span class='ru'>preview разрешает планирование, но НЕ автоматическое перемещение, упаковку или удаление.</span><span class='en'>preview authorizes planning, NOT automatic move, packaging, or deletion.</span></div>
    <script>{script}</script></body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")


def build_markdown(preview: Dict[str, Any], top_dirs: List[Tuple[str, int, int]], lang: str) -> str:
    ru = lang == "ru"
    lines: List[str] = []
    lines.append(f"# {'Batch 001 Preview — владелецкий gate' if ru else 'Batch 001 Preview — Owner Gate'}")
    lines.append("")
    lines.append(f"- Status: `{preview['status']}`")
    lines.append(f"- Source HEAD: `{preview['source_head_short']}`")
    lines.append(f"- Candidates: {preview['candidate_total']}")
    lines.append(f"- Total bytes: {preview['candidate_bytes_total']}")
    lines.append(f"- Mode: `{preview['mode']}`")
    lines.append("")
    lines.append("## " + ("Правило" if ru else "Rule"))
    lines.append(("Этот preview ничего не удаляет, не перемещает и не упаковывает. Он только показывает owner-у первый batch кандидатов." if ru else "This preview does not delete, move, or package anything. It only shows the first candidate batch to the owner."))
    lines.append("")
    lines.append("## Top folders")
    for name, count, size in top_dirs[:20]:
        lines.append(f"- `{name}`: {count} files, {size} bytes")
    lines.append("")
    lines.append("## " + ("Следующее действие" if ru else "Next action"))
    lines.append(("Если owner принимает preview, следующий patch может подготовить pack-to-vault execution только для выбранных high-confidence candidates. Source deletion остаётся запрещённым отдельным gate." if ru else "If the owner accepts the preview, the next patch may prepare pack-to-vault execution for selected high-confidence candidates only. Source deletion remains blocked behind a separate gate."))
    return "\n".join(lines) + "\n"


def build_terminal(preview: Dict[str, Any], top_dirs: List[Tuple[str, int, int]], candidates: List[Dict[str, Any]]) -> str:
    total_files = max(int(preview.get("classification_files_total") or 1), 1)
    candidate_total = int(preview.get("candidate_total") or 0)
    share = candidate_total / total_files
    lines = []
    lines.append("=" * 78)
    lines.append("IMPERIUM TRINITY PLUS — BATCH 001 OWNER-GATED PREVIEW")
    lines.append("=" * 78)
    lines.append(f"Patch      : {preview['patch_id']}")
    lines.append(f"Source     : {preview['source_head_short']} / {preview['source_branch']}")
    lines.append(f"Mode       : {preview['mode']}")
    lines.append(f"Candidates : {candidate_total} / {total_files} [{bar(share)}] {share*100:5.1f}%")
    lines.append(f"Bytes      : {preview['candidate_bytes_total']}")
    lines.append("")
    lines.append("RU: preview показывает кандидатов, но не выполняет cleanup.")
    lines.append("EN: preview shows candidates, but does not execute cleanup.")
    lines.append("")
    lines.append("TOP FOLDERS")
    for name, count, size in top_dirs[:12]:
        pct = count / max(candidate_total, 1)
        lines.append(f"{name:<50} {count:>5} [{bar(pct, 24)}] {pct*100:5.1f}% {size:>10} bytes")
    lines.append("")
    lines.append("FIRST CANDIDATES")
    for c in candidates[:20]:
        lines.append(f"{c['candidate_id']} {c['severity']:<8} {c.get('size_bytes',0):>8}  {c['path']}")
    lines.append("")
    lines.append("OWNER GATE: next patch may pack/copy only after explicit owner approval; no source deletion.")
    return "\n".join(lines) + "\n"


def select_candidates(rows: List[Dict[str, Any]], target_organ: str, target_lane: str) -> List[Dict[str, Any]]:
    return [r for r in rows if r.get("organ") == target_organ and r.get("lane") == target_lane]


def build(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    out_root = Path(args.out_root).resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    classification_report = load_json(Path(args.classification_report).resolve())
    lane_queue = load_jsonl(Path(args.lane_queue).resolve())
    head = git_head(repo)
    branch = git_branch(repo)
    if head != classification_report.get("source_head"):
        # Do not fail: the preview can still be useful, but report the mismatch.
        head_match = False
    else:
        head_match = True
    batch_id = args.batch_id or DEFAULT_BATCH_ID
    selected_raw = select_candidates(lane_queue, args.target_organ, args.target_lane)
    candidates = enrich_candidates(repo, selected_raw, batch_id)
    total_bytes = sum(int(c.get("size_bytes", 0)) for c in candidates)
    severity_counts = dict(sorted(Counter(c.get("severity", "UNKNOWN") for c in candidates).items()))
    ext_counts = dict(sorted(Counter(c.get("extension", "") for c in candidates).items()))
    top_counter: Dict[str, Tuple[int, int]] = {}
    for c in candidates:
        key = c.get("top_dir", "<unknown>")
        count, size = top_counter.get(key, (0, 0))
        top_counter[key] = (count + 1, size + int(c.get("size_bytes", 0)))
    top_dirs = [(k, v[0], v[1]) for k, v in top_counter.items()]
    top_dirs.sort(key=lambda x: (-x[1], -x[2], x[0]))

    preview = {
        "schema": SCHEMA,
        "surface": SURFACE,
        "version": VERSION,
        "status": "PASS_HYGIENE_BATCH_PREVIEW_BUILT",
        "generated_at_utc": utc_now(),
        "repo": str(repo),
        "source_head": head,
        "source_head_short": head[:12],
        "source_branch": branch,
        "classification_head": classification_report.get("source_head"),
        "classification_head_match": head_match,
        "patch_id": args.patch_id,
        "batch_id": batch_id,
        "mode": "read_only_owner_gated_preview",
        "target_organ": args.target_organ,
        "target_lane": args.target_lane,
        "classification_files_total": classification_report.get("files_total", 0),
        "classification_action_required_total": classification_report.get("action_required_total", 0),
        "candidate_total": len(candidates),
        "candidate_bytes_total": total_bytes,
        "severity_counts": severity_counts,
        "extension_counts": ext_counts,
        "top_dirs": [{"top_dir": k, "count": c, "size_bytes": s} for k, c, s in top_dirs[:50]],
        "owner_gate": {
            "required": True,
            "preview_authorizes": ["review", "planning", "batch selection"],
            "preview_does_not_authorize": ["source deletion", "source move", "Evidence Vault execution", "git rm"],
            "next_allowed_step_after_owner_acceptance": "prepare pack-to-vault execution patch for selected high-confidence candidates",
        },
        "trinity_plus": {
            "data_atlas": "Batch Preview card and dashboard expose candidate lanes.",
            "organ_logic": "Inquisition planner builds candidate queue from classification output.",
            "architecture_spine": "Owner-gated batch doctrine prevents cleanup without explicit approval.",
            "plus_visual_proof": "HTML/terminal/markdown/machine proof shows what would be affected before execution.",
        },
        "candidates_sample": candidates[: int(args.max_dashboard_items)],
        "outputs": {
            "preview": str(out_root / "BATCH_001_PREVIEW.json"),
            "owner_gate_ru": str(out_root / "BATCH_001_OWNER_GATE_RU.md"),
            "owner_gate_en": str(out_root / "BATCH_001_OWNER_GATE_EN.md"),
            "candidates_jsonl": str(out_root / "BATCH_001_CANDIDATES.jsonl"),
            "candidates_csv": str(out_root / "BATCH_001_CANDIDATES.csv"),
            "risk_summary": str(out_root / "BATCH_001_RISK_SUMMARY.json"),
            "sqlite_index": str(out_root / "BATCH_001_PREVIEW.sqlite"),
            "dashboard": str(out_root / "BATCH_001_VISUAL_PROOF_DASHBOARD.html"),
            "terminal": str(out_root / "BATCH_001_VISUAL_PROOF_TERMINAL_RU_EN.txt"),
            "machine_proof": str(out_root / "BATCH_001_VISUAL_PROOF_MACHINE.json"),
        },
        "recommended_next_action_ru": "Owner review: approve selected candidates for a later pack-to-vault execution patch; no cleanup is performed by this preview.",
    }

    write_json(out_root / "BATCH_001_PREVIEW.json", preview)
    write_jsonl(out_root / "BATCH_001_CANDIDATES.jsonl", candidates)
    write_csv(out_root / "BATCH_001_CANDIDATES.csv", candidates)
    write_json(out_root / "BATCH_001_RISK_SUMMARY.json", {
        "batch_id": batch_id,
        "candidate_total": len(candidates),
        "candidate_bytes_total": total_bytes,
        "severity_counts": severity_counts,
        "extension_counts": ext_counts,
        "top_dirs": preview["top_dirs"],
        "owner_gate_required": True,
    })
    (out_root / "BATCH_001_OWNER_GATE_RU.md").write_text(build_markdown(preview, top_dirs, "ru"), encoding="utf-8")
    (out_root / "BATCH_001_OWNER_GATE_EN.md").write_text(build_markdown(preview, top_dirs, "en"), encoding="utf-8")
    terminal = build_terminal(preview, top_dirs, candidates)
    (out_root / "BATCH_001_VISUAL_PROOF_TERMINAL_RU_EN.txt").write_text(terminal, encoding="utf-8")
    build_dashboard(preview, candidates, top_dirs, out_root / "BATCH_001_VISUAL_PROOF_DASHBOARD.html")
    write_json(out_root / "BATCH_001_VISUAL_PROOF_MACHINE.json", {"preview": preview, "top_dirs": preview["top_dirs"][:20]})
    build_sqlite(out_root / "BATCH_001_PREVIEW.sqlite", preview, candidates, ext_counts, top_dirs)
    return preview


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build an owner-gated hygiene batch preview from classification lane outputs.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--classification-report", required=True)
    ap.add_argument("--lane-queue", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--patch-id", default="V0_9_2-OWNER-GATED-HYGIENE-BATCH-PREVIEW")
    ap.add_argument("--batch-id", default=DEFAULT_BATCH_ID)
    ap.add_argument("--target-organ", default="REPORTS_LEGACY")
    ap.add_argument("--target-lane", default="PACK_TO_VAULT_CANDIDATE")
    ap.add_argument("--max-dashboard-items", type=int, default=50)
    args = ap.parse_args(argv)
    preview = build(args)
    print(json.dumps({k: v for k, v in preview.items() if k != "candidates_sample"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
